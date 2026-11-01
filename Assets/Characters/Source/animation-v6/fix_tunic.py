import bpy,json,os
from mathutils import Vector
BASE='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v6'
r=bpy.data.objects['Brother_AnimRig_v1'];s=bpy.data.scenes['Brother_Animation_v1'];bpy.context.window.scene=s
clips={t.name:t.strips[0].action for t in r.animation_data.nla_tracks}
samples={}
for clip,a in clips.items():
 r.animation_data.action=a;samples[clip]=[]
 for f in range(1,int(a.frame_range[1])+1):
  s.frame_set(f);bpy.context.view_layer.update();row={}
  for side in ['L','R']:
   b=r.pose.bones['tunic.'+side];loc=b.location.copy()
   if clip in ['Walk','Run']:
    # Separate the front tunic panels from the swinging trouser thighs.
    shift=Vector((.012 if side=='L' else -.012,-.045,0))
    parent=b.parent.matrix@b.parent.bone.matrix_local.inverted()@b.bone.matrix_local
    loc+=parent.to_3x3().inverted()@shift
   row[side]=loc
  samples[clip].append(row)
for ob in [r]+[o for o in bpy.data.objects if o.name.startswith('REVIEW_') and o.name.endswith('_Brother_Rig')]:
 for d in ob.animation_data.drivers:
  if 'tunic.' in d.data_path:d.mute=True
for clip,old in clips.items():
 a=old.copy();a.name='Brother_'+clip+'_v13';a.use_fake_user=True;r.animation_data.action=a
 for f,row in enumerate(samples[clip],1):
  s.frame_set(f)
  for side,loc in row.items():
   b=r.pose.bones['tunic.'+side];b.location=loc;b.keyframe_insert('location',frame=f,group=b.name)
 for layer in a.layers:
  for st in layer.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
 r.animation_data.nla_tracks[clip].strips[0].action=a
 bpy.data.objects['REVIEW_'+clip+'_Brother_Rig'].animation_data.action=a
r.animation_data.action=bpy.data.actions['Brother_Idle_v13']
result={'corrected':['Brother Walk','Brother Run'],'helper_motion':'Baked existing motion, additional front/outward clearance only in locomotion'}
