// SPDX-License-Identifier: GPL-2.0-or-later
#import "VLCThumbnailWorker.h"
#include <poll.h>
#include <signal.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

static double WorkerNow(void) { return NSProcessInfo.processInfo.systemUptime; }
static const NSUInteger PayloadLimit = 320 * 180 * 4;
static BOOL WaitFD(int fd, short events, double deadline)
{
    while (WorkerNow() < deadline) {
        struct pollfd p = {fd, events, 0};
        int remaining = (int)MIN(250, MAX(1, (deadline - WorkerNow()) * 1000));
        int result = poll(&p, 1, remaining);
        if (result > 0) return (p.revents & (events | POLLHUP)) != 0;
        if (result < 0 && errno != EINTR) return NO;
    }
    return NO;
}
@interface VLCThumbnailWorker ()
@property NSString *helperPath;
@property NSString *context;
@property NSTask *task;
@property NSTask *retiring;
@property NSPipe *input;
@property NSPipe *output;
@property NSUInteger epoch;
@property NSUInteger sequence;
@property NSUInteger launches;
@property NSUInteger requests;
@property NSDictionary *ready;
@end
@implementation VLCThumbnailWorker
- (instancetype)initWithHelperPath:(NSString *)path
{
    if ((self = [super init])) _helperPath = [path copy];
    return self;
}
- (void)invalidate
{
    @synchronized(self) {
        _epoch++;
        if (_task.running) kill(_task.processIdentifier, SIGKILL);
        if (_retiring.running) kill(_retiring.processIdentifier, SIGKILL);
    }
}
- (void)closeWorker
{
    NSTask *task;
    @synchronized(self) { task = _task; _task = nil; _context = nil; _ready = nil; }
    if (task.running) kill(task.processIdentifier, SIGKILL);
    // Do not wait indefinitely on a process stuck in kernel filesystem IO.
    // Retain it and refuse another launch until it actually exits.
    double end=WorkerNow()+.5;
    while(task.running && WorkerNow()<end) usleep(1000);
    @synchronized(self) { if(task.running)_retiring=task; }
    @try { [_input.fileHandleForWriting closeFile]; [_output.fileHandleForReading closeFile]; }
    @catch (NSException *exception) { (void)exception; }
    _input = nil; _output = nil;
}
- (NSDictionary *)metrics
{
    @synchronized(self) { return @{@"launched":@(_launches), @"worker_requests":@(_requests),
                                   @"worker_ready":@(_task.running && _ready != nil)}; }
}
- (BOOL)unchanged:(NSUInteger)epoch
{
    @synchronized(self) { return _epoch == epoch; }
}
- (NSData *)readBytes:(NSUInteger)length deadline:(double)deadline epoch:(NSUInteger)epoch
{
    NSMutableData *data = [NSMutableData dataWithLength:length];
    NSUInteger offset = 0; int fd = _output.fileHandleForReading.fileDescriptor;
    while (offset < length && [self unchanged:epoch]) {
        if (!WaitFD(fd, POLLIN, deadline)) return nil;
        ssize_t n = read(fd, (uint8_t *)data.mutableBytes + offset, length - offset);
        if (n > 0) offset += n;
        else if (n == 0 || (errno != EINTR && errno != EAGAIN)) return nil;
    }
    return offset == length ? data : nil;
}
- (NSDictionary *)readReply:(double)deadline epoch:(NSUInteger)epoch
{
    NSMutableData *line = [NSMutableData data];
    // Bounded header, including when a faulty process never emits a newline.
    for (NSUInteger i = 0; i < 4096; i++) {
        NSData *byte = [self readBytes:1 deadline:deadline epoch:epoch];
        if (!byte) return nil;
        if (*(const uint8_t *)byte.bytes == '\n') {
            id header = [NSJSONSerialization JSONObjectWithData:line options:0 error:nil];
            if (![header isKindOfClass:NSDictionary.class] ||
                ![header[@"version"] isKindOfClass:NSNumber.class] || ![header[@"version"] isEqualToNumber:@3] ||
                ![header[@"ok"] isKindOfClass:NSNumber.class]) return nil;
            NSNumber *size = header[@"payload_bytes"];
            if (size && (![size isKindOfClass:NSNumber.class] || size.longLongValue < 0 || size.unsignedLongLongValue > PayloadLimit)) return nil;
            NSUInteger length = size.unsignedIntegerValue;
            if (![header[@"ok"] boolValue] && (length || ![header[@"error"] isKindOfClass:NSString.class] || [header[@"error"] length]>64)) return nil;
            NSData *payload = [self readBytes:length deadline:deadline epoch:epoch];
            if (!payload) return nil;
            NSMutableData *raw = [line mutableCopy]; [raw appendBytes:"\n" length:1]; [raw appendData:payload];
            return @{@"header":header,@"raw":raw};
        }
        [line appendData:byte];
    }
    return nil;
}
- (NSDictionary *)fingerprintURL:(NSURL *)url policy:(NSString *)policy
{
    [self closeWorker];
    if(_retiring.running)return @{@"error":@"worker-stuck"};
    _retiring=nil;
    NSUInteger epoch; @synchronized(self) { epoch = _epoch; }
    NSTask *task = [NSTask new]; _output = [NSPipe pipe];
    task.launchPath = _helperPath; task.qualityOfService = NSQualityOfServiceUtility;
    task.arguments = @[@"--fingerprint",policy,@"--input",url.path];
    task.standardOutput = _output; task.standardError = [NSFileHandle fileHandleWithNullDevice];
    task.standardInput = [NSFileHandle fileHandleWithNullDevice];
    @synchronized(self) { _task = task; }
    double started = WorkerNow();
    @try { [task launch]; }
    @catch (NSException *exception) { [self closeWorker]; return @{@"error":@"helper-unavailable"}; }
    [_output.fileHandleForWriting closeFile];
    int fd = _output.fileHandleForReading.fileDescriptor;
    fcntl(fd,F_SETFL,fcntl(fd,F_GETFL)|O_NONBLOCK);
    NSDictionary *reply = [self readReply:started+15 epoch:epoch];
    NSDictionary *header = reply[@"header"];
    BOOL valid = [header[@"ok"] boolValue] && [header[@"type"] isEqual:@"identity"] &&
        [header[@"policy"] isEqual:policy] && [header[@"fingerprint"] isKindOfClass:NSString.class] &&
        [header[@"fingerprint"] length] == 64 && [header[@"stat_identity"] isKindOfClass:NSString.class];
    [self closeWorker];
    if (valid) return header;
    return @{@"error":header[@"error"] ?: (![self unchanged:epoch] ? @"cancelled" : WorkerNow()-started>=15 ? @"timeout" : @"worker-protocol")};
}
- (NSDictionary *)requestURL:(NSURL *)url videoOrdinal:(NSInteger)ordinal videoCount:(NSInteger)count time:(int64_t)time
{
    NSUInteger epoch;
    @synchronized(self) { epoch = _epoch; }
    NSString *context = [NSString stringWithFormat:@"%@:%ld:%ld",url.path,(long)ordinal,(long)count];
    double started = WorkerNow();
    if (![_context isEqual:context] || !_task.running || !_ready) {
        [self closeWorker];
        if(_retiring.running)return @{@"error":@"worker-stuck"};
        _retiring=nil;
        if (![self unchanged:epoch]) return @{@"error":@"cancelled"};
        NSTask *task = [NSTask new];
        _input = [NSPipe pipe]; _output = [NSPipe pipe];
        task.launchPath = _helperPath; task.qualityOfService = NSQualityOfServiceUtility;
        task.arguments = @[@"--worker",@"--input",url.path,@"--video-ordinal",@(ordinal).stringValue,
                           @"--video-count",@(count).stringValue,@"--max-width",@"320",@"--max-height",@"180"];
        task.standardInput = _input; task.standardOutput = _output;
        task.standardError = [NSFileHandle fileHandleWithNullDevice];
        @synchronized(self) { _task = task; }
        @try { [task launch]; }
        @catch (NSException *exception) { [self closeWorker]; return @{@"error":@"helper-unavailable"}; }
        // Parent's unused ends must close or worker death won't produce EOF.
        [_input.fileHandleForReading closeFile]; [_output.fileHandleForWriting closeFile];
        int fd = _output.fileHandleForReading.fileDescriptor;
        fcntl(fd, F_SETFL, fcntl(fd,F_GETFL) | O_NONBLOCK);
        @synchronized(self) { _launches++; }
        NSDictionary *startup = [self readReply:WorkerNow()+15 epoch:epoch];
        NSDictionary *header = startup[@"header"];
        if (![header[@"ok"] boolValue] || ![header[@"type"] isEqual:@"ready"] ||
            ![header[@"duration_us"] isKindOfClass:NSNumber.class] || [header[@"duration_us"] longLongValue] <= 0) {
            NSString *error = header[@"error"] ?: (![self unchanged:epoch] ? @"cancelled" : WorkerNow()-started>=15 ? @"timeout" : @"worker-protocol");
            [self closeWorker]; return @{@"error":error};
        }
        _ready = header; _context = context;
    }
    if (![self unchanged:epoch]) { [self closeWorker]; return @{@"error":@"cancelled"}; }
    NSUInteger ident = ++_sequence;
    NSData *command = [[NSString stringWithFormat:@"%lu %lld\n",(unsigned long)ident,time] dataUsingEncoding:NSASCIIStringEncoding];
    int fd = _input.fileHandleForWriting.fileDescriptor;
    // Darwin suppresses SIGPIPE on this descriptor without changing VLC signals.
    fcntl(fd, F_SETNOSIGPIPE, 1);
    ssize_t written;
    do { written = write(fd,command.bytes,command.length); } while(written<0 && errno==EINTR);
    if (written != (ssize_t)command.length) { [self closeWorker]; return @{@"error":@"worker-disconnected"}; }
    @synchronized(self) { _requests++; }
    double requestStarted = WorkerNow();
    NSDictionary *reply = [self readReply:requestStarted+15 epoch:epoch];
    NSDictionary *header = reply[@"header"];
    if (!reply || ![header[@"id"] isKindOfClass:NSNumber.class] || ![header[@"id"] isEqualToNumber:@(ident)] ||
        ![header[@"requested_us"] isKindOfClass:NSNumber.class] || ![header[@"requested_us"] isEqualToNumber:@(time)]) {
        NSString *error = ![self unchanged:epoch] ? @"cancelled" : WorkerNow()-requestStarted>=15 ? @"timeout" : @"worker-protocol";
        [self closeWorker]; return @{@"error":error};
    }
    if (![header[@"ok"] boolValue]) return @{@"error":header[@"error"] ?: @"decode-unavailable", @"header":header};
    return @{@"raw":reply[@"raw"], @"header":header, @"startup":_ready,
             @"worker_elapsed_ms":@((WorkerNow()-started)*1000)};
}
@end
