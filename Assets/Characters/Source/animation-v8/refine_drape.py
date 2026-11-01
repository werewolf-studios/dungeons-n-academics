import bpy,os,json
from mathutils import Vector
BASE='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v8'
r=bpy.data.objects['Brother_AnimRig_v1'];mesh=bpy.data.objects['Brother_AnimMesh_v1'];olddata=mesh.data
data=olddata.copy();data.name='Brother_Animation_UpperTrouserSupport_v8'
for o in bpy.data.objects:
 if o.type=='MESH' and o.data==olddata:o.data=data
groups={g.name:g.index for g in mesh.vertex_groups};pelvis=mesh.vertex_groups['pelvis'];changed=0
for v in data.vertices:
 weights={mesh.vertex_groups[g.group].name:g.weight for g in v.groups}
 if sum(weights.get(n,0) for n in ['thigh.L','thigh.R'])<.5 or v.co.z<.68:continue
 if sum(weights.get(n,0) for n in ['tunic.L','tunic.R'])>.01:continue
 t=max(0,min(1,(v.co.z-.68)/.20));support=.95*t*t*(3-2*t);transfer=0
 for n in ['thigh.L','thigh.R']:
  w=weights.get(n,0);transfer+=w*support
  if w:mesh.vertex_groups[n].add([v.index],w*(1-support),'REPLACE')
 if transfer:pelvis.add([v.index],weights.get('pelvis',0)+transfer,'REPLACE');changed+=1
s=bpy.data.scenes['Brother_Animation_v1'];bpy.context.window.scene=s
for clip in ['Walk','Run']:
 old=bpy.data.actions['Brother_'+clip+'_v14'];a=old.copy();a.name='Brother_'+clip+'_v15';a.use_fake_user=True;r.animation_data.action=a
 for f in range(1,int(a.frame_range[1])+1):
  s.frame_set(f)
  for side in ['L','R']:
   b=r.pose.bones['tunic.'+side];shift=Vector((0,-.02,0));parent=b.parent.matrix@b.parent.bone.matrix_local.inverted()@b.bone.matrix_local
   b.location=parent.to_3x3().inverted()@shift;b.keyframe_insert('location',frame=f,group=b.name)
 r.animation_data.nla_tracks[clip].strips[0].action=a;bpy.data.objects['REVIEW_'+clip+'_Brother_Rig'].animation_data.action=a
r.animation_data.action=bpy.data.actions['Brother_Idle_v13']
json.dump({'supported_upper_trouser_vertices':changed,'mesh_copy':data.name,'clearance_forward_m':.02},open(BASE+'/drape-change.json','w'),indent=2)
result={'supported_vertices':changed}
