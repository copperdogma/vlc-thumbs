# ADR-001 implementation research follow-up

VLC macOS timeline enhancements add hover previews and persistent one-to-three-
word timestamp labels. Cam accepted this boundary: labels in a feature-owned
Application Support store, regenerated thumbnail files in a separate Caches
area, and small settings in preferences. Preserve videos. Do not put labels or
images into VLC's resume-history keys, whose retention/clearing must not erase
labels. Format/schema/identity/cache limits are not chosen.

Pinned source: VLC 3.0.24 at 6de05adcbaf2e8b85fe86aad4169393098628119, from
https://code.videolan.org/videolan/vlc.git. VLCInputManager.m stores URI-to-seconds
NSUserDefaults records and caps recent resume entries at 30;
VLCDocumentController.m clears those records with recent history. These are
source findings, not a test of the new feature. Initial scope is same unchanged
local video, with correct handling of replaced files; move/rename support is open.

Bounded questions when implementation is ready:

1. Which supported APIs resolve Application Support/Caches directories for the
   selected macOS/VLC build, and how should feature namespaces be isolated?
2. What is the simplest durable format/schema with atomic update and recovery
   behavior for timestamp/short-label records? Compare complexity honestly.
3. How should media lookup distinguish duplicates and replacements without
   expensive unconditional hashing or silently losing labels?
4. Which cache invalidation/resource bounds suit the proven preview decoder,
   and how can cleanup be structurally confined to disposable data?
5. What isolated tests establish restart, history clearing/turnover and cache
   cleanup behavior without touching installed VLC or real annotations?

Return primary source/API pointers, observed facts versus inference, options and
remaining questions. Do not reopen the accepted split solely to explore variants.
Do not implement, change user data, contact others or make paid calls.
