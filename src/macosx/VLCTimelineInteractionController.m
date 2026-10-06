// SPDX-License-Identifier: GPL-2.0-or-later
#import "VLCTimelineInteractionController.h"
#import "VLCTimelineContext.h"
#import "VLCThumbnailService.h"
#import "VLCTimelineGeometry.h"
#import "VLCMain.h"
#import "misc.h"

@interface VLCTimelinePreviewPanel : NSPanel
@end
@implementation VLCTimelinePreviewPanel
- (BOOL)canBecomeKeyWindow { return NO; }
- (BOOL)canBecomeMainWindow { return NO; }
// Preview text/images are decorative; the original slider owns accessible
// time and seeking. Exclude the subtree rather than exposing a changing window.
- (BOOL)isAccessibilityElement { return NO; }
- (NSArray *)accessibilityChildren { return @[]; }
- (NSArray *)accessibilityChildrenInNavigationOrder { return @[]; }
@end

// Prototype: a stationary transparent host, with only the card moving inside
// it. AppKit owns the layer hierarchy; drawing clears the old card and shadow.
@interface VLCTimelinePreviewCanvas : NSView
@property (weak) NSView *card;
@end
@implementation VLCTimelinePreviewCanvas
- (void)drawRect:(NSRect)dirtyRect
{
    [[NSColor clearColor] setFill];
    NSRectFillUsingOperation(dirtyRect, NSCompositingOperationCopy);
    [NSGraphicsContext saveGraphicsState];
    NSShadow *shadow = [NSShadow new];
    shadow.shadowOffset = NSMakeSize(0, -2); shadow.shadowBlurRadius = 5;
    shadow.shadowColor = [NSColor colorWithCalibratedWhite:0 alpha:0.45];
    [shadow set];
    [[NSColor colorWithCalibratedWhite:0.08 alpha:0.97] setFill];
    NSRectFill(self.card.frame);
    [NSGraphicsContext restoreGraphicsState];
}
@end

@interface VLCTimelineInteractionController ()
@property (weak) NSSlider *slider;
@property NSTrackingArea *tracking;
@property (weak) NSView *trackingView;
@property NSPanel *panel;
@property VLCTimelinePreviewCanvas *canvas;
@property NSView *card;
@property NSImageView *imageView;
@property NSTextField *timeLabel;
@property NSTextField *stateLabel;
@property NSTimer *visibilityTimer;
@property NSTimer *previewRefreshTimer;
@property BOOL hovering;
@property BOOL previewsEnabled;
@property NSString *originalToolTip;
@property BOOL refreshing;
@property NSPoint point;
@property NSString *generation;
@property int64_t demand;
@property int64_t displayedActual;
@property NSUInteger presentation;
@property NSUInteger requestToken;
@property double hoverStarted;
@property id diagnosticMonitor;
@end
@implementation VLCTimelineInteractionController
- (instancetype)initWithSlider:(NSSlider *)slider
{
    self = [super init]; if (!self) return nil;
    _slider = slider; _demand = -1;
    if (getenv("VLC_TIMELINE_DIAGNOSTICS")) {
        NSMutableArray *ancestors = [NSMutableArray array];
        for (NSView *view = slider; view; view = view.superview)
            [ancestors addObject:@{@"class": NSStringFromClass(view.class),
                @"frame": NSStringFromRect(view.frame), @"bounds": NSStringFromRect(view.bounds),
                @"visible": NSStringFromRect(view.visibleRect), @"hidden": @(view.hidden),
                @"alpha": @(view.alphaValue), @"layer_backed": @(view.wantsLayer)}];
        VLCTimelineTrace(@{@"event": @"view-ancestry", @"views": ancestors});
    }
    [self refreshTracking]; slider.window.acceptsMouseMovedEvents = YES;
    slider.postsFrameChangedNotifications = YES; slider.postsBoundsChangedNotifications = YES;
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(refreshTracking)
        name:NSViewFrameDidChangeNotification object:slider];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(refreshTracking)
        name:NSViewBoundsDidChangeNotification object:slider];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(refreshTracking)
        name:NSWindowDidResizeNotification object:nil];
    // Standard fullscreen sliders can expose their translated name only via
    // the tooltip on modern AppKit. Keep that name before removing the popup.
    if (!slider.accessibilityLabel.length && slider.toolTip.length)
        slider.accessibilityLabel = slider.toolTip;
    _originalToolTip = slider.toolTip;
    _previewsEnabled = var_InheritBool(getIntf(), "macosx-timeline-previews");
    // Preserve slider AX role/actions; remove its generic tooltip to avoid two popups.
    slider.toolTip = _previewsEnabled ? nil : _originalToolTip;
    _panel = [[VLCTimelinePreviewPanel alloc] initWithContentRect:NSMakeRect(0, 0, 336, 224)
        styleMask:NSWindowStyleMaskBorderless backing:NSBackingStoreBuffered defer:NO];
    _panel.backgroundColor = [NSColor clearColor];
    _panel.opaque = NO; _panel.hasShadow = NO; _panel.ignoresMouseEvents = YES;
    _panel.hidesOnDeactivate = NO;
    _panel.collectionBehavior = NSWindowCollectionBehaviorFullScreenAuxiliary | NSWindowCollectionBehaviorTransient;
    _canvas = [[VLCTimelinePreviewCanvas alloc] initWithFrame:_panel.contentView.bounds];
    _canvas.wantsLayer = YES; _panel.contentView = _canvas;
    _card = [[NSView alloc] initWithFrame:NSMakeRect(8, 8, 336, 224)];
    _canvas.card = _card; [_canvas addSubview:_card];
    _imageView = [[NSImageView alloc] initWithFrame:NSMakeRect(8, 35, 320, 180)];
    _imageView.imageScaling = NSImageScaleProportionallyUpOrDown;
    [_card addSubview:_imageView];
    _timeLabel = [self labelWithFrame:NSMakeRect(8, 8, 108, 20) font:[NSFont monospacedDigitSystemFontOfSize:12 weight:NSFontWeightMedium]];
    _stateLabel = [self labelWithFrame:NSMakeRect(117, 8, 211, 20) font:[NSFont systemFontOfSize:11]];
    [_stateLabel setAlignment:NSTextAlignmentRight];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(preferenceChanged:)
        name:VLCConfigurationChangedNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(contextChanged:)
        name:VLCTimelineContextChanged object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(hide)
        name:NSApplicationDidResignActiveNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(hide)
        name:NSApplicationWillTerminateNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(stopDiagnosticMonitoring)
        name:NSApplicationWillTerminateNotification object:nil];
    VLCTimelineTrace(@{@"event": @"adapter-init", @"has_slider": @(slider != nil), @"bounds": NSStringFromRect(slider.bounds), @"window_set": @(slider.window != nil)});
    if (getenv("VLC_TIMELINE_DIAGNOSTICS")) {
        __weak typeof(self) weakSelf = self;
        _diagnosticMonitor = [NSEvent addLocalMonitorForEventsMatchingMask:
            NSEventMaskMouseMoved | NSEventMaskLeftMouseDragged | NSEventMaskRightMouseDown | NSEventMaskRightMouseUp
            handler:^NSEvent *(NSEvent *event) {
                typeof(self) owner = weakSelf;
                NSSlider *target = owner.slider;
                if (owner && target.window && event.window == target.window) {
                    NSPoint point = [target convertPoint:event.locationInWindow fromView:nil];
                    NSPoint pointer = [target convertPoint:[target.window convertPointFromScreen:[NSEvent mouseLocation]] fromView:nil];
                    VLCTimelineTrace(@{@"event": @"input-observation", @"type": @(event.type),
                        @"event_point": NSStringFromPoint(point), @"pointer_point": NSStringFromPoint(pointer),
                        @"bounds": NSStringFromRect(target.bounds), @"visible_rect": NSStringFromRect(target.visibleRect),
                        @"tracking_attached": @([owner.trackingView.trackingAreas containsObject:owner.tracking])});
                }
                return event;
            }];
    }
    return self;
}
- (NSTextField *)labelWithFrame:(NSRect)frame font:(NSFont *)font
{
    NSTextField *label = [[NSTextField alloc] initWithFrame:frame]; label.editable = NO;
    label.selectable = NO; label.bordered = NO; label.drawsBackground = NO;
    label.textColor = [NSColor whiteColor]; label.font = font;
    [_card addSubview:label]; return label;
}
- (void)dealloc
{
    [self stopDiagnosticMonitoring];
    [_trackingView removeTrackingArea:_tracking]; [_visibilityTimer invalidate];
    [[NSNotificationCenter defaultCenter] removeObserver:self]; [_panel orderOut:nil];
}
- (void)refreshTracking
{
    NSSlider *slider = _slider;
    NSView *view = slider.superview ?: slider;
    NSRect rect = [view convertRect:VLCTimelineHoverBounds(slider) fromView:slider];
    if (_trackingView != view || !_tracking || !NSEqualRects(_tracking.rect, rect)) {
        [_trackingView removeTrackingArea:_tracking]; _trackingView = view;
        _tracking = [[NSTrackingArea alloc] initWithRect:rect
            options:NSTrackingMouseEnteredAndExited | NSTrackingMouseMoved | NSTrackingActiveAlways |
                    NSTrackingEnabledDuringMouseDrag owner:self userInfo:nil];
        [view addTrackingArea:_tracking];
    }
    // Layout can change beneath a stationary pointer without a mouse event.
    // Recompute both the demand and panel position from the current screen point.
    if (_hovering) {
        _point = [slider convertPoint:[slider.window convertPointFromScreen:[NSEvent mouseLocation]] fromView:nil];
        _hoverStarted = [[NSProcessInfo processInfo] systemUptime];
        [self schedulePreviewRefresh];
    }
}
- (void)stopDiagnosticMonitoring
{
    if (_diagnosticMonitor) { [NSEvent removeMonitor:_diagnosticMonitor]; _diagnosticMonitor = nil; }
}
// Follow VLC's native preference convention: inherit an explicit command-line
// override, otherwise read the current config (including preferences Save).
- (BOOL)previewPreferenceEnabled
{
    BOOL enabled = getIntf() && var_InheritBool(getIntf(), "macosx-timeline-previews");
    if (enabled != _previewsEnabled) {
        _previewsEnabled = enabled;
        _slider.toolTip = enabled ? nil : _originalToolTip;
        if (!enabled) [self hide];
    }
    return enabled;
}
- (void)preferenceChanged:(NSNotification *)notification
{
    [[VLCThumbnailService sharedService] prepareContext:[[VLCTimelineContext sharedContext] snapshot] enabled:[self previewPreferenceEnabled]];
    [self previewPreferenceEnabled];
    // Saving preferences must cancel any pending presentation on every surface.
    [self hide];
}
- (void)mouseEntered:(NSEvent *)event {
    if (![self previewPreferenceEnabled]) return;
    VLCTimelineTrace(@{@"event": @"mouse-enter"});
    _slider.window.acceptsMouseMovedEvents = YES;
    _hovering = YES; [self mouseMoved:event];
}
- (void)mouseMoved:(NSEvent *)event
{
    if (![self previewPreferenceEnabled]) return;
    _hovering = YES; _point = [_slider convertPoint:event.locationInWindow fromView:nil];
    NSPoint pointer = [_slider convertPoint:[_slider.window convertPointFromScreen:[NSEvent mouseLocation]] fromView:nil];
    VLCTimelineTrace(@{@"event": @"mouse-move", @"event_point": NSStringFromPoint(_point),
        @"pointer_point": NSStringFromPoint(pointer), @"bounds": NSStringFromRect(_slider.bounds),
        @"visible_rect": NSStringFromRect(_slider.visibleRect), @"enabled": @(_slider.enabled),
        @"hidden": @(_slider.hiddenOrHasHiddenAncestor), @"window_set": @(_slider.window != nil),
        @"hit_bounds": NSStringFromRect(VLCTimelineHoverBounds(_slider)),
        @"tracking_attached": @([_trackingView.trackingAreas containsObject:_tracking])});
    _hoverStarted = [[NSProcessInfo processInfo] systemUptime];
    [self schedulePreviewRefresh];
    if (!_hovering) return;
    if (!_visibilityTimer) _visibilityTimer = [NSTimer scheduledTimerWithTimeInterval:0.1 target:self
        selector:@selector(checkVisibility:) userInfo:nil repeats:YES];
}
- (void)mouseExited:(NSEvent *)event { [self hide]; }
- (void)checkVisibility:(NSTimer *)timer
{
    NSSlider *slider = _slider;
    if (![self previewPreferenceEnabled]) return;
    if (!slider.window.visible || slider.hiddenOrHasHiddenAncestor || slider.window.alphaValue < 0.1 ||
        !slider.enabled) {
        VLCTimelineTrace(@{@"event": @"visibility-hide", @"window_visible": @(slider.window.visible),
          @"hidden": @(slider.hiddenOrHasHiddenAncestor), @"alpha": @(slider.window.alphaValue),
          @"app_active": @(NSApp.active), @"enabled": @(slider.enabled)});
        [self hide]; return; }
    NSPoint pointer = [slider convertPoint:[slider.window convertPointFromScreen:[NSEvent mouseLocation]] fromView:nil];
    if (!NSPointInRect(pointer, VLCTimelineHoverBounds(slider))) {
        VLCTimelineTrace(@{@"event": @"pointer-hide", @"pointer_x": @(pointer.x), @"pointer_y": @(pointer.y),
          @"bounds": NSStringFromRect(slider.bounds), @"mouse": NSStringFromPoint([NSEvent mouseLocation])});
        [self hide];
    }
}
- (void)contextChanged:(NSNotification *)notification
{
    if (_refreshing) return;
    _demand = -1; _generation = nil; _presentation++;
    _imageView.image = nil; [_panel orderOut:nil];
    if (_hovering) [self schedulePreviewRefresh];
}
- (void)hide
{
    [_previewRefreshTimer invalidate]; _previewRefreshTimer = nil;
    BOOL visible = _panel.visible;
    _hovering = NO; _presentation++; _demand = -1; _generation = nil;
    _imageView.image = nil; [_panel orderOut:nil];
    [_visibilityTimer invalidate]; _visibilityTimer = nil;
    if (visible) VLCTimelineTrace(@{ @"event": @"hide" });
    [[VLCThumbnailService sharedService] cancelRequest:_requestToken]; _requestToken = 0;
}
// Coalesce pointer bursts without moving the first scheduled deadline.
// Timers may run late; this is a presentation opportunity, not an input-priority
// guarantee. Invalidating immediately prevents an old completion from winning
// while the latest pointer/context is waiting for its refresh.
- (void)schedulePreviewRefresh
{
    if (![self previewPreferenceEnabled] || !_hovering) return;
    // Preserve same-bucket work and its callback across ordinary pointer jitter.
    // Latest intent is recomputed on the next coalesced presentation tick.
    if (_previewRefreshTimer.valid) return;
    __weak VLCTimelineInteractionController *weakSelf = self;
    _previewRefreshTimer = [NSTimer timerWithTimeInterval:0.016 repeats:NO block:^(NSTimer *timer) {
        VLCTimelineInteractionController *self = weakSelf;
        if (!self) return;
        self.previewRefreshTimer = nil;
        NSSlider *slider = self.slider;
        if (![self previewPreferenceEnabled] || !self.hovering || !NSApp.active || !slider.window.visible ||
            slider.hiddenOrHasHiddenAncestor || slider.window.alphaValue < 0.1 || !slider.enabled) {
            [self hide]; return;
        }
        self.point = [slider convertPoint:[slider.window convertPointFromScreen:[NSEvent mouseLocation]] fromView:nil];
        [self updatePreview];
    }];
    [[NSRunLoop mainRunLoop] addTimer:_previewRefreshTimer forMode:NSRunLoopCommonModes];
}
- (void)updatePreview
{
    NSSlider *slider = _slider;
    if (![self previewPreferenceEnabled] || !NSApp.active || !_hovering || !slider.window || slider.hiddenOrHasHiddenAncestor || !slider.enabled ||
        !NSPointInRect(_point, VLCTimelineHoverBounds(slider))) { [self hide]; return; }
    _refreshing = YES; NSDictionary *context = [[VLCTimelineContext sharedContext] snapshot]; _refreshing = NO;
    int64_t duration = [context[@"duration"] longLongValue];
    VLCTimelineTrace(@{@"event": @"context", @"duration": @(duration), @"eligible": context[@"eligible"] ?: @NO, @"ordinal": context[@"videoOrdinal"] ?: @(-1)});
    double left, right;
    if (!VLCTimelineTrackBounds(slider, &left, &right)) { [self hide]; return; }
    int64_t us = VLCTimelineTimeForPoint(_point.x, left, right, duration);
    if (us < 0) { [self hide]; return; }
    int64_t seconds = us / 1000000;
    _timeLabel.stringValue = seconds >= 3600 ? [NSString stringWithFormat:@"%lld:%02lld:%02lld", seconds / 3600, seconds / 60 % 60, seconds % 60]
                                               : [NSString stringWithFormat:@"%02lld:%02lld", seconds / 60, seconds % 60];
    NSPoint screenPoint = [slider.window convertPointToScreen:[slider convertPoint:NSMakePoint(_point.x, NSMaxY(slider.bounds)) toView:nil]];
    NSRect screen = NSInsetRect(slider.window.screen.visibleFrame, 8, 8);
    if (NSWidth(screen) < 336 || NSHeight(screen) < 224) { [self hide]; return; }
    NSRect hoverBounds = VLCTimelineHoverBounds(slider);
    NSPoint leftPoint = [slider.window convertPointToScreen:[slider convertPoint:NSMakePoint(NSMinX(hoverBounds), NSMaxY(slider.bounds)) toView:nil]];
    NSPoint rightPoint = [slider.window convertPointToScreen:[slider convertPoint:NSMakePoint(NSMaxX(hoverBounds), NSMaxY(slider.bounds)) toView:nil]];
    CGFloat firstX = fmax(NSMinX(screen), fmin(NSMaxX(screen) - 336, leftPoint.x - 168));
    CGFloat lastX = fmax(NSMinX(screen), fmin(NSMaxX(screen) - 336, rightPoint.x - 168));
    CGFloat cardX = fmax(NSMinX(screen), fmin(NSMaxX(screen) - 336, screenPoint.x - 168));
    CGFloat cardY = fmin(NSMaxY(screen) - 224, screenPoint.y + 12);
    NSRect frame = NSMakeRect(firstX - 8, cardY - 8, lastX - firstX + 352, 240);
    // Stable across ordinary pointer movement; only geometry changes resize or
    // move the external host needed by small detached control windows.
    if (!NSEqualRects(_panel.frame, frame)) [_panel setFrame:frame display:NO];
    NSRect oldCard = _card.frame;
    [_card setFrameOrigin:NSMakePoint(cardX - frame.origin.x, 8)];
    [_canvas setNeedsDisplayInRect:NSUnionRect(NSInsetRect(oldCard, -8, -8), NSInsetRect(_card.frame, -8, -8))];
    if (_panel.parentWindow != slider.window) {
        [_panel.parentWindow removeChildWindow:_panel]; [slider.window addChildWindow:_panel ordered:NSWindowAbove];
    }
    _panel.level = MAX(NSFloatingWindowLevel, slider.window.level + 1); [_panel orderFront:nil];
    if (![context[@"eligible"] boolValue]) {
        _presentation++; _demand = -1; _generation = nil;
        [[VLCThumbnailService sharedService] cancelRequest:_requestToken]; _requestToken = 0;
        _imageView.image = nil; _stateLabel.stringValue = @"Preview unavailable"; return;
    }
    int64_t bucket = VLCTimelineBucket(us, duration);
    NSString *generation = context[@"generation"];
    if (_demand == bucket && [_generation isEqualToString:generation]) return;
        BOOL sameContext = [_generation isEqualToString:generation];
    int64_t bridgeDistance = VLCThumbnailBridgeDistance(duration);
    if (!sameContext || llabs(_displayedActual - bucket) > bridgeDistance) _imageView.image = nil;
    _demand = bucket; _generation = generation;
    _stateLabel.stringValue = _imageView.image ? [NSString stringWithFormat:@"Keyframe %lld:%02lld · Preparing", _displayedActual / 60000000, _displayedActual / 1000000 % 60] : @"Preparing…";
    NSUInteger presentation = ++_presentation; double started = _hoverStarted;
    VLCTimelineTrace(@{ @"event": @"hover", @"requested_us": @(us), @"bucket_us": @(bucket),
                       @"generation": generation, @"duration_us": @(duration),
                       @"window": slider.window.title ?: @"", @"point_x": @(_point.x), @"left": @(left), @"right": @(right) });
    __weak typeof(self) weakSelf = self;
    _requestToken = [[VLCThumbnailService sharedService] requestURL:context[@"url"] generation:generation
        videoOrdinal:[context[@"videoOrdinal"] integerValue] videoCount:[context[@"videoCount"] integerValue] time:bucket completion:^(NSImage *image, NSDictionary *result) {
        typeof(self) strongSelf = weakSelf;
        if (!strongSelf || ![strongSelf previewPreferenceEnabled] || !strongSelf.hovering || strongSelf.presentation != presentation ||
            ![strongSelf.generation isEqualToString:generation]) return;
        int64_t actual = [result[@"actual_us"] longLongValue];
        if (!image || actual < 0 || actual >= duration) {
            strongSelf.imageView.image = nil;
            NSString *error = result[@"error"];
            if ([result[@"preparing"] boolValue])
                strongSelf.stateLabel.stringValue = [error isEqual:@"timeout"] ? @"Slow source · Retrying…" : @"Preparing · Retrying…";
            else if ([error isEqual:@"file-unavailable"] || [error isEqual:@"invalid_input"])
                strongSelf.stateLabel.stringValue = @"Video unavailable";
            else if ([error isEqual:@"timeout"])
                strongSelf.stateLabel.stringValue = @"Source too slow · Try again";
            else if ([error isEqual:@"media_changed"])
                strongSelf.stateLabel.stringValue = @"Video changed · Reopen";
            else strongSelf.stateLabel.stringValue = @"Preview unavailable";
        } else {
            strongSelf.imageView.image = image; strongSelf.displayedActual = actual;
            NSString *pending = [result[@"verification_pending"] boolValue] ? @" · Checking source…" : [result[@"preparing"] boolValue] ? @" · Preparing" : @"";
            strongSelf.stateLabel.stringValue = [NSString stringWithFormat:@"Keyframe %lld:%02lld%@", actual / 60000000, actual / 1000000 % 60, pending];
        }
        VLCTimelineTrace(@{ @"event": @"display", @"generation": generation, @"requested_us": @(us),
                           @"actual_us": @(actual), @"ok": @(strongSelf.imageView.image != nil),
                           @"cache": result[@"cache"] ?: @"error",
                           @"verification_pending": @([result[@"verification_pending"] boolValue]),
                           @"preparing": @([result[@"preparing"] boolValue]),
                           @"elapsed_ms": @(([[NSProcessInfo processInfo] systemUptime] - started) * 1000) });
    }];
}
@end
