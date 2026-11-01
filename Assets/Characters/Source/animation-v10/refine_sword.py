# Rebuilds the arms and upper-body turn of SwordIdle and SwordSlash. Legs and pelvis keep their
# existing motion. Exec with LABELS and OLD set, e.g. LABELS=['Brother'].
import bpy, json, math
from mathutils import Vector
ROOT = 'D:/GodotProjects/dungeons-n-academics'
exec(compile(open(ROOT + '/Assets/Characters/Source/animation-v10/armlib.py').read(), 'armlib', 'exec'))
TORSO = ['spine', 'chest', 'neck', 'head']
ARMS = [n + '.' + s for s in 'LR' for n in ['upper_arm', 'forearm', 'hand']]
NEW = '_v17'
# Brother-space targets, fitted per character. Right hand at waist height with the elbow near the ribs.
GUARD_G = (-.20, -.36, 1.07)
GUARD_B = (-.22, -.45, .87)
GUARD_P = (-.25, .15, -1)
GUARD_YAW = 8
# frame, grip, blade, elbow pole, chest yaw, head yaw, left wrist (out, fwd, down) as reach fractions, flat
SLASH = [
    (1, GUARD_G, GUARD_B, GUARD_P, GUARD_YAW, 2, (.24, .12, .90), True),
    (7, (-.30, -.28, 1.28), (-.38, -.05, .92), (-.78, .12, -.62), 0, 1, (.26, .17, .88), False),
    (13, (-.44, -.18, 1.50), (-.42, .60, .68), (-.88, .15, -.45), -10, -2, (.30, .24, .82), True),
    (16, (-.38, -.40, 1.42), (-.25, .18, .95), (-.85, .10, -.52), 0, 2, (.31, .12, .86), False),
    (18, (-.22, -.52, 1.30), (.50, -.05, .86), (-.55, .12, -.82), 16, 7, (.32, -.10, .85), False),
    (19, (-.08, -.50, 1.20), (.66, -.15, .70), (-.35, .12, -.92), 24, 10, (.32, -.20, .84), False),
    (20, (0, -.47, 1.12), (.85, -.10, .35), (-.32, .13, -.94), 27, 11, (.33, -.25, .83), False),
    (22, (.06, -.42, 1.04), (.90, .15, .25), (-.30, .15, -.95), 28, 12, (.33, -.28, .82), True),
    (27, (-.08, -.36, 1.02), (.35, -.35, .85), (-.28, .15, -.95), 20, 7, (.28, -.05, .86), False),
    (37, GUARD_G, GUARD_B, GUARD_P, GUARD_YAW, 2, (.24, .12, .90), True),
]
report = {}


def left_wrist(arms, frac):
    # Hang from the shoulder rest position in character-relative terms, so proportions carry over.
    s = arms.rig.data.bones['upper_arm.L'].head_local
    out, fwd, down = frac
    v = Vector((out, -fwd, -down)).normalized() * (arms.rest['L']['la'] + arms.rest['L']['lb']) * .965
    return s + v


LEFT_POLE = (.35, .85, -.20)
for label in LABELS:
    s = bpy.data.scenes[label + '_Animation_v1']
    bpy.context.window.scene = s
    report[label] = {}
    for clip, length in [('SwordIdle', 48), ('SwordSlash', 36)]:
        rig, a = install(label, clip, OLD[label][clip], label + '_' + clip + NEW)
        arms = Arms(rig)
        s.frame_set(1)
        bpy.context.view_layer.update()
        pelvis0 = rig.pose.bones['pelvis'].matrix.translation.copy()
        prev = {}
        twist = []
        err = []
        for f in range(1, length + 2):
            s.frame_set(f)
            bpy.context.view_layer.update()
            t = (f - 1) / length
            shift = rig.pose.bones['pelvis'].matrix.translation - pelvis0
            if clip == 'SwordIdle':
                breath = math.sin(2 * math.pi * t)
                sway = math.sin(2 * math.pi * t + .9)
                set_torso_yaw(rig, GUARD_YAW + .6 * sway, 2 + .4 * breath)
                g = Vector(GUARD_G) + Vector((0, -.004 * sway, .005 * breath))
                b = Vector(GUARD_B) + Vector((.012 * sway, 0, 0))
                p = Vector(GUARD_P)
                lw = (.24, .12 + .006 * sway, .90)
            else:
                chest = hermite([(r[0], Vector((r[4], 0)), r[-1]) for r in SLASH], f)[0]
                head = hermite([(r[0], Vector((r[5], 0)), r[-1]) for r in SLASH], f)[0]
                set_torso_yaw(rig, chest, head)
                g = channel(SLASH, 1, f)
                b = channel(SLASH, 2, f)
                p = channel(SLASH, 3, f)
                lw = tuple(channel(SLASH, 6, f))
            arms.snapshot()
            info = arms.solve_grip('R', arms.fit(g) + shift, b, p)
            arms.solve_relaxed('L', left_wrist(arms, lw) + shift, LEFT_POLE)
            bpy.context.view_layer.update()
            twist.append(round(info['twist_total'], 1))
            err.append(info['grip_error'])
            key_bones(rig, TORSO + ARMS, f, prev)
        linear(a)
        report[label][clip] = {'twist_total_by_frame': twist, 'max_grip_error_m': max(err), 'worst_grip_frame': err.index(max(err)) + 1}
    idle = 'Brother_Idle_v13' if label == 'Brother' else 'Sister_Idle_v3'
    rig.animation_data.action = bpy.data.actions[idle]
    s.frame_set(1)
result = report
