// SPDX-License-Identifier: GPL-2.0-or-later
#import <Foundation/Foundation.h>
#include <stdint.h>

// All times are media microseconds. Call on one serial owner (normally main).
// This class selects finite background targets; hover demands, pacing, active
// requests and retry budgets belong to the service. There is no reservation:
// call nextTargetNear:now: when dispatching, then mark or defer that target.
@interface VLCThumbnailScheduler : NSObject
@property (nonatomic, readonly) int64_t duration;
@property (nonatomic, copy, readonly) NSArray<NSNumber *> *targets; // breadth-first dyadic order
@property (nonatomic, readonly) NSUInteger completedCount;
@property (nonatomic, readonly) NSUInteger backgroundSelectionCount;

- (instancetype)initWithDuration:(int64_t)duration;
- (void)markTarget:(int64_t)target actual:(int64_t)actual;
- (void)loadCompletedMappings:(NSDictionary<NSNumber *, NSNumber *> *)mappings;
- (void)deferTarget:(int64_t)target until:(double)monotonic permanent:(BOOL)terminal;
// hover == -1 selects global largest-gap coverage. Other values are clamped.
- (NSNumber *)nextTargetNear:(int64_t)hover now:(double)monotonic;
- (NSDictionary<NSString *, NSNumber *> *)diagnostics;
@end
