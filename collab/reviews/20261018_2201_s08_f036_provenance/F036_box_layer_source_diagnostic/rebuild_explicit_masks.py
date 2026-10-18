from pathlib import Path
from PIL import Image
import numpy as np
O=Path(__file__).resolve().parent;R=O.parent;H=O/'history_before_layer_correction'
def rgba(p):return np.array(Image.open(p).convert('RGBA'))
a=rgba(R/'F036_color_final/candidates/S08_F036_whole_turn_same_raw_final_color_RGBA.png');n=rgba(H/'F036_FINAL_LOCKED/F036_true_near_hand_match_INDEPENDENT_FOREGROUND_RGBA.png');f=rgba(H/'F036_FINAL_LOCKED/F036_complete_underlying_far_hand_jade_AND_TRANSPARENT_SEAT_RGBA.png');d=np.array(Image.open(H/'F036_FINAL_LOCKED/F036_near_distal_hard_guard_footprint.png'))>0;yy,xx=np.indices(n.shape[:2]);bbox=(xx>=1190)&(xx<=1207)&(yy>=795)&(yy<=809)
blue=bbox&(n[:,:,3]>0)&(n[:,:,2].astype(int)-n[:,:,0].astype(int)>35)&~d&np.all(a==f,axis=2);assert blue.sum()==53;assert (blue&(n[:,:,3]==255)).sum()==10
Image.fromarray((blue*255).astype('uint8')).save(O/'EXCLUDE_near_archive_old_blue_collar_NOT_HAND.png')
oldbox=rgba(R/'F033_LAYER_PARTITION/frames/F033_table_box_original_pixels.png');newbox=rgba(H/'F036_LAYER_PARTITION/frames/F036_table_box_original_pixels.png');extra=(newbox[:,:,3]>0)&(oldbox[:,:,3]==0);assert extra.sum()==483
Image.fromarray((extra*255).astype('uint8')).save(O/'EXTRA483_original033_body_box_fringe.png')
print('53archivecollar +483originalbodyfringe masks rebuilt')
