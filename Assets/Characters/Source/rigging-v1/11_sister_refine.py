exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
import bmesh,numpy as np
s=bpy.data.scenes['Sister_Rig_Validation_v1'];bpy.context.window.scene=s
ob=bpy.data.objects['Sister_RigMesh_v1'];rig=bpy.data.objects['Sister_Humanoid_v1'];reset_pose(rig)
assert not ob.data.attributes.get('dna_tunic_region'), 'Topology split already performed'
parts=shells(ob);lower=set(parts[3]);before=signature(ob.data)
im=next(n.image for n in ob.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.name.endswith('_0'))
pix=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(pix);pix=pix.reshape(im.size[1],im.size[0],4)
def uvcolor(uv):return pix[int(uv[1]*(im.size[1]-1)),int(uv[0]*(im.size[0]-1)),:3]
clothfaces=set()
for p in ob.data.polygons:
    if not all(i in lower for i in p.vertices):continue
    uv=sum((ob.data.uv_layers.active.data[i].uv for i in p.loop_indices),Vector((0,0)))/len(p.loop_indices)
    r,g,b=uvcolor(uv)
    if r>.37 or b>.38 or (r>.30 and r/max(g,.01)>1.65):clothfaces.add(p.index)
# Separate only the fused tunic/leggings interface, retaining every face and UV corner.
bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
orig=bm.verts.layers.int.new('dna_original_vertex');region=bm.verts.layers.int.new('dna_tunic_region');fc=bm.faces.layers.int.new('dna_tunic_face')
for v in bm.verts:v[orig]=v.index
for f in bm.faces:f[fc]=int(f.index in clothfaces)
split=[e for e in bm.edges if len(e.link_faces)==2 and e.link_faces[0][fc]!=e.link_faces[1][fc]]
bmesh.ops.split_edges(bm,edges=split)
for v in bm.verts:v[region]=int(any(f[fc] for f in v.link_faces))
bm.to_mesh(ob.data);bm.free();ob.data.update()
origin=[d.value for d in ob.data.attributes['dna_original_vertex'].data]
tunic=[d.value for d in ob.data.attributes['dna_tunic_region'].data]
# For every loop corner the UV and original position remain identical.
heat=json.load(open(BASE+'/sister-auto-weights.json'))
oldpart={i:pi for pi,ids in enumerate(parts) for i in ids}
for v in ob.data.vertices:
    i=v.index;oi=origin[i];pi=oldpart[oi];x,y,z=v.co;side='L' if x>0 else 'R'
    if pi==3:
        if tunic[i]:ws=mix({'pelvis':1},{'tunic.'+side:1},1-smoothstep(1.0,1.10,z))
        else:
            leg=mix({'shin.'+side:1},{'thigh.'+side:1},smoothstep(.46,.59,z));ws=mix(leg,{'pelvis':1},smoothstep(.86,1.015,z))
        set_weights(ob,i,ws)
    elif pi==0 and z<1.34:
        central=mix({'pelvis':1},{'spine':1},smoothstep(1.13,1.22,z));central=mix(central,{'chest':1},smoothstep(1.21,1.33,z))
        ws=mix(central,{'upper_arm.'+side:1},smoothstep(.115,.205,abs(x)))
        set_weights(ob,i,ws)
    elif pi in [7,8,10,11,16,17,18,19,21,23,30,31,33,34]:
        ws=mix({'foot.'+side:1},{'shin.'+side:1},smoothstep(.16,.27,z));ws=mix(ws,{'toe.'+side:1},(1-smoothstep(-.23,-.15,y))*.8)
        set_weights(ob,i,ws)
ob['local_topology_note']='Tunic/leggings fused interface split by atlas face region, preserving all face corners, original positions and UVs. No new triangles.'
json.dump({'before':before,'after':signature(ob.data),'interface_edges_split':len(split),'cloth_faces':len(clothfaces),'cloth_vertices':sum(tunic),'origin_map':origin},open(BASE+'/sister-local-split-audit.json','w'),indent=2)
for test,pos in [('legs',(3,-5,1.6)),('shoulders',(0,-5,1.2)),('crouch',(3,-5,1.8))]:
    pose_world(rig,TESTS[test]);camera(s,pos);render(s,'sister-refined-'+test)
reset_pose(rig)
result={'audit':audit(ob,rig),'split_edges':len(split),'cloth_faces':len(clothfaces),'cloth_vertices':sum(tunic)}
