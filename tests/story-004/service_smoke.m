// SPDX-License-Identifier: GPL-2.0-or-later
#import <Cocoa/Cocoa.h>
#import "VLCThumbnailService.h"
static void Spin(double s) {double end=NSProcessInfo.processInfo.systemUptime+s;do{[NSRunLoop.mainRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:.001]];}while(NSProcessInfo.processInfo.systemUptime<end);}
static NSDictionary *Request(VLCThumbnailService *s,NSURL *url,NSString *gen,int64_t t) {
    __block NSDictionary *reply=nil;
    [s requestURL:url generation:gen videoOrdinal:0 videoCount:1 time:t completion:^(NSImage *image,NSDictionary *r){
        if(![r[@"preparing"] boolValue]) {NSMutableDictionary *v=[r mutableCopy];v[@"has_image"]=@(image!=nil);reply=v;}
    }];
    for(int i=0;i<20000&&!reply;i++)Spin(.001);
    return reply ?: @{@"error":@"test-timeout"};
}
int main(int argc,const char **argv) {@autoreleasepool {
    if(argc!=2&&argc!=5)return 2;[NSApplication sharedApplication];NSString *repo=@(argv[1]);
    NSURL *url=[NSURL fileURLWithPath:argc==5?@(argv[2]):[repo stringByAppendingPathComponent:@"work/fixtures/story-002/standard.mp4"]];
    NSString *helper=[repo stringByAppendingPathComponent:@"work/build/thumbnail-helper/thumbnail-helper"];
    NSString *cache=[repo stringByAppendingPathComponent:[@"work/validation/story004/service-smoke-" stringByAppendingString:NSUUID.UUID.UUIDString]];
    VLCThumbnailService *s=[[VLCThumbnailService alloc] initWithHelperPath:helper cacheRoot:cache];
    NSMutableArray *records=[NSMutableArray array];BOOL passed=YES;
    NSMutableArray<NSNumber *> *times=[NSMutableArray arrayWithArray:@[@5000000,@2000000,@12000000,@5000000]];
    if(argc==5) {
        [times removeAllObjects];
        for(NSString *value in [@(argv[4]) componentsSeparatedByString:@","]) {
            double seconds=value.doubleValue;if(!isfinite(seconds)||seconds<0)return 2;
            [times addObject:@((int64_t)llround(seconds*1000000))];
        }
        if(!times.count)return 2;
    }
    for(NSNumber *time in times) {
        NSDictionary *r=Request(s,url,@"first",time.longLongValue);[records addObject:r];passed&=[r[@"has_image"] boolValue];
    }
    passed&=[s.metrics[@"launched"] unsignedIntegerValue]==1;
    [s shutdown];Spin(.05);
    s=[[VLCThumbnailService alloc] initWithHelperPath:helper cacheRoot:cache];
    NSDictionary *reopen=Request(s,url,@"second",times.firstObject.longLongValue);[records addObject:reopen];
    passed&=[reopen[@"has_image"] boolValue]&&[reopen[@"cache"] isEqual:@"disk"]&&[s.metrics[@"launched"] unsignedIntegerValue]==0;
    [s shutdown];Spin(.05);
    NSData *data=[NSJSONSerialization dataWithJSONObject:@{@"passed":@(passed),@"records":records} options:NSJSONWritingPrettyPrinted error:nil];
        NSString *output=argc==5?@(argv[3]):[repo stringByAppendingPathComponent:@"work/validation/story004/service-smoke.json"];
    NSString *allowed=[repo stringByAppendingPathComponent:@"work/validation/story004/"];
    if(![output hasPrefix:allowed])return 2;
    [data writeToFile:output atomically:YES];
    [NSFileManager.defaultManager removeItemAtPath:cache error:nil];printf("Service smoke: %s\n",passed?"PASS":"FAIL");return passed?0:1;
}}
