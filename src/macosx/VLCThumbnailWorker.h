// SPDX-License-Identifier: GPL-2.0-or-later
#import <Foundation/Foundation.h>

// All requests are serial-worker operations. Invalidation is safe from main.
// Owns a single bounded private process; never uses the playing VLC input.
@interface VLCThumbnailWorker : NSObject
- (instancetype)initWithHelperPath:(NSString *)path;
- (NSDictionary *)requestURL:(NSURL *)url videoOrdinal:(NSInteger)ordinal
                 videoCount:(NSInteger)count time:(int64_t)time;
- (NSDictionary *)fingerprintURL:(NSURL *)url policy:(NSString *)policy;
- (void)invalidate;
- (NSDictionary *)metrics;
@end
