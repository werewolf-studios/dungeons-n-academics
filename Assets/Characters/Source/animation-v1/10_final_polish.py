exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v1/animlib.py').read(),'animlib','exec'))
report=json.load(open(BASE+'/animation-validation-v1.json'))
for label in ['Brother','Sister']:
 s=bpy.data.scenes[label+'_Animation_v1'];bpy.context.window.scene=s;rig=bpy.data.objects[label+'_AnimRig_v1'];rig.animation_data.action=bpy.data.actions[label+'_TakeDamage_v3'];mesh=bpy.data.objects[label+'_AnimMesh_v1'];errors=[];minz=100
 for frame in range(1,18):
  s.frame_set(frame);errors.append(pose_frame(rig,label,'TakeDamage',(frame-1)/16))
  for b in rig.pose.bones:b.keyframe_insert('rotation_quaternion',frame=frame,group=b.name);b.keyframe_insert('location',frame=frame,group=b.name)
  ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();minz=min(minz,min(v.co.z for v in me.vertices));ev.to_mesh_clear()
 report[label]['clips']['TakeDamage']['min_mesh_z']=minz
 report[label]['clips']['TakeDamage']['authoring_ik_target_error_m']=max(e['ik_error'] for e in errors)
 report[label]['clips']['TakeDamage']['polish']='Stronger chest recoil, asymmetric torso twist, head lag, knee absorption, raised hands.'
 rig.animation_data.action=bpy.data.actions[label+'_Idle_v3'];s.frame_set(1)
json.dump(report,open(BASE+'/animation-validation-v2.json','w'),indent=2)
# Correct review framing and increase temporal samples for final movies.
for clip in SPECS:
 s=bpy.data.scenes['ANIM_REVIEW_'+clip];s.camera.data.ortho_scale=4.3
 if hasattr(s,'eevee') and hasattr(s.eevee,'taa_render_samples'):s.eevee.taa_render_samples=32
 for ob in s.objects:
  if ob.name.startswith('ReviewFloor') and ob.type=='MESH':
   for v in ob.data.vertices:v.co.x*=20;v.co.y*=20
 s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG';s.render.filepath=BASE+'/review/'+clip+'.mp4'
exec(compile(open(BASE+'/07_export_timing.py').read(),'07_export_timing','exec'))
exec(compile(open(BASE+'/08_glb_compare.py').read(),'08_glb_compare','exec'))
job={'done':[],'remaining':list(SPECS),'state':'queued','version':'final'}
def status():json.dump(job,open(BASE+'/review/render-status.json','w'),indent=2)
def next_clip():
 try:
  if not job['remaining']:job['state']='complete';status();return None
  clip=job['remaining'].pop(0);job['state']='rendering '+clip;status();s=bpy.data.scenes['ANIM_REVIEW_'+clip];bpy.context.window.scene=s
  bpy.ops.render.render(animation=True,scene=s.name);job['done'].append(clip);status();return .2
 except Exception as e:job['state']='error';job['error']=str(e);status();return None
status();bpy.app.timers.register(next_clip,first_interval=1)
result={'final_movie_pass':'queued','clips':list(SPECS)}
