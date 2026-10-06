// SPDX-License-Identifier: GPL-2.0-or-later
// Contract-level persistence/fault tests. No media input or NAS access.
#import <Foundation/Foundation.h>
#import <CommonCrypto/CommonDigest.h>
#import "VLCThumbnailCache.h"
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <stdlib.h>

static NSUInteger checks, failures;
static NSFileManager *fm;
static void Check(BOOL pass, NSString *message) {
    checks++; if (!pass) { failures++; fprintf(stderr,"FAIL: %s\n",message.UTF8String); }
}
static NSString *Digest(NSData *data) {
    unsigned char bytes[CC_SHA256_DIGEST_LENGTH]; CC_SHA256(data.bytes,(CC_LONG)data.length,bytes);
    NSMutableString *s=NSMutableString.string;
    for (NSUInteger i=0;i<sizeof bytes;i++) [s appendFormat:@"%02x",bytes[i]];
    return s;
}
static NSString *NewRoot(NSString *parent, NSString *name) {
    NSString *root=[parent stringByAppendingPathComponent:name];
    [fm createDirectoryAtPath:root withIntermediateDirectories:YES attributes:nil error:NULL];return root;
}
static NSData *Raw(int64_t actual, BOOL large) {
    NSUInteger w=large?320:2, h=large?180:2;
    NSDictionary *header=@{@"version":@3,@"ok":@YES,@"sampling":@"keyframe",@"width":@(w),@"height":@(h),@"channels":@4,@"payload_bytes":@(w*h*4),@"actual_us":@(actual),@"requested_us":@(actual),@"video_ordinal":@0};
    NSMutableData *data=[[NSJSONSerialization dataWithJSONObject:header options:0 error:NULL] mutableCopy];
    [data appendBytes:"\n" length:1];[data appendData:[NSMutableData dataWithLength:w*h*4]];return data;
}
static NSString *ManifestPath(NSString *root) {
    for (NSString *name in [fm contentsOfDirectoryAtPath:root error:NULL]) if ([name.pathExtension isEqual:@"json"]) return [root stringByAppendingPathComponent:name];return nil;
}
static NSMutableDictionary *Manifest(NSString *root) {
    return [NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:ManifestPath(root)] options:NSJSONReadingMutableContainers error:NULL];
}
static void WriteManifest(NSString *path, id value) {
    [[NSJSONSerialization dataWithJSONObject:value options:0 error:NULL] writeToFile:path atomically:YES];
}
static VLCThumbnailCache *Cache(NSString *root, NSString *identity) {
    VLCThumbnailCache *cache=[[VLCThumbnailCache alloc] initWithRoot:root];[cache selectIdentity:identity];return cache;
}
static void Scenario(NSString *name, void (^body)(void)) {
    @try {body();} @catch(NSException *exception) {Check(NO,[NSString stringWithFormat:@"%@ threw %@: %@",name,exception.name,exception.reason]);}
}
int main(void) {
    @autoreleasepool {
        fm=NSFileManager.defaultManager;
        const char *owned=getenv("VLC_CACHE_TEST_ROOT");
        if(!owned) {fprintf(stderr,"Run with test-cache.sh to select the owned ignored test directory\n");return 1;}
        NSString *base=[NSString stringWithUTF8String:owned];
        NSString *parent=[base stringByAppendingPathComponent:[@"vlc-cache-contract-" stringByAppendingString:NSUUID.UUID.UUIDString]];
        [fm createDirectoryAtPath:parent withIntermediateDirectories:YES attributes:nil error:NULL];
        Scenario(@"aliases and restart", ^{
            NSString *root=NewRoot(parent,@"aliases");VLCThumbnailCache *cache=Cache(root,@"movie:track0:render3");
            Check([cache storeRaw:Raw(1000000,NO) requestedTime:1100000 actualTime:1000000],@"store first sample");
            NSMutableData *alternate=[Raw(1000000,NO) mutableCopy];((uint8_t *)alternate.mutableBytes)[alternate.length-1]=42;
            Check([cache storeRaw:alternate requestedTime:1200000 actualTime:1000000],@"store alias");
            Check([[[cache lookupTime:1200000 maximumDistance:-1] objectForKey:@"raw"] isEqual:Raw(1000000,NO)],@"alias retains original successful sample bytes");
            Check([cache.metrics[@"samples"] integerValue]==1&&[cache.metrics[@"targets"] integerValue]==2,@"aliases share one image");
            NSUInteger payloads=0;for(NSString *name in [fm contentsOfDirectoryAtPath:root error:NULL])if([name.pathExtension isEqual:@"rgba"])payloads++;
            Check(payloads==1,@"aliases persist a single payload");
            Check([[Cache(root,@"movie:track0:render3") lookupTime:1000000 maximumDistance:-1][@"cache"] isEqual:@"disk"],@"restart reuses actual PTS with no requested-time alias");
            VLCThumbnailCache *reopen=Cache(root,@"movie:track0:render3");
            NSDictionary *hit=[reopen lookupTime:1200000 maximumDistance:-1];
            Check([hit[@"cache"] isEqual:@"disk"]&&[hit[@"actual_us"] longLongValue]==1000000,@"restart loads partial cache as disk hit with actual time");
            Check([reopen.completedMappings count]==2,@"restart restores aliases/coverage");
            Check([[reopen lookupTime:1100000 maximumDistance:-1][@"cache"] isEqual:@"memory"],@"repeat uses memory");
            Check([reopen lookupTime:1500000 maximumDistance:500000]!=nil,@"nearest permitted sample served");
            Check([reopen lookupTime:1500001 maximumDistance:500000]==nil,@"distance policy rejects distant image");
            [reopen selectIdentity:@"movie:track1:render3"];
            Check([reopen lookupTime:1100000 maximumDistance:INT64_MAX]==nil,@"different selected identity cannot leak resident sample");
            [reopen selectIdentity:@"movie:track0:render3"];
            Check([reopen lookupTime:1100000 maximumDistance:-1]!=nil,@"return to identity reuses retained entry");
            [reopen selectIdentity:@"movie:track0:render4"];
            Check([reopen lookupTime:1100000 maximumDistance:INT64_MAX]==nil,@"changed render/protocol identity cannot reuse old image");
            [reopen selectIdentity:@"movie:track0:render3"];
            Check([reopen lookupTime:1100000 maximumDistance:-1]!=nil,@"returning original render/protocol identity reuses retained image");
        });
        Scenario(@"malformed manifest", ^{
            NSString *root=NewRoot(parent,@"manifest");VLCThumbnailCache *seed=Cache(root,@"manifest-media");[seed storeRaw:Raw(100,NO) requestedTime:100 actualTime:100];
            NSString *path=ManifestPath(root);NSDictionary *valid=[Manifest(root) copy];
            NSArray *bad=@[@{@"version":@4},@[@4],@{@"version":@3,@"key":valid[@"key"],@"samples":@{},@"targets":@{}},@{@"version":@4.5,@"key":valid[@"key"],@"samples":@{},@"targets":@{}},@{@"version":@[],@"key":valid[@"key"],@"samples":@{},@"targets":@{}},@{@"version":NSNull.null,@"key":valid[@"key"],@"samples":@{},@"targets":@{}}];
            for(id value in bad) Scenario(@"malformed manifest field", ^{WriteManifest(path,value);VLCThumbnailCache *c=Cache(root,@"manifest-media");Check([c.completedMappings count]==0,@"invalid manifest rejected");});
            [[@"{\"version\":4," dataUsingEncoding:NSUTF8StringEncoding] writeToFile:path atomically:YES];
            Check([Cache(root,@"manifest-media").completedMappings count]==0,@"truncated manifest rejected");
            WriteManifest(path,valid);
            Check([Cache(root,@"manifest-media") lookupTime:100 maximumDistance:0]!=nil,@"fault recovery retains valid payload");
            for(NSString *section in @[@"samples",@"targets"]) for(id malformed in @[@[],@{},NSNull.null,@1]) Scenario(@"nested manifest field", ^{
                NSMutableDictionary *changed=[NSJSONSerialization JSONObjectWithData:[NSJSONSerialization dataWithJSONObject:valid options:0 error:NULL] options:NSJSONReadingMutableContainers error:NULL];changed[section][@"100"]=malformed;WriteManifest(path,changed);
                Check([Cache(root,@"manifest-media").completedMappings count]==0,@"malformed nested record/target rejected");
            });
            for(NSString *field in @[@"file",@"sha256",@"actual_us"]) for(id malformed in @[@[],@{},NSNull.null]) Scenario(@"nested manifest sample field", ^{
                NSMutableDictionary *changed=[NSJSONSerialization JSONObjectWithData:[NSJSONSerialization dataWithJSONObject:valid options:0 error:NULL] options:NSJSONReadingMutableContainers error:NULL];changed[@"samples"][@"100"][field]=malformed;WriteManifest(path,changed);
                Check([Cache(root,@"manifest-media").completedMappings count]==0,@"malformed nested sample field rejected");
            });
            NSMutableDictionary *over=[valid mutableCopy];NSMutableDictionary *tooMany=NSMutableDictionary.dictionary;for(NSUInteger i=0;i<513;i++)tooMany[@(i).stringValue]=valid[@"samples"][@"100"];over[@"samples"]=tooMany;WriteManifest(path,over);
            Check(![Cache(root,@"manifest-media").metrics[@"manifest_loaded"] boolValue],@"oversized sample count rejected before iteration");
            over=[valid mutableCopy];tooMany=NSMutableDictionary.dictionary;for(NSUInteger i=0;i<2049;i++)tooMany[@(i).stringValue]=@"100";over[@"targets"]=tooMany;WriteManifest(path,over);
            Check(![Cache(root,@"manifest-media").metrics[@"manifest_loaded"] boolValue],@"oversized target count rejected");
        });
        Scenario(@"malformed payload", ^{
            NSString *root=NewRoot(parent,@"payload");VLCThumbnailCache *seed=Cache(root,@"payload-media");[seed storeRaw:Raw(100,NO) requestedTime:100 actualTime:100];
            NSDictionary *valid=Manifest(root);NSString *file=valid[@"samples"][@"100"][@"file"];
            NSString *path=[root stringByAppendingPathComponent:[file stringByAppendingPathExtension:@"rgba"]];
            NSMutableData *modified=[Raw(100,NO) mutableCopy];((uint8_t *)modified.mutableBytes)[modified.length-1]=1;[modified writeToFile:path atomically:YES];
            Check([Cache(root,@"payload-media") lookupTime:100 maximumDistance:0]==nil,@"checksum rejects equally sized altered image");
            [Raw(100,NO) writeToFile:path atomically:YES];
            NSData *truncated=[Raw(100,NO) subdataWithRange:NSMakeRange(0,Raw(100,NO).length-1)];[truncated writeToFile:path atomically:YES];
            Check([Cache(root,@"payload-media") lookupTime:100 maximumDistance:0]==nil,@"truncated payload rejected");
            NSMutableData *old=[Raw(100,NO) mutableCopy];NSString *text=[[NSString alloc] initWithData:[old subdataWithRange:NSMakeRange(0,old.length-16)] encoding:NSUTF8StringEncoding];text=[text stringByReplacingOccurrencesOfString:@"\"version\":3" withString:@"\"version\":2"];NSMutableData *oldVersion=[[text dataUsingEncoding:NSUTF8StringEncoding] mutableCopy];[oldVersion appendData:[NSMutableData dataWithLength:16]];
            Check(![seed storeRaw:oldVersion requestedTime:100 actualTime:100],@"incompatible response version rejected");
            NSArray *fields=@[@"version",@"ok",@"width",@"height",@"channels",@"payload_bytes",@"actual_us",@"requested_us",@"video_ordinal"];
            for(NSString *field in fields) for(id malformed in @[@[],@{},NSNull.null,@"1"]) Scenario(@"malformed payload scalar", ^{
                NSMutableDictionary *header=[@{@"version":@3,@"ok":@YES,@"sampling":@"keyframe",@"width":@2,@"height":@2,@"channels":@4,@"payload_bytes":@16,@"actual_us":@100,@"requested_us":@100,@"video_ordinal":@0} mutableCopy];header[field]=malformed;
                NSMutableData *raw=[[NSJSONSerialization dataWithJSONObject:header options:0 error:NULL] mutableCopy];[raw appendBytes:"\n" length:1];[raw appendData:[NSMutableData dataWithLength:16]];
                Check(![seed storeRaw:raw requestedTime:200 actualTime:100],[NSString stringWithFormat:@"reject nonnumeric %@",field]);
            });
            for(NSString *field in fields) Scenario(@"fractional payload scalar", ^{
                NSMutableDictionary *header=[@{@"version":@3,@"ok":@YES,@"sampling":@"keyframe",@"width":@2,@"height":@2,@"channels":@4,@"payload_bytes":@16,@"actual_us":@100,@"requested_us":@100,@"video_ordinal":@0} mutableCopy];header[field]=@([header[field] doubleValue]+0.5);
                NSMutableData *raw=[[NSJSONSerialization dataWithJSONObject:header options:0 error:NULL] mutableCopy];[raw appendBytes:"\n" length:1];[raw appendData:[NSMutableData dataWithLength:16]];
                Check(![seed storeRaw:raw requestedTime:200 actualTime:100],[NSString stringWithFormat:@"reject fractional %@",field]);
            });
        });
        Scenario(@"root and entry ownership", ^{
            NSString *owner=[parent stringByAppendingPathComponent:@"owner-data"];NSData *sentinel=[@"owner stays unchanged" dataUsingEncoding:NSUTF8StringEncoding];[sentinel writeToFile:owner atomically:YES];
            VLCThumbnailCache *regular=Cache(owner,@"regular");Check([regular storeRaw:Raw(1,NO) requestedTime:1 actualTime:1],@"unsafe disk root permits RAM fallback");
            Check([[NSData dataWithContentsOfFile:owner] isEqual:sentinel],@"regular-file root preserved");
            NSString *outside=NewRoot(parent,@"outside");NSString *link=[parent stringByAppendingPathComponent:@"root-link"];symlink(outside.fileSystemRepresentation,link.fileSystemRepresentation);
            VLCThumbnailCache *linked=Cache(link,@"linked");[linked storeRaw:Raw(1,NO) requestedTime:1 actualTime:1];
            Check([[fm contentsOfDirectoryAtPath:outside error:NULL] count]==0,@"symlink root never writes through to outside directory");
            NSString *child=NewRoot(outside,@"child");VLCThumbnailCache *ancestor=Cache([link stringByAppendingPathComponent:@"child"],@"ancestor-link");[ancestor storeRaw:Raw(1,NO) requestedTime:1 actualTime:1];
            Check([[fm contentsOfDirectoryAtPath:child error:NULL] count]==0,@"ancestor symlink never writes into outside child");
            VLCThumbnailCache *missing=Cache([link stringByAppendingPathComponent:@"missing-child"],@"missing-ancestor-link");[missing storeRaw:Raw(1,NO) requestedTime:1 actualTime:1];
            Check(![fm fileExistsAtPath:[outside stringByAppendingPathComponent:@"missing-child"]],@"missing root under symlink ancestor never creates outside directory");
            NSString *root=NewRoot(parent,@"entry-link");VLCThumbnailCache *seed=Cache(root,@"linked-entry");[seed storeRaw:Raw(10,NO) requestedTime:10 actualTime:10];
            NSDictionary *manifest=Manifest(root);NSString *file=manifest[@"samples"][@"10"][@"file"];NSString *entry=[root stringByAppendingPathComponent:[file stringByAppendingPathExtension:@"rgba"]];
            NSString *external=[outside stringByAppendingPathComponent:@"thumbnail-owner"];[Raw(10,NO) writeToFile:external atomically:YES];NSData *original=[NSData dataWithContentsOfFile:external];[fm removeItemAtPath:entry error:NULL];symlink(external.fileSystemRepresentation,entry.fileSystemRepresentation);
            VLCThumbnailCache *fresh=Cache(root,@"linked-entry");Check([fresh lookupTime:10 maximumDistance:0]==nil,@"disk entry symlink not followed even with valid payload");
            [fresh storeRaw:Raw(10,NO) requestedTime:10 actualTime:10];struct stat info;lstat(entry.fileSystemRepresentation,&info);
            Check(S_ISREG(info.st_mode),@"atomic store replaces symlink itself");Check([[NSData dataWithContentsOfFile:external] isEqual:original],@"entry symlink target preserved");
        });
        Scenario(@"read-only cache", ^{
            NSString *root=NewRoot(parent,@"read-only");VLCThumbnailCache *c=Cache(root,@"read-only-media");
            Check(chmod(root.fileSystemRepresentation,0500)==0,@"set owned cache read-only");
            @try {
                Check(access(root.fileSystemRepresentation,W_OK)!=0,@"fixture actually denies cache writes");
                Check([c storeRaw:Raw(10,NO) requestedTime:10 actualTime:10],@"read-only disk still permits preview RAM storage");
                Check([[c lookupTime:10 maximumDistance:-1][@"cache"] isEqual:@"memory"],@"read-only cache serves RAM preview");
                Check([[fm contentsOfDirectoryAtPath:root error:NULL] count]==0,@"read-only cache creates no payload/manifest");
                Check([Cache(root,@"read-only-media") lookupTime:10 maximumDistance:-1]==nil,@"read-only RAM fallback cannot claim persisted restart hit");
            } @finally {chmod(root.fileSystemRepresentation,0700);}
        });
        Scenario(@"quota and foreign ownership", ^{
            NSString *root=NewRoot(parent,@"quota");NSString *foreign=[root stringByAppendingPathComponent:@"personal-note.rgba"];NSData *owner=[@"keep me" dataUsingEncoding:NSUTF8StringEncoding];[owner writeToFile:foreign atomically:YES];
            for(NSUInteger i=0;i<3;i++) {NSString *stem=Digest([[NSString stringWithFormat:@"quota-%lu",(unsigned long)i] dataUsingEncoding:NSUTF8StringEncoding]);NSString *path=[root stringByAppendingPathComponent:[stem stringByAppendingPathExtension:@"rgba"]];int fd=open(path.fileSystemRepresentation,O_WRONLY|O_CREAT|O_EXCL,0600);Check(fd>=0&&ftruncate(fd,128*1024*1024)==0,@"create sparse quota fixture");if(fd>=0)close(fd);[fm setAttributes:@{NSFileModificationDate:[NSDate dateWithTimeIntervalSince1970:1+i]} ofItemAtPath:path error:NULL];}
            NSString *outside=[parent stringByAppendingPathComponent:@"quota-owner"];[owner writeToFile:outside atomically:YES];NSString *link=[root stringByAppendingPathComponent:[Digest([@"quota-link" dataUsingEncoding:NSUTF8StringEncoding]) stringByAppendingPathExtension:@"rgba"]];symlink(outside.fileSystemRepresentation,link.fileSystemRepresentation);
            NSString *ignored=[root stringByAppendingPathComponent:[Digest([@"unknown-format" dataUsingEncoding:NSUTF8StringEncoding]) stringByAppendingPathExtension:@"txt"]];[owner writeToFile:ignored atomically:YES];
            VLCThumbnailCache *c=Cache(root,@"quota-media");[c storeRaw:Raw(10,NO) requestedTime:10 actualTime:10];
            uint64_t total=0;for(NSString *name in [fm contentsOfDirectoryAtPath:root error:NULL]) {if(name.stringByDeletingPathExtension.length!=64)continue;struct stat info;NSString *path=[root stringByAppendingPathComponent:name];if(!lstat(path.fileSystemRepresentation,&info)&&S_ISREG(info.st_mode))total+=info.st_size;}
            Check(total<=256*1024*1024,@"recognized disk entries bounded to 256MiB");Check([[NSData dataWithContentsOfFile:foreign] isEqual:owner],@"quota eviction preserves unrecognized owner file");
            struct stat info;Check(lstat(link.fileSystemRepresentation,&info)==0&&S_ISLNK(info.st_mode),@"quota cleanup leaves symlink alone");Check([[NSData dataWithContentsOfFile:outside] isEqual:owner],@"quota cleanup preserves symlink target");Check([[NSData dataWithContentsOfFile:ignored] isEqual:owner],@"quota cleanup preserves unknown extension even with hashed stem");
        });
        Scenario(@"meaningful disk recency and passive coverage", ^{
            NSString *root=NewRoot(parent,@"recency");VLCThumbnailCache *cache=Cache(root,@"recency-media");
            Check([cache storeRaw:Raw(100,NO) requestedTime:101 actualTime:100],@"seed recency sample");
            NSString *payload=[root stringByAppendingPathComponent:[Manifest(root)[@"samples"][@"100"][@"file"] stringByAppendingPathExtension:@"rgba"]];
            NSString *manifest=ManifestPath(root);
            NSDate *old=[NSDate dateWithTimeIntervalSince1970:1];
            for(NSString *path in @[payload,manifest])[fm setAttributes:@{NSFileModificationDate:old} ofItemAtPath:path error:NULL];
            Check(cache.completedMappings[@"101"]!=nil,@"passive resident coverage retains mapping");
            Check([cache.metrics[@"demand_samples"] integerValue]==0,@"background store and passive resident scan do not claim demand priority");
            struct stat payloadState,manifestState;lstat(payload.fileSystemRepresentation,&payloadState);lstat(manifest.fileSystemRepresentation,&manifestState);
            Check(payloadState.st_mtimespec.tv_sec==1&&manifestState.st_mtimespec.tv_sec==1,@"passive resident coverage does not refresh disk recency");
            VLCThumbnailCache *reopen=Cache(root,@"recency-media");
            Check(reopen.completedMappings[@"101"]!=nil,@"passive restart coverage validates retained payload");
            Check([reopen.metrics[@"demand_samples"] integerValue]==0,@"passive disk scan does not claim demand priority");
            lstat(payload.fileSystemRepresentation,&payloadState);lstat(manifest.fileSystemRepresentation,&manifestState);
            Check(payloadState.st_mtimespec.tv_sec==1&&manifestState.st_mtimespec.tv_sec==1,@"passive disk coverage does not refresh disk recency");
            Check([[reopen residentLookupTime:101 maximumDistance:-1][@"cache"] isEqual:@"memory"],@"meaningful resident hover uses RAM");
            lstat(payload.fileSystemRepresentation,&payloadState);lstat(manifest.fileSystemRepresentation,&manifestState);
            Check(payloadState.st_mtimespec.tv_sec>1&&manifestState.st_mtimespec.tv_sec>1,@"RAM hover refreshes payload and manifest disk recency");
            for(NSString *path in @[payload,manifest])[fm setAttributes:@{NSFileModificationDate:old} ofItemAtPath:path error:NULL];
            Check([[Cache(root,@"recency-media") lookupTime:101 maximumDistance:-1][@"cache"] isEqual:@"disk"],@"meaningful restart lookup reads disk");
            lstat(payload.fileSystemRepresentation,&payloadState);lstat(manifest.fileSystemRepresentation,&manifestState);
            Check(payloadState.st_mtimespec.tv_sec>1&&manifestState.st_mtimespec.tv_sec>1,@"disk hover refreshes payload and manifest recency");
        });
        for(NSNumber *newer in @[@NO,@YES]) Scenario(@"hot RAM retention under older and newer background quota pressure", ^{
            NSString *root=NewRoot(parent,[NSString stringWithFormat:@"hot-quota-%@",newer]);VLCThumbnailCache *cache=Cache(root,@"hot-quota-media");
            Check([cache storeRaw:Raw(100,NO) requestedTime:101 actualTime:100],@"seed hot quota sample");
            NSString *payload=[root stringByAppendingPathComponent:[Manifest(root)[@"samples"][@"100"][@"file"] stringByAppendingPathExtension:@"rgba"]];
            [fm setAttributes:@{NSFileModificationDate:[NSDate dateWithTimeIntervalSince1970:1]} ofItemAtPath:payload error:NULL];
            Check([[cache lookupTime:101 maximumDistance:-1][@"cache"] isEqual:@"memory"],@"hot quota hover is a RAM hit");
            struct stat hot;lstat(payload.fileSystemRepresentation,&hot);
            Check(hot.st_mtimespec.tv_sec>1,@"hot quota RAM hit refreshes its old disk age");
            uint64_t initial=0;for(NSString *name in [fm contentsOfDirectoryAtPath:root error:NULL]) {struct stat state;NSString *path=[root stringByAppendingPathComponent:name];if(!lstat(path.fileSystemRepresentation,&state))initial+=state.st_size;}
            NSString *filler=[root stringByAppendingPathComponent:[Digest([@"hot-quota-filler" dataUsingEncoding:NSUTF8StringEncoding]) stringByAppendingPathExtension:@"rgba"]];
            int fd=open(filler.fileSystemRepresentation,O_WRONLY|O_CREAT|O_EXCL,0600);
            Check(fd>=0&&ftruncate(fd,256*1024*1024-initial)==0,@"fill exact logical disk quota with sparse cold entry");
            if(fd>=0) {
                // Exercise sub-second ordering: background grids can create many
                // entries within the same second as a meaningful hover.
                struct timespec times[2]={hot.st_atimespec,hot.st_mtimespec};
                if(times[1].tv_sec<=1)times[1]=(struct timespec){2,0};
                else if(newer.boolValue) {
                    if(times[1].tv_nsec<999999999)times[1].tv_nsec++;
                    else {times[1].tv_sec++;times[1].tv_nsec=0;}
                } else if(times[1].tv_nsec>0)times[1].tv_nsec--;
                else {times[1].tv_sec--;times[1].tv_nsec=999999999;}
                Check(futimens(fd,times)==0,@"set cold entry just older or newer than hot hover");close(fd);
            }
            Check([cache storeRaw:Raw(200,NO) requestedTime:201 actualTime:200 allowEviction:NO],@"background preparation stores at disk quota");
            Check([fm fileExistsAtPath:payload],@"background prune preserves recently hovered RAM payload on disk");
            Check(![fm fileExistsAtPath:filler],@"quota prunes older or newer background entry rather than hot preview");
            NSDictionary *restart=[Cache(root,@"hot-quota-media") lookupTime:101 maximumDistance:-1];
            Check([restart[@"cache"] isEqual:@"disk"]&&[restart[@"actual_us"] longLongValue]==100,@"hot alias and image survive reopening without regeneration");
        });
        Scenario(@"fresh demand retention and identity-scoped priority", ^{
            NSString *root=NewRoot(parent,@"fresh-demand");VLCThumbnailCache *cache=Cache(root,@"fresh-demand-media");
            NSString *filler=[root stringByAppendingPathComponent:[Digest([@"fresh-demand-filler" dataUsingEncoding:NSUTF8StringEncoding]) stringByAppendingPathExtension:@"rgba"]];
            int fd=open(filler.fileSystemRepresentation,O_WRONLY|O_CREAT|O_EXCL,0600);
            Check(fd>=0&&ftruncate(fd,256*1024*1024)==0,@"fill disk quota before first decoded demand");if(fd>=0)close(fd);
            [fm setAttributes:@{NSFileModificationDate:[NSDate dateWithTimeIntervalSinceNow:86400]} ofItemAtPath:filler error:NULL];
            Check([cache storeRaw:Raw(100,NO) requestedTime:101 actualTime:100 allowEviction:YES],@"store newly decoded demand without repeat hover");
            Check([cache.metrics[@"demand_samples"] integerValue]==1,@"new decoded demand immediately enters retention tier");
            Check(![fm fileExistsAtPath:filler],@"newer background entry yields to newly decoded demand");
            Check([[Cache(root,@"fresh-demand-media") lookupTime:101 maximumDistance:-1][@"cache"] isEqual:@"disk"],@"newly decoded demand and manifest survive restart without prior RAM lookup");
            NSDictionary *retained=ManifestPath(root)?Manifest(root):nil;
            NSString *file=retained[@"samples"][@"100"][@"file"];
            NSString *payload=file?[root stringByAppendingPathComponent:[file stringByAppendingPathExtension:@"rgba"]]:nil;
            fd=payload?open(payload.fileSystemRepresentation,O_WRONLY|O_NOFOLLOW):-1;
            Check(fd>=0&&ftruncate(fd,300*1024*1024)==0,@"replace protected disk size with oversized sparse fault");if(fd>=0)close(fd);
            [cache storeRaw:Raw(200,NO) requestedTime:201 actualTime:200 allowEviction:NO];
            uint64_t total=0;for(NSString *name in [fm contentsOfDirectoryAtPath:root error:NULL]) {struct stat state;NSString *path=[root stringByAppendingPathComponent:name];if(!lstat(path.fileSystemRepresentation,&state)&&S_ISREG(state.st_mode))total+=state.st_size;}
            Check(total<=256*1024*1024&&payload&&![fm fileExistsAtPath:payload],@"hard disk quota can evict a demand-tier oversized fault");
            [cache selectIdentity:@"different-demand-media"];
            Check([cache.metrics[@"demand_samples"] integerValue]==0,@"identity switch clears current-session demand protection");
        });
        Scenario(@"RAM recency does not follow swapped symlinks", ^{
            NSString *root=NewRoot(parent,@"touch-links");VLCThumbnailCache *cache=Cache(root,@"touch-link-media");
            [cache storeRaw:Raw(100,NO) requestedTime:101 actualTime:100];
            NSString *payload=[root stringByAppendingPathComponent:[Manifest(root)[@"samples"][@"100"][@"file"] stringByAppendingPathExtension:@"rgba"]];
            NSString *manifest=ManifestPath(root);NSString *owner=[parent stringByAppendingPathComponent:@"touch-owner"];
            NSData *original=Raw(100,NO);[original writeToFile:owner atomically:YES];
            [fm setAttributes:@{NSFileModificationDate:[NSDate dateWithTimeIntervalSince1970:1]} ofItemAtPath:owner error:NULL];
            for(NSString *entry in @[payload,manifest]) {[fm removeItemAtPath:entry error:NULL];Check(symlink(owner.fileSystemRepresentation,entry.fileSystemRepresentation)==0,@"swap retained entry for owner symlink");}
            Check([[cache residentLookupTime:101 maximumDistance:-1][@"cache"] isEqual:@"memory"],@"entry symlink does not prevent safe RAM fallback");
            struct stat state;lstat(owner.fileSystemRepresentation,&state);
            Check(state.st_mtimespec.tv_sec==1&&[[NSData dataWithContentsOfFile:owner] isEqual:original],@"RAM touch preserves entry-symlink target timestamps and bytes");
            [fm removeItemAtPath:payload error:NULL];Check(link(owner.fileSystemRepresentation,payload.fileSystemRepresentation)==0,@"swap payload for owner hard link");
            Check([[cache residentLookupTime:101 maximumDistance:-1][@"cache"] isEqual:@"memory"],@"hard-linked payload retains safe RAM fallback");
            lstat(owner.fileSystemRepresentation,&state);
            Check(state.st_mtimespec.tv_sec==1&&[[NSData dataWithContentsOfFile:owner] isEqual:original],@"RAM touch preserves hard-linked owner timestamps and bytes");
            NSString *moved=[root stringByAppendingString:@"-moved"];[fm moveItemAtPath:root toPath:moved error:NULL];
            NSString *outside=NewRoot(parent,@"touch-outside");Check(symlink(outside.fileSystemRepresentation,root.fileSystemRepresentation)==0,@"swap root for directory symlink");
            Check([[cache residentLookupTime:101 maximumDistance:-1][@"cache"] isEqual:@"memory"],@"swapped root retains safe RAM fallback");
            Check([[fm contentsOfDirectoryAtPath:outside error:NULL] count]==0,@"RAM touch never writes through swapped root symlink");
        });
        Scenario(@"resident-only provisional ownership", ^{
            NSString *root=NewRoot(parent,@"resident-only");VLCThumbnailCache *writer=Cache(root,@"resident-media");
            Check([writer storeRaw:Raw(2,NO) requestedTime:3 actualTime:2],@"seed resident-only sample");
            Check([writer residentLookupTime:3 maximumDistance:0]!=nil,@"current resident sample eligible for provisional lookup");
            VLCThumbnailCache *reader=Cache(root,@"resident-media");
            Check([reader residentLookupTime:3 maximumDistance:0]==nil,@"resident-only lookup cannot promote prior-session disk sample");
            Check([[reader lookupTime:3 maximumDistance:0][@"cache"] isEqual:@"disk"],@"ordinary lookup retains verified disk reuse");
            Check([[reader residentLookupTime:3 maximumDistance:0][@"cache"] isEqual:@"memory"],@"loaded sample is now resident in qualified context");
            [reader selectIdentity:@"other-resident-media"];
            Check([reader residentLookupTime:3 maximumDistance:10]==nil,@"identity change clears provisional residents");
        });
        Scenario(@"memory budget", ^{
            // Use a non-directory root so 35MiB generated bytes remain RAM-only.
            NSString *root=[parent stringByAppendingPathComponent:@"memory-only"];[@"owner" writeToFile:root atomically:YES encoding:NSUTF8StringEncoding error:NULL];VLCThumbnailCache *c=Cache(root,@"memory-media");
            for(int64_t i=0;i<150;i++)Check([c storeRaw:Raw(i,YES) requestedTime:i actualTime:i],@"store full-size bounded image");
            Check([c.metrics[@"memory_bytes"] unsignedLongLongValue]<=32*1024*1024,@"RAM LRU stays within 32MiB");Check([c lookupTime:149 maximumDistance:0]!=nil,@"recent image retained under RAM eviction");Check([c lookupTime:0 maximumDistance:0]==nil,@"old RAM-only image evicted");
        });
        Scenario(@"sample and alias caps", ^{
            NSString *root=NewRoot(parent,@"caps");VLCThumbnailCache *samples=Cache(root,@"samples");
            for(int64_t i=0;i<512;i++)Check([samples storeRaw:Raw(i,NO) requestedTime:i actualTime:i],@"fill finite sample budget");Check(!samples.hasCapacity,@"512 samples stop background capacity");Check(![samples storeRaw:Raw(512,NO) requestedTime:512 actualTime:512],@"513th distinct sample rejected");
            for(int64_t i=0;i<512;i++)Check([samples lookupTime:i maximumDistance:-1]!=nil,@"demand each bounded retained sample");
            Check([samples.metrics[@"demand_samples"] integerValue]==512,@"demand priority count stays within sample capacity");
            Check([samples lookupTime:0 maximumDistance:-1]!=nil,@"demand lookup refreshes sample recency");
            Check([samples storeRaw:Raw(4000,NO) requestedTime:9999 actualTime:4000 allowEviction:YES],@"demand at sample capacity displaces old sample");
            Check([samples.metrics[@"samples"] integerValue]==512&&[samples.metrics[@"targets"] integerValue]==512,@"demand sample eviction removes victim aliases and stays bounded");
            Check([samples.metrics[@"demand_samples"] integerValue]==512,@"sample eviction removes old demand priority before adding new demand");
            Check([samples lookupTime:1 maximumDistance:-1]==nil,@"least-recent sample evicted");Check([samples lookupTime:0 maximumDistance:-1]!=nil,@"recently demanded old sample protected");
            Check([[samples lookupTime:9999 maximumDistance:-1][@"cache"] isEqual:@"memory"],@"repeat overflow demand reused without decode");
            Check([[Cache(root,@"samples") lookupTime:4000 maximumDistance:-1][@"cache"] isEqual:@"disk"],@"overflow demand retained through restart and actual PTS reused");
            [samples selectIdentity:@"other-cap-identity"];Check([samples lookupTime:4000 maximumDistance:-1]==nil,@"demand eviction cannot cross identity");
            VLCThumbnailCache *aliases=Cache(root,@"aliases-cap");for(int64_t i=0;i<2048;i++)Check([aliases storeRaw:Raw(1,NO) requestedTime:i actualTime:1],@"fill finite target budget");Check(!aliases.hasCapacity,@"2048 targets stop capacity");Check(![aliases storeRaw:Raw(1,NO) requestedTime:2048 actualTime:1],@"2049th target rejected");Check([aliases.metrics[@"samples"] integerValue]==1,@"target budget doesn't duplicate payloads");
            [aliases lookupTime:0 maximumDistance:-1];Check([aliases storeRaw:Raw(1,NO) requestedTime:3000 actualTime:1 allowEviction:YES],@"demand at alias capacity retained");
            Check([aliases.metrics[@"targets"] integerValue]==2048&&[aliases.metrics[@"samples"] integerValue]==1,@"demand alias eviction keeps bounded single image");
            NSDictionary *coverage=aliases.completedMappings;Check(coverage[@"0"]!=nil&&coverage[@"1"]==nil&&coverage[@"3000"]!=nil,@"oldest alias evicted and recently used alias protected");
            Check([aliases lookupTime:3000 maximumDistance:-1]!=nil,@"overflow alias repeat reused");
            Check([Cache(root,@"aliases-cap") lookupTime:3000 maximumDistance:-1]!=nil,@"overflow alias survives restart");
        });
        [fm removeItemAtPath:parent error:NULL];
        printf("cache contracts: %lu checks, %lu failures\n",(unsigned long)checks,(unsigned long)failures);
    }
    return failures?1:0;
}
