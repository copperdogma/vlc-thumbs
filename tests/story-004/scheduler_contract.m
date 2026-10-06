// SPDX-License-Identifier: GPL-2.0-or-later
#import <Foundation/Foundation.h>
#import "VLCThumbnailScheduler.h"
#include <limits.h>

static NSUInteger failures;
static void Check(BOOL condition, const char *name)
{
    if (!condition) { failures++; fprintf(stderr, "FAIL: %s\n", name); }
}
static int64_t Pick(VLCThumbnailScheduler *scheduler, int64_t hover, double now)
{
    NSNumber *number = [scheduler nextTargetNear:hover now:now];
    return number ? number.longLongValue : -1;
}

int main(void) { @autoreleasepool {
    const int64_t second = 1000000;
    VLCThumbnailScheduler *s = [[VLCThumbnailScheduler alloc] initWithDuration:100*second];
    // Half-second rounding makes odd eighths 12.5, 37.5, etc.
    int64_t exactSeven[] = {50000000,25000000,75000000,12500000,
                            37500000,62500000,87500000};
    Check(s.targets.count == 7, "100-second coarse plan has seven targets");
    for (NSUInteger i=0; i<7; i++) {
        Check(s.targets[i].longLongValue == exactSeven[i], "dyadic breadth-first target order");
        Check(Pick(s,-1,0) == exactSeven[i], "empty coverage fills largest gap with earlier tie");
        [s markTarget:exactSeven[i] actual:exactSeven[i]];
    }
    Check(Pick(s,-1,0) == -1 && s.completedCount == 7,
          "completed coverage stops even with no retained images");

    s = [[VLCThumbnailScheduler alloc] initWithDuration:100*second];
    [s loadCompletedMappings:@{@(50000000):@(45000000), @(25000000):@(22000000)}];
    Check(s.completedCount == 2 && Pick(s,-1,0) == 75000000,
          "preloaded actual sample positions, rather than request positions, anchor gaps");
    Check([s.diagnostics[@"actualSamples"] unsignedIntegerValue] == 2,
          "preloaded mappings retain actual anchors");

    s = [[VLCThumbnailScheduler alloc] initWithDuration:100*second];
    [s markTarget:50000000 actual:50000000];
    Check(Pick(s,50000000,0) == 37500000, "hover tie initially favors earlier side");
    Check(Pick(s,50000000,0) == 62500000, "hover tie alternates to later side");

    s = [[VLCThumbnailScheduler alloc] initWithDuration:100*second];
    Check(Pick(s,5000000,0) == 12500000, "hover begins at nearest planned point");
    [s markTarget:12500000 actual:12500000];
    Check(Pick(s,5000000,0) == 25000000, "hover expands outward");
    [s markTarget:25000000 actual:25000000];
    Check(Pick(s,5000000,0) == 37500000, "hover remains local before fairness turn");
    [s markTarget:37500000 actual:37500000];
    Check(Pick(s,5000000,0) == 62500000, "fourth selection fills largest distant gap");

    s = [[VLCThumbnailScheduler alloc] initWithDuration:100*second];
    Check(Pick(s,95000000,0) == 87500000, "hover near end begins on the right");
    [s markTarget:87500000 actual:87500000];
    Check(Pick(s,95000000,0) == 75000000, "right-edge hover expands inward");
    s = [[VLCThumbnailScheduler alloc] initWithDuration:100*second];
    Check(Pick(s,0,0) == 12500000, "hover at start chooses first nearby point");

    s = [[VLCThumbnailScheduler alloc] initWithDuration:100*second];
    [s deferTarget:50000000 until:10 permanent:NO];
    Check(Pick(s,-1,9) == 37500000, "clock deferral allows another gap");
    Check(Pick(s,-1,10) == 50000000, "deferred target returns at deadline");
    [s deferTarget:50000000 until:0 permanent:YES];
    Check(Pick(s,-1,20) == 37500000, "permanent unsupported target is skipped");
    [s markTarget:25000000 actual:24000000];
    Check(Pick(s,-1,20) != 25000000, "successful alias never regenerates target");

    s = [[VLCThumbnailScheduler alloc] initWithDuration:INT64_MAX];
    Check(s.targets.count == 255, "huge duration obeys finite 255-target cap");
    NSMutableSet<NSNumber *> *unique = [NSMutableSet set];
    for (NSNumber *number in s.targets) {
        int64_t t = number.longLongValue;
        Check(t > 0 && t < INT64_MAX && t % 500000 == 0, "huge target stays interior and quantized");
        [unique addObject:number];
    }
    Check(unique.count == s.targets.count, "huge plan contains unique targets");
    for (int64_t duration=0; duration<=1000000; duration+=250000) {
        s = [[VLCThumbnailScheduler alloc] initWithDuration:duration];
        for (NSNumber *number in s.targets)
            Check(number.longLongValue > 0 && number.longLongValue < duration,
                  "tiny plan targets remain interior");
        Check(s.targets.count <= 1, "tiny plan respects half-second spacing");
    }

    s = [[VLCThumbnailScheduler alloc] initWithDuration:3600*second];
    NSUInteger planned = s.targets.count;
    NSMutableSet<NSNumber *> *visited = [NSMutableSet set];
    for (NSUInteger i=0; i<planned; i++) {
        int64_t target = Pick(s,-1,0);
        Check(target >= 0 && ![visited containsObject:@(target)], "finite full coverage selects unique target");
        if (target < 0) break;
        [visited addObject:@(target)];
        [s markTarget:target actual:target-100000];
    }
    Check(visited.count == planned && Pick(s,-1,0) == -1,
          "all planned targets complete exactly once despite shifted actual times");
    if (failures) return 1;
    puts("PASS: scheduler contract");
    return 0;
} }
