import bpy, math, json, os
from mathutils import Vector, Quaternion
OLD='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v1'
BASE='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v2'
src=open(OLD+'/animlib.py').read()
src=src.replace("'SwordSlash':(22,False,'Sword')", "'SwordSlash':(36,False,'Sword')")
src=src.replace("lean=7 if run else 2 if move else 0", "lean=10 if run else 3 if move else 0")
src=src.replace("-.075+.014*math.cos(4*math.pi*t)","-.067+.017*math.cos(4*math.pi*t)")
src=src.replace(".11 if run else .065", ".095 if run else .065")
src=src.replace("-.050+.008*math.cos(4*math.pi*t)","-.054+.014*math.cos(4*math.pi*t)")
src=src.replace("(.28,-1),(.48,1),(.62,1),(1,0)","(.34,-1),(.50,1),(.60,1),(.94,0),(1,0)")
src=src.replace("lean+=4*max(0,thrust)-9*hit", """step=shape_curve(t,[(0,0),(.10,0),(.32,1),(.66,1),(.94,0),(1,0)]) if clip=='SwordSlash' else 0
 shift=shape_curve(t,[(0,0),(.12,-.02),(.38,.10),(.52,.14),(.66,.14),(.96,0),(1,0)]) if clip=='SwordSlash' else 0
 lean+=4*max(0,thrust)-9*hit+7*max(0,cut)
 twist=(5 if run else 4)*math.cos(2*math.pi*t) if move else 0""")
src=src.replace("if move else 0,0),shift=", "if move else 0,twist),shift=")
src=src.replace(".008*math.sin(2*math.pi*t)",".018*math.sin(2*math.pi*t)")
src=src.replace("-.09*max(thrust,0),bob-.05*hit", "-.09*max(thrust,0)-shift,bob-.05*hit-.022*step")
src=src.replace("lean*.5,0,5*cut", "lean*.5,0,5*cut-twist")
src=src.replace("9*cut+8*hit", "12*cut+8*hit-twist")
src=src.replace("p.rotate('neck',(-lean*.15,0,-3*cut))", "p.rotate('neck',(-lean*.15,0,-3*cut+twist*.35))")
src=src.replace("contacts[side]=contact\n  end=p.ik", """if clip=='SwordSlash' and side=='L':
    ankle.y-=.24*step
    if .10<t<.32:ankle.z+=.065*math.sin(math.pi*(t-.10)/.22)**2;contact=False
    elif .66<t<.94:ankle.z+=.05*math.sin(math.pi*(t-.66)/.28)**2;contact=False
   contacts[side]=contact
  end=p.ik""")
src=src.replace("1.15+.16*max(-cut,0)-.08*max(cut,0)","1.15+.16*max(-cut,0)-.08*max(cut,0)")
src=src.replace("-.26-.08*max(cut,0)","-.26-.08*max(cut,0)-shift*.6")
src=src.replace("p.relaxed_arm('L',-.06,0)","p.relaxed_arm('L',-.06-shift*.5,.06*math.sin(math.pi*t) if clip=='SwordSlash' else 0)")
src=src.replace("p.grips('')", """p.grips('')
  if move:
   for side in ['L','R']:
    sign=1 if side=='L' else -1
    for bone,deg in [('fingers_base.',22 if run else 12),('fingers_tip.',28 if run else 15)]:
     rig.pose.bones[bone+side].rotation_quaternion=Quaternion((0,0,1),math.radians(sign*deg))""")
src=src.replace("p.relaxed_arm(side,(.11 if run else .075)*math.sin(2*math.pi*phase) if move else -.04*hit,.003*breath+.10*hit)","locomotion_arm(p,side,phase,run) if move else p.relaxed_arm(side,-.04*hit,.003*breath+.10*hit)")
exec(compile(src,'refined_animlib','exec'))
BASE='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v2'
def locomotion_arm(p,side,phase,run):
 sign=1 if side=='L' else -1
 # Shoulder swings opposite the same-side leg; elbow trails and folds forward.
 angle=math.radians(-(37 if run else 25)*math.cos(2*math.pi*phase))
 flex=math.radians((72 if run else 23)+(13 if run else 10)*math.sin(2*math.pi*phase-.35))
 shoulder=p.base('upper_arm.'+side).translation
 upper=Vector((sign*.27,-math.sin(angle),-math.cos(angle))).normalized()
 lower=Vector((sign*.09,-math.sin(angle+flex),-math.cos(angle+flex))).normalized()
 elbow=shoulder+upper*p.rig.data.bones['upper_arm.'+side].length
 wrist=elbow+lower*p.rig.data.bones['forearm.'+side].length
 p.direction('upper_arm.'+side,shoulder,elbow)
 p.direction('forearm.'+side,elbow,wrist)
 p.direction('hand.'+side,wrist,wrist+lower*.14)

audit={}
for label in ['Brother','Sister']:
 s=bpy.data.scenes[label+'_Animation_v1'];bpy.context.window.scene=s
 rig=bpy.data.objects[label+'_AnimRig_v1'];audit[label]={}
 for clip in ['Walk','Run','SwordSlash']:
  length,loop,weapon=SPECS[clip];name=label+'_'+clip+'_v6';assert not bpy.data.actions.get(name)
  a=bpy.data.actions.new(name);a.use_fake_user=True;rig.animation_data.action=a
  a['loop']=loop;a['duration_seconds']=length/24;a['export_clip']=clip
  samples=[]
  for frame in range(1,length+2):
   s.frame_set(frame);samples.append(pose_frame(rig,label,clip,(frame-1)/length))
   for b in rig.pose.bones:
    b.keyframe_insert('rotation_quaternion',frame=frame,group=b.name)
    b.keyframe_insert('location',frame=frame,group=b.name)
  for layer in a.layers:
   for st in layer.strips:
    for bag in st.channelbags:
     for fc in bag.fcurves:
      for k in fc.keyframe_points:k.interpolation='LINEAR'
  track=rig.animation_data.nla_tracks[clip];strip=track.strips[0]
  strip.action=a;strip.action_frame_start=1;strip.action_frame_end=length+1;strip.frame_end=length+1
  audit[label][clip]={'max_ik_error_m':max(v['ik_error'] for v in samples),'duration':length/24}
  review=bpy.data.scenes['ANIM_REVIEW_'+clip]
  review.objects['REVIEW_'+clip+'_'+label+'_Rig'].animation_data.action=a
  review.frame_end=length;review.frame_set(1)
 rig.animation_data.action=bpy.data.actions[label+'_Idle_v3'];s.frame_set(1)
json.dump(audit,open(BASE+'/authoring-audit.json','w'),indent=2)
bpy.context.window.scene=bpy.data.scenes['ANIM_REVIEW_Walk']
result=audit
