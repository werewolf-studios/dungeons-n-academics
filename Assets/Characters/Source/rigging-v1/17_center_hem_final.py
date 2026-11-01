exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
import ast
s=bpy.data.scenes['Brother_Rig_Validation_v1'];bpy.context.window.scene=s
ob=bpy.data.objects['Brother_RigMesh_v1'];rig=bpy.data.objects['Brother_Humanoid_v1'];act=rig.animation_data.action;rig.animation_data.action=None;reset_pose(rig)
count=0
for v in ob.data.vertices:
    ws={ob.vertex_groups[g.group].name:g.weight for g in v.groups}
    t=ws.pop('tunic.L',0)+ws.pop('tunic.R',0)
    if t:
        blend=smoothstep(-.09,.09,v.co.x);ws['tunic.L']=t*blend;ws['tunic.R']=t*(1-blend);set_weights(ob,v.index,ws);count+=1
for test,pos in [('legs',(3,5,1.7)),('crouch',(3,5,1.8)),('stride',(3,-5,1.7))]:
    pose_world(rig,TESTS[test]);camera(s,pos);render(s,'brother-v009-'+test+('-back' if test!='stride' else ''))
reset_pose(rig);rig.animation_data.action=act;s.frame_set(1)
tree=ast.parse(open(BASE+'/07_brother_validate.py').read());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='evaluate_tests');exec(compile(ast.Module(body=[node],type_ignores=[]),'evaluate_tests','exec'))
tree=ast.parse(open(BASE+'/14_final_validation.py').read());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='zero_triangles');exec(compile(ast.Module(body=[node],type_ignores=[]),'zero_triangles','exec'))
report=json.load(open(BASE+'/validation-v008.json'));report['version']=9;report['final_file']=BASE+'/siblings-rig-v009-reviewed.blend'
report['last_correction']='Sister collar matches nearby torso/neck; brother tunic helper weights blend smoothly across center +/-0.09m, removing sign discontinuity at back hem.'
for label in ['Brother','Sister']:
    s=bpy.data.scenes[label+'_Rig_Validation_v1'];bpy.context.window.scene=s;s.frame_set(1)
    mesh=bpy.data.objects[label+'_RigMesh_v1'];ar=bpy.data.objects[label+'_Humanoid_v1'];action=ar.animation_data.action;ar.animation_data.action=None
    report['characters'][label]['samples']=evaluate_tests(mesh,ar);baseline=zero_triangles(mesh.data);newbad=[]
    for name,rots in TESTS.items():
        for t in [.25,.5,.75,1]:
            pose_world(ar,{k:tuple(v*t for v in deg) for k,deg in rots.items()});ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();newly=zero_triangles(me)-baseline
            if newly:newbad.append({'pose':name,'fraction':t,'triangles':[list(ids) for ids in newly]})
            ev.to_mesh_clear()
    reset_pose(ar);ar.animation_data.action=action;s.frame_set(1)
    report['characters'][label]['weights']=audit(mesh,ar);report['characters'][label]['new_collapsed_triangles']=newbad
    json.dump([{mesh.vertex_groups[g.group].name:g.weight for g in v.groups if g.weight>0} for v in mesh.data.vertices],open(BASE+'/'+label.lower()+'-final-v009-weights.json','w'))
# The preview shares working mesh weights but has its own group definitions; copy current group weights explicitly.
rm=bpy.data.objects['REVIEW_ONLY_Brother_Mesh']
assert rm.data==ob.data
review=bpy.data.scenes['DNA_REVIEW_ONLY_v008'];bpy.context.window.scene=review
camera(review,(0,-5,1),scale=3.15);render(review,'rig-review-v009')
# Rest-only portable qualification remains separate from Godot's live player.
exec(compile(open(BASE+'/15_glb_qualification.py').read().replace('v007','v009'),'qualification_v009','exec'))
report['roundtrip']=json.load(open(BASE+'/qualification/roundtrip-v009.json'))
json.dump(report,open(BASE+'/validation-v009.json','w'),indent=2)
bpy.data.texts['DNA_RIGGING_README_v008'].write('\nFINAL UPDATE: use siblings-rig-v009-reviewed.blend, RIGGING_HANDOFF_v009.md and validation-v009.json.\n')
s=bpy.data.scenes['Brother_Rig_Validation_v1'];bpy.context.window.scene=s;s.frame_set(1);rig=bpy.data.objects['Brother_Humanoid_v1'];activate(rig);bpy.ops.object.mode_set(mode='POSE')
path=report['final_file'];assert not os.path.exists(path);bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
result={'saved':path,'center_blended_vertices':count,'preview':BASE+'/rig-review-v009.png',
 'audits':{label:{'weights':r['weights'],'max_stretch':max(t['edge_stretch_max'] for t in r['samples']),'p99_stretch_max':max(t['edge_stretch_p99'] for t in r['samples']),'waist_max_stretch':max(t['waist_band_stretch_max'] for t in r['samples']),'new_collapses':r['new_collapsed_triangles']} for label,r in report['characters'].items()}}
