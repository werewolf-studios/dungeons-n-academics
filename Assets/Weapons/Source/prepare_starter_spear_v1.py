import bpy
import bmesh
import json
import numpy as np
from pathlib import Path
from mathutils import Matrix, Vector

ROOT = Path(r'D:\GodotProjects\dungeons-n-academics')
SOURCE = ROOT / 'Assets/Weapons/Generated/tripo-out/starter-spear-v1-a4f6bb68/model.glb'
OUT = ROOT / 'Assets/Weapons/Runtime/starter-spear-v1.glb'
BLEND = ROOT / 'Assets/Weapons/Source/starter-spear-v1.blend'
PREVIEW = ROOT / 'Assets/Weapons/Source/starter-spear-v1-prepared.png'
for destination in [OUT, BLEND, PREVIEW]:
    if destination.exists():
        raise RuntimeError('Versioned destination already exists: ' + str(destination))
OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SOURCE), import_pack_images=True)
objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
if len(objects) != 1:
    raise RuntimeError('Expected one spear mesh')
obj = objects[0]
mesh = obj.data
uvs_before = [tuple(item.uv) for item in mesh.uv_layers.active.data]
normals_before = [normal.vector.copy() for normal in mesh.corner_normals]
world = obj.matrix_world.copy()
positions = np.array([tuple(world @ vertex.co) for vertex in mesh.vertices])
image = next(node.image for node in mesh.materials[0].node_tree.nodes
             if node.type == 'TEX_IMAGE' and node.image and node.image.name.startswith('Color_'))
w, h = image.size
pixels = np.empty(w*h*4, dtype=np.float32)
image.pixels.foreach_get(pixels)
pixels = pixels.reshape((h,w,4))
colors = [[] for _ in mesh.vertices]
for loop in mesh.loops:
    uv = mesh.uv_layers.active.data[loop.index].uv
    colors[loop.vertex_index].append(pixels[min(h-1,max(0,int(uv.y*h))),min(w-1,max(0,int(uv.x*w))),:3])
average = np.array([np.mean(items,axis=0) if items else np.zeros(3) for items in colors])
steel_mask = (average.min(axis=1)>.42) & ((average.max(axis=1)-average.min(axis=1))<.22)
wood_mask = (average[:,0]>average[:,1]*1.3) & (average[:,1]>average[:,2]*1.15) & (average[:,0]>.18)
if steel_mask.sum()<10 or wood_mask.sum()<10:
    raise RuntimeError('Cannot confidently identify spearhead and wooden shaft')
values, vectors = np.linalg.eigh(np.cov(positions.T))
axis = vectors[:,np.argmax(values)]
if np.dot(axis,positions[steel_mask].mean(axis=0)-positions[wood_mask].mean(axis=0))<0:
    axis = -axis
# Use the head's width axis, projected perpendicular to the shaft.
head_values, head_vectors = np.linalg.eigh(np.cov(positions[steel_mask].T))
candidates = [head_vectors[:,i]-np.dot(head_vectors[:,i],axis)*axis for i in np.argsort(head_values)[::-1]]
width = max(candidates,key=lambda v:float(np.var(positions[steel_mask] @ v))/float(np.dot(v,v)) if np.linalg.norm(v)>.1 else -1)
width = width/np.linalg.norm(width)
depth = np.cross(axis,width)
rotation = Matrix((tuple(width),tuple(depth),tuple(axis)))
oriented = positions @ np.array(rotation).T
wood_oriented = oriented[wood_mask]
length = float(oriented[:,2].max()-oriented[:,2].min())
pivot = np.array([wood_oriented[:,0].mean(),wood_oriented[:,1].mean(),oriented[:,2].min()+length/3])
prepared = (oriented-pivot)*(1.8/length)
for vertex, co in zip(mesh.vertices,prepared):
    vertex.co = co
obj.parent = None
obj.matrix_world = Matrix.Identity(4)
obj.name = 'SpearMesh'
mesh.name = 'StarterSpearMesh_v1'
normal_matrix = rotation @ world.to_3x3().inverted().transposed()
mesh.normals_split_custom_set([tuple((normal_matrix @ normal).normalized()) for normal in normals_before])
mesh.update()
if uvs_before != [tuple(item.uv) for item in mesh.uv_layers.active.data]:
    raise RuntimeError('UVs changed during spear preparation')
root = bpy.data.objects.new('StarterSpear',None)
bpy.context.scene.collection.objects.link(root)
obj.parent = root
root['asset_version'] = 'v1'
root['source_task'] = 'a4f6bb68-fd9c-46c4-bf1b-bbe931739d84'
root['length_m'] = 1.8
root['attachment_origin'] = 'shaft grip one third of total length above butt'
markers = []
for name,location in [('Grip',(0,0,0)),('Tip',(0,0,float(prepared[:,2].max()))),('Butt',(0,0,float(prepared[:,2].min())))]:
    marker = bpy.data.objects.new(name,None)
    marker.empty_display_type = 'PLAIN_AXES'
    marker.empty_display_size = .03
    bpy.context.scene.collection.objects.link(marker)
    marker.parent = root
    marker.location = location
    markers.append(marker)
for item in bpy.context.selected_objects:
    item.select_set(False)
for item in [root,obj,*markers]:
    item.select_set(True)
bpy.context.view_layer.objects.active = obj
mesh.calc_loop_triangles()
bm = bmesh.new()
bm.from_mesh(mesh)
audit = {'task_id':root['source_task'],'model':'P1-20260311','credits_consumed':40,
    'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'runtime_triangles':len(mesh.loop_triangles),
    'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'uv_layers':len(mesh.uv_layers),'uvs_unchanged':True,
    'total_length_m':1.8,'pivot':'shaft grip 0.6m above butt','tip_m':float(prepared[:,2].max()),'butt_m':float(prepared[:,2].min()),
    'bounds_min_m':prepared.min(axis=0).tolist(),'bounds_max_m':prepared.max(axis=0).tolist(),
    'blade_axis_blender':'+Z','blade_axis_godot':'+Y','head_width_axis_godot':'+X',
    'steel_sample_count':int(steel_mask.sum()),'wood_sample_count':int(wood_mask.sum()),
    'images':[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images],
    'runtime_file':str(OUT),'source_file':str(BLEND)}
bm.free()
if audit['runtime_triangles']>1000 or audit['zero_area_faces']:
    raise RuntimeError('Spear failed geometry checks: '+json.dumps(audit))
bpy.ops.export_scene.gltf(filepath=str(OUT),export_format='GLB',use_selection=True,
                         export_animations=False,export_extras=True,export_yup=True)
scene = bpy.context.scene
scene.world = bpy.data.worlds.new('SpearPreviewWorld')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.18,.18,.18,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .6
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 640
scene.render.resolution_y = 1280
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
center = Vector((0,0,float((prepared[:,2].min()+prepared[:,2].max())/2)))
camera_data = bpy.data.cameras.new('SpearPreviewCamera')
camera = bpy.data.objects.new('SpearPreviewCamera',camera_data)
scene.collection.objects.link(camera)
camera.location = center+Vector((.7,-3,.15))
camera.rotation_euler = (center-camera.location).to_track_quat('-Z','Y').to_euler()
camera_data.type = 'ORTHO'
camera_data.ortho_scale = 2.25
scene.camera = camera
for name,location,energy in [('Key',(-1,-1,2.4),150),('Fill',(1,-.5,1),85),('Rim',(0,1,1.8),140)]:
    data = bpy.data.lights.new(name,'AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = 1.5
    light = bpy.data.objects.new(name,data)
    scene.collection.objects.link(light)
    light.location = location
    light.rotation_euler = (center-light.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath = str(PREVIEW)
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND),compress=True)
(ROOT / 'Assets/Weapons/Source/starter-spear-v1-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps(audit))
