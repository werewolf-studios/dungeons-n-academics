import bpy,os,json,math
from mathutils import Vector,Matrix,Quaternion
BASE='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v3'
os.makedirs(BASE+'/review',exist_ok=True)
checkpoint=BASE+'/siblings-animation-v007-live-checkpoint.blend'
assert not os.path.exists(checkpoint)
bpy.ops.wm.save_as_mainfile(filepath=checkpoint,compress=True)
exec(compile(open(BASE.replace('animation-v3','animation-v1')+'/animlib.py').read(),'helpers','exec'))
BASE='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v3'
audit={}
for label in ['Brother','Sister']:
 s=bpy.data.scenes[label+'_Animation_v1'];bpy.context.window.scene=s;r=bpy.data.objects[label+'_AnimRig_v1'];audit[label]={}
 for clip,suffix,length in [('SwordIdle','v3',48),('SwordSlash','v6',36)]:
  old=bpy.data.actions[label+'_'+clip+'_'+suffix];a=old.copy();a.name=label+'_'+clip+'_v7';a.use_fake_user=True
  targets=[]
  r.animation_data.action=old
  for f in range(1,length+2):
   s.frame_set(f);bpy.context.view_layer.update();H=r.pose.bones['hand.R'].matrix.copy()
   targets.append((H@Vector((.025,.085,0)),H.to_3x3()@Vector((0,0,1))))
  r.animation_data.action=a;errors=[]
  for f,(grip,blade) in enumerate(targets,1):
   s.frame_set(f);bpy.context.view_layer.update()
   p=Pose.__new__(Pose);p.rig=r;p.m={b.name:b.matrix.copy() for b in r.pose.bones};p.errors=[]
   # Thumb is on hand-local -Z. Blade points toward thumb, not little finger.
   z=-blade.normalized();y=Vector((0,-1,-.1));y-=z*y.dot(z);y.normalize();x=y.cross(z).normalized();R=Matrix((x,y,z)).transposed()
   wrist=grip-R@Vector((.025,.085,0))
   end=p.ik('upper_arm.R','forearm.R',wrist,(-.62,.08,1.08))
   # Carry the grip roll through the forearm instead of twisting only the wrist.
   F=p.m['forearm.R'];fy=(end-F.translation).normalized();fx=x-fy*x.dot(fy);fx.normalize();fz=fx.cross(fy).normalized()
   p.put('forearm.R',mat(Matrix((fx,fy,fz)).transposed(),F.translation))
   p.put('hand.R',mat(R,end));p.finish()
   errors.append((r.pose.bones['hand.R'].matrix@Vector((.025,.085,0))-grip).length)
   for n in ['upper_arm.R','forearm.R','hand.R']:
    b=r.pose.bones[n];b.keyframe_insert('rotation_quaternion',frame=f,group=n);b.keyframe_insert('location',frame=f,group=n)
  for layer in a.layers:
   for st in layer.strips:
    for bag in st.channelbags:
     for fc in bag.fcurves:
      for k in fc.keyframe_points:k.interpolation='LINEAR'
  r.animation_data.nla_tracks[clip].strips[0].action=a
  bpy.data.objects['REVIEW_'+clip+'_'+label+'_Rig'].animation_data.action=a
  audit[label][clip]={'max_grip_position_change_m':max(errors),'frames':length+1}
 r.animation_data.action=bpy.data.actions[label+'_Idle_v3'];s.frame_set(1)
 # Compensate sword-only socket; source weapon geometry and spear sockets untouched.
 for name in [label+'_Anim_Sword','REVIEW_SwordIdle_'+label+'_Sword','REVIEW_SwordSlash_'+label+'_Sword']:
  o=bpy.data.objects[name];o.rotation_mode='QUATERNION';o.rotation_quaternion=Quaternion((1,0,0),math.pi)
json.dump(audit,open(BASE+'/grip-audit.json','w'),indent=2)
result=audit
