exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
import ast
# Repeat rest-pose qualification for the final collar correction, retaining imports.
exec(compile(open(BASE+'/15_glb_qualification.py').read().replace('v007','v008'),'qualification_v008','exec'))
tree=ast.parse(open(BASE+'/14_final_validation.py').read())
for fname in ['zero_triangles']:
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fname)
    exec(compile(ast.Module(body=[node],type_ignores=[]),fname,'exec'))
tree=ast.parse(open(BASE+'/07_brother_validate.py').read());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='evaluate_tests')
exec(compile(ast.Module(body=[node],type_ignores=[]),'evaluate_tests','exec'))
report=json.load(open(BASE+'/validation-v007.json'));report['version']=8
report['final_file']=BASE+'/siblings-rig-v008-reviewed.blend'
report['last_correction']='Sister collar weights transferred from nearest three torso/neck vertices to close opening under neck tilt.'
report['roundtrip']=json.load(open(BASE+'/qualification/roundtrip-v008.json'))
report['export_sampler_warning_review']='Exporter combines metallic/roughness images. All source image nodes use identical Linear/FLAT/REPEAT settings with the same active UV input; first-sampler warning has no settings conflict.'
for label in ['Brother','Sister']:
    s=bpy.data.scenes[label+'_Rig_Validation_v1'];bpy.context.window.scene=s;s.frame_set(1)
    ob=bpy.data.objects[label+'_RigMesh_v1'];rig=bpy.data.objects[label+'_Humanoid_v1'];action=rig.animation_data.action;rig.animation_data.action=None
    report['characters'][label]['samples']=evaluate_tests(ob,rig)
    baseline=zero_triangles(ob.data);newbad=[]
    for name,rots in TESTS.items():
        for t in [.25,.5,.75,1]:
            pose_world(rig,{k:tuple(v*t for v in deg) for k,deg in rots.items()});ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
            newly=zero_triangles(me)-baseline
            if newly:newbad.append({'pose':name,'fraction':t,'triangles':[list(ids) for ids in newly]})
            ev.to_mesh_clear()
    reset_pose(rig);rig.animation_data.action=action;s.frame_set(1)
    report['characters'][label]['weights']=audit(ob,rig);report['characters'][label]['new_collapsed_triangles']=newbad
    report['characters'][label]['source_unchanged']=signature(bpy.data.objects[ob['source_object']].data)==json.load(open(BASE+'/source-signatures.json'))['original_signatures'][ob['source_object']]
    json.dump([{ob.vertex_groups[g.group].name:g.weight for g in v.groups if g.weight>0} for v in ob.data.vertices],open(BASE+'/'+label.lower()+'-final-v008-weights.json','w'))
json.dump(report,open(BASE+'/validation-v008.json','w'),indent=2)
# Dedicated render-only copies; the two working rigs remain centered at origin.
review=bpy.data.scenes.new('DNA_REVIEW_ONLY_v008');review.unit_settings.system='METRIC';review.render.engine='CYCLES';review.cycles.samples=24
review.render.resolution_x=1400;review.render.resolution_y=1000;review.render.resolution_percentage=100;review.view_settings.view_transform='AgX'
review.world=bpy.data.scenes['Brother_Rig_Validation_v1'].world
col=bpy.data.collections.new('DNA_REVIEW_ONLY_v008');review.collection.children.link(col)
for label,offset in [('Brother',-.55),('Sister',.55)]:
    src=bpy.data.objects[label+'_Humanoid_v1'];rr=src.copy();rr.name='REVIEW_ONLY_'+label+'_Rig';col.objects.link(rr);rr.location.x=offset;rr['review_only']=True;rr.animation_data.action=None
    for fc in rr.animation_data.drivers:
        for v in fc.driver.variables:
            for t in v.targets:
                if t.id==src:t.id=rr
    sm=bpy.data.objects[label+'_RigMesh_v1'];rm=sm.copy();rm.name='REVIEW_ONLY_'+label+'_Mesh';col.objects.link(rm);rm.parent=rr;rm['review_only']=True
    for m in rm.modifiers:
        if m.type=='ARMATURE':m.object=rr
for o in bpy.data.scenes['Brother_Rig_Validation_v1'].objects:
    if o.type in ['CAMERA','LIGHT']:
        cp=o.copy();cp.name='REVIEW_ONLY_'+o.name;col.objects.link(cp)
        if cp.type=='CAMERA':review.camera=cp
bpy.context.window.scene=review
for label in ['Brother','Sister']:pose_world(bpy.data.objects['REVIEW_ONLY_'+label+'_Rig'],TESTS['arms'])
camera(review,(0,-5,1.0),scale=2.22);render(review,'rig-review-v008')
review['purpose']='Render-only copies. Author on Brother_Rig_Validation_v1 and Sister_Rig_Validation_v1.'
text=bpy.data.texts.new('DNA_RIGGING_README_v008')
text.write('Latest rigs: Brother_Rig_Validation_v1 / Sister_Rig_Validation_v1.\n24 matching bones; 1.8m; +Z up/-Y forward; neutral at frame 1.\nDEFORM_TEST_v2 actions are diagnostics only. Frames 1-169.\nSee project Assets/Characters/Source/rigging-v1/RIGGING_HANDOFF_v008.md and validation-v008.json.\nSister deep crouch/high knee garment intersection remains. Bake tunic helper drivers on future export.\nQUALIFICATION_ONLY and REVIEW_ONLY objects are inspection copies, not working characters.\n')
bs=bpy.data.scenes['Brother_Rig_Validation_v1'];bpy.context.window.scene=bs;bs.frame_set(1)
rig=bpy.data.objects['Brother_Humanoid_v1'];activate(rig);bpy.ops.object.mode_set(mode='POSE')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_location=(0,0,.9);area.spaces.active.region_3d.view_distance=2.8
            area.spaces.active.region_3d.view_rotation=Quaternion((1,0,0),math.pi/2)
path=report['final_file'];assert not os.path.exists(path);bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
result={'saved':path,'preview':BASE+'/rig-review-v008.png','validation':BASE+'/validation-v008.json',
 'characters':{label:{'weights':r['weights'],'new_collapses':r['new_collapsed_triangles'],'source_unchanged':r['source_unchanged']} for label,r in report['characters'].items()},
 'roundtrip':{label:{'joints':r['joints'],'hierarchy_matches':r['roundtrip']['hierarchy_matches'],'position_error':r['roundtrip']['rest_position_max_error']} for label,r in report['roundtrip'].items()}}
