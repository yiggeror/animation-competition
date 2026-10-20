export function createEarlyPhysicalRenderers({drawPuppet}) { const W=1920,H=1080,LINE="#3e2a1e"; const map={};
{function draw(data){
 const c=new OffscreenCanvas(W,H),x=c.getContext('2d'),A=data.A,p=A.points_scene;
 // True3D plane tilt + fixed yaw/pitch projection;no whole-bird squash factor.
 const yaw=15*Math.PI/180,pitch=12*Math.PI/180,tilt=55*Math.PI/180,K=.72;
 const e1=[K*Math.cos(yaw),-K*Math.sin(pitch)*Math.sin(yaw)];
 const e2=[-K*Math.cos(tilt)*Math.sin(yaw),-K*(Math.sin(tilt)*Math.cos(pitch)+Math.cos(tilt)*Math.cos(yaw)*Math.sin(pitch))];
 x.save();x.transform(e1[0],e1[1],e2[0],e2[1],p.crane_root[0],p.crane_root[1]);drawPuppet(x,data.crane,A.code_pose,'r');x.restore();
 // Unheld rod ends are supported by the narrow box rim, collinear through approved rim points.
 for(const [start,end] of [[p.free_gripR,p.P_body],[p.free_gripL,p.P_neck]]){
  x.strokeStyle=LINE;x.lineWidth=7;x.lineCap='round';x.beginPath();x.moveTo(...start);x.lineTo(...end);x.stroke();x.strokeStyle='#c99a52';x.lineWidth=3;x.stroke();
 }
 return {img:c,x:0,y:0,sc:1};
}
map["F000"]=draw;}
{function draw(data){
 const c=new OffscreenCanvas(W,H),x=c.getContext('2d'),A=data.A,p=A.points_scene;
 // True3D plane tilt + fixed yaw/pitch projection;no whole-bird squash factor.
 const yaw=15*Math.PI/180,pitch=12*Math.PI/180,tilt=55*Math.PI/180,K=.72;
 const e1=[K*Math.cos(yaw),-K*Math.sin(pitch)*Math.sin(yaw)];
 const e2=[-K*Math.cos(tilt)*Math.sin(yaw),-K*(Math.sin(tilt)*Math.cos(pitch)+Math.cos(tilt)*Math.cos(yaw)*Math.sin(pitch))];
 x.save();x.transform(e1[0],e1[1],e2[0],e2[1],p.crane_root[0],p.crane_root[1]);drawPuppet(x,data.crane,A.code_pose,'r');x.restore();
 // Unheld rod ends are supported by the narrow box rim, collinear through approved rim points.
 for(const [start,end] of [[p.free_gripR,p.P_body],[p.free_gripL,p.P_neck]]){
  x.strokeStyle=LINE;x.lineWidth=7;x.lineCap='round';x.beginPath();x.moveTo(...start);x.lineTo(...end);x.stroke();x.strokeStyle='#c99a52';x.lineWidth=3;x.stroke();
 }
 return {img:c,x:0,y:0,sc:1};
}
map["F012"]=draw;}
{function draw(data){
 const c=new OffscreenCanvas(W,H),x=c.getContext('2d'),A=data.A,p=A.points_scene;
 // True3D plane tilt + fixed yaw/pitch projection;no whole-bird squash factor.
 const yaw=15*Math.PI/180,pitch=12*Math.PI/180,tilt=55*Math.PI/180,K=.72;
 const e1=[K*Math.cos(yaw),-K*Math.sin(pitch)*Math.sin(yaw)];
 const e2=[-K*Math.cos(tilt)*Math.sin(yaw),-K*(Math.sin(tilt)*Math.cos(pitch)+Math.cos(tilt)*Math.cos(yaw)*Math.sin(pitch))];
 x.save();x.transform(e1[0],e1[1],e2[0],e2[1],p.crane_root[0],p.crane_root[1]);drawPuppet(x,data.crane,A.code_pose,'r');x.restore();
 // Unheld rod ends are supported by the narrow box rim, collinear through approved rim points.
 for(const [start,end] of [[p.free_gripR,p.P_body],[p.free_gripL,p.P_neck]]){
  x.strokeStyle=LINE;x.lineWidth=7;x.lineCap='round';x.beginPath();x.moveTo(...start);x.lineTo(...end);x.stroke();x.strokeStyle='#c99a52';x.lineWidth=3;x.stroke();
 }
 return {img:c,x:0,y:0,sc:1};
}
map["F012"]=draw;}
{function draw(data){
 const c=new OffscreenCanvas(W,H),x=c.getContext('2d'),A=data.A,p=A.points_scene;
 // True3D plane tilt + fixed yaw/pitch projection;no whole-bird squash factor.
 const yaw=15*Math.PI/180,pitch=12*Math.PI/180,tilt=55*Math.PI/180,K=.72;
 const e1=[K*Math.cos(yaw),-K*Math.sin(pitch)*Math.sin(yaw)];
 const e2=[-K*Math.cos(tilt)*Math.sin(yaw),-K*(Math.sin(tilt)*Math.cos(pitch)+Math.cos(tilt)*Math.cos(yaw)*Math.sin(pitch))];
 x.save();x.transform(e1[0],e1[1],e2[0],e2[1],p.crane_root[0],p.crane_root[1]);drawPuppet(x,data.crane,A.code_pose,'r');x.restore();
 // Unheld rod ends are supported by the narrow box rim, collinear through approved rim points.
 for(const [start,end] of [[p.free_gripR,p.P_body],[p.free_gripL,p.P_neck]]){
  x.strokeStyle=LINE;x.lineWidth=7;x.lineCap='round';x.beginPath();x.moveTo(...start);x.lineTo(...end);x.stroke();x.strokeStyle='#c99a52';x.lineWidth=3;x.stroke();
 }
 return {img:c,x:0,y:0,sc:1};
}
map["F018"]=draw;}
{function draw(data){
 const c=new OffscreenCanvas(W,H),x=c.getContext('2d'),A=data.A,p=A.points_scene;
 // True3D plane tilt + fixed yaw/pitch projection;no whole-bird squash factor.
 const yaw=15*Math.PI/180,pitch=12*Math.PI/180,tilt=55*Math.PI/180,K=.72;
 const e1=[K*Math.cos(yaw),-K*Math.sin(pitch)*Math.sin(yaw)];
 const e2=[-K*Math.cos(tilt)*Math.sin(yaw),-K*(Math.sin(tilt)*Math.cos(pitch)+Math.cos(tilt)*Math.cos(yaw)*Math.sin(pitch))];
 x.save();x.transform(e1[0],e1[1],e2[0],e2[1],p.crane_root[0],p.crane_root[1]);drawPuppet(x,data.crane,A.code_pose,'r');x.restore();
 // Unheld rod ends are supported by the narrow box rim, collinear through approved rim points.
 for(const [start,end] of [[p.free_gripR,p.P_body],[p.free_gripL,p.P_neck]]){
  x.strokeStyle=LINE;x.lineWidth=7;x.lineCap='round';x.beginPath();x.moveTo(...start);x.lineTo(...end);x.stroke();x.strokeStyle='#c99a52';x.lineWidth=3;x.stroke();
 }
 return {img:c,x:0,y:0,sc:1};
}
map["F022"]=draw;}
{function draw(data){
 const c=new OffscreenCanvas(W,H),x=c.getContext('2d'),A=data.A,p=A.points_scene;
 // True3D plane tilt + fixed yaw/pitch projection;no whole-bird squash factor.
 const yaw=15*Math.PI/180,pitch=12*Math.PI/180,tilt=55*Math.PI/180,K=.72;
 const e1=[K*Math.cos(yaw),-K*Math.sin(pitch)*Math.sin(yaw)];
 const e2=[-K*Math.cos(tilt)*Math.sin(yaw),-K*(Math.sin(tilt)*Math.cos(pitch)+Math.cos(tilt)*Math.cos(yaw)*Math.sin(pitch))];
 x.save();x.transform(e1[0],e1[1],e2[0],e2[1],p.crane_root[0],p.crane_root[1]);drawPuppet(x,data.crane,A.code_pose,'r');x.restore();
 // Unheld rod ends are supported by the narrow box rim, collinear through approved rim points.
 for(const [start,end] of [[p.free_gripR,p.P_body],[p.free_gripL,p.P_neck]]){
  x.strokeStyle=LINE;x.lineWidth=7;x.lineCap='round';x.beginPath();x.moveTo(...start);x.lineTo(...end);x.stroke();x.strokeStyle='#c99a52';x.lineWidth=3;x.stroke();
 }
 return {img:c,x:0,y:0,sc:1};
}
map["F026"]=draw;}
{function draw(data){
 const c=new OffscreenCanvas(W,H),x=c.getContext('2d'),A=data.A,p=A.points_scene;
 // True3D plane tilt + fixed yaw/pitch projection;no whole-bird squash factor.
 const yaw=15*Math.PI/180,pitch=12*Math.PI/180,tilt=55*Math.PI/180,K=.72;
 const e1=[K*Math.cos(yaw),-K*Math.sin(pitch)*Math.sin(yaw)];
 const e2=[-K*Math.cos(tilt)*Math.sin(yaw),-K*(Math.sin(tilt)*Math.cos(pitch)+Math.cos(tilt)*Math.cos(yaw)*Math.sin(pitch))];
 x.save();x.transform(e1[0],e1[1],e2[0],e2[1],p.crane_root[0],p.crane_root[1]);drawPuppet(x,data.crane,A.code_pose,'r');x.restore();
 // Unheld rod ends are supported by the narrow box rim, collinear through approved rim points.
 for(const [start,end] of [[p.free_gripR,p.P_body],[p.free_gripL,p.P_neck]]){
  x.strokeStyle=LINE;x.lineWidth=7;x.lineCap='round';x.beginPath();x.moveTo(...start);x.lineTo(...end);x.stroke();x.strokeStyle='#c99a52';x.lineWidth=3;x.stroke();
 }
 return {img:c,x:0,y:0,sc:1};
}
map["F030"]=draw;}
{function draw(data){
 const c=new OffscreenCanvas(W,H),x=c.getContext('2d'),A=data.A,p=A.points_scene;
 // True3D plane tilt + fixed yaw/pitch projection;no whole-bird squash factor.
 const yaw=15*Math.PI/180,pitch=12*Math.PI/180,tilt=55*Math.PI/180,K=.72;
 const e1=[K*Math.cos(yaw),-K*Math.sin(pitch)*Math.sin(yaw)];
 const e2=[-K*Math.cos(tilt)*Math.sin(yaw),-K*(Math.sin(tilt)*Math.cos(pitch)+Math.cos(tilt)*Math.cos(yaw)*Math.sin(pitch))];
 x.save();x.transform(e1[0],e1[1],e2[0],e2[1],p.crane_root[0],p.crane_root[1]);drawPuppet(x,data.crane,A.code_pose,'r');x.restore();
 // Unheld rod ends are supported by the narrow box rim, collinear through approved rim points.
 for(const [start,end] of [[p.free_gripR,p.P_body],[[931.5123178589768,757.1297395769899],p.P_neck]]){
  x.strokeStyle=LINE;x.lineWidth=7;x.lineCap='round';x.beginPath();x.moveTo(...start);x.lineTo(...end);x.stroke();x.strokeStyle='#c99a52';x.lineWidth=3;x.stroke();
 }
 return {img:c,x:0,y:0,sc:1};
}
map["F034"]=draw;}
{function draw(data){
 const c=new OffscreenCanvas(W,H),x=c.getContext('2d'),A=data.A,p=A.points_scene;
 // True3D plane tilt + fixed yaw/pitch projection;no whole-bird squash factor.
 const yaw=15*Math.PI/180,pitch=12*Math.PI/180,tilt=55*Math.PI/180,K=.72;
 const e1=[K*Math.cos(yaw),-K*Math.sin(pitch)*Math.sin(yaw)];
 const e2=[-K*Math.cos(tilt)*Math.sin(yaw),-K*(Math.sin(tilt)*Math.cos(pitch)+Math.cos(tilt)*Math.cos(yaw)*Math.sin(pitch))];
 x.save();x.transform(e1[0],e1[1],e2[0],e2[1],p.crane_root[0],p.crane_root[1]);drawPuppet(x,data.crane,A.code_pose,'r');x.restore();
 // Unheld rod ends are supported by the narrow box rim, collinear through approved rim points.
 for(const [start,end] of [[p.free_gripR,p.P_body],[[930.1059238245394,729.1297395769899],p.P_neck]]){
  x.strokeStyle=LINE;x.lineWidth=7;x.lineCap='round';x.beginPath();x.moveTo(...start);x.lineTo(...end);x.stroke();x.strokeStyle='#c99a52';x.lineWidth=3;x.stroke();
 }
 return {img:c,x:0,y:0,sc:1};
}
map["F040"]=draw;}
{function draw(data){
 const c=new OffscreenCanvas(W,H),x=c.getContext('2d'),A=data.A,p=A.points_scene;
 // True3D plane tilt + fixed yaw/pitch projection;no whole-bird squash factor.
 const yaw=15*Math.PI/180,pitch=12*Math.PI/180,tilt=55*Math.PI/180,K=.72;
 const e1=[K*Math.cos(yaw),-K*Math.sin(pitch)*Math.sin(yaw)];
 const e2=[-K*Math.cos(tilt)*Math.sin(yaw),-K*(Math.sin(tilt)*Math.cos(pitch)+Math.cos(tilt)*Math.cos(yaw)*Math.sin(pitch))];
 x.save();x.transform(e1[0],e1[1],e2[0],e2[1],p.crane_root[0],p.crane_root[1]);drawPuppet(x,data.crane,A.code_pose,'r');x.restore();
 // Unheld rod ends are supported by the narrow box rim, collinear through approved rim points.
 for(const [start,end] of [[p.free_gripR,p.P_body],[[930.1059238245394,729.1297395769899],p.P_neck]]){
  x.strokeStyle=LINE;x.lineWidth=7;x.lineCap='round';x.beginPath();x.moveTo(...start);x.lineTo(...end);x.stroke();x.strokeStyle='#c99a52';x.lineWidth=3;x.stroke();
 }
 return {img:c,x:0,y:0,sc:1};
}
map["F048"]=draw;}
{function draw(data){
 const c=new OffscreenCanvas(W,H),x=c.getContext('2d'),A=data.A,p=A.points_scene;
 // True3D plane tilt + fixed yaw/pitch projection;no whole-bird squash factor.
 const yaw=15*Math.PI/180,pitch=12*Math.PI/180,tilt=55*Math.PI/180,K=.72;
 const e1=[K*Math.cos(yaw),-K*Math.sin(pitch)*Math.sin(yaw)];
 const e2=[-K*Math.cos(tilt)*Math.sin(yaw),-K*(Math.sin(tilt)*Math.cos(pitch)+Math.cos(tilt)*Math.cos(yaw)*Math.sin(pitch))];
 x.save();x.transform(e1[0],e1[1],e2[0],e2[1],p.crane_root[0],p.crane_root[1]);drawPuppet(x,data.crane,A.code_pose,'r');x.restore();
 // Unheld rod ends are supported by the narrow box rim, collinear through approved rim points.
 for(const [start,end] of [[p.free_gripR,p.P_body],[[930.1059238245394,729.1297395769899],p.P_neck]]){
  x.strokeStyle=LINE;x.lineWidth=7;x.lineCap='round';x.beginPath();x.moveTo(...start);x.lineTo(...end);x.stroke();x.strokeStyle='#c99a52';x.lineWidth=3;x.stroke();
 }
 return {img:c,x:0,y:0,sc:1};
}
map["F052"]=draw;}
map.F056=map.F052;
map.F060=map.F052;
map.F064=map.F052;
return map;}