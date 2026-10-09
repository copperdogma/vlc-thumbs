# Independent context-duration correction review

Narrow read-only review of the three changed files in
`ui-context-duration-candidate.json`; all ten receipt hashes independently match.
No product edits or new runtime acquisition were performed by this reviewer.
The source set is `c3b0c1d4eda22b35bf96e8890e138854c8a96e68f232bc4deca8bfcef60c7642`.

No material issue was found in the authorized correction. Fresh eligible typed
positive context duration now governs pointer caption input and service request.
The right edge preserves duration as caption input and clamps request to duration-1.
The controls-bar duration is only a time-only fallback: malformed/ineligible context
cannot request an image. Disabled previews retain fresh pointer time without request.
Production uses the private preference accessor; testing overrides that actual seam.

Completion refreshes the snapshot before presentation/generation checks, preserving
the prior reentrancy repair. It independently compares current context duration to
the active captured hover duration, hiding/removing pixels on mismatch even when
a mocked generation is unchanged. Later pointer presentations change the serial,
so the mutable hover duration cannot authorize an older completion. Existing
seek/drag/lifecycle ownership is unchanged in this narrow delta.

Six new actual-slider/service-double regressions distinguish longer/shorter context
duration, zero stale-bar duration at the right edge, delayed same-generation duration
change, malformed/ineligible fallback, and disabled requests. The headless receipt
records12 methods and61 assertions passing. A disposable counterfactual restoring
only stale-bar mapping compiles and fails the longer-duration shown-time assertion
(`work/story005-ui-context-duration-checks/counterfactual.json`). This supports the
oracle's ability to catch the prior defect. It does not replace normal registered
XCTest or actual native pointer/window/reader validation on this changed freeze.

Changed file hashes:

| File | SHA256 |
| --- | --- |
| `modules/gui/macosx/views/VLCPlaybackProgressSlider.m` | `76289b6be84e615fa8746a5b18a600165b3d6755c7a85b25d7b8b10a4cbbdd10` |
| `modules/gui/macosx/tests/VLCTimelineHoverReentrancyTest.m` | `850dc33a8032b3a7c8fb4329d651ee46a6bd6d24a5b4b7fd8bc1224dd64c3715` |
| `modules/gui/macosx/tests/VLCTimelineHoverTestSupport.m` | `2a242068cc0b32b4e3ee5e94d490e6cf64ae4fe88f040f54317e420327ca07e3` |
