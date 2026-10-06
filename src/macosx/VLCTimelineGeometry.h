// SPDX-License-Identifier: GPL-2.0-or-later
#ifndef VLC_TIMELINE_GEOMETRY_H
#define VLC_TIMELINE_GEOMETRY_H
#include <stdint.h>
#include <math.h>
#ifdef __OBJC__
#import <AppKit/AppKit.h>
static inline NSRect VLCTimelineHoverBounds(NSSlider *slider)
{
    // Apple recommends 28pt macOS targets; use 32pt for comfortable hover.
    NSRect hit = slider.bounds;
    CGFloat height = MAX(NSHeight(hit), 32.);
    hit.origin.y = NSMidY(hit) - height / 2.; hit.size.height = height;
    if (slider.superview) {
        NSRect parent = [slider convertRect:slider.superview.bounds fromView:slider.superview];
        hit = NSIntersectionRect(hit, parent);
    }
    return hit;
}
static inline BOOL VLCTimelineTrackBounds(NSSlider *slider, double *left, double *right)
{
    // Read the live cell only. VLCSliderCell owns a CVDisplayLink and cannot
    // safely be copied using NSSliderCell's inherited copying implementation.
    NSSliderCell *cell = slider.cell;
    NSRect bar = [cell barRectFlipped:slider.flipped];
    NSRect knob = [cell knobRectFlipped:slider.flipped];
    double width = NSWidth(knob);
    *left = NSMinX(bar) + width / 2.;
    *right = NSMaxX(bar) - width / 2.;
    return isfinite(*left) && isfinite(*right) && width > 0 && *right > *left;
}
#endif
static inline int64_t VLCTimelineTimeForPoint(double x, double left, double right, int64_t duration)
{
    if (!isfinite(x) || !isfinite(left) || !isfinite(right) || right <= left || duration <= 0) return -1;
    double fraction = fmax(0., fmin(1., (x - left) / (right - left)));
    // Final pixel targets the last representable timeline time, not beyond EOF.
    return (int64_t)llround(fraction * (double)(duration - 1));
}
static inline int64_t VLCTimelineBucket(int64_t time, int64_t duration)
{
    if (time < 0 || duration <= 0) return -1;
    int64_t bucket = (int64_t)llround((double)time / 500000.) * 500000;
    return bucket < duration ? bucket : duration - 1;
}
#endif
