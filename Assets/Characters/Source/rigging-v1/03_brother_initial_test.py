exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
s=bpy.data.scenes['Brother_Rig_Validation_v1'];bpy.context.window.scene=s
ob=bpy.data.objects['Brother_RigMesh_v1'];rig=bpy.data.objects['Brother_Humanoid_v1']
pose_world(rig,TESTS['arms']);camera(s,(3,-5,1.9));render(s,'brother-auto-arms')
pose_world(rig,TESTS['legs']);camera(s,(3,-5,1.6));render(s,'brother-auto-legs')
pose_world(rig,TESTS['torso']);camera(s,(3,5,1.8));render(s,'brother-auto-torso-back')
reset_pose(rig)
result={'images':['brother-auto-arms.png','brother-auto-legs.png','brother-auto-torso-back.png']}
