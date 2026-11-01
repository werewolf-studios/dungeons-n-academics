# Read-only joint audit plus review sheets. Run in background Blender on a saved checkpoint:
# blender --background FILE --python joint_limits.py -- OUT_DIR Label.Clip.Version [...]
import bpy, json, math, os, sys
from mathutils import Vector, Quaternion
import numpy as np
args = sys.argv[sys.argv.index('--') + 1:]
OUT = args[0]
os.makedirs(OUT, exist_ok=True)
LIMITS = {'elbow_flex_idle': 125, 'elbow_flex_attack': 135, 'elbow_twist': 45, 'wrist_bend': 70, 'twist_step': 25, 'torso_bone': 25}
JOINTS = {'elbow': ('upper_arm', 'forearm'), 'wrist': ('forearm', 'hand')}


def rel(arm, pb, p, c):
    rest = (arm.bones[p].matrix_local.inverted() @ arm.bones[c].matrix_local).to_quaternion()
    return rest.inverted() @ (pb[p].matrix.inverted() @ pb[c].matrix).to_quaternion()


def swing_twist(q):
    tw = 2 * math.degrees(math.atan2(q.y, q.w))
    tw = (tw + 180) % 360 - 180
    t = Quaternion((q.w, 0, q.y, 0))
    t.normalize()
    sw = math.degrees((q @ t.inverted()).angle)
    return min(sw, 360 - sw), tw


report = {}
clips = []
for spec in args[1:]:
    label, clip, version = spec.split('.')
    clips.append((label, clip))
    s = bpy.data.scenes[label + '_Animation_v1']
    bpy.context.window.scene = s
    r = bpy.data.objects[label + '_AnimRig_v1']
    for t in r.animation_data.nla_tracks:
        t.mute = True
    a = bpy.data.actions[f'{label}_{clip}_{version}']
    r.animation_data.action = a
    r.animation_data.action_slot = a.slots[0]
    f0, f1 = int(a.frame_range[0]), int(a.frame_range[1])
    rec = {}
    last = {}
    for f in range(f0, f1 + 1):
        s.frame_set(f)
        pb = r.pose.bones
        for n in ['spine', 'chest', 'neck', 'head']:
            ang = math.degrees(pb[n].rotation_quaternion.angle)
            ang = min(ang, 360 - ang)
            d = rec.setdefault('torso.' + n, {'deg': [0, 0]})
            if ang > d['deg'][0]:
                d['deg'] = [round(ang, 1), f]
        for side in 'LR':
            for j, (p, c) in JOINTS.items():
                k = f'{j}.{side}'
                sw, tw = swing_twist(rel(r.data, pb, p + '.' + side, c + '.' + side))
                d = rec.setdefault(k, {'swing': [0, 0], 'twist': [999, -999], 'twist_step': [0, 0]})
                if sw > d['swing'][0]:
                    d['swing'] = [round(sw, 1), f]
                d['twist'] = [round(min(d['twist'][0], tw), 1), round(max(d['twist'][1], tw), 1)]
                if k in last and abs(tw - last[k]) > d['twist_step'][0]:
                    d['twist_step'] = [round(abs(tw - last[k]), 1), f]
                last[k] = tw
            sh, el, wr = pb['upper_arm.' + side].head, pb['forearm.' + side].head, pb['hand.' + side].head
            u = (wr - sh).normalized()
            n = (el - sh) - u * (el - sh).dot(u)
            sgn = 1 if side == 'L' else -1
            e = rec.setdefault('elbowdir.' + side, {'out': [], 'back': [], 'down': []})
            e['out'].append(sgn * n.x)
            e['back'].append(n.y)
            e['down'].append(-n.z)
    for k, v in rec.items():
        if k.startswith('elbowdir'):
            rec[k] = {m: [round(min(x), 3), round(max(x), 3)] for m, x in v.items()}
    idle = 'Idle' in clip
    fails = []
    for side in 'LR':
        el = rec['elbow.' + side]
        wr = rec['wrist.' + side]
        limit = LIMITS['elbow_flex_idle'] if idle else LIMITS['elbow_flex_attack']
        if el['swing'][0] > limit:
            fails.append(f"elbow.{side} bend {el['swing']}")
        if max(abs(el['twist'][0]), abs(el['twist'][1])) > LIMITS['elbow_twist']:
            fails.append(f"elbow.{side} twist {el['twist']}")
        if wr['swing'][0] > LIMITS['wrist_bend']:
            fails.append(f"wrist.{side} bend {wr['swing']}")
        if el['twist_step'][0] > LIMITS['twist_step']:
            fails.append(f"elbow.{side} twist step {el['twist_step']}")
    for n in ['spine', 'chest', 'neck', 'head']:
        if rec['torso.' + n]['deg'][0] > LIMITS['torso_bone']:
            fails.append(f"{n} twist {rec['torso.' + n]['deg']}")
    report[spec] = {'fails': fails, 'joints': rec}
    r.animation_data.action = None
json.dump(report, open(os.path.join(OUT, 'joint-limits.json'), 'w'), indent=1)
for k, v in report.items():
    print('AUDIT', k, 'PASS' if not v['fails'] else v['fails'])


def tile(s, cam, focus, d):
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


for label, clip in clips:
    s = bpy.data.scenes['ANIM_REVIEW_' + clip]
    bpy.context.window.scene = s
    s.render.resolution_x, s.render.resolution_y = 380, 480
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = 'PNG'
    other = 'Sister' if label == 'Brother' else 'Brother'
    for o in s.collection.all_objects:
        if o and ('_' + label in o.name):
            o.hide_render = False
        if o and ('_' + other in o.name or o.name.startswith(('Label_', 'Title_'))):
            o.hide_render = True
    rig = bpy.data.objects[f'REVIEW_{clip}_{label}_Rig']
    cam = s.camera
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 2.3 if clip.startswith('Spear') else 2.2 if clip == 'TakeDamage' else 2.0
    n = 8 if 'Idle' not in clip else 3
    fs = [round(s.frame_start + i * (s.frame_end - s.frame_start) / (n - 1)) for i in range(n)]
    if clip == 'SwordSlash':
        fs = [1, 7, 13, 16, 19, 22, 27, 36]
    elif clip == 'SpearThrust':
        fs = [1, 5, 8, 11, 13, 16, 20, 26]
    elif clip == 'TakeDamage':
        fs = [1, 4, 9, 13, 18, 23, 28, 34]
    rows = []
    for d in [(0, -3, .25), (-3, 0, .25), (-2.1, 2.1, .4)]:
        row = []
        for f in fs:
            s.frame_set(f)
            focus = rig.matrix_world @ Vector((0, 0 if clip == 'TakeDamage' else rig.pose.bones['pelvis'].matrix.translation.y, .95 if clip == 'TakeDamage' else 1.05))
            row.append(tile(s, cam, focus, d))
        rows.append(np.hstack(row))
    sheet = np.vstack(rows[::-1])
    H, W, _ = sheet.shape
    out = bpy.data.images.new(clip, W, H, alpha=True)
    out.pixels = sheet.ravel().tolist()
    out.filepath_raw = os.path.join(OUT, f'{label}-{clip}.png')
    out.file_format = 'PNG'
    out.save()
print('REVIEW_DONE')
