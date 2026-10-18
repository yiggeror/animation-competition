# S03a revision2 reference: Opus 14:00 stronger whole-head turn

Technical parameters are frozen by Opus commit da4035deafd441d0c69460e54c283194c1ea75d5. These construction images are waiting for the parent's independent quick reference review. They are not production drawings and not a film-integrated pass. Zero image-generation calls and zero GitHub/implementation changes so far.

Changes from reference version1:
- F014/F025: screen-left yaw15deg, screen-left roll2.5deg, local chin-lift pitch1deg.
- F017/F021/F023: screen-left yaw30deg, screen-left roll5deg, local chin-lift pitch3deg.
- Whole-head roll pivots near fixed neck base (842,742), not around the face. All skull/bangs/face/jaw/ears/roots/upper-neck landmarks follow the head.
- Eyes look back screen-right/down relative to the turned face toward the SAME offscreen phone. They never follow the face into empty left space. F014/F025 iris guide offset(13,12), F017/F021/F023(18,12). These are art-direction guides rather than recovered eye rays.
- Near ear visible envelope remains at most103.8px; far21.1px means occluded outer rim only. Never enlarge a round ear or squash its anatomy. Side-ear identity comes from real focus/turnaround.
- Free tails follow with lag, overshoot, settling. Right free-tail equilibrium swing is18px rather than computed solely from net root x: yaw and roll partly cancel root x but must not erase inertial tail movement.
- F021 and F023 head, face, eyes, ears, neck and roots are exactly equal in JSON. Only both free-tail endpoints differ.

Exposure list is unchanged: 000x8,008x3,011x3,014x3,017x4,021x2,023x2,025x3,028x8 =36 frames.

First review files:
- reference/F014_volume_REFERENCE_ONLY.png
- reference/F017_volume_REFERENCE_ONLY.png
- reference/first3_same_camera_volume.png
- reference/minimal5_same_camera.png
- S03a_whole_head_9exposures.json and9exposures_coordinates.csv

Direction/contact/actual-frame pages retain the prior reference content. New yaw/roll face-to-foreground clearances are in JSON: F014121.76px andF017150.86px. These are construction-only bounds, not production acceptance.

Sources are byte-identical copies. Production base remains focus_semantic_production_base.png, SHA256 aa7c4fd193e766b6debf4dc3dae6ed1ba0ce9d4668ddc12624d765a7fcd6021a. Shoulder/collar/garment stay pixel-locked to this approved corrected base; new neck boundaries must be drawn and checked for every new head pose. Foreground hand/melon is separate, untouched, and never baked into character drawings.

Build: python finalize_revision2.py (calls this revision's build_reference.py and then writes full JSON, coordinates, montage andQA). finish_reference.py is an unexecuted provenance copy from version1 and must not be used to build revision2.
