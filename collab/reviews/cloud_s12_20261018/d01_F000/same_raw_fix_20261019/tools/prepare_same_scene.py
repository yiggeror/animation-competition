from pathlib import Path
import json,hashlib,subprocess,re,shutil
R=Path.cwd();P=R/'collab/reviews/cloud_s12_20261018/d01_F000';O=P/'same_raw_fix_20261019';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=(P/'scene/s12_F000_scene.js').read_text();s=source.replace("'../../../../../js/","'../../../../../../js/").replace("'../../geometry/three_key_pose_proposal.json'","'../../../geometry/three_key_pose_proposal.json'")
# The sole scene-content edit: a shallow cloth depression and thin contact line, behind unchanged code crane.
fold="""
function clothPressureFold(x){
 x.save();
 const path=new Path2D();path.moveTo(1010,800);path.lineTo(1850,800);path.lineTo(1838,764);path.lineTo(1022,764);path.closePath();x.clip(path);
 // A small blue cloth fold dips under the visible right belly edge;wood/box geometry stays untouched.
 x.fillStyle='rgba(17,29,49,0.44)';x.beginPath();x.moveTo(1438,793);
 x.bezierCurveTo(1462,790,1489,800,1510,797);x.bezierCurveTo(1524,795,1537,789,1547,790);
 x.lineTo(1547,796);x.bezierCurveTo(1524,801,1496,802,1475,799);x.lineTo(1438,798);x.closePath();x.fill();
 x.strokeStyle='rgba(12,19,31,0.72)';x.lineWidth=1.5;x.lineCap='round';x.beginPath();x.moveTo(1445,796);
 x.bezierCurveTo(1466,795,1486,801,1509,797);x.stroke();
 x.strokeStyle='rgba(110,139,176,0.42)';x.lineWidth=1;x.beginPath();x.moveTo(1486,787);x.quadraticCurveTo(1512,794,1538,788);x.stroke();
 x.restore();
}
"""
needle='  return c;\n}\nlet FRONT = null;';assert s.count(needle)==1;s=s.replace(needle,'  clothPressureFold(x);\n  return c;\n}\n'+fold+'let FRONT = null;')
(O/'scene/s12_F000_scene.js').write_text(s)
meta=json.loads((P/'qa/native_alpha_contacts_registration.json').read_text());meta['native_candidate_SHA256']=sha(O/'candidate/F000.png');meta['source_raw_SHA256']=sha(P/'originals/F000_raw_attempt03.png');meta['registration_Astra_approved_for_F000']=True;meta['registration_reason']='Astra reviewed41cb60c F000 pose and this frame camera/placement;unchanged in same-raw repair.'
for c in meta['contacts']:c['path']=c['path'].replace('../contact_masks/','../../contact_masks/')
(O/'qa/native_alpha_contacts_registration.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n');shutil.copyfile(P/'tools/network_audit_chromium.cjs',O/'tools/network_audit_chromium.cjs')
# Byte-level proof of preserved relevant functions, after the path-only entry adaptation.
def section(text,start,end):return text[text.index(start):text.index(end,text.index(start))]
for a,b in [('async function room()','const lidPoly'),('function front()','function nativeContactShadows'),('function nativeContactShadows','function propAndRestingRods'),('function propAndRestingRods','let cachedShadows')]:assert section(s,a,b)==section(source,a,b),a
assert s[s.index('const sstep='):]==source[source.index('const sstep='):]
seen=set()
def visit(p):
 if p in seen:return
 seen.add(p)
 for spec in re.findall(r'''(?:from\s*|import\s*)['"]([^'"]+)['"]''',p.read_text()):
  if spec.startswith('.'):
   q=(p.parent/spec).resolve()
   if q.suffix=='.js':visit(q)
visit(O/'scene/s12_F000_scene.js');files=set(seen)
for p in [O/'candidate/F000.png',O/'qa/native_alpha_contacts_registration.json',R/'collab/reviews/cloud_s12_20261018/geometry/three_key_pose_proposal.json',R/'assets/paint/bg_01_room_wide.png',R/'tools/js/frames.cjs',R/'tools/js/serve.cjs',R/'dev/view.html',R/'assets/fonts/MaShanZheng-Regular.ttf',R/'assets/fonts/NotoSansSC-VF.ttf']+list((P/'contact_masks').glob('*.png')):files.add(p)
rows=[]
for p in sorted(files):
 rel=str(p.relative_to(R));fixed=rel.startswith(('js/','assets/','tools/','dev/'))
 if fixed:assert p.read_bytes()==subprocess.check_output(['git','show','41cb60c5a9703fc22e62553840f9523e4ae3fad5:'+rel])
 rows.append({'path':rel,'sha256':sha(p),'basis':'fixed41cb60c_shared' if fixed else 'owned_same_F000_assets'})
(O/'qa/runtime_source_manifest.json').write_text(json.dumps({'base_delivery_commit':'41cb60c5a9703fc22e62553840f9523e4ae3fad5','rows':rows,'room_front_shadow_prop_light_camera_functions_exact':True,'crane_plane55_and_rod_endpoints_exact':True,'only_scene_content_change':'clothPressureFold inside original cloth polygon atx1438..1547,y787..802,frontpanelstilloccludesy800+','box_registration':{'x0':1000,'x1':1860,'rim':800,'back':760,'floor':1040},'native_registration':{'scale':.70,'x':275,'y':112},'new_frame_numbers':[0]},ensure_ascii=False,indent=2)+'\n')
(O/'provenance/astra_zero_generation_repair_authorization.md').write_text('''Source thread:01a0fbb9-4718-7063-bf5b-9bf34d41700f

“S12 F000 第3稿主/独实看：身份、完整跪坐、双手空起势和本帧机位可保留。先同raw修色并清边再锁母：以03同材质区校肤色偏橘、蓝衫偏深饱和，裤色/线稿/alpha核心不重调；去轮廓外游离低alpha，保细发镜框。鞋可解释为底面朝上，近手拇指可被遮住，勿误判反脚/缺指而重生。箱内保持原55°/杆靠左沿，仅给鹤腹压布补小凹折和贴合暗线，别改角度/箱体。锁母前后用灰/深底及同实际F000核一次；未放后态。”

本轮零生成，沿41cb60c第3原件；源与变化mask保全，只在本独占review交付，未改共享实现或S24九图。
''')
print('preserved source functions exact;manifest',len(rows),'inputs;onlysmallclothpressureadd')
