# Native preview preference follow-up — 2026-10-05

The user-requested preference is complete in signed development build 155231
and the refreshed local `~/Applications/VLC Timeline Preview.app`. VideoLAN's
native macOS source already makes comparable interface affordances configurable;
this follows its boolean declaration, XIB/outlet, basic-preferences load/save and
configuration-change notification flow. See [source research](../../research/timeline-preview-preference.md).

## Findings and result

No outstanding material source finding after independent review. Review caught
and corrected tooltip initialization order, then a final command-line probe
caught a plain-config getter ignoring explicit overrides. The final accessor is
`var_InheritBool`, matching upstream status-menu handling: explicit command-line
values take priority for that launch, otherwise it reads live saved config.
No custom precedence framework was added.

“Show timeline thumbnail previews” is enabled by default under basic Preferences
→ Interface → Playback behaviour. Save applies to existing adapter instances
through VLC's normal configuration-change notification. Disabling hides the
panel, invalidates timers/presentation, cancels pending work and restores the
original localized slider tooltip; late completions cannot present. Enabling
resumes on subsequent pointer entry/movement. The original slider owns seeking
and accessibility throughout. Helper/cache/media-identity boundaries are unchanged.

[Final native evidence](native-preview-preference-final.json) proves initial
checked state, Save off, Cancel preserving off, off after full process restart,
and Save on restoring actual keyframe display. The final explicit off probe
also proves ordinary physical seek: slider value 2015.944→5585.997, Position label
and volume 256 retained, with zero hover/service/display work events. All media
were generated fixtures. A screenshot inspected during the first preference
candidate shows the checkbox fitting the existing auto-layout preferences pane;
its XIB is unchanged in the final build. Raw screenshots/traces remain ignored.

The native setting tests are fresh on the main window. Shared controller,
notification and gate wiring cover other adapters; this is not a claim of fresh
four-surface setting/VoiceOver tests. Earlier helper/service/cancellation/reader
and matched playback evidence remains separately scoped and inherited through
unchanged inputs. The setting affects previews only; bookmarks remain Story 003.

## Current response comparison

[Final current-build comparison](ordinary-control-preview-preference-final.json)
collects 20 actual native knob-render responses per arm in four balanced blocks
AB, BA, BA, AB, using the same qualified phase observer and 3000 ms bound.
Root recomputed all 40 earliest matching display-time latencies from raw eligible
frames; all 52 session contracts, frozen hashes and clean owned exits pass.

| Actual observed response | Baseline | Feature 155231 |
| --- | --- | --- |
| Valid scored responses | 20 | 20 |
| Median | 222.039 ms | 236.531 ms |
| Minimum–maximum | 158.141–617.109 ms | 113.493–526.612 ms |

Feature median is 6.527% higher, within the prospectively retained baseline +20%
allowance. Raw samples and all eight block medians are retained; no slow sample
is discarded. This is approximate paused-control observation on a shared host,
not precision p95, completed-seek timing or a causal attribution. It does not
prove zero overhead or a general performance guarantee. Previous 132643 and
154102 comparisons remain scoped to their own builds and are not pooled.

## Delivery and verification

[Final build manifest](app-build-preview-preference-final-155231.json) pins source,
patch, controller, helper and signed outputs. The matching SimplePreferences
nib is compiled explicitly during bundling. Incremental build and strict deep
signing pass. The relocated local copy preserves helper/plugin/cache bytes and
plugin mtimes; changing bundle identity/display name only refreshes its outer
signature. Its independent preview preferences/cache domain remains intact.

[Local update record](local-preview-preference-update.json) preserves previous
app copies and confirms the installed app launches with the new checkbox value 1.
Root left that Preferences window visible for Cam. Existing user preferences,
normal VLC and file associations were not changed. No shortcut, commit, push
or public distribution was performed.

Early Sky inspection created a second owned development instance; it was closed.
An intermediate scripted preferences action failed before the expected window
was ready and was not scored as a successful setting test. Final GUI tests wait
for the native window instead of a guessed short delay. The earlier failed
CLI-override probe remains recorded; the final inherited getter passes it.
