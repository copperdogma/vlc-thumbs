# Frozen UI lane independent source review

Reviewed the eight-file UI lane recorded by `ui-feature-candidate.json` against
base `2e358f3098c2f2b7621d1dc568de8b61ad786322`. All eight current hashes match the
frozen receipt. `feature-ui-review-hashes.json` records full hashes, including
read-only service/context/control dependencies. No source, app, preferences or
physical UI was changed by this review. Native UI remains blocked pending unlock.

## Material finding — P1, synchronous snapshot notification reentrancy

`VLCPlaybackProgressSlider.m:475-482` sets `_hovering = YES`, establishes the
presentation point/time, cancels the previous request, then calls context snapshot.
`VLCTimelineContext.m:116-140` synchronously refreshes on every snapshot and, when
player values or effective enabled state changed, posts `VLCTimelineContextChanged`.
The slider's observer synchronously calls hideHoverWindow (`177-184`, `388-403`),
which clears `_hovering` and advances `_previewPresentation`.

The original report method then resumes, issues a request and shows the panel
(`484-513`) without reestablishing hovering. Every subsequent completion rejects
because `_hovering` is false (`494`), so an eligible changed context can leave a
Preparing panel that receives no image until another pointer event. This path is
reachable when sourceEpoch/track/length changes are first detected by the pointer's
snapshot before the queued player notification, a required lifecycle case in the
frozen port plan. It is a source-proven control-flow defect; the actual visual
outcome has not been exercised on the locked Mac.

Acquire/refresh the snapshot before committing the new hover presentation, or
explicitly revalidate and establish state after all side-effecting snapshot work.
Also make callback refresh a separate first step, then recheck hovering,
availability, presentation serial and generation. Currently the callback guard
passes `_previewPresentation` and a side-effecting snapshot as separate arguments
in one expression (`495-496`); the serial may be read before the snapshot posts a
synchronous hide. Do not rely on argument evaluation order to preserve the guard.
Add a regression that injects a snapshot refresh notification during hover setup
and during callback admission; pure equality helper assertions do not exercise it.

## Source observations with no additional material finding

- One slider-owned NSTrackingArea is hosted by direct superview, removed before
  reinstall, without inVisibleRect (`193-218`). The helper centers a 32point band
  on the actual cell bar, horizontally bounds it, converts and intersects with
  the direct parent's bounds. This leaves slider frame/hit testing unchanged.
  Parent clipping can reduce usable height; only native inspection can prove the
  actual expanded band and overlapping controls/occlusion on each surface.
- Window/superview moves, frame/bounds changes, disabled/indefinite/hidden state,
  drag, app resignation and owning-window lifecycle cancel presentation. Fade
  hook precedes alpha animation in `VLCMainVideoViewController.m:466-472`; showing
  controls restores the flag (`501`). These are source paths, not event proof.
- Existing nonactivating, mouse-ignoring child panel is retained. Content layout
  keeps pointer time distinct from localized actual keyframe/status text, nil
  images remove pixels, weak slider capture avoids extending slider lifetime,
  request serial and generation guard late completion. Very wide localized
  captions are not width-constrained/wrapped; inspect in native layout/language
  proof before attributing material visual impact.
- Common controls retain original seek action and AX title/label
  (`VLCControlsBarCommon.m:151-152`, `412+`). Slider scrollWheel is unchanged;
  mouseDown delegates to NSSlider after hiding. No keyDown, key equivalents,
  target/action, slider frame, role or focus ownership replacement was added.
  Added caption/image are not accessibility elements. Reader behavior remains
  untested, as does keyboard focus across actual fullscreen transitions.
- Main/detached windows use VLCMainVideoViewController and its controls. Custom
  fullscreen reparents the same view (`VLCVideoWindowCommon.m:403-406`, `431-435`)
  and restores it on exit (`622+`); no obsolete3.0 fullscreen panel was added.
  Native fullscreen uses the existing window/controller. This supports source
  reuse across four surfaces but cannot qualify their actual UI behavior.
- Simple Preferences saves through config_PutInt and standard configuration-change
  notification; runtime slider reads var_InheritBool, so the existing variable
  precedence mechanism is preserved. Live save/Cancel/CLI/restart remains pending.
  Notification ordering can clear the hover before its configuration observer
  captures wasHovering: context observer refresh posts ContextChanged first.
  Therefore the receipt's same-window immediate hover restoration claim is not
  established by the source and belongs with the reentrancy regression above.
- Exact right bar endpoint maps to duration, which the service rejects as outside
  `[0,duration)`. This fails safely as Unavailable rather than wrong image; review
  desired last-frame endpoint behavior during native qualification.

The existing four-method/22-assertion UI test checks pure band conversion,
fraction clamps and equality guard. It does not instantiate slider lifecycle,
parent tracking ownership, cancellation, notification reentrancy or preferences.
Focused compile/XIB success is preserved as its own evidence boundary. This review
is not cleared until the material reentrancy finding is resolved and independently
rechecked on new hashes; it does not claim submission readiness.

## Repair addendum — exact ten-file freeze cleared for integration

Narrow rereview matched every source hash in the updated UI receipt, source-set
SHA256 `d02c16749264af51babe8d6d18f823d30a59b9806a7159afcc3f117026fc2b70`.
Full current hashes and independently executed harness binary hash are retained
in `feature-ui-repair-review-hashes.json`; the original eight-file review hashes
remain unchanged as historical evidence.

The material P1 is resolved at source/test boundary. `timelineSnapshot` now runs
before bar geometry and new hover state, followed by availability recheck
(`VLCPlaybackProgressSlider.m:483-499`). Completion admission obtains its snapshot
in a separate statement before reading hovering/current presentation/generation
(`467-473`). This removes both identified synchronous notification ordering flaws.
The private seam supports injection without changing the public slider API.

Independently executed the existing linked actual-slider headless harness:
6methods/32assertions passed. Its two new tests inject ContextChanged during
snapshot acquisition and check new-hover establishment and completion rejection.
The preserved old-order counterfactual exits by assertion failure on actual
slider hovering state, showing the test discriminates the original defect.
No physical native UI was acquired; test doubles omit windows/player/decoder.

Root-approved endpoint helper clamps requested samples to duration-1 while leaving
pointer time/display unchanged. Pure tests include endpoint, interior, one-tick
and invalid-zero duration boundaries. This removes the reviewed final-edge
Unavailable issue at the source contract boundary. Existing control input actions
remain unchanged. Native preference notification order, rendering and all four
surface gates still remain pending; this addendum clears only the prior material
source finding for integration, not the story's readiness or native qualification.
