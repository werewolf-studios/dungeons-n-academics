import bpy,os,json
from mathutils import Vector
BASE='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v7'
os.makedirs(BASE+'/review',exist_ok=True)
s=bpy.data.scenes['Brother_Animation_v1'];bpy.context.window.scene=s;r=bpy.data.objects['Brother_AnimRig_v1']
for clip in ['Walk','Run']:
 old=bpy.data.actions['Brother_'+clip+'_v13'];r.animation_data.action=old;values={n:[] for n in ['tunic.L','tunic.R']}
 for f in range(1,int(old.frame_range[1])+1):
  s.frame_set(f)
  for n in values:values[n].append(r.pose.bones[n].location.copy())
 # Both panels share a steady clearance pose; remove alternating hem pumping.
 fixed={n:Vector((sum(v.x for v in vs)/len(vs),sum(v.y for v in vs)/len(vs),min(v.z for v in vs))) for n,vs in values.items()}
 a=old.copy();a.name='Brother_'+clip+'_v14';a.use_fake_user=True;r.animation_data.action=a
 for f in range(1,int(a.frame_range[1])+1):
  s.frame_set(f)
  for n,loc in fixed.items():r.pose.bones[n].location=loc;r.pose.bones[n].keyframe_insert('location',frame=f,group=n)
 r.animation_data.nla_tracks[clip].strips[0].action=a;bpy.data.objects['REVIEW_'+clip+'_Brother_Rig'].animation_data.action=a
r.animation_data.action=bpy.data.actions['Brother_Idle_v13']
result={'stabilized':['Walk','Run']}
