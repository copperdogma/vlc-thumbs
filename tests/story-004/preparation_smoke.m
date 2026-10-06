// SPDX-License-Identifier: GPL-2.0-or-later
#import <Cocoa/Cocoa.h>
#import "VLCThumbnailService.h"
static double Now(void){return NSProcessInfo.processInfo.systemUptime;}
static void Spin(double seconds){double end=Now()+seconds;do{[NSRunLoop.mainRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:.002]];}while(Now()<end);}
int main(int argc,const char **argv){@autoreleasepool {
 if(argc!=2)return 2;[NSApplication sharedApplication];NSString *repo=@(argv[1]);
 NSString *helper=[repo stringByAppendingPathComponent:@"work/build/thumbnail-helper/thumbnail-helper"];
 NSString *cache=[repo stringByAppendingPathComponent:[@"work/validation/story004/preparation-smoke-" stringByAppendingString:NSUUID.UUID.UUIDString]];
 NSURL *url=[NSURL fileURLWithPath:[repo stringByAppendingPathComponent:@"work/fixtures/story-002/standard-cache-pressure.mp4"]];
 NSDictionary *context=@{@"url":url,@"generation":@"first",@"videoOrdinal":@0,@"videoCount":@1,@"duration":@90037333,@"eligible":@YES};
 VLCThumbnailService *service=[[VLCThumbnailService alloc] initWithHelperPath:helper cacheRoot:cache];
 double began=Now();[service prepareContext:context enabled:YES];
 while([service.metrics[@"completed"] intValue]<7&&Now()-began<20)Spin(.01);
 NSDictionary *first=service.metrics;double elapsed=Now()-began;
 BOOL passed=[first[@"completed"] intValue]==7&&[first[@"launched"] intValue]==1&&[first[@"worker_requests"] intValue]==7;
 [service shutdown];Spin(.05);
 service=[[VLCThumbnailService alloc] initWithHelperPath:helper cacheRoot:cache];
 NSMutableDictionary *reopened=[context mutableCopy];reopened[@"generation"]=@"second";
 [service prepareContext:reopened enabled:YES];Spin(2);
 NSDictionary *second=service.metrics;passed&=[second[@"completed"] intValue]>=1&&[second[@"worker_requests"] intValue]==0&&[second[@"launched"] intValue]==0;
 [service shutdown];Spin(.05);
 NSDictionary *result=@{@"passed":@(passed),@"scope":@"Real helper, generated90s video, no hover; finite7-target proactive plan then new service reloads coverage without decoding",@"coverage_seconds":@(elapsed),@"first":first,@"reopen":second};
 NSData *data=[NSJSONSerialization dataWithJSONObject:result options:NSJSONWritingPrettyPrinted error:nil];
 [data writeToFile:[repo stringByAppendingPathComponent:@"work/validation/story004/preparation-smoke.json"] atomically:YES];
 [NSFileManager.defaultManager removeItemAtPath:cache error:nil];printf("Preparation smoke: %s\n",passed?"PASS":"FAIL");return passed?0:1;
}}
