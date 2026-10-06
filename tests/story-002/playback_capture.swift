// Development-only observer; no VLC control or production integration.
import Foundation
import AppKit
import ScreenCaptureKit
import CoreMedia
import CoreVideo
import AudioToolbox

private let developmentBundleID = "org.videolan.vlc-thumbs.development"
private func seconds(_ t: CMTime) -> Double? {
    let v = CMTimeGetSeconds(t)
    return v.isFinite ? v : nil
}
private func json(_ value: Any) throws -> Data {
    var data = try JSONSerialization.data(withJSONObject: value, options: [.sortedKeys])
    data.append(10)
    return data
}
private func failure(_ message: String) -> NSError {
    NSError(domain: "Story002PlaybackCapture", code: 1, userInfo: [NSLocalizedDescriptionKey: message])
}

private struct Options {
    var pid: pid_t
    var output: URL
    var duration: Double
    var fps: Int
    var roi: [Double]
    var windowID: CGWindowID?
    var rawAudio: Bool
    var displayRect: CGRect?
    var silenceDB: Double
    var ownedDisplayAudio: Bool = false

    static func parse() throws -> Options {
        var values: [String: String] = [:]
        var raw = false
        var ownedDisplayAudio = false
        var i = 1
        while i < CommandLine.arguments.count {
            let key = CommandLine.arguments[i]
            if key == "--owned-display-audio" { ownedDisplayAudio = true; i += 1; continue }
            if key == "--raw-audio" { raw = true; i += 1; continue }
            guard ["--pid", "--output", "--duration", "--fps", "--roi", "--window-id", "--silence-db", "--display-rect"].contains(key), i + 1 < CommandLine.arguments.count else {
                throw failure("Usage: playback-capture --pid PID --output work/... [--duration 65] [--fps 30|60] [--roi x,y,w,h] [--window-id ID] [--raw-audio] [--silence-db -60]")
            }
            guard values[key] == nil else { throw failure("Duplicate argument: \(key)") }
            values[key] = CommandLine.arguments[i + 1]; i += 2
        }
        guard let pid = values["--pid"].flatMap(Int32.init), pid > 0,
              let path = values["--output"] else { throw failure("--pid and --output are required") }
        let duration = Double(values["--duration"] ?? "65") ?? .nan
        let fps = Int(values["--fps"] ?? "30") ?? 0
        let roi = (values["--roi"] ?? "0.2,0.15,0.6,0.35").split(separator: ",").compactMap { Double($0) }
        let silenceDB = Double(values["--silence-db"] ?? "-60") ?? .nan
        guard duration.isFinite, duration > 0, duration <= 65, [30, 60].contains(fps),
              silenceDB.isFinite, silenceDB >= -100, silenceDB <= -20,
              roi.count == 4, roi.allSatisfy({ $0.isFinite && $0 >= 0 }),
              roi[2] > 0, roi[3] > 0, roi[0] + roi[2] <= 1, roi[1] + roi[3] <= 1 else {
            throw failure("Invalid duration (0,65], fps (30/60), silence dB [-100,-20], or normalized ROI")
        }
        let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath).resolvingSymlinksInPath()
        guard FileManager.default.fileExists(atPath: root.appendingPathComponent("tests/story-002/playback_capture.swift").path),
              FileManager.default.fileExists(atPath: root.appendingPathComponent("AGENTS.md").path) else {
            throw failure("Run from the vlc-thumbs workspace root")
        }
        let work = root.appendingPathComponent("work", isDirectory: true).resolvingSymlinksInPath()
        let output = URL(fileURLWithPath: path, relativeTo: root).standardizedFileURL.resolvingSymlinksInPath()
        guard output.path.hasPrefix(work.path + "/") else { throw failure("Output must be confined beneath this workspace's work/") }
        var windowID: CGWindowID? = nil
        if let value = values["--window-id"] {
            guard let id = UInt32(value), id > 0 else { throw failure("Invalid --window-id") }
            windowID = id
        }
        var displayRect: CGRect? = nil
        if let text = values["--display-rect"] {
            let r = text.split(separator: ",").compactMap { Double($0) }
            guard r.count == 4, r.allSatisfy({ $0.isFinite }), r[2] > 0, r[3] > 0, !raw else { throw failure("Invalid display rectangle or incompatible raw audio") }
            displayRect = CGRect(x: r[0], y: r[1], width: r[2], height: r[3])
        }
        return Options(pid: pid, output: output, duration: duration, fps: fps, roi: roi, windowID: windowID, rawAudio: raw, displayRect: displayRect, silenceDB: silenceDB, ownedDisplayAudio: ownedDisplayAudio)
    }
}

private final class Observer: NSObject, SCStreamOutput, SCStreamDelegate, @unchecked Sendable {
    let queue = DispatchQueue(label: "story002.capture.samples")
    let options: Options
    let audioLog: FileHandle
    let screenLog: FileHandle
    let rawAudio: FileHandle?
    let begin = ProcessInfo.processInfo.systemUptime
    var ioError: String?
    var captureError: String?
    var captureErrors: [[String: Any]] = []
    var audioBuffers = 0, audioSamples = 0, screenBuffers = 0, hashedFrames = 0
    var invalidAudio = 0, invalidScreen = 0
    var audioFormats: [[String: Any]] = []
    var lastAudioEnd: Double?, lastAudioArrival: Double?
    var audioGapEvents: [[String: Any]] = [], audioObserverGaps: [[String: Any]] = []
    var screenGapEvents: [[String: Any]] = [], screenObserverGaps: [[String: Any]] = []
    var levelSum = 0.0, levelSamples = 0, levelStart: Double?
    var levelWindows = 0, silentStart: Double?, silentEnd: Double?
    var silentIntervals: [[String: Any]] = []
    var lastScreenPTS: Double?, lastScreenArrival: Double?
    var lastHash: UInt64?, repeatStart: Double?, repeatEnd: Double?
    var repeatedIntervals: [[String: Any]] = []
    var statusCounts: [String: Int] = [:]

    init(options: Options) throws {
        self.options = options
        try FileManager.default.createDirectory(at: options.output, withIntermediateDirectories: true)
        func create(_ name: String) throws -> FileHandle {
            let url = options.output.appendingPathComponent(name)
            guard !FileManager.default.fileExists(atPath: url.path),
                  FileManager.default.createFile(atPath: url.path, contents: nil) else { throw failure("Refusing to overwrite \(url.path)") }
            return try FileHandle(forWritingTo: url)
        }
        guard !FileManager.default.fileExists(atPath: options.output.appendingPathComponent("summary.json").path) else { throw failure("Refusing to overwrite summary.json") }
        audioLog = try create("audio.jsonl")
        screenLog = try create("screen.jsonl")
        rawAudio = options.rawAudio ? try create("audio-mono-f32le.pcm") : nil
        super.init()
    }

    func write(_ event: [String: Any], to file: FileHandle) {
        do { try file.write(contentsOf: json(event)) } catch { ioError = error.localizedDescription }
    }
    func closeSilence() {
        if let start = silentStart, let end = silentEnd {
            silentIntervals.append(["start_pts_s": start, "end_pts_s": end, "duration_s": end - start])
        }
        silentStart = nil; silentEnd = nil
    }
    func closeRepeat(_ reason: String) {
        if let start = repeatStart, let end = repeatEnd, end - start >= 0.1 {
            repeatedIntervals.append(["start_pts_s": start, "end_pts_s": end, "duration_s": end - start,
                                      "end_reason": reason, "classification": "unchanged_roi_candidate_not_vlc_attribution"])
        }
        repeatStart = nil; repeatEnd = nil; lastHash = nil
    }

    func stream(_ stream: SCStream, didStopWithError error: Error) {
        queue.async {
            let e = error as NSError
            self.captureErrors.append(["origin": "delegate", "domain": e.domain, "code": e.code, "message": e.localizedDescription, "uptime_s": ProcessInfo.processInfo.systemUptime])
            if self.captureError == nil { self.captureError = e.localizedDescription }
        }
    }
    func stream(_ stream: SCStream, didOutputSampleBuffer sampleBuffer: CMSampleBuffer, of type: SCStreamOutputType) {
        let arrival = ProcessInfo.processInfo.systemUptime - begin
        if type == .audio { audio(sampleBuffer, arrival: arrival) }
        else if type == .screen { screen(sampleBuffer, arrival: arrival) }
    }

    func audio(_ buffer: CMSampleBuffer, arrival: Double) {
        audioBuffers += 1
        guard buffer.isValid, let pts = seconds(buffer.presentationTimeStamp),
              let description = buffer.formatDescription,
              let format = CMAudioFormatDescriptionGetStreamBasicDescription(description)?.pointee else {
            invalidAudio += 1; write(["kind": "invalid_audio", "arrival_s": arrival], to: audioLog); return
        }
        let frames = CMSampleBufferGetNumSamples(buffer)
        let monoFloat = format.mFormatID == kAudioFormatLinearPCM && format.mBitsPerChannel == 32 &&
            format.mChannelsPerFrame == 1 && (format.mFormatFlags & kAudioFormatFlagIsFloat) != 0 &&
            (format.mFormatFlags & kAudioFormatFlagIsBigEndian) == 0 && format.mSampleRate > 0
        let metadata: [String: Any] = ["sample_rate": format.mSampleRate, "channels": format.mChannelsPerFrame,
            "bits_per_channel": format.mBitsPerChannel, "format_id": format.mFormatID, "format_flags": format.mFormatFlags,
            "rms_supported": monoFloat]
        if audioFormats.isEmpty || NSDictionary(dictionary: audioFormats.last!) != NSDictionary(dictionary: metadata) {
            audioFormats.append(metadata); write(["kind": "format", "format": metadata], to: audioLog)
        }
        let duration = Double(frames) / format.mSampleRate
        let gap = lastAudioEnd.map { pts - $0 } ?? 0
        let observerGap = lastAudioArrival.map { arrival - $0 } ?? 0
        if abs(gap) > 0.002 {
            audioGapEvents.append(["pts_s": pts, "gap_s": gap, "classification": "capture_timestamp_discontinuity"])
            closeSilence(); levelSum = 0; levelSamples = 0; levelStart = nil
        }
        if observerGap > max(0.1, duration * 3) {
            audioObserverGaps.append(["arrival_s": arrival, "gap_s": observerGap])
        }
        lastAudioEnd = pts + duration; lastAudioArrival = arrival
        write(["kind": "buffer", "pts_s": pts, "arrival_s": arrival, "frames": frames,
               "duration_s": duration, "pts_gap_s": gap, "observer_gap_s": observerGap], to: audioLog)
        guard monoFloat else { invalidAudio += 1; return }
        let windowFrames = max(1, Int((format.mSampleRate * 0.01).rounded()))
        do {
            try buffer.withAudioBufferList { list, _ in
                guard list.count == 1, let data = list[0].mData,
                      Int(list[0].mDataByteSize) >= frames * MemoryLayout<Float>.size else {
                    throw failure("Unexpected mono PCM AudioBufferList")
                }
                if let rawAudio { try rawAudio.write(contentsOf: Data(bytes: data, count: frames * MemoryLayout<Float>.size)) }
                let samples = data.assumingMemoryBound(to: Float.self)
                for index in 0..<frames {
                    let value = Double(samples[index])
                    guard value.isFinite else { throw failure("Nonfinite PCM sample") }
                    if levelSamples == 0 { levelStart = pts + Double(index) / format.mSampleRate }
                    levelSum += value * value; levelSamples += 1
                    if levelSamples == windowFrames, let start = levelStart {
                        let rms = sqrt(levelSum / Double(levelSamples))
                        let db = max(-200.0, 20 * log10(max(rms, 1e-10)))
                        let end = start + Double(levelSamples) / format.mSampleRate
                        let silent = db < options.silenceDB
                        if silent { if silentStart == nil { silentStart = start }; silentEnd = end }
                        else { closeSilence() }
                        write(["kind": "rms_10ms", "pts_s": start, "duration_s": end - start,
                               "rms": rms, "dbfs": db, "below_threshold": silent], to: audioLog)
                        levelWindows += 1; levelSum = 0; levelSamples = 0; levelStart = nil
                    }
                }
                audioSamples += frames
            }
        } catch { invalidAudio += 1; write(["kind": "audio_analysis_error", "message": error.localizedDescription], to: audioLog) }
    }

    func screen(_ buffer: CMSampleBuffer, arrival: Double) {
        screenBuffers += 1
        let attachments = CMSampleBufferGetSampleAttachmentsArray(buffer, createIfNecessary: false) as? [[SCStreamFrameInfo: Any]]
        let status = (attachments?.first?[.status] as? NSNumber)?.intValue ?? -1
        statusCounts[String(status), default: 0] += 1
        guard let pts = seconds(buffer.presentationTimeStamp) else { invalidScreen += 1; return }
        let ptsGap = lastScreenPTS.map { pts - $0 } ?? 0
        let arrivalGap = lastScreenArrival.map { arrival - $0 } ?? 0
        if ptsGap > 0.1 {
            screenGapEvents.append(["pts_s": pts, "gap_s": ptsGap, "classification": "capture_timestamp_gap"])
            closeRepeat("capture_timestamp_gap")
        }
        if arrivalGap > 0.1 {
            screenObserverGaps.append(["arrival_s": arrival, "gap_s": arrivalGap])
            closeRepeat("observer_callback_gap")
        }
        lastScreenPTS = pts; lastScreenArrival = arrival
        var event: [String: Any] = ["kind": "frame", "pts_s": pts, "arrival_s": arrival,
            "status": status, "pts_gap_s": ptsGap, "observer_gap_s": arrivalGap]
        if let displayTime = attachments?.first?[.displayTime] as? NSNumber {
            event["windowserver_display_time_mach_ticks"] = displayTime.uint64Value
        }
        var hash: UInt64?
        if status == SCFrameStatus.complete.rawValue, let image = buffer.imageBuffer {
            CVPixelBufferLockBaseAddress(image, .readOnly)
            defer { CVPixelBufferUnlockBaseAddress(image, .readOnly) }
            let width = CVPixelBufferGetWidth(image), height = CVPixelBufferGetHeight(image)
            let stride = CVPixelBufferGetBytesPerRow(image)
            if CVPixelBufferGetPixelFormatType(image) == kCVPixelFormatType_32BGRA,
               let base = CVPixelBufferGetBaseAddress(image)?.assumingMemoryBound(to: UInt8.self) {
                let x = Int(Double(width) * options.roi[0]), y = Int(Double(height) * options.roi[1])
                let w = min(width - x, max(1, Int(Double(width) * options.roi[2])))
                let h = min(height - y, max(1, Int(Double(height) * options.roi[3])))
                var value: UInt64 = 14695981039346656037
                for row in y..<(y + h) {
                    let bytes = base.advanced(by: row * stride + x * 4)
                    for col in 0..<(w * 4) { value = (value ^ UInt64(bytes[col])) &* 1099511628211 }
                }
                hash = value; hashedFrames += 1
                event["buffer_size"] = [width, height]; event["roi_pixels"] = [x, y, w, h]
            } else { invalidScreen += 1 }
        } else if status == SCFrameStatus.idle.rawValue {
            // Apple's idle status means no new frame because display content did not change.
            hash = lastHash
        } else { closeRepeat("noncomplete_status") }
        if let hash {
            event["roi_fnv1a64"] = String(format: "%016llx", hash)
            if hash == lastHash { repeatEnd = pts }
            else { closeRepeat("roi_changed"); repeatStart = pts; repeatEnd = pts; lastHash = hash }
        }
        write(event, to: screenLog)
    }

    func finish(window: SCWindow, startWall: Double, elapsed: Double, activation: [String: Any]) -> [String: Any] {
        closeSilence(); closeRepeat("capture_ended")
        for file in [audioLog, screenLog, rawAudio].compactMap({ $0 }) {
            do { try file.synchronize(); try file.close() } catch { ioError = error.localizedDescription }
        }
        return ["schema": 1, "kind": "story002_playback_capture", "pid": options.pid,
            "bundle_id": developmentBundleID, "window_id": window.windowID,
            "window_title": window.title ?? "", "window_frame": [window.frame.origin.x, window.frame.origin.y, window.frame.width, window.frame.height],
            "start_unix_s": startWall, "start_uptime_s": begin, "elapsed_s": elapsed,
            "observer_activation": activation,
            "requested_duration_s": options.duration, "requested_fps": options.fps,
            "owned_display_audio": options.ownedDisplayAudio, "display_rect_screen_points": options.displayRect.map { [$0.minX, $0.minY, $0.width, $0.height] } as Any? ?? NSNull(),
            "normalized_roi": options.roi, "silence_threshold_dbfs": options.silenceDB,
            "audio": ["buffers": audioBuffers, "samples_analyzed": audioSamples, "rms_windows": levelWindows,
                      "partial_window_samples_omitted": levelSamples, "invalid_or_unsupported_buffers": invalidAudio,
                      "formats": audioFormats, "timestamp_discontinuities": audioGapEvents,
                      "observer_callback_gaps": audioObserverGaps, "below_threshold_intervals": silentIntervals],
            "screen": ["buffers": screenBuffers, "hashed_complete_frames": hashedFrames,
                       "invalid_frames": invalidScreen, "status_counts": statusCounts,
                       "timestamp_gaps": screenGapEvents, "observer_callback_gaps": screenObserverGaps,
                       "unchanged_roi_intervals_at_least_100ms": repeatedIntervals],
            "capture_error": captureError as Any? ?? NSNull(), "capture_errors": captureErrors, "io_error": ioError as Any? ?? NSNull(),
            "raw_audio": options.rawAudio ? "audio-mono-f32le.pcm" : NSNull(),
            "scope": options.displayRect == nil ? "Selected development VLC window and containing app audio; no microphone or VLC control. Runner selects active interval." : (options.ownedDisplayAudio ? "Display crop filtered to owned VLC application plus only its audio; no microphone/desktop/unrelated apps. Runner verifies geometry/focus and active interval." : "Actual display crop wholly within active owned VLC window; screen pixels only, no audio/microphone, no whole desktop. Runner verifies geometry/focus and active interval."),
            "limitations": ["No automatic pass/fail or VLC attribution: screen/audio capture gaps may belong to observer.",
                            "Unchanged ROI is meaningful only after live verification that the ROI contains continuously moving video and excludes popup/controls/letterboxing.",
                            "Silence threshold must be checked against generated tone; capture observes digital app audio, not speaker hardware.",
                            "Capture load is part of both benchmark arms; pixel hashing and JSONL writes may affect observer latency."]]
    }
}

@main private struct PlaybackCapture {
    @MainActor
    static func main() async {
        do {
            var options = try Options.parse()
            // Standalone tools do not pass through NSApplicationMain. AppKit's
            // shared instance establishes WindowServer initialization needed by
            // SCContentFilter. A terminal host may reject policy changes; this
            // observer has no windows and never requests application activation.
            let app = NSApplication.shared
            let policyAccepted = app.setActivationPolicy(.prohibited)
            let activation: [String: Any] = ["requested_policy": "prohibited", "change_accepted": policyAccepted,
                                           "effective_policy_raw": app.activationPolicy().rawValue,
                                           "activation_requested": false, "observer_windows_created": 0]
            guard let running = NSRunningApplication(processIdentifier: options.pid),
                  running.bundleIdentifier == developmentBundleID else { throw failure("PID is not the isolated development VLC bundle") }
            let content = try await SCShareableContent.excludingDesktopWindows(true, onScreenWindowsOnly: true)
            guard let application = content.applications.first(where: { $0.processID == options.pid && $0.bundleIdentifier == developmentBundleID }) else {
                throw failure("Development VLC PID absent from shareable content (check capture authorization)")
            }
            let windows = content.windows.filter { $0.owningApplication?.processID == application.processID && $0.windowLayer == 0 && $0.frame.width >= 320 && $0.frame.height >= 180 }
            let window: SCWindow?
            if let id = options.windowID { window = windows.first(where: { $0.windowID == id }) }
            else { window = windows.max(by: { $0.frame.width * $0.frame.height < $1.frame.width * $1.frame.height }) }
            guard let window else { throw failure("No eligible development VLC video window; supply --window-id for unambiguous selection") }
            if options.ownedDisplayAudio {
                guard options.displayRect == nil, running.isActive else { throw failure("Owned-display audio requires active owned app and automatic ROI crop") }
                let f = window.frame
                options.displayRect = CGRect(x: f.minX + f.width * options.roi[0], y: f.minY + f.height * options.roi[1], width: f.width * options.roi[2], height: f.height * options.roi[3])
                options.roi = [0, 0, 1, 1]
                options.fps = 60
            }
            let observer = try Observer(options: options)
            let config = SCStreamConfiguration()
            config.capturesAudio = options.displayRect == nil || options.ownedDisplayAudio; config.captureMicrophone = false
            config.excludesCurrentProcessAudio = true
            config.sampleRate = 48_000; config.channelCount = 1
            config.pixelFormat = kCVPixelFormatType_32BGRA; config.showsCursor = false
            // Bound raster work even if a selected window has an unusual aspect ratio.
            let scale = 640 / max(window.frame.width, window.frame.height)
            config.width = max(2, Int(window.frame.width * scale) / 2 * 2)
            config.height = max(2, Int(window.frame.height * scale) / 2 * 2)
            config.minimumFrameInterval = CMTime(value: 1, timescale: CMTimeScale(options.fps))
            config.queueDepth = 3
            let filter: SCContentFilter
            if let rect = options.displayRect {
                guard window.frame.contains(rect), running.isActive,
                      let display = content.displays.first(where: { $0.frame.contains(rect) }) else {
                    throw failure("Display crop must fit within active owned VLC window and one display")
                }
                filter = options.ownedDisplayAudio ? SCContentFilter(display: display, including: [application], exceptingWindows: []) : SCContentFilter(display: display, excludingWindows: [])
                config.sourceRect = rect.offsetBy(dx: -display.frame.minX, dy: -display.frame.minY)
                let cropScale = min(1, 640 / max(rect.width, rect.height))
                config.width = max(2, Int(rect.width * cropScale) / 2 * 2)
                config.height = max(2, Int(rect.height * cropScale) / 2 * 2)
            } else {
                filter = SCContentFilter(desktopIndependentWindow: window)
            }
            let stream = SCStream(filter: filter, configuration: config, delegate: observer)
            if config.capturesAudio { try stream.addStreamOutput(observer, type: .audio, sampleHandlerQueue: observer.queue) }
            try stream.addStreamOutput(observer, type: .screen, sampleHandlerQueue: observer.queue)
            let startWall = Date().timeIntervalSince1970
            try await stream.startCapture()
            let ready: [String: Any] = ["event": "ready", "pid": options.pid, "window_id": window.windowID,
                                       "output": options.output.path, "start_unix_s": startWall,
                                       "start_uptime_s": observer.begin, "duration_s": options.duration,
                                       "observer_activation": activation]
            try FileHandle.standardOutput.write(contentsOf: json(ready))
            try await Task.sleep(nanoseconds: UInt64(options.duration * 1_000_000_000))
            observer.queue.sync { observer.write(["kind": "stop_requested", "uptime_s": ProcessInfo.processInfo.systemUptime], to: observer.screenLog) }
            do { try await stream.stopCapture() } catch { observer.queue.sync {
                let e = error as NSError
                observer.captureErrors.append(["origin": "stopCapture", "domain": e.domain, "code": e.code, "message": e.localizedDescription, "uptime_s": ProcessInfo.processInfo.systemUptime])
                if observer.captureError == nil { observer.captureError = e.localizedDescription }
            } }
            let summary = observer.queue.sync { observer.finish(window: window, startWall: startWall, elapsed: ProcessInfo.processInfo.systemUptime - observer.begin, activation: activation) }
            try json(summary).write(to: options.output.appendingPathComponent("summary.json"), options: .atomic)
            try FileHandle.standardOutput.write(contentsOf: json(["event": "finished", "summary": options.output.appendingPathComponent("summary.json").path]))
            if summary["io_error"] is String || summary["capture_error"] is String { exit(2) }
        } catch {
            let message = "playback-capture: \(error.localizedDescription)\n"
            try? FileHandle.standardError.write(contentsOf: Data(message.utf8))
            exit(1)
        }
    }
}
