exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
so=bpy.data.objects['Sister_RigMesh_v1'];sr=bpy.data.objects['Sister_Humanoid_v1']
# The temporary global front correction caused local folds; retain no shape correction.
if so.data.shape_keys:
    for key in list(so.data.shape_keys.key_blocks)[::-1]:so.shape_key_remove(key)
for side in ['L','R']:
    pb=sr.pose.bones['tunic.'+side];f=pb.bone.matrix_local.to_3x3().inverted()@Vector((.01 if side=='L' else -.01,-.12,.015));back=pb.bone.matrix_local.to_3x3().inverted()@Vector((0,.05,.01))
    for axis in range(3):sr.animation_data.drivers.find(pb.path_from_id('location'),index=axis).driver.expression=f'{f[axis]:.8f}*max(0,min(1,-r/0.96))+{back[axis]:.8f}*max(0,min(1,r/0.52))'
sr['cloth_notes']='Smoothed weights over fused tunic/leggings. Hem helpers translate up to .12m forward/.05m backward with hip flexion. Deep crouches/high knees still need corrective polish. Bake helpers for export.'
for label in ['Brother','Sister']:
    s=bpy.data.scenes[label+'_Rig_Validation_v1'];bpy.context.window.scene=s
    ob=bpy.data.objects[label+'_RigMesh_v1'];rig=bpy.data.objects[label+'_Humanoid_v1']
    if rig.animation_data:rig.animation_data.action=None
    for m in ob.modifiers:
        if m.type=='ARMATURE':m.use_deform_preserve_volume=False
    for test,pos in [('stride',(3,-5,1.7)),('arms',(3,-5,1.9)),('torso',(3,5,1.8))]:
        pose_world(rig,TESTS[test]);camera(s,pos);render(s,label.lower()+'-linear-'+test)
    reset_pose(rig)
path=BASE+'/siblings-rig-v006-linear-review.blend';assert not os.path.exists(path);bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
result={'saved':path,'linear_skinning':True,'sister_weights':audit(so,sr)}
