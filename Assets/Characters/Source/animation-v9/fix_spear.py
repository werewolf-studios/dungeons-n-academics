import bpy,math,os,json
from mathutils import Vector,Matrix
ROOT='D:/GodotProjects/dungeons-n-academics'
exec(compile(open(ROOT+'/Assets/Characters/Source/animation-v1/animlib.py').read(),'helpers','exec'))
BASE=ROOT+'/Assets/Characters/Source/animation-v9'
report={}
for label in ['Brother','Sister']:
 s=bpy.data.scenes[label+'_Animation_v1'];bpy.context.window.scene=s;r=bpy.data.objects[label+'_AnimRig_v1'];report[label]={}
 for clip,length in [('SpearIdle',48),('SpearThrust',26)]:
  old=bpy.data.actions[label+'_'+clip+('_v13' if label=='Brother' else '_v3')];r.animation_data.action=old;targets=[]
  for f in range(1,length+2):
   s.frame_set(f);bpy.context.view_layer.update();H=r.pose.bones['hand.R'].matrix.copy();targets.append((H@Vector((.025,.085,0)),H.to_3x3()@Vector((0,0,1))))
  a=old.copy();a.name=label+'_'+clip+'_v16';a.use_fake_user=True;r.animation_data.action=a;errors=[];previous={}
  for f,(grip,z) in enumerate(targets,1):
   s.frame_set(f);bpy.context.view_layer.update();p=Pose.__new__(Pose);p.rig=r;p.m={b.name:b.matrix.copy() for b in r.pose.bones};p.errors=[]
   # Extend the hand across the shaft from the forearm, rather than folding down.
   z.normalize();y=Vector((1,0,-.15));y-=z*y.dot(z);y.normalize();x=y.cross(z).normalized();R=Matrix((x,y,z)).transposed()
   wrist=grip-R@Vector((.025,.085,0));end=p.ik('upper_arm.R','forearm.R',wrist,(-.50,.10,.98))
   F=p.m['forearm.R'];fy=(end-F.translation).normalized();fx=x-fy*x.dot(fy);fx.normalize();fz=fx.cross(fy).normalized();p.put('forearm.R',mat(Matrix((fx,fy,fz)).transposed(),F.translation));p.put('hand.R',mat(R,end));p.finish()
   errors.append((r.pose.bones['hand.R'].matrix@Vector((.025,.085,0))-grip).length)
   for n in ['upper_arm.R','forearm.R','hand.R']:
    b=r.pose.bones[n];q=b.rotation_quaternion.copy()
    if n in previous and q.dot(previous[n])<0:q.negate();b.rotation_quaternion=q
    previous[n]=q.copy();b.keyframe_insert('rotation_quaternion',frame=f,group=n);b.keyframe_insert('location',frame=f,group=n)
  for layer in a.layers:
   for st in layer.strips:
    for bag in st.channelbags:
     for fc in bag.fcurves:
      for k in fc.keyframe_points:k.interpolation='LINEAR'
  r.animation_data.nla_tracks[clip].strips[0].action=a;bpy.data.objects['REVIEW_'+clip+'_'+label+'_Rig'].animation_data.action=a
  report[label][clip]={'max_grip_target_change_m':max(errors)}
 r.animation_data.action=bpy.data.actions[label+'_Idle_'+('v13' if label=='Brother' else 'v3')]
json.dump(report,open(BASE+'/grip-check.json','w'),indent=2)
result=report
