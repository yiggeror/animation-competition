// 剪辑表：全片按顺序的每个镜头。mod = 已经做好的镜头模块（导出 DURATION 和 renderFrame），没有就先用占位卡。
// line：'engine' 床单戏（js/lamp 光照引擎），'paint' 屋内镜头（js/paint 背景图 + 程序打光），'code' 纯程序画（手机屏等）。
// 时长按 docs/preproduction/beat-sheet.md 的节拍，比原镜头表（34 个）压缩、合并了一些动作；总长约 4 分 40 秒。
export const SHOTS = [
  // 第 1 场 · 闷（日光灯）。10-18 按"代码动画的节奏"重排：时长跟着信息走，每个动作只做一次，不循环（js/anim/，代码人物先定节奏，之后按姿势配画）
  { id: 'S01', scene: 1, line: 'paint', dur: 3.5, mod: 'js/anim/s01_drawn.js', text: '全景：吊扇转、蚊香烟被吹斜、电视亮着；小满趴在竹席上玩手机，奶奶坐矮凳剥毛豆' },
  { id: 'S02', scene: 1, line: 'code', dur: 2.5, mod: 'js/anim/s02.js', text: '特写：手机屏幕，游戏画面 + 电量 2%（插着充电）' },
  { id: 'S02a', scene: 1, line: 'paint', dur: 2.5, mod: 'js/anim/s02a_drawn.js', text: '近景：小满的脸被屏幕照蓝，差点输——眉毛一挑，躲过去了——嘴角一撇' },
  { id: 'S03', scene: 1, line: 'paint', dur: 4, mod: 'js/anim/s03_drawn.js', text: '中近景：奶奶抬眼看小满，笑了笑，拿起一块西瓜往她那边推过去，等着' },
  { id: 'S03a', scene: 1, line: 'paint', dur: 1.5, mod: 'js/anim/s03a_drawn.js', text: '近景：西瓜推到跟前，小满头也不抬，摇了一下头' },
  { id: 'S03b', scene: 1, line: 'paint', dur: 2, mod: 'js/anim/s03b_drawn.js', text: '近景：奶奶把西瓜收回来，自己咬了一口，嚼着——随你' },
  // 第 2 场 · 停电
  { id: 'S04', scene: 2, line: 'paint', dur: 3, mod: 'js/anim/s04_drawn.js', text: '全景："啪"——灯灭、电视缩成一个亮点、吊扇慢下来；奶奶的手停住，抬头看灯；小满还在玩' },
  { id: 'S04a', scene: 2, line: 'code', dur: 2, mod: 'js/anim/s04a.js', text: '特写：吊扇停了，蚊香的烟变成一根直直往上升的线' },
  { id: 'S05', scene: 2, line: 'code', dur: 3, mod: 'js/anim/s05.js', text: '特写：手机 1%，手指狂按——屏幕一暗、全黑，拇指停住' },
  { id: 'S05a', scene: 2, line: 'paint', dur: 2.5, mod: 'js/anim/s05a_drawn.js', text: '近景：小满的脸也黑了——愣住，"不是吧"，猛按电源键' },
  { id: 'S06', scene: 2, line: 'paint', dur: 86 / 24, mod: 'js/anim/s06_drawn.js', text: '特写（月光，侧面）：墙脚插座，小满拔下插头再插回去；再拔、吹一口、插回去——还是不亮' },
  { id: 'S07', scene: 2, line: 'paint', dur: 4.5, mod: 'js/anim/s07_drawn.js', text: '全景：小满放下手机、翻身仰躺，扇两下风；奶奶把盆放到脚边，撑着膝盖站起来，转身走到八仙桌边，伸手拿桌上的马灯' },
  { id: 'S08', scene: 2, line: 'paint', dur: 6, mod: 'js/anim/s08_drawn.js', text: '中景：奶奶在八仙桌边"嚓"地划着火柴，火光照亮脸；抬起灯罩，凑近点着灯芯，甩灭火柴；灯罩落下"叮"，暖光铺开，她看着灯笑了，往小满那边瞟一眼' },
  // 第 3 场 · 手电
  { id: 'S09', scene: 3, line: 'paint', dur: 4, mod: 'js/anim/s09_drawn.js', text: '近景（马灯从右边照过来）：小满跪在电视柜前捧着旧手电，推开关不亮，往手心磕两下，再推——亮了，光柱打出去' },
  { id: 'S10', scene: 3, line: 'paint', dur: 5, mod: 'js/anim/s10_drawn.js', text: '手电光束扫过屋子，照到奶奶，奶奶眯起眼' },
  // 第 4 场 · 木箱
  { id: 'S12', scene: 4, line: 'paint', dur: 8, mod: 'js/paint/shots/s12.js', text: '中景：樟木箱开着，奶奶跪在箱边俯身握住签子，直起身把鹤立起来，马灯的光透过牛皮，鹤影落在箱盖内侧' },
  { id: 'S13', scene: 4, line: 'paint', dur: 5, mod: 'js/anim/s13_drawn.js', text: '近景：小满盯着看 → 发现奶奶在看她 → 假装打哈欠，扭开头' },
  // 第 5 场 · 搭台
  { id: 'S14', scene: 5, line: 'paint', dur: 10, mod: 'js/paint/shots/s14.js', text: '全景：奶奶把床单搭上铁丝、夹衣夹、挂马灯，床单亮起；小满拖板凳坐下，抱起胳膊' },
  // 第 6 场 · 鹤
  { id: 'S15', scene: 6, line: 'engine', dur: 8, mod: 'js/anim/s15_drawn.js', text: '床单正面：鹤的大虚影从远处贴近床单、变清楚；亮相，昂首；小满抱着胳膊 → 看呆了' },
  { id: 'S16', scene: 6, line: 'engine', dur: 8, mod: 'js/lamp/shots/s16.js', text: '床单正面：鹤踱步、梳毛、啄水（慢慢推近）' },
  // 第 7 场 · 乌龟
  { id: 'S17', scene: 7, line: 'engine', dur: 14, mod: 'js/lamp/shots/s17.js', text: '床单正面：乌龟爬进来；鹤啄空、一头撞在龟壳上、晕了' },
  { id: 'S18', scene: 7, line: 'engine', dur: 3, mod: 'js/lamp/shots/s18.js', text: '近景：小满"噗"地笑出声，捂住嘴' },
  // 第 8 场 · 上手
  { id: 'S20', scene: 8, line: 'engine', dur: 9, mod: 'js/lamp/shots/s20.js', text: '后台（机位 C）：奶奶把乌龟交给小满；签子缠在一起，乌龟翻了肚皮；奶奶笑弯了腰' },
  { id: 'S21', scene: 8, line: 'engine', dur: 6, mod: 'js/lamp/shots/s21.js', text: '床单正面：乌龟的影子忽大忽小、忽清忽虚，鹤"笑"得前仰后合' },
  { id: 'S22', scene: 8, line: 'code', dur: 5, mod: 'js/anim/s22_drawn.js', text: '特写（后台）：奶奶从后面握住小满握签子的手——慢一点；乌龟一步步爬起来' },
  { id: 'S23', scene: 8, line: 'engine', dur: 5, mod: 'js/lamp/shots/s23.js', text: '床单正面：乌龟伸长脖子咬住鹤嘴，鹤僵住；后台小满得意地看奶奶' },
  { id: 'S24', scene: 8, line: 'engine', dur: 2.5, mod: 'js/anim/s24_drawn.js', text: '后台近景：小满回过头，得意地看奶奶' },
  // 第 9 场 · 小狗
  { id: 'S25', scene: 9, line: 'code', dur: 6, mod: 'js/anim/s25_drawn.js', text: '后台：小满把手电架在木箱上，两只手伸进光里比出小狗' },
  { id: 'S26', scene: 9, line: 'engine', dur: 18, mod: 'js/lamp/shots/s26.js', text: '床单正面：暖的皮影、冷的狗影；小狗追鹤，乌龟骑在狗背上，越演越快' },
  // 第 10 场 · 来电
  { id: 'S27', scene: 10, line: 'engine', dur: 5, mod: 'js/lamp/shots/s27.js', text: '床单正面（硬切进惨白）：日光灯闪两下亮了，影子几乎看不见' },
  { id: 'S28', scene: 10, line: 'paint', dur: 8, mod: 'js/paint/shots/s28.js', text: '全景（日光灯）：吊扇转起、电视嘶响、一地毛豆壳；两人被晃得眯眼；竹席上手机亮起充电图标' },
  // 第 11 场 · 收
  { id: 'S29', scene: 11, line: 'paint', dur: 12, mod: 'js/paint/shots/s29.js', text: '奶奶笑笑，开始用布包皮影；手机"叮咚"开机；小满看看手机，又看看奶奶' },
  // 第 12 场 · 关灯
  { id: 'S30', scene: 12, line: 'paint', dur: 12, mod: 'js/paint/shots/s30_drawn.js', text: '全景：小满走到门边，踮脚拉灯绳——"咔嗒"，暗了；马灯的光重新显出来' },
  { id: 'S31', scene: 12, line: 'paint', dur: 14, mod: 'js/paint/shots/s31_drawn.js', text: '床单前：小满把手电抵在下巴下往上照、做鬼脸，举着乌龟晃一晃；切床单正面：鹤跳起来，乌龟爬进来，又演起来了' },
  // 第 13 场 · 尾声
  { id: 'S32', scene: 13, line: 'code', dur: 15, mod: 'js/code/s32.js', text: '屋外，慢慢后退：家家户户白灯，只有这扇窗暖黄，窗里鹤和乌龟的影子；片名"来电"' },
  { id: 'END', scene: 0, line: 'code', dur: 9, mod: 'js/code/credits.js', text: '字幕；最后一张：竹席上小满的手机，锁屏壁纸换成床单上的鹤影，屏幕熄灭' },
];
export const TOTAL = SHOTS.reduce((s, x) => s + x.dur, 0);
