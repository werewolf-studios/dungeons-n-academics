exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
import ast
for file,fname in [('07_brother_validate.py','evaluate_tests'),('14_final_validation.py','zero_triangles')]:
    tree=ast.parse(open(BASE+'/'+file).read());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fname);exec(compile(ast.Module(body=[node],type_ignores=[]),fname,'exec'))
report=json.load(open(BASE+'/validation-v009.json'));report['version']=10;report['final_file']=BASE+'/siblings-rig-v010-reviewed.blend'
report['last_correction']='Brother front hem uses driven clearance while rear hem blends pelvis/thigh weights, smoothly across both center and depth; repaired waist remains held to pelvis. Sister collar matches adjacent torso/neck.'
s=bpy.data.scenes['Brother_Rig_Validation_v1'];bpy.context.window.scene=s;s.frame_set(1);ob=bpy.data.objects['Brother_RigMesh_v1'];rig=bpy.data.objects['Brother_Humanoid_v1'];action=rig.animation_data.action;rig.animation_data.action=None
report['characters']['Brother']['samples']=evaluate_tests(ob,rig);baseline=zero_triangles(ob.data);newbad=[]
for name,rots in TESTS.items():
    for t in [.25,.5,.75,1]:
        pose_world(rig,{k:tuple(v*t for v in deg) for k,deg in rots.items()});ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();newly=zero_triangles(me)-baseline
        if newly:newbad.append({'pose':name,'fraction':t,'triangles':[list(ids) for ids in newly]})
        ev.to_mesh_clear()
reset_pose(rig);rig.animation_data.action=action;s.frame_set(1)
report['characters']['Brother']['weights']=audit(ob,rig);report['characters']['Brother']['new_collapsed_triangles']=newbad
report['characters']['Brother']['visual_review_v010']='55deg hip/95deg knee and 60deg crouch viewed from back and front. Rear thigh clipping corrected; open side splits reveal the leg during high flexion. Waist band stretch <0.006%.'
originals=json.load(open(BASE+'/source-signatures.json'))['original_signatures']
for label in ['Brother','Sister']:
    mesh=bpy.data.objects[label+'_RigMesh_v1'];src=mesh['source_object']
    report['characters'][label]['source_unchanged']=signature(bpy.data.objects[src].data)==originals[src]
    report['characters'][label]['uv_exact']=signature(mesh.data)['uv']==originals[src]['uv']
    json.dump([{mesh.vertex_groups[g.group].name:g.weight for g in v.groups if g.weight>0} for v in mesh.data.vertices],open(BASE+'/'+label.lower()+'-final-v010-weights.json','w'))
review=bpy.data.scenes['DNA_REVIEW_ONLY_v008'];bpy.context.window.scene=review
for label in ['Brother','Sister']:pose_world(bpy.data.objects['REVIEW_ONLY_'+label+'_Rig'],TESTS['arms'])
camera(review,(0,-5,1),scale=3.15);render(review,'rig-review-v010')
exec(compile(open(BASE+'/15_glb_qualification.py').read().replace('v007','v010'),'qualification_v010','exec'))
report['roundtrip']=json.load(open(BASE+'/qualification/roundtrip-v010.json'))
json.dump(report,open(BASE+'/validation-v010.json','w'),indent=2)
notes='''# Character rigging handoff — v010

Latest working file: `siblings-rig-v010-reviewed.blend` in this directory.
Both approved designs are rigged; the brother was bound/tested first. The sister
has a documented deep-flexion garment limitation. No production animation or
Godot player replacement was performed.

## Working scenes and objects

| Scene | Working mesh | Armature |
| --- | --- | --- |
| Brother_Rig_Validation_v1 | Brother_RigMesh_v1 | Brother_Humanoid_v1 |
| Sister_Rig_Validation_v1 | Sister_RigMesh_v1 | Sister_Humanoid_v1 |

The final file opens on the brother rig, Pose mode, neutral frame 1. Switch scenes
to work on the sister. Objects/scenes prefixed REVIEW_ONLY or QUALIFICATION_ONLY
are inspection copies, not authoring targets. All original scenes and approved
source objects remain intact. The external dungeoncharacter.blend and canonical
p2-cleanup-v2-smooth-tunic.blend were never overwritten.

## Bind and hierarchy

Each character is 1.8 m tall, feet at Z=0, with mesh/rig transforms at identity.
Blender: +Z up, -Y forward, X left/right. The earlier review rotation/spacing is
not baked into the rig. glTF converts this to +Y up / +Z model forward. Reconcile
model yaw with Player.cs Basis.LookingAt during later integration; do not assume
this rest export can directly replace the existing player subtree.

Both use the same 24 bone names and parent relationships, independently fitted:
root -> pelvis -> spine -> chest -> neck -> head; clavicle.L/R -> upper_arm.L/R
-> forearm.L/R -> hand.L/R under chest; thigh.L/R -> shin.L/R -> foot.L/R ->
toe.L/R under pelvis; tunic.L/R under pelvis. Root is non-deforming in the source.
No individual finger bones were added to the generated hands. No facial/IK rig.

The two tunic helpers use Blender location drivers from local thigh ROT_X.
They are a limited clearance aid, not cloth simulation. Their transforms MUST
be baked with future animation exports. Final skinning uses LINEAR blend
skinning (preserve-volume OFF) to match ordinary Godot/glTF behavior.

## Weight and deformation work

Heat weights were only the starting point. Head/hair/eye/mouth shells were
attached to the head, neck transitions painted numerically, the pouch fixed to
pelvis, and clasps attached to chest. Wrist transitions, cuffs, shoe layers,
waist, sleeves and hem weights were corrected after rendered bend tests.

Brother: removed residual arm influence from the repaired waist band. Smoothed
left/right hem influence across the center. Front hem uses driven clearance;
rear hem follows pelvis/thigh blends so it does not pull through the trousers.
The repaired seam band remains essentially rigid across all sampled stresses.

Sister: tightened sleeve weights, retained mouth/hair shell attachment, transferred
collar weights from nearby torso/neck to close a visible gap under neck tilt,
and kept the layered chunky shoes on a consistent foot/shin field. The stiff
sole does not use the reserved toe bones. Lower tunic/leggings are fused along
irregular generated junctions; smoothed weights reduce tears while retaining
the approved source topology. Atlas splitting and a global shape correction
were tested and discarded: neither is present in the final working mesh.

## Validation

`validation-v010.json` is the final machine-readable audit. Per-vertex weights
are also saved as brother-final-v010-weights.json and sister-final-v010-weights.json.

| Check | Brother | Sister |
| --- | ---: | ---: |
| Source vertices | 6,229 | 6,106 |
| Runtime triangles | 11,910 | 11,280 |
| Unweighted vertices | 0 | 0 |
| Non-normalized sums (tolerance 1e-5) | 0 | 0 |
| Maximum influences | 4 | 4 |
| New collapsed triangles in samples | 0 | 0 |
| Sampled stress/transition states | 28 | 28 |
| Exact UV corner hash preserved | yes | yes |
| Original source geometry unchanged | yes | yes |

Original topology, UVs and material datablocks are retained. Each source material
still references its original four packed 2048x2048 PBR images. The brother has
three near-collinear triangles before binding (boot/collar details); these are
not new joint collapses. No global weld, remesh, decimation or redesign was used.

The DEFORM_TEST_v2 actions are diagnostic only, neutral between every stress:

| Peak frame | Stress |
| --- | --- |
| 1 | neutral |
| 13 | shoulders forward, elbows 95/80 degrees, wrists |
| 37 | 55 degree hip, 95 degree knee, ankle |
| 61 | distributed torso bend/twist and neck/head turn |
| 85 | wide shoulder abduction from A-pose |
| 109 | 60 degree hip / 100 degree knee crouch stress |
| 133 | moderate 30 degree hip / 55 degree knee stride |
| 157 | wrist/ankle/neck side-bend stress |
| 169 | neutral |

Intermediate states were sampled at 25%, 50%, 75%, 100% of these targets. The
actions use in-place FK poses with no foot locking or travel. They are not
production idle/walk/run clips and must not be shipped as such.

`qualification/*-v010-rest.glb` were exported and re-imported through connected
Blender MCP. Both retain the 24-joint hierarchy, exact triangle counts, UVs,
normalized four-influence skinning and embedded 2K maps. Rest-position error is
under 0.003 mm. glTF combines metallic/roughness into one image (three embedded
images total). The exporter sampler warning was checked: all contributing nodes
have identical Linear/FLAT/REPEAT settings and active UV inputs.

These are REST-ONLY qualification files under Source/.gdignore, with no
animations and no live helper drivers. They are not the final runtime assets.
Round-trip vertex counts increase because UV/normal discontinuities split
render vertices; triangle counts do not change. See qualification/roundtrip-v010.json.

## Visual evidence and remaining limitations

- rig-review-v010.png: both characters in elbow/shoulder/wrist stress.
- brother-v010-legs.png, brother-v010-crouch.png: final rear-hem correction.
- brother-v010-legs-front.png: front view of high hip/knee stress.
- brother-linear-stride.png, sister-linear-stride.png: moderate stride review.
- sister-v008-wrists_ankles.png and sister-v008-torso.png: final collar correction.
- brother-v007-shoulders.png, sister-v007-shoulders.png: shoulder stress.
- sister-v007-legs.png and sister-v007-crouch.png: retained deep-flexion limits.

SISTER LIMITATION: At 55-60 degree hip flexion/deep crouch, the thighs still
intersect the short tunic. Moderate stride and upper-body poses are usable, but
the rig is not cleared for deep crouch/seated/high-knee production clips. Those
need local garment/hip correctives or careful retopology in the animation stage.
Broad sleeve folds also need checking in final overhead clips. Long hair is
rigidly attached to head; extreme head turns near shoulders need clip polish.

Brother high flexion opens the authored tunic side splits; there is no physical
cloth/contact solving. Neither rig has facial/finger controls, IK, foot locking
or production animations. Three source near-collinear triangles remain on brother.

## Subsequent milestone

Create production in-place idle/locomotion actions after resolving any garment
limits required by the chosen clips. Bake tunic helper motion and validate the
animated GLB in Godot, including texture appearance, orientation and cadence.
Use a new runtime directory outside Source. Preserve existing movement,
interaction, pushing, combat character selection, and C debug swap behavior.
Address the documented mismatch: Player.cs expects Pivot/Male-Character and
Pivot/Female-Character, while the current male placeholder is at the scene root.
Player-scene replacement and production animation are still deferred.

No paid generation or external rigging service was used. Future model generation:
Tripo preferred, Genex fallback; Blender owns rigging and animation.
'''
open(BASE+'/RIGGING_HANDOFF_v010.md','w',encoding='utf-8').write(notes)
t=bpy.data.texts.new('DNA_RIGGING_FINAL_v010');t.write(notes)
s=bpy.data.scenes['Brother_Rig_Validation_v1'];bpy.context.window.scene=s;s.frame_set(1);rig=bpy.data.objects['Brother_Humanoid_v1'];activate(rig);bpy.ops.object.mode_set(mode='POSE')
path=report['final_file'];assert not os.path.exists(path);bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
result={'saved':path,'notes':BASE+'/RIGGING_HANDOFF_v010.md','report':BASE+'/validation-v010.json','preview':BASE+'/rig-review-v010.png',
 'audits':{label:{'weights':r['weights'],'max_stretch':max(t['edge_stretch_max'] for t in r['samples']),'waist_max_stretch':max(t['waist_band_stretch_max'] for t in r['samples']),'new_collapses':r['new_collapsed_triangles']} for label,r in report['characters'].items()}}
