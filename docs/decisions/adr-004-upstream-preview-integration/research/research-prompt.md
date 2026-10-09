# Research prompt — VLC upstream preview integration

Prepare native macOS timeline previews for upstream VLC master2e358f3098c2f2b7621d1dc568de8b61ad786322.
The local VLC3.0.24 app already has bounded helper extraction, actual frame PTS,
selected-track guards, progressive preparation and32MiB RAM/256MiB disk reuse.
Freshness uses guarded metadata plus16x64KiB sampled SHA256, with an explicit
unsampled-change limitation. Preserve this behavior or explicitly resolve changes.
Do not touch installed apps/media or contact upstream.

1. Does the native preparser's actual picture PTS, selected-track identity and
   exported transform match playback on legal MP4/MKV/offset/rotation fixtures?
2. Does its one-input-per-request lifetime preserve responsiveness on slow NAS?
   Compare measured cost with retained-session extraction, not process reuse alone.
3. What small shared extension, if any, fits issue#29393 and open macOS MR!7493?
   Distinguish published direction, inaccessible review discussion and conjecture.
4. Which cache/identity primitives can be reused without losing bounded retention,
   restart freshness, corruption handling, cancellation and media privacy?
5. What minimal patch series can build independently and receive branch-native
   regression/UI/control/playback proof, with correct source licenses/attribution?

Root owns selection. Return exact source/proof evidence and remaining uncertainty;
no broad implementation or external communication is authorized by this prompt.
