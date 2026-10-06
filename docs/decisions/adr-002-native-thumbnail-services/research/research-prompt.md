# Bounded implementation questions

For VLC 3.0.24 arm64 macOS timeline thumbnails, verify the selected existing
contrib FFmpeg helper against generated MP4/MKV and timestamp/presentation cases.
1. Does normalized PTS agree with VLC's timeline for starts/edit offsets/VFR?
2. Can one active process + latest pending demand meet p95 hover budgets?
3. Do windowed and separate fullscreen slider adapters preserve controls/AX?
4. Are cache/process/IO bounds, file-only access and stale-result rejection real?
5. Does the final isolated bundle launch/sign without external runtime libraries?

Use existing local libraries and diagnostic evidence; no paid research/model
calls. Native interaction and actual frames are required. Do not infer product
success from build/probe results or change installed VLC/user media.
