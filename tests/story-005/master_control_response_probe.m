#import <signal.h>
// SPDX-License-Identifier: GPL-2.0-or-later
// Master-specific adaptation of Story002 control_response_probe.m; old source retained.
// Development-only actual-display crop observer for ordinary VLC controls.
// Separate from the qualified preview probe. No windows/audio/microphone/cursor.
// Emits measurements only; Python owns independent templates and judgments.
#import <AppKit/AppKit.h>
#import <ApplicationServices/ApplicationServices.h>
#import <ScreenCaptureKit/ScreenCaptureKit.h>
#import <CoreMedia/CoreMedia.h>
#import <CoreVideo/CoreVideo.h>
#import <ImageIO/ImageIO.h>
#import <mach/mach_time.h>
#import <math.h>
#import <stdint.h>
#import <stdio.h>
#import <stdlib.h>
#import <string.h>
#import <limits.h>
#import <errno.h>
#import <sys/stat.h>
#import <unistd.h>
#import <pthread.h>
#import <stdatomic.h>

static NSString *ExpectedBundleID;
static NSUInteger BrightMinimum=230, KnobMinimum=6, KnobMaximum=32;
static double Now(void) { return NSProcessInfo.processInfo.systemUptime; }
static BOOL WriteJSON(FILE *out,NSDictionary *row) {
    NSData *data=[NSJSONSerialization dataWithJSONObject:row options:NSJSONWritingSortedKeys error:nil];
    if(!data)return NO;fwrite(data.bytes,1,data.length,out);fputc('\n',out);fflush(out);return YES;
}
static BOOL ParseRect(const char *text,CGRect *out) {
    double v[4];const char *p=text;
    for(int i=0;i<4;i++){char *end=NULL;v[i]=strtod(p,&end);if(end==p||!isfinite(v[i]))return NO;if(i<3){if(*end!=',')return NO;p=end+1;}else if(*end)return NO;}
    *out=CGRectMake(v[0],v[1],v[2],v[3]);return v[2]>0&&v[3]>0;
}
static BOOL ParsePoint(const char *text,CGPoint *out) {
    char *end=NULL;double x=strtod(text,&end);if(end==text||*end!=','||!isfinite(x))return NO;
    const char *ys=end+1;double y=strtod(ys,&end);if(end==ys||*end||!isfinite(y))return NO;*out=CGPointMake(x,y);return YES;
}
static NSString *CanonicalFreshWorkFile(NSString *input) {
    if(![input isKindOfClass:NSString.class]||!input.isAbsolutePath||![input isEqualToString:input.stringByStandardizingPath])return nil;
    char cwd[PATH_MAX];if(!getcwd(cwd,sizeof(cwd)))return nil;char *root=realpath(cwd,NULL);if(!root)return nil;
    NSString *rootPath=[NSString stringWithUTF8String:root];free(root);
    if(![[NSFileManager defaultManager] fileExistsAtPath:[rootPath stringByAppendingPathComponent:@"AGENTS.md"]])return nil;
    NSString *workPath=[rootPath stringByAppendingPathComponent:@"work"];
    char *resolvedWork=realpath(workPath.fileSystemRepresentation,NULL);if(!resolvedWork)return nil;
    NSString *canonicalWork=[NSString stringWithUTF8String:resolvedWork];free(resolvedWork);
    if(![canonicalWork isEqualToString:workPath])return nil;
    NSString *parent=input.stringByDeletingLastPathComponent;char *resolvedParent=realpath(parent.fileSystemRepresentation,NULL);if(!resolvedParent)return nil;
    NSString *canonicalParent=[NSString stringWithUTF8String:resolvedParent];free(resolvedParent);
    if(![canonicalParent isEqualToString:parent]||
       !([canonicalParent isEqualToString:canonicalWork]||[canonicalParent hasPrefix:[canonicalWork stringByAppendingString:@"/"]]))return nil;
    struct stat st;if(lstat(input.fileSystemRepresentation,&st)==0||errno!=ENOENT)return nil;return input;
}
static BOOL ParseWindowBounds(NSDictionary *entry,CGRect *bounds) {
    NSDictionary *b=entry[(id)kCGWindowBounds];if(![b isKindOfClass:NSDictionary.class])return NO;
    double x=[b[@"X"] doubleValue],y=[b[@"Y"] doubleValue],w=[b[@"Width"] doubleValue],h=[b[@"Height"] doubleValue];
    if(!isfinite(x)||!isfinite(y)||!isfinite(w)||!isfinite(h)||w<=0||h<=0)return NO;*bounds=CGRectMake(x,y,w,h);return YES;
}
static BOOL FindMainWindow(pid_t pid,CGRect rect,CGPoint point,CGRect *parent) {
    NSArray *list=CFBridgingRelease(CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly,kCGNullWindowID));
    for(NSDictionary *entry in list){if([entry[(id)kCGWindowOwnerPID] intValue]!=pid||[entry[(id)kCGWindowLayer] intValue]!=0)continue;CGRect b;
        if(ParseWindowBounds(entry,&b)&&CGRectContainsRect(b,rect)&&CGRectContainsPoint(b,point)){*parent=b;return YES;}}
    return NO;
}
static BOOL OwnAXHit(pid_t pid,CGPoint point,NSString **error) {
    AXUIElementRef system=AXUIElementCreateSystemWide(),hit=NULL;pid_t hitPID=0;
    AXError result=AXUIElementCopyElementAtPosition(system,(float)point.x,(float)point.y,&hit);if(result==kAXErrorSuccess&&hit)AXUIElementGetPid(hit,&hitPID);
    if(hit)CFRelease(hit);CFRelease(system);if(result!=kAXErrorSuccess||hitPID!=pid){*error=[NSString stringWithFormat:@"AX point ownership failed (error=%d pid=%d expected=%d)",result,hitPID,pid];return NO;}return YES;
}
// Target-process routing receipt, not an AppKit action acknowledgment. Only
// this invocation's nonce-tagged events are retained; unrelated input is ignored.
typedef struct { CGEventType type; CGPoint point; double received; uint64_t timestamp; } RoutedEvent;
typedef struct { pid_t pid; int64_t tag; atomic_bool ready, stop, failed; size_t count; RoutedEvent events[8]; } RoutingTap;
static CGEventRef RouteCallback(CGEventTapProxy proxy,CGEventType type,CGEventRef event,void *context) {
    RoutingTap *tap=context;
    if(type==kCGEventTapDisabledByTimeout||type==kCGEventTapDisabledByUserInput){atomic_store(&tap->failed,true);return event;}
    if(!event||CGEventGetIntegerValueField(event,kCGEventSourceUserData)!=tap->tag)return event;
    if(type!=kCGEventMouseMoved&&type!=kCGEventLeftMouseDown&&type!=kCGEventLeftMouseUp)return event;
    if(tap->count>=8){atomic_store(&tap->failed,true);return event;}
    tap->events[tap->count++]=(RoutedEvent){type,CGEventGetLocation(event),Now(),CGEventGetTimestamp(event)};
    return event;
}
static void *RouteThread(void *context) { @autoreleasepool {
    RoutingTap *tap=context;
    CGEventMask mask=CGEventMaskBit(kCGEventMouseMoved)|CGEventMaskBit(kCGEventLeftMouseDown)|CGEventMaskBit(kCGEventLeftMouseUp);
    CFMachPortRef port=CGEventTapCreateForPid(tap->pid,kCGHeadInsertEventTap,kCGEventTapOptionListenOnly,mask,RouteCallback,tap);
    CFRunLoopSourceRef source=port?CFMachPortCreateRunLoopSource(NULL,port,0):NULL;
    if(!source){if(port)CFRelease(port);atomic_store(&tap->failed,true);atomic_store(&tap->ready,true);return NULL;}
    CFRunLoopAddSource(CFRunLoopGetCurrent(),source,kCFRunLoopDefaultMode);
    CGEventTapEnable(port,true); if(!CGEventTapIsEnabled(port))atomic_store(&tap->failed,true);
    atomic_store(&tap->ready,true);
    while(!atomic_load(&tap->stop)&&!atomic_load(&tap->failed))CFRunLoopRunInMode(kCFRunLoopDefaultMode,.05,false);
    CFRunLoopRemoveSource(CFRunLoopGetCurrent(),source,kCFRunLoopDefaultMode);
    CFMachPortInvalidate(port);CFRelease(source);CFRelease(port);return NULL;
}}
// Retain the pre-input slider, since moving its knob can change the point-hit
// leaf. Parent resolution is bounded to eight links and never crosses PID.
static NSDictionary *AXPhase(pid_t pid,CGPoint point,NSString *phase,AXUIElementRef heldSlider,AXUIElementRef *resolvedSlider) {
    double begin=Now(); AXUIElementRef system=AXUIElementCreateSystemWide(),hit=NULL;pid_t hitPID=0;
    AXError hitError=AXUIElementCopyElementAtPosition(system,point.x,point.y,&hit);
    CFTypeRef hitRole=NULL; AXError hitRoleError=kAXErrorFailure;
    if(hitError==kAXErrorSuccess&&hit){AXUIElementGetPid(hit,&hitPID);hitRoleError=AXUIElementCopyAttributeValue(hit,kAXRoleAttribute,&hitRole);}
    id actualHitRole=hitRole&&CFGetTypeID(hitRole)==CFStringGetTypeID()?(__bridge id)hitRole:(id)NSNull.null;
    AXUIElementRef slider=heldSlider?(AXUIElementRef)CFRetain(heldSlider):NULL; NSInteger depth=-1;
    if(!slider&&resolvedSlider&&hitError==kAXErrorSuccess&&hitPID==pid){
        AXUIElementRef current=(AXUIElementRef)CFRetain(hit);
        for(NSInteger i=0;i<=8;i++){
            pid_t currentPID=0;CFTypeRef role=NULL;
            AXError pidError=AXUIElementGetPid(current,&currentPID);
            AXError roleError=AXUIElementCopyAttributeValue(current,kAXRoleAttribute,&role);
            BOOL found=pidError==kAXErrorSuccess&&currentPID==pid&&roleError==kAXErrorSuccess&&role&&CFEqual(role,kAXSliderRole);
            if(role)CFRelease(role);
            if(found){slider=current;depth=i;break;}
            if(pidError!=kAXErrorSuccess||currentPID!=pid||i==8){CFRelease(current);break;}
            CFTypeRef parent=NULL;AXError parentError=AXUIElementCopyAttributeValue(current,kAXParentAttribute,&parent);
            CFRelease(current);
            if(parentError!=kAXErrorSuccess||!parent||CFGetTypeID(parent)!=AXUIElementGetTypeID()){if(parent)CFRelease(parent);break;}
            current=(AXUIElementRef)parent;
        }
        if(slider)*resolvedSlider=(AXUIElementRef)CFRetain(slider);
    }
    pid_t sliderPID=0;CFTypeRef role=NULL,value=NULL;
    AXError pidError=kAXErrorFailure,roleError=kAXErrorFailure,valueError=kAXErrorFailure;
    if(slider){pidError=AXUIElementGetPid(slider,&sliderPID);roleError=AXUIElementCopyAttributeValue(slider,kAXRoleAttribute,&role);valueError=AXUIElementCopyAttributeValue(slider,kAXValueAttribute,&value);}
    BOOL isSlider=roleError==kAXErrorSuccess&&role&&CFEqual(role,kAXSliderRole);double number=NAN;
    if(valueError==kAXErrorSuccess&&value&&CFGetTypeID(value)==CFNumberGetTypeID())CFNumberGetValue(value,kCFNumberDoubleType,&number);
    NSString *identity=slider?[NSString stringWithFormat:@"%p",(void *)slider]:nil;
    NSDictionary *row=@{@"kind":@"ax_phase",@"phase":phase,@"query_begin_uptime_s":@(begin),@"query_end_uptime_s":@(Now()),
        @"owned":@(hitError==kAXErrorSuccess&&hitPID==pid&&pidError==kAXErrorSuccess&&sliderPID==pid&&isSlider&&valueError==kAXErrorSuccess&&isfinite(number)),
        @"point_hit_owned":@(hitError==kAXErrorSuccess&&hitPID==pid),@"point_hit_pid":@(hitPID),@"point_hit_error":@(hitError),
        @"point_hit_role":actualHitRole,@"point_hit_role_error":@(hitRoleError),
        @"slider_pid":@(sliderPID),@"slider_pid_error":@(pidError),@"slider_role":@(isSlider),@"slider_role_error":@(roleError),
        @"slider_element_identity":identity?:(id)NSNull.null,@"queries_held_pre_slider":@(heldSlider!=NULL),@"resolved_parent_depth":@(depth),
        @"value_error":@(valueError),@"slider_value":isfinite(number)?@(number):(id)NSNull.null};
    if(value)CFRelease(value);if(role)CFRelease(role);if(slider)CFRelease(slider);if(hitRole)CFRelease(hitRole);if(hit)CFRelease(hit);CFRelease(system);
    return row;
}
static void PumpMainRunLoop(void) { CFRunLoopRunInMode(kCFRunLoopDefaultMode,0.001,false); }
static NSString *ApplicationExecutablePath(NSRunningApplication *app) {
    return app.executableURL.URLByResolvingSymlinksInPath.path;
}
static BOOL RetainedTargetAlive(NSRunningApplication *target,pid_t pid,NSString *expectedPath) {
    return target && target.processIdentifier==pid && !target.terminated && kill(pid,0)==0 &&
        [target.bundleIdentifier isEqualToString:ExpectedBundleID] &&
        [ApplicationExecutablePath(target) isEqualToString:expectedPath];
}
static BOOL RetainedTargetForeground(NSRunningApplication *target,NSRunningApplication *front,pid_t pid,NSString *expectedPath) {
    return RetainedTargetAlive(target,pid,expectedPath) && front && [front isEqual:target] &&
        front.processIdentifier==pid && [front.bundleIdentifier isEqualToString:ExpectedBundleID];
}
static BOOL WaitPumpingRunLoop(dispatch_semaphore_t done,double timeout) {
    double deadline=Now()+timeout;
    while(dispatch_semaphore_wait(done,DISPATCH_TIME_NOW)){
        if(Now()>=deadline)return NO;
        [[NSRunLoop currentRunLoop] runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.001]];
    }
    return YES;
}
static BOOL FindDisplay(CGRect rect,SCDisplay **display,NSError **error) {
    __block SCShareableContent *content=nil;__block NSError *shareError=nil;dispatch_semaphore_t done=dispatch_semaphore_create(0);
    [SCShareableContent getShareableContentWithCompletionHandler:^(SCShareableContent *value,NSError *e){content=value;shareError=e;dispatch_semaphore_signal(done);}];
    if(!WaitPumpingRunLoop(done,3)){*error=[NSError errorWithDomain:@"ContinuousVisibleProbe" code:1 userInfo:@{NSLocalizedDescriptionKey:@"shareable-content timeout"}];return NO;}
    if(shareError){*error=shareError;return NO;}
    for(SCDisplay *candidate in content.displays)if(CGRectContainsRect(candidate.frame,rect)){*display=candidate;return YES;}
    *error=[NSError errorWithDomain:@"ContinuousVisibleProbe" code:2 userInfo:@{NSLocalizedDescriptionKey:@"crop must fit wholly on one ScreenCaptureKit display"}];return NO;
}
static NSString *HashPixels(const uint8_t *p,size_t len,size_t width,size_t height,size_t bpp,size_t row,double *mean,size_t *sampleCount) {
    uint64_t hash=14695981039346656037ULL,total=0;size_t samples=0,stride=MAX((size_t)1,(size_t)sqrt((double)(width*height)/4096.0));
    if(!p||!bpp||!row){if(mean)*mean=0;if(sampleCount)*sampleCount=0;return @"";}
    for(size_t y=0;y<height;y+=stride)for(size_t x=0;x<width;x+=stride){size_t at=y*row+x*bpp;if(at+bpp>len)continue;size_t colors=MIN((size_t)3,bpp);for(size_t c=0;c<colors;c++){hash=(hash^p[at+c])*1099511628211ULL;total+=p[at+c];}samples+=colors;}
    if(mean)*mean=samples?(double)total/samples:0;if(sampleCount)*sampleCount=samples;return [NSString stringWithFormat:@"%016llx",(unsigned long long)hash];
}
static NSDictionary *GenericImageStats(CGImageRef image) {
    size_t w=CGImageGetWidth(image),h=CGImageGetHeight(image),bpp=CGImageGetBitsPerPixel(image)/8,row=CGImageGetBytesPerRow(image);
    CFDataRef data=CGDataProviderCopyData(CGImageGetDataProvider(image));if(!data)return @{@"pixel_width":@(w),@"pixel_height":@(h),@"stats_error":@"no_provider_data"};
    double mean=0;size_t samples=0;NSString *hash=HashPixels(CFDataGetBytePtr(data),CFDataGetLength(data),w,h,bpp,row,&mean,&samples);CFRelease(data);
    return @{@"pixel_width":@(w),@"pixel_height":@(h),@"sample_hash_fnv1a64":hash,@"sample_mean":@(mean),@"sample_count":@(samples)};
}
// Light-style VLCSliderCell: normal/active knob fill1.0/.95 versus track
// .66-.75 (pinned setSliderStyleLight). This primitive intentionally supports
// only an explicitly calibrated bright-pill profile and fixed2x sRGB BGRA capture.
// Saved-image tests qualify classification only, never live ownership or response latency.
static NSDictionary *KnobPixels(const uint8_t *pixels,size_t length,size_t width,size_t height,size_t stride,CGRect crop,CGPoint point) {
    long middle=lround((point.y-crop.origin.y)*2.0);
    NSMutableArray *rows=[NSMutableArray array],*widths=[NSMutableArray array];
    double total=0,minCenter=INFINITY,maxCenter=-INFINITY; NSUInteger consistent=0; BOOL ambiguous=NO;
    if(!pixels||width>SIZE_MAX/4||stride<width*4||height>SIZE_MAX/stride||length<height*stride||middle<2||middle+2>=(long)height)
        return @{@"valid":@NO,@"present":@NO,@"reason":@"invalid_pixel_geometry",@"consistent_rows":@0};
    for(long y=middle-2;y<=middle+2;y++) {
        NSUInteger clusters=0,start=0,end=0; BOOL inside=NO;
        for(size_t x=0;x<=width;x++) {
            const uint8_t *pixel=x<width?pixels+(size_t)y*stride+x*4:NULL;
            BOOL bright=pixel&&pixel[0]>=BrightMinimum&&pixel[1]>=BrightMinimum&&pixel[2]>=BrightMinimum&&pixel[3]>=240;
            if(bright&&!inside){inside=YES;start=x;clusters++;}
            if(!bright&&inside){inside=NO;end=x-1;}
        }
        NSUInteger span=clusters==1?end-start+1:0;
        NSMutableDictionary *row=[@{@"pixel_y":@(y),@"clusters":@(clusters),@"width_pixels":@(span)} mutableCopy];
        if(clusters>1||(clusters==1&&(span<KnobMinimum||span>KnobMaximum)))ambiguous=YES;
        if(clusters==1&&span>=KnobMinimum&&span<=KnobMaximum) {
            double center=((double)start+(double)end+1.0)/2.0;
            row[@"center_pixels"]=@(center);row[@"xmin"]=@(start);row[@"xmax"]=@(end);
            minCenter=fmin(minCenter,center);maxCenter=fmax(maxCenter,center);total+=center;consistent++;
            [widths addObject:@(span)];
        }
        [rows addObject:row];
    }
    BOOL valid=!ambiguous&&consistent>=3&&maxCenter-minCenter<=2.0;
    NSMutableDictionary *result=[@{@"valid":@(valid),@"present":@(consistent>0),@"consistent_rows":@(consistent),
        @"widths_pixels":widths,@"rows":rows,@"ambiguous":@(ambiguous),@"calibrated_bright_pill_only":@YES,
        @"bright_rgb_min":@(BrightMinimum),@"alpha_min":@240,@"center_spread_pixels":consistent?@(maxCenter-minCenter):(id)NSNull.null} mutableCopy];
    if(valid)result[@"center_x_global_points"]=@(crop.origin.x+(total/consistent)/2.0);
    return result;
}
// Optional headless fixture exercise: two tones, gray bar, ambiguous clusters,
// and a geometrically valid old-position knob far from the expected new input.
static int PixelSelfTest(void) {
    const size_t w=480,h=56,stride=w*4;uint8_t *p=malloc(stride*h);if(!p)return 1;
    CGRect crop=CGRectMake(900,1016,240,28);CGPoint point=CGPointMake(955,1028);
    for(int mode=0;mode<5;mode++) {
        for(size_t i=0;i<w*h;i++){p[i*4]=p[i*4+1]=p[i*4+2]=190;p[i*4+3]=255;}
        if(mode!=2)for(size_t y=22;y<=26;y++)for(size_t x=100;x<120;x++)p[y*stride+x*4]=p[y*stride+x*4+1]=p[y*stride+x*4+2]=mode==1?242:255;
        if(mode==3)for(size_t y=22;y<=26;y++)for(size_t x=200;x<220;x++)p[y*stride+x*4]=p[y*stride+x*4+1]=p[y*stride+x*4+2]=255;
        NSDictionary *r=KnobPixels(p,stride*h,w,h,stride,crop,point);
        BOOL good=(mode==2||mode==3)?![r[@"valid"] boolValue]:([r[@"valid"] boolValue]&&fabs([r[@"center_x_global_points"] doubleValue]-955.)<0.001);
        if(mode==4)good=good&&fabs([r[@"center_x_global_points"] doubleValue]-1095.)>100.;
        if(!good){free(p);return 1;}
    }
    free(p);puts("pixel-self-test:5 cases passed");return 0;
}

static uint64_t DisplayTicks(NSDictionary *attachments) {
    id value=attachments[SCStreamFrameInfoDisplayTime];return [value respondsToSelector:@selector(unsignedLongLongValue)]?[value unsignedLongLongValue]:0;
}
static double MachSeconds(uint64_t ticks) { mach_timebase_info_data_t info;mach_timebase_info(&info);return (double)ticks*(double)info.numer/(double)info.denom/1e9; }


@interface ControlObserver : NSObject <SCStreamOutput,SCStreamDelegate>
@property pid_t pid;
@property(strong) NSRunningApplication *targetApplication;
@property(copy) NSString *expectedExecutablePath;
@property CGRect expectedParent;
@property CGRect crop;
@property CGPoint point;
@property size_t width, height;
@property FILE *output;
@property double inputT0, deadline;
@property BOOL postInput, finished;
@property NSUInteger frames, warmFrames, limit;
@property NSString *fatalError;
@property NSData *lastImageData;
@property size_t lastRowBytes;
@property BOOL saveLastImage;
@property BOOL phaseAX;
@property NSLock *lock;
- (void)write:(NSDictionary *)row;
@end
@implementation ControlObserver
- (instancetype)init { if((self=[super init])) _lock=[NSLock new]; return self; }
- (void)write:(NSDictionary *)row { [_lock lock]; WriteJSON(_output,row); [_lock unlock]; }
- (void)stream:(SCStream *)stream didStopWithError:(NSError *)error {
    if(error) { self.fatalError=error.localizedDescription;
        [self write:@{@"kind":@"stream_error",@"callback_received_uptime_s":@(Now()),@"error":self.fatalError}]; self.finished=YES; }
}
- (void)stream:(SCStream *)stream didOutputSampleBuffer:(CMSampleBufferRef)sampleBuffer ofType:(SCStreamOutputType)type {
    @autoreleasepool {
    if(type!=SCStreamOutputTypeScreen)return;
    double receipt=Now();
    CFArrayRef raw=CMSampleBufferGetSampleAttachmentsArray(sampleBuffer,false);
    NSDictionary *attachments=raw&&CFArrayGetCount(raw)?CFBridgingRelease(CFRetain(CFArrayGetValueAtIndex(raw,0))):@{};
    NSInteger status=[attachments[SCStreamFrameInfoStatus] respondsToSelector:@selector(integerValue)]?[attachments[SCStreamFrameInfoStatus] integerValue]:-1;
    double pts=CMTimeGetSeconds(CMSampleBufferGetPresentationTimeStamp(sampleBuffer)); if(!isfinite(pts))pts=-1;
    uint64_t ticks=DisplayTicks(attachments);
    double appQueryBegin=Now();
    NSRunningApplication *app=[NSRunningApplication runningApplicationWithProcessIdentifier:self.pid]; CGRect parent=CGRectNull;
    NSString *bundle=app.bundleIdentifier; BOOL expectedBundle=[bundle isEqualToString:ExpectedBundleID];
    BOOL targetActive=app.active; BOOL targetTerminated=app.terminated; pid_t returnedPID=app.processIdentifier; BOOL osExists=kill(self.pid,0)==0; double appQueryEnd=Now();
    double frontQueryBegin=Now(); NSRunningApplication *front=NSWorkspace.sharedWorkspace.frontmostApplication; pid_t frontPID=front?front.processIdentifier:0; NSString *frontBundle=front.bundleIdentifier; double frontQueryEnd=Now();
    BOOL legacyActive=app&&expectedBundle&&targetActive;
    double retainedBegin=Now(); NSRunningApplication *target=self.targetApplication;
    BOOL retainedTerminated=target.terminated; NSString *retainedBundle=target.bundleIdentifier;
    NSString *retainedPath=ApplicationExecutablePath(target); pid_t retainedPID=target.processIdentifier;
    BOOL retainedOSExists=kill(self.pid,0)==0; BOOL retainedEqual=front && [front isEqual:target];
    BOOL active=RetainedTargetForeground(target,front,self.pid,self.expectedExecutablePath); double retainedEnd=Now();
    BOOL contained=FindMainWindow(self.pid,self.crop,self.point,&parent)&&CGRectEqualToRect(parent,self.expectedParent);
    BOOL axChecked=!self.phaseAX&&status==SCFrameStatusComplete;
    NSString *hitError=nil; double axBegin=Now(); BOOL hit=axChecked?OwnAXHit(self.pid,self.point,&hitError):NO; double axEnd=Now();
    BOOL ownerOK=active&&contained&&(self.phaseAX||status!=SCFrameStatusComplete||hit);
    NSMutableDictionary *row=[@{@"kind":self.postInput?@"display_frame":@"readiness_frame",
        @"index":@(self.frames),@"frame_status":@(status),@"presentation_pts_seconds":@(pts),
        @"presentation_pts_value":@(CMSampleBufferGetPresentationTimeStamp(sampleBuffer).value),
        @"presentation_pts_timescale":@(CMSampleBufferGetPresentationTimeStamp(sampleBuffer).timescale),
        @"display_time_mach_ticks":@(ticks),@"display_time_present":@(ticks>0),
        @"display_time_uptime_seconds":@(MachSeconds(ticks)),@"callback_received_uptime_s":@(receipt),
        @"retained_target_present":@((BOOL)(target!=nil)),@"retained_target_pid":@(retainedPID),@"retained_target_bundle":retainedBundle?:NSNull.null,@"retained_target_executable_path":retainedPath?:NSNull.null,@"expected_executable_path":self.expectedExecutablePath,@"retained_target_terminated":@(retainedTerminated),@"retained_target_os_exists":@(retainedOSExists),@"frontmost_equals_retained_target":@(retainedEqual),@"retained_target_query_begin_uptime_s":@(retainedBegin),@"retained_target_query_end_uptime_s":@(retainedEnd),@"frontmost_pid":@(frontPID),@"frontmost_bundle":frontBundle?:NSNull.null,@"frontmost_query_begin_uptime_s":@(frontQueryBegin),@"frontmost_query_end_uptime_s":@(frontQueryEnd),@"legacy_app_active":@(legacyActive),@"target_terminated":@(targetTerminated),@"target_os_exists":@(osExists),@"foreground_policy":@"workspace-frontmost-retained-instance-v4",@"observer_version":@5,@"ax_check_scope":self.phaseAX?@"phase-only-unqualified":@"complete-presentations-only",@"app_active":@(active),@"app_exists":@(app!=nil),@"app_bundle":bundle?:NSNull.null,@"bundle_expected":@(expectedBundle),@"target_active":@(targetActive),@"app_returned_pid":@(returnedPID),@"app_query_begin_uptime_s":@(appQueryBegin),@"app_query_end_uptime_s":@(appQueryEnd),@"parent_window_contains_crop":@(contained),@"ax_input_point_owned":self.phaseAX?@NO:(axChecked?@(hit):(id)NSNull.null),@"ax_checked_this_frame":@(axChecked),@"ax_mode":self.phaseAX?@"phase":@"per-frame",
        @"crop_screen_points":@[@(self.crop.origin.x),@(self.crop.origin.y),@(self.crop.size.width),@(self.crop.size.height)]} mutableCopy];
    if(axChecked){row[@"ax_query_begin_uptime_s"]=@(axBegin);row[@"ax_query_end_uptime_s"]=@(axEnd);}
    if(self.postInput) { row[@"input_t0_uptime_s"]=@(self.inputT0);
        row[@"input_to_callback_ms"]=@((receipt-self.inputT0)*1000);
        row[@"post_input_complete_presentation"]=@(status==SCFrameStatusComplete&&ticks>0&&MachSeconds(ticks)>=self.inputT0&&pts>=self.inputT0); }
    CVPixelBufferRef pixel=CMSampleBufferGetImageBuffer(sampleBuffer);
    row[@"pixel_width"]=@(pixel?CVPixelBufferGetWidth(pixel):0); row[@"pixel_height"]=@(pixel?CVPixelBufferGetHeight(pixel):0);
    if(status==SCFrameStatusComplete) {
        if(!pixel||CVPixelBufferGetPixelFormatType(pixel)!=kCVPixelFormatType_32BGRA||
           CVPixelBufferGetWidth(pixel)!=self.width||CVPixelBufferGetHeight(pixel)!=self.height) row[@"error"]=@"unexpected_complete_pixel_buffer";
        else {
            CVPixelBufferLockBaseAddress(pixel,kCVPixelBufferLock_ReadOnly);
            void *base=CVPixelBufferGetBaseAddress(pixel); size_t stride=CVPixelBufferGetBytesPerRow(pixel),length=stride*self.height;
            CGDataProviderRef provider=CGDataProviderCreateWithData(NULL,base,length,NULL);
            CGColorSpaceRef color=CGColorSpaceCreateWithName(kCGColorSpaceSRGB);
            CGImageRef image=CGImageCreate(self.width,self.height,8,32,stride,color,kCGImageAlphaPremultipliedFirst|kCGBitmapByteOrder32Little,provider,NULL,false,kCGRenderingIntentDefault);
            if(image) { row[@"result"]=GenericImageStats(image); row[@"knob"]=KnobPixels(base,length,self.width,self.height,stride,self.crop,self.point); if(!self.postInput&&ownerOK&&ticks>0&&MachSeconds(ticks)>0&&pts>=0)self.warmFrames++;
                if(self.saveLastImage){self.lastImageData=[NSData dataWithBytes:base length:length];self.lastRowBytes=stride;}
                CGImageRelease(image); }
            else row[@"error"]=@"could_not_wrap_pixel_buffer";
            if(color)CGColorSpaceRelease(color);if(provider)CGDataProviderRelease(provider);
            CVPixelBufferUnlockBaseAddress(pixel,kCVPixelBufferLock_ReadOnly);
        }
    }
    if(!ownerOK)row[@"error"]=hitError?:@"target_inactive_or_crop_left_owned_main_window";
    [self write:row];
    if(row[@"error"]){self.fatalError=row[@"error"];self.finished=YES;}
    if(self.postInput){self.frames++;if(self.frames>=self.limit||receipt>=self.deadline)self.finished=YES;}
    }
}
@end
static BOOL WaitForStart(SCStream *stream,NSError **error) {
    dispatch_semaphore_t done=dispatch_semaphore_create(0);__block NSError *failure=nil;
    [stream startCaptureWithCompletionHandler:^(NSError *e){failure=e;dispatch_semaphore_signal(done);}];
    if(!WaitPumpingRunLoop(done,3)){*error=[NSError errorWithDomain:@"ContinuousVisibleProbe" code:3 userInfo:@{NSLocalizedDescriptionKey:@"stream start timeout"}];return NO;}
    *error=failure;return failure==nil;
}
static NSError *StopStream(SCStream *stream) {
    dispatch_semaphore_t done=dispatch_semaphore_create(0);__block NSError *failure=nil;
    [stream stopCaptureWithCompletionHandler:^(NSError *e){failure=e;dispatch_semaphore_signal(done);}];
    if(!WaitPumpingRunLoop(done,3))return [NSError errorWithDomain:@"ContinuousVisibleProbe" code:4 userInfo:@{NSLocalizedDescriptionKey:@"stream stop timeout"}];
    return failure;
}
static BOOL SavePNG(CGImageRef image,NSString *path) {
    if(!image||!path)return NO;CGImageDestinationRef dest=CGImageDestinationCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:path],CFSTR("public.png"),1,NULL);
    if(!dest)return NO;CGImageDestinationAddImage(dest,image,NULL);BOOL ok=CGImageDestinationFinalize(dest);CFRelease(dest);return ok;
}

static CGImageRef SavedImage(ControlObserver *observer) {
    if(!observer.lastImageData)return NULL;
    CGDataProviderRef provider=CGDataProviderCreateWithCFData((__bridge CFDataRef)observer.lastImageData);
    CGColorSpaceRef color=CGColorSpaceCreateWithName(kCGColorSpaceSRGB);
    CGImageRef image=CGImageCreate(observer.width,observer.height,8,32,observer.lastRowBytes,color,
        kCGImageAlphaPremultipliedFirst|kCGBitmapByteOrder32Little,provider,NULL,false,kCGRenderingIntentDefault);
    CGColorSpaceRelease(color);CGDataProviderRelease(provider);return image;
}
static int ClassifySaved(const char *argument) {
    NSData *input=[NSData dataWithContentsOfFile:[NSString stringWithUTF8String:argument]];
    NSDictionary *d=input?[NSJSONSerialization JSONObjectWithData:input options:0 error:nil]:nil;
    NSString *path=d[@"image"]; NSArray *r=d[@"crop"],*origin=d[@"window_origin"],*point=d[@"point"],*profile=d[@"classifier"];
    if(![path isKindOfClass:NSString.class]||r.count!=4||origin.count!=2||point.count!=2||profile.count!=3||[d[@"scale"] doubleValue]!=2)return 2;
    CGRect crop=CGRectMake([r[0] doubleValue],[r[1] doubleValue],[r[2] doubleValue],[r[3] doubleValue]);
    CGPoint target=CGPointMake([point[0] doubleValue],[point[1] doubleValue]);
    BrightMinimum=[profile[0] unsignedIntegerValue];KnobMinimum=[profile[1] unsignedIntegerValue];KnobMaximum=[profile[2] unsignedIntegerValue];
    if(BrightMinimum<128||BrightMinimum>255||KnobMinimum<2||KnobMaximum<KnobMinimum||KnobMaximum>128||crop.size.width<=0||crop.size.height<=0||!CGRectContainsPoint(crop,target))return 2;
    CGImageSourceRef source=CGImageSourceCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:path],NULL);
    CGImageRef image=source?CGImageSourceCreateImageAtIndex(source,0,NULL):NULL;
    if(source)CFRelease(source);if(!image)return 2;
    CGRect pixels=CGRectMake((crop.origin.x-[origin[0] doubleValue])*2,(crop.origin.y-[origin[1] doubleValue])*2,crop.size.width*2,crop.size.height*2);
    if(!CGRectContainsRect(CGRectMake(0,0,CGImageGetWidth(image),CGImageGetHeight(image)),pixels)){CGImageRelease(image);return 2;}
    CGImageRef cut=CGImageCreateWithImageInRect(image,pixels);CGImageRelease(image);if(!cut)return 2;
    size_t w=CGImageGetWidth(cut),h=CGImageGetHeight(cut),stride=w*4;
    if(w>4096||h>4096){CGImageRelease(cut);return 2;}
    uint8_t *data=calloc(h,stride);CGColorSpaceRef color=CGColorSpaceCreateWithName(kCGColorSpaceSRGB);
    CGContextRef ctx=data?CGBitmapContextCreate(data,w,h,8,stride,color,kCGImageAlphaPremultipliedFirst|kCGBitmapByteOrder32Little):NULL;
    CGColorSpaceRelease(color);if(!ctx){free(data);CGImageRelease(cut);return 2;}
    CGContextDrawImage(ctx,CGRectMake(0,0,w,h),cut);
    NSDictionary *result=KnobPixels(data,h*stride,w,h,stride,crop,target);
    WriteJSON(stdout,@{@"kind":@"saved_image_classifier",@"image":path,@"knob":result,@"scope":@"Offline pixels only; no live capture/input/timing qualification"});
    CGContextRelease(ctx);CGImageRelease(cut);free(data);return 0;
}
static void Usage(void) {
    fprintf(stderr,"usage: master-control-response-probe --bundle-id ID --classifier bright,minWidth,maxWidth --pid PID --expected-executable /absolute/app/Contents/MacOS/VLC --rect x,y,w,h --point x,y --click|--move --count 1..600 --output work/...jsonl [--duration-ms 1..5000] [--save-last-image work/...png] [--ax-mode per-frame|phase]\n");
}
int main(int argc,const char **argv){@autoreleasepool{
    if(argc==2&&!strcmp(argv[1],"--pixel-self-test"))return PixelSelfTest();
    if(argc==3&&!strcmp(argv[1],"--classify-saved"))return ClassifySaved(argv[2]);
    int pid=0,duration=2000,count=0; CGRect rect=CGRectNull; CGPoint point=CGPointMake(NAN,NAN);
    int action=0; BOOL phaseAX=NO,modeSet=NO; const char *outputArg=NULL,*saveArg=NULL,*executableArg=NULL,*bundleArg=NULL; BOOL profileSet=NO;
    for(int i=1;i<argc;){
        if((!strcmp(argv[i],"--click")||!strcmp(argv[i],"--move"))&&!action){action=!strcmp(argv[i],"--click")?2:1;i++;}
        else if(!strcmp(argv[i],"--pid")&&i+1<argc&&!pid){char *end=NULL;long n=strtol(argv[i+1],&end,10);if(end==argv[i+1]||*end||n<=0||n>INT32_MAX){Usage();return 2;}pid=(int)n;i+=2;}
        else if(!strcmp(argv[i],"--bundle-id")&&i+1<argc&&!bundleArg){bundleArg=argv[i+1];i+=2;}
        else if(!strcmp(argv[i],"--classifier")&&i+1<argc&&!profileSet){unsigned bright,min,max;char tail;if(sscanf(argv[i+1],"%u,%u,%u%c",&bright,&min,&max,&tail)!=3||bright<128||bright>255||min<2||max<min||max>128){Usage();return 2;}BrightMinimum=bright;KnobMinimum=min;KnobMaximum=max;profileSet=YES;i+=2;}
        else if(!strcmp(argv[i],"--expected-executable")&&i+1<argc&&!executableArg){executableArg=argv[i+1];i+=2;}
        else if(!strcmp(argv[i],"--rect")&&i+1<argc&&CGRectIsNull(rect)){if(!ParseRect(argv[i+1],&rect)){Usage();return 2;}i+=2;}
        else if(!strcmp(argv[i],"--point")&&i+1<argc&&isnan(point.x)){if(!ParsePoint(argv[i+1],&point)){Usage();return 2;}i+=2;}
        else if((!strcmp(argv[i],"--count")||!strcmp(argv[i],"--duration-ms"))&&i+1<argc){char *end=NULL;long n=strtol(argv[i+1],&end,10);BOOL isCount=!strcmp(argv[i],"--count");if(end==argv[i+1]||*end||n<1||n>(isCount?600:5000)){Usage();return 2;}if(isCount)count=(int)n;else duration=(int)n;i+=2;}
        else if(!strcmp(argv[i],"--ax-mode")&&i+1<argc&&!modeSet){if(strcmp(argv[i+1],"phase")&&strcmp(argv[i+1],"per-frame")){Usage();return 2;}phaseAX=!strcmp(argv[i+1],"phase");modeSet=YES;i+=2;}
        else if(!strcmp(argv[i],"--output")&&i+1<argc&&!outputArg){outputArg=argv[i+1];i+=2;}
        else if(!strcmp(argv[i],"--save-last-image")&&i+1<argc&&!saveArg){saveArg=argv[i+1];i+=2;}
        else {Usage();return 2;}
    }
    if(!pid||!action||!count||CGRectIsNull(rect)||rect.size.width>400||rect.size.height>100||
       floor(rect.size.width*2)!=rect.size.width*2||floor(rect.size.height*2)!=rect.size.height*2||
       !isfinite(point.x)||!isfinite(point.y)||!CGRectContainsPoint(rect,point)||!outputArg||!executableArg||!bundleArg||!profileSet){Usage();return 2;}
    ExpectedBundleID=[NSString stringWithUTF8String:bundleArg];
    if(![ExpectedBundleID hasPrefix:@"org.videolan.vlc.story005."]){Usage();return 2;}
    NSString *expectedExecutable=[[NSString stringWithUTF8String:executableArg] stringByResolvingSymlinksInPath];
    if(!expectedExecutable.isAbsolutePath||access(expectedExecutable.fileSystemRepresentation,X_OK)!=0){Usage();return 2;}
    NSString *output=CanonicalFreshWorkFile([NSString stringWithUTF8String:outputArg]);
    NSString *save=saveArg?CanonicalFreshWorkFile([NSString stringWithUTF8String:saveArg]):nil;
    if(!output||(saveArg&&!save)||(save&&[save isEqual:output])){fprintf(stderr,"Outputs must be distinct fresh canonical absolute work paths\n");return 2;}
    FILE *file=fopen(output.fileSystemRepresentation,"wx");if(!file){perror("--output");return 2;}
    NSTimer *freshnessWake=[NSTimer timerWithTimeInterval:0.001 repeats:YES block:^(NSTimer *timer) {}];
    [[NSRunLoop mainRunLoop] addTimer:freshnessWake forMode:NSDefaultRunLoopMode];
    BOOL policy=[NSApplication.sharedApplication setActivationPolicy:NSApplicationActivationPolicyProhibited];
    CGRect parent;NSString *guardError=nil;
    double preFrontBegin=Now(); NSRunningApplication *preFront=NSWorkspace.sharedWorkspace.frontmostApplication;
    pid_t preFrontPID=preFront?preFront.processIdentifier:0; NSString *preFrontBundle=preFront.bundleIdentifier; double preFrontEnd=Now();
    NSRunningApplication *app=preFront; // Exact identity guards below validate readiness before retaining.
    WriteJSON(file,@{@"kind":@"foreground_pre",@"policy":@"workspace-frontmost-retained-instance-v4",@"query_begin_uptime_s":@(preFrontBegin),@"query_end_uptime_s":@(preFrontEnd),@"frontmost_pid":@(preFrontPID),@"frontmost_bundle":preFrontBundle?:NSNull.null,@"target_active_diagnostic":@(app.active),@"frontmost_equals_retained_target":@((BOOL)(preFront && [preFront isEqual:app])),@"retained_target_executable_path":ApplicationExecutablePath(app)?:NSNull.null,@"expected_executable_path":expectedExecutable,@"retained_target_terminated":@(app.terminated)});
    if(!RetainedTargetForeground(app,preFront,pid,expectedExecutable)||
       !FindMainWindow(pid,rect,point,&parent)||!OwnAXHit(pid,point,&guardError)){
        WriteJSON(file,@{@"kind":@"probe_error",@"error":guardError?:@"active owned main-window crop required"});fclose(file);return 1;}
    AXUIElementRef resolvedSlider=NULL;
    NSDictionary *preAX=AXPhase(pid,point,@"pre",NULL,&resolvedSlider);
    id heldSlider=CFBridgingRelease(resolvedSlider); // ARC releases on every early return.
    WriteJSON(file,preAX);
    if(![preAX[@"owned"] boolValue]||preAX[@"slider_value"]==NSNull.null){WriteJSON(file,@{@"kind":@"probe_error",@"error":@"pre AX slider ownership/value unavailable"});fclose(file);return 1;}
    SCDisplay *display=nil;NSError *error=nil;
    if(!FindDisplay(rect,&display,&error)){WriteJSON(file,@{@"kind":@"probe_error",@"error":error.localizedDescription?:@"display lookup failed"});fclose(file);return 1;}
    SCContentFilter *filter=[[SCContentFilter alloc]initWithDisplay:display excludingWindows:@[]];
    SCStreamConfiguration *config=[SCStreamConfiguration new];config.sourceRect=CGRectOffset(rect,-display.frame.origin.x,-display.frame.origin.y);
    config.width=(size_t)(rect.size.width*2);config.height=(size_t)(rect.size.height*2);config.pixelFormat=kCVPixelFormatType_32BGRA;config.colorSpaceName=kCGColorSpaceSRGB;
    config.minimumFrameInterval=CMTimeMake(1,60);config.queueDepth=3;config.showsCursor=NO;config.showMouseClicks=NO;config.capturesAudio=NO;config.captureMicrophone=NO;
    ControlObserver *observer=[ControlObserver new];observer.pid=pid;observer.targetApplication=app;observer.expectedExecutablePath=expectedExecutable;observer.expectedParent=parent;observer.crop=rect;observer.point=point;observer.output=file;
    observer.phaseAX=phaseAX;observer.width=config.width;observer.height=config.height;observer.limit=count;observer.saveLastImage=save!=nil;
    dispatch_queue_t frames=dispatch_queue_create("story002.control-response.frames",DISPATCH_QUEUE_SERIAL);
    SCStream *stream=[[SCStream alloc]initWithFilter:filter configuration:config delegate:observer];
    NSError *addError=nil;
    if(![stream addStreamOutput:observer type:SCStreamOutputTypeScreen sampleHandlerQueue:frames error:&addError]){WriteJSON(file,@{@"kind":@"probe_error",@"error":addError.localizedDescription?:@"stream output failed"});fclose(file);return 1;}
    WriteJSON(file,@{@"kind":@"session",@"readiness_acquisition":@"validated-frontmost-instance",@"observer_version":@5,@"ax_check_scope":phaseAX?@"phase-only-unqualified":@"complete-presentations-only",@"foreground_policy":@"workspace-frontmost-retained-instance-v4",@"expected_executable_path":expectedExecutable,@"retained_target_executable_path":ApplicationExecutablePath(app),@"expected_bundle_id":ExpectedBundleID,@"target_identity_policy":@"readiness-retained-no-replacement",@"pid":@(pid),@"rect_screen_points":@[@(rect.origin.x),@(rect.origin.y),@(rect.size.width),@(rect.size.height)],
        @"point":@[@(point.x),@(point.y)],@"scale":@2,@"stream_width":@(config.width),@"stream_height":@(config.height),
        @"ax_mode":phaseAX?@"phase":@"per-frame",@"phase_guard_equivalence_proven":@NO,@"routing_observer":@"exact_pid_passive_nonce_filtered",@"fps_cap":@60,@"queue_depth":@3,@"cursor":@NO,@"audio":@NO,@"microphone":@NO,@"observer_windows_created":@0,
        @"prohibited_policy_accepted":@(policy),@"input":action==2?@"move-down-up":@"move",@"frame_limit":@(count),@"duration_ms":@(duration)});
    if(!WaitForStart(stream,&error)){WriteJSON(file,@{@"kind":@"probe_error",@"error":error.localizedDescription?:@"stream start failed"});StopStream(stream);dispatch_sync(frames,^{});fclose(file);return 1;}
    double warmDeadline=Now()+3;
    while(observer.warmFrames<1&&Now()<warmDeadline&&!observer.fatalError)PumpMainRunLoop();
    if(!observer.warmFrames){WriteJSON(file,@{@"kind":@"probe_error",@"error":observer.fatalError?:@"no complete owned readiness frame"});StopStream(stream);dispatch_sync(frames,^{});fclose(file);return 1;}
    RoutingTap tap={0};tap.pid=pid;tap.tag=(int64_t)(mach_absolute_time()^((uint64_t)getpid()<<32));if(!tap.tag)tap.tag=1;
    atomic_init(&tap.ready,false);atomic_init(&tap.stop,false);atomic_init(&tap.failed,false);pthread_t tapThread;
    int threadError=pthread_create(&tapThread,NULL,RouteThread,&tap);
    if(!threadError){while(!atomic_load(&tap.ready))PumpMainRunLoop();}
    if(threadError||atomic_load(&tap.failed)){if(!threadError)pthread_join(tapThread,NULL);WriteJSON(file,@{@"kind":@"probe_error",@"error":@"exact PID passive event tap unavailable or disabled; no fallback"});StopStream(stream);dispatch_sync(frames,^{});fclose(file);return 1;}
    CGEventRef move=CGEventCreateMouseEvent(NULL,kCGEventMouseMoved,point,kCGMouseButtonLeft);
    CGEventRef down=action==2?CGEventCreateMouseEvent(NULL,kCGEventLeftMouseDown,point,kCGMouseButtonLeft):NULL;
    CGEventRef up=action==2?CGEventCreateMouseEvent(NULL,kCGEventLeftMouseUp,point,kCGMouseButtonLeft):NULL;
    if(!move||(action==2&&(!down||!up))){atomic_store(&tap.stop,true);pthread_join(tapThread,NULL);if(move)CFRelease(move);if(down)CFRelease(down);if(up)CFRelease(up);StopStream(stream);dispatch_sync(frames,^{});fclose(file);return 1;}
    if(down)CGEventSetIntegerValueField(down,kCGMouseEventClickState,1);if(up)CGEventSetIntegerValueField(up,kCGMouseEventClickState,1);
    CGEventSetIntegerValueField(move,kCGEventSourceUserData,tap.tag);if(down)CGEventSetIntegerValueField(down,kCGEventSourceUserData,tap.tag);if(up)CGEventSetIntegerValueField(up,kCGEventSourceUserData,tap.tag);
    dispatch_sync(frames,^{observer.postInput=YES;observer.inputT0=Now();observer.deadline=observer.inputT0+(double)duration/1000.;});
    CGError warp=CGWarpMouseCursorPosition(point);
    if(warp==kCGErrorSuccess){CGEventPost(kCGHIDEventTap,move);if(down)CGEventPost(kCGHIDEventTap,down);if(up)CGEventPost(kCGHIDEventTap,up);}
    CFRelease(move);if(down)CFRelease(down);if(up)CFRelease(up);
    [observer write:@{@"kind":@"input_posted",@"input_t0_uptime_s":@(observer.inputT0),@"post_complete_uptime_s":@(Now()),@"warp_success":@(warp==kCGErrorSuccess),@"event_tag":@(tap.tag)}];
    while(warp==kCGErrorSuccess&&!observer.finished&&Now()<observer.deadline)PumpMainRunLoop();
    double observationEnd=Now();
    NSError *stopError=StopStream(stream);dispatch_sync(frames,^{});
    atomic_store(&tap.stop,true);pthread_join(tapThread,NULL);
    BOOL routed=!atomic_load(&tap.failed)&&tap.count==(action==2?3:1);
    CGEventType expected[3]={kCGEventMouseMoved,kCGEventLeftMouseDown,kCGEventLeftMouseUp};
    for(size_t i=0;i<tap.count;i++){RoutedEvent e=tap.events[i];if(i>=3||e.type!=expected[i]||fabs(e.point.x-point.x)>.5||fabs(e.point.y-point.y)>.5||e.received<observer.inputT0)routed=NO;
        WriteJSON(file,@{@"kind":@"input_routed",@"pid":@(pid),@"event_tag":@(tap.tag),@"type":@(e.type),@"location":@[@(e.point.x),@(e.point.y)],@"received_uptime_s":@(e.received),@"event_timestamp_ns":@(e.timestamp),@"sequence_index":@(i)});}
    NSDictionary *postAX=AXPhase(pid,point,@"post",(__bridge AXUIElementRef)heldSlider,NULL);WriteJSON(file,postAX);
    if(!routed)WriteJSON(file,@{@"kind":@"probe_error",@"error":@"tagged input routing sequence missing, invalid or tap disabled; no fallback"});
    NSRunningApplication *after=[NSRunningApplication runningApplicationWithProcessIdentifier:pid];NSString *afterError=nil;CGRect afterParent;
    double postFrontBegin=Now(); NSRunningApplication *postFront=NSWorkspace.sharedWorkspace.frontmostApplication;
    pid_t postFrontPID=postFront?postFront.processIdentifier:0; NSString *postFrontBundle=postFront.bundleIdentifier; double postFrontEnd=Now();
    WriteJSON(file,@{@"kind":@"foreground_post",@"policy":@"workspace-frontmost-retained-instance-v4",@"query_begin_uptime_s":@(postFrontBegin),@"query_end_uptime_s":@(postFrontEnd),@"frontmost_pid":@(postFrontPID),@"frontmost_bundle":postFrontBundle?:NSNull.null,@"target_active_diagnostic":@(after.active),@"frontmost_equals_retained_target":@((BOOL)(postFront && [postFront isEqual:observer.targetApplication])),@"retained_target_executable_path":ApplicationExecutablePath(observer.targetApplication)?:NSNull.null,@"expected_executable_path":expectedExecutable,@"retained_target_terminated":@(observer.targetApplication.terminated)});
    BOOL afterOwned=RetainedTargetForeground(observer.targetApplication,postFront,pid,expectedExecutable)&&FindMainWindow(pid,rect,point,&afterParent)&&CGRectEqualToRect(afterParent,parent)&&OwnAXHit(pid,point,&afterError);
    CGImageRef image=save?SavedImage(observer):NULL;BOOL saveOK=!save||(image&&SavePNG(image,save));if(image)CGImageRelease(image);
    WriteJSON(file,@{@"kind":@"completion",@"post_input_frames":@(observer.frames),@"observation_end_uptime_s":@(observationEnd),@"observation_bound_reached":@(observationEnd>=observer.deadline),@"after_owned":@(afterOwned),@"input_routed_sequence":@(routed),@"tap_disabled_or_failed":@(atomic_load(&tap.failed)),
        @"input_t0_uptime_s":@(observer.inputT0),@"save_success":@(saveOK),@"error":observer.fatalError?:stopError.localizedDescription?:afterError?:(id)NSNull.null});
    fclose(file);return routed&&[postAX[@"owned"] boolValue]&&postAX[@"slider_value"]!=NSNull.null&&warp==kCGErrorSuccess&&observer.frames>0&&!observer.fatalError&&!stopError&&afterOwned&&saveOK?0:1;
}}
