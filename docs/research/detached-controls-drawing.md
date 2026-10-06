# Detached control drawing — 2026-10-04

Problem class: native view composition/drawing. A semantically accessible
control can remain invisible due to layout, clipping or composition. Do not
infer visibility from AX frame/button action or a preview popup alone.

Current and unmodified Story001-module baseline both show a 36pt black bottom
bar without visible buttons/time/slider on this host. AX exposes the controls
and Play/Pause actions work. Resizing baseline from1687x1084 to960x608 leaves
the defect. Source has no normal detached idle-fade; Windows.m hides the bar
only for native fullscreen, then restores it. This is a baseline defect rather
than evidence that timeline preview code removed the controls.

Apple [layer backing guidance](https://developer.apple.com/documentation/appkit/nsview/wantslayer)
and [OpenGL drawing guidance](https://developer.apple.com/library/archive/documentation/GraphicsImaging/Conceptual/OpenGL-MacProgGuide/opengl_drawing/opengl_drawing.html)
distinguish AppKit-managed backing layers and layer-hosting/OpenGL views.
A bounded hypothesis was that the unlayered bar was composed underneath video.
An opt-in experiment making its ancestor VLCBottomBarView layer-backed did not
restore visible controls. Removed the experiment; do not accumulate layer
special cases without inspecting actual ancestor geometry and video extent.

Owned captures remain under work/validation/story002:
baseline-detached-controls.png, baseline-detached-resized.png,
layer-test-detached-controls.png. Baseline app hash/provenance is in
baseline-app-manifest.json. Actual scene/ancestor diagnostics are next. No
installed app or private media changed. Full detached visual qualification
remains incomplete.

Follow-up: Apple's [clipsToBounds documentation](https://developer.apple.com/documentation/appkit/nsview/clipstobounds) warns that modern AppKit dirty rectangles may extend outside view bounds. Pinned VLCVoutView.drawRect filled the whole rectangle black. Intersecting the fill with self.bounds restores visible detached controls without changing layer configuration or playback geometry. Both unsuccessful layer experiments were removed. This is a locally demonstrated fix on the declared host.

Actual rebuilt wide and resized detached controls/previews appear in detached-fixed-tall-hover.png and detached-resized-hover.png. Pointer movements above/below show previews; leaving hides them; endpoint requests return available first/last keyframes. Paused playback stays at 00:36. Complete-story playback and remaining interaction gates are separate.
