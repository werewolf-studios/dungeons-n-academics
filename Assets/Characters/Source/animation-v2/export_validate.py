import bpy,json,os,math,hashlib
from mathutils import Vector
BASE='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v2'
OLD=BASE.replace('animation-v2','animation-v1')
OUT='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Animated/v2'
os.makedirs(OUT,exist_ok=True)
exec(compile(open(BASE+'/refine.py').read().split('audit={}')[0],'defs','exec'))
refs={};audit={}
def action(label,clip):return bpy.data.actions[label+'_'+clip+('_v6' if clip in ['Walk','Run','SwordSlash'] else '_v3')]
for label in ['Brother','Sister']:
 s=bpy.data.scenes[label+'_Animation_v1'];bpy.context.window.scene=s
 rig=bpy.data.objects[label+'_AnimRig_v1'];mesh=bpy.data.objects[label+'_AnimMesh_v1'];refs[label.lower()]={};audit[label]={}
 for clip,(length,loop,weapon) in SPECS.items():
  rig.animation_data.action=action(label,clip);samples=[];poses=[];minz=100;finite=True
  for f in range(1,length+2):
   s.frame_set(f);bpy.context.view_layer.update()
   poses.append({b.name:b.matrix.copy() for b in rig.pose.bones})
   finite=finite and all(math.isfinite(v) for b in rig.pose.bones for row in b.matrix for v in row)
   if clip in ['Walk','Run','SwordSlash']:
    evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());minz=min(minz,min((evaluated.matrix_world@v.co).z for v in evaluated.data.vertices))
  looperr=max(abs(poses[0][n][i][j]-poses[-1][n][i][j]) for n in poses[0] for i in range(4) for j in range(4)) if loop else None
  assert finite and (looperr is None or looperr<1e-5)
  audit[label][clip]={'finite':finite,'loop_matrix_error':looperr,'mesh_min_z':minz if minz<100 else None}
  for t in [0,.25,.5,.75,1]:
   f=1+t*length;s.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();points={}
   for name in ['pelvis','head','hand.R','hand.L','foot.R','foot.L','tunic.R','tunic.L']:
    p=rig.pose.bones[name].matrix.translation;points[name]=[p.x,p.z,-p.y]
   samples.append({'fraction':t,'points':points})
  refs[label.lower()][clip]=samples
 mesh.data.calc_loop_triangles()
 audit[label]['mesh']={'triangles':len(mesh.data.loop_triangles),'vertices':len(mesh.data.vertices),'max_influences':max(len([g for g in v.groups if g.weight>1e-6]) for v in mesh.data.vertices),'unweighted':sum(not any(g.weight>1e-6 for g in v.groups) for v in mesh.data.vertices)}
 rig.animation_data.action=None
 for tr in rig.animation_data.nla_tracks:tr.mute=False
 activate(mesh);rig.select_set(True);s.frame_set(1)
 bpy.ops.export_scene.gltf(filepath=OUT+'/'+label.lower()+'-animations-v2.glb',export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_bake_animation=True,export_anim_slide_to_zero=True,export_frame_step=1,export_optimize_animation_size=False,export_skins=True,export_influence_nb=4,export_all_influences=False,export_def_bones=False,export_leaf_bone=False,export_yup=True,export_materials='EXPORT',export_rest_position_armature=True)
 for tr in rig.animation_data.nla_tracks:tr.mute=True
 rig.animation_data.action=action(label,'Idle');s.frame_set(1)
json.dump(refs,open(BASE+'/pose-reference.json','w'),indent=2)
json.dump(audit,open(BASE+'/validation.json','w'),indent=2)
manifest=json.load(open(OUT.replace('/v2','/v1')+'/animation-manifest.json'))
manifest['clips']['SwordSlash'].update(duration=1.5,event_frame=19,event_time_seconds=.75)
manifest['revision']='v2: Walk, Run and stepping SwordSlash refined; other five clips unchanged.'
manifest['godot_runtime_status']='v1 preview confirmed working by user; v2 awaiting user visual review.'
json.dump(manifest,open(OUT+'/animation-manifest.json','w'),indent=2)
# Independently evaluate exported channels against Blender sample positions.
code=open(OLD+'/08_glb_compare.py').read()
code=code.replace("refs=json.load", "BASE='"+BASE+"'\nrefs=json.load")
code=code.replace('Animated/v1/','Animated/v2/').replace('-animations-v1.glb','-animations-v2.glb')
exec(compile(code,'raw_comparison','exec'))
