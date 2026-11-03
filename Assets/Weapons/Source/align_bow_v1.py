import bpy
import json
import math
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(r'D:\GodotProjects\dungeons-n-academics')
root=bpy.data.objects['StarterBow']
frame=bpy.data.objects['BowFrame']
string=bpy.data.objects['BowString']
print('STRING_BEFORE',[(key.name,key.value) for key in string.data.shape_keys.key_blocks],string.show_only_shape_key)
nock=bpy.data.objects['StringNock'].location.copy()
angle=-math.pi/2-math.atan2(nock.y,nock.x)
rotation=Matrix.Rotation(angle,3,'Z')
normal_rotation=rotation
normals=[n.vector.copy() for n in frame.data.corner_normals]
frame.data.transform(rotation.to_4x4())
frame.data.normals_split_custom_set([tuple((normal_rotation@n).normalized()) for n in normals])
for obj in root.children:
    if obj.type=='EMPTY':obj.location=rotation@obj.location
top=bpy.data.objects['StringUpper'].location.copy()
bottom=bpy.data.objects['StringLower'].location.copy()
nock=bpy.data.objects['StringNock'].location.copy()
bpy.data.objects['ArrowRest'].location=(nock.x,0,nock.z)

def coordinates(points):
    vertices=[]
    for i,p in enumerate(points):
        tangent=(points[min(2,i+1)]-points[max(0,i-1)]).normalized()
        a=Vector((1,0,0));b=tangent.cross(a).normalized()
        for j in range(6):vertices.append(p+.0015*(math.cos(j*math.pi/3)*a+math.sin(j*math.pi/3)*b))
    return vertices
basis=coordinates([top,nock,bottom]);drawn=coordinates([top,nock+Vector((0,-.25,0)),bottom])
string.data.shape_keys.key_blocks['Draw'].value=0
string.show_only_shape_key=False
string.active_shape_key_index=0
for v,co in zip(string.data.vertices,basis):v.co=co
for v,co in zip(string.data.shape_keys.key_blocks['Basis'].data,basis):v.co=co
for v,co in zip(string.data.shape_keys.key_blocks['Draw'].data,drawn):v.co=co
string.data.update()
for obj in bpy.context.selected_objects:obj.select_set(False)
for obj in [root,*root.children_recursive]:obj.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.gltf(filepath=str(ROOT/'Assets/Weapons/Runtime/starter-bow-v1.glb'),export_format='GLB',use_selection=True,
    export_extras=True,export_animations=False,export_yup=True)
string.data.shape_keys.key_blocks['Draw'].value=0
string.show_only_shape_key=False
string.active_shape_key_index=0
scene=bpy.context.scene;center=Vector((0,0,(top.z+bottom.z)/2))
scene.camera.location=center+Vector((2,-.65,.15))
scene.camera.rotation_euler=(center-scene.camera.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
audit_path=ROOT/'Assets/Weapons/Source/starter-bow-v1-audit.json'
audit=json.loads(audit_path.read_text(encoding='utf-8'))
audit['markers_blender']={o.name:list(o.location) for o in root.children if o.type=='EMPTY'}
audit['markers_godot']={o.name:[o.location.x,o.location.z,-o.location.y] for o in root.children if o.type=='EMPTY'}
audit['string_draw_value_saved']=float(string.data.shape_keys.key_blocks['Draw'].value)
audit['orientation_corrected']=True
audit_path.write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps(audit))
