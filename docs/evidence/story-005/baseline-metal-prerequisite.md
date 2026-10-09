# Required Metal toolchain component

Baseline021319Z reached VLC configure and stopped exit1 after44.2s because
metallib was missing. `xcrun --find metallib` fails and `xcrun metal --version`
reports missing Metal Toolchain. No VLC config.h/library/app was produced.

Problem class: separately distributed platform compiler component. Pinned
configure.ac4697 and local `xcodebuild -help` identify the supported installation
command `xcodebuild -downloadComponent MetalToolchain`. Apple primary reference:
https://developer.apple.com/documentation/xcode/downloading-and-installing-additional-xcode-components

Decision: install the Xcode-selected component with Apple's supported command,
using the same1GiB free-space process-group guard/no-deletion monitor. This is a
host build prerequisite, not a source-version substitution or product patch.
Record command/download outcome in its baseline-build timestamp receipt;
then verify actual metal/metallib availability before retrying configure.
Existing VLC apps, source3.0 and old work/build are untouched.

Result: Apple component acquisition021453Z exited0 after60.2s, installing
Metal Toolchain27A266a from838.9MB download. `xcrun --find metallib` now resolves
to the system Metal cryptex; `xcrun metal --version` reports Apple metal32023.921
(metalfe-32023.921.6), target air64-apple-darwin27.0.0. Actual tools available.
