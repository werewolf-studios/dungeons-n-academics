exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v1/animlib.py').read(),'animlib','exec'))
import numpy as np
OUT='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Animated/v1';os.makedirs(OUT,exist_ok=True)
report={}
for label in ['Brother','Sister']:
 s=bpy.data.scenes[label+'_Animation_v1'];bpy.context.window.scene=s;rig=bpy.data.objects[label+'_AnimRig_v1'];mesh=bpy.data.objects[label+'_AnimMesh_v1'];clips={}
 for clip,(length,loop,weapon) in SPECS.items():
  rig.animation_data.action=bpy.data.actions[label+'_'+clip+'_v3'];pose_states=[];foot_errors=[];grip_errors=[];nonfinite=0;minz=100
  for frame in range(1,length+2):
   s.frame_set(frame);bpy.context.view_layer.update();state=np.array([list(b.matrix_basis) for b in rig.pose.bones]);pose_states.append(state)
   nonfinite+=int(not np.isfinite(state).all())
   for side in ['L','R']:
    if clip in ['Walk','Run']:
     phase=(frame-1)/length+(.5 if side=='R' else 0);dy,dz,contact=footpath(phase,.50 if clip=='Run' else .46,.38 if clip=='Run' else .60,.11 if clip=='Run' else .065)
     goal=rig.data.bones['foot.'+side].head_local+Vector((0,dy,dz));actual=rig.pose.bones['foot.'+side].head
     foot_errors.append((actual-goal).length)
   if weapon=='Spear':
    R=rig.pose.bones['hand.R'].matrix;L=rig.pose.bones['hand.L'].matrix;g=R@Vector((.025,.085,0));other=L@Vector((-.025,.085,0));axis=R.to_3x3()@Vector((0,0,1));grip_errors.append((other-(g+axis*.28)).length)
   ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();minz=min(minz,min(v.co.z for v in me.vertices));ev.to_mesh_clear()
  delta=float(np.max(np.abs(pose_states[0]-pose_states[-1])))
  clips[clip]={'duration':length/24,'frames_including_endpoint':length+1,'loop':loop,'weapon':weapon,'loop_matrix_error':delta if loop else None,'start_end_matrix_error':delta,'max_foot_target_error_m':max(foot_errors,default=0),'max_spear_contact_error_m':max(grip_errors,default=0),'nonfinite_states':nonfinite,'min_mesh_z':minz}
 # Verify weights after finger additions, preserving the exact original UV corner data.
 counts=[];bad=0;empty=0
 for v in mesh.data.vertices:
  w=[g.weight for g in v.groups if g.weight>1e-6];counts.append(len(w));bad+=abs(sum(w)-1)>1e-5;empty+=not bool(w)
 uv=hashlib.sha256(b''.join(struct.pack('2f',*d.uv) for d in mesh.data.uv_layers.active.data)).hexdigest();mesh.data.calc_loop_triangles()
 report[label]={'clips':clips,'weights':{'unweighted':empty,'non_normalized':bad,'max_influences':max(counts)},'triangles':len(mesh.data.loop_triangles),'uv_preserved':uv==json.load(open(BASE+'/source-manifest.json'))[label]['signature']['uv'],'bones':len(rig.data.bones)}
 # Keep only the approved clip actions on this animation copy's export tracks.
 rig.animation_data.action=None
 assert len(rig.animation_data.nla_tracks)==0
 for clip,(length,loop,weapon) in SPECS.items():
  tr=rig.animation_data.nla_tracks.new();tr.name=clip;st=tr.strips.new(clip,1,bpy.data.actions[label+'_'+clip+'_v3']);st.action_frame_start=1;st.action_frame_end=length+1;st.blend_type='REPLACE';st.extrapolation='NOTHING'
 activate(mesh);rig.select_set(True);s.frame_set(1)
 path=OUT+'/'+label.lower()+'-animations-v1.glb';assert not os.path.exists(path)
 bpy.ops.export_scene.gltf(filepath=path,export_format='GLB',use_selection=True,use_active_scene=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_bake_animation=True,export_frame_step=1,export_optimize_animation_size=False,export_skins=True,export_influence_nb=4,export_all_influences=False,export_def_bones=False,export_leaf_bone=False,export_yup=True,export_materials='EXPORT',export_rest_position_armature=True)
 raw=open(path,'rb').read();ln=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+ln]);names=[a.get('name') for a in doc.get('animations',[])]
 report[label]['export']={'file':path,'animation_names':names,'joints':len(doc['skins'][0]['joints']),'embedded_images':len(doc.get('images',[])),'helper_translation_channels':{a['name']:[doc['nodes'][c['target']['node']].get('name') for c in a['channels'] if c['target']['path']=='translation' and doc['nodes'][c['target']['node']].get('name','').startswith('tunic.')] for a in doc.get('animations',[])}}
 assert set(names)==set(SPECS),'Missing clip export'
 for tr in rig.animation_data.nla_tracks:tr.mute=True
 rig.animation_data.action=bpy.data.actions[label+'_Idle_v3'];s.frame_start=1;s.frame_end=72;s.frame_set(1)
json.dump(report,open(BASE+'/animation-validation-v1.json','w'),indent=2)
json.dump({'fps':24,'clips':{k:{'duration':v[0]/24,'loop':v[1],'weapon':v[2],'event_frame':11 if k=='SwordSlash' else 12 if k=='SpearThrust' else 4 if k=='TakeDamage' else None} for k,v in SPECS.items()},'walk_reference_speed_mps':.46/(.60*(28/24)),'run_reference_speed_mps':.50/(.38*(18/24)),'socket':{'bone':'hand.R','position':[.025,.085,0],'weapon_rotation_degrees':[90,0,0]},'spear_front_grip_distance_m':.28},open(OUT+'/animation-manifest.json','w'),indent=2)
path=BASE+'/siblings-animation-v004-exported.blend';assert not os.path.exists(path);bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
result=report
