exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v1/animlib.py').read(),'animlib','exec'))
def build(label):
 s=bpy.data.scenes[label+'_Animation_v1'];bpy.context.window.scene=s;rig=bpy.data.objects[label+'_AnimRig_v1'];evidence={}
 for clip,(length,loop,weapon) in SPECS.items():
  assert not bpy.data.actions.get(label+'_'+clip+'_v1')
  act=bpy.data.actions.new(label+'_'+clip+'_v1');rig.animation_data.action=act;act.use_fake_user=True;act['loop']=loop;act['weapon']=weapon or 'None';act['duration_seconds']=length/24;act['export_clip']=clip
  samples=[]
  for frame in range(1,length+2):
   s.frame_set(frame);stats=pose_frame(rig,label,clip,(frame-1)/length);samples.append(stats)
   for b in rig.pose.bones:
    b.keyframe_insert('rotation_quaternion',frame=frame,group=b.name);b.keyframe_insert('location',frame=frame,group=b.name)
  # Use linear interpolation between per-frame samples to avoid overshoot.
  for layer in act.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      for k in fc.keyframe_points:k.interpolation='LINEAR'
  evidence[clip]={'frames':length+1,'loop':loop,'max_ik_target_error_m':max(x['ik_error'] for x in samples),'max_spear_hand_error_m':max(x['spear_grip_error'] for x in samples)}
 rig.animation_data.action=bpy.data.actions[label+'_Idle_v1'];s.frame_start=1;s.frame_end=72;s.frame_set(1)
 json.dump(evidence,open(BASE+'/'+label.lower()+'-authoring-audit.json','w'),indent=2)
 return evidence
result={'Brother':build('Brother')}
for clip,frame in [('Idle',1),('Walk',8),('Run',5),('SwordSlash',11),('SpearThrust',12)]:render('Brother',clip,frame,BASE+'/brother-'+clip.lower()+'-block.png')
path=BASE+'/siblings-animation-v002-brother-blocking.blend';assert not os.path.exists(path);bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
