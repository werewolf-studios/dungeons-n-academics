import bpy
scene = bpy.context.scene
scene.camera.data.ortho_scale = 1.1
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
