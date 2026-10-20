"""Copy only the adopted S12 tail blobs from the published handoff commit.

No generated art, person deformation, exposure interpolation, or prefix changes.
"""
from pathlib import Path
import hashlib, io, json, subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[5]
COMMIT = '4051f3ef4d00bd1234a2e7b8cf3524c82b262c43'
SOURCE = 'collab/reviews/20261020_s12_full192_handoff/tail/'
OUT = ROOT / 'assets/chars/g12'

def blob(relative):
    return subprocess.check_output(['git', '-c', 'gc.auto=0', 'show', COMMIT + ':' + SOURCE + relative], cwd=ROOT)

manifest = json.loads(blob('TAIL_EXPOSURE_MANIFEST.json'))
sequence = json.loads((OUT / 'sequence.json').read_text())
prefix = [s for s in sequence['states'] if s['start'] < 106]
assert prefix[-1]['end'] == 105
prepared, provenance = {}, []
for folder in dict.fromkeys(e['folder'] for e in manifest['timeline']):
    p = json.loads(blob(folder + '/prop_plan.json'))
    b, k = p['paper_3D_camera_basis'], p['mm_to_scene_scale']
    entry = {'registration': {'x': 0, 'y': 0, 'scale': 1}, 'background': prefix[-1]['background'],
             'prop': {'root': p['root_scene'], 'matrix': [[k*b[0][0], k*b[0][1]], [k*b[1][0], k*b[1][1]]],
                      'pose': p['code_pose'], 'free': {r: p['rods'][r]['free_scene'] for r in ['R', 'L']},
                      'paperDegrees': p['paper_plane_inclination_degrees']},
             'transmission': 0 if folder == 'F106' else 1}
    for side in ['BG', 'FG']:
        source = folder + '/scene_' + side + '.png'
        data = blob(source)
        im = Image.open(io.BytesIO(data)); im.load()
        assert im.size == (1920, 1080) and im.mode == 'RGBA', source
        sha = hashlib.sha256(data).hexdigest()
        name = folder + '_' + side + '_' + sha[:12] + '.png'
        (OUT / name).write_bytes(data)
        entry[side.lower()] = name
        provenance.append({'source': SOURCE + source, 'commit': COMMIT, 'asset': name, 'SHA256': sha, 'bytes': len(data)})
    # Retain the exact physical plan as provenance, including unchanged 3D rod lengths.
    (ROOT / 'collab/reviews/cloud_s12_20261018/formal_scene_20261020' / (folder + '_adopted_prop_plan.json')).write_bytes(blob(folder + '/prop_plan.json'))
    prepared[folder] = entry
tail = [dict(prepared[e['folder']], key=e['frames'][0], start=e['frames'][0], end=e['frames'][1], adoptedDrawing=e['drawing']) for e in manifest['timeline']]
assert [f for s in prefix + tail for f in range(s['start'], s['end'] + 1)] == list(range(192))
sequence.update(availableThrough=191, status='ADOPTED_FULL192_ACTUAL_CAM_PENDING', states=prefix + tail, tailAdoptionCommit=COMMIT)
(OUT / 'sequence.json').write_text(json.dumps(sequence, ensure_ascii=False, indent=2) + '\n')
(ROOT / 'collab/reviews/cloud_s12_20261018/formal_scene_20261020/tail_source_adoption.json').write_text(json.dumps(provenance, indent=2) + '\n')
print(json.dumps({'tailRows': len(tail), 'uniqueDrawings': len(prepared), 'verifiedRGBA': len(provenance), 'prefixRewritten': False}))
