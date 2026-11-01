import bpy,os,json,math
BASE='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v5'
os.makedirs(BASE+'/review',exist_ok=True)
for label in ['Brother','Sister']:
 s=bpy.data.scenes[label+'_Animation_v1'];bpy.context.window.scene=s;r=bpy.data.objects[label+'_AnimRig_v1'];old=bpy.data.actions[label+'_TakeDamage_v11'];r.animation_data.action=old
 names=[part+'.'+side for side in ['L','R'] for part in ['upper_arm','forearm','hand']]
 samples={}
 for f in [1,5]:
  s.frame_set(f);bpy.context.view_layer.update();samples[f]={n:(r.pose.bones[n].rotation_quaternion.copy(),r.pose.bones[n].location.copy()) for n in names}
 a=old.copy();a.name=label+'_TakeDamage_v12';a.use_fake_user=True;r.animation_data.action=a
 previous={}
 for f in range(1,26):
  s.frame_set(f)
  if f<=5:t=(f-1)/4;amount=t*t*(3-2*t)
  elif f<=7:amount=1
  else:t=(f-7)/18;amount=1-t*t*(3-2*t)
  for n in names:
   q0,l0=samples[1][n];q1,l1=samples[5][n];q=q0.slerp(q1,amount)
   if n in previous and previous[n].dot(q)<0:q.negate()
   previous[n]=q.copy();b=r.pose.bones[n];b.rotation_quaternion=q;b.location=l0.lerp(l1,amount)
   b.keyframe_insert('rotation_quaternion',frame=f,group=n);b.keyframe_insert('location',frame=f,group=n)
 for layer in a.layers:
  for st in layer.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
 r.animation_data.nla_tracks['TakeDamage'].strips[0].action=a
 bpy.data.objects['REVIEW_TakeDamage_'+label+'_Rig'].animation_data.action=a
 r.animation_data.action=bpy.data.actions[label+'_Idle_'+('v11' if label=='Brother' else 'v3')]
# Reuse proven export checks with the new damage actions and a new output directory.
wrapper=open(BASE.replace('animation-v5','animation-v4')+'/export_validate.py').read()
exec(compile(wrapper.rsplit('exec(compile(code',1)[0],'export_setup','exec'))
code=code.replace('animation-v4','animation-v5').replace('Animated/v4','Animated/v5').replace('-animations-v4.glb','-animations-v5.glb')
code=code.replace("('_v11' if clip=='TakeDamage' or (clip=='Idle' and label=='Brother')", "('_v12' if clip=='TakeDamage' else '_v11' if (clip=='Idle' and label=='Brother')")
code=code.replace('v4: Brother right-arm Idle correction and stronger TakeDamage for both.','v5: smooth quaternion arm recovery for TakeDamage; other clips unchanged.')
exec(compile(code,'export_v5','exec'))
