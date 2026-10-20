#!/bin/bash
set -euo pipefail
D=/workspace/scratch/f060b5601755/s28_rod_clearance_review/gm_avoidance_finish
for F in 006 012; do
 if [ "$F" = 006 ]; then P='502,798 527,812 527,827 502,820'; else P='497,803 522,820 522,834 502,832'; fi
 magick -size 1024x1536 xc:none -fill '#3b445b' -draw "polygon $P" "$D/F$F/hip_underfill.png"
 magick "$D/F$F/hip_underfill.png" -alpha extract "$D/F$F/hip_underfill_mask.png"
 magick "$D/S28_GM_F${F}_finished.png" "$D/F$F/hip_underfill.png" -compose DstOver -composite "$D/F$F/hip_underfill_composite.png"
 magick "$D/S28_GM_F${F}_finished.png" "$D/F$F/hip_underfill_composite.png" "$D/F$F/hip_underfill_mask.png" -channel RGBA -fx 'u[2]>0?u[1]:u' +channel -depth 8 "$D/F$F/final_hip_closed.png"
 magick "$D/F$F/final_hip_closed.png" "$D/S28_GM_F${F}_finished.png"
 magick "$D/S28_GM_F${F}_finished.png" -background '#969696' -alpha remove -alpha off "$D/F$F/gray.png"
 magick "$D/S28_GM_F${F}_finished.png" -background '#2c3443' -alpha remove -alpha off "$D/F$F/deep.png"
 magick "$D/F$F/gray.png" -crop 700x430+150+500 +repage -resize 1400x860 "$D/F$F/seams_2x.png"
done
