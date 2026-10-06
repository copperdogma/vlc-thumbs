// SPDX-License-Identifier: GPL-2.0-or-later
#import "VLCTimelineContext.h"
#import "VLCMain.h"
#import "VLCThumbnailService.h"
NSString * const VLCTimelineContextChanged = @"VLCTimelineContextChanged";

@interface VLCTimelineContext ()
@property NSString *session;
@property NSUInteger generation;
@property uintptr_t inputIdentity;
@property NSDictionary *current;
@end
@implementation VLCTimelineContext
+ (instancetype)sharedContext
{
    static VLCTimelineContext *context; static dispatch_once_t once;
    dispatch_once(&once, ^{ context = [[self alloc] init]; }); return context;
}
- (instancetype)init
{
    self = [super init]; if (self) {
        _session = [NSUUID UUID].UUIDString; _current = @{};
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(refresh)
            name:VLCInputChangedNotification object:nil];
    } return self;
}
- (void)invalidate
{
    NSAssert([NSThread isMainThread], @"Timeline context is main-thread");
    _generation++; _inputIdentity = 0; _current = @{};
    [[VLCThumbnailService sharedService] cancel];
    [[NSNotificationCenter defaultCenter] postNotificationName:VLCTimelineContextChanged object:self];
}
- (void)refresh
{
    NSAssert([NSThread isMainThread], @"Timeline context is main-thread");
    input_thread_t *input = pl_CurrentInput(getIntf());
    if (!input) { if (_inputIdentity || _current.count) [self invalidate]; return; }
    char *uri = input_item_GetURI(input_GetItem(input));
    NSURL *url = uri ? [NSURL URLWithString:[NSString stringWithUTF8String:uri]] : nil; free(uri);
    int64_t duration = input_item_GetDuration(input_GetItem(input));
    BOOL seekable = var_GetBool(input, "can-seek");
    int selected = var_GetInteger(input, "video-es");
    NSInteger ordinal = -1, count = 0;
    vlc_value_t values, labels;
    if (var_Change(input, "video-es", VLC_VAR_GETCHOICES, &values, &labels) == VLC_SUCCESS) {
        for (int i = 0; i < values.p_list->i_count; i++) {
            int value = values.p_list->p_values[i].i_int;
            if (value < 0) continue;
            if (value == selected) ordinal = count;
            count++;
        }
        var_FreeList(&values, &labels);
    }
    uintptr_t identity = (uintptr_t)input;
    vlc_object_release(input);
    if (_inputIdentity != identity || ![_current[@"url"] isEqual:url] || [_current[@"videoID"] intValue] != selected) {
        _generation++; _inputIdentity = identity;
    }
    NSString *generation = [NSString stringWithFormat:@"%@-%lu", _session, (unsigned long)_generation];
    BOOL eligible = url.isFileURL && duration > 0 && seekable && ordinal >= 0;
    NSMutableDictionary *next = [@{ @"generation": generation, @"duration": @(MAX(duration, 0)),
        @"seekable": @(seekable), @"eligible": @(eligible), @"videoOrdinal": @(ordinal),
        @"videoID": @(selected), @"videoCount": @(count) } mutableCopy];
    if (url) next[@"url"] = url;
    BOOL changed = ![_current isEqualToDictionary:next]; _current = next;
    [[VLCThumbnailService sharedService] prepareContext:_current enabled:getIntf() && var_InheritBool(getIntf(), "macosx-timeline-previews")];
    if (changed) [[NSNotificationCenter defaultCenter] postNotificationName:VLCTimelineContextChanged object:self];
}
- (NSDictionary *)snapshot { [self refresh]; return [_current copy]; }
@end
