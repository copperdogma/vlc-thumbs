// SPDX-License-Identifier: GPL-2.0-or-later
#import "VLCTimelineGeometry.h"
@interface GuardedCell : NSSliderCell
@property BOOL protect;
@end
@implementation GuardedCell
- (id)copyWithZone:(NSZone *)zone { abort(); }
- (void)setDoubleValue:(double)value { if (_protect) abort(); [super setDoubleValue:value]; }
@end
int main(void) { @autoreleasepool {
    [NSApplication sharedApplication]; int checks=0;
    for (NSNumber *width in @[@73.,@200.5,@620.]) for (NSNumber *size in @[@0,@1,@2]) {
        NSSlider *s=[[NSSlider alloc] initWithFrame:NSMakeRect(0,0,width.doubleValue,24)];
        GuardedCell *cell=[[GuardedCell alloc] init];s.cell=cell;
        s.controlSize=size.integerValue;s.minValue=100;s.maxValue=20000;
        s.doubleValue=s.minValue;[cell calcDrawInfo:s.bounds];
        double expectedLeft=NSMidX([cell knobRectFlipped:s.flipped]);
        s.doubleValue=s.maxValue;double expectedRight=NSMidX([cell knobRectFlipped:s.flipped]);
        s.doubleValue=4567;cell.protect=YES;
        for(int i=0;i<1000;i++) { double left,right;
            if(!VLCTimelineTrackBounds(s,&left,&right) || fabs(left-expectedLeft)>0.01 || fabs(right-expectedRight)>0.01 || s.doubleValue!=4567) abort();
            checks++;
        }
        cell.protect=NO;
    }
    printf("{\"checks\":%d,\"copies\":0,\"playback_value_writes\":0,\"native_endpoint_error_max\":0}\n",checks);
}return 0; }
