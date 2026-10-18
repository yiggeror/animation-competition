# 给 Opus：S23→S24 幕上咬合与承接的集中处理

固定审查 commit：155d25986b9d6bb38acc8f09043ca74922e4dd16。

实际S24整景60f审查未过：F059明确脱咬；F000/F040的轮廓相交实为喙越过龟颈，不能按嘴部咬合通过。人物九图已锁且不重开；相机、曝光、材色、曝光表保持。共享EDL/audio不动。

根因：S23把龟和鹤独立摆动，没有接点约束；S24又调用sheet23(3.4+.1*t)，回拨S23甩头中段。原S23末(4.958333秒)shake=0，但S24首为-0.287903。仅把S24某历史帧冻结，不能解决接嘴与跨镜连续。

建议最小接点公式如下。这是建议文本，不是已写入共享源码的实现，也未生成修后画面。

```js
// In S24's own scene_candidate/s24_drawn.js only, if a local wrapper is needed:
import { solve, pointOn } from '../../../../js/puppet.js';
import { turtleRods } from '../../../../js/lamp/choreo.js';

const MOUTH_MM = [57 * 1.3, -4 * 1.3];
const BILL_HOLD_MM = [126 * 1.35, 1 * 1.35];

function anchorWorld(actor, local) {
  const q = pointOn(actor.pup, solve(actor.pup, actor.pose), 'head', local);
  return [
    actor.root[0] + (actor.pose.facing ?? 1) * q[0] / 1000,
    actor.root[1] + q[1] / 1000,
  ];
}

function clampBite(actors, env) {
  const turtle = actors.find(a => a.pup.name === 'turtle');
  const crane = actors.find(a => a.pup === env.crane);
  if (!turtle || !crane || turtle.dist !== crane.dist) {
    throw new Error('S24 bite constraint requires the existing turtle/crane on one sheet plane.');
  }
  const m = anchorWorld(turtle, MOUTH_MM);
  const b = anchorWorld(crane, BILL_HOLD_MM);
  const root = [turtle.root[0] + b[0] - m[0], turtle.root[1] + b[1] - m[1]];
  return actors.map(a => a !== turtle ? a : {
    ...a,
    root,
    rods: turtleRods(root, turtle.pose.facing ?? -1),
  });
}
```

该公式保留两个角色原骨角/rootAngle，鹤完全不动，龟root由嘴部接点求出，并把签子手端同步。两个角色同为dist=.004，灯投影放大一致，世界接点重合会保持幕上/相机投影重合。选定喙握点位于喙尖内13.5mm，须实际图验证插入深度及嘴线可读；锚点相等不等于已经视觉通过。

若暂时对现入口做局部候选：`sheet:(u,env)=>clampBite(sheet23(3.4+.1*u,env),env)` 可以保现有角度摆动并消除接点漂移，但这不是跨镜完成版，因为仍回拨。不得凭该版直接签整景ready。

**必要的共享S23同步，由Opus负责：**

1. 把同一接点公式放入S23既有actor状态构造末端。在已有咬合建立1.2–1.6秒内，以原bite=sstep(1.2,1.6,t)连续混合龟原root与约束root；t≥1.6后必须完全锁定。每帧重建龟签子，保留已有伸颈、龟/鹤角度、甩头节奏和角色距离，不另换剧情。
2. 修后S23末态必须实际确认嘴线夹住喙且龟壳/签子没有出界。原末态需要约(+0.115834,-0.053842)m的龟root补偿，所以不是“现在已经咬住，只补末帧”即可。
3. S24优先改成读取修后S23的DURATION=5秒终态并保持，结束3.4秒回拨。原S24源码注释本已要求“鹤僵住、乌龟叼着不放”，因此终态保持符合已有剧情。取5秒也与S23最后采样119/24秒相邻，主体的shake/root/颈头均已稳定；若冻结整个pose，龟尾也按这一终态固定。
4. 如果导演要求S24继续摇摆，请明确后续曲线并从修后S23终态开始；不要直接重播历史3.4秒。接点约束可以保持任何批准的原角度曲线，但不能替导演决定重启甩头。
5. 不动人物9张PNG、其SHA、6/3/3/3/4/5/8/8/20曝光、B=.70+(590,20)、相机、曝光.22、雾.5、人物材色；不动共享EDL/audio和其他镜头。

验收必须是修后S23咬合建立/末→S24首、S24所有曝光边界和末停实际解码与原速切镜，重点看嘴而不是任意轮廓相交。保留S24完整60f/1080p24fps/2.5s无声。此审查没有写实现或重渲染。
