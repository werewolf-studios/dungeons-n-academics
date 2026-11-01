exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v1/animlib.py').read(),'animlib','exec'))
os.makedirs(BASE+'/review',exist_ok=True)
assert not bpy.data.scenes.get('ANIM_REVIEW_Walk')
for clip,(length,loop,weapon) in SPECS.items():
 if bpy.data.scenes.get('ANIM_REVIEW_'+clip):continue
 s=bpy.data.scenes.new('ANIM_REVIEW_'+clip);s.render.engine='BLENDER_EEVEE';s.render.fps=24;s.frame_start=1;s.frame_end=length;s.view_settings.view_transform='AgX'
 s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100
 if hasattr(s,'eevee') and hasattr(s.eevee,'taa_render_samples'):s.eevee.taa_render_samples=8
 s.world=bpy.data.scenes['Brother_Animation_v1'].world
 col=bpy.data.collections.new('REVIEW_'+clip);s.collection.children.link(col)
 for label,offset in [('Brother',-.68),('Sister',.68)]:
  source=bpy.data.objects[label+'_AnimRig_v1'];rig=source.copy();rig.name='REVIEW_'+clip+'_'+label+'_Rig';col.objects.link(rig);rig.location.x=offset;rig.animation_data.action=bpy.data.actions[label+'_'+clip+'_v3']
  for fc in rig.animation_data.drivers:
   for v in fc.driver.variables:
    for t in v.targets:
     if t.id==source:t.id=rig
  src=bpy.data.objects[label+'_AnimMesh_v1'];mesh=src.copy();mesh.name='REVIEW_'+clip+'_'+label+'_Mesh';mesh.parent=rig;col.objects.link(mesh)
  for m in mesh.modifiers:
   if m.type=='ARMATURE':m.object=rig
  for w in ['Sword','Spear']:
   if weapon==w:
    ob=bpy.data.objects[label+'_Anim_'+w].copy();ob.name='REVIEW_'+clip+'_'+label+'_'+w;col.objects.link(ob);ob.parent=rig;ob.hide_render=False;ob.hide_viewport=False
  td=bpy.data.curves.new('ReviewLabel','FONT');td.body=label;td.align_x='CENTER';td.size=.10;txt=bpy.data.objects('unused') if False else bpy.data.objects.new('Label_'+label,td);col.objects.link(txt);txt.location=(offset,0,2.02);txt.rotation_euler=(math.pi/2,0,0)
 # Floor supplies a visual ground reference; not exported with characters.
 floor=bpy.data.meshes.new('ReviewFloor');floor.from_pydata([(-10,-10,-.002),(10,-10,-.002),(10,10,-.002),(-10,10,-.002)],[],[(0,1,2,3)]);ob=bpy.data.objects.new('ReviewFloor',floor);col.objects.link(ob)
 material=bpy.data.materials.new('ReviewFloorMaterial');material.diffuse_color=(.14,.16,.20,1);material.use_nodes=True;material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.14,.16,.20,1);material.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.85;floor.materials.append(material)
 for ob in bpy.data.scenes['Brother_Animation_v1'].objects:
  if ob.type in ['CAMERA','LIGHT']:
   cp=ob.copy();cp.data=ob.data.copy();cp.name='Review_'+clip+'_'+ob.type;col.objects.link(cp)
   if cp.type=='CAMERA':s.camera=cp
 target=Vector((0,-.2 if weapon=='Spear' else 0,1.0));s.camera.location=(3.5,-5,2.0) if weapon=='Spear' else (1.5,-6,2.0);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=3.8
 titledata=bpy.data.curves.new('ClipTitle','FONT');titledata.body=clip;titledata.align_x='CENTER';titledata.size=.12;title=bpy.data.objects.new('Title_'+clip,titledata);col.objects.link(title);title.location=(0,0,2.22);title.rotation_euler=(math.pi/2,0,0)
 s['purpose']='Side-by-side animation review; edit the Brother/Sister Animation working scenes.'
 s.frame_set(1)
 # FFmpeg is built into Blender; no external encoder install or downloads.
for clip in SPECS:
 s=bpy.data.scenes['ANIM_REVIEW_'+clip]
 s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.ffmpeg_preset='REALTIME';s.render.filepath=BASE+'/review/'+clip+'.mp4'
job={'done':[],'remaining':list(SPECS),'state':'queued'}
def status():json.dump(job,open(BASE+'/review/render-status.json','w'),indent=2)
status()
def next_clip():
 try:
  if not job['remaining']:
   job['state']='complete';status();return None
  clip=job['remaining'].pop(0);job['state']='rendering '+clip;status();s=bpy.data.scenes['ANIM_REVIEW_'+clip];bpy.context.window.scene=s
  bpy.ops.render.render(animation=True,scene=s.name);job['done'].append(clip);status();return .2
 except Exception as e:
  job['state']='error';job['error']=str(e);status();return None
bpy.app.timers.register(next_clip,first_interval=1)
result={'queued':list(SPECS),'status_file':BASE+'/review/render-status.json'}
