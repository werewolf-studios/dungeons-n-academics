exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
import statistics
s=bpy.data.scenes['Brother_Rig_Validation_v1'];bpy.context.window.scene=s
ob=bpy.data.objects['Brother_RigMesh_v1'];rig=bpy.data.objects['Brother_Humanoid_v1']
def evaluate_tests(ob,rig):
    rest=[v.co.copy() for v in ob.data.vertices]
    edges=[(e.vertices[0],e.vertices[1],(rest[e.vertices[0]]-rest[e.vertices[1]]).length) for e in ob.data.edges]
    seam=[(a,b,l) for a,b,l in edges if all(1.06<rest[i].z<1.09 and abs(rest[i].x)<.18 for i in [a,b])]
    records=[]
    for name,rot in TESTS.items():
        for t in [.25,.5,.75,1.0]:
            pose_world(rig,{k:tuple(d*t for d in v) for k,v in rot.items()})
            dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles()
            coords=[v.co.copy() for v in me.vertices]
            ratios=sorted((coords[a]-coords[b]).length/l for a,b,l in edges if l>1e-7)
            seamratios=[(coords[a]-coords[b]).length/l for a,b,l in seam if l>1e-7]
            records.append({'test':name,'fraction':t,'nonfinite_vertices':sum(not all(math.isfinite(c) for c in v) for v in coords),
                'zero_area_triangles':sum((coords[tri.vertices[1]]-coords[tri.vertices[0]]).cross(coords[tri.vertices[2]]-coords[tri.vertices[0]]).length<1e-12 for tri in me.loop_triangles),
                'edge_stretch_p99':ratios[int(.99*(len(ratios)-1))],'edge_stretch_max':max(ratios),'edge_compression_min':min(ratios),
                'waist_band_edges':len(seam),'waist_band_stretch_max':max(seamratios) if seamratios else None})
            ev.to_mesh_clear()
    reset_pose(rig)
    return records
def diagnostic_action(s,rig,label):
    assert rig.animation_data is None or rig.animation_data.action is None
    rig.animation_data_create();act=bpy.data.actions.new(label+'_DEFORM_TEST_v1');rig.animation_data.action=act
    keys=[(1,'neutral'),(13,'arms'),(25,'neutral'),(37,'legs'),(49,'neutral'),(61,'torso'),(73,'neutral'),(85,'shoulders'),(97,'neutral'),(109,'crouch'),(121,'neutral')]
    for frame,name in keys:
        s.frame_set(frame);pose_world(rig,TESTS.get(name,{}))
        for pb in rig.pose.bones:
            pb.rotation_mode='QUATERNION'
            if name=='neutral' or pb.name not in TESTS.get(name,{}):pb.rotation_quaternion=(1,0,0,0)
            pb.keyframe_insert('rotation_quaternion',frame=frame,group=pb.name)
        mark=s.timeline_markers.new(label+' '+name,frame=frame)
    s.frame_start=1;s.frame_end=121;s.render.fps=24;s.frame_set(1)
    act['purpose']='DIAGNOSTIC ONLY: neutral transitions and joint stresses. Not a production animation.';act.use_fake_user=True
    return act.name
validation=evaluate_tests(ob,rig)
action=diagnostic_action(s,rig,'Brother')
camera(s,(0,-5,1.0));render(s,'brother-final-bind')
originals=json.load(open(BASE+'/source-signatures.json'))['original_signatures']
unchanged={n:signature(bpy.data.objects[n].data)==sig for n,sig in originals.items()}
uv=signature(ob.data)['uv']==originals['Brother_SmoothTunic_v2']['uv']
report={'weights':audit(ob,rig),'source_objects_unchanged':unchanged,'uv_exactly_preserved':uv,'deformations':validation,'diagnostic_action':action,
 'rest_height':max(v.co.z for v in ob.data.vertices)-min(v.co.z for v in ob.data.vertices),'feet_min_z':min(v.co.z for v in ob.data.vertices),
 'visual_review':{'arms':'95/80deg elbow bends; hands retained, no finger rig','legs':'55deg hip,95deg knee,20deg ankle; hem translation clears front thigh','torso':'30deg distributed forward bend +24deg twist; repaired waist held to pelvis','shoulders':'73deg abduction from A-pose; no long sleeve-weight spikes','crouch':'60deg hip/100deg knee stress; short tunic opens at side splits'},
 'limitations':['No individual finger/facial controls.','No physical cloth/contact solving; extreme seated, crossed-leg and overhead poses require clip-specific polish.','Tunic helper drivers must be baked for runtime export.','Dual quaternion preserve-volume is used in Blender; linear skinning must be checked separately before production export.']}
json.dump(report,open(BASE+'/brother-validation-v003.json','w'),indent=2)
path=BASE+'/brother-rig-v003-validated.blend';assert not os.path.exists(path)
bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
result={'saved':path,'audit':report['weights'],'sources_unchanged':unchanged,'uv_preserved':uv,'samples':len(validation),'nonfinite':sum(r['nonfinite_vertices'] for r in validation),'zero_area_triangles':sum(r['zero_area_triangles'] for r in validation),'seam_band_stretch_max':max(r['waist_band_stretch_max'] for r in validation)}
