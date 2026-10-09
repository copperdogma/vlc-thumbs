# Untouched master baseline OpenGL attribution

After the native owner handed off a quiet desktop, the single registered `test_modules_video_output_opengl_filters` test was run through the exact planned Automake test-driver/libtool-wrapper command. No rebuild, backend override, UI input, or additional selector was used. The untouched source remained clean at `2e358f3098c2f2b7621d1dc568de8b61ad786322`; planned executable/library hashes matched before acquisition.

The native test aborted with exit134 after0.942s: `GL_INVALID_OPERATION` in `test_opengl_offscreen`, filters.c:134, immediately after appending the renderer. Automake TRS records FAIL; the test-driver's own exit0 does not mean PASS. The baseline log selects the same `cvpx_gl` offscreen provider, `glsampler_builtin` sampler, `vout_macosx` renderer, and OpenGL2.1 Metal91.7 on Apple M4Pro as the failing independent distcheck log.

This reproduces the failure signature on untouched master. It does not establish the exact OpenGL cause or matched whole-build equivalence: the baseline has full macOS configuration/normal contrib, while distcheck is minimal. No workaround or upstream core repair was attempted.

The owned process group was absent after completion, the outer90s/native10s timeout was not reached, and minimum free space was50,863,620,096 bytes (above the1GiB floor). Graphics acquisition was released to root immediately after the run. No unknown process was stopped.

Exact inputs, command, environment, TRS, raw-log hashes and post-run status: [acquisition receipt](baseline-opengl-attribution-20261006T134341Z.json). Raw output: [test log](baseline-opengl-planned001.log), [TRS](baseline-opengl-planned001.trs). Prior planning/source equivalence limits: [plan](baseline-opengl-attribution-plan.json).
