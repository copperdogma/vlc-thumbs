# Independent frozen service review

Reviewed the twelve files in `service-port-source-receipt.json` against the frozen
feature-port plan and pinned master `2e358f3098c2f2b7621d1dc568de8b61ad786322`.
All twelve SHA256 hashes were independently recomputed and matched. This is source
and existing-receipt review; no product edits, native app run or additional XCTest
execution were performed. It does not establish Story005 readiness.

## Exact reviewed freeze

| File | SHA256 |
| --- | --- |
| `modules/gui/macosx/timeline/VLCThumbnailCache.h` | `6e529b5db2c69f64276fee828977bab0db512109d1a8ced542ec734138e59640` |
| `modules/gui/macosx/timeline/VLCThumbnailCache.m` | `fdd63448a6e4a561a8158e2dad34fb22e207360ea4a44a717a6fd0ea4dc546e2` |
| `modules/gui/macosx/timeline/VLCThumbnailScheduler.h` | `3358d1078438a65971e67c116d7f1400c69b8033a700427faf7a480419e3c5ec` |
| `modules/gui/macosx/timeline/VLCThumbnailScheduler.m` | `49b2b4e37b69978c38ef6bd99eba66c65a2a299a4d3f4751bf28a7f3ebcb79e0` |
| `modules/gui/macosx/timeline/VLCThumbnailService.h` | `77446215166b7a9f1527c92c1380503d6c411666e06b4306b753fa4bee8d1767` |
| `modules/gui/macosx/timeline/VLCThumbnailService.m` | `28783c9310ae523494e9c321fa2ff5fc765e36dc65155ba73e3d1e9c86211894` |
| `modules/gui/macosx/timeline/VLCThumbnailWorker.h` | `f39aaaad41e397ddbdf8f7b6e3602fc010404ab62287f4cea72af85328bc6296` |
| `modules/gui/macosx/timeline/VLCThumbnailWorker.m` | `1b435123f053af48c421f42385c741f3cb950ad319e5d7741bb84e3baa94a8ac` |
| `modules/gui/macosx/tests/VLCThumbnailCacheTest.m` | `e3a6f36235b9d797ca163d3ecf8bb12b565abaed258c150e4ed40f19f6607ca5` |
| `modules/gui/macosx/tests/VLCThumbnailSchedulerTest.m` | `a0cc60c7f761e59761ba225f8ef16f02ffe65552632de045dd70b1eb9aaa7f1e` |
| `modules/gui/macosx/tests/VLCThumbnailServiceTest.m` | `66dc4893a48ef468e72b448ac11503cd090f1b14b836fd4716ff51e4b1c6f131` |
| `modules/gui/macosx/tests/VLCThumbnailTestHelper.c` | `889d8cf5047cac42374e8303ac6fc786ea73575697cb9bb94a7c8067024fe87c` |

## Findings and minimum corrections

**S1: invalid eligibility values can throw before rejection.** `ValidContext`
coerces `eligible` with `boolValue` without checking its raw type. NSNull or a
dictionary reaches an unsupported selector rather than returning invalid-request.
The complete-context rejection test omits this field. Add a strict raw eligibility
check and malformed-value tests. Normal context production supplies an NSNumber;
this is public boundary robustness, not a reproduced player-generated failure.

**S2: the complete frozen context contract does not require sourceEpoch.**
`ValidContext` never checks sourceEpoch, and current test adapters omit it.
The production context embeds lifecycle changes in generation and includes epoch,
so no actual same-URI regression is established. Nevertheless the review packet's
claim that missing contexts cannot launch is stronger than this validator. Require
a nonnegative integer epoch and include it in fixtures/removal/type tests, or
explicitly narrow the contract with root approval.

**S3: channel count validation truncates malformed numeric values.** Both cache
`Header` and service `DecodeResponse` compare `channels.intValue` to4 after accepting
integral numbers.4294967300 truncates to4, so an invalid header can qualify.
Use exact NSNumber equality with4 and add the overflow value to malformed tests.
Payload length is independently constrained to width*height*4, so this finding
does not establish an overread or corrupt image allocation.

**Bounded-write contract hardening.** Worker command writes are blocking, with
SIGPIPE suppressed but no nonblocking/deadline loop. Read timeout starts afterward.
With the compliant helper there is one tiny command outstanding and every reply
follows consuming its command; that invariant prevents normal pipe backpressure.
A misbehaving helper that emits valid unsolicited replies without consuming input
can eventually fill the pipe. No production occurrence was reproduced. A bounded
nonblocking write is a small repair to the plan's parent-operation bound and should
be tested with a deliberately faulty child; this is defense against child protocol
failure rather than evidence that a merely nonreading normal child hangs today.

A cache timing asymmetry remains: fresh extraction rejects actual_us>=context
duration, while cacheResult does not receive or check duration. Namespace excludes
duration, so a previously qualified sample remains reusable after an otherwise
identical context's length decreases. No real media counterexample was established
by this review. A focused fixture changing duration can distinguish whether this
needs the same guard; it is not grounds to invent timestamp-origin corrections.

## Sound boundaries and proof limits

Selection certification checks exact native input ID, bounded video count and
single/Matroska mapping; negative/duplicate/unrepresentable selection is the helper's
separate boundary. Protocol3 data cannot qualify under the protocol4 namespace.
Context dictionary equality and serial invalidation reject stale asynchronous
results. Worker cancellation increments its epoch; retained retiring children block
replacement until exit, with bounded wait and NSTask lifetime ownership.

Unresolved provisional presentation owns one fixed15-second timer. Cancelling
pointer presentation does not reset it; source failure clears the current image,
including a newer hover than the discovering request. Context cancellation and
shutdown clear state, kill both workers and suppress subsequent main callbacks.
Scheduling and retries remain finite; cache sizes, manifests, samples and aliases
have explicit limits. Disk reads use regular-file/size/no-follow guards and hashes;
RAM/disk cache reuse receives source qualification. Sampled identity retains its
known unsampled-change limitation and is unrelated to durable bookmarks.

The inherited service suite uses an injected compiled test helper and deliberately
disables proactive scheduling in its demand adapter. Proactive preparation has
separate tests. Diagnostic and normal registered receipts distinguish the initial
malformed-cache exceptions, subsequent focused diagnostic fix, and pending normal
focused rerun. Their reported checks do not prove production FFmpeg decoding, real
player sourceEpoch cancellation, native hover, playback, NAS, Intel or old-macOS
runtime behavior. Resolving this review's boundary findings and rerunning focused
registered tests is necessary evidence, not full feature acceptance.

## Narrow service repair re-review

All twelve hashes in `service-port-repair-receipt.json` were independently
recomputed and matched. S1/S2/S3 are resolved in this freeze: eligibility must be
true CFBoolean, sourceEpoch is required and bounded to a nonboolean nonnegative
NSUInteger, and both pixel parsers require exact NSNumber channels equality to4.
Fixtures now supply epoch; malformed eligibility/epoch and channel-overflow tests
exercise rejection without launching or presenting pixels.

The private command writer now sets O_NONBLOCK and F_SETNOSIGPIPE, loops over
partial writes/EINTR, polls on EAGAIN in at most50ms slices, fails on disconnected
pipes, and checks epoch/deadline throughout. Production request uses one fixed
deadline for both this writer and response reader; failure closes the worker.
Real-pipe tests cover saturated timeout, epoch cancellation, disconnected reader,
and byte-exact large partial-write completion with a bounded slow reader. The
large command is deliberately a private-seam test, not a production command-size
claim. The previous blocking-write hardening concern is closed.

The mapping now requires `matroska-track-number-flat-v1`; the previous mapping is
explicitly rejected in the focused test. Namespace includes `transform1:flat-mkv1`,
preventing prior uncertified Matroska cache reuse. This validates the consumer
boundary only; FFmpeg/helper admission of genuinely flat Matroska remains its
separate proof gate.

Existing focused diagnostic logs in this receipt record passing cache, pipe,
channel, selection and incomplete-context cases. The final mapping/context run
records two tests and zero failures. This reviewer inspected source/receipts and
did not rerun tests. Normal registered focused execution remains the build owner's
responsibility. No new material issue was found in the narrow repaired paths.
The cache-duration asymmetry noted above was not changed or qualified by this
repair. Native acceptance and readiness remain outside this review.

Exact repaired hashes:

| File | SHA256 |
| --- | --- |
| `modules/gui/macosx/timeline/VLCThumbnailCache.h` | `6e529b5db2c69f64276fee828977bab0db512109d1a8ced542ec734138e59640` |
| `modules/gui/macosx/timeline/VLCThumbnailCache.m` | `2207283584e23c0c44ec235b89ae3baed676afb11d5d2585d0f2e59b52bb4297` |
| `modules/gui/macosx/timeline/VLCThumbnailScheduler.h` | `3358d1078438a65971e67c116d7f1400c69b8033a700427faf7a480419e3c5ec` |
| `modules/gui/macosx/timeline/VLCThumbnailScheduler.m` | `49b2b4e37b69978c38ef6bd99eba66c65a2a299a4d3f4751bf28a7f3ebcb79e0` |
| `modules/gui/macosx/timeline/VLCThumbnailService.h` | `77446215166b7a9f1527c92c1380503d6c411666e06b4306b753fa4bee8d1767` |
| `modules/gui/macosx/timeline/VLCThumbnailService.m` | `2f39645a0783fcb53a19e77dfe6b3117eb2a91fd570d80fb208be52337629343` |
| `modules/gui/macosx/timeline/VLCThumbnailWorker.h` | `f39aaaad41e397ddbdf8f7b6e3602fc010404ab62287f4cea72af85328bc6296` |
| `modules/gui/macosx/timeline/VLCThumbnailWorker.m` | `18f4aa213f2f8823b69a340ef2e3849c6461cd71070332c814fe44f8ed1ec5b7` |
| `modules/gui/macosx/tests/VLCThumbnailCacheTest.m` | `a20d2840937a77f9a46b173d209724ed21e70fd6640bf6b365dfe51bf051b2b4` |
| `modules/gui/macosx/tests/VLCThumbnailSchedulerTest.m` | `a0cc60c7f761e59761ba225f8ef16f02ffe65552632de045dd70b1eb9aaa7f1e` |
| `modules/gui/macosx/tests/VLCThumbnailServiceTest.m` | `50c06c0a2945ec84bbb90de11272ea657e5b893a0066277686f7082b38142bd1` |
| `modules/gui/macosx/tests/VLCThumbnailTestHelper.c` | `492a4be90691f574375b919458b850f0d8992426491769f7bcd3ad76a5069e21` |
