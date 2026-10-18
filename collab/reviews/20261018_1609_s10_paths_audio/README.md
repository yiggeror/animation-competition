# S10 production-path migration and actual audio check

S10 has passed complete visual review and Opus has attached audio at e22841c. This changes only dedicated module import/path strings and stores the eight adopted PNGs under assets/chars/g10. Each asset is exactly the existing Git blob; no image change, no timing/light/camera change. Existing review copy remains. Mapping records source and target. Rendering at production paths is still requested as a path-resolution/frame-equality check, not a new subjective review.

Actual S10_drawn_v1.mp4: 592625 bytes, SHA256 952339fd2df74bf42edc95004f17d4072dfd24994e94315ad6dd58b6a3006f8f. Extracted H264 is byte-identical to the reviewed 120f source. Actual 240000-sample stereo PCM spans master samples2140000–2380000. Current four audio source blobs equal the independently executed rebuild; max difference3LSB, RMSE0.010607LSB. AAC best lag0, correlation0.999244. These are actual technical audio checks, not a claim of subjective listening or lossless AAC. EDL/audio untouched by Astra.

S08 single-frame diagnostic is separately under collab/reviews/20261018_1606_s08_f000_scene. It contains the final new F000 only, not the withdrawn user atlas. Original table front can occlude the two elbow tips and must be assessed in the actual frame before changing the scene.
