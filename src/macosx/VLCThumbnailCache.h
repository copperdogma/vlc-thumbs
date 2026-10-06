// SPDX-License-Identifier: GPL-2.0-or-later
#import <Foundation/Foundation.h>

// Worker-queue confined. Keys describe verified media content and rendering,
// never runtime presentation generations. Disk IO refusal leaves previews usable.
@interface VLCThumbnailCache : NSObject
- (instancetype)initWithRoot:(NSString *)root;
- (void)selectIdentity:(NSString *)identity;
- (NSDictionary *)lookupTime:(int64_t)time maximumDistance:(int64_t)distance;
// Never reads payload bytes from disk or promotes a retained entry into RAM.
// Meaningful hits may update local retention timestamps. Caller qualifies the
// current media identity before using this for provisional presentation.
- (NSDictionary *)residentLookupTime:(int64_t)time maximumDistance:(int64_t)distance;
- (BOOL)storeRaw:(NSData *)raw requestedTime:(int64_t)time actualTime:(int64_t)actual;
// Demand may displace the least-recently-used retained sample/alias. Background
// stores remain finite and refuse overflow without evicting useful work.
// Disk pruning prefers background samples over current-identity demand samples;
// demand retention is bounded by sample capacity and never overrides disk quota.
- (BOOL)storeRaw:(NSData *)raw requestedTime:(int64_t)time actualTime:(int64_t)actual allowEviction:(BOOL)allowEviction;
- (NSDictionary *)completedMappings;
- (BOOL)hasCapacity;
- (NSDictionary *)metrics;
@end
