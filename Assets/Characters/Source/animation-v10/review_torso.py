# Read-only: chest and collar close-ups, for spotting mesh tears from torso twist.
# blender --background FILE --python review_torso.py -- OUT_DIR
import bpy, os, sys
from mathutils import Vector
import numpy as np
OUT = sys.argv[sys.argv.index('--') + 1]
rows = []
for clip, frame in [('SpearIdle', 1), ('SpearThrust', 6), ('SpearThrust', 13)]:
    s = bpy.data.scenes['ANIM_REVIEW_' + clip]
    bpy.context.window.scene = s
    s.render.resolution_x, s.render.resolution_y = 420, 420
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = 'PNG'
    for o in s.collection.all_objects:
        if o and o.type == 'MESH' and o.name.endswith('_Spear'):
            o.hide_render = True
    s.frame_set(frame)
    cam = s.camera
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = .7
    row = []
    for label in ['Brother', 'Sister']:
        rig = bpy.data.objects[f'REVIEW_{clip}_{label}_Rig']
        chest = rig.matrix_world @ rig.pose.bones['chest'].matrix.translation
        for d in [(-.9, -2.4, .3), (.9, -2.4, .3)]:
            cam.location = chest + Vector(d)
            cam.rotation_euler = (chest - cam.location).to_track_quat('-Z', 'Y').to_euler()
            p = os.path.join(OUT, '_t.png')
            s.render.filepath = p
            bpy.ops.render.render(write_still=True, scene=s.name)
            im = bpy.data.images.load(p)
            w, h = im.size
            row.append(np.array(im.pixels[:], dtype=np.float32).reshape(h, w, im.channels)[:, :, :4])
            bpy.data.images.remove(im)
            os.remove(p)
    rows.append(np.hstack(row))
sheet = np.vstack(rows[::-1])
H, W, _ = sheet.shape
out = bpy.data.images.new('torso', W, H, alpha=True)
out.pixels = sheet.ravel().tolist()
out.filepath_raw = os.path.join(OUT, 'spear-torso.png')
out.file_format = 'PNG'
out.save()
print('TORSO_DONE')
