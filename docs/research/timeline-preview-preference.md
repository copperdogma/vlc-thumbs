# Timeline preview preference — 2026-10-05

Cam requested an on/off setting if it follows normal VLC development. Pinned
VLC3.0.24 `modules/gui/macosx/macosx.m` registers native boolean options for
fullscreencontroller, media keys, resizing, and playback buttons. Its simple
preferences use XIB/outlet, `setupButton:forBoolValue:`, `config_PutInt`, and
`config_SaveConfigFile`, then post `VLCConfigurationChangedNotification`.

Primary upstream example: [VideoLAN macOS preference addition](https://mailman.videolan.org/pipermail/vlc-commits/2019-May/056020.html) adds a native
resizecheckbox through those same declaration/controller/XIB seams. It supports
configurability of comparable UI features, not a rule that every feature must
have a toggle.

Decision: register `macosx-timeline-previews`, defaulttrue, with a visible
“Show timeline thumbnail previews” checkbox in basic Preferences→Interface.
Use normal VLC config persistence and its existing savedconfiguration notification.
Saving disables all current adapters, cancels pending timers/requests and hides
existingpreview; future pointer/visibility/completion checks rejectdisabledwork.
Restore originalslider tooltip when disabled and preserve accessible slider
label. Read config directly so advanced preferences also apply on nextinput
or100msvisibilitycheck whilehovering. Cancellation remains generationguarded.

Update only the isolated development and Cam's local previewcopy, preserving
regularVLC and the earlier validated app. Verify checkboxoff/on, Cancel, restart
persistence and physicalhover, plus source/fixture/build/signature provenance.
No publicdistribution, defaultfileassociation or commit/push is requested.

Implementation review caught commonbar tooltip setup ordering: restore the
localized Position tooltip before adapterconstruction and let the adapter own
suppression. This correction is included in the final154102 build. XIBcompile
and strictdeep signing passed. Physical basicpreferences proof shows defaulton,
Saveoff, Cancelpreservation, offchoiceafterrestart and Saveon restoring actual
keyframe display. The screenshot shows the newrow fitting Playbackbehaviour.
Earlier Skyinspection launched a second testinstance; both exactownedinstances
were closed and finaltests use exactPID AppleScript/nativepointer. This is test
setup history, not a product defect. Rawtestdata remain ignoredsynthetic media.

Final correction: a directconfig getter passed saved-preference tests but ignored
the new option's explicit command-line override. Pinned native
`VLCStatusBarIcon.m:154` uses `var_InheritBool` after configuration-change
notification; `src/misc/variables.c:1173` resolves inherited variables first and
falls back to currentconfig (`VLC_VAR_BOOL`,1196–1197). Adopt that standard
accessor rather than adding customprecedence state. ExplicitCLI overrides win
for that launch; ordinary app launches use live savedconfiguration. The final
155231 build passes CLIoff with zeropreviewwork and normalphysicalseek
2015.944→5585.997, same volume256 and Positionlabel. Final004 basicGUI offSave,
Cancel, offafterrestart and onSave display also pass. The003 scriptedpreferences
windowfailure happened beforeSave; it remains invalid, not a product failure.
Final004 waits for expectednativewindow readiness instead of a guessed300ms
delay. ExactPID control avoids LaunchServices duplicate-instance ambiguity.
