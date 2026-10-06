// SPDX-License-Identifier: GPL-2.0-or-later
// Development-only actual-display crop observer for visible VLC preview work.
// It creates no windows and captures no audio, microphone, or cursor.
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
static BOOL HashArgument(const char *value) {
    if(!value||strlen(value)!=16)return NO;for(const char *p=value;*p;p++)if(!((*p>='0'&&*p<='9')||(*p>='a'&&*p<='f')||(*p>='A'&&*p<='F')))return NO;return YES;
}
static BOOL TimeMaskArgument(const char *value) {
    if(!value||strlen(value)!=540)return NO;for(const char *p=value;*p;p++)if(!((*p>='0'&&*p<='9')||(*p>='a'&&*p<='f')||(*p>='A'&&*p<='F')))return NO;return YES;
}
static NSUInteger MaskDistance(NSString *left,NSString *right) {
    if(left.length!=right.length)return NSUIntegerMax;NSUInteger distance=0;
    for(NSUInteger i=0;i<left.length;i++){unsigned a=0,b=0;[[NSScanner scannerWithString:[left substringWithRange:NSMakeRange(i,1)]] scanHexInt:&a];[[NSScanner scannerWithString:[right substringWithRange:NSMakeRange(i,1)]] scanHexInt:&b];unsigned x=a^b;while(x){distance+=x&1;x>>=1;}}
    return distance;
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
static BOOL FindOwnedPreview(pid_t pid,CGRect *actual,NSDictionary **metadata) {
    NSArray *list=CFBridgingRelease(CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly,kCGNullWindowID));
    for(NSDictionary *entry in list){if([entry[(id)kCGWindowOwnerPID] intValue]!=pid)continue;int level=[entry[(id)kCGWindowLayer] intValue];if(level!=3&&level!=9)continue;CGRect b;
        if(ParseWindowBounds(entry,&b)&&fabs(b.size.width-336)<0.01&&fabs(b.size.height-224)<0.01){*actual=b;*metadata=entry;return YES;}}
    return NO;
}
static BOOL OwnAXHit(pid_t pid,CGPoint point,NSString **error) {
    AXUIElementRef system=AXUIElementCreateSystemWide(),hit=NULL;pid_t hitPID=0;
    AXError result=AXUIElementCopyElementAtPosition(system,(float)point.x,(float)point.y,&hit);if(result==kAXErrorSuccess&&hit)AXUIElementGetPid(hit,&hitPID);
    if(hit)CFRelease(hit);CFRelease(system);if(result!=kAXErrorSuccess||hitPID!=pid){*error=[NSString stringWithFormat:@"AX point ownership failed (error=%d pid=%d expected=%d)",result,hitPID,pid];return NO;}return YES;
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
static NSDictionary *ImageROIStats(CGImageRef image,CGRect pointRect) {
    double scale=(double)CGImageGetWidth(image)/336.0;CGRect pixels=CGRectMake(round(pointRect.origin.x*scale),round(pointRect.origin.y*scale),round(pointRect.size.width*scale),round(pointRect.size.height*scale));
    CGImageRef crop=CGImageCreateWithImageInRect(image,pixels);if(!crop)return @{@"roi_error":@"crop_failed"};NSDictionary *result=GenericImageStats(crop);CGImageRelease(crop);return result;
}
static NSString *MaskForRect(const uint8_t *p,size_t len,size_t width,size_t height,size_t bpp,size_t row,CGRect roi,double scale,NSUInteger *glyphs) {
    NSUInteger cols=(NSUInteger)llround(roi.size.width),rows=(NSUInteger)llround(roi.size.height);NSMutableString *hex=[NSMutableString string];unsigned nibble=0,bits=0;*glyphs=0;
    for(NSUInteger y=0;y<rows;y++)for(NSUInteger x=0;x<cols;x++){size_t px=(size_t)floor((roi.origin.x+x+0.5)*scale),py=(size_t)floor((roi.origin.y+y+0.5)*scale),at=py*row+px*bpp;BOOL white=NO;
        if(p&&bpp>=3&&px<width&&py<height&&at+bpp<=len){unsigned intensity=((unsigned)p[at]+p[at+1]+p[at+2])/3;white=intensity>180;}
        if(white)*glyphs+=1;nibble=(nibble<<1)|(white?1:0);bits++;if(bits==4){[hex appendFormat:@"%x",nibble];nibble=0;bits=0;}}
    if(bits)[hex appendFormat:@"%x",nibble<<(4-bits)];return hex;
}
static NSDictionary *PointImageStats(CGImageRef image) {
    size_t w=CGImageGetWidth(image),h=CGImageGetHeight(image),bpp=CGImageGetBitsPerPixel(image)/8,row=CGImageGetBytesPerRow(image);
    CFDataRef data=CGDataProviderCopyData(CGImageGetDataProvider(image));if(!data)return @{@"stats_error":@"no_provider_data",@"pixel_width":@(w),@"pixel_height":@(h)};
    const uint8_t *p=CFDataGetBytePtr(data);size_t len=CFDataGetLength(data);double scale=(double)w/336.0;NSUInteger tg=0,sg=0;
    NSString *timeMask=MaskForRect(p,len,w,h,bpp,row,CGRectMake(8,196,108,20),scale,&tg);
    NSString *stateMask=MaskForRect(p,len,w,h,bpp,row,CGRectMake(117,196,211,20),scale,&sg);
    NSDictionary *imageROI=ImageROIStats(image,CGRectMake(8,9,320,180));
    NSDictionary *timeROI=ImageROIStats(image,CGRectMake(8,196,108,20));
    NSDictionary *stateROI=ImageROIStats(image,CGRectMake(117,196,211,20));
    NSDictionary *result=@{@"pixel_width":@(w),@"pixel_height":@(h),@"scale_from_336_points":@(scale),
        @"panel_sample_hash_fnv1a64":HashPixels(p,len,w,h,bpp,row,NULL,NULL),@"image_roi_points":@[@8,@9,@320,@180],
        @"image_sample_hash_fnv1a64":imageROI[@"sample_hash_fnv1a64"]?:@"",@"image_sample_mean":imageROI[@"sample_mean"]?:@0,
        @"time_roi_points":@[@8,@196,@108,@20],@"time_mask_hex":timeMask,@"time_glyph_count":@(tg),
        @"time_sample_hash_fnv1a64":timeROI[@"sample_hash_fnv1a64"]?:@"",@"time_sample_mean":timeROI[@"sample_mean"]?:@0,
        @"state_roi_points":@[@117,@196,@211,@20],@"state_mask_hex":stateMask,@"state_glyph_count":@(sg),
        @"state_sample_hash_fnv1a64":stateROI[@"sample_hash_fnv1a64"]?:@"",@"state_sample_mean":stateROI[@"sample_mean"]?:@0};
    CFRelease(data);return result;
}
static uint64_t DisplayTicks(NSDictionary *attachments) {
    id value=attachments[SCStreamFrameInfoDisplayTime];return [value respondsToSelector:@selector(unsignedLongLongValue)]?[value unsignedLongLongValue]:0;
}
static double MachSeconds(uint64_t ticks) { mach_timebase_info_data_t info;mach_timebase_info(&info);return (double)ticks*(double)info.numer/(double)info.denom/1e9; }

@interface FrameObserver : NSObject <SCStreamOutput,SCStreamDelegate>
@property(atomic) pid_t pid;
@property(atomic) CGRect crop;
@property(atomic) CGPoint point;
@property(atomic) FILE *output;
@property(atomic,strong) NSString *expectedHash;
@property(atomic,strong) NSString *expectedTimeMask;
@property(atomic,strong) NSString *previousTimeMask;
@property(atomic) double inputT0;
@property(atomic) double deadline;
@property(atomic) BOOL postInput;
@property(atomic) BOOL finished;
@property(atomic) BOOL matched;
@property(atomic) int warmFrames;
@property(atomic) NSUInteger frames;
@property(atomic,strong) NSString *fatalError;
@property(atomic,strong) NSData *lastImageData;
@property(atomic) size_t lastRowBytes;
@property(atomic) BOOL saveLastImage;
@property(atomic,strong) NSLock *lock;
- (void)write:(NSDictionary *)row;
@end
@implementation FrameObserver
- (instancetype)init {if((self=[super init]))_lock=[NSLock new];return self;}
- (void)dealloc {}
- (void)write:(NSDictionary *)row {[_lock lock];WriteJSON(_output,row);[_lock unlock];}
- (void)stream:(SCStream *)stream didStopWithError:(NSError *)error {
    if(error){self.fatalError=error.localizedDescription;[self write:@{@"kind":@"stream_error",@"callback_received_uptime_s":@(Now()),@"error":self.fatalError}];self.finished=YES;}
}
- (void)stream:(SCStream *)stream didOutputSampleBuffer:(CMSampleBufferRef)sampleBuffer ofType:(SCStreamOutputType)type {
    @autoreleasepool {
    double receipt=Now();if(type!=SCStreamOutputTypeScreen)return;
    CFArrayRef raw=CMSampleBufferGetSampleAttachmentsArray(sampleBuffer,false);
    NSDictionary *attachments=raw&&CFArrayGetCount(raw)?CFBridgingRelease(CFRetain(CFArrayGetValueAtIndex(raw,0))):@{};
    NSInteger status=[attachments[SCStreamFrameInfoStatus] respondsToSelector:@selector(integerValue)]?[attachments[SCStreamFrameInfoStatus] integerValue]:-1;
    if(!self.postInput){
        CVPixelBufferRef warm=CMSampleBufferGetImageBuffer(sampleBuffer);
        [self write:@{@"kind":@"readiness_frame",@"frame_status":@(status),@"width":@(warm?CVPixelBufferGetWidth(warm):0),@"height":@(warm?CVPixelBufferGetHeight(warm):0),@"callback_uptime_s":@(receipt)}];
        if(status==SCFrameStatusComplete&&warm&&CVPixelBufferGetWidth(warm)==672&&CVPixelBufferGetHeight(warm)==448){self.warmFrames++;}
        return;
    }
    double pts=CMTimeGetSeconds(CMSampleBufferGetPresentationTimeStamp(sampleBuffer));if(!isfinite(pts))pts=-1;
    uint64_t displayTicks=DisplayTicks(attachments);CGRect actual=CGRectNull;NSDictionary *panel=nil;BOOL panelFound=FindOwnedPreview(self.pid,&actual,&panel);BOOL panelMatches=panelFound&&CGRectEqualToRect(actual,self.crop);
    NSRunningApplication *app=[NSRunningApplication runningApplicationWithProcessIdentifier:self.pid];CGRect parent=CGRectNull;
    BOOL activeOK=app&&[app.bundleIdentifier isEqualToString:@"org.videolan.vlc-thumbs.development"]&&app.active;
    BOOL parentContains=FindMainWindow(self.pid,self.crop,self.point,&parent);BOOL ownerOK=activeOK&&parentContains;
    NSMutableDictionary *row=[@{@"kind":@"display_frame",@"index":@(self.frames),@"frame_status":@(status),
        @"presentation_pts_seconds":@(pts),@"presentation_pts_value":@(CMSampleBufferGetPresentationTimeStamp(sampleBuffer).value),
        @"presentation_pts_timescale":@(CMSampleBufferGetPresentationTimeStamp(sampleBuffer).timescale),
        @"display_time_mach_ticks":@(displayTicks),
        @"display_time_present":@(displayTicks>0),
        @"display_time_uptime_seconds":@(MachSeconds(displayTicks)),@"callback_received_uptime_s":@(receipt),
        @"input_t0_uptime_s":@(self.inputT0),@"input_to_callback_ms":@((receipt-self.inputT0)*1000.0),
        @"crop_screen_points":@[@(self.crop.origin.x),@(self.crop.origin.y),@(self.crop.size.width),@(self.crop.size.height)],
        @"actual_panel_rect":panelFound?@[@(actual.origin.x),@(actual.origin.y),@(actual.size.width),@(actual.size.height)]:(id)NSNull.null,
        @"actual_panel_window_id":panel[(id)kCGWindowNumber]?:@0,@"panel_rect_matches_crop":@(panelMatches),
        @"parent_window_contains_crop":@(parentContains),@"app_active":@(activeOK)} mutableCopy];
    {CVPixelBufferRef pixel=CMSampleBufferGetImageBuffer(sampleBuffer);
        if(pixel&&CVPixelBufferGetPixelFormatType(pixel)==kCVPixelFormatType_32BGRA&&CVPixelBufferGetWidth(pixel)==672&&CVPixelBufferGetHeight(pixel)==448){
            CVPixelBufferLockBaseAddress(pixel,kCVPixelBufferLock_ReadOnly);void *base=CVPixelBufferGetBaseAddress(pixel);size_t rowBytes=CVPixelBufferGetBytesPerRow(pixel),length=rowBytes*CVPixelBufferGetHeight(pixel);
            CGDataProviderRef provider=CGDataProviderCreateWithData(NULL,base,length,NULL);CGColorSpaceRef color=CGColorSpaceCreateWithName(kCGColorSpaceSRGB);
            CGImageRef image=CGImageCreate(672,448,8,32,rowBytes,color,kCGImageAlphaPremultipliedFirst|kCGBitmapByteOrder32Little,provider,NULL,false,kCGRenderingIntentDefault);
            if(image){row[@"result"]=PointImageStats(image);NSString *hash=row[@"result"][@"image_sample_hash_fnv1a64"];
                BOOL imageHashMatches=self.expectedHash&&[hash caseInsensitiveCompare:self.expectedHash]==NSOrderedSame;
                row[@"opaque_image_hash_matches_expected"]=self.expectedHash?@(imageHashMatches):(id)NSNull.null;
                row[@"expected_image_hash_match"]=self.expectedHash?@(imageHashMatches&&panelMatches):(id)NSNull.null;
                NSString *observedTime=row[@"result"][@"time_mask_hex"];
                NSUInteger timeDistance=self.expectedTimeMask?MaskDistance(observedTime,self.expectedTimeMask):NSUIntegerMax;
                NSUInteger previousDistance=self.previousTimeMask?MaskDistance(observedTime,self.previousTimeMask):NSUIntegerMax;
                BOOL timeMatches=self.expectedTimeMask&&timeDistance<=22;
                BOOL nearerNew=!self.previousTimeMask||timeDistance<previousDistance;
                row[@"expected_time_mask_hamming"]=self.expectedTimeMask?@(timeDistance):(id)NSNull.null;
                row[@"previous_time_mask_hamming"]=self.previousTimeMask?@(previousDistance):(id)NSNull.null;
                row[@"expected_time_mask_match_within_22_bits"]=self.expectedTimeMask?@(timeMatches):(id)NSNull.null;
                row[@"expected_time_nearer_than_previous"]=self.previousTimeMask?@(nearerNew):(id)NSNull.null;
                BOOL postInputPresentation=status==SCFrameStatusComplete&&displayTicks>0&&MachSeconds(displayTicks)>=self.inputT0&&pts>=self.inputT0;
                row[@"post_input_complete_presentation"]=@(postInputPresentation);
                row[@"expected_visible_match"]=@(postInputPresentation&&panelMatches&&imageHashMatches&&timeMatches&&nearerNew);
                if(self.saveLastImage){self.lastImageData=[NSData dataWithBytes:base length:length];self.lastRowBytes=rowBytes;}
                CGImageRelease(image);
            } else row[@"error"]=@"could_not_wrap_stream_pixel_buffer";
            if(color)CGColorSpaceRelease(color);if(provider)CGDataProviderRelease(provider);CVPixelBufferUnlockBaseAddress(pixel,kCVPixelBufferLock_ReadOnly);
        } else if(status==SCFrameStatusComplete)row[@"error"]=@"missing_or_unexpected_672x448_BGRA_frame";
        else row[@"image_stats_skipped_status"]=@(status);
    }
    if(!ownerOK)row[@"error"]=@"target_app_inactive_or_crop_left_owned_main_window";
    self.frames++;
    [self write:row];
    if(!ownerOK){self.fatalError=row[@"error"];self.finished=YES;return;}
    if(self.expectedHash&&[row[@"expected_visible_match"] boolValue]){self.matched=YES;self.finished=YES;return;}
    if(receipt>=self.deadline)self.finished=YES;
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
static CGImageRef ImageFromOwnedData(NSData *data,size_t rowBytes) {
    if(!data||rowBytes<672*4)return NULL;CGDataProviderRef provider=CGDataProviderCreateWithCFData((__bridge CFDataRef)data);CGColorSpaceRef color=CGColorSpaceCreateWithName(kCGColorSpaceSRGB);
    CGImageRef image=CGImageCreate(672,448,8,32,rowBytes,color,kCGImageAlphaPremultipliedFirst|kCGBitmapByteOrder32Little,provider,NULL,false,kCGRenderingIntentDefault);
    CGColorSpaceRelease(color);CGDataProviderRelease(provider);return image;
}
static void Usage(void) {
    fprintf(stderr,"usage: continuous-visible-probe --pid PID --rect x,y,336,224 --point x,y --expected-hash 16HEX --expected-time-mask 540HEX [--previous-time-mask 540HEX] --output work/...jsonl [--save-last-image work/...png]\n"
                   "   or: continuous-visible-probe --pid PID --rect x,y,336,224 --point x,y --settle-ms 1000 --output work/...jsonl [--save-last-image work/...png]\n");
}
int main(int argc,const char **argv){@autoreleasepool{
    int pid=0,settle=0;CGRect rect=CGRectNull;CGPoint point=CGPointMake(NAN,NAN);const char *expectedArg=NULL,*expectedTimeArg=NULL,*previousTimeArg=NULL,*outputArg=NULL,*saveArg=NULL;
    for(int i=1;i<argc;){
        if(!strcmp(argv[i],"--pid")&&i+1<argc&&pid==0){char *end=NULL;long n=strtol(argv[i+1],&end,10);if(end==argv[i+1]||*end||n<=0||n>INT32_MAX){Usage();return 2;}pid=(int)n;i+=2;}
        else if(!strcmp(argv[i],"--rect")&&i+1<argc&&CGRectIsNull(rect)){if(!ParseRect(argv[i+1],&rect)){Usage();return 2;}i+=2;}
        else if(!strcmp(argv[i],"--point")&&i+1<argc&&isnan(point.x)){if(!ParsePoint(argv[i+1],&point)){Usage();return 2;}i+=2;}
        else if(!strcmp(argv[i],"--expected-hash")&&i+1<argc&&!expectedArg){expectedArg=argv[i+1];if(!HashArgument(expectedArg)){Usage();return 2;}i+=2;}
        else if(!strcmp(argv[i],"--expected-time-mask")&&i+1<argc&&!expectedTimeArg){expectedTimeArg=argv[i+1];if(!TimeMaskArgument(expectedTimeArg)){Usage();return 2;}i+=2;}
        else if(!strcmp(argv[i],"--previous-time-mask")&&i+1<argc&&!previousTimeArg){previousTimeArg=argv[i+1];if(!TimeMaskArgument(previousTimeArg)){Usage();return 2;}i+=2;}
        else if(!strcmp(argv[i],"--settle-ms")&&i+1<argc&&settle==0){char *end=NULL;long n=strtol(argv[i+1],&end,10);if(end==argv[i+1]||*end||n<1||n>5000){Usage();return 2;}settle=(int)n;i+=2;}
        else if(!strcmp(argv[i],"--output")&&i+1<argc&&!outputArg){outputArg=argv[i+1];i+=2;}
        else if(!strcmp(argv[i],"--save-last-image")&&i+1<argc&&!saveArg){saveArg=argv[i+1];i+=2;}
        else {Usage();return 2;}
    }
    BOOL expectedMode=expectedArg&&expectedTimeArg;
    if(!pid||CGRectIsNull(rect)||rect.size.width!=336||rect.size.height!=224||isnan(point.x)||!isfinite(point.y)||!outputArg||
       (expectedMode==(settle>0))||(previousTimeArg&&!expectedMode)||((expectedArg||expectedTimeArg)&&!expectedMode)){Usage();return 2;}
    NSString *output=CanonicalFreshWorkFile([NSString stringWithUTF8String:outputArg]);NSString *save=saveArg?CanonicalFreshWorkFile([NSString stringWithUTF8String:saveArg]):nil;
    if(!output||(saveArg&&!save)){fprintf(stderr,"output and optional PNG must be fresh canonical absolute paths beneath work/\n");return 2;}
    FILE *file=fopen(output.fileSystemRepresentation,"wx");if(!file){perror("--output");return 2;}
    NSApplication *application=NSApplication.sharedApplication;
    BOOL policyAccepted=[application setActivationPolicy:NSApplicationActivationPolicyProhibited];
    NSRunningApplication *app=[NSRunningApplication runningApplicationWithProcessIdentifier:(pid_t)pid];NSString *guardError=nil;CGRect parent;
    if(!app||![app.bundleIdentifier isEqualToString:@"org.videolan.vlc-thumbs.development"]||!app.active||!FindMainWindow(pid,rect,point,&parent)||!OwnAXHit(pid,point,&guardError)){
        WriteJSON(file,@{@"kind":@"probe_error",@"error":guardError?:@"target must be active development VLC; crop and point must be inside its visible main window"});fclose(file);return 1;
    }
    SCDisplay *display=nil;NSError *error=nil;
    if(!FindDisplay(rect,&display,&error)){WriteJSON(file,@{@"kind":@"probe_error",@"error":error.localizedDescription?:@"display lookup failed"});fclose(file);return 1;}
    SCContentFilter *filter=[[SCContentFilter alloc]initWithDisplay:display excludingWindows:@[]];
    SCStreamConfiguration *config=[SCStreamConfiguration new];config.sourceRect=CGRectOffset(rect,-display.frame.origin.x,-display.frame.origin.y);config.width=672;config.height=448;config.pixelFormat=kCVPixelFormatType_32BGRA;config.colorSpaceName=kCGColorSpaceSRGB;
    config.minimumFrameInterval=CMTimeMake(1,60);config.queueDepth=3;config.showsCursor=NO;config.showMouseClicks=NO;config.capturesAudio=NO;config.captureMicrophone=NO;
    FrameObserver *observer=[FrameObserver new];observer.pid=pid;observer.crop=rect;observer.point=point;observer.output=file;
    observer.saveLastImage=save!=nil;
    dispatch_queue_t frameQueue=dispatch_queue_create("story002.continuous-visible.frames",DISPATCH_QUEUE_SERIAL);
    SCStream *stream=[[SCStream alloc]initWithFilter:filter configuration:config delegate:observer];
    observer.expectedHash=expectedArg?[NSString stringWithUTF8String:expectedArg]:nil;
    observer.expectedTimeMask=expectedTimeArg?[NSString stringWithUTF8String:expectedTimeArg]:nil;
    observer.previousTimeMask=previousTimeArg?[NSString stringWithUTF8String:previousTimeArg]:nil;
    NSError *addError=nil;if(![stream addStreamOutput:observer type:SCStreamOutputTypeScreen sampleHandlerQueue:frameQueue error:&addError]){
        WriteJSON(file,@{@"kind":@"probe_error",@"error":addError.localizedDescription?:@"could not add screen output"});fclose(file);return 1;
    }
    WriteJSON(file,@{@"kind":@"session",@"pid":@(pid),@"rect_screen_points":@[@(rect.origin.x),@(rect.origin.y),@(rect.size.width),@(rect.size.height)],@"point":@[@(point.x),@(point.y)],@"stream_width":@672,@"stream_height":@448,@"pixel_format":@"BGRA",@"fps_cap":@60,@"queue_depth":@3,@"cursor":@NO,@"audio":@NO,@"microphone":@NO,@"activation_requested":@NO,@"prohibited_policy_accepted":@(policyAccepted),@"observer_windows_created":@0,@"warmup_complete_frames_required":@1});
    if(!WaitForStart(stream,&error)){WriteJSON(file,@{@"kind":@"probe_error",@"error":error.localizedDescription?:@"stream start failed"});StopStream(stream);dispatch_sync(frameQueue,^{});fclose(file);return 1;}
    double warmDeadline=Now()+3.0;while(observer.warmFrames<1&&Now()<warmDeadline&&!observer.fatalError)usleep(1000);
    if(observer.warmFrames<1){NSString *why=observer.fatalError?:@"did not receive a complete 672x448 crop frame within 3s";WriteJSON(file,@{@"kind":@"probe_error",@"error":why});StopStream(stream);dispatch_sync(frameQueue,^{});fclose(file);return 1;}
    // Readiness callbacks only update warmFrames. Arm the measurement on the
    // serial frame queue before physical input; a second warm callback must
    // never terminate a new measurement or consume its first presentation.
    dispatch_sync(frameQueue,^{
        observer.finished=NO;observer.inputT0=Now();
        observer.deadline=observer.inputT0+(expectedArg?2.0:(double)settle/1000.0);
        observer.postInput=YES;
    });
    CGError warp=CGWarpMouseCursorPosition(point);CGEventRef event=CGEventCreateMouseEvent(NULL,kCGEventMouseMoved,point,kCGMouseButtonLeft);
    if(warp!=kCGErrorSuccess||!event){if(event)CFRelease(event);WriteJSON(file,@{@"kind":@"probe_error",@"input_t0_uptime_s":@(observer.inputT0),@"error":@"pointer placement failed"});StopStream(stream);dispatch_sync(frameQueue,^{});fclose(file);return 1;}
    CGEventPost(kCGHIDEventTap,event);CFRelease(event);
    while(!observer.finished&&Now()<observer.deadline)usleep(1000);
    NSError *stopError=StopStream(stream);dispatch_sync(frameQueue,^{});
    if(!observer.matched&&expectedMode)[observer write:@{@"kind":@"probe_error",@"input_t0_uptime_s":@(observer.inputT0),@"frames":@(observer.frames),@"error":observer.fatalError?:@"expected image and new time caption not observed within 2s"}];
    if(stopError)[observer write:@{@"kind":@"stream_stop_error",@"error":stopError.localizedDescription}];
    CGImageRef lastImage=save?ImageFromOwnedData(observer.lastImageData,observer.lastRowBytes):NULL;
    BOOL saveOK=!save||(lastImage&&SavePNG(lastImage,save));if(lastImage)CGImageRelease(lastImage);
    if(!saveOK)[observer write:@{@"kind":@"save_error",@"error":@"could not save last captured PNG"}];
    fflush(file);fclose(file);
    return (observer.matched||!expectedMode)&&!observer.fatalError&&!stopError&&saveOK?0:1;
}}
