# Rebuilds the arms and upper-body turn of SpearIdle and SpearThrust. Legs and pelvis keep their
# existing motion. Both thumbs point toward the tip, as with the sword, so the spear is flipped in
# the hand. Exec with LABELS and OLD set, e.g. LABELS=['Brother'].
import bpy, json, math
from mathutils import Vector, Quaternion
ROOT = 'D:/GodotProjects/dungeons-n-academics'
exec(compile(open(ROOT + '/Assets/Characters/Source/animation-v10/armlib.py').read(), 'armlib', 'exec'))
TORSO = ['spine', 'chest', 'neck', 'head']
ARMS = [n + '.' + s for s in 'LR' for n in ['upper_arm', 'forearm', 'hand']]
NEW = '_v17'
# Brother-space targets, fitted per character. Rear hand at the right hip, shaft up on the diagonal.
GUARD_G = (-.24, -.18, .99)
GUARD_A = (-.03, -.74, .67)
GUARD_S = .27
GUARD_PR = (-.55, .35, -.75)
GUARD_PL = (.55, .10, -.85)
GUARD_YAW = -32
GUARD_ROW = (1, GUARD_G, GUARD_A, GUARD_PR, GUARD_PL, GUARD_S, GUARD_YAW, -18, True)
# frame, rear grip, shaft axis, right pole, left pole, hand separation, chest yaw, head yaw, flat
THRUST = [
    GUARD_ROW,
    (6, (-.27, -.06, 1.02), (.08, -.86, .50), (-.75, .35, -.55), (.58, .10, -.82), .29, -36, -20, True),
    (10, (-.22, -.22, 1.03), (.12, -.90, .40), (-.85, .20, -.48), (.52, .08, -.85), .22, -30, -17, False),
    (13, (-.15, -.24, 1.03), (.12, -.93, .34), (-.82, .10, -.55), (.48, .05, -.87), .17, -28, -15, True),
    (16, (-.16, -.23, 1.02), (.14, -.92, .36), (-.82, .12, -.55), (.48, .06, -.87), .18, -28, -15, False),
    (21, (-.22, -.22, 1.01), (.05, -.82, .57), (-.70, .28, -.62), (.52, .08, -.85), .24, -30, -17, False),
    (27,) + GUARD_ROW[1:],
]
# Shaft seat in hand space (palm-side distance, along the hand) and finger curl, from fit_contact.py.
GRIP = {'Brother': dict(seat=(.08, .07), base=50, tip=20, front=(.08, .07), front_base=50, front_tip=20),
        'Sister': dict(seat=(.07, .065), base=60, tip=20, front=(.07, .065), front_base=60, front_tip=20)}
FINGERS = [n + '.' + s for s in 'LR' for n in ['fingers_base', 'fingers_tip', 'thumb']]
report = {}


def scalar(rows, column, f):
    return hermite([(r[0], Vector((r[column], 0)), r[-1]) for r in rows], f)[0]


for label in LABELS:
    s = bpy.data.scenes[label + '_Animation_v1']
    bpy.context.window.scene = s
    report[label] = {}
    for name in [label + '_Anim_Spear', 'REVIEW_SpearIdle_' + label + '_Spear', 'REVIEW_SpearThrust_' + label + '_Spear']:
        o = bpy.data.objects[name]
        o.rotation_mode = 'QUATERNION'
        o.rotation_quaternion = Quaternion((1, 0, 0), math.pi)
        hand = bpy.data.objects[label + '_AnimRig_v1'].data.bones['hand.R'].length
        o.location = (GRIP[label]['seat'][0], GRIP[label]['seat'][1] - hand, 0)
    for clip, length in [('SpearIdle', 48), ('SpearThrust', 26)]:
        rig, a = install(label, clip, OLD[label][clip], label + '_' + clip + NEW)
        arms = Arms(rig)
        s.frame_set(1)
        bpy.context.view_layer.update()
        pelvis0 = rig.pose.bones['pelvis'].matrix.translation.copy()
        prev = {}
        twist = {'R': [], 'L': []}
        err = {'R': [], 'L': []}
        for f in range(1, length + 2):
            s.frame_set(f)
            bpy.context.view_layer.update()
            t = (f - 1) / length
            shift = rig.pose.bones['pelvis'].matrix.translation - pelvis0
            if clip == 'SpearIdle':
                breath = math.sin(2 * math.pi * t)
                sway = math.sin(2 * math.pi * t + .9)
                set_torso_yaw(rig, (GUARD_YAW + .6 * sway) * GRIP[label].get('turn', 1), -18 * GRIP[label].get('turn', 1) + .4 * breath)
                g = Vector(GUARD_G) + Vector((0, -.004 * sway, .005 * breath))
                axis = Vector(GUARD_A) + Vector((.006 * sway, 0, .006 * breath))
                pr, pl, sep = Vector(GUARD_PR), Vector(GUARD_PL), GUARD_S
            else:
                set_torso_yaw(rig, scalar(THRUST, 6, f) * GRIP[label].get('turn', 1), scalar(THRUST, 7, f) * GRIP[label].get('turn', 1))
                g = channel(THRUST, 1, f)
                axis = channel(THRUST, 2, f)
                pr = channel(THRUST, 3, f)
                pl = channel(THRUST, 4, f)
                sep = scalar(THRUST, 5, f)
            for side, sgn in (('L', 1), ('R', -1)):
                curl = GRIP[label]
                rig.pose.bones['fingers_base.' + side].rotation_quaternion = Quaternion((0, 0, 1), math.radians(sgn * (curl['base'] if side == 'R' else curl['front_base'])))
                rig.pose.bones['fingers_tip.' + side].rotation_quaternion = Quaternion((0, 0, 1), math.radians(sgn * (curl['tip'] if side == 'R' else curl['front_tip'])))
                rig.pose.bones['thumb.' + side].rotation_quaternion = Quaternion((1, 0, 0), math.radians(10)) @ Quaternion((0, 1, 0), math.radians(sgn * 12.5)) @ Quaternion((0, 0, 1), math.radians(sgn * 7.5))
            arms.snapshot()
            axis = axis.normalized()
            rear = arms.fit(g) + shift
            front = rear + axis * sep * (arms.reach / BROTHER_REACH)
            for side, grip, pole in [('R', rear, pr), ('L', front, pl)]:
                if side == 'L':
                    # Follow where the right hand actually put the shaft, in case it hit full reach.
                    seat = GRIP[label]['seat']
                    held = arms.m['hand.R'] @ Vector((seat[0], seat[1], 0))
                    grip = held + axis * sep * (arms.reach / BROTHER_REACH)
                info = arms.solve_grip(side, grip, axis, pole, prefer=(.08, 0, -.30) if side == 'R' else None, seat=GRIP[label]['seat'] if side == 'R' else GRIP[label]['front'])
                twist[side].append(round(info['twist_total'], 1))
                err[side].append(round(info['grip_error'], 4))
            bpy.context.view_layer.update()
            key_bones(rig, TORSO + ARMS + FINGERS, f, prev)
        linear(a)
        report[label][clip] = {'twist_total': twist, 'max_grip_error_m': {k: max(v) for k, v in err.items()}}
    idle = 'Brother_Idle_v13' if label == 'Brother' else 'Sister_Idle_v3'
    rig.animation_data.action = bpy.data.actions[idle]
    s.frame_set(1)
result = report
