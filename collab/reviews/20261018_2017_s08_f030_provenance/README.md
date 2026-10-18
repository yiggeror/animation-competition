# S08 F030 exact source preservation and portable replay

Locked final SHA-256: `ef53ba49d805d2a9eb2cf934f62b2098a07e924250fcbbd5070cb33fcbba6bc8`.
Repository destination: `collab/reviews/20261018_2017_s08_f030_provenance`.

## Verified result

The isolated replay exited 0 and reproduced the locked PNG byte-for-byte, with 0 different decoded RGBA pixels and maximum channel difference 0. All 32 upstream and final image/mask checksum checkpoints passed. Production source files were read-only and all 90 preserved source files were rechecked unchanged after this work.

The fresh replay directory contained exactly six original PNG inputs, `replay_f030.py`, and `REPLAY_DEPENDENCIES.json`. Neither the final image nor a registered or repaired intermediate image was present. The final image was read by the external harness only after the replay subprocess had exited. See `ISOLATED_REPLAY_LOG.json`, captured stdout/stderr and `REPLAY_RESULT.json`.

This is deterministic postprocessing of the preserved call15 output. It does not repeat the image-generation service, make network requests, install packages or create a new image-generation call. This supplement adds no new visual approval and makes no claim about actual Canvas integration.

## Reproduce

Recorded runtime: Python 3.12.14, Pillow 12.3.0, NumPy 2.3.5, SciPy 1.17.0 and zlib 1.3.2. These packages were already installed. Exact PNG bytes depend on the recorded numerical/image/compression implementation. `requirements-replay.txt` records the three Python packages; it installs nothing automatically.

From this package directory, choose a fresh sandbox:

    python run_isolated_replay.py --sandbox /tmp/f030-replay-new --verify-against final/S08_F030_whole_turn_same_raw_final_color_RGBA.png

Or run without the optional external final oracle:

    python run_isolated_replay.py --sandbox /tmp/f030-replay-new

The minimal replay is:

    python replay_f030.py --out /tmp/f030-output-new

Existing output or sandbox directories are refused. The Python audit hook rejects undeclared project file reads, writes outside the new output directory, and network/subprocess operations from the replay. Runtime-library reads remain allowed. This is an audit guard, not an operating-system security sandbox. Existing-directory refusal tests are recorded in `REPLAY_NEGATIVE_TESTS.json`.

## Six computational inputs

1. Original locked F027 full RGBA.
2. Original F027 true near-hand/match footprint.
3. Original F027 whole closed far-hand/jade/transparent-seat footprint.
4. Original F027 fixed table-box footprint.
5. Original F027 near-wrist connector mask used by its body/arm partition.
6. Preserved native call15 raw PNG.

The script reconstructs the original F027 body partition, all eight frozen F030 input masks and original-pixel preplacement, the actual raw registration, all accepted semantic-v6 masks and image, then the four final color masks and final image. `REPLAY_DEPENDENCIES.json` contains every computational input, SHA-256, Git blob SHA-1, byte count and checkpoint hash. `SOURCE_DEPENDENCY_AUDIT.json` describes the original-script dependency graph and the distinction between computational, generation-reference, diagnostic and downstream-layer dependencies.

The registration uses the actual executed values `scale=0.9520895`, `tx=2.45681689`, `ty=4.89641481`, not the optimizer diagnostic's additional decimal places. Original order, dtypes, resampling, alpha composition and rounding are retained. Only export/preview branches that do not affect the final output are omitted.

## Generation and historical evidence

`ROWS_MINIMUM_ONLY.json` is the first-delivery list of exactly nine files: the original request, complete original prompt, five actual ordered reference images, preserved raw and `MINIMUM_SOURCE_RECEIPT.json`. Total: 3,973,490 bytes. The request SHA-256 is `50c4647e13062538ec801eee5d6341718818d2205a9d895121b28928cde98b51`; raw SHA-256 is `875c9f44855705b9f0a42cd9a36d7e31d873a8ba173c790004038453cae40a51`. The preserved raw was also checked against its original native generation output file. There was one successful F030 native call; the prior global argument-validation failure belongs to call14, not F030.

All original scripts and diagnostic JSONs remain unchanged, including historical pending/rejected status labels and the filename containing `UNCLEAN_DIAGNOSTIC`. Those labels are not rewritten to imply historical acceptance. The later sealed final contract separately establishes which image was accepted. Redundant rejected/intermediate PNGs are checksum-indexed in `DIAGNOSTIC_EVIDENCE_INDEX.json` rather than copied. Repeated preview boards, MP4s and generated replay PNGs are not included.

The old `color_masks_and_checks_INITIAL_BUILD_AUDIT.json` is preserved. The corrected interpretation is also preserved: 402 changed pixels inside the broad near-arm extraction alpha are blue blouse/cuff or antialiasing contamination; actual near-arm skin changed 0. Alpha and protected hand/match/jade/seat/box pixels changed 0. The replay independently confirms these counts. No global ±4 claim is made for every skin or hair shadow pixel.

The first replay attempt computed the exact final PNG, then failed while reporting because an original material-list variable shadowed the portable dependency-manifest variable. Only that local diagnostic variable was renamed in the portable code; the original script was untouched. The exact failure log and cause are retained in `INITIAL_REPLAY_FAILURE.json` and `INITIAL_REPLAY.stderr.txt`, followed by the successful fresh isolated run.

## Delivery

`ROWS.json` contains the complete package transfer list. `ROWS_SUPPLEMENT_ONLY.json` excludes the nine first-delivery files. Rows contain `path`, `local`, `gitsha`, compatibility alias `sha`, `bytes` and `upload`. `gitsha`/`sha` are Git blob SHA-1 values, not SHA-256.

`EXISTING_BLOB_REUSE.json` supplies fixed-commit/path evidence for four reused blobs, including the 579,264-byte F027 source image at commit `0d2e05307403d7a009c7bff854f5b13a7909c015`. Those rows use `upload:false`. Other rows remain `upload:true` unless the coordinator establishes additional reuse. The two preserved copies of request/prompt have identical content; a coordinator can upload one blob for each SHA and reference it twice.

The final F030 layer scripts, contract and sealed checksum manifests are retained as downstream documentary evidence. The three layer PNGs belong to the coordinator's existing integration delivery and are not necessary inputs to this final-character replay.

Transfer lists are local coordination metadata and are not recursively included in their own rows. Local package-preparation helper scripts are not part of the delivery. This worker made no GitHub writes or external uploads.
