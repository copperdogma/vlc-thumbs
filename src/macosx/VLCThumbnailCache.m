// SPDX-License-Identifier: GPL-2.0-or-later
#import "VLCThumbnailCache.h"
#import <CommonCrypto/CommonDigest.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

static const NSUInteger CacheMemoryLimit=32*1024*1024, CacheDiskLimit=256*1024*1024;
static const NSUInteger CacheResponseLimit=320*180*4+4096, ManifestLimit=256*1024;
static NSString *Hash(NSData *data) {
    uint8_t digest[CC_SHA256_DIGEST_LENGTH]; CC_SHA256(data.bytes,(CC_LONG)data.length,digest);
    NSMutableString *s=[NSMutableString string]; for(NSUInteger i=0;i<sizeof digest;i++) [s appendFormat:@"%02x",digest[i]]; return s;
}
static BOOL Hex(NSString *s) {
    return [s isKindOfClass:NSString.class] && s.length==64 &&
        [s rangeOfCharacterFromSet:[[NSCharacterSet characterSetWithCharactersInString:@"0123456789abcdef"] invertedSet]].location==NSNotFound;
}
static BOOL Decimal(NSString *s) {
    return [s isKindOfClass:NSString.class] && s.length>0 && s.length<=19 &&
        [s rangeOfCharacterFromSet:[[NSCharacterSet decimalDigitCharacterSet] invertedSet]].location==NSNotFound && s.longLongValue>=0;
}
static BOOL SafeAncestors(NSString *path) {
    if(!path.isAbsolutePath)return NO;
    if([path.pathComponents containsObject:@".."]||[path.pathComponents containsObject:@"."])return NO;
    NSString *cursor=path;
    while(cursor.length>1) {
        struct stat state;
        if(!lstat(cursor.fileSystemRepresentation,&state)) {
            if(!S_ISDIR(state.st_mode))return NO;
        } else if(errno!=ENOENT)return NO;
        NSRange slash=[cursor rangeOfString:@"/" options:NSBackwardsSearch];
        cursor=slash.location==0?@"/":[cursor substringToIndex:slash.location];
    }
    return YES;
}
static NSData *SafeRead(NSString *path, NSUInteger limit) {
    int fd=open(path.fileSystemRepresentation,O_RDONLY|O_NOFOLLOW|O_NONBLOCK); struct stat s;
    if(fd<0) return nil;
    if(fstat(fd,&s)||!S_ISREG(s.st_mode)||s.st_size<=0||(uint64_t)s.st_size>limit) {close(fd);return nil;}
    NSMutableData *out=[NSMutableData dataWithLength:(NSUInteger)s.st_size]; NSUInteger n=0;
    while(n<out.length) {ssize_t r=read(fd,(uint8_t *)out.mutableBytes+n,out.length-n);if(r<=0)break;n+=r;}
    close(fd);return n==out.length ? out : nil;
}
static BOOL Integer(NSNumber *number,int64_t minimum,int64_t maximum) {
    if(![number isKindOfClass:NSNumber.class])return NO;
    double value=number.doubleValue;
    return isfinite(value)&&floor(value)==value&&[number compare:@(minimum)]!=NSOrderedAscending&&[number compare:@(maximum)]!=NSOrderedDescending;
}
static NSDictionary *Header(NSData *raw) {
    const uint8_t *p=raw.bytes;NSUInteger n=0;while(n<raw.length&&n<4096&&p[n]!='\n')n++;
    if(n==raw.length||n==4096)return nil;
    id h=[NSJSONSerialization JSONObjectWithData:[raw subdataWithRange:NSMakeRange(0,n)] options:0 error:nil];
    if(![h isKindOfClass:NSDictionary.class])return nil;
    for(NSString *field in @[@"version",@"ok",@"width",@"height",@"channels",@"payload_bytes",@"actual_us",@"requested_us",@"video_ordinal"])
        if(!Integer(h[field],0,INT64_MAX))return nil;
    if(![h[@"ok"] boolValue]||![h[@"sampling"] isEqual:@"keyframe"]||![h[@"version"] isEqualToNumber:@3])return nil;
    NSInteger w=[h[@"width"] integerValue],height=[h[@"height"] integerValue];
    if(w<1||w>320||height<1||height>180||[h[@"channels"] intValue]!=4||
       [h[@"payload_bytes"] unsignedIntegerValue]!=(NSUInteger)w*height*4||raw.length-n-1!=(NSUInteger)w*height*4||
       ![h[@"actual_us"] isKindOfClass:NSNumber.class]||[h[@"actual_us"] longLongValue]<0)return nil;
    return h;
}
@interface VLCThumbnailCache ()
@property NSString *root,*key;
@property NSMutableDictionary *samples,*targets,*memory;
@property NSMutableArray *lru;
@property NSMutableArray *sampleRecency,*targetRecency;
@property NSMutableSet *demandFiles;
@property NSUInteger memoryBytes;
@property BOOL loaded;
@end
@implementation VLCThumbnailCache
- (instancetype)initWithRoot:(NSString *)root {
    if((self=[super init])) {_root=[root copy];_memory=[NSMutableDictionary dictionary];_lru=[NSMutableArray array];}
    return self;
}
- (BOOL)safeRoot {
    struct stat s;return SafeAncestors(_root) && !lstat(_root.fileSystemRepresentation,&s)&&S_ISDIR(s.st_mode);
}
- (NSString *)path:(NSString *)stem extension:(NSString *)ext {
    return [_root stringByAppendingPathComponent:[stem stringByAppendingPathExtension:ext]];
}
- (void)selectIdentity:(NSString *)identity {
    NSString *key=Hash([identity dataUsingEncoding:NSUTF8StringEncoding]);if([_key isEqual:key])return;
    _key=key;_samples=[NSMutableDictionary dictionary];_targets=[NSMutableDictionary dictionary];_loaded=NO;
    _sampleRecency=[NSMutableArray array];_targetRecency=[NSMutableArray array];
    _demandFiles=[NSMutableSet set];
    if(![self safeRoot])return;
    NSData *data=SafeRead([self path:key extension:@"json"],ManifestLimit);
    id manifest=data?[NSJSONSerialization JSONObjectWithData:data options:0 error:nil]:nil;
    if(![manifest isKindOfClass:NSDictionary.class]||![manifest[@"version"] isKindOfClass:NSNumber.class]||![manifest[@"version"] isEqualToNumber:@4]||
       ![manifest[@"key"] isEqual:key]||![manifest[@"samples"] isKindOfClass:NSDictionary.class]||
       ![manifest[@"targets"] isKindOfClass:NSDictionary.class]||[manifest[@"samples"] count]>512||[manifest[@"targets"] count]>2048)return;
    NSDictionary *samples=manifest[@"samples"],*targets=manifest[@"targets"];
    for(id stamp in samples) {
        id record=samples[stamp];
        if(!Decimal(stamp)||![record isKindOfClass:NSDictionary.class]||
           !Hex(record[@"file"])||!Hex(record[@"sha256"])||!Integer(record[@"actual_us"],0,INT64_MAX)||
           [record[@"actual_us"] longLongValue]<0||![stamp isEqual:[record[@"actual_us"] stringValue]])return;
        NSString *expected=Hash([[NSString stringWithFormat:@"%@:%@",key,stamp] dataUsingEncoding:NSUTF8StringEncoding]);
        if(![expected isEqual:record[@"file"]])return;
    }
    for(id t in targets) {
        id actual=targets[t];
        if(!Decimal(t)||!Decimal(actual)||!samples[actual])return;
    }
    _samples=[samples mutableCopy];_targets=[targets mutableCopy];_loaded=YES;
    // Recency is bounded per context. Older v4 manifests require no migration;
    // restart establishes deterministic order and subsequent use refreshes it.
    NSComparator numeric=^NSComparisonResult(NSString *a,NSString *b){return [@(a.longLongValue) compare:@(b.longLongValue)];};
    [_sampleRecency addObjectsFromArray:[samples.allKeys sortedArrayUsingComparator:numeric]];
    [_targetRecency addObjectsFromArray:[targets.allKeys sortedArrayUsingComparator:numeric]];
}
- (void)remember:(NSData *)raw key:(NSString *)key {
    if(!_memory[key]) {
        while(_memoryBytes+raw.length>CacheMemoryLimit&&_lru.count) {
            NSString *victim=_lru.firstObject;_memoryBytes-=[_memory[victim] length];[_memory removeObjectForKey:victim];[_lru removeObjectAtIndex:0];
        }
        _memory[key]=raw;_memoryBytes+=raw.length;
    }
    [_lru removeObject:key];[_lru addObject:key];
}
- (void)forgetSample:(NSString *)stamp {
    NSString *file=_samples[stamp][@"file"];
    if(file)[_demandFiles removeObject:file];
    [_samples removeObjectForKey:stamp];[_sampleRecency removeObject:stamp];
    NSArray *keys=[_targets allKeysForObject:stamp];[_targets removeObjectsForKeys:keys];[_targetRecency removeObjectsInArray:keys];
    if(file&&_memory[file]) {_memoryBytes-=[_memory[file] length];[_memory removeObjectForKey:file];[_lru removeObject:file];}
}
- (void)touch:(NSString *)key order:(NSMutableArray *)order {
    [order removeObject:key];[order addObject:key];
}
- (void)touchDiskSample:(NSString *)file {
    if(![self safeRoot])return;
    // Refresh the entry itself through no-follow descriptors. A resident hit
    // must count as use on disk too; passive coverage scans must not. Keep its
    // manifest recent as well, otherwise a retained payload could lose aliases.
    int rootFD=open(_root.fileSystemRepresentation,O_RDONLY|O_DIRECTORY|O_NOFOLLOW);
    if(rootFD<0)return;
    const struct timespec times[2]={{0,UTIME_OMIT},{0,UTIME_NOW}};
    for(NSString *name in @[[file stringByAppendingPathExtension:@"rgba"],[_key stringByAppendingPathExtension:@"json"]]) {
        int fd=openat(rootFD,name.fileSystemRepresentation,O_RDONLY|O_NOFOLLOW|O_NONBLOCK);
        struct stat state;
        if(fd>=0) {
            if(!fstat(fd,&state)&&S_ISREG(state.st_mode)&&state.st_nlink==1)futimens(fd,times);
            close(fd);
        }
    }
    close(rootFD);
}
- (NSDictionary *)sample:(NSString *)stamp touch:(BOOL)touch {
    NSDictionary *record=_samples[stamp];NSString *file=record[@"file"];if(!file)return nil;
    NSData *raw=_memory[file];NSString *source=raw?@"memory":@"disk";
    if(!raw&&[self safeRoot]) raw=SafeRead([self path:file extension:@"rgba"],CacheResponseLimit);
    NSDictionary *header=raw?Header(raw):nil;
    if(!header||![Hash(raw) isEqual:record[@"sha256"]]||[header[@"actual_us"] longLongValue]!=[record[@"actual_us"] longLongValue]) {
        [self forgetSample:stamp];
        return nil;
    }
    [self remember:raw key:file];
    if(touch) {
        [_demandFiles addObject:file];
        [self touch:stamp order:_sampleRecency];
        [self touchDiskSample:file];
    }
    return @{@"raw":raw,@"cache":source,@"actual_us":record[@"actual_us"]};
}
- (NSDictionary *)lookupTime:(int64_t)time maximumDistance:(int64_t)distance {
    return [self lookupTime:time maximumDistance:distance residentOnly:NO];
}
- (NSDictionary *)residentLookupTime:(int64_t)time maximumDistance:(int64_t)distance {
    return [self lookupTime:time maximumDistance:distance residentOnly:YES];
}
- (BOOL)isResidentSample:(NSString *)stamp {
    NSString *file=_samples[stamp][@"file"];return file&&_memory[file]!=nil;
}
- (NSDictionary *)lookupTime:(int64_t)time maximumDistance:(int64_t)distance residentOnly:(BOOL)residentOnly {
    NSString *target=@(time).stringValue;
    NSString *mapped=_targets[target];
    if(mapped&&(!residentOnly||[self isResidentSample:mapped])) {NSDictionary *hit=[self sample:mapped touch:YES];if(hit){[self touch:target order:_targetRecency];return hit;}}
    // An actual PTS is independently reusable even if no requested-time alias
    // was recorded for that exact value (including after app restart).
    NSDictionary *exact=(!residentOnly||[self isResidentSample:target])?[self sample:target touch:YES]:nil;if(exact)return exact;
    if(distance<0)return nil;
    NSArray *ordered=[_samples.allKeys sortedArrayUsingComparator:^NSComparisonResult(NSString *a,NSString *b) {
        uint64_t da=llabs(a.longLongValue-time),db=llabs(b.longLongValue-time);
        return da==db?[@(a.longLongValue) compare:@(b.longLongValue)]:[@(da) compare:@(db)];
    }];
    for(NSString *stamp in ordered) {
        if(llabs(stamp.longLongValue-time)>distance)break;
        if(residentOnly&&![self isResidentSample:stamp])continue;
        NSDictionary *hit=[self sample:stamp touch:YES];if(hit)return hit;
    }return nil;
}
- (BOOL)hasCapacity {return _samples.count<512&&_targets.count<2048;}
- (BOOL)storeRaw:(NSData *)raw requestedTime:(int64_t)time actualTime:(int64_t)actual {
    return [self storeRaw:raw requestedTime:time actualTime:actual allowEviction:NO];
}
- (BOOL)storeRaw:(NSData *)raw requestedTime:(int64_t)time actualTime:(int64_t)actual allowEviction:(BOOL)allowEviction {
    NSDictionary *header=Header(raw);if(!header||[header[@"actual_us"] longLongValue]!=actual||actual<0||time<0)return NO;
    NSString *stamp=@(actual).stringValue;NSString *file=Hash([[NSString stringWithFormat:@"%@:%@",_key,stamp] dataUsingEncoding:NSUTF8StringEncoding]);
    NSString *target=@(time).stringValue;
    if(!allowEviction&&((!_samples[stamp]&&_samples.count>=512)||(!_targets[target]&&_targets.count>=2048)))return NO;
    // Keep original successful payload for aliases: one actual keyframe, many targets.
    NSDictionary *existing=[self sample:stamp touch:NO];
    if(existing)raw=existing[@"raw"];
    if(!_samples[stamp]&&_samples.count>=512) {
        NSString *victim=_sampleRecency.firstObject;if(!victim)return NO;
        [self forgetSample:victim];
    }
    if(!_targets[target]&&_targets.count>=2048) {
        NSString *victim=_targetRecency.firstObject;if(!victim)return NO;
        [_targets removeObjectForKey:victim];[_targetRecency removeObjectAtIndex:0];
    }
    _samples[stamp]=@{@"file":file,@"sha256":Hash(raw),@"actual_us":@(actual)};
    if(allowEviction)[_demandFiles addObject:file];
    _targets[target]=stamp;[self remember:raw key:file];
    [self touch:stamp order:_sampleRecency];[self touch:target order:_targetRecency];
    NSFileManager *fm=NSFileManager.defaultManager;struct stat s;
    if(!SafeAncestors(_root))return YES;
    if(lstat(_root.fileSystemRepresentation,&s)&&errno==ENOENT)
        [fm createDirectoryAtPath:_root withIntermediateDirectories:YES attributes:@{NSFilePosixPermissions:@0700} error:nil];
    if(![self safeRoot])return YES;
    NSString *path=[self path:file extension:@"rgba"];
    // Atomic replacement replaces an entry symlink, never follows its target.
    if(![raw writeToFile:path options:NSDataWritingAtomic error:nil])return YES;
    NSData *manifest=[NSJSONSerialization dataWithJSONObject:@{@"version":@4,@"key":_key,@"samples":_samples,@"targets":_targets} options:NSJSONWritingSortedKeys error:nil];
    if(manifest.length<=ManifestLimit)[manifest writeToFile:[self path:_key extension:@"json"] options:NSDataWritingAtomic error:nil];
    [self prune];return YES;
}
- (NSDictionary *)completedMappings {
    NSMutableDictionary *maps=[NSMutableDictionary dictionary];
    for(NSString *target in _targets.allKeys.copy) {
        NSString *stamp=_targets[target];if([self sample:stamp touch:NO])maps[target]=@(stamp.longLongValue);
    }return maps;
}
- (NSDictionary *)metrics {return @{@"memory_bytes":@(_memoryBytes),@"samples":@(_samples.count),@"targets":@(_targets.count),@"demand_samples":@(_demandFiles.count),@"manifest_loaded":@(_loaded)};}
- (void)prune {
    if(![self safeRoot])return;
    NSMutableArray *entries=[NSMutableArray array];uint64_t bytes=0;NSFileManager *fm=NSFileManager.defaultManager;
    for(NSString *name in [fm contentsOfDirectoryAtPath:_root error:nil]) {
        NSString *ext=name.pathExtension;if(!([ext isEqual:@"rgba"]||[ext isEqual:@"json"])||!Hex(name.stringByDeletingPathExtension))continue;
        NSString *p=[_root stringByAppendingPathComponent:name];struct stat s;if(lstat(p.fileSystemRepresentation,&s)||!S_ISREG(s.st_mode)||s.st_size<0)continue;
        // Demand has greater retention value than background coverage, even
        // when that coverage is newer. This is a bounded current-identity tier,
        // not a pin: the hard disk limit can still evict it if necessary.
        BOOL demand=([ext isEqual:@"rgba"]&&[_demandFiles containsObject:name.stringByDeletingPathExtension])||
            ([ext isEqual:@"json"]&&[name.stringByDeletingPathExtension isEqual:_key]&&_demandFiles.count>0);
        bytes+=s.st_size;[entries addObject:@{@"path":p,@"bytes":@(s.st_size),@"demand":@(demand),@"age":@(s.st_mtimespec.tv_sec),@"nanoseconds":@(s.st_mtimespec.tv_nsec)}];
    }
    [entries sortUsingComparator:^NSComparisonResult(NSDictionary *a,NSDictionary *b){
        NSComparisonResult demand=[a[@"demand"] compare:b[@"demand"]];
        if(demand!=NSOrderedSame)return demand;
        NSComparisonResult age=[a[@"age"] compare:b[@"age"]];
        return age==NSOrderedSame?[a[@"nanoseconds"] compare:b[@"nanoseconds"]]:age;
    }];
    for(NSDictionary *e in entries) {if(bytes<=CacheDiskLimit)break;if([fm removeItemAtPath:e[@"path"] error:nil])bytes-=[e[@"bytes"] unsignedLongLongValue];}
}
@end
