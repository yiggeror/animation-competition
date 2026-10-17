import {stateAt,CONFIG} from '../../js/motion/pullcord_proof.js';
import fs from 'node:fs';
const result={samples:721,maxBoneError:0,maxFingerBoneError:0,maxToeError:0,maxWristError:0,maxContactError:0,minHeelHeight:Infinity,maxHeelHeight:0,maxJointStep:0,finite:true,frameMetrics:[]};
const length=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);let prev;
for(let i=0;i<=720;i++){
 const t=i/240,m=stateAt(t).metrics;
 result.maxToeError=Math.max(result.maxToeError,m.toeErrorN,m.toeErrorF);
 result.maxWristError=Math.max(result.maxWristError,m.wristError);
 result.minHeelHeight=Math.min(result.minHeelHeight,m.heelHeightN,m.heelHeightF);result.maxHeelHeight=Math.max(result.maxHeelHeight,m.heelHeightN,m.heelHeightF);
 if(t>=1.08&&t<=2.05)result.maxContactError=Math.max(result.maxContactError,m.gripError);
 for(const b of m.bones)result.maxBoneError=Math.max(result.maxBoneError,Math.abs(b.length-b.nominal));
 for(const f of Object.values(m.fingers).flat())for(const [a,b,l] of [[f.base,f.joint,f.lengths[0]],[f.joint,f.tip,f.lengths[1]]])result.maxFingerBoneError=Math.max(result.maxFingerBoneError,Math.abs(length(a,b)-l));
 for(const [n,p] of Object.entries(m.joints)){if(!p.every(Number.isFinite))result.finite=false;if(prev)result.maxJointStep=Math.max(result.maxJointStep,length(p,prev.joints[n]));}
 if(i%10===0&&i<720)result.frameMetrics.push(m);prev=m;
}
result.startEndFlat=Math.abs(stateAt(0).metrics.heelHeightN)<1e-9&&Math.abs(stateAt(3).metrics.heelHeightN)<1e-9;
result.passed=result.finite&&result.startEndFlat&&result.maxBoneError<1e-6&&result.maxFingerBoneError<1e-6&&result.maxToeError<1e-6&&result.maxWristError<1e-6&&result.maxContactError<1e-6&&result.minHeelHeight>-.001;
if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({...result,frameMetrics:'72 complete frames exported'},null,2));if(!result.passed)process.exitCode=1;
