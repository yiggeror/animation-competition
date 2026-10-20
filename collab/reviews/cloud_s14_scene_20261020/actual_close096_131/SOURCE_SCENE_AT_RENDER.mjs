// S14 formal-background integration in progress. Existing artwork only.
import {renderPaint,loadImg} from '/js/paint/paintshot.js';
import {makeLampClose,exposureAt,VIEW} from '../20261020_0236_s14_lamp_close/integration_candidate/lamp_close.mjs';
import {flameShape} from '../20261020_0236_s14_lamp_close/integration_candidate/original_lamp.mjs';

export const DURATION=10,FPS=24;
export const CLOSE_BACKGROUND=Object.freeze({
  asset:'/assets/paint/bg_01_room_wide.png',
  // One fixed crop of the original room. The original chest lid, not a raised
  // replacement box, supports the lamp at source(860,980).
  sourceChestLid:[540,487],localChestLid:[860,980],scale:10,
  coordinateSystem:'2D original painted-room camera registration; not a world/camera calibration to S15'
});
const root='/collab/reviews/20261020_0236_s14_lamp_close/adopted/';
const drawings=new Map();
async function requiredImage(p){const im=await loadImg(p);if(!im)throw Error('Missing published S14 source '+p);return im;}
async function adopted(id){if(!drawings.has(id))drawings.set(id,requiredImage(root+id+'.png'));return drawings.get(id);}
async function drawExistingBackstage(ctx){
  const b=CLOSE_BACKGROUND,im=await requiredImage(b.asset);
  ctx.drawImage(im,b.localChestLid[0]-b.sourceChestLid[0]*b.scale,b.localChestLid[1]-b.sourceChestLid[1]*b.scale,im.width*b.scale,im.height*b.scale);
}
async function applyExistingLight(ctx,{t,exposure:e}){
  // The unchanged production paint renderer applies its existing linear-light
  // material pass, grain and vignette to this actual viewport.
  const alb=new OffscreenCanvas(VIEW.width,VIEW.height),a=alb.getContext('2d');
  a.drawImage(ctx.canvas,0,0,VIEW.width,VIEW.height);
  const flame=[e.lampX-VIEW.x,e.lampY-VIEW.y-226*.8];
  const flick=1+.05*Math.sin(t*9.3)+.03*Math.sin(t*17.7);
  await renderPaint(ctx,t,ctx.canvas.width,ctx.canvas.height,{
    bg:alb,size:[VIEW.width,VIEW.height],layers:()=>[],
    light:()=>({ambient:[.022,.026,.044],lights:[
      {x:flame[0],y:flame[1],r:1300*flick,color:[1,.68,.38],i:.75,falloff:1.8}
    ],exposure:1,vignette:.5,grain:7}),
    glow:()=>[{x:flame[0],y:flame[1]-12,r:80,color:[255,184,96],a:.12}],
    emit:x=>flameShape(x,flame,.6,5.8),
    cam:()=>({x:VIEW.width/2,y:VIEW.height/2,fit:1})
  });
}
const close=makeLampClose({loadAdopted:adopted,drawExistingBackstage,applyExistingLight});
export async function renderFrame(ctx,t,W,H){
  if(await close(ctx,t,W,H))return;
  throw Error('S14 frame '+Math.floor(t*24+1e-6)+' not yet bound to published complete character mapping. No old candidate substitution.');
}
export function frameBinding(f){
  const e=exposureAt(f/24);
  return e?{frame:f,drawing:e.id,shot:'approved096–131close',lampSource:[e.lampX,e.lampY],curtainLit:false,background:CLOSE_BACKGROUND}:null;
}
