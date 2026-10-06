// SPDX-License-Identifier: GPL-2.0-or-later
// Native main-runloop service contracts; this does not exercise mouse/UI presentation.
#import <Cocoa/Cocoa.h>
#import "VLCThumbnailService.h"
#import "VLCTimelineGeometry.h"
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>

static NSMutableArray *checks;
static NSString *base, *repo;
static NSUInteger failures;
static double Now(void) { return NSProcessInfo.processInfo.systemUptime; }
static void Check(NSString *name, BOOL passed, NSDictionary *detail) {
    [checks addObject:@{@"name":name,@"passed":@(passed),@"detail":detail ?: @{}}];
    if (!passed) { failures++; fprintf(stderr,"FAIL: %s\n",name.UTF8String); }
}
static void Spin(double seconds) {
    double end=Now()+seconds;
    do { [NSRunLoop.mainRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:.001]]; } while(Now()<end);
}
static BOOL Idle(VLCThumbnailService *s, double seconds) {
    double end=Now()+seconds;
    while ([s.metrics[@"active"] boolValue] && Now()<end) Spin(.001);
    return ![s.metrics[@"active"] boolValue];
}
static NSDictionary *RequestCount(VLCThumbnailService *s, NSURL *url, NSString *generation, int64_t time, NSUInteger count) {
    __block NSDictionary *reply=nil; double start=Now();
    [s requestURL:url generation:generation videoOrdinal:0 videoCount:count time:time completion:^(NSImage *image, NSDictionary *r) {
        NSMutableDictionary *copy=[r mutableCopy]; copy[@"has_image"]=@(image!=nil);
        copy[@"measured_ms"]=@((Now()-start)*1000); reply=copy;
    }];
    while(!reply && Now()-start<7) Spin(.001);
    return reply ?: @{@"error":@"test-timeout",@"has_image":@NO};
}
static NSDictionary *Request(VLCThumbnailService *s, NSURL *url, NSString *generation, int64_t time) {
    return RequestCount(s,url,generation,time,1);
}
static NSString *Root(NSString *name) { return [base stringByAppendingPathComponent:name]; }
static NSString *FakeInput(NSString *name, NSString *mode) {
    NSString *p=Root(name); [mode writeToFile:p atomically:YES encoding:NSUTF8StringEncoding error:nil]; return p;
}
static VLCThumbnailService *Service(NSString *helper, NSString *root) {
    return [[VLCThumbnailService alloc] initWithHelperPath:helper cacheRoot:root];
}
static NSArray *Files(NSString *root) { return [NSFileManager.defaultManager contentsOfDirectoryAtPath:root error:nil] ?: @[]; }
static NSDictionary *Stats(NSArray *values) {
    NSArray *sorted=[values sortedArrayUsingSelector:@selector(compare:)];
    return @{@"samples":@(values.count),@"p95_ms":sorted[(NSUInteger)ceil(values.count*.95)-1],@"max_ms":sorted.lastObject};
}
static void Sparse(NSString *path, off_t bytes) {
    int fd=open(path.fileSystemRepresentation,O_WRONLY|O_CREAT|O_TRUNC,0600);
    if(fd>=0) { ftruncate(fd,bytes); close(fd); }
}
int main(int argc, const char **argv) { @autoreleasepool {
    if(argc!=2) return 2;
    [NSApplication sharedApplication];
    repo=@(argv[1]); checks=[NSMutableArray array];
    base=[repo stringByAppendingPathComponent:[@"work/validation/story002/service-stores-" stringByAppendingString:NSUUID.UUID.UUIDString]];
    [NSFileManager.defaultManager createDirectoryAtPath:base withIntermediateDirectories:YES attributes:nil error:nil];
    NSString *helper=[repo stringByAppendingPathComponent:@"work/build/thumbnail-helper/thumbnail-helper"];
    NSString *fake=[repo stringByAppendingPathComponent:@"tests/story-002/fake-helper.py"];
    NSString *fixture=NSProcessInfo.processInfo.environment[@"VLC_TEST_FIXTURE"] ?: @"standard.mp4";
    if (![fixture isEqual:@"standard.mp4"] && ![fixture isEqual:@"standard.mkv"]) return 2;
    NSURL *media=[NSURL fileURLWithPath:[[repo stringByAppendingPathComponent:@"work/fixtures/story-002"] stringByAppendingPathComponent:fixture]];
    Check(@"geometry clamped endpoints",VLCTimelineTimeForPoint(-5,10,110,1000000)==0 && VLCTimelineTimeForPoint(200,10,110,1000000)==999999,nil);
    Check(@"geometry midpoint and invalid inputs",VLCTimelineTimeForPoint(60,10,110,1000001)==500000 && VLCTimelineTimeForPoint(NAN,10,110,1)==-1 && VLCTimelineTimeForPoint(10,10,10,1)==-1 && VLCTimelineTimeForPoint(10,10,20,0)==-1,nil);
    Check(@"bucket quantization and EOF",VLCTimelineBucket(251000,1000000)==500000 && VLCTimelineBucket(999999,1000000)==999999 && VLCTimelineBucket(-1,10)==-1,nil);
    VLCThumbnailService *s;
    BOOL skipLatency=[NSProcessInfo.processInfo.environment[@"VLC_TEST_SKIP_LATENCY"] boolValue];
    if (!skipLatency) {
    s=Service(helper,Root(@"latency"));
    NSMutableArray *miss=[NSMutableArray array],*ram=[NSMutableArray array],*disk=[NSMutableArray array];
    BOOL all=YES;
    for(int i=0;i<100;i++) {
        NSDictionary *r=Request(s,media,@"latency",500000+((i*37)%100)*500000LL);
        all &= [r[@"has_image"] boolValue] && [r[@"cache"] isEqual:@"miss"];
        [miss addObject:r[@"measured_ms"] ?: @7000];
    }
    for(int i=0;i<100;i++) {
        NSDictionary *r=Request(s,media,@"latency",500000+((i*37)%100)*500000LL);
        all &= [r[@"has_image"] boolValue] && [r[@"cache"] isEqual:@"memory"];
        [ram addObject:r[@"measured_ms"] ?: @7000];
    }
    [s shutdown]; Idle(s,2); s=Service(helper,Root(@"latency"));
    for(int i=0;i<100;i++) {
        NSDictionary *r=Request(s,media,@"latency",500000+((i*37)%100)*500000LL);
        all &= [r[@"has_image"] boolValue] && [r[@"cache"] isEqual:@"disk"];
        [disk addObject:r[@"measured_ms"] ?: @7000];
    }
    Check(@"100 settled requests per cache condition",all,@{@"miss":Stats(miss),@"memory":Stats(ram),@"disk":Stats(disk)});
    Check(@"service latency thresholds",[Stats(miss)[@"p95_ms"] doubleValue]<=1000 && [Stats(ram)[@"p95_ms"] doubleValue]<=100 && [Stats(disk)[@"p95_ms"] doubleValue]<=150,nil);
    NSDictionary *gen=Request(s,media,@"new-open",500000);
    Check(@"new media generation cannot reuse earlier cache",[gen[@"cache"] isEqual:@"miss"],gen); [s shutdown];
    }

    NSURL *tracks=[NSURL fileURLWithPath:[repo stringByAppendingPathComponent:@"work/fixtures/story-002/two-tracks.mkv"]];
    s=Service(helper,Root(@"track-count"));
    NSDictionary *mapped=RequestCount(s,tracks,@"same-track-open",4000000,2);
    NSDictionary *wrongCount=RequestCount(s,tracks,@"same-track-open",4000000,1);
    NSDictionary *mappedAgain=RequestCount(s,tracks,@"same-track-open",4000000,2);
    Check(@"native track count reaches helper mapping",[mapped[@"has_image"] boolValue] && [mapped[@"video_track_number"] integerValue]==1,mapped);
    Check(@"track count mismatch cannot reuse valid cached pixels",![wrongCount[@"has_image"] boolValue] && wrongCount[@"error"] && [mappedAgain[@"has_image"] boolValue] && [mappedAgain[@"cache"] isEqual:@"memory"],@{@"mismatch":wrongCount,@"recovered":mappedAgain});
    [s shutdown];

    NSURL *valid=[NSURL fileURLWithPath:FakeInput(@"valid.txt",@"valid")];
    s=Service(fake,Root(@"invalidate")); Request(s,valid,@"same",0);
    [@"valid\n" writeToFile:valid.path atomically:YES encoding:NSUTF8StringEncoding error:nil];
    NSDictionary *changed=Request(s,valid,@"same",0);
    Check(@"file stat identity change invalidates cache",[changed[@"cache"] isEqual:@"miss"],changed); [s shutdown];

    for(NSString *mode in @[@"malformed",@"oversized",@"crash",@"hang"]) {
        s=Service(fake,Root(mode)); NSDictionary *r=Request(s,[NSURL fileURLWithPath:FakeInput([mode stringByAppendingString:@".txt"],mode)],@"fault",0);
        Check([@"fault " stringByAppendingString:mode],![r[@"has_image"] boolValue] && r[@"error"] && ![r[@"error"] isEqual:@"test-timeout"] && [r[@"measured_ms"] doubleValue]<6500,r);
        NSDictionary *recovered=Request(s,valid,@"after-fault",0);
        Check([@"recovery after " stringByAppendingString:mode],[recovered[@"has_image"] boolValue],recovered); [s shutdown];
    }
    s=Service(Root(@"missing-helper"),Root(@"unavailable"));
    NSDictionary *unavailable=Request(s,valid,@"fault",0);
    Check(@"missing helper",[unavailable[@"error"] isEqual:@"helper-unavailable"],unavailable); [s shutdown];

    s=Service(fake,Root(@"network"));
    NSDictionary *network=Request(s,[NSURL URLWithString:@"https://example.invalid/private.mp4"],@"network",0);
    Check(@"nonlocal media never launches helper",![network[@"has_image"] boolValue] && [s.metrics[@"launched"] unsignedIntegerValue]==0,network);
    [s shutdown]; NSDictionary *stopped=Request(s,valid,@"stopped",0);
    Check(@"shutdown rejects new demand",[stopped[@"error"] isEqual:@"shutdown"],stopped);
    s=Service(fake,Root(@"middecode"));
    NSURL *changing=[NSURL fileURLWithPath:FakeInput(@"changing.txt",@"slow")];
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW,100*NSEC_PER_MSEC),dispatch_get_main_queue(), ^{
        [@"valid" writeToFile:changing.path atomically:YES encoding:NSUTF8StringEncoding error:nil];
    });
    NSDictionary *during=Request(s,changing,@"changing",0);
    Check(@"file changed during decode cannot be cached or delivered",![during[@"has_image"] boolValue] && [during[@"error"] isEqual:@"changed-or-cancelled"] && Files(Root(@"middecode")).count==0,during); [s shutdown];

    s=Service(fake,Root(@"burst")); NSURL *slow=[NSURL fileURLWithPath:FakeInput(@"slow.txt",@"slow")];
    __block NSUInteger deliveries=0; __block int64_t delivered=-1;
    VLCThumbnailCompletion callback=^(NSImage *image,NSDictionary *r){deliveries++; if(image) delivered=[r[@"requested_us"] longLongValue];};
    [s requestURL:slow generation:@"burst" videoOrdinal:0 videoCount:1 time:0 completion:callback]; Spin(.1);
    NSUInteger first=0,last=0,maxActive=0,maxPending=0;
    for(int i=1;i<=100;i++) {
        NSUInteger token=[s requestURL:slow generation:@"burst" videoOrdinal:0 videoCount:1 time:i*1000 completion:callback];
        if(i==1) first=token; last=token;
        maxActive=MAX(maxActive,[s.metrics[@"active"] unsignedIntegerValue]); maxPending=MAX(maxPending,[s.metrics[@"pending"] unsignedIntegerValue]);
    }
    [s cancelRequest:first];
    BOOL idle=Idle(s,3);
    Check(@"burst latest delivery with stale-token cancellation",idle && deliveries==1 && delivered==100000 && maxActive<=1 && maxPending<=1,@{@"deliveries":@(deliveries),@"delivered_us":@(delivered),@"max_active":@(maxActive),@"max_pending":@(maxPending),@"metrics":s.metrics,@"last_token":@(last)});
    deliveries=0; NSUInteger cancel=[s requestURL:slow generation:@"cancel" videoOrdinal:0 videoCount:1 time:0 completion:callback]; Spin(.08); [s cancelRequest:cancel];
    idle=Idle(s,2); Check(@"active cancellation delivers no stale completion",idle && deliveries==0,s.metrics); [s shutdown];

    NSString *escape=Root(@"outside"),*link=Root(@"symlink-root");
    [NSFileManager.defaultManager createDirectoryAtPath:escape withIntermediateDirectories:YES attributes:nil error:nil];
    symlink(escape.fileSystemRepresentation,link.fileSystemRepresentation);
    s=Service(fake,escape); Request(s,valid,@"symlink",0); [s shutdown];
    NSUInteger outsideBefore=Files(escape).count;
    s=Service(fake,link); NSDictionary *safe=Request(s,valid,@"symlink",0);
    Check(@"symlink cache root neither reads nor writes through",[safe[@"has_image"] boolValue] && [safe[@"cache"] isEqual:@"miss"] && [s.metrics[@"launched"] unsignedIntegerValue]==1 && Files(escape).count==outsideBefore,safe); [s shutdown];
    NSString *denied=FakeInput(@"cache-root-is-file",@"owner sentinel");
    s=Service(fake,denied); NSDictionary *withoutCache=Request(s,valid,@"denied",0);
    NSDictionary *nextWithoutCache=Request(s,valid,@"denied",1000);
    Check(@"cache IO refusal preserves valid preview and subsequent demand",[withoutCache[@"has_image"] boolValue] && [nextWithoutCache[@"has_image"] boolValue] && [[NSString stringWithContentsOfFile:denied encoding:NSUTF8StringEncoding error:nil] isEqual:@"owner sentinel"],@{@"first":withoutCache,@"next":nextWithoutCache}); [s shutdown];
    NSString *corrupt=Root(@"corrupt-cache"); s=Service(fake,corrupt); Request(s,valid,@"corrupt",0); [s shutdown];
    NSString *entry=[corrupt stringByAppendingPathComponent:Files(corrupt).firstObject];
    [@"{\"version\":2,\"ok\":false}\n" writeToFile:entry atomically:YES encoding:NSUTF8StringEncoding error:nil];
    s=Service(fake,corrupt); NSDictionary *repair=Request(s,valid,@"corrupt",0); [s shutdown];
    s=Service(fake,corrupt); NSDictionary *repaired=Request(s,valid,@"corrupt",0);
    Check(@"corrupt disk cache repaired and reusable",[repair[@"cache"] isEqual:@"miss"] && [repaired[@"cache"] isEqual:@"disk"] && [repaired[@"has_image"] boolValue],@{@"repair":repair,@"reopened":repaired}); [s shutdown];

    NSString *quota=Root(@"quota"); [NSFileManager.defaultManager createDirectoryAtPath:quota withIntermediateDirectories:YES attributes:nil error:nil];
    for(int i=0;i<3;i++) Sparse([quota stringByAppendingPathComponent:[NSString stringWithFormat:@"%064x.rgba",i]],100*1024*1024);
    NSString *unrelated=[quota stringByAppendingPathComponent:@"owner-notes.txt"]; Sparse(unrelated,1);
    NSString *nonhex=[quota stringByAppendingPathComponent:[[@"z" stringByPaddingToLength:64 withString:@"z" startingAtIndex:0] stringByAppendingString:@".rgba"]]; Sparse(nonhex,100*1024*1024);
    [NSFileManager.defaultManager setAttributes:@{NSFileModificationDate:[NSDate dateWithTimeIntervalSince1970:1]} ofItemAtPath:nonhex error:nil];
    NSString *linked=[quota stringByAppendingPathComponent:[NSString stringWithFormat:@"%064x.rgba",99]]; symlink(unrelated.fileSystemRepresentation,linked.fileSystemRepresentation);
    s=Service(fake,quota); Request(s,valid,@"quota",0);
    unsigned long long ownedBytes=0; for(NSString *name in Files(quota)) {
        if(name.length!=69 || ![name hasSuffix:@".rgba"] || [name rangeOfCharacterFromSet:[[NSCharacterSet characterSetWithCharactersInString:@"0123456789abcdef"] invertedSet] options:0 range:NSMakeRange(0,64)].location!=NSNotFound) continue;
        struct stat st; NSString *p=[quota stringByAppendingPathComponent:name]; if(!lstat(p.fileSystemRepresentation,&st) && S_ISREG(st.st_mode)) ownedBytes+=st.st_size;
    }
    Check(@"disk quota and cleanup ownership",ownedBytes<=256*1024*1024 && [NSFileManager.defaultManager fileExistsAtPath:unrelated] && [NSFileManager.defaultManager fileExistsAtPath:nonhex] && [NSFileManager.defaultManager fileExistsAtPath:linked],@{@"owned_bytes":@(ownedBytes),@"unrelated_preserved":@([NSFileManager.defaultManager fileExistsAtPath:nonhex])}); [s shutdown];
    s=Service(fake,Root(@"memory-limit")); for(int i=0;i<150;i++) Request(s,valid,@"memory",i*1000);
    NSUInteger memoryBytes=[[s valueForKey:@"memoryBytes"] unsignedIntegerValue];
    NSDictionary *evicted=Request(s,valid,@"memory",0);
    Check(@"memory LRU remains bounded and evicts oldest",memoryBytes<=32*1024*1024 && [evicted[@"cache"] isEqual:@"disk"],@{@"bytes_before_reload":@(memoryBytes),@"oldest":evicted}); [s shutdown];
    NSDictionary *report=@{@"schema":@1,@"passed":@(failures==0),@"failures":@(failures),@"checks":checks,@"scope":@"Canonical Objective-C service on native main runloop with actual NSImage creation. Cache/decoder and delivery latency; excludes hover debounce, actual pointer interaction, floating panel presentation and playback. OS page cache recently populated; cold filesystem state is uncontrolled.",@"fixture":fixture,@"latency_trials_per_condition":@(skipLatency ? 0 : 100),@"request_order":@"deterministic permutation (i*37)%100, not timeline order",@"unqualified_fault":@"True filesystem ENOSPC was not induced; a regular-file cache root provides deterministic IO refusal without filling global disk"};
    NSData *json=[NSJSONSerialization dataWithJSONObject:report options:NSJSONWritingPrettyPrinted error:nil];
    [json writeToFile:[repo stringByAppendingPathComponent:@"work/validation/story002/service-results.json"] atomically:YES];
    [NSFileManager.defaultManager removeItemAtPath:base error:nil];
    printf("Service contracts: %lu checks, %lu failures\n",(unsigned long)checks.count,(unsigned long)failures);
    return failures ? 1 : 0;
}}
