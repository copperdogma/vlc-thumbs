// SPDX-License-Identifier: GPL-2.0-or-later
#import <Cocoa/Cocoa.h>
#import "VLCThumbnailService.h"
#import "VLCThumbnailWorker.h"
#import "VLCThumbnailCache.h"
static NSUInteger failed;static NSString *root,*repo;static NSMutableArray *checks;
static double Now(void){return NSProcessInfo.processInfo.systemUptime;}
static void Spin(double s){double end=Now()+s;do{[NSRunLoop.mainRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:.001]];}while(Now()<end);}
static void Check(NSString *name,BOOL passed,NSDictionary *detail){[checks addObject:@{@"name":name,@"passed":@(passed),@"detail":detail?:@{}}];if(!passed){failed++;fprintf(stderr,"FAIL %s\n",name.UTF8String);}}
static NSURL *Input(NSString *name,NSString *mode){NSString *p=[root stringByAppendingPathComponent:name];[mode writeToFile:p atomically:YES encoding:NSUTF8StringEncoding error:nil];return [NSURL fileURLWithPath:p];}
static VLCThumbnailService *Service(NSString *name){return [[VLCThumbnailService alloc] initWithHelperPath:[repo stringByAppendingPathComponent:@"tests/story-004/fake-worker.py"] cacheRoot:[root stringByAppendingPathComponent:name]];}
static NSDictionary *Request(VLCThumbnailService *s,NSURL *url,NSString *gen,int64_t time){
 __block NSDictionary *reply=nil;double start=Now();
 [s requestURL:url generation:gen videoOrdinal:0 videoCount:1 time:time completion:^(NSImage *image,NSDictionary *r){if(![r[@"preparing"] boolValue]&&![r[@"verification_pending"] boolValue]){NSMutableDictionary *v=[r mutableCopy];v[@"has_image"]=@(image!=nil);v[@"measured_ms"]=@((Now()-start)*1000);reply=v;}}];
 while(!reply&&Now()-start<20)Spin(.001);return reply?:@{@"error":@"test-timeout"};
}
int main(int argc,const char **argv){@autoreleasepool{
 if(argc!=2)return 2;repo=@(argv[1]);[NSApplication sharedApplication];checks=[NSMutableArray array];
 root=[repo stringByAppendingPathComponent:[@"work/validation/story004/service-contract-" stringByAppendingString:NSUUID.UUID.UUIDString]];
 [NSFileManager.defaultManager createDirectoryAtPath:root withIntermediateDirectories:YES attributes:nil error:nil];
 Check(@"shared bridge policy follows coarse plan and bounds",VLCThumbnailBridgeDistance(90000000)==5625000&&VLCThumbnailBridgeDistance(0)==2000000&&VLCThumbnailBridgeDistance(86400000000LL)==60000000,@{});
 NSURL *valid=Input(@"valid.txt",@"valid");
 VLCThumbnailService *missing=[[VLCThumbnailService alloc] initWithHelperPath:[root stringByAppendingPathComponent:@"absent-helper"] cacheRoot:[root stringByAppendingPathComponent:@"missing-cache"]];
 NSDictionary *missingReply=Request(missing,valid,@"missing",0);Check(@"missing helper cannot throw or stall",[missingReply[@"error"] isEqual:@"helper-unavailable"],missingReply);[missing shutdown];
 VLCThumbnailService *s=Service(@"reuse");
 NSDictionary *first=Request(s,valid,@"one",1000000),*second=Request(s,valid,@"one",5000000);Check(@"worker reused across uncached targets",[first[@"has_image"] boolValue]&&[second[@"has_image"] boolValue]&&[s.metrics[@"launched"] intValue]==1,s.metrics);[s shutdown];Spin(.02);
 s=Service(@"reuse");NSDictionary *restart=Request(s,valid,@"two",1000000);Check(@"new presentation generation retains verified disk sample",[restart[@"has_image"] boolValue]&&[restart[@"cache"] isEqual:@"disk"]&&[s.metrics[@"launched"] intValue]==0,restart);NSString *qualifiedIdentity=[[s valueForKey:@"verifiedIdentity"] copy];[s shutdown];
 // Seed a valid payload under the formerly accepted mapping policy. A fresh
 // service must decode under the corrected policy instead of serving it.
 NSString *legacyIdentity=[qualifiedIdentity stringByReplacingOccurrencesOfString:@"keyframe-countguard2" withString:@"keyframe-tracknumber"];
 NSString *reuseRoot=[root stringByAppendingPathComponent:@"reuse"];
 NSData *legacyRaw=nil;
 for(NSString *name in [NSFileManager.defaultManager contentsOfDirectoryAtPath:reuseRoot error:nil])
   if([name.pathExtension isEqual:@"rgba"]){legacyRaw=[NSData dataWithContentsOfFile:[reuseRoot stringByAppendingPathComponent:name]];break;}
 NSString *legacyRoot=[root stringByAppendingPathComponent:@"legacy-mapping"];
 VLCThumbnailCache *legacyCache=[[VLCThumbnailCache alloc] initWithRoot:legacyRoot];
 [legacyCache selectIdentity:legacyIdentity];
 NSUInteger headerLength=0;const uint8_t *legacyBytes=legacyRaw.bytes;
 while(headerLength<legacyRaw.length&&legacyBytes[headerLength]!='\n')headerLength++;
 NSDictionary *legacyHeader=[NSJSONSerialization JSONObjectWithData:[legacyRaw subdataWithRange:NSMakeRange(0,headerLength)] options:0 error:nil];
 BOOL seeded=[legacyCache storeRaw:legacyRaw requestedTime:1000000 actualTime:[legacyHeader[@"actual_us"] longLongValue]];
 s=Service(@"legacy-mapping");NSDictionary *corrected=Request(s,valid,@"corrected-policy",1000000);
 Check(@"old track mapping cache policy cannot bypass corrected decoder",seeded&&![legacyIdentity isEqual:qualifiedIdentity]&&[corrected[@"has_image"] boolValue]&&[s.metrics[@"launched"] intValue]==1,@{@"result":corrected,@"metrics":s.metrics});[s shutdown];
 s=Service(@"cache-bypass");NSURL *cacheSlow=Input(@"cache-slow.txt",@"cache-slow");
 NSDictionary *seed=Request(s,cacheSlow,@"cache-bypass",2000000);
 __block BOOL oldFinal=NO;
 [s requestURL:cacheSlow generation:@"cache-bypass" videoOrdinal:0 videoCount:1 time:8000000 completion:^(NSImage *image,NSDictionary *r){(void)image;if(![r[@"preparing"] boolValue]&&![r[@"verification_pending"] boolValue])oldFinal=YES;}];
 double activeDeadline=Now()+2;while([s.metrics[@"worker_requests"] intValue]<2&&Now()<activeDeadline)Spin(.001);NSDictionary *bypass=Request(s,cacheSlow,@"cache-bypass",2000000);
 Check(@"cached hover bypasses active extraction",[seed[@"has_image"] boolValue]&&[bypass[@"has_image"] boolValue]&&[bypass[@"cache"] isEqual:@"memory"]&&[s.metrics[@"active"] boolValue]&&!oldFinal,@{@"result":bypass,@"metrics":s.metrics});
 double finishedDeadline=Now()+2;while([s.metrics[@"active"] boolValue]&&Now()<finishedDeadline)Spin(.001);Check(@"bypassed active extraction finishes without an extra decode",[s.metrics[@"worker_requests"] intValue]==2,s.metrics);[s shutdown];
 s=Service(@"cached-mutation");NSURL *cachedMutation=Input(@"cached-mutation.txt",@"cache-slow");
 Request(s,cachedMutation,@"cached-mutation",2000000);
 [s requestURL:cachedMutation generation:@"cached-mutation" videoOrdinal:0 videoCount:1 time:8000000 completion:^(NSImage *image,NSDictionary *r){(void)image;(void)r;}];
 double mutationActiveDeadline=Now()+2;while([s.metrics[@"worker_requests"] intValue]<2&&Now()<mutationActiveDeadline)Spin(.001);
 __block BOOL cachedShown=NO,invalidatedCurrent=NO;
 [s requestURL:cachedMutation generation:@"cached-mutation" videoOrdinal:0 videoCount:1 time:2000000 completion:^(NSImage *image,NSDictionary *r){if(image)cachedShown=YES;if([r[@"error"] isEqual:@"media_changed"]&&!image)invalidatedCurrent=YES;}];
 double cachedDeadline=Now()+2;while(!cachedShown&&Now()<cachedDeadline)Spin(.001);
 [@"valid" writeToFile:cachedMutation.path atomically:YES encoding:NSUTF8StringEncoding error:nil];
 double invalidationDeadline=Now()+2;while(!invalidatedCurrent&&Now()<invalidationDeadline)Spin(.001);
 Check(@"obsolete extraction invalidates currently displayed cached hover",cachedShown&&invalidatedCurrent,s.metrics);[s shutdown];
 s=Service(@"metadata-single-owner");NSURL *metadataSlow=Input(@"metadata-slow.txt",@"metadata-slow");
 Request(s,metadataSlow,@"metadata",2000000);
 NSString *statLog=[metadataSlow.path stringByAppendingString:@".statcalls"];
 NSUInteger beforeStats=[[NSString stringWithContentsOfFile:statLog encoding:NSUTF8StringEncoding error:nil] componentsSeparatedByString:@"stat\n"].count-1;
 NSUInteger beforeDecodes=[s.metrics[@"worker_requests"] unsignedIntegerValue];
 __block NSUInteger cacheFinals=0,cacheProvisionals=0;__block BOOL cacheImage=NO;double cachedBegin=Now();__block double firstCachedProvisional=0;
 [s requestURL:metadataSlow generation:@"metadata" videoOrdinal:0 videoCount:1 time:2000000 completion:^(NSImage *image,NSDictionary *r){if(image&&[r[@"verification_pending"] boolValue]){cacheProvisionals++;if(!firstCachedProvisional)firstCachedProvisional=Now()-cachedBegin;}if(![r[@"preparing"] boolValue]&&![r[@"verification_pending"] boolValue]){cacheFinals++;cacheImage=image!=nil;}}];
 Spin(.8);
 NSUInteger afterStats=[[NSString stringWithContentsOfFile:statLog encoding:NSUTF8StringEncoding error:nil] componentsSeparatedByString:@"stat\n"].count-1;
 Check(@"cached provisional precedes one final owner and one metadata validation",cacheProvisionals==1&&firstCachedProvisional>0&&firstCachedProvisional<.2&&cacheFinals==1&&cacheImage&&afterStats-beforeStats==1&&[s.metrics[@"worker_requests"] unsignedIntegerValue]==beforeDecodes,@{@"finals":@(cacheFinals),@"metadata_calls":@(afterStats-beforeStats),@"metrics":s.metrics});
 __block BOOL replacementProvisional=NO,replacementValidated=NO,replacementRejected=NO;
 [s requestURL:metadataSlow generation:@"metadata" videoOrdinal:0 videoCount:1 time:2000000 completion:^(NSImage *image,NSDictionary *r){if(image&&[r[@"verification_pending"] boolValue])replacementProvisional=YES;
 if(image&&![r[@"verification_pending"] boolValue]&&![r[@"preparing"] boolValue])replacementValidated=YES;
 if([r[@"error"] isEqual:@"media_changed"])replacementRejected=YES;}];
 dispatch_after(dispatch_time(DISPATCH_TIME_NOW,100*NSEC_PER_MSEC),dispatch_get_main_queue(),^{[@"valid" writeToFile:metadataSlow.path atomically:YES encoding:NSUTF8StringEncoding error:nil];});
 Spin(.8);
 Check(@"replacement during cached validation clears provisional without a stale validated hit",replacementProvisional&&!replacementValidated&&replacementRejected,s.metrics);[s shutdown];
 s=Service(@"blocked-validation-latest");NSURL *queuedMetadata=Input(@"queued-metadata.txt",@"metadata-slow");
 Request(s,queuedMetadata,@"queued",2000000);Request(s,queuedMetadata,@"queued",6000000);
 NSString *delayPath=[queuedMetadata.path stringByAppendingString:@".metadata-delay"];
 [@"1" writeToFile:delayPath atomically:YES encoding:NSUTF8StringEncoding error:nil];
 __block NSUInteger oldValidationFinals=0,newValidationFinals=0;__block BOOL newestProvisional=NO;
 [s requestURL:queuedMetadata generation:@"queued" videoOrdinal:0 videoCount:1 time:2000000 completion:^(NSImage *image,NSDictionary *r){(void)image;if(![r[@"preparing"] boolValue]&&![r[@"verification_pending"] boolValue])oldValidationFinals++;}];Spin(.08);
 double newestBegin=Now();__block double newestProvisionalTime=0;
 [s requestURL:queuedMetadata generation:@"queued" videoOrdinal:0 videoCount:1 time:6000000 completion:^(NSImage *image,NSDictionary *r){if(image&&[r[@"verification_pending"] boolValue]){newestProvisional=YES;newestProvisionalTime=Now()-newestBegin;}if(![r[@"preparing"] boolValue]&&![r[@"verification_pending"] boolValue])newValidationFinals++;}];
 Spin(.2);Check(@"latest RAM provisional bypasses blocked older source validation",newestProvisional&&newestProvisionalTime<.2&&oldValidationFinals==0&&newValidationFinals==0,@{@"provisional_s":@(newestProvisionalTime),@"metrics":s.metrics});
 Spin(2.1);Check(@"superseded validation cannot replace latest hover",oldValidationFinals==0&&newValidationFinals==1&&[s.metrics[@"worker_requests"] unsignedIntegerValue]==2,s.metrics);[s shutdown];
 s=Service(@"cancel-validation");NSURL *cancelMetadata=Input(@"cancel-metadata.txt",@"metadata-slow");Request(s,cancelMetadata,@"cancel-validation",2000000);
 [@"1" writeToFile:[cancelMetadata.path stringByAppendingString:@".metadata-delay"] atomically:YES encoding:NSUTF8StringEncoding error:nil];
 __block NSUInteger cancelProvisional=0,cancelFinal=0;
 NSUInteger cancelToken=[s requestURL:cancelMetadata generation:@"cancel-validation" videoOrdinal:0 videoCount:1 time:2000000 completion:^(NSImage *image,NSDictionary *r){if(image&&[r[@"verification_pending"] boolValue])cancelProvisional++;if(![r[@"verification_pending"] boolValue])cancelFinal++;}];Spin(.1);[s cancelRequest:cancelToken];Spin(1.2);
 Check(@"leaving during cached source check suppresses late presentation",cancelProvisional==1&&cancelFinal==0,s.metrics);[s shutdown];
 s=Service(@"cancel-validation");__block BOOL reopenProvisional=NO,reopenFinal=NO;
 [s requestURL:cancelMetadata generation:@"reopened" videoOrdinal:0 videoCount:1 time:2000000 completion:^(NSImage *image,NSDictionary *r){if(image&&[r[@"verification_pending"] boolValue])reopenProvisional=YES;if(image&&![r[@"preparing"] boolValue]&&![r[@"verification_pending"] boolValue])reopenFinal=YES;}];
 Spin(.15);Check(@"fresh reopen cannot provisionally reuse prior-session cache",!reopenProvisional&&!reopenFinal,s.metrics);Spin(3.2);
 Check(@"fresh reopen returns disk image only after qualified identity",!reopenProvisional&&reopenFinal&&[s.metrics[@"launched"] intValue]==0,s.metrics);[s shutdown];
 s=Service(@"provisional-deadline");NSURL *deadlineMetadata=Input(@"deadline-metadata.txt",@"metadata-slow");Request(s,deadlineMetadata,@"deadline",2000000);
 NSString *deadlineDelay=[deadlineMetadata.path stringByAppendingString:@".metadata-delay"];
 [@"17" writeToFile:deadlineDelay atomically:YES encoding:NSUTF8StringEncoding error:nil];
 __block BOOL earlyDeadlineImage=NO,deadlineCleared=NO;double deadlineBegin=Now();__block double clearedAfter=0;
 VLCThumbnailCompletion deadlineCallback=^(NSImage *image,NSDictionary *r){if(image&&[r[@"verification_pending"] boolValue])earlyDeadlineImage=YES;if(!image&&r[@"error"]){deadlineCleared=YES;clearedAfter=Now()-deadlineBegin;}};
 [s requestURL:deadlineMetadata generation:@"deadline" videoOrdinal:0 videoCount:1 time:2000000 completion:deadlineCallback];
 VLCThumbnailService *deadlineService=s;
 dispatch_after(dispatch_time(DISPATCH_TIME_NOW,12*NSEC_PER_SEC),dispatch_get_main_queue(),^{[deadlineService requestURL:deadlineMetadata generation:@"deadline" videoOrdinal:0 videoCount:1 time:2000000 completion:deadlineCallback];});
 Spin(16.5);Check(@"pointer movement cannot renew provisional source-check lifetime",earlyDeadlineImage&&deadlineCleared&&clearedAfter<=16.1,@{@"cleared_after_s":@(clearedAfter),@"metrics":s.metrics});
 __block BOOL redisplayedFailure=NO;
 [s requestURL:deadlineMetadata generation:@"deadline" videoOrdinal:0 videoCount:1 time:2000000 completion:^(NSImage *image,NSDictionary *r){if(image&&[r[@"verification_pending"] boolValue])redisplayedFailure=YES;}];Spin(.15);
 Check(@"known source failure suppresses provisional redisplay",!redisplayedFailure,s.metrics);[s shutdown];
 s=Service(@"actual-key");NSDictionary *alias=Request(s,valid,@"actual-key",3000000);NSDictionary *actual=Request(s,valid,@"actual-key",2000000);
 Check(@"actual timestamp cache hit needs no requested alias",[alias[@"has_image"] boolValue]&&[actual[@"cache"] isEqual:@"memory"]&&[s.metrics[@"worker_requests"] intValue]==1,actual);[s shutdown];
 s=Service(@"actual-key");actual=Request(s,valid,@"actual-key-reopen",2000000);Check(@"actual timestamp disk reuse after reopen",[actual[@"cache"] isEqual:@"disk"]&&[s.metrics[@"launched"] intValue]==0,actual);[s shutdown];
 s=Service(@"burst");NSURL *slow=Input(@"slow.txt",@"slow");__block NSUInteger finals=0,bridges=0;__block int64_t delivered=-1;
 VLCThumbnailCompletion callback=^(NSImage *image,NSDictionary *r){(void)image;if([r[@"preparing"] boolValue])bridges++;else{finals++;delivered=[r[@"requested_us"] longLongValue];}};
 [s requestURL:slow generation:@"burst" videoOrdinal:0 videoCount:1 time:0 completion:callback];Spin(.08);
 NSUInteger stale=0,latest=0;for(int i=1;i<=100;i++){NSUInteger token=[s requestURL:slow generation:@"burst" videoOrdinal:0 videoCount:1 time:i*1000 completion:callback];if(i==1)stale=token;latest=token;}
 [s cancelRequest:stale];double end=Now()+3;while(!finals&&Now()<end)Spin(.001);
 Check(@"active extraction finishes and latest bounded hover wins",finals==1&&delivered==100000&&[s.metrics[@"launched"] intValue]==1&&[s.metrics[@"worker_requests"] intValue]==2,@{@"finals":@(finals),@"bridges":@(bridges),@"metrics":s.metrics});
 finals=0;[s requestURL:slow generation:@"burst" videoOrdinal:0 videoCount:1 time:6000000 completion:callback];Spin(.05);[s cancelRequest:latest+1];Spin(.35);Check(@"presentation exit keeps useful active extraction",finals==0&&[s.metrics[@"launched"] intValue]==1,s.metrics);
 NSDictionary *afterExit=Request(s,slow,@"burst",6000000);Check(@"exit result is cached for subsequent hover",[afterExit[@"cache"] isEqual:@"memory"],afterExit);[s shutdown];
 for(NSString *mode in @[@"malformed",@"startup-malformed",@"crash",@"fractional",@"unsupported",@"fail-once"]){s=Service(mode);NSDictionary *r=Request(s,Input([mode stringByAppendingString:@".txt"],mode),mode,0);BOOL expected=[mode isEqual:@"fail-once"]?[r[@"has_image"] boolValue]:![r[@"has_image"] boolValue]&&r[@"error"]&&![r[@"error"] isEqual:@"test-timeout"];Check([@"fault and finite retry " stringByAppendingString:mode],expected,r);NSDictionary *recovered=Request(s,valid,@"recovery",0);Check([@"recover context after " stringByAppendingString:mode],[recovered[@"has_image"] boolValue],recovered);[s shutdown];}
 for(NSString *mode in @[@"hang",@"startup-hang"]) {
   s=Service([@"cancel-" stringByAppendingString:mode]);__block BOOL staleFinal=NO;
   [s requestURL:Input([mode stringByAppendingString:@".txt"],mode) generation:mode videoOrdinal:0 videoCount:1 time:0 completion:^(NSImage *image,NSDictionary *r){(void)image;if(![r[@"preparing"] boolValue]&&![r[@"verification_pending"] boolValue])staleFinal=YES;}];
   double launchedDeadline=Now()+3;while([s.metrics[@"launched"] intValue]<1&&Now()<launchedDeadline)Spin(.001);
   NSDictionary *recovered=Request(s,valid,@"cancel-recovery",0);
   Check([@"context change terminates obsolete " stringByAppendingString:mode],[recovered[@"has_image"] boolValue]&&!staleFinal,recovered);[s shutdown];
 }
 s=Service(@"mutation");NSURL *changing=Input(@"changing.txt",@"mutating");dispatch_after(dispatch_time(DISPATCH_TIME_NOW,100*NSEC_PER_MSEC),dispatch_get_main_queue(),^{[@"valid" writeToFile:changing.path atomically:YES encoding:NSUTF8StringEncoding error:nil];});NSDictionary *changed=Request(s,changing,@"mutation",1000000);Check(@"file mutation does not present stale pixels",![changed[@"has_image"] boolValue],changed);[s shutdown];
 // Proactive work needs no hover; a short finite plan completes under available resources.
 s=Service(@"background");[s prepareContext:@{@"url":valid,@"generation":@"background",@"videoOrdinal":@0,@"videoCount":@1,@"duration":@8000000,@"eligible":@YES} enabled:YES];Spin(2.5);Check(@"finite proactive coverage without hover",[s.metrics[@"completed"] intValue]>=7&&[s.metrics[@"launched"] intValue]==1,s.metrics);
 // A stream of already cached hovers must not reserve the extraction slot.
 NSUInteger completedBeforeSweep=[s.metrics[@"completed"] unsignedIntegerValue];
 [s prepareContext:@{@"url":valid,@"generation":@"cached-sweep",@"videoOrdinal":@0,@"videoCount":@1,@"duration":@90000000,@"eligible":@YES} enabled:YES];
 Request(s,valid,@"cached-sweep",0);
 double sweepEnd=Now()+2.5;while(Now()<sweepEnd){[s requestURL:valid generation:@"cached-sweep" videoOrdinal:0 videoCount:1 time:0 completion:^(NSImage *image,NSDictionary *r){(void)image;(void)r;}];Spin(.04);}
 Check(@"sustained cached hover leaves turns for global preparation",[s.metrics[@"completed"] unsignedIntegerValue]>completedBeforeSweep+2,s.metrics);
 [s prepareContext:@{} enabled:NO];Spin(.05);NSUInteger before=[s.metrics[@"worker_requests"] unsignedIntegerValue];Spin(.5);Check(@"disable stops background extraction",[s.metrics[@"worker_requests"] unsignedIntegerValue]==before&&![s.metrics[@"worker_ready"] boolValue],s.metrics);[s shutdown];
 NSData *json=[NSJSONSerialization dataWithJSONObject:@{@"passed":@(failed==0),@"checks":checks} options:NSJSONWritingPrettyPrinted error:nil];[json writeToFile:[repo stringByAppendingPathComponent:@"work/validation/story004/service-contract.json"] atomically:YES];[NSFileManager.defaultManager removeItemAtPath:root error:nil];printf("Service contracts %lu checks, %lu failures\n",checks.count,failed);return failed?1:0;
}}
