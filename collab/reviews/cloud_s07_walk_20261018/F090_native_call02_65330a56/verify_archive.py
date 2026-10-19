"""Read-only frozen-call/source/replay checks; never invokes generation."""
from pathlib import Path
from io import BytesIO
import base64,hashlib,json,subprocess
from PIL import Image
import numpy as np

P=Path(__file__).resolve().parent
REPO=P.parents[3]
COMMIT='65330a56639246c622ae3ad7881b9378fb9bd98f'
PREFIX='collab/reviews/cloud_s07_walk_20261018/F090_corrected_volume_input_gate_20261019/'


def j(path):return json.loads(path.read_text())
def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    frozen=P/'frozen_input_65330a56'
    count=0
    for f in frozen.rglob('*'):
        if f.is_file():
            assert f.read_bytes()==subprocess.check_output(['git','show',COMMIT+':'+PREFIX+str(f.relative_to(frozen))],cwd=REPO),str(f)
            count+=1
    args=j(P/'requests/arguments_call02_EXACT.json')
    assert args==j(frozen/'requests/arguments_PREPARED_NOT_CALLED.json')
    assert args['prompt']==(P/'requests/prompt_call02_EXACT.txt').read_text()
    for path,row in zip(args['referenced_image_paths'],j(frozen/'geometry/preparation_checks.json')['inputs']):
        assert Path(path).read_bytes()==(frozen/row['path']).read_bytes()
    raw_bytes=(P/'originals/F090_call02_RAW.png').read_bytes()
    identity=j(P/'originals/source_identity.json')
    assert sha(raw_bytes)==identity['sha256']
    assert raw_bytes==base64.b64decode(j(P/'requests/call02_raw_tool_return.json')['image_url'].split(',',1)[1])
    host=Path(identity['host_path'])
    if host.exists():assert host.read_bytes()==raw_bytes
    raw=np.array(Image.open(BytesIO(raw_bytes)).convert('RGBA'))
    mask=np.array(Image.open(P/'masks/RAW_whole_native_trousers_material.png'))>0
    extracted=np.array(Image.open(P/'production_layers/RAW_whole_native_trousers_EXTRACTED_ORIGINAL_RGB.png').convert('RGBA'))
    assert raw.shape==(1536,1024,4)
    assert np.array_equal(extracted,np.where(mask[:,:,None],raw,0))
    local=Image.fromarray(extracted).resize((540,810),Image.Resampling.LANCZOS)
    pants=Image.new('RGBA',(1672,1080));pants.alpha_composite(local,(1080,250))
    assert np.array_equal(np.array(pants),np.array(Image.open(P/'production_layers/F090_call02_actual_whole_trousers_ORIGINAL_COLOR.png')))
    layers={}
    for f in (frozen/'production_reference_layers').glob('*.png'):
        assert f.read_bytes()==(P/'production_layers'/('SOURCE_'+f.name)).read_bytes()
        layers[f.stem]=Image.open(f).convert('RGBA')
    replay=Image.new('RGBA',(1672,1080))
    for im in [layers['F090_far_shoe_ankle_LANDED'],pants,layers['F090_far_complete_arm_jade_hand'],layers['F090_body_head_blouse'],layers['F090_near_complete_arm'],layers['F090_near_shoe_ankle_SUPPORT_FIXED']]:replay.alpha_composite(im)
    candidate=P/'candidate/F090_call02_complete_trousers_PENDING_ASTRA.png'
    assert np.array_equal(np.array(replay),np.array(Image.open(candidate)))
    state=j(P/'requests/execution_state.json')
    assert state['call02_requests_sent']==state['call02_originals_received']==1
    assert state['automatic_retry_authorized'] is False and state['F095_unopened'] is True
    reg=j(P/'qa/actual_shoe_and_blouse_registration.json')
    delta=reg['actual_minus_frozen_sole_material_centroid_delta_native_px']
    assert max(abs(v)for xy in delta for v in xy)<.5
    palette=j(P/'qa/assembly_source_and_material_checks.json')['material_interiors']
    current=np.array(palette['call02']['interior_mean_RGB'])
    assert all(np.max(np.abs(current-np.array(palette[k]['interior_mean_RGB'])))<2 for k in ['F057','F062'])
    delivery=P/'DELIVERY_SHA256.json'
    if delivery.exists():
        for row in j(delivery)['files']:assert sha((P/row['path']).read_bytes())==row['sha256'],row['path']
    print(json.dumps({'status':'PASS_ARCHIVE_SOURCE_AND_CANDIDATE_REPLAY_PENDING_ASTRA','frozen_files_equal_approved_git':count,'call02_requests':1,'call02_originals':1,'F090_total_requests':2,'F090_total_originals':2,'source_layer_files_unchanged':5,'actual_whole_pants_original_RGB':True,'candidate_SHA256':sha(candidate.read_bytes()),'F095_unopened':True}))


if __name__=='__main__':main()
