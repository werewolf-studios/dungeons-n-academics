import bpy, math, json, os
from mathutils import Matrix, Vector
from collections import defaultdict
BASE = 'D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1'
os.makedirs(BASE, exist_ok=True)
assert not bpy.data.scenes.get('Brother_Rig_Validation_v1'), 'Already prepared; inspect instead of rerunning'
ORIGINALS = {}
def signature(mesh):
    import hashlib, struct
    return {'vertices':len(mesh.vertices),'faces':len(mesh.polygons),
        'coords':hashlib.sha256(b''.join(struct.pack('3f',*v.co) for v in mesh.vertices)).hexdigest(),
        'uv':hashlib.sha256(b''.join(struct.pack('2f',*d.uv) for d in mesh.uv_layers.active.data)).hexdigest()}
for n in ['Brother_SmoothTunic_v2','Sister_Clean_v1']:
    ORIGINALS[n] = signature(bpy.data.objects[n].data)
json.dump({'live_file':bpy.data.filepath,'original_signatures':ORIGINALS},open(BASE+'/source-signatures.json','w'),indent=2)

def prepare(label, source_name):
    s=bpy.data.scenes.new(label+'_Rig_Validation_v1')
    s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1
    col=bpy.data.collections.new(label+'_Rig_Working_v1'); s.collection.children.link(col)
    src=bpy.data.objects[source_name]
    ob=src.copy(); ob.data=src.data.copy(); ob.name=label+'_RigMesh_v1'; ob.data.name=label+'_RigMeshData_v1'
    col.objects.link(ob); ob.hide_viewport=False; ob.hide_render=False
    ob.matrix_world=Matrix.Identity(4)
    zmin=min(v.co.z for v in ob.data.vertices); zmax=max(v.co.z for v in ob.data.vertices)
    scale=1.8/(zmax-zmin)
    transform=Matrix(((0,scale,0,0),(-scale,0,0,0),(0,0,scale,-zmin*scale),(0,0,0,1)))
    ob.data.transform(transform); ob.data.update()
    ob['source_object']=source_name; ob['bind_convention']='1.8m height; +Z up; -Y front; feet z=0; origin on floor'
    ob['source_scale_factor']=scale
    s.render.engine='CYCLES'; s.cycles.samples=24
    s.render.resolution_x=900; s.render.resolution_y=1000; s.render.resolution_percentage=100
    s.world=bpy.data.worlds.new(label+'_Rig_World_v1'); s.world.use_nodes=True
    s.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.18,.18,.18,1)
    s.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.5
    s.view_settings.view_transform='AgX'
    camdata=bpy.data.cameras.new(label+'_Rig_Camera_v1'); cam=bpy.data.objects.new(camdata.name,camdata); col.objects.link(cam)
    cam.location=(0,-5,1); cam.rotation_euler=(Vector((0,0,.9))-cam.location).to_track_quat('-Z','Y').to_euler()
    camdata.type='ORTHO'; camdata.ortho_scale=2.12; s.camera=cam
    for name,loc,power,size in [('Key',(-3,-4,5),450,4),('Fill',(3,-2,3),230,3),('Rim',(0,3,4),350,3)]:
        ld=bpy.data.lights.new(label+'_Rig_'+name,'AREA'); ld.energy=power; ld.shape='DISK'; ld.size=size
        lo=bpy.data.objects.new(ld.name,ld); col.objects.link(lo); lo.location=loc
        lo.rotation_euler=(Vector((0,0,.9))-lo.location).to_track_quat('-Z','Y').to_euler()
    return s,ob,col

def shells(ob):
    adj=[[] for v in ob.data.vertices]
    for e in ob.data.edges:
        a,b=e.vertices; adj[a].append(b); adj[b].append(a)
    seen=set(); parts=[]
    for v in ob.data.vertices:
        if v.index in seen: continue
        ids=[]; todo=[v.index]; seen.add(v.index)
        while todo:
            i=todo.pop(); ids.append(i)
            for j in adj[i]:
                if j not in seen: seen.add(j); todo.append(j)
        parts.append(ids)
    return sorted(parts,key=len,reverse=True)

s,ob,col=prepare('Brother','Brother_SmoothTunic_v2')
bpy.context.window.scene=s
parts=shells(ob)
info=[]
for i,ids in enumerate(parts):
    vs=[ob.data.vertices[j].co for j in ids]
    info.append({'id':i,'count':len(ids),'bounds':[[round(min(v[k] for v in vs),4),round(max(v[k] for v in vs),4)] for k in range(3)],'center':[round(sum(v[k] for v in vs)/len(vs),4) for k in range(3)]})
json.dump(info,open(BASE+'/brother-shells.json','w'),indent=2)
s.render.filepath=BASE+'/brother-bind-front.png'
bpy.ops.render.render(write_still=True)
result={'scene':s.name,'object':ob.name,'scale':ob['source_scale_factor'],'shells':info,'image':s.render.filepath}
