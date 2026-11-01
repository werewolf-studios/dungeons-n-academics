import bpy
import bmesh
import json
import numpy as np
from pathlib import Path
from mathutils import Matrix, Vector

ROOT = Path(r'D:\GodotProjects\dungeons-n-academics')
SOURCE = ROOT / 'Assets/Weapons/Generated/tripo-out/starter-sword-v1-ec14d3ea/model.glb'
OUT = ROOT / 'Assets/Weapons/Runtime/starter-sword-v1.glb'
BLEND = ROOT / 'Assets/Weapons/Source/starter-sword-v1.blend'
PREVIEW = ROOT / 'Assets/Weapons/Source/starter-sword-v1-prepared.png'
for destination in [OUT, BLEND, PREVIEW]:
    if destination.exists():
        raise RuntimeError('Versioned destination already exists: ' + str(destination))
OUT.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SOURCE), import_pack_images=True)
meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
if len(meshes) != 1:
    raise RuntimeError('Expected one sword mesh')
obj = meshes[0]
mesh = obj.data
original_uvs = [tuple(item.uv) for item in mesh.uv_layers.active.data]
original_normals = [normal.vector.copy() for normal in mesh.corner_normals]
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
    color = pixels[min(h-1,max(0,int(uv.y*h))), min(w-1,max(0,int(uv.x*w))), :3]
    colors[loop.vertex_index].append(color)
averages = np.array([np.mean(items, axis=0) if items else np.zeros(3) for items in colors])
steel_mask = (averages.min(axis=1) > .42) & ((averages.max(axis=1)-averages.min(axis=1)) < .22)
grip_mask = (averages[:,0] > averages[:,1]*1.3) & (averages[:,1] > averages[:,2]*1.15) & (averages[:,0] > .18)
if steel_mask.sum() < 15 or grip_mask.sum() < 10:
    raise RuntimeError('Cannot confidently identify blade and brown grip')
steel = positions[steel_mask]
grip = positions[grip_mask]
eigenvalues, eigenvectors = np.linalg.eigh(np.cov(steel.T))
blade_axis = eigenvectors[:,np.argmax(eigenvalues)]
if np.dot(blade_axis, steel.mean(axis=0)-grip.mean(axis=0)) < 0:
    blade_axis = -blade_axis
width_axis = eigenvectors[:,np.argsort(eigenvalues)[-2]]
depth_axis = np.cross(blade_axis,width_axis)
rotation = Matrix((tuple(width_axis),tuple(depth_axis),tuple(blade_axis)))
oriented = positions @ np.array(rotation).T
grip_oriented = grip @ np.array(rotation).T
pivot = (grip_oriented.min(axis=0)+grip_oriented.max(axis=0))/2
scale = .85 / (oriented[:,2].max()-oriented[:,2].min())
prepared = (oriented-pivot)*scale
for vertex, co in zip(mesh.vertices,prepared):
    vertex.co = co
obj.parent = None
obj.matrix_world = Matrix.Identity(4)
obj.name = 'SwordMesh'
mesh.name = 'StarterSwordMesh_v1'
normal_matrix = rotation @ world.to_3x3().inverted().transposed()
mesh.normals_split_custom_set([tuple((normal_matrix @ normal).normalized()) for normal in original_normals])
mesh.update()
if original_uvs != [tuple(item.uv) for item in mesh.uv_layers.active.data]:
    raise RuntimeError('UVs changed during pivot preparation')
root = bpy.data.objects.new('StarterSword',None)
bpy.context.scene.collection.objects.link(root)
obj.parent = root
root['asset_version'] = 'v1'
root['source_task'] = 'ec14d3ea-a6bd-4fce-b9ea-4426066de0fa'
root['length_m'] = .85
root['attachment_origin'] = 'brown grip center'
markers = []
for name,location in [('Grip',(0,0,0)),('Tip',(0,0,float(prepared[:,2].max())))]:
    marker = bpy.data.objects.new(name,None)
    marker.empty_display_type = 'PLAIN_AXES'
    marker.empty_display_size = .025
    bpy.context.scene.collection.objects.link(marker)
    marker.parent = root
    marker.location = location
    markers.append(marker)
for item in bpy.context.selected_objects:
    item.select_set(False)
for item in [root,obj,*markers]:
    item.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.export_scene.gltf(filepath=str(OUT),export_format='GLB',use_selection=True,
                         export_animations=False,export_extras=True,export_yup=True)
mesh.calc_loop_triangles()
bm = bmesh.new()
bm.from_mesh(mesh)
audit = {'task_id':root['source_task'],'model':'P1-20260311','credits_consumed':40,
    'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'runtime_triangles':len(mesh.loop_triangles),
    'zero_area_faces':sum(face.calc_area()<1e-12 for face in bm.faces),
    'uv_layers':len(mesh.uv_layers),'uvs_unchanged':True,'total_length_m':.85,
    'bounds_min_m':prepared.min(axis=0).tolist(),'bounds_max_m':prepared.max(axis=0).tolist(),
    'blade_axis_blender':'+Z','blade_axis_godot':'+Y','broad_face_godot':'XY plane; normals approximately +/-Z',
    'pivot':'center of brown grip','grip_sample_count':int(grip_mask.sum()),'steel_sample_count':int(steel_mask.sum()),
    'images':[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images],
    'runtime_file':str(OUT),'source_file':str(BLEND)}
bm.free()
if audit['runtime_triangles'] > 1000:
    raise RuntimeError('Triangle budget exceeded')
scene = bpy.context.scene
scene.world = bpy.data.worlds.new('SwordPreviewWorld')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.18,.18,.18,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .6
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 640
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
center = Vector((0,0,float((prepared[:,2].min()+prepared[:,2].max())/2)))
camera_data = bpy.data.cameras.new('SwordPreviewCamera')
camera = bpy.data.objects.new('SwordPreviewCamera',camera_data)
scene.collection.objects.link(camera)
camera.location = center+Vector((.7,-2,.2))
camera.rotation_euler = (center-camera.location).to_track_quat('-Z','Y').to_euler()
camera_data.type = 'ORTHO'
camera_data.ortho_scale = 1.1
scene.camera = camera
for name, location, energy in [('Key',(-1,-1,1.6),120),('Fill',(1,-.5,.7),65),('Rim',(0,1,1.2),100)]:
    light_data = bpy.data.lights.new(name,'AREA')
    light_data.energy = energy
    light_data.shape = 'DISK'
    light_data.size = 1.5
    light = bpy.data.objects.new(name,light_data)
    scene.collection.objects.link(light)
    light.location = location
    light.rotation_euler = (center-light.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath = str(PREVIEW)
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND),compress=True)
(ROOT / 'Assets/Weapons/Source/starter-sword-v1-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps(audit))
