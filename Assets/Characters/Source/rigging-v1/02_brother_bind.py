exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
s=bpy.data.scenes['Brother_Rig_Validation_v1'];bpy.context.window.scene=s
ob=bpy.data.objects['Brother_RigMesh_v1']; col=bpy.data.collections['Brother_Rig_Working_v1']
assert not bpy.data.objects.get('Brother_Humanoid_v1')
rig=make_rig('Brother',col)
activate(ob);rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
for m in ob.modifiers:
    if m.type=='ARMATURE':m.use_deform_preserve_volume=True
initial=audit(ob,rig)
json.dump(initial,open(BASE+'/brother-auto-weights-audit.json','w'),indent=2)
path=BASE+'/brother-rig-v001-auto.blend'; assert not os.path.exists(path)
bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
result={'saved':path,'initial_audit':initial,'bone_axes':{b.name:[list(row) for row in b.matrix_local.to_3x3()] for b in rig.data.bones if b.name in ['upper_arm.L','forearm.L','thigh.L','shin.L','spine']}}
