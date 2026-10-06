# Foreground transition diagnostic boundary

2026-10-05. Bounded primary-source review only; no collector implementation,
UI interaction, new recording or guard relaxation.

The current ordinary-control observer combines target-app existence, expected
bundle identity and `NSRunningApplication.active` into `app_active`. An observed
false value establishes a failed eligibility guard, but the retained rows do not
identify the frontmost application or the cause of the transient condition.
Correct later pixels and post-input ownership do not waive the earlier failure.

The installed macOS SDK's `NSRunningApplication.h` states that time-varying
properties are inherently race-prone and persist until the next turn of the
main run loop in a common mode. Thread-safe atomic reads do not remove this
policy. This permits a cache/race hypothesis; it does not establish that a
particular false sample was an API artifact. Current observer collection waits
with `usleep` on its main thread while a background queue reads this property,
so an independent recorder must service its own run loop continuously.

The SDK's `NSWorkspace.h` requires workspace application notifications to be
registered on `NSWorkspace.sharedWorkspace.notificationCenter`. Both
`NSWorkspaceDidActivateApplicationNotification` and
`NSWorkspaceDidDeactivateApplicationNotification` supply the affected
`NSRunningApplication` under `NSWorkspaceApplicationKey`.
`frontmostApplication` identifies the application that receives key events.

The smallest proposed next diagnostic is one separate, bounded foreground
notification collector around one owned ordinary-control trial during an
exclusive interaction window. Register both notifications before declaring
collector readiness, service its run loop, and retain initial/final frontmost
snapshots plus activation/deactivation receipts. Each receipt records only
notification kind, affected PID/bundle, monotonic receipt time, and current
frontmost PID/bundle. Avoid creating an `NSApplication`, activation requests,
AX calls, input taps, window titles, environment dumps or per-frame polling.
Use the same uptime clock as the existing probe and preserve raw event order.

Notification receipt time is not an exact WindowServer transition timestamp.
A corroborating target-deactivate/other-activate sequence near a guard failure
would identify the observed transition; absence of such receipts would leave
the cause unresolved. It must not convert a failed trial into qualification.
A future provenance-only decomposition of the existing boolean into
`app_exists`, `bundle_expected`, and `target_active` could remove ambiguity
about which component failed. No such observer change is made here.

Primary sources:

- Installed SDK `AppKit.framework/Headers/NSRunningApplication.h`, lines50–56
  and78–80; [NSRunningApplication](https://developer.apple.com/documentation/appkit/nsrunningapplication?language=objc).
- Installed SDK `AppKit.framework/Headers/NSWorkspace.h`, lines33–34,
  143–144 and285–295; [NSWorkspace](https://developer.apple.com/documentation/appkit/nsworkspace).

Scope of the next deliverable: foreground identity/transition evidence only,
with the existing exact-PID, pixel, input-routing and eligibility guards intact.
No conclusion about coalescing performance follows from this research.
