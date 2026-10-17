from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;S=Path('/workspace/animation-competition/assets/chars/g03_watermelon.png');sha=hashlib.sha256(S.read_bytes()).hexdigest()
common='''以附图 g03_watermelon 为唯一身份和构图母版，编辑一张动画关键帧。必须同一个奶奶、同一镜头和坐姿、同一裁切长宽比例（母版941×1212），不能缩放或挪动整个人，头顶与最下方衣裤保留原裁切。灰白头发发髻、三颗红发珠、圆眼镜、眼镜腿、蓝色白花短袖衬衫、纽扣、深蓝裤子保持原样。画面右的持瓜手是奶奶解剖左手，只有这一只腕有一只绿色玉镯；画面左的解剖右手裸腕，继续放在腿上，右手指形和落点不变。不要增加手、手指、戒指、第二只镯。
西瓜始终是母版这一小块半月形西瓜，绿条纹瓜皮、白瓤厚度、红瓤与黑籽布置、已有的上边咬痕保持识别。西瓜和原来抓住它的左掌/手指作为一组移动；拇指压在原来的瓜皮前边，手指托住同一位置，不能让瓜悬浮、穿掌、滑脱或换成新瓜。允许左肩肘腕自然连动以达到下述动作，保持正常肢体长度，不能只搬西瓜把胳膊留在旧姿势。除了明确的嘴部接触咬态，其余帧不要增加缺口。
腰以下的坐姿、最下部蓝衣摆与深蓝裤子完全保持母版形状/花纹/边线，尤其母版(165,1084)、(843,1147)、(594,1111)附近衣摆裤缝不变；它们只是图卡配准参考，不要把点标记画出来。脸保持同一身份/原年龄，只做要求的小表情；不新增豆盆、豆荚、板凳、桌子、其他道具或背景。平光，保持已有透明背景alpha，不新增灰底矩形；不写文字，不画骨架线。
本帧动作：'''
poses={
'k02':('持瓜低眼眨眼','瓜、左手和臂维持母版原位置。奶奶眼睛轻轻闭到眨眼的中途/接近闭合，视线原先低看瓜，嘴角从母版浅笑收成平静的小闭唇。头位与肩基本不动，不是嚼瓜，不张嘴。'),
'k03':('递瓜途中','左手把瓜向画面左边的小满递出一半。瓜整体中心由母版约(565,660)到约(475,680)，只是中等幅度参考，不承诺数值。仍原瓜朝向，左掌紧跟瓜，肘向前自然打开，玉镯随腕。眼睛睁开并看向画面左外的小满，眉稍抬，嘴闭合温和，不露齿。右手仍搭膝。'),
'k04':('递瓜到位','左手把同一块瓜继续向画面左边小满递到位。瓜整体中心约(385,700)，比母版左移约180、下移40，左臂跨身向左前方伸，瓜仍完全在画幅内。左掌稳稳托握原瓜边，玉镯腕自然连前臂，肘不过度伸直。头和视线轻轻看左外，眉温和期待，嘴仍轻闭。身体和下半身不跟着搬移。'),
'k05':('递瓜停住眨眼','与递到位相同：同一瓜中心约(385,700)，左手/腕/臂仍保持自然递出的位置。只把眼睛改成一次温柔眨眼，眉头不皱，嘴闭合浅笑收一点，读成等对方回应，不是不耐烦。不能把手/瓜收回到母版位置。'),
'k06':('收瓜途中','没有等到小满接瓜，左手把已递出的瓜收回一半。瓜中心约(475,680)，与母版相比仍偏左约90，握持原位、玉镯随腕、肘自然弯回。眼睛睁开后视线落向瓜，嘴角平静收住，表现轻淡的“随你”，不是生气或失望苦脸。不能捏碎西瓜或新增咬痕。'),
'k07':('嘴边将咬','把同一块有旧咬痕的西瓜抬到自己嘴边，但红瓤尚未接触嘴。瓜中心大约(410,510)，比母版左移和上移约150；原有上边咬口在嘴下前方留约20–30个母版像素空隙。奶奶嘴小幅张开准备咬，眼睛略向下看瓜；嘴只自然张一小口，不露夸张整排牙。左手/镯/腕跟同一瓜同步抬起，肘弯曲靠身，右手仍膝上。保持肩和头整体机位，不把头夸张探过去。'),
'k08':('实际咬合接触','同一瓜抬到嘴，原有咬口边缘真正接到上下唇之间。瓜中心约(400,490)，原红瓤上沿靠近母版嘴约(335,412)；嘴唇/牙口自然夹住红瓤的一个小位置，不能隔空咬。眼睛轻眯，嘴不是大笑，不画液体飞溅。左掌始终握原来瓜皮位置，玉镯在原左腕。旧缺口可以在这一口接触处极轻微增大一点；瓜皮弧形、其余轮廓和籽不重画成另一块。'),
'k09':('咬后嚼A','咬过这一口后，把瓜从嘴边略放下，瓜中心约(440,580)，上沿与嘴明确分开。已有旧缺口在这一口接触处仅有很小的新增缺口，其余瓜皮弧形与籽保持。嘴唇闭合，腮帮一侧仅轻鼓一点点，眼睛平静睁开略看左外，表现淡淡的“随你”，不夸张笑。左腕手瓜成组下降，左肘自然回收，右手留膝。'),
'k10':('咬后嚼B','和嚼A相同姿态：瓜中心约(440,580)，离嘴并保持同样的小新增缺口。嘴闭合，下颌比嚼A轻轻压下一点再合、双颊回平，眼睛轻眨到半闭，眉放松，不皱成忧愁。只做微小咀嚼表情与几像素握瓜落稳，瓜和玉镯手的位置/朝向不要另换。')}
requests=[]
for k,(name,action) in poses.items():
 q={'key':k,'pose':name,'source':str(S),'source_sha256':sha,'referenced_image_paths':[str(S)],'transparent_background':True,'prompt':common+action,'author_scope':'Only requested pose editing, no added bean action/props. First bean-action interval remains unresolved editorial dependency.'}
 (P/'requests'/f'{k}.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');requests.append(q)
(P/'requests.json').write_text(json.dumps(requests,ensure_ascii=False,indent=2)+'\n')
plan={'source_sha256':sha,'source_size':[941,1212],'anchors':[[165,1084],[843,1147]],'holdout':[594,1111],'anchors_are':'fixed lower-garment/trouser features only, not static scene props; assumed unchanged seated lower body must be visually checked','keys':['k01']+list(poses),'generation_count_planned':9,'timeline_draft':[[0,0],[18,1],[21,0],[30,2],[42,3],[54,4],[57,3],[69,5],[75,0],[81,6],[91,7],[102,8],[111,9],[120,8],[129,9],[138,8]],'fps':24,'total_frames':144,'bite_frame':91,'crunch_frame':96,'opening_dependency':'No bean basin exists in mother. Bean shelling belongs to story and is not claimed completed here; root/Opus deciding g01 insert or timing.'}
(P/'motion_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
