// SPDX-License-Identifier: GPL-2.0-or-later
// Diagnostic only: same capture/pixel conventions; ownership checked pre/post,
// not per frame. Never substitute this observer for qualification without review.
// Reuse parsing, sRGB/ROI analysis, capture and path guards unchanged.
#define main ContinuousProbeUnusedMain
#include "continuous_visible_probe.m"
#undef main

#define BUFFERED_FRAME_CAP 32
#define BUFFERED_ROW_CAP 4096
#define BUFFERED_HEIGHT 448
#define BUFFERED_WINDOW_S .500

typedef struct {
    double receipt, callbackDuration, pts;
    int64_t ptsValue;
    int32_t ptsScale;
    uint64_t displayTicks;
    NSInteger status;
    size_t rowBytes;
    BOOL copied, invalidPixel;
} BufferedFrame;

@interface BufferedObserver : NSObject <SCStreamOutput, SCStreamDelegate>
@property(atomic) int warmFrames;
@property(atomic) BOOL armed;
@property(atomic) BOOL finished;
@property(atomic) double t0;
@property(atomic) double deadline;
@property(atomic) NSUInteger count;
@property(atomic,strong) NSString *failure;
@property(nonatomic) BufferedFrame *frames;
@property(nonatomic) uint8_t *pixels;
@end
@implementation BufferedObserver
- (instancetype)init {
    if((self=[super init])) {
        _frames=calloc(BUFFERED_FRAME_CAP,sizeof(BufferedFrame));
        _pixels=malloc((size_t)BUFFERED_FRAME_CAP*BUFFERED_ROW_CAP*BUFFERED_HEIGHT);
        if(!_frames||!_pixels) _failure=@"fixed pixel allocation failed";
        else memset(_pixels,0,(size_t)BUFFERED_FRAME_CAP*BUFFERED_ROW_CAP*BUFFERED_HEIGHT); // fault pages before capture/input
    }return self;
}
- (void)dealloc { free(_frames); free(_pixels); }
- (void)stream:(SCStream *)stream didStopWithError:(NSError *)error {
    if(error){self.failure=error.localizedDescription;self.finished=YES;}
}
- (void)stream:(SCStream *)stream didOutputSampleBuffer:(CMSampleBufferRef)buffer ofType:(SCStreamOutputType)type {
    @autoreleasepool {
        double receipt=Now(); if(type!=SCStreamOutputTypeScreen)return;
        CFArrayRef raw=CMSampleBufferGetSampleAttachmentsArray(buffer,false);
        NSDictionary *a=raw&&CFArrayGetCount(raw)?(__bridge NSDictionary *)CFArrayGetValueAtIndex(raw,0):nil;
        NSInteger status=[a[SCStreamFrameInfoStatus] respondsToSelector:@selector(integerValue)]?[a[SCStreamFrameInfoStatus] integerValue]:-1;
        CVPixelBufferRef pixel=CMSampleBufferGetImageBuffer(buffer);
        if(!self.armed){
            if(status==SCFrameStatusComplete&&pixel&&CVPixelBufferGetWidth(pixel)==672&&CVPixelBufferGetHeight(pixel)==448)self.warmFrames++;
            return;
        }
        // A fixed half-second input-relative interval. Extra stop callbacks are
        // ignored; no scene queries, allocation, JSON, masks or hashes here.
        if(receipt>self.deadline||self.finished)return;
        NSUInteger n=self.count;
        if(n>=BUFFERED_FRAME_CAP){self.failure=@"fixed 32-frame capacity exhausted";self.finished=YES;return;}
        BufferedFrame *f=&_frames[n];f->receipt=receipt;f->status=status;
        CMTime pts=CMSampleBufferGetPresentationTimeStamp(buffer);
        f->pts=CMTimeGetSeconds(pts);if(!isfinite(f->pts))f->pts=-1;
        f->ptsValue=pts.value;f->ptsScale=pts.timescale;f->displayTicks=DisplayTicks(a);
        if(status==SCFrameStatusComplete){
            if(!pixel||CVPixelBufferGetPixelFormatType(pixel)!=kCVPixelFormatType_32BGRA||
               CVPixelBufferGetWidth(pixel)!=672||CVPixelBufferGetHeight(pixel)!=448||CVPixelBufferIsPlanar(pixel))f->invalidPixel=YES;
            else {
                CVReturn locked=CVPixelBufferLockBaseAddress(pixel,kCVPixelBufferLock_ReadOnly);
                if(locked==kCVReturnSuccess){
                    void *base=CVPixelBufferGetBaseAddress(pixel);size_t row=CVPixelBufferGetBytesPerRow(pixel);
                    if(base&&row>=672*4&&row<=BUFFERED_ROW_CAP){
                        memcpy(_pixels+n*BUFFERED_ROW_CAP*BUFFERED_HEIGHT,base,row*BUFFERED_HEIGHT);
                        f->copied=YES;f->rowBytes=row;
                    }else f->invalidPixel=YES;
                    CVPixelBufferUnlockBaseAddress(pixel,kCVPixelBufferLock_ReadOnly);
                }else f->invalidPixel=YES;
            }
        }
        f->callbackDuration=Now()-receipt;self.count=n+1;
        // Captured buffers are never retained and are returned at callback exit.
    }
}
@end

static NSDictionary *SceneGuard(pid_t pid,CGRect crop,CGPoint point) {
    NSRunningApplication *app=[NSRunningApplication runningApplicationWithProcessIdentifier:pid];
    CGRect parent=CGRectNull,panel=CGRectNull;NSDictionary *meta=nil;NSString *hitError=nil;
    BOOL active=app&&app.active&&[app.bundleIdentifier isEqualToString:@"org.videolan.vlc-thumbs.development"];
    BOOL parentOK=FindMainWindow(pid,crop,point,&parent),found=FindOwnedPreview(pid,&panel,&meta),hit=OwnAXHit(pid,point,&hitError);
    return @{@"app_active":@(active),@"parent_window_contains_crop":@(parentOK),@"ax_point_owned":@(hit),
        @"panel_found":@(found),@"panel_rect_matches_crop":@(found&&CGRectEqualToRect(crop,panel)),
        @"actual_panel_rect":found?@[@(panel.origin.x),@(panel.origin.y),@(panel.size.width),@(panel.size.height)]:(id)NSNull.null,
        @"actual_panel_window_id":meta[(id)kCGWindowNumber]?:@0,@"ax_error":hitError?:@""};
}

int main(int argc,const char **argv){@autoreleasepool{
    int pid=0;CGRect crop=CGRectNull;CGPoint point=CGPointMake(NAN,NAN);const char *hash=NULL,*tm=NULL,*pm=NULL,*out=NULL,*saveArg=NULL;
    for(int i=1;i<argc;i+=2){
        if(i+1>=argc){Usage();return 2;}
        if(!strcmp(argv[i],"--pid")&&!pid){char *end=NULL;long v=strtol(argv[i+1],&end,10);if(end==argv[i+1]||*end||v<=0||v>INT32_MAX)return 2;pid=(int)v;}
        else if(!strcmp(argv[i],"--rect")&&CGRectIsNull(crop)){if(!ParseRect(argv[i+1],&crop))return 2;}
        else if(!strcmp(argv[i],"--point")&&isnan(point.x)){if(!ParsePoint(argv[i+1],&point))return 2;}
        else if(!strcmp(argv[i],"--expected-hash")&&!hash){hash=argv[i+1];if(!HashArgument(hash))return 2;}
        else if(!strcmp(argv[i],"--expected-time-mask")&&!tm){tm=argv[i+1];if(!TimeMaskArgument(tm))return 2;}
        else if(!strcmp(argv[i],"--previous-time-mask")&&!pm){pm=argv[i+1];if(!TimeMaskArgument(pm))return 2;}
        else if(!strcmp(argv[i],"--output")&&!out)out=argv[i+1];
        else if(!strcmp(argv[i],"--save-last-image")&&!saveArg)saveArg=argv[i+1];
        else {Usage();return 2;}
    }
    if(!pid||CGRectIsNull(crop)||crop.size.width!=336||crop.size.height!=224||!isfinite(point.x)||!isfinite(point.y)||!hash||!tm||!out)return 2;
    NSString *output=CanonicalFreshWorkFile([NSString stringWithUTF8String:out]);
    NSString *save=saveArg?CanonicalFreshWorkFile([NSString stringWithUTF8String:saveArg]):nil;
    if(!output||(saveArg&&!save))return 2;
    FILE *file=fopen(output.fileSystemRepresentation,"wx");if(!file)return 2;
    [NSApplication.sharedApplication setActivationPolicy:NSApplicationActivationPolicyProhibited];
    NSDictionary *pre=SceneGuard(pid,crop,point);
    WriteJSON(file,@{@"kind":@"session",@"diagnostic_only":@YES,@"guard_equivalence_proven":@NO,
        @"ownership_guard_scope":@"pre/post only; transient occlusion/inactivity unobserved",@"window_ms":@500,@"frame_capacity":@32,@"PNG_selection":@"first exact image/new-time match; subsequent state correctness checked by runner",
        @"stream_width":@672,@"stream_height":@448,@"fps_cap":@60,@"queue_depth":@3,@"cursor":@NO,@"audio":@NO,@"microphone":@NO,@"pre_guard":pre});
    if(![pre[@"app_active"] boolValue]||![pre[@"parent_window_contains_crop"] boolValue]||![pre[@"ax_point_owned"] boolValue]||![pre[@"panel_found"] boolValue]){WriteJSON(file,@{@"kind":@"probe_error",@"error":@"pre-input ownership guard failed"});fclose(file);return 1;}
    SCDisplay *display=nil;NSError *error=nil;
    if(!FindDisplay(crop,&display,&error)){WriteJSON(file,@{@"kind":@"probe_error",@"error":error.localizedDescription?:@"display lookup failed"});fclose(file);return 1;}
    SCContentFilter *filter=[[SCContentFilter alloc]initWithDisplay:display excludingWindows:@[]];
    SCStreamConfiguration *config=[SCStreamConfiguration new];config.sourceRect=CGRectOffset(crop,-display.frame.origin.x,-display.frame.origin.y);
    config.width=672;config.height=448;config.pixelFormat=kCVPixelFormatType_32BGRA;config.colorSpaceName=kCGColorSpaceSRGB;
    config.minimumFrameInterval=CMTimeMake(1,60);config.queueDepth=3;config.showsCursor=NO;config.showMouseClicks=NO;config.capturesAudio=NO;config.captureMicrophone=NO;
    BufferedObserver *observer=[BufferedObserver new];dispatch_queue_t queue=dispatch_queue_create("story002.buffered-visible.frames",DISPATCH_QUEUE_SERIAL);
    SCStream *stream=[[SCStream alloc]initWithFilter:filter configuration:config delegate:observer];
    if(observer.failure||![stream addStreamOutput:observer type:SCStreamOutputTypeScreen sampleHandlerQueue:queue error:&error]||!WaitForStart(stream,&error)){
        WriteJSON(file,@{@"kind":@"probe_error",@"error":observer.failure?:error.localizedDescription?:@"capture start failed"});StopStream(stream);dispatch_sync(queue,^{});fclose(file);return 1;
    }
    double warmEnd=Now()+3;while(observer.warmFrames<1&&Now()<warmEnd&&!observer.failure)usleep(1000);
    if(observer.warmFrames<1){WriteJSON(file,@{@"kind":@"probe_error",@"error":observer.failure?:@"no complete readiness frame within 3s"});StopStream(stream);dispatch_sync(queue,^{});fclose(file);return 1;}
    dispatch_sync(queue,^{observer.t0=Now();observer.deadline=observer.t0+BUFFERED_WINDOW_S;observer.armed=YES;});
    CGError warp=CGWarpMouseCursorPosition(point);CGEventRef event=CGEventCreateMouseEvent(NULL,kCGEventMouseMoved,point,kCGMouseButtonLeft);
    if(warp!=kCGErrorSuccess||!event){observer.failure=@"pointer placement failed";}else CGEventPost(kCGHIDEventTap,event);if(event)CFRelease(event);
    while(Now()<observer.deadline&&!observer.failure)usleep(1000);
    NSError *stopError=StopStream(stream);dispatch_sync(queue,^{});
    NSDictionary *post=SceneGuard(pid,crop,point);
    BOOL guards=[post[@"app_active"] boolValue]&&[post[@"parent_window_contains_crop"] boolValue]&&[post[@"ax_point_owned"] boolValue]&&[post[@"panel_rect_matches_crop"] boolValue]&&
        [post[@"actual_panel_window_id"] isEqual:pre[@"actual_panel_window_id"]];
    WriteJSON(file,@{@"kind":@"post_capture_guard",@"guard":post,@"same_panel_window_id":@([post[@"actual_panel_window_id"] isEqual:pre[@"actual_panel_window_id"]])});
    NSString *expected=[NSString stringWithUTF8String:hash],*timeMask=[NSString stringWithUTF8String:tm],*previous=pm?[NSString stringWithUTF8String:pm]:nil;
    BOOL matched=NO,frameError=NO;CGImageRef matchedImage=NULL;
    for(NSUInteger n=0;n<observer.count;n++){
        BufferedFrame f=observer.frames[n];double shown=MachSeconds(f.displayTicks);
        NSMutableDictionary *row=[@{@"kind":@"display_frame",@"index":@(n),@"frame_status":@(f.status),
            @"presentation_pts_seconds":@(f.pts),@"presentation_pts_value":@(f.ptsValue),@"presentation_pts_timescale":@(f.ptsScale),
            @"display_time_mach_ticks":@(f.displayTicks),@"display_time_present":@(f.displayTicks>0),@"display_time_uptime_seconds":@(shown),
            @"callback_received_uptime_s":@(f.receipt),@"callback_work_ms":@(f.callbackDuration*1000),@"input_t0_uptime_s":@(observer.t0),
            @"input_to_callback_ms":@((f.receipt-observer.t0)*1000),@"app_active":post[@"app_active"],@"parent_window_contains_crop":post[@"parent_window_contains_crop"],
            @"panel_rect_matches_crop":@(guards),@"actual_panel_rect":post[@"actual_panel_rect"],@"actual_panel_window_id":post[@"actual_panel_window_id"],
            @"ownership_guard_scope":@"pre/post only; frame-level ownership not observed",@"diagnostic_only":@YES} mutableCopy];
        if(f.invalidPixel){row[@"error"]=@"unexpected complete pixel frame or copy/lock failure";frameError=YES;}
        if(f.copied){
            NSData *data=[NSData dataWithBytesNoCopy:observer.pixels+n*BUFFERED_ROW_CAP*BUFFERED_HEIGHT length:f.rowBytes*BUFFERED_HEIGHT freeWhenDone:NO];
            CGImageRef image=ImageFromOwnedData(data,f.rowBytes);
            if(image){NSDictionary *stats=PointImageStats(image);row[@"result"]=stats;
                NSUInteger distance=MaskDistance(stats[@"time_mask_hex"],timeMask),prior=previous?MaskDistance(stats[@"time_mask_hex"],previous):NSUIntegerMax;
                BOOL eligible=f.status==SCFrameStatusComplete&&f.displayTicks>0&&shown>=observer.t0&&f.pts>=observer.t0;
                BOOL exact=[stats[@"image_sample_hash_fnv1a64"] caseInsensitiveCompare:expected]==NSOrderedSame;
                BOOL match=eligible&&guards&&exact&&distance<=22&&(!previous||distance<prior);
                row[@"expected_visible_match"]=@(match);row[@"post_input_complete_presentation"]=@(eligible);
                row[@"expected_time_mask_hamming"]=@(distance);row[@"previous_time_mask_hamming"]=previous?@(prior):(id)NSNull.null;
                if(match&&!matchedImage)matchedImage=CGImageRetain(image);matched=matched||match;CGImageRelease(image);
            }else {row[@"error"]=@"owned pixel wrapping failed";frameError=YES;}
        }
        WriteJSON(file,row);
    }
    BOOL saveOK=!save||(matchedImage&&SavePNG(matchedImage,save));if(matchedImage)CGImageRelease(matchedImage);
    if(observer.failure||stopError||!guards||frameError||!matched||!saveOK){
        NSString *why=observer.failure?:stopError.localizedDescription;
        if(!why)why=!guards?@"post guard failed":frameError?@"pixel analysis failure":!matched?@"expected image/time not seen in fixed 500ms":@"PNG save failed";
        WriteJSON(file,@{@"kind":@"probe_error",@"error":why});
    }
    fclose(file);return !observer.failure&&!stopError&&guards&&!frameError&&matched&&saveOK?0:1;
}}
