#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>
#import <ImageIO/ImageIO.h>
#import <CoreServices/CoreServices.h>
#include <mach/mach_time.h>

static double monotonicSeconds(void) {
    static mach_timebase_info_data_t tb;
    if (!tb.denom) mach_timebase_info(&tb);
    return (double)mach_absolute_time() * tb.numer / tb.denom / 1e9;
}

int main(int argc, const char **argv) {
    @autoreleasepool {
        if (argc != 3) return 2;
        NSString *path = [NSString stringWithUTF8String:argv[1]];
        NSString *output = [NSString stringWithUTF8String:argv[2]];
        double opened = monotonicSeconds();
        AVURLAsset *asset = [AVURLAsset URLAssetWithURL:[NSURL fileURLWithPath:path] options:nil];
        AVAssetImageGenerator *generator = [[AVAssetImageGenerator alloc] initWithAsset:asset];
        generator.maximumSize = CGSizeMake(320, 180);
        generator.appliesPreferredTrackTransform = YES;
        generator.requestedTimeToleranceBefore = CMTimeMake(1,20);
        generator.requestedTimeToleranceAfter = CMTimeMake(1,20);
        NSArray *times = @[@0.5, @7.25, @2.3, @6.75, @2.3];
        if ([path.lastPathComponent isEqualToString:@"build-smoke.mp4"]) times = @[@0.5, @2.25, @1.3, @1.75, @1.3];
        NSMutableArray *records = [NSMutableArray array];
        int index = 0;
        for (NSNumber *target in times) {
            dispatch_semaphore_t sem = dispatch_semaphore_create(0);
            __block NSDictionary *record = nil;
            double started = monotonicSeconds();
            CMTime request = CMTimeMakeWithSeconds(target.doubleValue, 600);
            NSString *imagePath = [output stringByAppendingPathComponent:[NSString stringWithFormat:@"%@-%d.png",path.lastPathComponent,index]];
            [generator generateCGImagesAsynchronouslyForTimes:@[[NSValue valueWithCMTime:request]] completionHandler:^(CMTime requested, CGImageRef image, CMTime actual, AVAssetImageGeneratorResult result, NSError *error) {
                double elapsed = (monotonicSeconds()-started)*1000.0;
                NSMutableDictionary *r = [@{@"requested_seconds":@(CMTimeGetSeconds(requested)), @"result":@(result), @"elapsed_ms":@(elapsed), @"open_to_callback_ms":@((monotonicSeconds()-opened)*1000.0), @"success":@(result==AVAssetImageGeneratorSucceeded)} mutableCopy];
                if (CMTIME_IS_NUMERIC(actual)) r[@"actual_seconds"] = @(CMTimeGetSeconds(actual));
                if (image) {
                    r[@"width"] = @(CGImageGetWidth(image)); r[@"height"] = @(CGImageGetHeight(image));
                    CGImageDestinationRef dest = CGImageDestinationCreateWithURL((__bridge CFURLRef)[NSURL fileURLWithPath:imagePath],kUTTypePNG,1,NULL);
                    BOOL written = NO;
                    if (dest) { CGImageDestinationAddImage(dest,image,NULL); written = CGImageDestinationFinalize(dest); CFRelease(dest); }
                    r[@"png_written"] = @(written); r[@"image_path"] = imagePath;
                }
                if (error) {r[@"error_domain"] = error.domain; r[@"error_code"] = @(error.code); r[@"error"] = error.localizedDescription;}
                record = r;
                dispatch_semaphore_signal(sem);
            }];
            if (dispatch_semaphore_wait(sem,dispatch_time(DISPATCH_TIME_NOW,5*NSEC_PER_SEC))) {
                [generator cancelAllCGImageGeneration];
                [records addObject:@{@"requested_seconds":target,@"success":@NO,@"timeout":@YES}];
                break;
            }
            [records addObject:record];
            index++;
        }
        NSDictionary *summary = @{@"input":path,@"maximum_width":@320,@"maximum_height":@180,@"tolerance_seconds":@0.05,@"requests":records};
        NSData *data = [NSJSONSerialization dataWithJSONObject:summary options:NSJSONWritingPrettyPrinted error:nil];
        fwrite(data.bytes,1,data.length,stdout); putchar('\n');
    }
    return 0;
}
