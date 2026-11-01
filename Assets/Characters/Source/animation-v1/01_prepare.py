import bpy, os, json, hashlib,struct
from mathutils import Matrix,Vector
BASE='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v1'
os.makedirs(BASE,exist_ok=True)
assert not bpy.data.scenes.get('Brother_Animation_v1')
backup=BASE+'/siblings-animation-v001-live-checkpoint.blend'
assert not os.path.exists(backup)
bpy.ops.wm.save_as_mainfile(filepath=backup,compress=True)
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
def sig(ob):
 return {'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons),'uv':hashlib.sha256(b''.join(struct.pack('2f',*d.uv) for d in ob.data.uv_layers.active.data)).hexdigest()}
manifest={}
for label in ['Brother','Sister']:
 old=bpy.data.scenes[label+'_Rig_Validation_v1'];s=bpy.data.scenes.new(label+'_Animation_v1');s.unit_settings.system='METRIC';s.render.fps=24
 col=bpy.data.collections.new(label+'_Animation_Working_v1');s.collection.children.link(col)
 src=bpy.data.objects[label+'_Humanoid_v1'];rig=src.copy();rig.data=src.data.copy();rig.name=label+'_AnimRig_v1';col.objects.link(rig);rig.animation_data.action=None
 for fc in rig.animation_data.drivers:
  for v in fc.driver.variables:
   for t in v.targets:
    if t.id==src:t.id=rig
 meshsrc=bpy.data.objects[label+'_RigMesh_v1'];mesh=meshsrc.copy();mesh.data=meshsrc.data.copy();mesh.name=label+'_AnimMesh_v1';col.objects.link(mesh);mesh.parent=rig
 for m in mesh.modifiers:
  if m.type=='ARMATURE':m.object=rig
 for b in rig.pose.bones:b.rotation_mode='QUATERNION';b.rotation_quaternion=(1,0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
 for o in old.objects:
  if o.type in ['CAMERA','LIGHT']:
   cp=o.copy();cp.data=o.data.copy();cp.name=label+'_Anim_'+o.type;col.objects.link(cp)
   if cp.type=='CAMERA':s.camera=cp
 s.world=old.world;s.render.engine='CYCLES';s.cycles.samples=16;s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
 s.camera.location=(3,-5,2.1);s.camera.rotation_euler=(Vector((0,-.1,.9))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=2.3
 manifest[label]={'source':meshsrc.name,'signature':sig(meshsrc),'rig':rig.name,'mesh':mesh.name}
 bpy.context.window.scene=s
 bpy.context.view_layer.objects.active=rig;rig.select_set(True)
 # Appended weapon source objects keep their original prepared local axes and packed images.
 weapons={}
 for weapon in ['sword','spear']:
  path='D:/GodotProjects/dungeons-n-academics/Assets/Weapons/Source/starter-'+weapon+'-v1.blend'
  with bpy.data.libraries.load(path,link=False) as (a,b):
   b.objects=[n for n in a.objects if not any(t in n.lower() for t in ['camera','light','floor','ground','plane'])]
  imported=[]
  for o in b.objects:
   if o and o.type=='MESH':
    col.objects.link(o);o.name=label+'_Anim_'+weapon.capitalize();o.hide_render=True;o.hide_viewport=False;o.hide_set(True);imported.append(o.name)
  weapons[weapon]=imported
 manifest[label]['weapons']=weapons
json.dump(manifest,open(BASE+'/source-manifest.json','w'),indent=2)
bpy.context.window.scene=bpy.data.scenes['Brother_Animation_v1']
result={'backup':backup,'manifest':manifest,'weapons':[{ 'name':o.name,'bounds':[list(v) for v in o.bound_box],'matrix':[list(r) for r in o.matrix_world]} for o in bpy.context.scene.objects if 'Anim_Sword' in o.name or 'Anim_Spear' in o.name]}
