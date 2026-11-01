exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
s=bpy.data.scenes['Brother_Rig_Validation_v1'];bpy.context.window.scene=s
ob=bpy.data.objects['Brother_RigMesh_v1'];rig=bpy.data.objects['Brother_Humanoid_v1'];reset_pose(rig)
add_tunic_bones(rig)
for test,pos in [('legs',(3,-5,1.6)),('crouch',(3,-5,1.8)),('arms',(3,-5,1.9))]:
    pose_world(rig,TESTS[test]);camera(s,pos);render(s,'brother-final-'+test)
reset_pose(rig)
result={'audit':audit(ob,rig),'driver_count':len(rig.animation_data.drivers)}
