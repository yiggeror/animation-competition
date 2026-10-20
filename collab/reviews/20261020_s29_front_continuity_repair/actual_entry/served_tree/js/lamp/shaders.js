// "一盏灯照亮的世界"的着色器。场景是真实尺寸（米）的屋子：
//   x 沿着床单（往右为正），y 往里（床单在 y = 0，后台 y > 0，看戏的这边 y < 0），z 往上。
// 每个像素从镜头射出一条光线，和屋子、床单、两床挂起来的被子求交，再按真实的光源算照度：
//   · 床单是面光源：把床单分成 8×6 小块，每块的亮度来自物理影子图（shadowplay.js），按 cosθ·cosθ' / r² 累加；
//   · 马灯在床单后面：看戏这边的点能不能看见火苗，取决于"点 → 灯"这条线穿过 y = 0 平面的位置有没有被床单、被子、
//     晾衣铁丝和夹子挡住；火苗和玻璃罩有大小，所以边缘有半影（半影宽 = 光源半径 × 点到布帘 / 点到灯）；
//   · 月光从右墙的窗户斜射进来（窗框的十字影子），人物会挡住床单光和月光，在地上留下软影子；
//   · 空气里有一点灰尘：沿视线积分散射光（同样判断马灯能不能照到），得到布帘上下沿漏出来的光柱。
// 人物和道具是"卡片"：2D 画好的固有色 + 由轮廓算出来的法线图 + 深度，在同一套光照里计算。

export function common(S) {
  const f = (v) => (Number.isInteger(v) ? v.toFixed(1) : String(v));
  const v3 = (a) => `vec3(${a.map(f).join(',')})`;
  return `#version 300 es
precision highp float;
precision highp int;
in vec2 uv; out vec4 o;
uniform vec2 uRes;
uniform vec3 uCam, uFwd, uRight, uUp; uniform float uFocal;
uniform vec3 uLamp; uniform float uLampI;
uniform float uFluor;   // 日光灯（来电）：0 = 关，1 = 亮
uniform vec3 uPatch[48];
uniform float uTime;
#define PI 3.14159265
const vec3 B0 = ${v3(S.room[0])}, B1 = ${v3(S.room[1])};
const vec4 SHEET = vec4(${[S.sheet.x0, S.sheet.x1, S.sheet.z0, S.sheet.z1].map(f).join(',')});
const vec4 QL = vec4(${S.quiltL.map(f).join(',')});   // 左边的被子 x0 x1 z0 z1
const vec4 QR = vec4(${S.quiltR.map(f).join(',')});   // 右边的毯子
const float PIN0 = ${f(S.pin0)}, PINDX = ${f(S.pinDx)};
const float LAMP_CORE = ${f(S.lamp.core)}, LAMP_GLOBE = ${f(S.lamp.globe)};
const vec3 LAMP_RGB = ${v3(S.lamp.rgb)};
const vec3 MOON_L = normalize(${v3(S.moon.dir)});
const vec3 MOON_RGB = ${v3(S.moon.rgb)};
const vec4 WIN = vec4(${S.window.map(f).join(',')});    // 侧墙上的窗户 y0 y1 z0 z1
const float BEAM_Y[3] = float[3](${S.beams.map(f).join(',')});
const int NOCC = ${S.occ.length};
const vec4 OCC[${Math.max(1, S.occ.length)}] = vec4[${Math.max(1, S.occ.length)}](${(S.occ.length ? S.occ : [[0, 0, -9, 0.01]]).map((s) => `vec4(${s.map(f).join(',')})`).join(',')});
const int NOCB = ${S.occBack.length};
const vec4 OCB[${Math.max(1, S.occBack.length)}] = vec4[${Math.max(1, S.occBack.length)}](${(S.occBack.length ? S.occBack : [[0, 0, -9, 0.01]]).map((s) => `vec4(${s.map(f).join(',')})`).join(',')});

float hash12(vec2 p) { vec3 p3 = fract(vec3(p.xyx) * 0.1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
float hash13(vec3 p3) { p3 = fract(p3 * 0.1031); p3 += dot(p3, p3.zyx + 31.32); return fract((p3.x + p3.y) * p3.z); }
float vnoise(vec2 p) { vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash12(i), hash12(i + vec2(1, 0)), f.x), mix(hash12(i + vec2(0, 1)), hash12(i + vec2(1, 1)), f.x), f.y); }
float fbm(vec2 p) { float a = 0.5, s = 0.0; for (int i = 0; i < 5; i++) { s += a * vnoise(p); p = p * 2.03 + 17.1; a *= 0.5; } return s; }
float vnoise3(vec3 p) { vec3 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
  float n000 = hash13(i), n100 = hash13(i + vec3(1,0,0)), n010 = hash13(i + vec3(0,1,0)), n110 = hash13(i + vec3(1,1,0));
  float n001 = hash13(i + vec3(0,0,1)), n101 = hash13(i + vec3(1,0,1)), n011 = hash13(i + vec3(0,1,1)), n111 = hash13(i + vec3(1,1,1));
  return mix(mix(mix(n000, n100, f.x), mix(n010, n110, f.x), f.y), mix(mix(n001, n101, f.x), mix(n011, n111, f.x), f.y), f.z); }

vec3 rayDir(vec2 px) { return normalize(uFwd * uFocal + uRight * (px.x - 0.5 * uRes.x) - uUp * (px.y - 0.5 * uRes.y)); }

// ---------------- 布帘：晾衣铁丝、床单、两边的被子
float wireZ(float x) { float u = (x - 0.5 * (B0.x + B1.x)) / (0.5 * (B1.x - B0.x)); return ${f(S.wireZ)} - 0.04 * (1.0 - u * u); }
float sag(float x) { float u = fract((x - PIN0) / PINDX); return 0.016 * sin(PI * u); }
float sheetTop(float x) { return min(SHEET.w, wireZ(x) - 0.012) - sag(x); }
float sheetBot(float x) { return SHEET.z + 0.010 * sin(x * 9.0 + 1.3) + 0.006 * sin(x * 23.0) + 0.012 * smoothstep(SHEET.y - 0.25, SHEET.y, x); }
float quiltTop(float x) { return wireZ(x) - 0.01 - sag(x) * 0.6; }
float boxSD(vec2 q, float x0, float x1, float z0, float z1) { return max(max(x0 - q.x, q.x - x1), max(z0 - q.y, q.y - z1)); }
float sdSheet(vec2 q) { return boxSD(q, SHEET.x, SHEET.y, sheetBot(q.x), sheetTop(q.x)); }
float sdQL(vec2 q) { return boxSD(q, QL.x, QL.y, QL.z + 0.02 * sin(q.x * 7.0), quiltTop(q.x)); }
float sdQR(vec2 q) { return boxSD(q, QR.x, QR.y, QR.z + 0.025 * sin(q.x * 5.0 + 2.0), quiltTop(q.x)); }
// 夹子：每隔 PINDX 一个，夹在布的上沿
float sdPin(vec2 q) { float i = floor((q.x - PIN0) / PINDX + 0.5); float cx = PIN0 + i * PINDX; float zt = wireZ(cx);
  return boxSD(q, cx - 0.009, cx + 0.009, zt - 0.055, zt + 0.018); }
float cov(float sd, float rho) { return 1.0 - smoothstep(-rho, rho, sd); }
float curtainCover(vec2 q, float rho) {
  float c = max(cov(sdSheet(q), rho), max(cov(sdQL(q), rho), cov(sdQR(q), rho)));
  c = max(c, cov(sdPin(q), rho));
  float dw = abs(q.y - wireZ(q.x));
  c = max(c, clamp(0.003 / (2.0 * rho + 0.003), 0.0, 1.0) * (1.0 - smoothstep(0.0015, 0.0015 + 2.0 * rho, dw)));
  return c;
}

// ---------------- 遮挡：房梁（盒子）、小满和奶奶（一串球）
bool segBox(vec3 a, vec3 b, vec3 bmin, vec3 bmax) {
  vec3 d = b - a; vec3 inv = 1.0 / d;
  vec3 t0 = (bmin - a) * inv, t1 = (bmax - a) * inv;
  vec3 tn = min(t0, t1), tf = max(t0, t1);
  float n = max(max(tn.x, tn.y), tn.z), fa = min(min(tf.x, tf.y), tf.z);
  return n < fa && fa > 0.0 && n < 1.0;
}
float beamsVis(vec3 a, vec3 b) {
  if (max(a.z, b.z) < ${f(S.beamZ0)}) return 1.0;
  for (int i = 0; i < 3; i++) if (segBox(a, b, vec3(B0.x, BEAM_Y[i] - 0.07, ${f(S.beamZ0)}), vec3(B1.x, BEAM_Y[i] + 0.07, B1.z))) return 0.0;
  return 1.0;
}
// 一串球挡住线段 a→b：penumbra = 光源张角 × 球到接收点的距离
float sphereOcc(vec3 a, vec3 b, vec4 s, float spread) {
  vec3 d = b - a; float L = length(d); d /= L;
  float h = clamp(dot(s.xyz - a, d), 0.0, L);
  float dist = length(a + d * h - s.xyz);
  float w = 0.004 + spread * h;
  return smoothstep(s.w - w, s.w + w, dist);
}
float occFront(vec3 a, vec3 b, float spread) { float v = 1.0; for (int i = 0; i < NOCC; i++) v *= sphereOcc(a, b, OCC[i], spread); return v; }
float occBack(vec3 a, vec3 b, float spread) { float v = 1.0; for (int i = 0; i < NOCB; i++) v *= sphereOcc(a, b, OCB[i], spread); return v; }

// ---------------- 马灯能不能照到 P（0..1，带半影）
float lampVis(vec3 P) {
  vec3 L = uLamp;
  if (P.y >= 0.0) return occBack(P, L, 0.03) * beamsVis(P, L);
  float t = -P.y / (L.y - P.y);
  vec3 Q = P + t * (L - P);
  vec2 q = vec2(Q.x, Q.z);
  float c1 = curtainCover(q, max(0.0008, LAMP_CORE * t)), c2 = curtainCover(q, max(0.002, LAMP_GLOBE * t));
  float v = mix(1.0 - c1, 1.0 - c2, 0.38);
  if (v > 0.0005) v *= beamsVis(P, L) * occBack(Q, L, 0.03);
  return v;
}
vec3 lampE(vec3 P, vec3 N) {
  vec3 d = uLamp - P; float r2 = dot(d, d); vec3 l = d * inversesqrt(r2);
  float c = max(0.0, dot(N, l));
  if (c <= 0.0) return vec3(0);
  return LAMP_RGB * uLampI * c / r2 * lampVis(P);
}
// 卡片（人物）受马灯照：后台的人物卡片不被代表她自己身体的遮挡球挡（不然自己把自己照得斑斑驳驳）
// 卡片是一张正对镜头的二维画：灯在卡片背面（比人离镜头还远）时，把灯的方向沿卡片平面镜像到正面——
// 画里的人是侧着身子朝灯的，朝灯那一侧（脸、手）就该被照亮；不镜像的话只有法线偏向灯的小块被照到，斑斑驳驳
vec3 lampEcard(vec3 P, vec3 N) {
  if (P.y < 0.0) return lampE(P, N);
  vec3 d = uLamp - P; float r2 = dot(d, d); vec3 l = d * inversesqrt(r2);
  vec3 cn = -uFwd; float k = 1.0;
  if (dot(l, cn) < 0.0) { l = normalize(l - 2.0 * dot(l, cn) * cn); k = 0.85; }
  float c = max(0.0, (dot(N, l) + 0.5) / 1.5);   // 包裹一点：后台马灯离人很近，纯朗伯的明暗太硬，画上已有的明暗会被叠出一块一块
  return LAMP_RGB * uLampI * k * c / r2 * beamsVis(P, uLamp);
}
// ---------------- 床单这块面光源对 P 的照度（只照看戏的这边）
vec3 patchCenter(int i, int j) {
  float x = SHEET.x + (float(i) + 0.5) * (SHEET.y - SHEET.x) / 8.0;
  float z = SHEET.z + (5.5 - float(j)) * (SHEET.w - SHEET.z) / 6.0;
  return vec3(x, 0.0, z);
}
const float PATCH_A = (SHEET.y - SHEET.x) * (SHEET.w - SHEET.z) / 48.0;
vec3 sheetE(vec3 P, vec3 N, float wrap, bool shadows) {
  if (P.y >= -0.002) return vec3(0);
  vec3 E = vec3(0);
  for (int j = 0; j < 6; j++) for (int i = 0; i < 8; i++) {
    vec3 S = patchCenter(i, j); vec3 d = S - P; float r2 = dot(d, d); vec3 w = d * inversesqrt(r2);
    float c = (dot(N, w) + wrap) / (1.0 + wrap);
    if (c <= 0.0) continue;
    float v = shadows ? occFront(P, S, 0.5 * 0.26 / sqrt(r2)) : 1.0;
    E += uPatch[j * 8 + i] * (c * w.y * PATCH_A / max(r2, 0.02) * v);
  }
  return E;
}
// ---------------- 月光：从右墙窗户进来的平行光（窗框十字）
// bars = false：不算窗框的十字影子（人物身上用——一道细窗框影子横在胳膊上，看起来像关节缝）
float moonVisB(vec3 P, bool bars) {
  float s = ((MOON_L.x > 0.0 ? B1.x : B0.x) - P.x) / MOON_L.x; vec3 W = P + s * MOON_L;
  float pen = 0.004 + 0.0045 * s;
  float inWin = (1.0 - smoothstep(-pen, pen, max(max(WIN.x - W.y, W.y - WIN.y), max(WIN.z - W.z, W.z - WIN.w))));
  float my = 0.5 * (WIN.x + WIN.y), mz = WIN.z + 0.62 * (WIN.w - WIN.z);
  float bar = max(1.0 - smoothstep(0.02 - pen, 0.02 + pen, abs(W.y - my)), 1.0 - smoothstep(0.018 - pen, 0.018 + pen, abs(W.z - mz)));
  return bars ? inWin * (1.0 - bar) : inWin * 0.85;
}
float moonVis(vec3 P) { return moonVisB(P, true); }
vec3 moonE(vec3 P, vec3 N, bool shadows) {
  float c = dot(N, MOON_L); if (c <= 0.0) return vec3(0);
  float v = moonVisB(P, shadows); if (v <= 0.0) return vec3(0);
  if (shadows) v *= occFront(P, P + MOON_L * 4.0, 0.0045);
  return MOON_RGB * c * v;
}
`;
}

// ================================================================== 第一遍：表面
export function sceneFS(S) {
  return common(S) + `
uniform sampler2D uSheet, uQuiltL, uQuiltR, uAlb, uNrm, uMat;
// 手电（第 9 场）：架在后台，光斑打在床单上；uSheet2 是手电挡出来的影子（狗的手影、皮影）
uniform sampler2D uSheet2; uniform vec4 uFlash; uniform float uFlashI; uniform vec3 uFlashCol;   // uFlash = (x, 离床单, z, 光斑半径)
uniform float uCardDbg;

// 盒子从里面射出去
float roomExit(vec3 ro, vec3 rd, out vec3 n) {
  vec3 t1 = (B1 - ro) / rd, t0 = (B0 - ro) / rd;
  vec3 tf = max(t0, t1);
  float t = min(min(tf.x, tf.y), tf.z);
  if (t == tf.x) n = vec3(rd.x > 0.0 ? -1.0 : 1.0, 0, 0);
  else if (t == tf.y) n = vec3(0, rd.y > 0.0 ? -1.0 : 1.0, 0);
  else n = vec3(0, 0, rd.z > 0.0 ? -1.0 : 1.0);
  return t;
}
float beamHit(vec3 ro, vec3 rd, out vec3 n) {
  float best = 1e9;
  for (int i = 0; i < 3; i++) {
    vec3 bmin = vec3(B0.x, BEAM_Y[i] - 0.07, ${S.beamZ0}), bmax = vec3(B1.x, BEAM_Y[i] + 0.07, B1.z);
    vec3 inv = 1.0 / rd; vec3 t0 = (bmin - ro) * inv, t1 = (bmax - ro) * inv;
    vec3 tn = min(t0, t1), tf = max(t0, t1);
    float a = max(max(tn.x, tn.y), tn.z), b = min(min(tf.x, tf.y), tf.z);
    if (a < b && a > 0.0 && a < best) { best = a; n = a == tn.y ? vec3(0, -sign(rd.y), 0) : (a == tn.z ? vec3(0, 0, -sign(rd.z)) : vec3(-sign(rd.x), 0, 0)); }
  }
  return best;
}

// 环境光：月夜的天光（冷）+ 被马灯照亮的天花板和地面反射回来的一点暖光
vec3 ambient(vec3 P, vec3 N) {
  vec3 sky = vec3(0.006, 0.009, 0.020) * (0.6 + 0.4 * N.z);
  float near = exp(-abs(P.y) * 1.2) * smoothstep(-0.5, 1.2, P.x) * (1.0 - smoothstep(2.6, 4.0, P.x));
  vec3 warm = LAMP_RGB * 0.010 * near * (0.55 + 0.45 * max(N.z, -N.y * 0.6));
  if (P.y > 0.0) warm = LAMP_RGB * 0.03 * (0.7 + 0.3 * N.z);
  // 日光灯：屋顶一根灯管，冷白、平、从上往下，满屋子都亮
  vec3 fluor = uFluor * vec3(0.86, 0.93, 1.0) * 0.55 * (0.62 + 0.38 * max(N.z, 0.0));
  return sky + warm + fluor;
}

// 屋子表面的固有色
vec3 albedoRoom(vec3 P, vec3 n) {
  if (n.z > 0.5) { // 地：青砖，错缝铺
    vec2 q = P.xy / vec2(0.24, 0.12); q.x += 0.5 * mod(floor(q.y), 2.0);
    vec2 f = fract(q), id = floor(q);
    float mortar = smoothstep(0.0, 0.035, f.x) * smoothstep(1.0, 0.965, f.x) * smoothstep(0.0, 0.07, f.y) * smoothstep(1.0, 0.93, f.y);
    float h = hash12(id);
    vec3 brick = vec3(0.27, 0.25, 0.22) * (0.8 + 0.35 * h) * (0.85 + 0.3 * fbm(P.xy * 9.0));
    return mix(vec3(0.10, 0.09, 0.08), brick, mortar);
  }
  if (n.z < -0.5) { // 顶棚：芦苇席（人字纹编的），旧了有点发黄
    vec2 q = P.xy * 22.0; float hb = mod(floor(q.x) + floor(q.y), 2.0);
    float strand = 0.85 + 0.15 * sin((hb > 0.5 ? q.x : q.y) * 18.0);
    return vec3(0.46, 0.36, 0.22) * strand * (0.8 + 0.35 * fbm(P.xy * 3.0));
  }
  // 墙：白灰墙，下半截刷绿漆的墙裙
  float stain = fbm(P.xz * vec2(1.3, 2.2) + P.y);
  vec3 wall = vec3(0.62, 0.57, 0.48) * (0.82 + 0.25 * stain);
  float wz = 1.0 + 0.004 * sin((P.x + P.y) * 13.0);
  vec3 wains = vec3(0.13, 0.25, 0.20) * (0.85 + 0.25 * fbm(P.xz * 6.0));
  vec3 c = P.z < wz ? wains : wall;
  if (abs(P.z - wz) < 0.012) c = vec3(0.30, 0.10, 0.07);
  if (P.y > 0.05) c *= 0.45;   // 后台的墙：旧，熏得发暗
  return c;
}

vec3 shadeDiffuse(vec3 P, vec3 N, vec3 alb, bool shadows) {
  vec3 E = lampE(P, N) + sheetE(P, N, 0.0, shadows) + moonE(P, N, shadows) + ambient(P, N);
  return alb * E / PI;
}

// ---------------- 卡片（人物、道具）
vec3 shadeCard(vec3 P, vec3 N, vec3 V, vec3 alb, float mat, float extra) {
  int m = int(mat * 255.0 / 30.0 + 0.5);   // cards.js 里材质号 × 30 存的
  if (m == 8) return alb * (1.0 + 7.0 * extra) * uLampI;   // 自己发光（马灯的火苗和玻璃罩），亮度随火苗闪
  float wrap = m == 1 ? 0.6 : (m == 2 ? 0.3 : 0.55);
  // 地面反光：床单前面被照亮的地面把暖光从下往上反到人身上（离床单越近越亮）
  vec3 fl = vec3(P.x + 0.25, -0.35, 0.0) - P; vec3 fw = normalize(fl);
  vec3 bounce = LAMP_RGB * ${S.bounce} * (m == 3 ? 1.6 : 1.0) * max(0.0, (dot(N, fw) + 0.5) / 1.5) * smoothstep(-3.0, -0.5, P.y);
  vec3 E = sheetE(P, N, wrap, false) * ${S.cardSheetGain} + lampEcard(P, N) + moonE(P, N, false) * (m == 3 ? 0.15 : 0.3) + ambient(P, N) * 1.5 + bounce;
  if (m == 1) E += LAMP_RGB * 0.02 + vec3(0.014, 0.005, 0.002);
  if (m == 3) E += LAMP_RGB * 0.012;   // 皮肤：暗部也透着一点暖（皮下散射）
  vec3 c = alb * E / PI;
  // 逆光：光从物体背后穿过发丝、耳廓、绒毛射向镜头，轮廓边上一圈亮（皮肤偏红，头发偏暖）
  if (m == 1 || m == 2 || m == 6) {
    float edge = pow(1.0 - clamp(dot(N, V), 0.0, 1.0), m == 2 ? 2.0 : 3.0);
    vec3 back = vec3(0);
    for (int j = 0; j < 6; j += 2) for (int i = 0; i < 8; i += 2) {
      vec3 S2 = patchCenter(i, j) + vec3(0.13, 0, -0.1); vec3 d = S2 - P; float r2 = dot(d, d); vec3 w = d * inversesqrt(r2);
      float fwd = pow(max(0.0, dot(-V, w)), 3.0) * max(0.0, dot(N, w) + 0.6);
      back += uPatch[j * 8 + i] * fwd * PATCH_A * 4.0 / max(r2, 0.05);
    }
    vec3 tint = m == 1 ? vec3(1.0, 0.55, 0.42) : (m == 2 ? vec3(1.0, 0.75, 0.5) : vec3(1.0, 0.9, 0.7));
    c += back * edge * tint * (m == 2 ? 0.5 : 0.25) * (0.4 + extra);   // 皮肤的亮边收一点，形状靠外形读，不靠描亮边
  }
  // 眼睛里映着床单（高光）
  if (m == 4) c = alb * dot(uPatch[19] + uPatch[20] + uPatch[27] + uPatch[28], vec3(0.25)) * 2.2 * vec3(1.0, 0.92, 0.8);
  // 皮影（后台看到的牛皮）：马灯透过彩色牛皮
  if (m == 7) c += alb * LAMP_RGB * uLampI * 0.9 * extra;
  return c;
}

void main() {
  vec2 px = vec2(uv.x * uRes.x, (1.0 - uv.y) * uRes.y);
  vec3 rd = rayDir(px), ro = uCam;
  vec3 n; float t = roomExit(ro, rd, n);
  vec3 bn; float tb = beamHit(ro, rd, bn);
  vec3 col; float depth;
  // 布帘平面
  float tc = ro.y * rd.y < 0.0 ? -ro.y / rd.y : 1e9;   // 从前面或后台都能看到床单所在的平面
  int kind = 0;   // 0 屋子 1 床单 2 左被 3 右毯 4 铁丝 5 夹子 6 房梁
  vec2 q;
  if (tb < t) { t = tb; n = bn; kind = 6; }
  if (tc < t) {
    vec3 Q = ro + rd * tc; q = vec2(Q.x, Q.z);
    float aa = 1.5 * tc / uFocal;     // 一个像素在布帘上多宽（米）
    float wire = 1.0 - smoothstep(0.0015, 0.0015 + aa, abs(q.y - wireZ(q.x)));
    if (sdPin(q) < 0.0) kind = 5;
    else if (wire > 0.5) kind = 4;
    else if (sdSheet(q) < 0.0) kind = 1;
    else if (sdQL(q) < 0.0) kind = 2;
    else if (sdQR(q) < 0.0) kind = 3;
    if (kind != 0) t = tc;
  }
  vec3 P = ro + rd * t;
  vec3 N = n, alb = vec3(0), emit = vec3(0);
  float ao = 1.0; bool shadows = false; bool lit = true;
  if (kind == 1) {
    vec2 suv = vec2((q.x - SHEET.x) / (SHEET.y - SHEET.x), (SHEET.w - q.y) / (SHEET.w - SHEET.z));
    // 亮度用浮点精确算（和 s06_key.js 的 sheetRadiance 同一个公式），贴图只是影子（透过皮影的颜色）
    vec3 Lq = vec3(q.x, 0.0, q.y) - uLamp; float r2 = dot(Lq, Lq); float rr = sqrt(r2);
    float diff = ${S.sheetTau} * uLampI * uLamp.y / (r2 * rr);
    float hot = uLampI * (${S.sheetHot} * exp(-(Lq.x * Lq.x + Lq.z * Lq.z) / (0.12 * 0.12)) + 0.10 * exp(-(Lq.x * Lq.x + Lq.z * Lq.z) / (0.34 * 0.34)));
    // 床单比正经的影幕厚：光在布里散开一点（约 1.5 毫米），影子边缘略柔、颜色略淡
    vec2 du = vec2(0.0015 / (SHEET.y - SHEET.x), 0.0015 / (SHEET.w - SHEET.z));
    vec3 msk = pow(texture(uSheet, suv).rgb, vec3(2.2)) * 0.4
      + (pow(texture(uSheet, suv + vec2(du.x, 0)).rgb, vec3(2.2)) + pow(texture(uSheet, suv - vec2(du.x, 0)).rgb, vec3(2.2))
       + pow(texture(uSheet, suv + vec2(0, du.y)).rgb, vec3(2.2)) + pow(texture(uSheet, suv - vec2(0, du.y)).rgb, vec3(2.2))) * 0.15;
    msk = mix(msk, vec3(dot(msk, vec3(0.3, 0.5, 0.2))), 0.15);
    vec3 s = vec3(diff + hot, diff + hot * 0.92, diff + hot * 0.8) * LAMP_RGB * msk;
    // 手电的光斑：中间亮、边上一圈软边；被手和皮影挡住的地方是影子（冷色的光斑里一只暖暗的狗）
    if (uFlashI > 0.0) {
      float dd = length(q - vec2(uFlash.x, uFlash.z)) / uFlash.w;
      float spot = uFlashI * smoothstep(1.0, 0.78, dd) * (0.7 + 0.3 * (1.0 - dd * dd));
      vec3 m2 = pow(texture(uSheet2, suv).rgb, vec3(2.2));
      s += spot * uFlashCol * m2;
    }
    // 从后台看：床单这一面直接被马灯照着（棉布反射约 0.7，比透过去的亮），没有"透过布看见灯芯"的那团亮；影子一样
    if (ro.y > 0.0) s = vec3(diff * (0.7 / ${S.sheetTau}) / PI + hot * 0.08) * LAMP_RGB * msk;
    // 挂起来的褶：上沿夹子之间往下垂的弧形褶，下沿轻微的波浪；棉布在褶子处厚一点、暗一点
    float fold = 0.5 + 0.5 * sin((q.x - PIN0) / PINDX * 2.0 * PI);
    float topFold = exp(-(sheetTop(q.x) - q.y) * 9.0) * fold;
    float lowFold = 0.5 + 0.5 * sin(q.x * 9.0 + 1.3 + q.y * 0.6);
    // 棉布：细细的布纹；叠放多年留下的折痕（横竖各几道，一条暗线旁边一条亮边）；四边双层的布边和一道针脚；
    // 一圈褪了色的印花边（淡粉的小花、淡青的叶子），背光时透出淡淡的颜色
    float bu = q.x - SHEET.x, bv = sheetTop(q.x) - q.y, bw = SHEET.y - SHEET.x, bh = sheetTop(q.x) - sheetBot(q.x);
    float weave = 1.0 + 0.025 * (vnoise(vec2(bu, bv) * 90.0) - 0.5) + 0.02 * (vnoise(vec2(bu * 260.0, bv * 40.0)) - 0.5);
    float crease = 0.0;
    for (int k = 1; k < 3; k++) { float cx = bw * float(k) / 3.0 + 0.01 * sin(bv * 5.0 + float(k)); float d = bu - cx; crease += -0.07 * exp(-d * d / 0.00002) + 0.035 * exp(-(d - 0.006) * (d - 0.006) / 0.00006); }
    { float cz = bh * 0.5 + 0.008 * sin(bu * 4.0); float d = bv - cz; crease += -0.06 * exp(-d * d / 0.00002) + 0.03 * exp(-(d + 0.006) * (d + 0.006) / 0.00006); }
    float edge = min(min(bu, bw - bu), min(bv, bh - bv));
    float hem = edge < 0.025 ? 0.72 : 1.0;
    float stitch = (abs(edge - 0.02) < 0.0012 && fract(max(bu, bv) * 120.0) < 0.55) ? 0.8 : 1.0;
    vec3 print = vec3(1.0);
    if (edge > 0.05 && edge < 0.13) {
      vec2 cell = vec2(bu + bv, bv - bu) * 18.0; vec2 cf = fract(cell) - 0.5; float ci = hash12(floor(cell));
      float flower = smoothstep(0.22, 0.17, length(cf)) * step(0.35, ci);
      float leaf = smoothstep(0.08, 0.04, abs(cf.x + cf.y * 0.6)) * smoothstep(0.42, 0.3, length(cf)) * step(ci, 0.6);
      print = mix(print, vec3(1.0, 0.76, 0.74), flower * 0.55);
      print = mix(print, vec3(0.78, 0.92, 0.86), leaf * 0.5);
      print *= 1.0 - 0.10 * (smoothstep(0.05, 0.052, edge) - smoothstep(0.128, 0.13, edge) + 0.0);
    }
    float hang = 1.0 + 0.035 * sin(bu * 7.0 + 0.6 * sin(bv * 2.0)) + 0.02 * sin(bu * 17.0 + 1.0);
    emit = s * (1.0 - 0.10 * topFold) * weave * (1.0 + crease) * hem * stitch * hang * print;
    // 来电：床单被屋里的日光灯照着，白布反光把透过来的影子冲淡，几乎看不见
    emit += uFluor * vec3(0.84, 0.9, 0.96) * 0.30 * weave * (1.0 + crease) * hem * print;
    lit = false;
  } else if (kind == 2 || kind == 3) {
    float u = kind == 2 ? (q.x - QL.x) / (QL.y - QL.x) : (q.x - QR.x) / (QR.y - QR.x);
    vec4 r = kind == 2 ? QL : QR;
    vec2 tuv = vec2(u, (quiltTop(q.x) - q.y) / (quiltTop(q.x) - r.z));
    alb = (kind == 2 ? pow(texture(uQuiltL, tuv).rgb, vec3(2.2)) : pow(texture(uQuiltR, tuv).rgb, vec3(2.2))) * 0.55;
    // 被子厚，挂着有竖向的大褶：法线左右摆
    float ph = q.x * (kind == 2 ? 7.5 : 6.0) + 0.8 * sin(q.y * 2.0);
    N = normalize(vec3(0.55 * sin(ph), -1.0, 0.0));
    ao = 0.75 + 0.25 * (0.5 + 0.5 * cos(ph));
    P.y -= 0.01;
  } else if (kind == 4 || kind == 5) {
    alb = kind == 4 ? vec3(0.05) : vec3(0.28, 0.18, 0.10);
    N = vec3(0, -1, 0); P.y -= 0.01;
    emit = alb * 0.4 * lampE(P - vec3(0, 0.01, 0), normalize(vec3(0, -0.2, 1.0))) / PI;
  } else if (kind == 6) {
    alb = vec3(0.16, 0.10, 0.06) * (0.8 + 0.3 * fbm(vec2(P.x * 2.0, P.z * 40.0)));
    P += n * 0.002;
  } else {
    alb = albedoRoom(P, n);
    P += n * 0.002; shadows = true;
  }
  col = emit;
  if (lit) col += shadeDiffuse(P, N, alb, shadows) * ao;
  depth = t;
  // 卡片
  vec2 suv = vec2(uv.x, 1.0 - uv.y);
  vec4 nr = texture(uNrm, suv);
  if (nr.a > 0.002) {
    vec4 mt = texture(uMat, suv);
    float dc = mt.r * 8.0;
    if (dc < t) {
      vec4 al = texture(uAlb, suv);
      vec3 ns = nr.xyz * 2.0 - 1.0;
      vec3 N = normalize(uRight * ns.x + uUp * ns.y - uFwd * ns.z);
      vec3 Pc = ro + rd * dc;
      vec3 cc = shadeCard(Pc, N, -rd, pow(al.rgb, vec3(2.2)), mt.g, mt.b);
      if (uCardDbg > 0.5 && uCardDbg < 1.5) cc = pow(al.rgb, vec3(2.2)) * 0.2;
      if (uCardDbg > 1.5 && uCardDbg < 2.5) cc = pow(nr.rgb, vec3(2.2)) * 0.2;
      if (uCardDbg > 2.5) cc = vec3(mt.g * 255.0 / 120.0, mt.b, mt.r) * 0.2;
      col = mix(col, cc, nr.a);
      depth = mix(t, dc, step(0.5, nr.a));
    }
  }
  o = vec4(col, depth);
}
`;
}

// ================================================================== 第二遍：空气里的散射光（四分之一分辨率）
export function fogFS(S) {
  return common(S) + `
uniform sampler2D uScene;
uniform float uSigma;
float phaseHG(float c, float g) { float g2 = g * g; return (1.0 - g2) / (4.0 * PI * pow(1.0 + g2 - 2.0 * g * c, 1.5)); }
float density(vec3 P) {
  // 薄薄的浮尘 + 马灯上方升起的烟气（慢慢飘、有絮状的起伏）
  float smoke = 2.2 * exp(-length((P - uLamp - vec3(0, 0, 0.45)) * vec3(1.6, 1.8, 0.75)));
  float n = vnoise3(P * 2.4 + vec3(0.0, 0.0, -uTime * 0.06)) * 0.9 + vnoise3(P * 6.1 + vec3(uTime * 0.04, 0.0, 0.0)) * 0.5;
  return (0.35 + smoke) * (0.35 + n);
}
void main() {
  vec2 px = vec2(uv.x * uRes.x, (1.0 - uv.y) * uRes.y);
  vec2 fuv = vec2(uv.x, uv.y);
  float tEnd = texture(uScene, fuv).a;
  vec3 rd = rayDir(px), ro = uCam;
  const int N = 56;
  float jit = fract(52.9829189 * fract(dot(px, vec2(0.06711056, 0.00583715))));
  float dt = tEnd / float(N);
  vec3 acc = vec3(0);
  for (int i = 0; i < N; i++) {
    float tt = (float(i) + jit) * dt;
    vec3 P = ro + rd * tt;
    float s = density(P);
    // 马灯
    vec3 dl = uLamp - P; float r2 = dot(dl, dl); vec3 l = dl * inversesqrt(r2);
    float v = lampVis(P);
    vec3 Ls = LAMP_RGB * uLampI * v / max(r2, 0.04) * phaseHG(dot(rd, l), 0.45);
    // 床单（粗略：四块）
    if (P.y < 0.0) {
      for (int j = 1; j < 6; j += 2) for (int k = 1; k < 8; k += 3) {
        vec3 Sp = patchCenter(k, j); vec3 d = Sp - P; float q2 = dot(d, d); vec3 w = d * inversesqrt(q2);
        Ls += uPatch[j * 8 + k] * (w.y * PATCH_A * 3.0 / max(q2, 0.05)) * phaseHG(dot(rd, w), 0.35);
      }
      Ls += MOON_RGB * moonVis(P) * phaseHG(dot(rd, MOON_L), 0.3) * 0.45;
    }
    acc += Ls * s * dt;
  }
  o = vec4(acc * uSigma, tEnd);
}
`;
}

// ================================================================== 第三遍：合成（雾按深度上采样）
export const combineFS = `#version 300 es
precision highp float;
in vec2 uv; out vec4 o;
uniform sampler2D uScene, uFog, uDust;
uniform vec2 uFogRes;
uniform float uExt;
void main() {
  vec4 sc = texture(uScene, uv);
  float d = sc.a;
  // 按深度加权的上采样（3×3 邻域），人物边缘不糊，顺便把逐像素抖动的噪点抹平
  vec2 p = uv * uFogRes - 0.5; vec2 b = (floor(p) + 0.5) / uFogRes; vec2 f = fract(p);
  vec3 acc = vec3(0); float ws = 0.0;
  for (int j = -1; j <= 2; j++) for (int i = -1; i <= 2; i++) {
    vec2 o2 = vec2(i, j);
    vec4 fg = texture(uFog, b + o2 / uFogRes);
    vec2 dd = o2 - f;
    float w = exp(-dot(dd, dd) * 0.55) / (0.03 + abs(fg.a - d));
    acc += fg.rgb * w; ws += w;
  }
  vec3 fog = acc / max(ws, 1e-5);
  vec3 c = sc.rgb * exp(-uExt * d) + fog;
  vec4 du = texture(uDust, vec2(uv.x, 1.0 - uv.y));
  c += pow(du.rgb, vec3(2.2)) * du.a * 0.9;
  o = vec4(c, d);
}`;

// ================================================================== 泛光：降采样 + 高斯模糊
export const downFS = `#version 300 es
precision highp float;
in vec2 uv; out vec4 o;
uniform sampler2D uSrc; uniform vec2 uTexel;
void main() {
  vec3 c = texture(uSrc, uv + uTexel * vec2(-1, -1)).rgb + texture(uSrc, uv + uTexel * vec2(1, -1)).rgb
         + texture(uSrc, uv + uTexel * vec2(-1, 1)).rgb + texture(uSrc, uv + uTexel * vec2(1, 1)).rgb;
  o = vec4(c * 0.25, 1.0);
}`;
export const blurFS = `#version 300 es
precision highp float;
in vec2 uv; out vec4 o;
uniform sampler2D uSrc; uniform vec2 uDir;
void main() {
  const float w[5] = float[5](0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);
  vec3 c = texture(uSrc, uv).rgb * w[0];
  for (int i = 1; i < 5; i++) { c += texture(uSrc, uv + uDir * float(i)).rgb * w[i]; c += texture(uSrc, uv - uDir * float(i)).rgb * w[i]; }
  o = vec4(c, 1.0);
}`;

// ================================================================== 最后：曝光、色调映射、调色、颗粒
export const finalFS = `#version 300 es
precision highp float;
in vec2 uv; out vec4 o;
uniform sampler2D uSrc, uB1, uB2, uB3;
uniform vec2 uRes; uniform float uExp, uTime, uBloom;
vec3 aces(vec3 x) { return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0); }
float hash12(vec2 p) { vec3 p3 = fract(vec3(p.xyx) * 0.1031); p3 += dot(p3, p3.yzx + 33.33); return fract((p3.x + p3.y) * p3.z); }
void main() {
  vec2 px = uv * uRes;
  // （不做色差：在高动态范围下，眼睛高光、浮尘这种小亮点会被线性插值漏到旁边，出红蓝边）
  vec2 cuv = uv - 0.5;
  vec3 c = texture(uSrc, uv).rgb;
  vec3 b1 = texture(uB1, uv).rgb, b2 = texture(uB2, uv).rgb, b3 = texture(uB3, uv).rgb;
  vec3 bloom = b1 * 0.5 + b2 * 0.35 + b3 * 0.35;
  c += bloom * uBloom;
  // 胶片的晕光：亮处外面一圈偏红的光
  c += b3 * vec3(0.10, 0.025, 0.01) * 0.8;
  c *= uExp;
  // 暗部偏蓝绿、亮部偏暖（分离色调）
  float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
  c = mix(c, c * vec3(0.88, 1.0, 1.18), 0.35 * (1.0 - smoothstep(0.0, 0.06, l)));
  c = aces(c);
  // 暗角
  float vig = smoothstep(1.05, 0.25, length(cuv * vec2(1.0, 1.15)));
  c *= mix(0.62, 1.0, vig);
  c = pow(c, vec3(1.0 / 2.2));
  // 胶片颗粒（暗部明显一点）
  float g = hash12(px + fract(uTime * 7.31) * 113.0) + hash12(px * 1.37 + 31.7 + fract(uTime * 3.17) * 71.0) - 1.0;
  c += g * mix(0.018, 0.007, l);
  o = vec4(c, 1.0);
}`;
