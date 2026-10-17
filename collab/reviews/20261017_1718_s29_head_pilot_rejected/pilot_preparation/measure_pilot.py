#!/usr/bin/env python3
"""Read-only fixed-window NCC audit. Fits A+B only; H is held out.

No image generation, file edits, image outputs, adaptive search, local deformation,
RANSAC, optical flow or production render. The globally aligned in-memory image is
used only to compute diagnostics. A numeric pass always requires visual review.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import affine_transform
from scipy.signal import fftconvolve

HERE = Path(__file__).resolve().parent
MASTER = HERE.parent / 'refs/x29_look_a.png'
MASTER_SHA256 = 'f20ba5137ad60169950c2d3019218cb9d9fe880985c1c0d3841d4f72895bfff7'

def load_config(path=None):
    return json.loads(Path(path or HERE/'measurement_config.json').read_text())

def apply_similarity(points, matrix):
    pts = np.asarray(points, dtype=float)
    return pts @ np.asarray(matrix, dtype=float)[:, :2].T + np.asarray(matrix)[:, 2]

def solve_two_point_similarity(candidate_points, target_points):
    src = np.asarray(candidate_points, dtype=float)
    dst = np.asarray(target_points, dtype=float)
    if src.shape != (2, 2) or dst.shape != (2, 2):
        raise ValueError('Exactly two points are allowed; H must never enter the fit.')
    v, w = src[1]-src[0], dst[1]-dst[0]
    denom = float(v @ v)
    if denom < 1e-9 or float(w @ w) < 1e-9:
        raise ValueError('Degenerate registration pair.')
    a = float(v @ w) / denom
    b = float(v[0]*w[1]-v[1]*w[0]) / denom
    linear = np.array([[a, -b], [b, a]])
    shift = dst[0] - linear @ src[0]
    return np.column_stack((linear, shift))

def rgba_array(im):
    return np.asarray(im.convert('RGBA'), dtype=np.float32)

def premultiplied(arr):
    out = np.array(arr, dtype=np.float32, copy=True)
    out[:, :, :3] *= out[:, :, 3:4] / 255.
    return out

def grayscale_visible(im, gray):
    arr = rgba_array(im)
    a = arr[:, :, 3:4]/255.
    rgb = arr[:, :, :3]*a + float(gray)*(1-a)
    return rgb @ np.array([.299, .587, .114], dtype=np.float32)

def _subpixel(values, index):
    if index <= 0 or index >= len(values)-1:
        return float(index)
    denominator = values[index-1]-2*values[index]+values[index+1]
    delta = .5*(values[index-1]-values[index+1])/denominator if abs(denominator)>1e-12 else 0
    return index + float(np.clip(delta, -.5, .5))

def match_anchor(master_gray, candidate_gray, definition, config):
    x0, y0, x1, y1 = definition['patch_xyxy']
    radius = config['search_radius_px']
    if min(x0-radius, y0-radius) < 0 or x1+radius > candidate_gray.shape[1] or y1+radius > candidate_gray.shape[0]:
        raise ValueError('Frozen search window must be entirely inside the canvas.')
    template = master_gray[y0:y1, x0:x1].astype(float)
    win = candidate_gray[y0-radius:y1+radius, x0-radius:x1+radius].astype(float)
    template -= template.mean()
    energy = float((template*template).sum())
    if energy < 1e-8:
        raise ValueError('Frozen template is textureless; choose/freeze before generation.')
    n = template.size
    ones = np.ones(template.shape)
    sums = fftconvolve(win, ones, mode='valid')
    sums2 = fftconvolve(win*win, ones, mode='valid')
    numerator = fftconvolve(win, template[::-1, ::-1], mode='valid')
    denominator = np.sqrt(np.maximum(sums2-sums*sums/n, 0)*energy)
    ncc = np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator>1e-9)
    ncc = np.clip(ncc, -1., 1.)
    iy, ix = np.unravel_index(np.argmax(ncc), ncc.shape)
    fx = _subpixel(ncc[iy], ix); fy = _subpixel(ncc[:, ix], iy)
    px, py = definition['point']
    q = [px-radius+fx, py-radius+fy]
    yy, xx = np.indices(ncc.shape)
    outside = (xx-ix)**2+(yy-iy)**2 > config['second_peak_exclusion_radius_px']**2
    second = float(ncc[outside].max()) if outside.any() else -1.
    return {'point':q, 'ncc':float(ncc[iy,ix]), 'peak_margin':float(ncc[iy,ix]-second),
            'peak_on_search_boundary': bool(ix in (0,ncc.shape[1]-1) or iy in (0,ncc.shape[0]-1)),
            'fixed_template_xyxy':[x0,y0,x1,y1],
            'fixed_search_window_xyxy':[x0-radius,y0-radius,x1+radius,y1+radius]}

def globally_registered_for_metrics(candidate, candidate_to_master, output_shape):
    matrix = np.vstack((candidate_to_master, [0.,0.,1.]))
    inverse = np.linalg.inv(matrix)
    # scipy uses (row=y, col=x), opposite the documented x/y landmarks.
    yx_matrix = inverse[:2,:2][::-1, ::-1]
    yx_offset = inverse[:2,2][::-1]
    premul = premultiplied(rgba_array(candidate))
    aligned = np.empty((*output_shape,4),dtype=np.float32)
    for channel in range(4):
        affine_transform(premul[:,:,channel], yx_matrix, yx_offset,
                         output_shape=output_shape, output=aligned[:,:,channel],
                         order=1,mode='constant',cval=0.,prefilter=False)
    return aligned

def pixel_metrics(master_premul, candidate_premul, mask):
    delta = np.abs(master_premul-candidate_premul)
    valid = mask & ((master_premul[:,:,3]>0)|(candidate_premul[:,:,3]>0))
    if not valid.any():
        return {'pixels':0}
    ma = master_premul[:,:,3]>128; ca = candidate_premul[:,:,3]>128
    intersection = (ma & ca & mask).sum(); union = ((ma | ca)&mask).sum()
    return {'pixels':int(valid.sum()),
            'premultiplied_rgb_mae_255':float(delta[:,:,:3][valid].mean()),
            'premultiplied_rgb_p99_abs_255':float(np.percentile(delta[:,:,:3][valid],99)),
            'alpha_mae_255':float(delta[:,:,3][valid].mean()),
            'alpha_IoU_gt128':float(intersection/union) if union else 1.,
            'source_opaque_pixels_lost':int((ma & ~ca & mask).sum()),
            'extra_opaque_pixels':int((~ma & ca & mask).sum())}

def measure_images(master, candidate, config):
    failures = []
    result = {'numeric_failures':failures, 'candidate_to_master':None,
              'fit_points':['A','B'], 'independent_check_point':'H',
              'acceptance':'manual_structure_and_midpose_review_required',
              'automatic_visual_acceptance':False,
              'candidate_mode':candidate.mode, 'candidate_size':list(candidate.size)}
    if tuple(master.size) != tuple(config['canvas']):
        raise ValueError('Master canvas differs from frozen configuration.')
    if tuple(candidate.size) != tuple(config['canvas']):
        failures.append('canvas_must_be_1024x1536');return result
    if candidate.mode != 'RGBA':failures.append('RGBA_required')
    ca = rgba_array(candidate)
    if not (ca[:,:,3]==0).any():failures.append('missing_transparent_background')
    mg = grayscale_visible(master,config['alpha_composite_gray'])
    cg = grayscale_visible(candidate,config['alpha_composite_gray'])
    matches = {name:match_anchor(mg,cg,definition,config) for name,definition in config['anchors'].items()}
    result['matches'] = matches
    for name,match in matches.items():
        if match['ncc'] < config['ncc_minimum']:failures.append(name+'_NCC_below_frozen_minimum')
        if match['peak_on_search_boundary']:failures.append(name+'_peak_at_frozen_search_boundary')
        if match['peak_margin'] < config['ncc_peak_margin_minimum']:failures.append(name+'_ambiguous_template_peak')
    # H is deliberately absent from these two arrays and the solve call.
    fit = solve_two_point_similarity([matches[name]['point'] for name in ('A','B')],
                                   [config['anchors'][name]['point'] for name in ('A','B')])
    result['candidate_to_master'] = fit.tolist()
    heldout = apply_similarity([matches['H']['point']],fit)[0]
    residual = float(np.linalg.norm(heldout-np.array(config['anchors']['H']['point'])))
    result['independent_H_mapped_to_master'] = heldout.tolist()
    result['independent_H_residual_px'] = residual
    scale = float(np.hypot(fit[0,0],fit[1,0])); rotation = math.degrees(math.atan2(fit[1,0],fit[0,0]))
    result['global_similarity'] = {'scale':scale,'rotation_degrees':rotation,'translation_xy':fit[:,2].tolist(),
                                   'A_B_fit_residual_is_not_independent_evidence':True}
    if residual > config['H_residual_max_px']:failures.append('H_residual_above_3px')
    if abs(scale-1.) > config['similarity_scale_deviation_max']:failures.append('global_scale_deviation_above_frozen_limit')
    if abs(rotation) > config['similarity_rotation_abs_max_deg']:failures.append('global_rotation_above_frozen_limit')
    mp = premultiplied(rgba_array(master)); cp = premultiplied(ca)
    aligned = globally_registered_for_metrics(candidate,fit,mp.shape[:2])
    mask = np.zeros(mp.shape[:2],dtype=bool);mask[config['non_target_y_start']:]=True
    result['non_target_raw'] = pixel_metrics(mp,cp,mask)
    result['non_target_registered'] = pixel_metrics(mp,aligned,mask)
    result['protected_regions_registered'] = {}
    for name,(x0,y0,x1,y1) in config['protected_regions'].items():
        local = np.zeros_like(mask);local[y0:y1,x0:x1]=True
        result['protected_regions_registered'][name] = pixel_metrics(mp,aligned,local)
    x0,y0,x1,y1 = config['head_roi_xyxy'];head = np.zeros_like(mask);head[y0:y1,x0:x1]=True
    result['head_roi_registered_metrics_not_midpose_proof'] = pixel_metrics(mp,aligned,head)
    result['mandatory_visual_review'] = config['mandatory_review']
    if failures:result['acceptance']='reject_or_hold_no_rescue_warp_no_retry'
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate',type=Path,help='Original candidate; use master only for baseline self-check')
    parser.add_argument('--out',type=Path,required=True,help='JSON report inside pilot_preparation')
    args=parser.parse_args()
    out=args.out.resolve()
    if HERE not in out.parents:parser.error('Report output must remain in pilot_preparation.')
    if out.exists():parser.error('Refusing to overwrite an existing report; choose a new report name.')
    if hashlib.sha256(MASTER.read_bytes()).hexdigest()!=MASTER_SHA256:parser.error('Frozen master hash changed.')
    config_path=HERE/'measurement_config.json'; config=load_config(config_path)
    result=measure_images(Image.open(MASTER),Image.open(args.candidate),config)
    result.update({'master_file':str(MASTER),'master_sha256':MASTER_SHA256,
                   'candidate_file':str(args.candidate.resolve()),'candidate_sha256':hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
                   'frozen_config_sha256':hashlib.sha256(config_path.read_bytes()).hexdigest(),
                   'measurement_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({'report':str(out),'numeric_failures':result['numeric_failures'],
                      'H_residual_px':result.get('independent_H_residual_px'),'acceptance':result['acceptance']}))
    raise SystemExit(2 if result['numeric_failures'] else 0)

if __name__=='__main__':main()
