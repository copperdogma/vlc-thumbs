// SPDX-License-Identifier: GPL-2.0-or-later
// Story 002 diagnostic: measure on-screen screenshot callback latency and
// calibrate visible preview glyph regions. Development-only; no VLC controls.
#import <AppKit/AppKit.h>
#import <ApplicationServices/ApplicationServices.h>
#import <ScreenCaptureKit/ScreenCaptureKit.h>
#import <ImageIO/ImageIO.h>
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
static void Usage(void) {
    fprintf(stderr,"usage: visible-capture-probe --rect x,y,w,h --count N [--output JSONL]\n"
                   "   or: visible-capture-probe --pid PID --point x,y [--settle-ms 500] [--count N] [--expected-hash HEX] [--expected-time-mask HEX --previous-time-mask HEX] [--save-last-image PNG] [--output JSONL]\n");
}
static BOOL ParseRect(const char *text, CGRect *out) {
    double v[4]; const char *p=text;
    for(int i=0;i<4;i++){char *end=NULL;v[i]=strtod(p,&end);if(end==p||!isfinite(v[i]))return NO;if(i<3){if(*end!=',')return NO;p=end+1;}else if(*end)return NO;}
    if(v[2]<=0||v[3]<=0||v[2]>4096||v[3]>4096)return NO;
    *out=CGRectMake(v[0],v[1],v[2],v[3]);return YES;
}
static BOOL ParsePoint(const char *text,CGPoint *out){char *end=NULL;double x=strtod(text,&end);if(end==text||*end!=','||!isfinite(x))return NO;const char *ytext=end+1;double y=strtod(ytext,&end);if(end==ytext||*end||!isfinite(y))return NO;*out=CGPointMake(x,y);return YES;}
static BOOL InScreenBounds(CGRect rect) { for(NSScreen *s in NSScreen.screens)if(CGRectContainsRect(s.frame,rect))return YES;return NO; }
static BOOL WriteJSON(FILE *out, NSDictionary *row) {
    NSData *d=[NSJSONSerialization dataWithJSONObject:row options:NSJSONWritingSortedKeys error:nil];
    if(!d)return NO;fwrite(d.bytes,1,d.length,out);fputc('\n',out);fflush(out);return YES;
}
static CFDataRef ProviderData(CGImageRef image) { return CGDataProviderCopyData(CGImageGetDataProvider(image)); }
static NSString *HashPixels(const uint8_t *p,size_t len,size_t width,size_t height,size_t bpp,size_t row,double *mean,size_t *sampleCount) {
    uint64_t h=14695981039346656037ULL,total=0;size_t samples=0,stride=MAX((size_t)1,(size_t)sqrt((double)(width*height)/4096.0));
    if(!p||!bpp||!row){if(mean)*mean=0;if(sampleCount)*sampleCount=0;return @"";}
    for(size_t y=0;y<height;y+=stride)for(size_t x=0;x<width;x+=stride){size_t at=y*row+x*bpp;if(at+bpp>len)continue;size_t colors=MIN((size_t)3,bpp);for(size_t c=0;c<colors;c++){h=(h^p[at+c])*1099511628211ULL;total+=p[at+c];}samples+=colors;}
    if(mean)*mean=samples?(double)total/samples:0;if(sampleCount)*sampleCount=samples;
    return [NSString stringWithFormat:@"%016llx",(unsigned long long)h];
}
static NSDictionary *GenericImageStats(CGImageRef image) {
    size_t w=CGImageGetWidth(image),h=CGImageGetHeight(image),bpp=CGImageGetBitsPerPixel(image)/8,row=CGImageGetBytesPerRow(image);
    CFDataRef d=ProviderData(image);if(!d)return @{@"pixel_width":@(w),@"pixel_height":@(h),@"stats_error":@"no_provider_data"};
    double mean=0;size_t samples=0;NSString *hash=HashPixels(CFDataGetBytePtr(d),CFDataGetLength(d),w,h,bpp,row,&mean,&samples);CFRelease(d);
    return @{@"pixel_width":@(w),@"pixel_height":@(h),@"sample_hash_fnv1a64":hash,@"sample_mean":@(mean),@"sample_count":@(samples)};
}
@interface CaptureBox : NSObject
@property(nonatomic) double received;
@property(nonatomic,assign) CGImageRef image;
@property(nonatomic,strong) NSError *error;
@end
@implementation CaptureBox
- (void)dealloc {if(_image)CGImageRelease(_image);}
@end
static BOOL CaptureRaw(CGRect rect,double timeout,CaptureBox *result) {
    result.received=0;result.image=NULL;result.error=nil;dispatch_semaphore_t done=dispatch_semaphore_create(0);
    if(@available(macOS 15.2,*)) [SCScreenshotManager captureImageInRect:rect completionHandler:^(CGImageRef image,NSError *error){
        result.received=Now();if(error)result.error=error;if(image)result.image=CGImageRetain(image);dispatch_semaphore_signal(done);
    }];
    else { result.error=[NSError errorWithDomain:@"VisibleCaptureProbe" code:1 userInfo:@{NSLocalizedDescriptionKey:@"captureImageInRect requires macOS 15.2"}];dispatch_semaphore_signal(done); }
    // This async API does not promise a background completion queue. Keep the
    // calling AppKit runloop alive instead of blocking the main thread.
    double deadline=Now()+timeout;
    while(dispatch_semaphore_wait(done,DISPATCH_TIME_NOW)) {
        if(Now()>=deadline)return NO;
        [[NSRunLoop currentRunLoop] runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.001]];
    }
    return result.image!=NULL&&!result.error;
}
static int CaptureRectMode(CGRect rect,int count,FILE *out) {
    if(!InScreenBounds(rect)){fprintf(stderr,"--rect must fit within one NSScreen frame in screen points\n");return 2;}
    int failures=0;
    for(int i=-5;i<count;i++){
        BOOL warm=i<0;int index=warm?i+5:i;double started=Now();CaptureBox *r=[CaptureBox new];
        BOOL ok=CaptureRaw(rect,10,r);NSDictionary *stats=r.image?GenericImageStats(r.image):@{};
        NSMutableDictionary *row=[@{@"kind":@"visible_capture_probe",@"index":@(index),@"warmup":@(warm),
            @"requested_rect_screen_points":@[@(rect.origin.x),@(rect.origin.y),@(rect.size.width),@(rect.size.height)],
            @"started_uptime_s":@(started),@"callback_received_uptime_s":@(r.received),
            @"callback_latency_ms":@((r.received-started)*1000),@"result":stats,
            @"error":r.error.localizedDescription ?: (ok?(id)NSNull.null:@"capture_timeout_or_missing_image")} mutableCopy];
        if(!r.received)row[@"error"]=@"capture_timeout_after_10s";
        WriteJSON(out,row);if(!ok)failures++;
    }
    return failures?1:0;
}
static BOOL ParseWindowBounds(NSDictionary *entry,CGRect *bounds) {
    NSDictionary *b=entry[(id)kCGWindowBounds];if(![b isKindOfClass:NSDictionary.class])return NO;
    double x=[b[@"X"] doubleValue],y=[b[@"Y"] doubleValue],w=[b[@"Width"] doubleValue],h=[b[@"Height"] doubleValue];
    if(!isfinite(x)||!isfinite(y)||!isfinite(w)||!isfinite(h)||w<=0||h<=0)return NO;
    *bounds=CGRectMake(x,y,w,h);return YES;
}
static BOOL FindMainWindow(pid_t pid,CGPoint point,CGRect *bounds) {
    NSArray *list=CFBridgingRelease(CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly,kCGNullWindowID));
    for(NSDictionary *e in list){if([e[(id)kCGWindowOwnerPID] intValue]!=pid||[e[(id)kCGWindowLayer] intValue]!=0)continue;CGRect b;if(ParseWindowBounds(e,&b)&&CGRectContainsPoint(b,point)){*bounds=b;return YES;}}
    return NO;
}
static NSDictionary *ImageROIStats(CGImageRef image,CGRect pointRect) {
    double scale=(double)CGImageGetWidth(image)/336.0;
    CGRect pixels=CGRectMake(round(pointRect.origin.x*scale),round(pointRect.origin.y*scale),round(pointRect.size.width*scale),round(pointRect.size.height*scale));
    CGImageRef crop=CGImageCreateWithImageInRect(image,pixels);if(!crop)return @{@"roi_error":@"crop_failed"};
    NSDictionary *stats=GenericImageStats(crop);CGImageRelease(crop);return stats;
}
static BOOL FindPreviewWindow(pid_t pid,CGRect *bounds,NSDictionary **metadata) {
    NSArray *list=CFBridgingRelease(CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly,kCGNullWindowID));
    for(NSDictionary *e in list){if([e[(id)kCGWindowOwnerPID] intValue]!=pid)continue;int level=[e[(id)kCGWindowLayer] intValue];if(level!=3&&level!=9)continue;CGRect b;if(!ParseWindowBounds(e,&b))continue;
        if(fabs(b.size.width-336)>1||fabs(b.size.height-224)>1)continue;*bounds=b;*metadata=e;return YES;}
    return NO;
}
static BOOL ValidateOwnHit(pid_t pid,CGPoint point,NSString **why) {
    AXUIElementRef system=AXUIElementCreateSystemWide(),hit=NULL;pid_t hitPID=0;
    AXError e=AXUIElementCopyElementAtPosition(system,(float)point.x,(float)point.y,&hit);
    if(e==kAXErrorSuccess&&hit)AXUIElementGetPid(hit,&hitPID);
    if(hit)CFRelease(hit);CFRelease(system);
    if(e!=kAXErrorSuccess){*why=[NSString stringWithFormat:@"AX ownership hit-test failed (%d)",e];return NO;}
    if(hitPID!=pid){*why=[NSString stringWithFormat:@"point hit PID %d, expected VLC PID %d",hitPID,pid];return NO;}
    return YES;
}
static NSString *MaskForRect(const uint8_t *p,size_t len,size_t width,size_t height,size_t bpp,size_t row,CGRect roi,double scale,NSUInteger *glyphs) {
    NSUInteger cols=(NSUInteger)llround(roi.size.width),rows=(NSUInteger)llround(roi.size.height);NSMutableString *hex=[NSMutableString string];unsigned nibble=0,bits=0;*glyphs=0;
    for(NSUInteger y=0;y<rows;y++)for(NSUInteger x=0;x<cols;x++){
        size_t px=(size_t)floor((roi.origin.x+x+0.5)*scale),py=(size_t)floor((roi.origin.y+y+0.5)*scale),at=py*row+px*bpp;BOOL white=NO;
        if(p&&bpp>=3&&px<width&&py<height&&at+bpp<=len){unsigned mean=((unsigned)p[at]+p[at+1]+p[at+2])/3;white=mean>180;}
        if(white)*glyphs+=1;nibble=(nibble<<1)|(white?1:0);bits++;
        if(bits==4){[hex appendFormat:@"%x",nibble];nibble=0;bits=0;}
    }
    if(bits)[hex appendFormat:@"%x",nibble<<(4-bits)];return hex;
}
static NSUInteger Hamming(NSString *a,NSString *b) {
    if(a.length!=b.length)return NSUIntegerMax;NSUInteger d=0;
    for(NSUInteger i=0;i<a.length;i++){unsigned x=0,y=0;[[NSScanner scannerWithString:[a substringWithRange:NSMakeRange(i,1)]] scanHexInt:&x];[[NSScanner scannerWithString:[b substringWithRange:NSMakeRange(i,1)]] scanHexInt:&y];x^=y;while(x){d+=x&1;x>>=1;}}
    return d;
}
static BOOL ValidMask(const char *text){if(!text||strlen(text)!=540)return NO;for(const char *p=text;*p;p++)if(!((*p>='0'&&*p<='9')||(*p>='a'&&*p<='f')||(*p>='A'&&*p<='F')))return NO;return YES;}
static NSDictionary *PointImageStats(CGImageRef image,NSString **timeMaskOut,NSUInteger *timeGlyphsOut) {
    size_t w=CGImageGetWidth(image),h=CGImageGetHeight(image),bpp=CGImageGetBitsPerPixel(image)/8,row=CGImageGetBytesPerRow(image);
    CFDataRef d=ProviderData(image);if(!d)return @{@"stats_error":@"no_provider_data",@"pixel_width":@(w),@"pixel_height":@(h)};
    const uint8_t *p=CFDataGetBytePtr(d);size_t len=CFDataGetLength(d);double scale=(double)w/336.0;
    NSUInteger tg=0,sg=0;NSString *tm=MaskForRect(p,len,w,h,bpp,row,CGRectMake(8,196,108,20),scale,&tg);
    NSString *sm=MaskForRect(p,len,w,h,bpp,row,CGRectMake(117,196,211,20),scale,&sg);
    NSDictionary *imageROI=ImageROIStats(image,CGRectMake(8,9,320,180));
    NSDictionary *timeROI=ImageROIStats(image,CGRectMake(8,196,108,20));
    NSDictionary *stateROI=ImageROIStats(image,CGRectMake(117,196,211,20));
    NSDictionary *result=@{@"pixel_width":@(w),@"pixel_height":@(h),@"scale_from_336_points":@(scale),
        @"panel_sample_hash_fnv1a64":HashPixels(p,len,w,h,bpp,row,NULL,NULL),@"image_roi_points":@[@8,@9,@320,@180],
        @"image_sample_hash_fnv1a64":imageROI[@"sample_hash_fnv1a64"]?:@"",
        @"image_sample_mean":imageROI[@"sample_mean"]?:@0,
        @"time_roi_points":@[@8,@196,@108,@20],@"time_sample_hash_fnv1a64":timeROI[@"sample_hash_fnv1a64"]?:@"",
        @"time_sample_mean":timeROI[@"sample_mean"]?:@0,
        @"state_roi_points":@[@117,@196,@211,@20],@"time_mask_hex":tm,@"time_glyph_count":@(tg),
        @"state_sample_hash_fnv1a64":stateROI[@"sample_hash_fnv1a64"]?:@"",
        @"state_sample_mean":stateROI[@"sample_mean"]?:@0,@"state_mask_hex":sm,@"state_glyph_count":@(sg)};
    *timeMaskOut=tm;*timeGlyphsOut=tg;CFRelease(d);return result;
}
static BOOL SavePNG(CGImageRef image,NSString *path) {
    if(!image||!path.length||[[NSFileManager defaultManager] fileExistsAtPath:path])return NO;
    NSURL *url=[NSURL fileURLWithPath:path];CGImageDestinationRef dest=CGImageDestinationCreateWithURL((__bridge CFURLRef)url,CFSTR("public.png"),1,NULL);
    if(!dest)return NO;CGImageDestinationAddImage(dest,image,NULL);BOOL ok=CGImageDestinationFinalize(dest);CFRelease(dest);return ok;
}
static int PointMode(pid_t pid,CGPoint point,int settleMS,int maxCount,NSString *expectedHash,NSString *expectedMask,NSString *previousMask,NSString *savePath,FILE *out) {
    NSRunningApplication *app=[NSRunningApplication runningApplicationWithProcessIdentifier:pid];
    if(!app||![app.bundleIdentifier isEqualToString:@"org.videolan.vlc-thumbs.development"]||!app.active){fprintf(stderr,"--pid must identify the active org.videolan.vlc-thumbs.development app\n");return 2;}
    CGRect parent;
    if(!FindMainWindow(pid,point,&parent)){fprintf(stderr,"--point must lie inside an on-screen layer-zero VLC window\n");return 2;}
    NSString *why=nil;if(!ValidateOwnHit(pid,point,&why)){fprintf(stderr,"%s\n",why.UTF8String);return 2;}
    if(savePath&&[[NSFileManager defaultManager] fileExistsAtPath:savePath]){fprintf(stderr,"--save-last-image path already exists\n");return 2;}
    // Warm only the read-only measurement API on the preceding owned panel;
    // no pointer event, decoder request or cache population occurs here.
    NSMutableArray *warmupLatencies=[NSMutableArray array];
    CGRect oldPanel;NSDictionary *oldMetadata=nil;
    if(FindPreviewWindow(pid,&oldPanel,&oldMetadata)&&CGRectContainsRect(parent,oldPanel)) {
        for(int i=0;i<5;i++) {
            double began=Now();CaptureBox *warm=[CaptureBox new];
            if(!CaptureRaw(oldPanel,2.0,warm)){fprintf(stderr,"observer warmup capture failed\n");return 1;}
            [warmupLatencies addObject:@((warm.received-began)*1000)];
        }
    }
    // Input origin is captured before either physical cursor placement or event posting.
    double inputT0=Now();CGError warp=CGWarpMouseCursorPosition(point);
    CGEventRef event=CGEventCreateMouseEvent(NULL,kCGEventMouseMoved,point,kCGMouseButtonLeft);
    if(warp!=kCGErrorSuccess||!event){if(event)CFRelease(event);fprintf(stderr,"pointer placement failed (%d)\n",warp);return 1;}
    CGEventPost(kCGHIDEventTap,event);CFRelease(event);
    double deadline=inputT0+(expectedHash||expectedMask?2.0:(double)settleMS/1000.0);
    NSString *lastMask=nil;BOOL matched=NO;int captures=0,failures=0;double previousReceipt=0;CGImageRef lastImage=NULL;
    do {
        CGRect panel=CGRectNull;NSDictionary *window=nil;double findDeadline=MIN(deadline,Now()+2.0);
        while(Now()<findDeadline&&!FindPreviewWindow(pid,&panel,&window))usleep(10000);
        if(CGRectIsNull(panel)){
            WriteJSON(out,@{@"kind":@"visible_preview_capture",@"index":@(captures),@"input_t0_uptime_s":@(inputT0),@"error":@"owned_preview_window_not_found_before_deadline"});failures++;break;
        }
        if(!CGRectContainsRect(parent,panel)){WriteJSON(out,@{@"kind":@"visible_preview_capture",@"index":@(captures),@"input_t0_uptime_s":@(inputT0),@"window_bounds_screen_points":@[@(panel.origin.x),@(panel.origin.y),@(panel.size.width),@(panel.size.height)],@"error":@"owned_preview_rect_not_contained_by_parent_window"});failures++;break;}
        double remaining=deadline-Now();if(remaining<0.03)break;
        CaptureBox *r=[CaptureBox new];BOOL ok=CaptureRaw(panel,2.0,r);captures++;
        if(!r.received){WriteJSON(out,@{@"kind":@"visible_preview_capture",@"observer_warmup_callback_ms":warmupLatencies,@"index":@(captures-1),@"input_t0_uptime_s":@(inputT0),@"window_bounds_screen_points":@[@(panel.origin.x),@(panel.origin.y),@(panel.size.width),@(panel.size.height)],@"error":r.error.localizedDescription?:@"capture_timeout_after_2s"});failures++;break;}
        NSString *tm=nil;NSUInteger glyphs=0;NSDictionary *stats=r.image?PointImageStats(r.image,&tm,&glyphs):@{};
        NSString *hash=stats[@"image_sample_hash_fnv1a64"];
        BOOL hashMatch=expectedHash&&[hash caseInsensitiveCompare:expectedHash]==NSOrderedSame;
        NSUInteger maskDistance=expectedMask?Hamming(tm,expectedMask):NSUIntegerMax;
        NSUInteger tolerance=(NSUInteger)ceil(108.0*20.0*0.01);
        BOOL maskMatch=expectedMask&&maskDistance<=tolerance;
        NSMutableDictionary *row=[@{@"kind":@"visible_preview_capture",@"index":@(captures-1),@"input_t0_uptime_s":@(inputT0),
            @"callback_received_uptime_s":@(r.received),@"input_to_callback_ms":@((r.received-inputT0)*1000),
            @"callback_to_callback_ms":@(previousReceipt?(r.received-previousReceipt)*1000:0),
            @"window_id":window[(id)kCGWindowNumber]?:@0,@"window_level":window[(id)kCGWindowLayer]?:@0,
            @"window_bounds_screen_points":@[@(panel.origin.x),@(panel.origin.y),@(panel.size.width),@(panel.size.height)],
            @"result":stats,@"previous_time_mask_hex":lastMask?:@"",@"time_mask_changed_since_previous":@(lastMask&&![lastMask isEqualToString:tm]),
            @"previous_calibration_time_mask_hex":previousMask?:@"",
            @"expected_differs_from_previous_calibration":previousMask?@(![previousMask isEqualToString:expectedMask]):(id)NSNull.null,
            @"expected_hash_match":expectedHash?@(hashMatch):(id)NSNull.null,@"expected_time_mask_hamming":expectedMask?@(maskDistance):(id)NSNull.null,
            @"expected_time_mask_match_within_1pct":expectedMask?@(maskMatch):(id)NSNull.null,
            @"error":ok?(id)NSNull.null:(r.error.localizedDescription?:@"capture_failed")} mutableCopy];
        if(lastMask)row[@"previous_time_mask_distinct"]=@(![lastMask isEqualToString:tm]);
        WriteJSON(out,row);if(!ok)failures++;
        previousReceipt=r.received;lastMask=tm;
        if(r.image){if(lastImage)CGImageRelease(lastImage);lastImage=CGImageRetain(r.image);}
        if(hashMatch||maskMatch){matched=YES;break;}
        if(!expectedHash&&!expectedMask&&captures>=maxCount)break;
    } while(Now()<deadline&&captures<maxCount);
    if(savePath&&!SavePNG(lastImage,savePath)){fprintf(stderr,"could not save PNG to requested path\n");failures++;}
    if(lastImage)CGImageRelease(lastImage);
    if((expectedHash||expectedMask)&&!matched){WriteJSON(out,@{@"kind":@"visible_preview_capture",@"input_t0_uptime_s":@(inputT0),@"captures":@(captures),@"error":@"expected_image_not_observed_within_2s"});failures++;}
    return failures?1:0;
}
static NSString *CanonicalFreshWorkFile(NSString *input) {
    if(![input isKindOfClass:NSString.class]||!input.isAbsolutePath||![input isEqualToString:input.stringByStandardizingPath])return nil;
    char cwd[PATH_MAX];if(!getcwd(cwd,sizeof(cwd)))return nil;
    char *root=realpath(cwd,NULL);if(!root)return nil;
    NSString *rootPath=[NSString stringWithUTF8String:root];free(root);
    if(![[NSFileManager defaultManager] fileExistsAtPath:[rootPath stringByAppendingPathComponent:@"AGENTS.md"]])return nil;
    NSString *workPath=[rootPath stringByAppendingPathComponent:@"work"];
    char *resolvedWork=realpath(workPath.fileSystemRepresentation,NULL);if(!resolvedWork)return nil;
    NSString *canonicalWork=[NSString stringWithUTF8String:resolvedWork];free(resolvedWork);
    if(![canonicalWork isEqualToString:workPath])return nil;
    NSString *parent=input.stringByDeletingLastPathComponent;
    char *resolvedParent=realpath(parent.fileSystemRepresentation,NULL);if(!resolvedParent)return nil;
    NSString *canonicalParent=[NSString stringWithUTF8String:resolvedParent];free(resolvedParent);
    if(![canonicalParent isEqualToString:parent]||
       !([canonicalParent isEqualToString:canonicalWork]||[canonicalParent hasPrefix:[canonicalWork stringByAppendingString:@"/"]]))return nil;
    struct stat st;if(lstat(input.fileSystemRepresentation,&st)==0||errno!=ENOENT)return nil;
    return input;
}
static NSDictionary *ReadCommandLine(const char *line,size_t length,NSString **errorText) {
    NSData *data=[NSData dataWithBytes:line length:length];NSError *error=nil;
    id value=[NSJSONSerialization JSONObjectWithData:data options:NSJSONReadingFragmentsAllowed error:&error];
    if(![value isKindOfClass:NSDictionary.class]){*errorText=error.localizedDescription?:@"command must be one JSON object";return nil;}
    return value;
}
static size_t CountLines(NSString *path) {
    FILE *file=fopen(path.fileSystemRepresentation,"rb");if(!file)return 0;size_t count=0;int ch;
    while((ch=fgetc(file))!=EOF)if(ch=='\n')count++;fclose(file);return count;
}
static BOOL FiniteNumber(id value,double *number) {
    if(![value isKindOfClass:NSNumber.class]||CFGetTypeID((__bridge CFTypeRef)value)==CFBooleanGetTypeID())return NO;
    *number=[value doubleValue];return isfinite(*number);
}
static void ServerAck(BOOL ready,pid_t target,int returnCode,NSString *output,size_t count,NSString *error) {
    NSMutableDictionary *row=ready?[@{@"ready":@YES,@"server_pid":@(getpid()),@"target_pid":@(target)} mutableCopy]:
        [@{@"returncode":@(returnCode),@"output":output?:NSNull.null,@"count":@(count)} mutableCopy];
    (void)error;
    WriteJSON(stdout,row);
}
static int Serve(pid_t target) {
    (void)NSApplication.sharedApplication;
    ServerAck(YES,target,0,nil,0,nil);
    char *line=NULL;size_t capacity=0;ssize_t length;
    while((length=getline(&line,&capacity,stdin))!=-1){
        @autoreleasepool {
            NSString *errorText=nil,*output=nil,*savePath=nil;size_t count=0;int rc=2;FILE *file=NULL;
            if(length>65536){errorText=@"command exceeds 65536 bytes";ServerAck(NO,target,rc,nil,0,errorText);continue;}
            NSDictionary *command=ReadCommandLine(line,(size_t)length,&errorText);
            NSSet *allowed=[NSSet setWithArray:@[@"point",@"output",@"expected_hash",@"settle_ms",@"count",@"save_last_image"]];
            for(id key in command)if(![allowed containsObject:key]){errorText=[NSString stringWithFormat:@"unsupported command field: %@",key];break;}
            NSArray *pointValues=command[@"point"];double x=0,y=0;
            if(!errorText&&(![pointValues isKindOfClass:NSArray.class]||pointValues.count!=2||!FiniteNumber(pointValues[0],&x)||!FiniteNumber(pointValues[1],&y)))errorText=@"point must be two finite coordinates";
            NSString *outputInput=command[@"output"];
            if(!errorText){output=CanonicalFreshWorkFile(outputInput);if(!output)errorText=@"output must be a fresh canonical file beneath work/";}
            NSString *expected=command[@"expected_hash"];
            BOOL hasExpected=expected!=nil;
            int settle=500,maximum=100;
            if(!errorText&&hasExpected){
                if(![expected isKindOfClass:NSString.class]||expected.length!=16)errorText=@"expected_hash must be a 16-character image hash";
                for(NSUInteger i=0;!errorText&&i<expected.length;i++){unichar c=[expected characterAtIndex:i];if(!((c>='0'&&c<='9')||(c>='a'&&c<='f')||(c>='A'&&c<='F')))errorText=@"expected_hash must be hexadecimal";}
                if(command[@"settle_ms"])errorText=@"expected_hash cannot be combined with settle_ms";
            } else if(!errorText) {
                double d=0;if(!FiniteNumber(command[@"settle_ms"],&d)||floor(d)!=d||d<1||d>2000)errorText=@"settle_ms must be an integer in [1,2000]";else settle=(int)d;
            }
            if(!errorText&&command[@"count"]){double d=0;if(!FiniteNumber(command[@"count"],&d)||floor(d)!=d||d<1||d>100)errorText=@"count must be an integer in [1,100]";else maximum=(int)d;}
            if(!errorText&&command[@"save_last_image"]){savePath=CanonicalFreshWorkFile(command[@"save_last_image"]);if(!savePath)errorText=@"save_last_image must be a fresh canonical file beneath work/";}
            if(!errorText){file=fopen(output.fileSystemRepresentation,"wx");if(!file)errorText=@"could not create fresh output file";}
            if(!errorText){rc=PointMode(target,CGPointMake(x,y),settle,maximum,hasExpected?expected:nil,nil,nil,savePath,file);fflush(file);fclose(file);file=NULL;count=CountLines(output);}
            if(file)fclose(file);
            ServerAck(NO,target,errorText?2:rc,output,count,errorText);
        }
    }
    free(line);return 0;
}
int main(int argc,const char **argv){@autoreleasepool{
    if(argc==3&&!strcmp(argv[1],"--serve")){char *end=NULL;long n=strtol(argv[2],&end,10);if(end==argv[2]||*end||n<=0||n>INT32_MAX){Usage();return 2;}return Serve((pid_t)n);}
    CGRect rect=CGRectNull;int count=0,settleMS=500,pid=0;CGPoint point=CGPointMake(NAN,NAN);
    const char *outputPath=NULL,*expectedHashArg=NULL,*expectedMaskArg=NULL,*previousMaskArg=NULL,*saveArg=NULL;
    for(int i=1;i<argc;){
        if(!strcmp(argv[i],"--rect")&&i+1<argc&&CGRectIsNull(rect)){if(!ParseRect(argv[i+1],&rect)){Usage();return 2;}i+=2;}
        else if(!strcmp(argv[i],"--count")&&i+1<argc&&count==0){char *e=NULL;long n=strtol(argv[i+1],&e,10);if(e==argv[i+1]||*e||n<1||n>100){Usage();return 2;}count=(int)n;i+=2;}
        else if(!strcmp(argv[i],"--pid")&&i+1<argc&&pid==0){char *e=NULL;long n=strtol(argv[i+1],&e,10);if(e==argv[i+1]||*e||n<1||n>INT32_MAX){Usage();return 2;}pid=(int)n;i+=2;}
        else if(!strcmp(argv[i],"--point")&&i+1<argc&&isnan(point.x)){if(!ParsePoint(argv[i+1],&point)){Usage();return 2;}i+=2;}
        else if(!strcmp(argv[i],"--settle-ms")&&i+1<argc){char *e=NULL;long n=strtol(argv[i+1],&e,10);if(e==argv[i+1]||*e||n<1||n>2000){Usage();return 2;}settleMS=(int)n;i+=2;}
        else if(!strcmp(argv[i],"--output")&&i+1<argc&&!outputPath){outputPath=argv[i+1];i+=2;}
        else if(!strcmp(argv[i],"--expected-hash")&&i+1<argc&&!expectedHashArg){expectedHashArg=argv[i+1];i+=2;}
        else if(!strcmp(argv[i],"--expected-time-mask")&&i+1<argc&&!expectedMaskArg){expectedMaskArg=argv[i+1];if(!ValidMask(expectedMaskArg)){Usage();return 2;}i+=2;}
        else if(!strcmp(argv[i],"--previous-time-mask")&&i+1<argc&&!previousMaskArg){previousMaskArg=argv[i+1];if(!ValidMask(previousMaskArg)){Usage();return 2;}i+=2;}
        else if(!strcmp(argv[i],"--save-last-image")&&i+1<argc&&!saveArg){saveArg=argv[i+1];i+=2;}
        else {Usage();return 2;}
    }
    (void)NSApplication.sharedApplication;
    FILE *out=stdout;if(outputPath){out=fopen(outputPath,"wx");if(!out){perror("--output");return 2;}}
    int result;
    if(pid||!isnan(point.x)){
        if(!pid||isnan(point.x)||!isfinite(point.x)||!isfinite(point.y)||!CGRectIsNull(rect)||
           (previousMaskArg&&!expectedMaskArg)||(expectedHashArg&&expectedMaskArg)||
           (expectedMaskArg&&previousMaskArg&&!strcasecmp(expectedMaskArg,previousMaskArg))) {Usage();result=2;}
        else result=PointMode((pid_t)pid,point,settleMS,count?count:100,expectedHashArg?[NSString stringWithUTF8String:expectedHashArg]:nil,
            expectedMaskArg?[NSString stringWithUTF8String:expectedMaskArg]:nil,previousMaskArg?[NSString stringWithUTF8String:previousMaskArg]:nil,
            saveArg?[NSString stringWithUTF8String:saveArg]:nil,out);
    } else if(!CGRectIsNull(rect)&&count>0) result=CaptureRectMode(rect,count,out);
    else {Usage();result=2;}
    if(outputPath)fclose(out);return result;
}}
