exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v1/animlib.py').read(),'animlib','exec'))
assert json.load(open(BASE+'/review/render-status.json'))['state']=='complete'
manifest_path='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Animated/v1/animation-manifest.json'
manifest=json.load(open(manifest_path))
for clip,event in [('SwordSlash',12),('SpearThrust',13)]:manifest['clips'][clip]['event_frame']=event;manifest['clips'][clip]['event_time_seconds']=(event-1)/24
manifest['godot_runtime_status']='Pending editor/playback approval due .NET launch popups; see ANIMATION_HANDOFF.md'
json.dump(manifest,open(manifest_path,'w'),indent=2)
movies={}
for clip,(length,loop,weapon) in SPECS.items():
 path=BASE+'/review/'+clip+'.mp4';raw=open(path,'rb').read();idx=raw.find(b'mvhd');assert idx>=0 and b'ftyp' in raw[:40]
 version=raw[idx+4];offset=idx+4+4+(16 if version else 8);scale=struct.unpack_from('>I',raw,offset)[0];duration=struct.unpack_from('>Q' if version else '>I',raw,offset+4)[0]/scale
 assert abs(duration-length/24)<.01
 movies[clip]={'file':path,'bytes':len(raw),'duration':duration}
# Final preview renders show the latest damage polish and uncropped titles.
for clip,frame in [('SpearThrust',13),('SwordSlash',12),('TakeDamage',4),('Run',5)]:
 s=bpy.data.scenes['ANIM_REVIEW_'+clip];bpy.context.window.scene=s;s.frame_set(frame);s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.filepath=BASE+'/review/'+clip+'-review.png';bpy.ops.render.render(write_still=True)
for clip in SPECS:
 s=bpy.data.scenes['ANIM_REVIEW_'+clip];s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.frame_set(1)
for label in ['Brother','Sister']:
 s=bpy.data.scenes[label+'_Animation_v1'];bpy.context.window.scene=s;rig=bpy.data.objects[label+'_AnimRig_v1'];rig.animation_data.action=bpy.data.actions[label+'_Idle_v3'];s.frame_start=1;s.frame_end=72;s.frame_set(1)
 for w in ['Sword','Spear']:
  ob=bpy.data.objects[label+'_Anim_'+w];ob.hide_render=True;ob.hide_set(True)
notes=open(BASE+'/ANIMATION_HANDOFF.md',encoding='utf-8').read();td=bpy.data.texts.new('DNA_ANIMATION_HANDOFF_v1');td.write(notes)
s=bpy.data.scenes['ANIM_REVIEW_SpearThrust'];bpy.context.window.scene=s;s.frame_set(13)
bpy.ops.object.select_all(action='DESELECT')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.overlay.show_overlays=False;area.spaces.active.shading.type='MATERIAL'
path=BASE+'/siblings-animation-v005-reviewed.blend';assert not os.path.exists(path);bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
report={'final_blend':path,'review_scenes':['ANIM_REVIEW_'+c for c in SPECS],'movies':movies,'raw_glb_max_error_m':max(max(s['errors_m'].values()) for char in json.load(open(BASE+'/raw-glb-comparison.json')).values() for clip in char.values() for s in clip['samples']),'godot_status':manifest['godot_runtime_status'],'notes':BASE+'/ANIMATION_HANDOFF.md'}
json.dump(report,open(BASE+'/delivery-manifest.json','w'),indent=2)
result=report
