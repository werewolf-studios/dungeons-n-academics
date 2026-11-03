"""Prepare the user-created Tripo Workspace v3 bow in an isolated Blender process."""
import bpy
import bmesh
import json
import math
import numpy as np
from pathlib import Path
from mathutils import Matrix, Vector

ROOT=Path(r'D:\GodotProjects\dungeons-n-academics')
SOURCE=ROOT/'Assets/Weapons/Source'
RUNTIME=ROOT/'Assets/Weapons/Runtime'
REPORT={}

def marker(root,name,co):
    obj=bpy.data.objects.new(name,None)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent=root;obj.location=co;obj.empty_display_size=.025
    return obj

def audit_mesh(obj):
    mesh=obj.data;mesh.calc_loop_triangles()
    bm=bmesh.new();bm.from_mesh(mesh)
    result={'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),
        'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'uv_layers':len(mesh.uv_layers)}
    bm.free();return result

def finish(root,name,center,height,report):
    out=RUNTIME/(name+'.glb');blend=SOURCE/(name+'.blend');preview=SOURCE/(name+'-prepared.png')
    for path in [out,blend,preview]:
        if path.exists():raise RuntimeError('Versioned output exists: '+str(path))
    for obj in bpy.context.selected_objects:obj.select_set(False)
    root.select_set(True)
    for obj in root.children_recursive:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,
        export_extras=True,export_animations=False,export_yup=True)
    scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x=640;scene.render.resolution_y=960;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.world=bpy.data.worlds.new(name+'_World');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.18,.18,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
    camera_data=bpy.data.cameras.new(name+'_Camera');camera=bpy.data.objects.new(camera_data.name,camera_data)
    scene.collection.objects.link(camera);camera.location=center+Vector((2,-.65,.15))
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    if name=='starter-arrow-v1':
        camera.location=center+Vector((.2,-.3,2))
        back=(camera.location-center).normalized()
        right=Vector((0,1,0)).cross(back).normalized()
        up=back.cross(right).normalized()
        camera.rotation_euler=Matrix((right,up,back)).transposed().to_euler()
    camera_data.type='ORTHO';camera_data.ortho_scale=height*1.3;scene.camera=camera
    for label,location,energy in [('Key',(-1,-1,2),130),('Fill',(1,-.5,1),75),('Rim',(0,1,1.6),100)]:
        data=bpy.data.lights.new(label,'AREA');data.energy=energy;data.shape='DISK';data.size=1.5
        obj=bpy.data.objects.new(label,data);scene.collection.objects.link(obj);obj.location=center+Vector(location)
        obj.rotation_euler=(center-obj.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(preview)
    bpy.ops.render.render(write_still=True)
    for suffix,offset in [('back',(-2,-.65,.15)),('end-on',(0,-2,.15))]:
        camera.location=center+Vector(offset)
        camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(SOURCE/(name+'-'+suffix+'.png'))
        bpy.ops.render.render(write_still=True)
    camera.location=center+Vector((2,-.65,.15))
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(preview)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
    report.update({'runtime_file':str(out),'source_file':str(blend),'preview':str(preview)})
    (SOURCE/(name+'-audit.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    REPORT[name]=report

# Bow: retain the generated mesh and UVs; establish a consistent attachment frame.
bpy.ops.wm.read_factory_settings(use_empty=True)
bow_source=ROOT/'Assets/Weapons/Generated/tripo-out/starter-bow-v3/starter_bow_v3.glb'
bpy.ops.import_scene.gltf(filepath=str(bow_source),import_pack_images=True)
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
if len(objects)!=1:raise RuntimeError('Expected one bow frame mesh')
bow=objects[0];mesh=bow.data;world=bow.matrix_world.copy()
original_uvs=[tuple(d.uv) for d in mesh.uv_layers.active.data]
normals=[n.vector.copy() for n in mesh.corner_normals]
positions=np.array([tuple(world@v.co) for v in mesh.vertices])
image=next(n.image for n in mesh.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image and 'basecolor' in n.image.name.lower())
w,h=image.size;pixels=np.empty(w*h*4,dtype=np.float32);image.pixels.foreach_get(pixels);pixels=pixels.reshape((h,w,4))
colors=[[] for _ in mesh.vertices]
for loop in mesh.loops:
    uv=mesh.uv_layers.active.data[loop.index].uv
    colors[loop.vertex_index].append(pixels[min(h-1,max(0,int(uv.y*h))),min(w-1,max(0,int(uv.x*w))),:3])
average=np.array([np.mean(c,axis=0) if c else np.zeros(3) for c in colors])
purple=(average[:,2]>average[:,1]*1.35)&(average[:,2]>average[:,0]*1.05)
if purple.sum()<8:raise RuntimeError('Cannot identify bow grip')
values,vectors=np.linalg.eigh(np.cov(positions.T))
vertical=vectors[:,np.argmax(values)]
if vertical[2]<0:vertical=-vertical
projection=positions@vertical
end_points=positions[(projection>projection.max()-.035)|(projection<projection.min()+.035)]
back=end_points.mean(axis=0)-positions[purple].mean(axis=0)
back=back-np.dot(back,vertical)*vertical
if np.linalg.norm(back)<.02:raise RuntimeError('Cannot confidently establish bow draw direction')
depth=-back/np.linalg.norm(back)
thickness=np.cross(depth,vertical)
rotation=Matrix((tuple(thickness),tuple(depth),tuple(vertical)))
coords=positions@np.array(rotation).T
grip=(coords[purple].min(axis=0)+coords[purple].max(axis=0))/2
coords=(coords-grip)*(1.2/(coords[:,2].max()-coords[:,2].min()))
for v,co in zip(mesh.vertices,coords):v.co=co
bow.parent=None;bow.matrix_world=Matrix.Identity(4);bow.name='BowFrame';mesh.name='StarterBowFrame_v3'
normal_matrix=rotation@world.to_3x3().inverted().transposed()
mesh.normals_split_custom_set([tuple((normal_matrix@n).normalized()) for n in normals]);mesh.update()
if original_uvs!=[tuple(d.uv) for d in mesh.uv_layers.active.data]:raise RuntimeError('Bow UVs changed')
mesh.calc_loop_triangles();raw_triangle_count=len(mesh.loop_triangles)
locally_reduced=False  # Preserve the user-approved Workspace mesh without decimation.
root=bpy.data.objects.new('StarterBow',None);bpy.context.scene.collection.objects.link(root);bow.parent=root
root['source_task']='user-created-in-tripo-workspace';root['height_m']=1.2;root['asset_version']='v3'
top=Vector(coords[coords[:,2]>coords[:,2].max()-.016].mean(axis=0))
bottom=Vector(coords[coords[:,2]<coords[:,2].min()+.016].mean(axis=0))
top.y-=.002;bottom.y-=.002
fraction=(.035-bottom.z)/(top.z-bottom.z);nock=bottom.lerp(top,fraction)
rest=Vector((nock.x,0,nock.z))
for name,co in [('Grip',(0,0,0)),('StringUpper',top),('StringLower',bottom),('StringNock',nock),('ArrowRest',rest)]:marker(root,name,co)

def cord_vertices(points,radius=.0015,sides=6):
    result=[]
    for i,p in enumerate(points):
        tangent=(points[min(2,i+1)]-points[max(0,i-1)]).normalized()
        a=Vector((1,0,0));b=tangent.cross(a).normalized()
        for j in range(sides):result.append(p+radius*(math.cos(j*2*math.pi/sides)*a+math.sin(j*2*math.pi/sides)*b))
    return result
cord_faces=[]
for row in range(2):
    for j in range(6):cord_faces.append((row*6+j,row*6+(j+1)%6,(row+1)*6+(j+1)%6,(row+1)*6+j))
cord_faces.extend([tuple(reversed(range(6))),tuple(range(12,18))])
cord=bpy.data.meshes.new('BowStringMesh_v3');cord.from_pydata(cord_vertices([top,nock,bottom]),[],cord_faces);cord.update()
string=bpy.data.objects.new('BowString',cord);bpy.context.scene.collection.objects.link(string);string.parent=root
mat=bpy.data.materials.new('Bowstring_Flax');mat.diffuse_color=(.35,.27,.17,1);mat.use_nodes=True
mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=mat.diffuse_color
mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.9;cord.materials.append(mat)
string.shape_key_add(name='Basis');draw=string.shape_key_add(name='Draw')
drawn_nock=nock+Vector((0,-.25,0))
for v,co in zip(draw.data,cord_vertices([top,drawn_nock,bottom])):v.co=co
draw.value=0
string['draw_displacement_godot']=[0,0,.25]
frame_audit=audit_mesh(bow);string_audit=audit_mesh(string)
print('BOW_INITIAL_AUDIT',json.dumps({'frame':frame_audit,'string':string_audit}))
if frame_audit['zero_area_faces'] or string_audit['zero_area_faces']:raise RuntimeError('Bow geometry failed checks')
bow_report={'task_id':root['source_task'],'generation_credits':None,'local_preparation_credits':0,
    'frame':frame_audit,'string':string_audit,'total_triangles':frame_audit['triangles']+string_audit['triangles'],
    'height_m':1.2,'generated_uv_map_retained':True,'uvs_exactly_unchanged':not locally_reduced,
    'raw_triangle_count':raw_triangle_count,'local_budget_reduction_applied':locally_reduced,
    'aim_direction_godot':'-Z','height_axis_godot':'+Y',
    'markers_blender':{o.name:list(o.location) for o in root.children if o.type=='EMPTY'},
    'markers_godot':{o.name:[o.location.x,o.location.z,-o.location.y] for o in root.children if o.type=='EMPTY'},
    'input_model':'Assets/Weapons/Generated/tripo-out/starter-bow-v3/starter_bow_v3.glb',
    'string_draw_morph_m':.25,'limb_deformation_included':False}
finish(root,'starter-bow-v3',Vector((0,0,float((coords[:,2].min()+coords[:,2].max())/2))),1.2,bow_report)


print(json.dumps(REPORT))

