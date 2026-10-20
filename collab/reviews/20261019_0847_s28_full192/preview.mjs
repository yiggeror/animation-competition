import {renderFrame} from './entry.mjs';
import {routeFrame} from './s28_full192.mjs';
import {phoneState} from './phone_insert.mjs';
const c=document.querySelector('canvas'),x=c.getContext('2d');window.ready=true;window.renderS28Full=async frame=>{const q=routeFrame(frame),start=performance.now();await renderFrame(x,q.time,c.width,c.height);return{...q,phone:q.part==='phone'?phoneState(q.time):null,elapsedMs:performance.now()-start,png:c.toDataURL('image/png')};};
