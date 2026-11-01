exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
import ast
tree=ast.parse(open(BASE+'/07_brother_validate.py').read())
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='evaluate_tests')
exec(compile(ast.Module(body=[node],type_ignores=[]),'evaluate_tests','exec'))
def zero_triangles(mesh):
    mesh.calc_loop_triangles();cs=[v.co for v in mesh.vertices]
    return {tuple(sorted(t.vertices)) for t in mesh.loop_triangles if (cs[t.vertices[1]]-cs[t.vertices[0]]).cross(cs[t.vertices[2]]-cs[t.vertices[0]]).length<1e-12}
def action_v2(s,rig,label):
    rig.animation_data_create();act=bpy.data.actions.new(label+'_DEFORM_TEST_v2');rig.animation_data.action=act;act.use_fake_user=True
    keys=[(1,'neutral')]
    for i,name in enumerate(TESTS):keys.extend([(13+24*i,name),(25+24*i,'neutral')])
    for frame,name in keys:
        s.frame_set(frame);pose_world(rig,TESTS.get(name,{}))
        for pb in rig.pose.bones:
            pb.rotation_mode='QUATERNION'
            if name=='neutral' or pb.name not in TESTS.get(name,{}):pb.rotation_quaternion=(1,0,0,0)
            pb.keyframe_insert('rotation_quaternion',frame=frame,group=pb.name)
        s.timeline_markers.new('v2 '+name,frame=frame)
    act['purpose']='Deformation diagnostics only, not production locomotion. Extremes intentionally expose limits.'
    s.frame_start=1;s.frame_end=keys[-1][0];s.frame_set(1);s.render.fps=24
    return {'name':act.name,'poses':keys}
report={'version':7,'status':'Rigged and tested; sister deep-flexion garment limitation remains',
 'bind_convention':{'height_m':1.8,'up':'+Z','front':'-Y','feet_z':0,'scale_applied':True,'mesh_and_rig_transforms':'identity'},
 'skin_method':'Linear blend skinning (preserve volume disabled), matching ordinary glTF/Godot skinning',
 'characters':{},'integration':'No Godot scene or gameplay code changed. Production clips and player replacement deferred.'}
originals=json.load(open(BASE+'/source-signatures.json'))['original_signatures']
for label,source in [('Brother','Brother_SmoothTunic_v2'),('Sister','Sister_Clean_v1')]:
    s=bpy.data.scenes[label+'_Rig_Validation_v1'];bpy.context.window.scene=s
    ob=bpy.data.objects[label+'_RigMesh_v1'];rig=bpy.data.objects[label+'_Humanoid_v1'];rig.animation_data.action=None
    reset_pose(rig);baseline=zero_triangles(ob.data);samples=evaluate_tests(ob,rig);newbad=[]
    for name,rots in TESTS.items():
        for t in [.25,.5,.75,1]:
            pose_world(rig,{k:tuple(v*t for v in deg) for k,deg in rots.items()});ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
            newly=zero_triangles(me)-baseline
            if newly:newbad.append({'pose':name,'fraction':t,'triangles':[list(ids) for ids in newly]})
            ev.to_mesh_clear()
    reset_pose(rig)
    for test,pos in [('legs',(3,-5,1.7)),('crouch',(3,-5,1.8)),('shoulders',(0,-5,1.2)),('wrists_ankles',(3,-5,1.7))]:
        pose_world(rig,TESTS[test]);camera(s,pos);render(s,label.lower()+'-v007-'+test)
    reset_pose(rig);camera(s,(0,-5,1));render(s,label.lower()+'-v007-bind')
    uv=signature(ob.data)['uv']==originals[source]['uv']
    weights=audit(ob,rig)
    materials=[{'name':m.name,'same_datablock_as_source':m==bpy.data.objects[source].data.materials[i],
       'images':[{'name':n.image.name,'size':list(n.image.size),'packed':bool(n.image.packed_file)} for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]} for i,m in enumerate(ob.data.materials)]
    action=action_v2(s,rig,label)
    report['characters'][label]={'mesh':ob.name,'rig':rig.name,'scene':s.name,'weights':weights,'uv_exact':uv,'materials':materials,
        'source_unchanged':signature(bpy.data.objects[source].data)==originals[source],
        'source_topology_preserved':len(ob.data.vertices)==originals[source]['vertices'] and len(ob.data.polygons)==originals[source]['faces'],
        'rest_near_zero_triangle_count':len(baseline),'new_collapsed_triangles':newbad,'sample_count':len(samples),'samples':samples,
        'action':action,'hierarchy':[(b.name,b.parent.name if b.parent else None) for b in rig.data.bones],
        'bones':[{'name':b.name,'head':list(b.head_local),'tail':list(b.tail_local),'deform':b.use_deform} for b in rig.data.bones],
        'height':max(v.co.z for v in ob.data.vertices)-min(v.co.z for v in ob.data.vertices),'feet_min_z':min(v.co.z for v in ob.data.vertices)}
    json.dump([{ob.vertex_groups[g.group].name:g.weight for g in v.groups if g.weight>0} for v in ob.data.vertices],open(BASE+'/'+label.lower()+'-final-v007-weights.json','w'))
report['hierarchies_match']=report['characters']['Brother']['hierarchy']==report['characters']['Sister']['hierarchy']
report['limitations']=[
 'Sister: moderate 30deg hip stride, arms, torso, neck, wrists and ankles visually reviewed. At 55-60deg hip flexion/deep crouch, thighs still intersect the short fused tunic; not approved for deep crouch/seated production clips.',
 'Sister: shoulder stress is usable but the generated sleeve has a broad fold; final overhead clips need silhouette polish.',
 'Both: simple FK hand bones, no independent finger controls, facial rig, IK, cloth physics, foot locking or production animation.',
 'Brother: near-collinear source triangles retained; no new collapsed joint triangles in sampled tests.',
 'Tunic helper location drivers must be baked into exported animation. Rest-only qualification GLBs do not reproduce live drivers.',
 'Sister footwear is a stiff sole: toe bones reserved for future clips and not used to flex the shoes.',
 'Godot scene scale, model forward yaw, animation cadence and the existing debug-swap node-path mismatch remain integration work.'
]
json.dump(report,open(BASE+'/validation-v007.json','w'),indent=2)
path=BASE+'/siblings-rig-v007-tested.blend';assert not os.path.exists(path);bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
result={'saved':path,'hierarchies_match':report['hierarchies_match'],'characters':{label:{'weights':r['weights'],'uv_exact':r['uv_exact'],'source_unchanged':r['source_unchanged'],'samples':r['sample_count'],'baseline_degenerate_triangles':r['rest_near_zero_triangle_count'],'new_collapses':r['new_collapsed_triangles']} for label,r in report['characters'].items()}}
