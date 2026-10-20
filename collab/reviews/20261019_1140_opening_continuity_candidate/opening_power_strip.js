// S06-approved continuity prop, original 1672x941 room plate.
// Neutral colors receive the same shot lighting as the characters. Never emits light.
export const STRIP_SOCKET = Object.freeze([646,724]);
export const ADAPTER_CABLE_EXIT = Object.freeze([646,707]);
export const WALL_OUTLET = Object.freeze([34,601]);
// S01/S04 left short-end port is hidden by real fingers. This is an occluded anchor, not a visible socket.
export const HELD_PHONE_PORT = Object.freeze([635,627]);
export const LANDED_PHONE_PORT = Object.freeze([646.8,661.5]);
const cache=new Map();
const outline='#625b50';
function curve(x,pts){x.beginPath();x.moveTo(...pts[0]);for(let i=1;i+2<pts.length;i+=3)x.bezierCurveTo(...pts[i],...pts[i+1],...pts[i+2]);}
function cord(x,pts,width=1.35){
 x.save();x.lineCap='round';x.lineJoin='round';
 x.translate(0,1.1);x.strokeStyle='rgba(24,20,15,.22)';x.lineWidth=width+1.7;curve(x,pts);x.stroke();
 x.translate(0,-1.1);x.strokeStyle='#827d70';x.lineWidth=width+1;curve(x,pts);x.stroke();
 x.strokeStyle='#ddd8ca';x.lineWidth=width;curve(x,pts);x.stroke();x.restore();
}
function poly(x,points,color){x.beginPath();x.moveTo(...points[0]);for(const p of points.slice(1))x.lineTo(...p);x.closePath();x.fillStyle=color;x.fill();x.strokeStyle=outline;x.lineWidth=.65;x.stroke();}
export function drawPowerStrip(x,phonePort=HELD_PHONE_PORT){
 // The cabinet leg hides the only omitted cable interval, between (73,647) and (45,637).
 cord(x,[[616,726],[606,730],[594,736],[581,733],[467,727],[276,719],[145,700],[111,690],[92,675],[73,647]],1.55);
 cord(x,[[45,637],[39,629],[34,620],[34,611],[34,607],[34,605],[34,601]],1.55);
 x.save();x.fillStyle='rgba(20,17,13,.22)';x.filter='blur(1.3px)';x.beginPath();x.ellipse(650,735,35,4.1,0,0,Math.PI*2);x.fill();x.restore();
 poly(x,[[616,718],[679,718],[684,728],[621,728]],'#e8e2d4');
 poly(x,[[621,728],[684,728],[683,736],[619,735]],'#cbc4b4');
 poly(x,[[616,718],[621,728],[619,735],[615,726]],'#b7b09f');
 x.save();x.strokeStyle='#625d53';x.lineWidth=1.2;x.lineCap='round';
 for(const cx of [632,665]){x.beginPath();x.moveTo(cx-2,721.4);x.lineTo(cx-1.2,724.3);x.moveTo(cx+2,721.4);x.lineTo(cx+2.8,724.3);x.stroke();}
 x.fillStyle='#7d7b70';x.beginPath();x.ellipse(675,724,.85,.55,0,0,Math.PI*2);x.fill();x.restore();
 // Charger housing stays inserted after S06; no exposed prongs or glowing indicator.
 poly(x,[[641,708],[649,708],[651,721.5],[642,722.5]],'#e8e5dc');
 poly(x,[[649,708],[651,706.5],[653,720],[651,721.5]],'#c4c1b8');
 poly(x,[[641,708],[643,706.5],[651,706.5],[649,708]],'#f0eee6');
 const [px,py]=phonePort;
 cord(x,[[646,707],[630,698],[625,Math.max(py+17,670)],[px,py]],1.05);
 // The tiny plug end is behind the real phone outline/fingers, not a floating contact.
 x.save();x.translate(px,py);x.rotate(-.25);x.fillStyle='#c7c5bc';x.strokeStyle=outline;x.lineWidth=.35;x.beginPath();x.rect(-1.4,-.8,2.8,1.6);x.fill();x.stroke();x.restore();
}
export function s07PhonePort(f){if(f<3)return[647,651];if(f<6)return[646,655];if(f<8)return[646.5,659.5];return LANDED_PHONE_PORT;}
export function openingPowerStripLayer(phonePort=HELD_PHONE_PORT){
 const key=phonePort.join(',');
 if(!cache.has(key)){const c=new OffscreenCanvas(1672,941),x=c.getContext('2d');drawPowerStrip(x,phonePort);cache.set(key,{img:c,x:0,y:0,sc:1});}
 return cache.get(key);
}
