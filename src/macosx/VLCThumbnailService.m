// SPDX-License-Identifier: GPL-2.0-or-later
#import "VLCThumbnailService.h"
#import "VLCThumbnailWorker.h"
#import "VLCThumbnailCache.h"
#import "VLCThumbnailScheduler.h"
#include <sys/stat.h>
#include <signal.h>
#include <unistd.h>
#include <fcntl.h>
#include <float.h>


int64_t VLCThumbnailBridgeDistance(int64_t duration)
{
    long double desired=(long double)MAX((int64_t)0,duration)/30000000.0L;
    NSUInteger count=7;long double error=fabsl(desired-7.0L);
    for(NSUInteger candidate=15;candidate<=255;candidate=candidate*2+1) {
        long double candidateError=fabsl(desired-(long double)candidate);
        if(candidateError<error){count=candidate;error=candidateError;}
    }
    return MIN(60000000LL,MAX(2000000LL,MAX((int64_t)0,duration)/(int64_t)(count+1)/2));
}

void VLCTimelineTrace(NSDictionary *event)
{
    NSString *path = [[[NSProcessInfo processInfo] environment] objectForKey:@"VLC_TIMELINE_DIAGNOSTICS"];
    if (![path isAbsolutePath]) return;
    static dispatch_queue_t traceQueue;
    static dispatch_once_t once;
    dispatch_once(&once, ^{ traceQueue = dispatch_queue_create("org.videolan.timeline.trace", DISPATCH_QUEUE_SERIAL); });
    NSMutableDictionary *record = [event mutableCopy];
    record[@"monotonic"] = @([[NSProcessInfo processInfo] systemUptime]);
    dispatch_async(traceQueue, ^{
        NSData *line = [NSJSONSerialization dataWithJSONObject:record options:0 error:nil];
        if (!line) return;
        int fd = open([path fileSystemRepresentation], O_WRONLY | O_CREAT | O_APPEND | O_NOFOLLOW, 0600);
        if (fd < 0) return;
        NSMutableData *out = [line mutableCopy]; [out appendBytes:"\n" length:1];
        const uint8_t *bytes = out.bytes; NSUInteger done = 0;
        while (done < out.length) { ssize_t n = write(fd, bytes + done, out.length - done); if (n <= 0) break; done += n; }
        close(fd);
    });
}

static NSDictionary *DecodeResponse(NSData *data, int64_t expected, NSInteger ordinal)
{
    const uint8_t *bytes = data.bytes; NSUInteger n = data.length, split = 0;
    while (split < n && split < 4096 && bytes[split] != '\n') split++;
    if (split == n || split == 4096) return nil;
    NSDictionary *header = [NSJSONSerialization JSONObjectWithData:[data subdataWithRange:NSMakeRange(0, split)] options:0 error:nil];
    if (![header isKindOfClass:[NSDictionary class]] || ![header[@"version"] isKindOfClass:[NSNumber class]] || ![header[@"version"] isEqualToNumber:@3]) return nil;
    if (![header[@"ok"] isKindOfClass:[NSNumber class]]) return nil;
    if (![header[@"ok"] boolValue]) return @{ @"ok": @NO, @"error": [header[@"error"] isKindOfClass:NSString.class] ? header[@"error"] : @"decode-unavailable" };
    if (![header[@"sampling"] isEqual:@"keyframe"]) return nil;
    for (NSString *key in @[@"width", @"height", @"channels", @"payload_bytes", @"actual_us", @"requested_us", @"video_ordinal"])
        if (![header[key] isKindOfClass:[NSNumber class]] || !isfinite([header[key] doubleValue]) || floor([header[key] doubleValue]) != [header[key] doubleValue]) return nil;
    NSInteger w = [header[@"width"] integerValue], h = [header[@"height"] integerValue];
    int64_t actual = [header[@"actual_us"] longLongValue];
    if (w < 1 || w > 320 || h < 1 || h > 180 || [header[@"channels"] intValue] != 4 ||
        [header[@"payload_bytes"] unsignedLongLongValue] != (uint64_t)w * h * 4 ||
        n - split - 1 != (NSUInteger)w * h * 4 || actual < 0 ||
        ![header[@"requested_us"] isEqualToNumber:@(expected)] || ![header[@"video_ordinal"] isEqualToNumber:@(ordinal)]) return nil;
    NSMutableDictionary *answer = [header mutableCopy];
    answer[@"pixels"] = [data subdataWithRange:NSMakeRange(split + 1, n - split - 1)];
    return answer;
}

static NSImage *ImageForResponse(NSDictionary *response)
{
    NSInteger w = [response[@"width"] integerValue], h = [response[@"height"] integerValue];
    NSData *pixels = response[@"pixels"];
    if (!pixels) return nil;
    NSBitmapImageRep *rep = [[NSBitmapImageRep alloc] initWithBitmapDataPlanes:NULL pixelsWide:w pixelsHigh:h
        bitsPerSample:8 samplesPerPixel:4 hasAlpha:YES isPlanar:NO colorSpaceName:NSDeviceRGBColorSpace
        bitmapFormat:NSBitmapFormatAlphaNonpremultiplied bytesPerRow:w * 4 bitsPerPixel:32];
    if (!rep) return nil;
    memcpy(rep.bitmapData, pixels.bytes, pixels.length);
    NSImage *image = [[NSImage alloc] initWithSize:NSMakeSize(w, h)];
    [image addRepresentation:rep]; return image;
}

static NSNumber *HeaderTime(NSData *raw) {
    const uint8_t *p=raw.bytes;NSUInteger n=0;while(n<raw.length&&n<4096&&p[n]!='\n')n++;
    if(n>=raw.length||n>=4096)return nil;
    id h=[NSJSONSerialization JSONObjectWithData:[raw subdataWithRange:NSMakeRange(0,n)] options:0 error:nil];
    return [h isKindOfClass:NSDictionary.class]&&[h[@"requested_us"] isKindOfClass:NSNumber.class]?h[@"requested_us"]:nil;
}
@interface VLCThumbnailService ()
@property dispatch_queue_t queue,decodeQueue,metadataQueue;
@property VLCThumbnailWorker *decoder,*identityWorker;
@property VLCThumbnailCache *cache;
@property VLCThumbnailScheduler *scheduler;
@property NSDictionary *context,*hover;
@property NSDictionary *pendingCacheValidation;
@property NSMutableDictionary *failures;
@property NSString *verifiedIdentity,*verifiedState,*invalidatedGeneration;
@property NSTimer *wake,*provisionalExpiry;
@property NSUInteger requestID,contextSerial,completed,superseded;
@property BOOL running,stopped,hoverSatisfied,cacheRunning,cacheIntentPending;
@property BOOL validationRunning,cacheResolvedHit,provisionalAllowed;
@property NSUInteger cacheResolvedRequestID,lastValidatedRequestID;
@property double nextBackground;
@end
static double ServiceNow(void) {return NSProcessInfo.processInfo.systemUptime;}
static BOOL Terminal(NSString *error) {
    return [error hasPrefix:@"unsupported"] || [error hasPrefix:@"ambiguous"] ||
        [error hasPrefix:@"unknown"] || [error isEqual:@"track_unavailable"] || [error isEqual:@"invalid_arguments"] || [error isEqual:@"media_changed"];
}
@implementation VLCThumbnailService
+ (instancetype)sharedService {
    static VLCThumbnailService *service; static dispatch_once_t once;
    dispatch_once(&once, ^{
        NSBundle *b=NSBundle.mainBundle;
        NSString *root=NSSearchPathForDirectoriesInDomains(NSCachesDirectory,NSUserDomainMask,YES).firstObject;
        root=[[root stringByAppendingPathComponent:b.bundleIdentifier ?: @"org.videolan.vlc-thumbs.development"] stringByAppendingPathComponent:@"TimelineThumbnails"];
        NSString *helper=[b.executablePath.stringByDeletingLastPathComponent stringByAppendingPathComponent:@"vlc-thumbnail-helper"];
        service=[[self alloc] initWithHelperPath:helper cacheRoot:root];
        [NSNotificationCenter.defaultCenter addObserver:service selector:@selector(shutdown) name:NSApplicationWillTerminateNotification object:nil];
    });return service;
}
- (instancetype)initWithHelperPath:(NSString *)helperPath cacheRoot:(NSString *)root {
    if((self=[super init])) {
        _queue=dispatch_queue_create("org.videolan.timeline.thumbnail",dispatch_queue_attr_make_with_qos_class(DISPATCH_QUEUE_SERIAL,QOS_CLASS_UTILITY,0));
        _decodeQueue=dispatch_queue_create("org.videolan.timeline.decode",dispatch_queue_attr_make_with_qos_class(DISPATCH_QUEUE_SERIAL,QOS_CLASS_UTILITY,0));
        _metadataQueue=dispatch_queue_create("org.videolan.timeline.metadata",dispatch_queue_attr_make_with_qos_class(DISPATCH_QUEUE_SERIAL,QOS_CLASS_UTILITY,0));
        _decoder=[[VLCThumbnailWorker alloc] initWithHelperPath:helperPath];
        _identityWorker=[[VLCThumbnailWorker alloc] initWithHelperPath:helperPath];
        _cache=[[VLCThumbnailCache alloc] initWithRoot:root];_failures=[NSMutableDictionary dictionary];
        _provisionalAllowed=YES;
    }return self;
}
- (void)prepareContext:(NSDictionary *)context enabled:(BOOL)enabled {
    NSAssert(NSThread.isMainThread,@"Thumbnail context is main-thread");
    if(_stopped)return;
    if(!enabled||![context[@"eligible"] boolValue]) {if(_context)[self cancel];return;}
    if([_context isEqualToDictionary:context])return;
    if([_invalidatedGeneration isEqual:context[@"generation"]])return;
    self.invalidatedGeneration=nil;
    [self cancel];_context=[context copy];
    int64_t duration=[context[@"duration"] longLongValue];
    if(duration>0)_scheduler=[[VLCThumbnailScheduler alloc] initWithDuration:duration];
    _nextBackground=ServiceNow()+.25;[self pump];
}
- (NSUInteger)requestURL:(NSURL *)url generation:(NSString *)generation videoOrdinal:(NSInteger)ordinal videoCount:(NSInteger)count time:(int64_t)time completion:(VLCThumbnailCompletion)completion {
    NSAssert(NSThread.isMainThread,@"Thumbnail requests must be main-thread");
    if(_stopped) {completion(nil,@{@"error":@"shutdown"});return 0;}
    if(!url||!generation||time<0) {completion(nil,@{@"error":@"invalid-request"});return 0;}
    if(![_context[@"url"] isEqual:url]||![_context[@"generation"] isEqual:generation]||[_context[@"videoOrdinal"] integerValue]!=ordinal||[_context[@"videoCount"] integerValue]!=count) {
        [self prepareContext:@{@"eligible":@(url.isFileURL),@"url":url,@"generation":generation,
                              @"videoOrdinal":@(ordinal),@"videoCount":@(count),@"duration":@0} enabled:YES];
    }
    if(!url.isFileURL) {completion(nil,@{@"error":@"not-local-or-cancelled"});return 0;}
    if([_invalidatedGeneration isEqual:generation]) {completion(nil,@{@"error":@"media_changed"});return 0;}
    if(_hover)_superseded++;
    NSUInteger token=++_requestID;
    _hover=@{@"time":@(time),@"id":@(token),@"completion":[completion copy],@"started":@(ServiceNow())};
    _hoverSatisfied=NO;
    _pendingCacheValidation=nil;
    NSDictionary *failure=_failures[@(time)];
    if(failure&&ServiceNow()-[failure[@"last"] doubleValue]>30) [_failures removeObjectForKey:@(time)];
    _cacheIntentPending=YES;[self pumpCachedPresentation];[self pump];return token;
}
- (void)cancelRequest:(NSUInteger)token {
    NSAssert(NSThread.isMainThread,@"Thumbnail cancellation must be main-thread");
    if(!token||token!=_requestID)return;
    _requestID++;_hover=nil;_hoverSatisfied=NO;_pendingCacheValidation=nil;
    [_provisionalExpiry invalidate];_provisionalExpiry=nil;[self pump];
}
- (void)cancel {
    NSAssert(NSThread.isMainThread,@"Thumbnail cancellation must be main-thread");
    @synchronized(self) {_contextSerial++;}
    _requestID++;_hover=nil;_context=nil;_scheduler=nil;_hoverSatisfied=NO;_cacheIntentPending=NO;
    _pendingCacheValidation=nil;_provisionalAllowed=YES;_cacheResolvedRequestID=0;_lastValidatedRequestID=0;
    [_provisionalExpiry invalidate];_provisionalExpiry=nil;
    [_wake invalidate];_wake=nil;[_failures removeAllObjects];
    [_decoder invalidate];[_identityWorker invalidate];
    // Worker-owned verification state is reset in-order, after any old job exits.
    dispatch_async(_queue, ^{self.verifiedIdentity=nil;self.verifiedState=nil;});
}
- (void)shutdown {[self cancel];_stopped=YES;}
- (NSDictionary *)metrics {
    NSMutableDictionary *m=[NSMutableDictionary dictionaryWithDictionary:[_decoder metrics]];
    [m addEntriesFromDictionary:@{@"active":@(_running),@"pending":@(_hover&&!_hoverSatisfied),@"completed":@(_completed),@"superseded":@(_superseded)}];return m;
}
- (BOOL)currentSerial:(NSUInteger)serial {@synchronized(self){return serial==_contextSerial;}}
- (BOOL)activeContext:(NSDictionary *)context serial:(NSUInteger)serial {
    return [self currentSerial:serial]&&![self.invalidatedGeneration isEqual:context[@"generation"]];
}
- (void)wakeAt:(double)when {
    [_wake invalidate];__weak typeof(self) weakSelf=self;
    _wake=[NSTimer timerWithTimeInterval:MAX(.01,when-ServiceNow()) repeats:NO block:^(NSTimer *timer){(void)timer;
        typeof(self) owner=weakSelf;owner.wake=nil;[owner pump];
    }];
    [NSRunLoop.mainRunLoop addTimer:_wake forMode:NSRunLoopCommonModes];
}
- (void)deliver:(NSDictionary *)result hover:(NSDictionary *)hover serial:(NSUInteger)serial preparing:(BOOL)preparing {
    if(!hover||![self currentSerial:serial]||[hover[@"id"] unsignedIntegerValue]!=_requestID||_stopped)return;
    if(![result[@"verification_pending"] boolValue]) {
        [_provisionalExpiry invalidate];_provisionalExpiry=nil;
        if([result[@"ok"] boolValue]) {_lastValidatedRequestID=_requestID;_provisionalAllowed=YES;}
    }
    NSMutableDictionary *meta=[result mutableCopy] ?: [NSMutableDictionary dictionary];[meta removeObjectForKey:@"pixels"];[meta removeObjectForKey:@"completed_mappings"];
    meta[@"requested_us"]=hover[@"time"];meta[@"preparing"]=@(preparing);
    meta[@"elapsed_ms"]=@((ServiceNow()-[hover[@"started"] doubleValue])*1000);
    VLCThumbnailCompletion callback=hover[@"completion"];
    callback([result[@"ok"] boolValue]?ImageForResponse(result):nil,meta);
    VLCTimelineTrace(@{@"event":@"service",@"generation":_context[@"generation"] ?: @"",@"result":meta});
}
// At most one cache-validation chain and one extraction/identity chain submit
// here. No media IO or blocked child wait occupies the cache coordinator.
- (void)verifyURL:(NSURL *)url policy:(NSString *)policy serial:(NSUInteger)serial completion:(void (^)(NSDictionary *))completion {
    dispatch_async(_metadataQueue, ^{@autoreleasepool {
        double begin=ServiceNow();
        NSDictionary *state=[self currentSerial:serial]?[self.identityWorker fingerprintURL:url policy:policy]:@{@"error":@"cancelled"};
        if(![state[@"ok"] boolValue]&&![state[@"error"] isEqual:@"cancelled"]) {
            NSMutableDictionary *failure=[state mutableCopy];failure[@"source_verification_failed"]=@YES;state=failure;
        }
        VLCTimelineTrace(@{@"event":[policy isEqual:@"stat"]?@"identity-stat":@"identity-fingerprint",@"started":@(begin),@"elapsed_ms":@((ServiceNow()-begin)*1000),@"ok":@([state[@"ok"] boolValue]),@"error":state[@"error"] ?: @""});
        dispatch_async(self.queue, ^{completion([self currentSerial:serial]?state:@{@"error":@"cancelled"});});
    }});
}
- (NSDictionary *)cacheResult:(NSDictionary *)hit time:(int64_t)time ordinal:(NSInteger)ordinal {
    NSDictionary *answer=hit?DecodeResponse(hit[@"raw"],[HeaderTime(hit[@"raw"]) longLongValue],ordinal):nil;
    if(!answer)return nil;
    NSMutableDictionary *result=[answer mutableCopy];result[@"cache"]=hit[@"cache"];result[@"requested_us"]=@(time);
    for(NSString *field in @[@"bytes_read",@"read_calls",@"seek_calls",@"open_count",@"request_bytes_read",@"request_read_calls",@"request_seek_calls",@"operation_us"])result[field]=@0;
    return result;
}
// Main-thread context-wide failures must also clear an image owned by a newer
// hover than the request which discovered the failure.
- (void)sourceFailure:(NSDictionary *)failure serial:(NSUInteger)serial {
    if(![self currentSerial:serial]||_stopped||[failure[@"error"] isEqual:@"cancelled"])return;
    _provisionalAllowed=NO;
    _hoverSatisfied=NO;
    _cacheResolvedHit=NO;_pendingCacheValidation=nil;
    [_provisionalExpiry invalidate];_provisionalExpiry=nil;
    if([failure[@"error"] isEqual:@"media_changed"]) {
        self.invalidatedGeneration=_context[@"generation"];_scheduler=nil;
        _hoverSatisfied=YES;_cacheIntentPending=NO;_pendingCacheValidation=nil;
        [_decoder invalidate];[_identityWorker invalidate];
    }
    NSMutableDictionary *result=[failure mutableCopy];result[@"verification_pending"]=@NO;
    [self deliver:result hover:_hover serial:serial preparing:NO];
}
- (void)deliverProvisional:(NSDictionary *)result hover:(NSDictionary *)hover serial:(NSUInteger)serial {
    if(!_provisionalAllowed||_hoverSatisfied||_lastValidatedRequestID==[hover[@"id"] unsignedIntegerValue]||
       ![self currentSerial:serial]||[hover[@"id"] unsignedIntegerValue]!=_requestID||
       [_invalidatedGeneration isEqual:_context[@"generation"]])return;
    // This deadline belongs to the unresolved source check, not pointer movement.
    // Queue wait counts too; a later queued 15 s operation cannot prolong it.
    if(!_provisionalExpiry) {
        __weak typeof(self) weakSelf=self;
        _provisionalExpiry=[NSTimer timerWithTimeInterval:15 repeats:NO block:^(NSTimer *timer){(void)timer;
            typeof(self) owner=weakSelf;if(!owner)return;
            owner.provisionalExpiry=nil;
            [owner sourceFailure:@{@"error":@"timeout"} serial:serial];
        }];
        [NSRunLoop.mainRunLoop addTimer:_provisionalExpiry forMode:NSRunLoopCommonModes];
    }
    NSMutableDictionary *preview=[result mutableCopy];preview[@"verification_pending"]=@YES;
    [self deliver:preview hover:hover serial:serial preparing:YES];
}
- (void)pumpCacheValidation {
    if(_validationRunning||!_pendingCacheValidation||_stopped)return;
    NSDictionary *intent=_pendingCacheValidation;_pendingCacheValidation=nil;_validationRunning=YES;
    NSDictionary *context=intent[@"context"],*hover=intent[@"hover"];
    NSUInteger serial=[intent[@"serial"] unsignedIntegerValue];
    dispatch_async(_queue, ^{
        [self verifyURL:context[@"url"] policy:@"stat" serial:serial completion:^(NSDictionary *state){
            NSDictionary *failure=nil;
            if(![state[@"ok"] boolValue])failure=state;
            else if(![state[@"stat_identity"] isEqual:intent[@"state"]])failure=@{@"error":@"media_changed"};
            dispatch_async(dispatch_get_main_queue(), ^{
                self.validationRunning=NO;
                if([self currentSerial:serial]&&!self.stopped) {
                    if(failure) [self sourceFailure:failure serial:serial];
                    else if(![self.invalidatedGeneration isEqual:context[@"generation"]]) {
                        self.provisionalAllowed=YES;
                        if([hover[@"id"] unsignedIntegerValue]==self.requestID&&!self.hoverSatisfied) {
                            BOOL exact=[intent[@"exact"] boolValue];
                            if(exact)self.hoverSatisfied=YES;
                            else self.cacheResolvedHit=NO;
                            NSMutableDictionary *validated=[intent[@"result"] mutableCopy];validated[@"verification_pending"]=@NO;
                            [self deliver:validated hover:hover serial:serial preparing:!exact];
                        }
                    }
                }
                [self pumpCacheValidation];[self pumpCachedPresentation];[self pump];
            });
        }];
    });
}
- (void)pumpCachedPresentation {
    if(_cacheRunning||!_cacheIntentPending||!_hover||_hoverSatisfied||!_context||_stopped)return;
    _cacheIntentPending=NO;_cacheRunning=YES;
    NSDictionary *hover=_hover,*context=_context;NSUInteger serial=_contextSerial;
    dispatch_async(_queue, ^{@autoreleasepool {
        NSDictionary *result=nil,*resident=nil;BOOL exact=NO;NSString *state=nil;
        if([self currentSerial:serial]&&self.verifiedIdentity&&![self.invalidatedGeneration isEqual:context[@"generation"]]) {
            int64_t time=[hover[@"time"] longLongValue];
            int64_t distance=VLCThumbnailBridgeDistance([context[@"duration"] longLongValue]);
            // Read resident bytes before ordinary lookup can promote a disk entry.
            NSDictionary *ram=[self.cache residentLookupTime:time maximumDistance:distance];
            resident=[self cacheResult:ram time:time ordinal:[context[@"videoOrdinal"] integerValue]];
            NSDictionary *hit=[self.cache lookupTime:time maximumDistance:-1];exact=hit!=nil;
            if(!hit)hit=[self.cache lookupTime:time maximumDistance:distance];
            result=[self cacheResult:hit time:time ordinal:[context[@"videoOrdinal"] integerValue]];
            state=self.verifiedState;
        }
        dispatch_async(dispatch_get_main_queue(), ^{
            self.cacheRunning=NO;
            if([self currentSerial:serial]&&!self.stopped&&!self.hoverSatisfied&&[hover[@"id"] unsignedIntegerValue]==self.requestID&&
               ![self.invalidatedGeneration isEqual:context[@"generation"]]) {
                self.cacheResolvedRequestID=self.requestID;self.cacheResolvedHit=result!=nil;
                if(resident)[self deliverProvisional:resident hover:hover serial:serial];
                if(result&&state) {
                    self.pendingCacheValidation=@{@"context":context,@"hover":hover,@"serial":@(serial),@"state":state,@"result":result,@"exact":@(exact)};
                    [self pumpCacheValidation];
                }
            }
            [self pumpCachedPresentation];[self pump];
        });
    }});
}
// Coordinator continuation after the context has a qualified identity and a
// fresh pre-operation state. Every asynchronous boundary rechecks the generation.
- (void)performQualifiedTime:(int64_t)time context:(NSDictionary *)context serial:(NSUInteger)serial hover:(NSDictionary *)hover before:(NSString *)before newIdentity:(BOOL)newIdentity completion:(void (^)(NSDictionary *))finish {
    if(![self activeContext:context serial:serial]){finish(@{@"error":@"cancelled"});return;}
    NSURL *url=context[@"url"];
    int64_t duration=[context[@"duration"] longLongValue];NSInteger ordinal=[context[@"videoOrdinal"] integerValue];
    NSDictionary *hit=[_cache lookupTime:time maximumDistance:-1];
    NSDictionary *answer=[self cacheResult:hit time:time ordinal:ordinal];
    if(answer) {
        [self verifyURL:url policy:@"stat" serial:serial completion:^(NSDictionary *after){
            if(![self activeContext:context serial:serial]){finish(@{@"error":@"cancelled"});return;}
            if(![after[@"ok"] boolValue]){finish(after);return;}
            if(![before isEqual:after[@"stat_identity"]]){finish(@{@"error":@"media_changed"});return;}
            NSMutableDictionary *result=[answer mutableCopy];if(newIdentity)result[@"completed_mappings"]=[self.cache completedMappings];finish(result);
        }];
        return;
    }
    // The separate cache path owns nearby presentation; extraction does not
    // duplicate its validation or provisional callbacks.
    dispatch_async(_decodeQueue, ^{@autoreleasepool {
        NSDictionary *decoded=[self activeContext:context serial:serial]?[self.decoder requestURL:url videoOrdinal:ordinal videoCount:[context[@"videoCount"] integerValue] time:time]:@{@"error":@"cancelled"};
        dispatch_async(self.queue, ^{@autoreleasepool {
            if(![self activeContext:context serial:serial]){finish(@{@"error":@"cancelled"});return;}
            if(!decoded[@"raw"]){finish(decoded);return;}
            NSDictionary *reply=DecodeResponse(decoded[@"raw"],time,ordinal);
            if(![reply[@"ok"] boolValue]){finish(@{@"error":@"worker-protocol"});return;}
            if(duration>0&&[reply[@"actual_us"] longLongValue]>=duration){finish(@{@"error":@"unknown_timing"});return;}
            [self verifyURL:url policy:@"stat" serial:serial completion:^(NSDictionary *after){
                if(![self activeContext:context serial:serial]){finish(@{@"error":@"cancelled"});return;}
                if(![after[@"ok"] boolValue]){finish(after);return;}
                if(![before isEqual:after[@"stat_identity"]]){finish(@{@"error":@"media_changed"});return;}
                [self.cache storeRaw:decoded[@"raw"] requestedTime:time actualTime:[reply[@"actual_us"] longLongValue] allowEviction:hover!=nil];
                NSMutableDictionary *result=[reply mutableCopy];result[@"cache"]=@"miss";
                result[@"cache_capacity"]=@([self.cache hasCapacity]);result[@"cache_metrics"]=[self.cache metrics];
                if(newIdentity)result[@"completed_mappings"]=[self.cache completedMappings];finish(result);
            }];
        }});
    }});
}
- (void)performTime:(int64_t)time context:(NSDictionary *)context serial:(NSUInteger)serial hover:(NSDictionary *)hover completion:(void (^)(NSDictionary *))finish {
    NSURL *url=context[@"url"];
    if(!url.isFileURL||![self activeContext:context serial:serial]){finish(@{@"error":@"cancelled"});return;}
    [self verifyURL:url policy:@"stat" serial:serial completion:^(NSDictionary *state){
        if(![self activeContext:context serial:serial]){finish(@{@"error":@"cancelled"});return;}
        if(![state[@"ok"] boolValue]){finish(state);return;}
        NSString *before=state[@"stat_identity"];
        if(self.verifiedState&&![self.verifiedState isEqual:before]) {
            self.verifiedIdentity=nil;self.verifiedState=nil;[self.decoder invalidate];finish(@{@"error":@"media_changed"});return;
        }
        if(self.verifiedIdentity) {
            [self performQualifiedTime:time context:context serial:serial hover:hover before:before newIdentity:NO completion:finish];return;
        }
        [self verifyURL:url policy:@"sampled" serial:serial completion:^(NSDictionary *verified){
            if(![self activeContext:context serial:serial]){finish(@{@"error":@"cancelled"});return;}
            if(![verified[@"ok"] boolValue]){finish(verified);return;}
            if(![before isEqual:verified[@"stat_identity"]]){finish(@{@"error":@"media_changed"});return;}
            self.verifiedState=before;
            self.verifiedIdentity=[NSString stringWithFormat:@"v4:keyframe-countguard2:transform1:%@:%@:%@:%@:%@:%@",url.absoluteString,before,@"sampled",verified[@"fingerprint"],context[@"videoOrdinal"],context[@"videoCount"]];
            [self.cache selectIdentity:self.verifiedIdentity];
            [self performQualifiedTime:time context:context serial:serial hover:hover before:before newIdentity:YES completion:finish];
        }];
    }];
}
- (void)pump {
    if(_running||_stopped||!_context)return;
    double now=ServiceNow();BOOL demand=_hover&&!_hoverSatisfied;
    // Only local lookup gates the next demand. A pending cache validation does
    // not reserve the extraction slot: background coverage can keep progressing,
    // and a newer known cache miss can be dispatched independently.
    if(demand&&_cacheResolvedRequestID!=_requestID)return;
    NSDictionary *hover=demand&&!_cacheResolvedHit?_hover:nil;
    NSDictionary *failure=hover?_failures[hover[@"time"]]:nil;
    if([failure[@"terminal"] boolValue]) { [self deliver:failure hover:hover serial:_contextSerial preparing:NO];_hoverSatisfied=YES;hover=nil;demand=NO; }
    double ready=hover?[failure[@"retry_at"] doubleValue]:0;
    NSNumber *target=nil;
    if(hover&&now>=ready)target=hover[@"time"];
    else if(now>=_nextBackground)target=[_scheduler nextTargetNear:_hover?[_hover[@"time"] longLongValue]:-1 now:now];
    if(!target) {
        double later=0;if(hover)later=MAX(now+.05,ready);
        if(_scheduler&&_nextBackground>now)later=later?MIN(later,_nextBackground):_nextBackground;
        // Finite polling covers a deferred coverage gap; completed plans stay idle.
        if(!later&&[_scheduler.diagnostics[@"deferred"] unsignedIntegerValue])later=now+1;
        if(later)[self wakeAt:later];return;
    }
    BOOL isHover=hover&&[target isEqual:hover[@"time"]];if(!isHover)hover=nil;
    NSDictionary *context=_context;NSUInteger serial=_contextSerial;_running=YES;double start=now;
    VLCTimelineTrace(@{@"event":@"dispatch",@"time_us":target,@"hover":@(isHover),@"generation":context[@"generation"]});
    dispatch_async(_queue, ^{@autoreleasepool {
        [self performTime:target.longLongValue context:context serial:serial hover:hover completion:^(NSDictionary *result) {
        dispatch_async(dispatch_get_main_queue(), ^{
            self.running=NO;
            if([self activeContext:context serial:serial]&&!self.stopped) {
                if(result[@"completed_mappings"]) {
                    NSMutableDictionary *maps=[NSMutableDictionary dictionary];
                    for(NSString *key in result[@"completed_mappings"]) maps[@(key.longLongValue)]=result[@"completed_mappings"][key];
                    [self.scheduler loadCompletedMappings:maps];
                }
                BOOL ok=[result[@"ok"] boolValue];
                if(ok) {
                    [self.scheduler markTarget:target.longLongValue actual:[result[@"actual_us"] longLongValue]];
                    [self.failures removeObjectForKey:target];self.completed++;
                    if(result[@"cache_capacity"]&&![result[@"cache_capacity"] boolValue])self.scheduler=nil;
                    if(isHover&&[hover[@"id"] unsignedIntegerValue]==self.requestID)self.hoverSatisfied=YES;
                } else {
                    NSUInteger count=[self.failures[target][@"attempts"] unsignedIntegerValue]+1;
                    NSString *error=result[@"error"] ?: @"decode-unavailable";
                    BOOL terminal=Terminal(error)||count>=3;
                    double retry=ServiceNow()+(count==1?1:3);
                    // A sweep of failed arbitrary targets must not grow session state.
                    if(self.failures.count>=1024&&!self.failures[target]) {
                        NSNumber *oldest=nil;double age=DBL_MAX;
                        for(NSNumber *key in self.failures) {
                            double timestamp=[self.failures[key][@"last"] doubleValue];
                            if(timestamp<age){age=timestamp;oldest=key;}
                        }
                        if(oldest)[self.failures removeObjectForKey:oldest];
                    }
                    self.failures[target]=@{@"attempts":@(count),@"retry_at":@(retry),@"terminal":@(terminal),@"last":@(ServiceNow()),@"error":error};
                    [self.scheduler deferTarget:target.longLongValue until:retry permanent:terminal];
                    if(Terminal(error))self.scheduler=nil;
                    if([error isEqual:@"media_changed"]||[result[@"source_verification_failed"] boolValue])
                        [self sourceFailure:result serial:serial];
                }
                if(![result[@"error"] isEqual:@"media_changed"]&&![result[@"source_verification_failed"] boolValue])
                    [self deliver:result hover:hover serial:serial preparing:!ok&&![self.failures[target][@"terminal"] boolValue]];
                double pause=MAX(.25,ServiceNow()-start);
                if(NSProcessInfo.processInfo.thermalState>=NSProcessInfoThermalStateSerious)pause=MAX(pause,2);
                self.nextBackground=ServiceNow()+pause;
            }
            self.cacheIntentPending=self.hover&&!self.hoverSatisfied&&![self.invalidatedGeneration isEqual:self.context[@"generation"]]&&
                !(self.cacheResolvedRequestID==self.requestID&&self.cacheResolvedHit);
            [self pumpCachedPresentation];[self pump];
        });
        }];
    }});
}
@end
