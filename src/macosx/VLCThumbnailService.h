// SPDX-License-Identifier: GPL-2.0-or-later
#import <Cocoa/Cocoa.h>

typedef void (^VLCThumbnailCompletion)(NSImage *image, NSDictionary *result);

// All public operations and completions are main-thread only. IO/decode work is
// confined to one worker; each call supersedes presentation demand only.
@interface VLCThumbnailService : NSObject
+ (instancetype)sharedService;
- (instancetype)initWithHelperPath:(NSString *)helperPath cacheRoot:(NSString *)cacheRoot;
- (NSUInteger)requestURL:(NSURL *)url generation:(NSString *)generation
     videoOrdinal:(NSInteger)ordinal videoCount:(NSInteger)count time:(int64_t)microseconds
       completion:(VLCThumbnailCompletion)completion;
- (void)prepareContext:(NSDictionary *)context enabled:(BOOL)enabled;
- (void)cancelRequest:(NSUInteger)token;
- (void)cancel;
- (void)shutdown;
- (NSDictionary *)metrics;
@end

// Shared nearby-image limit: half the coarse interval, bounded to 2–60 seconds.
int64_t VLCThumbnailBridgeDistance(int64_t duration);
void VLCTimelineTrace(NSDictionary *event);
