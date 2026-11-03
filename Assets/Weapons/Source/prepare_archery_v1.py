"""Prepare the generated bow and repair the malformed generated arrow locally."""
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
    scene.collection.objects.link(camera);camera.location=center+Vector((.8,-2,.2))
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
    bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
    report.update({'runtime_file':str(out),'source_file':str(blend),'preview':str(preview)})
    (SOURCE/(name+'-audit.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    REPORT[name]=report

# Bow: retain the generated mesh and UVs; establish a consistent attachment frame.
bpy.ops.wm.read_factory_settings(use_empty=True)
bow_source=ROOT/'Assets/Weapons/Generated/tripo-out/starter-bow-v1-288f15aa/model.glb'
bpy.ops.import_scene.gltf(filepath=str(bow_source),import_pack_images=True)
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
if len(objects)!=1:raise RuntimeError('Expected one bow frame mesh')
bow=objects[0];mesh=bow.data;world=bow.matrix_world.copy()
original_uvs=[tuple(d.uv) for d in mesh.uv_layers.active.data]
normals=[n.vector.copy() for n in mesh.corner_normals]
positions=np.array([tuple(world@v.co) for v in mesh.vertices])
image=next(n.image for n in mesh.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.name.startswith('Color_'))
w,h=image.size;pixels=np.empty(w*h*4,dtype=np.float32);image.pixels.foreach_get(pixels);pixels=pixels.reshape((h,w,4))
colors=[[] for _ in mesh.vertices]
for loop in mesh.loops:
    uv=mesh.uv_layers.active.data[loop.index].uv
    colors[loop.vertex_index].append(pixels[min(h-1,max(0,int(uv.y*h))),min(w-1,max(0,int(uv.x*w))),:3])
average=np.array([np.mean(c,axis=0) if c else np.zeros(3) for c in colors])
purple=(average[:,2]>average[:,1]*1.35)&(average[:,2]>average[:,0]*1.05)
if purple.sum()<8:raise RuntimeError('Cannot identify bow grip')
values,vectors=np.linalg.eigh(np.cov(positions.T));vertical=vectors[:,np.argmax(values)]
if vertical[2]<0:vertical=-vertical
thickness=vectors[:,np.argmin(values)];depth=np.cross(vertical,thickness)
rotation=Matrix((tuple(thickness),tuple(depth),tuple(vertical)))
coords=positions@np.array(rotation).T
grip=(coords[purple].min(axis=0)+coords[purple].max(axis=0))/2
ends=coords[(coords[:,2]>coords[:,2].max()-.04)|(coords[:,2]<coords[:,2].min()+.04)].mean(axis=0)
if grip[1]<ends[1]:
    rotation=Matrix.Diagonal(Vector((-1,-1,1)))@rotation
    coords=positions@np.array(rotation).T
    grip=(coords[purple].min(axis=0)+coords[purple].max(axis=0))/2
coords=(coords-grip)*(1.2/(coords[:,2].max()-coords[:,2].min()))
for v,co in zip(mesh.vertices,coords):v.co=co
bow.parent=None;bow.matrix_world=Matrix.Identity(4);bow.name='BowFrame';mesh.name='StarterBowFrame_v1'
normal_matrix=rotation@world.to_3x3().inverted().transposed()
mesh.normals_split_custom_set([tuple((normal_matrix@n).normalized()) for n in normals]);mesh.update()
if original_uvs!=[tuple(d.uv) for d in mesh.uv_layers.active.data]:raise RuntimeError('Bow UVs changed')
mesh.calc_loop_triangles();raw_triangle_count=len(mesh.loop_triangles)
locally_reduced=raw_triangle_count>1000
if locally_reduced:
    bpy.context.view_layer.objects.active=bow;bow.select_set(True)
    modifier=bow.modifiers.new('BudgetReduction','DECIMATE');modifier.ratio=985/raw_triangle_count
    modifier.use_collapse_triangulate=True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    mesh=bow.data
root=bpy.data.objects.new('StarterBow',None);bpy.context.scene.collection.objects.link(root);bow.parent=root
root['source_task']='288f15aa-d82e-4dc8-a95f-34f7c4c790b5';root['height_m']=1.2
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
cord=bpy.data.meshes.new('BowStringMesh_v1');cord.from_pydata(cord_vertices([top,nock,bottom]),[],cord_faces);cord.update()
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
if frame_audit['triangles']>1000 or frame_audit['zero_area_faces'] or string_audit['zero_area_faces']:raise RuntimeError('Bow geometry failed checks')
bow_report={'task_id':root['source_task'],'generation_credits':40,'local_preparation_credits':0,
    'frame':frame_audit,'string':string_audit,'total_triangles':frame_audit['triangles']+string_audit['triangles'],
    'height_m':1.2,'generated_uv_map_retained':True,'uvs_exactly_unchanged':not locally_reduced,
    'raw_triangle_count':raw_triangle_count,'local_budget_reduction_applied':locally_reduced,
    'aim_direction_godot':'-Z','height_axis_godot':'+Y',
    'markers_blender':{o.name:list(o.location) for o in root.children if o.type=='EMPTY'},
    'string_draw_morph_m':.25,'limb_deformation_included':False}
finish(root,'starter-bow-v1',Vector((0,0,float((coords[:,2].min()+coords[:,2].max())/2))),1.2,bow_report)

# Arrow: the paid result put feathers at the head, so construct a corrected small
# final prop locally. Preserve the rejected download as provenance, not a runtime asset.
bpy.ops.wm.read_factory_settings(use_empty=True)
verts=[];faces=[];slots=[];smooth=[]
def add_polyhedron(vs,fs,slot,shading=None):
    offset=len(verts);verts.extend(vs)
    faces.extend(tuple(offset+i for i in f) for f in fs);slots.extend([slot]*len(fs))
    smooth.extend(shading if shading else [False]*len(fs))
def cylinder(radius,start,end,slot,sides=8):
    vs=[(radius*math.cos(j*2*math.pi/sides),y,radius*math.sin(j*2*math.pi/sides)) for y in [start,end] for j in range(sides)]
    fs=[(j,(j+1)%sides,sides+(j+1)%sides,sides+j) for j in range(sides)]
    fs.extend([tuple(reversed(range(sides))),tuple(range(sides,2*sides))])
    add_polyhedron(vs,fs,slot,[True]*sides+[False,False])
def box(lo,hi,slot):
    x,y,z=lo;X,Y,Z=hi
    add_polyhedron([(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],
        [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],slot)
cylinder(.0055,.021,.568,0)
cylinder(.0065,.55,.575,1)
add_polyhedron([(0,.65,0),(-.021,.565,0),(.021,.565,0),(0,.59,.004),(0,.59,-.004)],
    [(0,1,3),(1,2,3),(2,0,3),(1,0,4),(2,1,4),(0,2,4)],1)
for angle in [0,2*math.pi/3,4*math.pi/3]:
    radial=Vector((math.cos(angle),0,math.sin(angle)));tangent=Vector((-math.sin(angle),0,math.cos(angle)))
    profile=[(.006,.034),(.027,.052),(.027,.112),(.006,.13)]
    vs=[tuple(radial*r+Vector((0,y,0))+tangent*side) for side in [-.0007,.0007] for r,y in profile]
    add_polyhedron(vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],2)
cylinder(.0075,.012,.026,3)
box((-.0075,0,-.004),(-.002,.014,.004),3)
box((.002,0,-.004),(.0075,.014,.004),3)
mesh=bpy.data.meshes.new('StarterArrowMesh_v1');mesh.from_pydata(verts,[],faces);mesh.update()
uvs=mesh.uv_layers.new(name='UVMap')
for p,slot,is_smooth in zip(mesh.polygons,slots,smooth):
    p.use_smooth=is_smooth
    for j,li in enumerate(p.loop_indices):
        angle=j*2*math.pi/len(p.loop_indices)
        uvs.data[li].uv=((slot+.5)/4+.085*math.cos(angle),.5+.35*math.sin(angle))
colors=[(.29,.105,.035,1),(.66,.69,.72,1),(.19,.035,.40,1),(.58,.37,.07,1)]
base=bpy.data.images.new('ArrowPalette_BaseColor',width=64,height=64,alpha=True)
orm=bpy.data.images.new('ArrowPalette_ORM',width=64,height=64,alpha=True);orm.colorspace_settings.name='Non-Color'
base_pixels=[];orm_pixels=[]
for y in range(64):
    for x in range(64):
        slot=x//16;base_pixels.extend(colors[slot]);orm_pixels.extend((1,.38 if slot in [1,3] else .7,.75 if slot in [1,3] else 0,1))
base.pixels=base_pixels;orm.pixels=orm_pixels;base.pack();orm.pack()
material=bpy.data.materials.new('ArrowPalette_PBR_v1');material.use_nodes=True
nodes=material.node_tree.nodes;links=material.node_tree.links;shader=nodes.get('Principled BSDF')
color_node=nodes.new('ShaderNodeTexImage');color_node.image=base;links.new(color_node.outputs['Color'],shader.inputs['Base Color'])
orm_node=nodes.new('ShaderNodeTexImage');orm_node.image=orm;split=nodes.new('ShaderNodeSeparateColor')
links.new(orm_node.outputs['Color'],split.inputs['Color']);links.new(split.outputs['Green'],shader.inputs['Roughness']);links.new(split.outputs['Blue'],shader.inputs['Metallic'])
mesh.materials.append(material)
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
obj=bpy.data.objects.new('ArrowMesh',mesh);bpy.context.scene.collection.objects.link(obj)
root=bpy.data.objects.new('StarterArrow',None);bpy.context.scene.collection.objects.link(root);obj.parent=root
root['source_task']='ad1b4ba5-f006-48e0-a29e-6eaf3fc09d7a';root['local_repair']='Rebuilt malformed arrow; corrected tail vanes and notched nock'
for name,co in [('Nock',(0,0,0)),('Tip',(0,.65,0)),('Grip',(0,.3,0))]:marker(root,name,co)
arrow_audit=audit_mesh(obj)
if arrow_audit['triangles']>300 or arrow_audit['zero_area_faces']:raise RuntimeError('Arrow geometry failed checks')
arrow_report={'task_id':root['source_task'],'generation_credits':40,'local_preparation_credits':0,
    'generated_result_issue':'Fletching at head; unsuitable as submitted','local_rebuild':True,
    'mesh':arrow_audit,'length_m':.65,'flight_direction_godot':'-Z','pivot':'notched nock at origin',
    'fletching_count':3,'palette_atlas_size':[64,64],'material_count':1,'markers_godot':{'Nock':[0,0,0],'Tip':[0,0,-.65],'Grip':[0,0,-.3]}}
finish(root,'starter-arrow-v1',Vector((0,.325,0)),.65,arrow_report)
print(json.dumps(REPORT))
