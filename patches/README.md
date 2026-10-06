# Source and license notices

This repository publishes project source, minimal upstream patches and diagnostic evidence. It does not include VLC/FFmpeg source trees, compiled apps, dependency archives or private media. Applied patches retain the original upstream copyright and license headers.

- `vlc-3.0.24/0001-native-timeline-previews.patch` modifies VLC3.0.24 macOS interface source, pinned at `6de05adcbaf2e8b85fe86aad4169393098628119`. Original source copyrights belong to the VLC authors and VideoLAN as recorded in those files. Their GPL-2.0-or-later terms apply to the patch context and modified interface source. New native/helper source declares GPL-2.0-or-later; the license text is in [src/COPYING](../src/COPYING). Upstream source: https://github.com/videolan/vlc/tree/6de05adcbaf2e8b85fe86aad4169393098628119
- `ffmpeg-8.1.2/matroska-track-number.patch` modifies FFmpeg8.1.2 `libavformat/matroskadec.c`, copyright2003–2008 The FFmpeg Project and subsequent upstream contributors. That file declares LGPL-2.1-or-later. Its unmodified license text is [COPYING.LGPLv2.1](ffmpeg-8.1.2/COPYING.LGPLv2.1). Upstream release source: https://ffmpeg.org/releases/ffmpeg-8.1.2.tar.xz

Build scripts fetch/use separately pinned upstream source and preserve original archives. Local development app qualification does not establish public binary redistribution compliance. A public assembled-app release requires a separate dependency/configuration audit and corresponding-source obligations; no binary release is supplied here.
