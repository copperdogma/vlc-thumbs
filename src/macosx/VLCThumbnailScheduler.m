// SPDX-License-Identifier: GPL-2.0-or-later
#import "VLCThumbnailScheduler.h"
#include <math.h>
#include <limits.h>

static const int64_t kQuantum = 500000; // half-second interior grid

@interface VLCThumbnailScheduler ()
@property (nonatomic, readwrite) int64_t duration;
@property (nonatomic, copy, readwrite) NSArray<NSNumber *> *targets;
@property (nonatomic, readwrite) NSUInteger backgroundSelectionCount;
@property (nonatomic) BOOL preferEarlierOnTie;
@property (nonatomic, strong) NSMutableSet<NSNumber *> *completed;
@property (nonatomic, strong) NSMutableSet<NSNumber *> *actualSamples;
@property (nonatomic, strong) NSMutableSet<NSNumber *> *permanent;
@property (nonatomic, strong) NSMutableDictionary<NSNumber *, NSNumber *> *deferredUntil;
@end

@implementation VLCThumbnailScheduler

- (instancetype)initWithDuration:(int64_t)duration
{
    self = [super init];
    if (!self) return nil;
    _duration = MAX((int64_t)0, duration);
    _completed = [NSMutableSet set];
    _actualSamples = [NSMutableSet set];
    _permanent = [NSMutableSet set];
    _deferredUntil = [NSMutableDictionary dictionary];
    _preferEarlierOnTie = YES;

    // Choose the nearest complete dyadic level to roughly one target/30 s.
    // The seven-point minimum yields broad early coverage on short media;
    // half-second quantization and the 255-point ceiling bound every plan.
    long double desired = (long double)_duration / 30000000.0L;
    NSUInteger levelCount = 7;
    long double error = fabsl(desired - 7.0L);
    for (NSUInteger candidate = 15; candidate <= 255; candidate = candidate * 2 + 1) {
        long double nextError = fabsl(desired - (long double)candidate);
        if (nextError < error) { levelCount = candidate; error = nextError; }
    }
    uint64_t available = _duration > 0 ? ((uint64_t)_duration - 1) / (uint64_t)kQuantum : 0;
    NSUInteger limit = (NSUInteger)MIN((uint64_t)levelCount, available);
    NSMutableArray<NSNumber *> *plan = [NSMutableArray arrayWithCapacity:limit];
    NSMutableSet<NSNumber *> *seen = [NSMutableSet setWithCapacity:limit];
    for (NSUInteger level = 1; level <= 8 && plan.count < limit; level++) {
        int64_t denominator = (int64_t)1 << level;
        for (int64_t numerator = 1; numerator < denominator && plan.count < limit; numerator += 2) {
            // duration*numerator/denominator without overflowing int64_t.
            int64_t raw = (_duration / denominator) * numerator
                        + ((_duration % denominator) * numerator) / denominator;
            int64_t bucket = raw / kQuantum + ((raw % kQuantum) >= kQuantum / 2);
            if (bucket > INT64_MAX / kQuantum) continue;
            int64_t target = bucket * kQuantum;
            NSNumber *number = @(target);
            if (target <= 0 || target >= _duration || [seen containsObject:number]) continue;
            [seen addObject:number];
            [plan addObject:number];
        }
    }
    _targets = [plan copy];
    return self;
}

- (NSUInteger)completedCount { return self.completed.count; }

- (void)markTarget:(int64_t)target actual:(int64_t)actual
{
    NSNumber *number = @(target);
    if ([self.targets containsObject:number]) {
        [self.completed addObject:number];
        [self.deferredUntil removeObjectForKey:number];
        [self.permanent removeObject:number];
    }
    if (actual > 0 && actual < self.duration) [self.actualSamples addObject:@(actual)];
}

- (void)loadCompletedMappings:(NSDictionary<NSNumber *,NSNumber *> *)mappings
{
    for (NSNumber *target in mappings) {
        NSNumber *actual = mappings[target];
        if (![target isKindOfClass:NSNumber.class] || ![actual isKindOfClass:NSNumber.class]) continue;
        [self markTarget:target.longLongValue actual:actual.longLongValue];
    }
}

- (void)deferTarget:(int64_t)target until:(double)monotonic permanent:(BOOL)terminal
{
    NSNumber *number = @(target);
    if (![self.targets containsObject:number] || [self.completed containsObject:number]) return;
    if (terminal) {
        [self.permanent addObject:number];
        [self.deferredUntil removeObjectForKey:number];
    } else if (isfinite(monotonic)) {
        [self.permanent removeObject:number];
        self.deferredUntil[number] = @(monotonic);
    }
}

- (NSArray<NSNumber *> *)eligibleAt:(double)now
{
    NSMutableArray<NSNumber *> *eligible = [NSMutableArray array];
    for (NSNumber *target in self.targets) {
        if ([self.completed containsObject:target] || [self.permanent containsObject:target] ||
            [self.actualSamples containsObject:target]) continue;
        NSNumber *until = self.deferredUntil[target];
        if (until && (!isfinite(now) || now < until.doubleValue)) continue;
        [eligible addObject:target];
    }
    return eligible;
}

- (NSNumber *)largestGapTargetFrom:(NSArray<NSNumber *> *)eligible
{
    if (eligible.count == 0) return nil;
    NSMutableArray<NSNumber *> *anchors = [NSMutableArray arrayWithObject:@0];
    [anchors addObjectsFromArray:self.actualSamples.allObjects];
    [anchors addObject:@(self.duration)];
    [anchors sortUsingSelector:@selector(compare:)];
    NSNumber *winner = nil;
    int64_t largestWidth = -1, earlierStart = INT64_MAX;
    for (NSUInteger i = 1; i < anchors.count; i++) {
        int64_t left = anchors[i-1].longLongValue, right = anchors[i].longLongValue;
        int64_t width = right - left;
        if (width < largestWidth || (width == largestWidth && left >= earlierStart)) continue;
        NSNumber *closest = nil;
        uint64_t bestMidDistance = UINT64_MAX;
        for (NSNumber *point in eligible) {
            int64_t t = point.longLongValue;
            if (t <= left || t >= right) continue;
            // Compare |2*t-left-right| without overflowing signed arithmetic.
            uint64_t twiceLeft = (uint64_t)(t - left);
            uint64_t twiceRight = (uint64_t)(right - t);
            uint64_t distance = twiceLeft >= twiceRight ? twiceLeft - twiceRight : twiceRight - twiceLeft;
            if (!closest || distance < bestMidDistance ||
                (distance == bestMidDistance && t < closest.longLongValue)) {
                closest = point;
                bestMidDistance = distance;
            }
        }
        if (closest) { winner = closest; largestWidth = width; earlierStart = left; }
    }
    return winner;
}

- (NSNumber *)nextTargetNear:(int64_t)hover now:(double)monotonic
{
    NSArray<NSNumber *> *eligible = [self eligibleAt:monotonic];
    if (eligible.count == 0) return nil;
    BOOL global = hover == -1 || ((self.backgroundSelectionCount + 1) % 4 == 0);
    NSNumber *winner = global ? [self largestGapTargetFrom:eligible] : nil;
    if (!winner) {
        int64_t center = MAX((int64_t)0, MIN(hover, self.duration));
        uint64_t bestDistance = UINT64_MAX;
        BOOL hadTie = NO;
        for (NSNumber *point in eligible) {
            int64_t t = point.longLongValue;
            uint64_t distance = t >= center ? (uint64_t)(t - center) : (uint64_t)(center - t);
            if (!winner || distance < bestDistance) {
                winner = point; bestDistance = distance; hadTie = NO;
            } else if (distance == bestDistance) {
                hadTie = YES;
                BOOL pointEarlier = t < center;
                BOOL winnerEarlier = winner.longLongValue < center;
                if (pointEarlier != winnerEarlier && pointEarlier == self.preferEarlierOnTie)
                    winner = point;
                else if (pointEarlier == winnerEarlier && t < winner.longLongValue)
                    winner = point;
            }
        }
        if (hadTie) self.preferEarlierOnTie = !self.preferEarlierOnTie;
    }
    if (winner) self.backgroundSelectionCount++;
    return winner;
}

- (NSDictionary<NSString *,NSNumber *> *)diagnostics
{
    return @{ @"planned": @(self.targets.count), @"completed": @(self.completed.count),
              @"actualSamples": @(self.actualSamples.count), @"permanent": @(self.permanent.count),
              @"deferred": @(self.deferredUntil.count), @"backgroundSelections": @(self.backgroundSelectionCount) };
}
@end
