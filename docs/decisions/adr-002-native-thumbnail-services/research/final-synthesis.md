# Decision basis

Stable native slider/source/build inventory and diagnostic probes justify the
route chosen in ADR-002. AVFoundation failed the tested MKV; contrib libav helper
passed 15 requests with MP4/MKV RGB equality and returned normalized timestamps.
These support availability, not production IPC/performance/UI correctness.

Implementation will record measured outcomes under docs/evidence/story-002.
A short-lived worker is the simplest first production candidate. If actual
end-to-end latency is inadequate, measure persistent-worker reuse behind the
same bounded service rather than accumulate a second extraction engine.
