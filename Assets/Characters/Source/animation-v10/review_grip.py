# Read-only: hand close-ups and a both-characters view of the spear clips.
# blender --background FILE --python review_grip.py -- OUT_DIR
import bpy, os, sys
from mathutils import Vector
import numpy as np
OUT = sys.argv[sys.argv.index('--') + 1]


def shot(s, cam, focus, d, scale):
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = scale
    cam.location = focus + Vector(d)
    cam.rotation_euler = (focus - cam.location).to_track_quat('-Z', 'Y').to_euler()
    p = os.path.join(OUT, '_t.png')
    s.render.filepath = p
    bpy.ops.render.render(write_still=True, scene=s.name)
    im = bpy.data.images.load(p)
    w, h = im.size
    px = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, im.channels)[:, :, :4]
    bpy.data.images.remove(im)
    os.remove(p)
    return px


def save(rows, name):
    sheet = np.vstack(rows[::-1])
    H, W, _ = sheet.shape
    out = bpy.data.images.new(name, W, H, alpha=True)
    out.pixels = sheet.ravel().tolist()
    out.filepath_raw = os.path.join(OUT, name + '.png')
    out.file_format = 'PNG'
    out.save()


rows = []
for clip, frame in [('SpearIdle', 1), ('SpearThrust', 13)]:
    s = bpy.data.scenes['ANIM_REVIEW_' + clip]
    bpy.context.window.scene = s
    s.render.resolution_x, s.render.resolution_y = 420, 420
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = 'PNG'
    s.frame_set(frame)
    cam = s.camera
    for label in ['Brother', 'Sister']:
        rig = bpy.data.objects[f'REVIEW_{clip}_{label}_Rig']
        row = []
        for side in 'RL':
            hand = rig.matrix_world @ rig.pose.bones['hand.' + side].matrix.translation
            for d in [(-1.6, -1.2, .7), (-1.2, 1.2, 1.0)]:
                row.append(shot(s, cam, hand, d, .55))
        rows.append(np.hstack(row))
save(rows, 'spear-hands')
# Both characters, same framing as a three-quarter viewport.
rows = []
for clip, fs in [('SpearIdle', [1]), ('SpearThrust', [6, 13, 21])]:
    s = bpy.data.scenes['ANIM_REVIEW_' + clip]
    bpy.context.window.scene = s
    s.render.resolution_x, s.render.resolution_y = 560, 460
    for o in s.collection.all_objects:
        if o and o.name.startswith(('Label_', 'Title_')):
            o.hide_render = True
    a = bpy.data.objects[f'REVIEW_{clip}_Brother_Rig'].matrix_world.translation
    b = bpy.data.objects[f'REVIEW_{clip}_Sister_Rig'].matrix_world.translation
    focus = (a + b) / 2 + Vector((0, -.2, 1.0))
    for f in fs:
        s.frame_set(f)
        rows.append(shot(s, s.camera, focus, (.5, -2.8, 2.0), 2.6))
save([np.hstack(rows)], 'spear-both')
print('GRIP_REVIEW_DONE')
