import bpy, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'D:\GodotProjects\dungeons-n-academics')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'Assets/Weapons/Generated/tripo-out/starter-bow-v3/starter_bow_v3.glb'),import_pack_images=True)
for obj in bpy.context.scene.objects:
    if obj.type!='MESH': continue
    obj.data.calc_loop_triangles()
    points=[obj.matrix_world@v.co for v in obj.data.vertices]
    print('INSPECT',json.dumps({'name':obj.name,'vertices':len(points),'triangles':len(obj.data.loop_triangles),'bounds':[list(map(min,zip(*points))),list(map(max,zip(*points)))], 'materials':[m.name for m in obj.data.materials], 'textures':[(n.image.name,list(n.image.size)) for m in obj.data.materials for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]}))
scene=bpy.context.scene
points=[o.matrix_world@v.co for o in scene.objects if o.type=='MESH' for v in o.data.vertices]
lo=Vector(tuple(map(min,zip(*points))));hi=Vector(tuple(map(max,zip(*points))));center=(lo+hi)/2
scene.world=bpy.data.worlds.new('World');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=640;scene.render.resolution_y=800;scene.render.resolution_percentage=100
camera=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));scene.collection.objects.link(camera);scene.camera=camera
camera.data.type='ORTHO';camera.data.ortho_scale=max(hi-lo)*1.3
for label,offset in [('Side',(2,0,.2)),('Front',(0,-2,.2))]:
    camera.location=center+Vector(offset);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    light=bpy.data.objects.new(label,bpy.data.lights.new(label,'AREA'));scene.collection.objects.link(light);light.location=camera.location;light.rotation_euler=camera.rotation_euler;light.data.energy=100;light.data.size=3
    scene.render.filepath=str(ROOT/f'Assets/Weapons/Source/starter-bow-v3-inspect-{label.lower()}.png')
    bpy.ops.render.render(write_still=True)
