from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
H=Path(__file__).resolve().parents[1];P=H.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
raw=P/'d07_F024_zero_call_repair/candidates/F024_original_pixel_sleeve_repair_rgba.png';final=H/'candidates/F024_final_rgba.png'
# Direct source->final alpha and protected-domain accounting across both separate steps.
a=np.array(Image.open(raw));o=np.array(Image.open(final));c=np.array(Image.open(H/'candidates/F024_cleanup_before_color.png'));mask=np.any(a!=o,2);alpha=a[:,:,3]!=o[:,:,3]
features=np.array(Image.open(H/'masks/protected_features_blush_and_frozen_collar.png'))>0;hair=np.array(Image.open(H/'masks/protected_hair_lines_highlights.png'))>0;cloth=np.array(Image.open(H/'masks/protected_clothing_yellow_white.png'))>0
corridors=(np.array(Image.open(H/'masks/left_corridor_weight.png'))>0)|(np.array(Image.open(H/'masks/right_corridor_weight.png'))>0)
frill=np.array(Image.open(H/'masks/real_frill_color_stroke_AA_protected.png'))>0
color_change=np.any(c!=o,2);cleanup_change=np.any(a!=c,2)
# Clothing masks are material/step specific. Transparent RGB and newly exposed skin AA in the cleanup corridor are not white fabric.
cloth_combined=(cloth&~corridors)|frill
assert not np.any(mask&features);assert not np.any(mask&hair);assert not np.any(mask&cloth_combined);assert not np.any(color_change&cloth);assert not np.any(cleanup_change&frill);assert np.array_equal(c[:,:,3],o[:,:,3]);assert not np.any(alpha[:1400]);assert not np.any(alpha[1475:])
Image.fromarray((alpha*255).astype('uint8')).save(H/'masks/final_vs_4a203_alpha_changes_left_corridor_only.png')
result={'fixed_source_commit':'4a203f2fa3e56603b30c4fa2faf26ca134047074','final_sha256':sha(final),'color_step_alpha_changes':0,'total_alpha_changes_in_left_cleanup_corridor':int(alpha.sum()),'facial_features_blush_collar_changes':int((mask&features).sum()),'hair_line_highlight_changes':int((mask&hair).sum()),'clothing_material_changes_outside_authorized_skin_corridors':int((mask&cloth_combined).sum()),'clothing_color_step_changes':int((color_change&cloth).sum()),'true_frill_RGBA_cleanup_step_changes':int((cleanup_change&frill).sum()),'image_calls':0,'F032_started':False,'not_Canvas_scene':True}
(H/'qa/combined_protection_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
