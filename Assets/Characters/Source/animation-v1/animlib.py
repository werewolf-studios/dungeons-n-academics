import bpy,math,json,os,struct,hashlib
from mathutils import Vector,Matrix,Quaternion
BASE='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v1'
def smooth(a,b,t):
 t=max(0,min(1,(t-a)/(b-a)));return t*t*(3-2*t)
def activate(o):
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
def mat(rot,pos):
 m=rot.to_matrix().to_4x4() if isinstance(rot,Quaternion) else rot.to_4x4();m.translation=pos;return m
def axisrot(xyz):
 q=Quaternion((1,0,0,0))
 for a,v in zip([(1,0,0),(0,1,0),(0,0,1)],xyz):q=Quaternion(a,math.radians(v))@q
 return q
class Pose:
 def __init__(self,rig):
  self.rig=rig;self.m={};self.errors=[]
  for b in rig.pose.bones:b.rotation_mode='QUATERNION';b.rotation_quaternion=(1,0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
 def base(self,name):
  b=self.rig.data.bones[name]
  return self.m[b.parent.name]@b.parent.matrix_local.inverted()@b.matrix_local if b.parent else b.matrix_local.copy()
 def put(self,name,M):
  b=self.rig.data.bones[name];base=self.base(name);self.rig.pose.bones[name].matrix_basis=base.inverted()@M;self.m[name]=M
 def rotate(self,name,degs=(0,0,0),shift=None):
  base=self.base(name);r=base.to_quaternion();q=r.inverted()@axisrot(degs)@r
  M=base@q.to_matrix().to_4x4()
  if shift is not None:M.translation+=Vector(shift)
  self.put(name,M)
 def direction(self,name,head,tail):
  b=self.rig.data.bones[name];r=b.matrix_local.to_quaternion();q=(r@Vector((0,1,0))).rotation_difference((tail-head).normalized())@r
  self.put(name,mat(q,head))
 def ik(self,a,b,target,pole):
  root=self.base(a).translation;v=Vector(target)-root;dist=v.length;la=self.rig.data.bones[a].length;lb=self.rig.data.bones[b].length
  d=min(dist,la+lb-.0001);d=max(d,abs(la-lb)+.0001);u=v.normalized();n=Vector(pole)-root;n-=u*n.dot(u)
  if n.length<1e-5:n=Vector((0,-1,0));n-=u*n.dot(u)
  n.normalize();along=(la*la-lb*lb+d*d)/(2*d);height=math.sqrt(max(0,la*la-along*along));joint=root+u*along+n*height;end=root+u*d
  self.direction(a,root,joint);self.direction(b,joint,end);self.errors.append(max(0,dist-d));return end
 def hand(self,side,grip,axis):
  # Shaft axis is local Z, through the width of the four fingers.
  z=Vector(axis).normalized();y=Vector((0,0,-1));y-=z*y.dot(z)
  if y.length<.05:y=Vector((0,-1,-.2));y-=z*y.dot(z)
  y.normalize();x=y.cross(z).normalized();R=Matrix((x,y,z)).transposed()
  offset=Vector((.025 if side=='R' else -.025,.085,0));wrist=Vector(grip)-R@offset
  sgn=-1 if side=='R' else 1
  end=self.ik('upper_arm.'+side,'forearm.'+side,wrist,(sgn*.60,.08,1.10))
  self.put('hand.'+side,mat(R,end));return end+R@offset
 def relaxed_arm(self,side,swing=0,breath=0):
  sign=1 if side=='L' else -1;w=Vector((sign*.285,-.025+swing,.865+breath))
  end=self.ik('upper_arm.'+side,'forearm.'+side,w,(sign*.35,-.25,1.04))
  self.direction('hand.'+side,end,end+Vector((sign*.012,-.005,-.14)))
 def grips(self,which):
  for side in ['R','L']:
   amount=1 if side in which else 0;sgn=-1 if side=='R' else 1
   for name,deg in [('fingers_base.',sgn*65),('fingers_tip.',sgn*70)]:
    b=self.rig.pose.bones[name+side];b.rotation_quaternion=Quaternion((0,0,1),math.radians(deg*amount))
   self.rig.pose.bones['thumb.'+side].rotation_quaternion=axisrot((20*amount,sgn*25*amount,sgn*15*amount))
 def finish(self):bpy.context.view_layer.update()
SPECS={'Idle':(72,True,None),'Walk':(28,True,None),'Run':(18,True,None),'SwordIdle':(48,True,'Sword'),'SpearIdle':(48,True,'Spear'),'SwordSlash':(22,False,'Sword'),'SpearThrust':(26,False,'Spear'),'TakeDamage':(16,False,None)}
def footpath(p,stride,stance,lift):
 p%=1
 if p<stance:return -stride/2+stride*p/stance,0,True
 t=(p-stance)/(1-stance);v=stride/stance*(1-stance)
 y=(2*t**3-3*t*t+1)*stride/2+(t**3-2*t*t+t)*v+(-2*t**3+3*t*t)*(-stride/2)+(t**3-t*t)*v
 return y,lift*math.sin(math.pi*t)**2,False
def shape_curve(t,keys):
 for (a,va),(b,vb) in zip(keys,keys[1:]):
  if a<=t<=b:
   f=smooth(a,b,t);return va+(vb-va)*f
 return keys[-1][1]
def pose_frame(rig,label,clip,t):
 p=Pose(rig);breath=math.sin(2*math.pi*t);run=clip=='Run';move=clip in ['Walk','Run'];weapon=SPECS[clip][2]
 lean=7 if run else 2 if move else 0;bob=(-.075+.014*math.cos(4*math.pi*t)) if run else (-.050+.008*math.cos(4*math.pi*t)) if move else -.012+.003*breath
 hit=shape_curve(t,[(0,0),(.18,1),(.32,.9),(1,0)]) if clip=='TakeDamage' else 0
 thrust=shape_curve(t,[(0,0),(.22,-.4),(.43,1),(.54,1),(.85,0),(1,0)]) if clip=='SpearThrust' else 0
 cut=shape_curve(t,[(0,0),(.28,-1),(.48,1),(.62,1),(1,0)]) if clip=='SwordSlash' else 0
 lean+=4*max(0,thrust)-9*hit
 p.rotate('root');p.rotate('pelvis',(0,2*math.sin(2*math.pi*t) if move else 0,0),shift=(.008*math.sin(2*math.pi*t) if move else 0,-.09*max(thrust,0),bob-.05*hit))
 p.rotate('spine',(lean*.5,0,5*cut));p.rotate('chest',(lean*.5+1.3*breath*(not move)-10*hit,-8*hit,9*cut+8*hit));p.rotate('neck',(-lean*.15,0,-3*cut));p.rotate('head',(-lean*.15-5*hit,0,-3*cut-5*hit))
 contacts={}
 for side,phase in [('L',t),('R',t+.5)]:
  b=rig.data.bones['foot.'+side];ankle=b.head_local.copy()
  if move:
   dy,dz,contact=footpath(phase,.50 if run else .46,.38 if run else .60,.11 if run else .065);ankle.y+=dy;ankle.z+=dz;contacts[side]=contact
  else:
   contact=True
   if weapon:ankle.y+=-.055 if side=='L' else .045;ankle.x+=.015 if side=='L' else -.015
   contacts[side]=contact
  end=p.ik('thigh.'+side,'shin.'+side,ankle,(ankle.x,-1,.45))
  p.put('foot.'+side,mat(b.matrix_local.to_quaternion(),end));p.rotate('toe.'+side)
 for side in ['L','R']:p.rotate('clavicle.'+side)
 grip_error=0
 if weapon=='Spear':
  axis=Vector((.16,-.985,.04)).normalized();grip=Vector((-.12,-.11-.16*thrust,1.115+.002*breath));front=grip+axis*.28
  actual=p.hand('R',grip,axis);actualL=p.hand('L',front,-axis);grip_error=(actualL-(actual+axis*.28)).length;p.grips('RL')
 elif weapon=='Sword':
  grip=Vector((-.25+.22*max(cut,0)+.03*min(cut,0),-.26-.08*max(cut,0),1.15+.16*max(-cut,0)-.08*max(cut,0)))
  axis=Vector((.2+.75*cut,-.35-.5*min(cut,0),.96-.75*max(cut,0))).normalized()
  actual=p.hand('R',grip,axis);p.relaxed_arm('L',-.06,0);p.grips('R')
 else:
  for side,phase in [('L',t),('R',t+.5)]:
   p.relaxed_arm(side,(.11 if run else .075)*math.sin(2*math.pi*phase) if move else -.04*hit,.003*breath+.10*hit)
  p.grips('')
 p.finish();return {'ik_error':max(p.errors),'spear_grip_error':grip_error,'contacts':contacts}
def render(label,clip,frame,path,view='front'):
 s=bpy.data.scenes[label+'_Animation_v1'];bpy.context.window.scene=s;rig=bpy.data.objects[label+'_AnimRig_v1'];rig.animation_data.action=bpy.data.actions[label+'_'+clip+'_'+rig.get('clip_suffix','v1')];s.frame_set(frame)
 for w in ['Sword','Spear']:
  ob=bpy.data.objects[label+'_Anim_'+w];on=SPECS[clip][2]==w;ob.hide_render=not on;ob.hide_set(not on)
 pos=(3,-5,2) if view=='front' else (3,5,2) if view=='back' else (5,-.6,1.7)
 target=Vector((0,-.3 if clip.startswith('Spear') else 0,.9));s.camera.location=pos;s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=2.5 if clip.startswith('Spear') else 2.25
 s.render.filepath=path;bpy.ops.render.render(write_still=True)
