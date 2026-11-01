exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
from mathutils.kdtree import KDTree
os.makedirs(BASE+'/qualification',exist_ok=True)
reports={}
for label in ['Brother','Sister']:
    s=bpy.data.scenes[label+'_Rig_Validation_v1'];bpy.context.window.scene=s;s.frame_set(1)
    ob=bpy.data.objects[label+'_RigMesh_v1'];rig=bpy.data.objects[label+'_Humanoid_v1']
    activate(ob);rig.select_set(True)
    p=BASE+'/qualification/'+label.lower()+'-v007-rest.glb';assert not os.path.exists(p)
    bpy.ops.export_scene.gltf(filepath=p,export_format='GLB',use_selection=True,use_active_scene=True,export_animations=False,
       export_skins=True,export_influence_nb=4,export_all_influences=False,export_yup=True,export_leaf_bone=False,
       export_def_bones=False,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_rest_position_armature=True)
    raw=open(p,'rb').read();length,kind=struct.unpack_from('<II',raw,12);doc=json.loads(raw[20:20+length])
    embedded=all('bufferView' in im and 'uri' not in im for im in doc.get('images',[]))
    attrs=[pr['attributes'] for m in doc['meshes'] for pr in m['primitives']]
    record={'file':p,'bytes':len(raw),'skins':len(doc.get('skins',[])),'joints':len(doc['skins'][0]['joints']),
      'embedded_images':len(doc.get('images',[])),'all_images_embedded':embedded,'animation_count':len(doc.get('animations',[])),
      'has_uv_and_weights':all('TEXCOORD_0' in a and 'JOINTS_0' in a and 'WEIGHTS_0' in a for a in attrs),
      'has_extra_influence_sets':any('JOINTS_1' in a for a in attrs)}
    prior_objects=set(bpy.data.objects)
    rt=bpy.data.scenes.new(label+'_QUALIFICATION_ONLY_Roundtrip_v007');bpy.context.window.scene=rt
    bpy.ops.import_scene.gltf(filepath=p,import_pack_images=True,merge_vertices=False,import_shading='NORMALS',bone_heuristic='BLENDER',disable_bone_shape=True)
    imported=[o for o in bpy.data.objects if o not in prior_objects]
    mo=next(o for o in imported if o.type=='MESH');ar=next(o for o in imported if o.type=='ARMATURE')
    mo.data.calc_loop_triangles();coords=[mo.matrix_world@v.co for v in mo.data.vertices]
    kd=KDTree(len(ob.data.vertices))
    for v in ob.data.vertices:kd.insert(ob.matrix_world@v.co,v.index)
    kd.balance()
    original_hierarchy={b.name:b.parent.name if b.parent else None for b in rig.data.bones}
    rt_hierarchy={b.name:b.parent.name if b.parent else None for b in ar.data.bones}
    record['roundtrip']={'triangles':len(mo.data.loop_triangles),'vertices_after_uv_normal_splits':len(mo.data.vertices),
      'hierarchy_matches':original_hierarchy==rt_hierarchy,'bone_count':len(ar.data.bones),
      'height':max(v.z for v in coords)-min(v.z for v in coords),'feet_min_z':min(v.z for v in coords),
      'rest_position_max_error':max(kd.find(v)[2] for v in coords),'weights':audit(mo,ar),
      'images':[{'name':n.image.name,'size':list(n.image.size),'packed':bool(n.image.packed_file)} for m in mo.data.materials for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]}
    reports[label]=record
    # Retain qualification imports for inspection. No cleanup or datablock removal.
    for o in imported:
        o.name='QUALIFICATION_ONLY_'+o.name
        o['qualification_only']=True
    rt['purpose']='Rest-pose GLB round-trip qualification only. Author on the Rig_Validation scenes.'
    bpy.context.window.scene=s
json.dump(reports,open(BASE+'/qualification/roundtrip-v007.json','w'),indent=2)
result=reports
