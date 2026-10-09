# Explicit SDK for direct test compiler invocations

Unchanged baseline app build022001Z passed. Subsequent official CI compile-all
command `make -j4 check TESTS=` stopped20.1s in attempt022526Z because direct
Objective-C compiler invocations could not find Foundation/Foundation.h.

Problem class: command-line compiler SDK context differs between a build wrapper
and a later directly invoked make. Official build.sh exports SDKROOT inside its
process, but that child export does not persist into its caller. This host's
direct clang driver does not automatically find framework headers.

Small actual applicability probe: same Xcode clang and minimal Foundation import
failed with SDKROOTunset and passed with SDKROOT set to
`xcrun --sdk macosx --show-sdk-path`. Full receipt is
`baseline-test-sdk-probe.json`. This is the compiler SDK-selection environment,
not a source/build-code change or wider library discovery.

Decision: explicitly export actual SDKROOT for subsequent direct makechecks;
monitor records exact resolved path. Retry022629Z retains original commands.
