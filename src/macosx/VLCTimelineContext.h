// SPDX-License-Identifier: GPL-2.0-or-later
#import <Foundation/Foundation.h>
extern NSString * const VLCTimelineContextChanged;
@interface VLCTimelineContext : NSObject
+ (instancetype)sharedContext;
- (NSDictionary *)snapshot;
- (void)refresh;
- (void)invalidate;
@end
