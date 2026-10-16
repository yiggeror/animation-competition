// 剪辑表：全片按顺序的每个镜头。mod = 已经做好的镜头模块（导出 DURATION 和 renderFrame），没有就先用占位卡。
// line：'engine' 床单戏（js/lamp 光照引擎），'paint' 屋内镜头（js/paint 背景图 + 程序打光），'code' 纯程序画（手机屏等）。
// 时长按 docs/preproduction/beat-sheet.md 的节拍，比原镜头表（34 个）压缩、合并了一些动作；总长约 4 分 40 秒。
export const SHOTS = [
  // 第 1 场 · 闷（日光灯）
  { id: 'S01', scene: 1, line: 'paint', dur: 12, text: '全景：吊扇转、蚊香烟、电视亮着；小满趴在竹席上玩手机，奶奶坐矮凳剥毛豆，推过来一块西瓜，小满摇头' },
  { id: 'S02', scene: 1, line: 'code', dur: 4, text: '特写：手机屏幕，游戏画面 + 电量 2%' },
  { id: 'S03', scene: 1, line: 'paint', dur: 6, text: '中近景：奶奶剥一颗豆，看一眼小满，自己咬一口西瓜' },
  // 第 2 场 · 停电
  { id: 'S04', scene: 2, line: 'paint', dur: 8, text: '全景："啪"——灯灭、电视缩成一个亮点、吊扇慢慢停；月光从窗口斜进来' },
  { id: 'S05', scene: 2, line: 'code', dur: 4, text: '特写：手机 1%，手指狂按，屏幕黑' },
  { id: 'S06', scene: 2, line: 'paint', dur: 8, text: '近景（月光）：小满跪在插座前，拔了又插，瞪着插座，狠狠插回去' },
  { id: 'S07', scene: 2, line: 'paint', dur: 5, text: '全景：小满往后一倒瘫在竹席上扇风；奶奶起身走向立柜，踮脚摸马灯' },
  { id: 'S08', scene: 2, line: 'paint', dur: 6, text: '特写：奶奶划火柴、点灯芯、放下灯罩——暖光铺开' },
  // 第 3 场 · 手电
  { id: 'S09', scene: 3, line: 'paint', dur: 5, text: '中景（马灯侧光）：小满翻抽屉找到手电，按不亮，拍两下，亮' },
  { id: 'S10', scene: 3, line: 'paint', dur: 5, text: '手电光束扫过屋子，照到奶奶，奶奶眯起眼' },
  // 第 4 场 · 木箱
  { id: 'S12', scene: 4, line: 'paint', dur: 8, text: '中近景：奶奶打开木箱，拿起鹤对着马灯，彩色光斑落在箱盖上' },
  { id: 'S13', scene: 4, line: 'paint', dur: 5, text: '近景：小满盯着看 → 发现奶奶在看她 → 假装打哈欠，扭开头' },
  // 第 5 场 · 搭台
  { id: 'S14', scene: 5, line: 'paint', dur: 10, text: '全景：奶奶把床单搭上铁丝、夹衣夹、挂马灯，床单亮起；小满拖板凳坐下，抱起胳膊' },
  // 第 6 场 · 鹤
  { id: 'S15', scene: 6, line: 'engine', dur: 5, mod: 'js/lamp/s06_key.js', text: '床单正面：鹤亮相，昂首；小满抱着胳膊 → 看呆了' },
  { id: 'S16', scene: 6, line: 'engine', dur: 8, mod: 'js/lamp/shots/s16.js', text: '床单正面：鹤踱步、梳毛、啄水（慢慢推近）' },
  // 第 7 场 · 乌龟
  { id: 'S17', scene: 7, line: 'engine', dur: 14, mod: 'js/lamp/shots/s17.js', text: '床单正面：乌龟爬进来；鹤啄空、一头撞在龟壳上、晕了' },
  { id: 'S18', scene: 7, line: 'engine', dur: 3, text: '近景：小满"噗"地笑出声，捂住嘴' },
  // 第 8 场 · 上手
  { id: 'S20', scene: 8, line: 'engine', dur: 9, text: '后台（机位 C）：奶奶把乌龟交给小满；签子缠在一起，乌龟翻了肚皮；奶奶笑弯了腰' },
  { id: 'S21', scene: 8, line: 'engine', dur: 6, mod: 'js/lamp/shots/s21.js', text: '床单正面：乌龟的影子忽大忽小、忽清忽虚，鹤"笑"得前仰后合' },
  { id: 'S22', scene: 8, line: 'engine', dur: 5, text: '特写（后台）：奶奶从后面握住小满握签子的手——慢一点；乌龟一步步爬起来' },
  { id: 'S23', scene: 8, line: 'engine', dur: 5, mod: 'js/lamp/shots/s23.js', text: '床单正面：乌龟伸长脖子咬住鹤嘴，鹤僵住；后台小满得意地看奶奶' },
  // 第 9 场 · 小狗
  { id: 'S25', scene: 9, line: 'engine', dur: 6, text: '后台：小满把手电架在木箱上，两只手伸进光里比出小狗' },
  { id: 'S26', scene: 9, line: 'engine', dur: 18, mod: 'js/lamp/shots/s26.js', text: '床单正面：暖的皮影、冷的狗影；小狗追鹤，乌龟骑在狗背上，越演越快' },
  // 第 10 场 · 来电
  { id: 'S27', scene: 10, line: 'engine', dur: 5, mod: 'js/lamp/shots/s27.js', text: '床单正面（硬切进惨白）：日光灯闪两下亮了，影子几乎看不见' },
  { id: 'S28', scene: 10, line: 'paint', dur: 8, text: '全景（日光灯）：吊扇转起、电视嘶响、一地毛豆壳；两人被晃得眯眼；竹席上手机亮起充电图标' },
  // 第 11 场 · 收
  { id: 'S29', scene: 11, line: 'paint', dur: 12, text: '奶奶笑笑，开始用布包皮影；手机"叮咚"开机；小满看看手机，又看看奶奶' },
  // 第 12 场 · 关灯
  { id: 'S30', scene: 12, line: 'paint', dur: 12, text: '全景：小满走到门边，踮脚拉灯绳——"咔嗒"，暗了；马灯的光重新显出来' },
  { id: 'S31', scene: 12, line: 'engine', dur: 14, text: '床单正面：小满拿手电从下巴往上照、做鬼脸，举着乌龟晃一晃；鹤和乌龟又动起来' },
  // 第 13 场 · 尾声
  { id: 'S32', scene: 13, line: 'paint', dur: 15, text: '屋外，慢慢后退：家家户户白灯，只有这扇窗暖黄，窗里鹤和乌龟的影子；片名"来电"' },
  { id: 'END', scene: 0, line: 'code', dur: 15, text: '字幕' },
];
export const TOTAL = SHOTS.reduce((s, x) => s + x.dur, 0);
