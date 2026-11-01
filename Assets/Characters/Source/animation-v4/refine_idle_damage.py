import bpy,math,json,os
from mathutils import Vector
ROOT='D:/GodotProjects/dungeons-n-academics'
exec(compile(open(ROOT+'/Assets/Characters/Source/animation-v1/animlib.py').read(),'helpers','exec'))
BASE=ROOT+'/Assets/Characters/Source/animation-v4'
def linear(a):
 for layer in a.layers:
  for st in layer.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
def current_pose(r):
 p=Pose.__new__(Pose);p.rig=r;p.m={b.name:b.matrix.copy() for b in r.pose.bones};p.errors=[];return p
def calm_right(p):
 shoulder=p.base('upper_arm.R').translation
 u=Vector((-.24,-.015,-.97)).normalized();v=Vector((-.16,-.14,-.977)).normalized()
 elbow=shoulder+u*p.rig.data.bones['upper_arm.R'].length
 wrist=elbow+v*p.rig.data.bones['forearm.R'].length
 p.direction('upper_arm.R',shoulder,elbow);p.direction('forearm.R',elbow,wrist)
 p.direction('hand.R',wrist,wrist+Vector((-.012,-.005,-.14)))
r=bpy.data.objects['Brother_AnimRig_v1'];s=bpy.data.scenes['Brother_Animation_v1'];bpy.context.window.scene=s
a=bpy.data.actions['Brother_Idle_v3'].copy();a.name='Brother_Idle_v11';a.use_fake_user=True;r.animation_data.action=a
for f in range(1,74):
 s.frame_set(f);bpy.context.view_layer.update();p=current_pose(r);calm_right(p);p.finish()
 for n in ['upper_arm.R','forearm.R','hand.R']:
  r.pose.bones[n].keyframe_insert('rotation_quaternion',frame=f,group=n);r.pose.bones[n].keyframe_insert('location',frame=f,group=n)
linear(a);r.animation_data.nla_tracks['Idle'].strips[0].action=a
bpy.data.objects['REVIEW_Idle_Brother_Rig'].animation_data.action=a
audit={}
for label in ['Brother','Sister']:
 s=bpy.data.scenes[label+'_Animation_v1'];bpy.context.window.scene=s;r=bpy.data.objects[label+'_AnimRig_v1']
 idle=bpy.data.actions[label+'_Idle_'+('v11' if label=='Brother' else 'v3')];r.animation_data.action=idle;s.frame_set(1);bpy.context.view_layer.update()
 neutral={b.name:b.matrix_basis.copy() for b in r.pose.bones};wrists={side:r.pose.bones['hand.'+side].matrix.translation.copy() for side in ['L','R']}
 a=bpy.data.actions.new(label+'_TakeDamage_v11');a.use_fake_user=True;a['duration_seconds']=1.0;a['export_clip']='TakeDamage';a['loop']=False;r.animation_data.action=a
 errors=[]
 for f in range(1,26):
  s.frame_set(f);t=(f-1)/24
  hit=shape_curve(t,[(0,0),(.125,1),(.25,.95),(.45,.6),(.72,.14),(1,0)])
  lag=shape_curve(t,[(0,0),(.08,.15),(.22,1),(.38,.9),(.65,.12),(.82,-.16),(1,0)])
  settle=shape_curve(t,[(0,0),(.35,0),(.55,1),(.8,.3),(1,0)])
  p=Pose(r);p.rotate('root')
  p.rotate('pelvis',(-3*hit,3*hit,3*hit),shift=(.035*hit,.065*hit,-.012-.065*hit-.015*settle))
  p.rotate('spine',(-8*hit+3*settle,-6*hit,5*hit))
  p.rotate('chest',(-15*hit+6*settle,-9*hit,8*hit))
  p.rotate('neck',(-4*lag,0,-3*lag));p.rotate('head',(-9*lag,4*lag,-7*lag))
  for side in ['L','R']:
   b=r.data.bones['foot.'+side];end=p.ik('thigh.'+side,'shin.'+side,b.head_local,(b.head_local.x,-1,.45));p.put('foot.'+side,mat(b.matrix_local.to_quaternion(),end));p.rotate('toe.'+side)
  for side in ['L','R']:p.rotate('clavicle.'+side,(0,0,(-4 if side=='R' else 5)*hit))
  for side in ['L','R']:
   sign=1 if side=='L' else -1
   target=wrists[side]+Vector((sign*.075*hit,-(.14 if side=='R' else .20)*hit,(.23 if side=='R' else .29)*hit))
   end=p.ik('upper_arm.'+side,'forearm.'+side,target,(sign*.35,-.25,1.04-.54*hit))
   p.direction('hand.'+side,end,end+Vector((sign*(.012+.035*lag),-.005-.05*lag,-.14)))
  p.grips('');p.finish();errors.append(max(p.errors))
  # Exact neutral endpoints keep transitions to the updated Idle seamless.
  if f in [1,25]:
   for b in r.pose.bones:b.matrix_basis=neutral[b.name]
  for b in r.pose.bones:
   b.keyframe_insert('rotation_quaternion',frame=f,group=b.name);b.keyframe_insert('location',frame=f,group=b.name)
 linear(a);strip=r.animation_data.nla_tracks['TakeDamage'].strips[0];strip.action=a;strip.action_frame_end=25;strip.frame_end=25
 bpy.data.objects['REVIEW_TakeDamage_'+label+'_Rig'].animation_data.action=a
 r.animation_data.action=idle;s.frame_set(1);audit[label]={'max_ik_error_m':max(errors),'damage_duration_seconds':1.0}
bpy.data.scenes['ANIM_REVIEW_TakeDamage'].frame_end=24
json.dump(audit,open(BASE+'/authoring-audit.json','w'),indent=2)
result=audit


