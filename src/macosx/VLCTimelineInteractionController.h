// SPDX-License-Identifier: GPL-2.0-or-later
#import <Cocoa/Cocoa.h>
@interface VLCTimelineInteractionController : NSObject
- (instancetype)initWithSlider:(NSSlider *)slider;
- (void)hide;
@end
