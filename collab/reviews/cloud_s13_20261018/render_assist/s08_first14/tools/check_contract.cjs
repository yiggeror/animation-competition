// Verify only pure exposure/range functions; never render the missing frame014.
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const assert=require('assert/strict');
const P=path.resolve(__dirname,'..');
(async()=>{
 const c=await import(pathToFileURL(path.resolve('collab/reviews/20261018_1721_s08_first14_scene/contract.js')).href);
 assert.equal(c.FRAME_COUNT,14);assert.equal(c.DURATION,14/24);
 assert.deepEqual(c.EXPOSE.map(x=>[x.start,x.hold,x.asset]),[[0,3,'000'],[3,2,'003'],[5,1,'005'],[6,3,'006'],[9,3,'009'],[12,2,'005']]);
 const expected=['000','000','000','003','003','005','006','006','006','009','009','009','005','005'];
 const states=[];for(let f=0;f<14;f++){
  const pose=c.poseAt(f/24),fire=c.fireAt(f/24);
  assert.equal(pose.frame,f);assert.equal(pose.asset,expected[f]);assert.equal(fire.lit,f>=5);assert.equal(fire.wick,0);assert.equal(fire.lift,0);
  states.push({frame:f,pose,fire});
 }
 let rejected=false,message='';try{c.frameAt(14/24);}catch(e){rejected=e instanceof RangeError;message=e.message;}
 assert.equal(rejected,true);
 fs.writeFileSync(path.join(P,'contract_runtime.json'),JSON.stringify({status:'PASS_14_FRAME_EXPOSURE_AND_MISSING_FRAME_GUARD',frame014_pure_contract_rejected:rejected,frame014_error:message,frame014_render_called:false,states},null,2)+'\n');
 console.log('PASS five original states/six exposures/14frames;fire from005;wick/lift0;pure frame014 guard throws;no missing-frame render');
})().catch(e=>{console.error(e);process.exitCode=1});
