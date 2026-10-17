const fs = require('fs');
const { chromium } = require('/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out = '/tmp/laidian-audit-1a90-main';
(async () => {
  const browser = await chromium.launch({ executablePath: '/usr/bin/chromium', args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage();
    const result = await page.evaluate(() => {
      // Exact S10 cone at t=0, same native canvas and white-alpha mask as paintshot.js.
      const W=1672,H=941,k={x:-60,y:1060,len:1900,ang:-1.12,spread:0.1,soft:60,i:0.95};
      const m=new OffscreenCanvas(W,H),mx=m.getContext('2d');
      const g=mx.createRadialGradient(k.x,k.y,0,k.x,k.y,k.len);
      g.addColorStop(0,'rgba(255,255,255,1)');g.addColorStop(.6,'rgba(255,255,255,.5)');g.addColorStop(1,'rgba(255,255,255,0)');
      mx.filter=`blur(${k.soft}px)`;mx.fillStyle=g;
      mx.beginPath();mx.moveTo(k.x,k.y);mx.arc(k.x,k.y,k.len,k.ang-k.spread,k.ang+k.spread);mx.closePath();mx.fill();
      const d=mx.getImageData(0,0,W,H).data;
      const samples=[];
      for(const wanted of [1,4,16,64,128]) {
        let best=null;
        for(let y=50;y<H-50;y++)for(let x=50;x<W-50;x++) {
          const i=(y*W+x)*4,a=d[i+3];
          if(d[i]===255 && a===wanted){best={x,y,rgba:Array.from(d.slice(i,i+4)),currentContribution:d[i]/255*k.i,alphaWeightedContribution:d[i]/255*a/255*k.i};break;}
          if(best)break;
        }
        if(best)samples.push(best);
      }
      let nonzero=0,lowAlpha=0;
      for(let i=0;i<W*H;i++){if(d[i*4+3]>0){nonzero++;if(d[i*4+3]<=16)lowAlpha++;}}
      return {W,H,parameters:k,samples,nonzeroMaskPixels:nonzero,alphaAtMost16Pixels:lowAlpha};
    });
    result.browser=browser.version();
    result.sourceCommit='d1f3fbc0aa0d5dca15d2fee03c6cdc135bc0273d';
    result.method='Reproduce the exact t=0 S10 cone mask only; no implementation or render edits.';
    fs.writeFileSync(out+'/light-mask-check.json',JSON.stringify(result,null,2)+'\n');
    console.log(JSON.stringify(result));
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1});
