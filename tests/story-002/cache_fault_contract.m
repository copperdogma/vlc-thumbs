// SPDX-License-Identifier: GPL-2.0-or-later
// Run against a caller-owned unwritable or genuinely full cache filesystem.
#import <Cocoa/Cocoa.h>
#import "VLCThumbnailService.h"
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
static double Now(void) { return NSProcessInfo.processInfo.systemUptime; }
static NSDictionary *Request(VLCThumbnailService *s, NSURL *media, int64_t time) {
    __block NSDictionary *result=nil; double start=Now();
    [s requestURL:media generation:@"filesystem-fault" videoOrdinal:0 videoCount:1 time:time completion:^(NSImage *image,NSDictionary *reply){
        NSMutableDictionary *r=[reply mutableCopy]; r[@"has_image"]=@(image!=nil); r[@"measured_ms"]=@((Now()-start)*1000); result=r;
    }];
    while(!result && Now()-start<7) [NSRunLoop.mainRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:.001]];
    return result ?: @{@"has_image":@NO,@"error":@"test-timeout"};
}
static NSUInteger Entries(NSString *root) {
    NSUInteger n=0; for(NSString *name in [NSFileManager.defaultManager contentsOfDirectoryAtPath:root error:nil])
        if([name hasSuffix:@".rgba"]) n++; return n;
}
int main(int argc,const char **argv) { @autoreleasepool {
    if(argc!=4) return 2;
    [NSApplication sharedApplication]; NSString *repo=@(argv[1]),*root=@(argv[2]),*phase=@(argv[3]);
    NSString *helper=[repo stringByAppendingPathComponent:@"work/build/thumbnail-helper/thumbnail-helper"];
    NSURL *media=[NSURL fileURLWithPath:[repo stringByAppendingPathComponent:@"work/fixtures/story-002/standard.mp4"]];
    if([phase isEqual:@"identity"]) {
        [NSFileManager.defaultManager createDirectoryAtPath:root withIntermediateDirectories:YES attributes:nil error:nil];
        NSString *input=[root stringByAppendingPathComponent:@"owned-mode.txt"],*replacement=[root stringByAppendingPathComponent:@"replacement.txt"];
        [@"slow" writeToFile:input atomically:NO encoding:NSUTF8StringEncoding error:nil];
        struct stat before; if(stat(input.fileSystemRepresentation,&before)) return 2;
        NSURL *owned=[NSURL fileURLWithPath:input];
        NSString *fake=[repo stringByAppendingPathComponent:@"tests/story-002/fake-helper.py"];
        VLCThumbnailService *identity=[[VLCThumbnailService alloc] initWithHelperPath:fake cacheRoot:[root stringByAppendingPathComponent:@"Cache"]];
        NSDictionary *seed=Request(identity,owned,0);
        __block BOOL preserved=NO,renamed=NO;
        dispatch_after(dispatch_time(DISPATCH_TIME_NOW,100*NSEC_PER_MSEC),dispatch_get_main_queue(),^{
            [@"fast" writeToFile:replacement atomically:NO encoding:NSUTF8StringEncoding error:nil];
            renamed=rename(replacement.fileSystemRepresentation,input.fileSystemRepresentation)==0;
            struct timespec times[2]={before.st_atimespec,before.st_mtimespec};
            if(renamed && utimensat(AT_FDCWD,input.fileSystemRepresentation,times,0)==0) {
                struct stat after; preserved=stat(input.fileSystemRepresentation,&after)==0 && after.st_size==before.st_size &&
                    after.st_mtimespec.tv_sec==before.st_mtimespec.tv_sec && after.st_mtimespec.tv_nsec==before.st_mtimespec.tv_nsec && after.st_ino!=before.st_ino;
            }
        });
        NSDictionary *inflight=Request(identity,owned,1000000); [identity shutdown];
        identity=[[VLCThumbnailService alloc] initWithHelperPath:fake cacheRoot:[root stringByAppendingPathComponent:@"Cache"]];
        NSDictionary *reopened=Request(identity,owned,0); [identity shutdown];
        BOOL passed=[seed[@"has_image"] boolValue] && renamed && preserved && ![inflight[@"has_image"] boolValue] &&
            [inflight[@"error"] isEqual:@"changed-or-cancelled"] && [reopened[@"has_image"] boolValue] && [reopened[@"cache"] isEqual:@"miss"];
        NSDictionary *report=@{@"phase":phase,@"passed":@(passed),@"same_size_and_exact_nanosecond_mtime":@(preserved),
            @"atomic_replacement":@(renamed),@"seed":seed,@"inflight":inflight,@"reopened":reopened};
        NSData *json=[NSJSONSerialization dataWithJSONObject:report options:NSJSONWritingPrettyPrinted error:nil];
        fwrite(json.bytes,1,json.length,stdout); fputc('\n',stdout); return passed?0:1;
    }
    VLCThumbnailService *s=[[VLCThumbnailService alloc] initWithHelperPath:helper cacheRoot:root];
    NSDictionary *first,*next; BOOL passed;
    if([phase isEqual:@"fault"]) {
        first=Request(s,media,1000000); next=Request(s,media,2000000);
        passed=[first[@"has_image"] boolValue] && [next[@"has_image"] boolValue] &&
            [first[@"cache"] isEqual:@"miss"] && [next[@"cache"] isEqual:@"miss"] && Entries(root)==0;
        [s shutdown];
    } else if([phase isEqual:@"recovery"]) {
        first=Request(s,media,3000000); [s shutdown];
        s=[[VLCThumbnailService alloc] initWithHelperPath:helper cacheRoot:root];
        next=Request(s,media,3000000); [s shutdown];
        passed=[first[@"has_image"] boolValue] && [first[@"cache"] isEqual:@"miss"] &&
            [next[@"has_image"] boolValue] && [next[@"cache"] isEqual:@"disk"] && Entries(root)>0;
    } else return 2;
    NSDictionary *report=@{@"phase":phase,@"passed":@(passed),@"first":first,@"next":next,@"disk_entries":@(Entries(root))};
    NSData *json=[NSJSONSerialization dataWithJSONObject:report options:NSJSONWritingPrettyPrinted error:nil];
    fwrite(json.bytes,1,json.length,stdout); fputc('\n',stdout); return passed?0:1;
}}
