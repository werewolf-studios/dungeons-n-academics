exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v1/animlib.py').read(),'animlib','exec'))
OUT='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Animated/v1'
refs={}
for label in ['Brother','Sister']:
 s=bpy.data.scenes[label+'_Animation_v1'];bpy.context.window.scene=s;rig=bpy.data.objects[label+'_AnimRig_v1'];mesh=bpy.data.objects[label+'_AnimMesh_v1'];refs[label.lower()]={}
 for clip,(length,loop,weapon) in SPECS.items():
  rig.animation_data.action=bpy.data.actions[label+'_'+clip+'_v3'];samples=[]
  for t in [0,.25,.5,.75,1]:
   f=1+t*length;s.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();points={}
   for name in ['pelvis','head','hand.R','hand.L','foot.R','foot.L','tunic.R','tunic.L']:
    p=rig.pose.bones[name].matrix.translation;points[name]=[p.x,p.z,-p.y]
   samples.append({'fraction':t,'points':points})
  refs[label.lower()][clip]=samples
 rig.animation_data.action=None
 for tr in rig.animation_data.nla_tracks:tr.mute=False
 activate(mesh);rig.select_set(True);s.frame_set(1)
 path=OUT+'/'+label.lower()+'-animations-v1.glb'
 # These are the exports created in this session; replace them with corrected zero-based timing.
 bpy.ops.export_scene.gltf(filepath=path,export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_bake_animation=True,export_anim_slide_to_zero=True,export_frame_step=1,export_optimize_animation_size=False,export_skins=True,export_influence_nb=4,export_all_influences=False,export_def_bones=False,export_leaf_bone=False,export_yup=True,export_materials='EXPORT',export_rest_position_armature=True)
 for tr in rig.animation_data.nla_tracks:tr.mute=True
 rig.animation_data.action=bpy.data.actions[label+'_Idle_v3'];s.frame_set(1)
json.dump(refs,open(BASE+'/pose-reference.json','w'),indent=2)
result={'export_timing':'All clips start at zero; duplicate loop endpoint retained at exact duration','reference':BASE+'/pose-reference.json'}
