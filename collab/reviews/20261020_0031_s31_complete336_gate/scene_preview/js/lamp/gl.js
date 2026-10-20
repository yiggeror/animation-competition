// WebGL2 小工具：全屏着色器、浮点渲染目标、从 2D 画布上传贴图。
// 无头 Chromium 里用的是 SwiftShader（CPU 上的软件实现），结果和显卡无关、可复现。
const VS = `#version 300 es
in vec2 p; out vec2 uv;
void main() { uv = p * 0.5 + 0.5; gl_Position = vec4(p, 0.0, 1.0); }`;

export class GL {
  constructor(W, H) {
    this.cv = new OffscreenCanvas(W, H);
    const gl = (this.gl = this.cv.getContext('webgl2', { premultipliedAlpha: false, preserveDrawingBuffer: true, antialias: false, alpha: false }));
    if (!gl) throw new Error('WebGL2 不可用');
    if (!gl.getExtension('EXT_color_buffer_float')) throw new Error('不支持浮点渲染目标');
    gl.getExtension('OES_texture_float_linear');
    this.W = W; this.H = H;
    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    this.progs = {};
    this.targets = {};
    this.texs = {};
  }
  program(name, fs) {
    if (this.progs[name]) return this.progs[name];
    const gl = this.gl;
    const sh = (type, src) => {
      const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
        const log = gl.getShaderInfoLog(s);
        const lines = src.split('\n').map((l, i) => `${i + 1}: ${l}`);
        const m = /0:(\d+)/.exec(log); const ln = m ? +m[1] : 0;
        throw new Error(`着色器 ${name} 编译失败：${log}\n${lines.slice(Math.max(0, ln - 4), ln + 2).join('\n')}`);
      }
      return s;
    };
    const p = gl.createProgram();
    gl.attachShader(p, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, fs));
    gl.bindAttribLocation(p, 0, 'p');
    gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(`着色器 ${name} 链接失败：${gl.getProgramInfoLog(p)}`);
    const u = {};
    const n = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
    for (let i = 0; i < n; i++) { const info = gl.getActiveUniform(p, i); u[info.name.replace(/\[0\]$/, '')] = { loc: gl.getUniformLocation(p, info.name), type: info.type, size: info.size }; }
    return (this.progs[name] = { p, u });
  }
  // 浮点渲染目标（RGBA16F），可以当贴图读
  target(name, w, h) {
    const gl = this.gl;
    let t = this.targets[name];
    if (t && t.w === w && t.h === h) return t;
    if (!t) t = this.targets[name] = { tex: gl.createTexture(), fb: gl.createFramebuffer() };
    t.w = w; t.h = h;
    gl.bindTexture(gl.TEXTURE_2D, t.tex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA16F, w, h, 0, gl.RGBA, gl.HALF_FLOAT, null);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.bindFramebuffer(gl.FRAMEBUFFER, t.fb);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, t.tex, 0);
    return t;
  }
  // 从画布 / ImageData / 浮点数组上传贴图（第 0 行 = 画布最上面一行）
  texture(name, src, o = {}) {
    const gl = this.gl;
    let t = this.texs[name];
    if (!t) t = this.texs[name] = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, t);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
    gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
    if (src instanceof Float32Array) gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA32F, o.w, o.h, 0, gl.RGBA, gl.FLOAT, src);
    else gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, src);
    const f = o.nearest ? gl.NEAREST : gl.LINEAR;
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, f); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, f);
    const wr = o.repeat ? gl.REPEAT : gl.CLAMP_TO_EDGE;
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, wr); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, wr);
    return t;
  }
  // 画一遍：prog 名、目标（null = 屏幕）、uniform、贴图 {名: 贴图或目标}
  draw(name, target, uniforms = {}, textures = {}) {
    const gl = this.gl, P = this.progs[name];
    gl.bindFramebuffer(gl.FRAMEBUFFER, target ? target.fb : null);
    gl.viewport(0, 0, target ? target.w : this.W, target ? target.h : this.H);
    gl.useProgram(P.p);
    gl.enableVertexAttribArray(0);
    gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
    // 每个采样器都显式绑一张贴图（没给的绑 1×1 的空贴图），免得默认的 0 号单元正好是渲染目标自己
    if (!this.dummy) { this.dummy = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, this.dummy); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array(4)); }
    let unit = 0;
    for (const [k, u] of Object.entries(P.u)) {
      if (u.type !== gl.SAMPLER_2D) continue;
      const v = textures[k];
      gl.activeTexture(gl.TEXTURE0 + unit);
      gl.bindTexture(gl.TEXTURE_2D, v ? v.tex || v : this.dummy);
      gl.uniform1i(u.loc, unit++);
    }
    for (const [k, v] of Object.entries(uniforms)) {
      const u = P.u[k]; if (!u) continue;
      const a = typeof v === 'number' ? [v] : v;
      switch (u.type) {
        case gl.FLOAT: gl.uniform1fv(u.loc, a); break;
        case gl.FLOAT_VEC2: gl.uniform2fv(u.loc, a); break;
        case gl.FLOAT_VEC3: gl.uniform3fv(u.loc, a); break;
        case gl.FLOAT_VEC4: gl.uniform4fv(u.loc, a); break;
        case gl.INT: gl.uniform1iv(u.loc, a); break;
        case gl.FLOAT_MAT3: gl.uniformMatrix3fv(u.loc, false, a); break;
        default: throw new Error('uniform 类型未处理：' + k);
      }
    }
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    if (this.debug) { const e = gl.getError(); if (e) console.log("GL error", name, e); }
  }
}
