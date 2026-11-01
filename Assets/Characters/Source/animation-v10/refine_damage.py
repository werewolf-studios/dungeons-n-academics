# Rebuilds TakeDamage: a two-frame hit from the front on the existing event frame, a brief hold, a stagger
# step back, a teetering off-balance beat and a quick catch. Starts and ends on the action's first-frame
# pose so it blends with Idle. Exec with LABELS and OLD set, e.g. LABELS=['Brother'].
import bpy, math
from mathutils import Vector, Matrix, Quaternion
ROOT = 'D:/GodotProjects/dungeons-n-academics'
exec(compile(open(ROOT + '/Assets/Characters/Source/animation-v10/armlib.py').read(), 'armlib', 'exec'))
NEW = '_v17'
LENGTH = 37
# frame, pelvis back, down, then forward pitch of pelvis, spine, chest, neck, head, chest yaw,
# right foot back, pelvis toward character-left, chest roll toward character-left, flat
BODY = [
    (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, True),
    (2, .04, .015, 2, 3, 4, 0, -4, 1, 0, 0, 0, False),
    (3, .11, .04, 2, 6, 8, -2, -8, 4, 0, 0, 0, False),
    (4, .15, .065, 3, 9, 13, -4, -5, 8, 0, 0, 0, False),
    (6, .165, .07, 3, 10, 14, -5, -8, 9, .02, 0, 0, False),
    (9, .19, .065, 3, 8, 11, -4, -6, 7, .16, -.01, -1, False),
    (13, .21, .06, 1, 0, -4, -2, 2, 5, .18, -.03, -4, False),
    (18, .20, .05, 2, 6, 10, -3, -5, 3, .18, .02, 5, False),
    (23, .17, .055, 2, 3, 3, -1, -2, -2, .18, -.02, -4, False),
    (28, .13, .05, 1, 4, 6, -1, -2, 1, .17, .01, 2, False),
    (33, .04, .02, 0, 1, 2, 0, -1, 0, .03, 0, 0, False),
    (LENGTH + 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, True),
]
# frame, left arm (out, forward, down), right arm (out, forward, down), flat.
# Thrown out and low on the hit, then spread and alternating for balance while he teeters.
ARMS_KEYS = [
    (4, (.55, .30, .75), (.45, .40, .75), False),
    (6, (.60, .25, .72), (.50, .30, .78), False),
    (9, (.50, .10, .82), (.46, .15, .82), False),
    (13, (.68, .22, .66), (.62, .28, .70), False),
    (18, (.75, .10, .60), (.60, .00, .75), False),
    (23, (.60, .05, .75), (.72, .10, .62), False),
    (28, (.48, .05, .85), (.50, .08, .84), False),
]
# Degrees the tunic hem tips back at full crouch, to keep it clear of the hips.
HEM_TILT = {'Brother': 0, 'Sister': 7}
ARM_BONES = [n + '.' + s for s in 'LR' for n in ['upper_arm', 'forearm', 'hand']]


def smooth(a, b, t):
    t = max(0, min(1, (t - a) / (b - a)))
    return t * t * (3 - 2 * t)


def tip(rig, name, degrees, axis):
    pb = rig.pose.bones[name]
    head = pb.matrix.translation.copy()
    pb.matrix = Matrix.Translation(head) @ Matrix.Rotation(math.radians(degrees), 4, axis) @ Matrix.Translation(-head) @ pb.matrix
    bpy.context.view_layer.update()


def aim(arms, name, head, tail):
    b = arms.rig.data.bones[name]
    r = b.matrix_local.to_quaternion()
    q = (r @ Vector((0, 1, 0))).rotation_difference((tail - head).normalized()) @ r
    arms.put(name, q.to_matrix(), head)


def leg(arms, side, ankle, foot_rot):
    la = arms.rig.data.bones['thigh.' + side].length
    lb = arms.rig.data.bones['shin.' + side].length
    root = arms.base('thigh.' + side).translation
    v = ankle - root
    d = min(v.length, la + lb - .001)
    u = v.normalized()
    n = orth(Vector((ankle.x, -1, .45)) - root, u)
    along = (la * la - lb * lb + d * d) / (2 * d)
    knee = root + u * along + n * math.sqrt(max(0, la * la - along * along))
    end = root + u * d
    aim(arms, 'thigh.' + side, root, knee)
    aim(arms, 'shin.' + side, knee, end)
    arms.put('foot.' + side, foot_rot, end)
    return (ankle - end).length


def solve_from_idle(arms, side, idle, wrist, pole, flex):
    """Swing the idle arm onto the solved positions with minimal rotation, so roll and bend stay continuous."""
    root, elbow, end, u, f = arms.bend(side, wrist, pole)
    Ru = idle['u'].rotation_difference(u).to_matrix() @ idle['Ru']
    Rf = idle['f'].rotation_difference(f).to_matrix() @ idle['Rf']
    sgn = 1 if side == 'L' else -1
    R = Rf @ idle['hand_rel'] @ Quaternion((0, 0, 1), math.radians(sgn * flex)).to_matrix()
    arms.put('upper_arm.' + side, Ru, root)
    arms.put('forearm.' + side, Rf, elbow)
    arms.put('hand.' + side, R, end)


report = {}
for label in LABELS:
    s = bpy.data.scenes[label + '_Animation_v1']
    bpy.context.window.scene = s
    rig, a = install(label, 'TakeDamage', OLD[label], label + '_TakeDamage' + NEW)
    arms = Arms(rig)
    s.frame_set(1)
    bpy.context.view_layer.update()
    pb = rig.pose.bones
    pelvis0 = pb['pelvis'].matrix.translation.copy()
    feet = {side: pb['foot.' + side].matrix.copy() for side in 'LR'}
    reach = arms.rest['R']['la'] + arms.rest['R']['lb']
    idle = {}
    rows = {}
    poles = {}
    for side, column in (('L', 1), ('R', 2)):
        sgn = 1 if side == 'L' else -1
        sh, el, wr = [pb[n + '.' + side].matrix.translation.copy() for n in ['upper_arm', 'forearm', 'hand']]
        Ru, Rf, Rh = [pb[n + '.' + side].matrix.to_3x3() for n in ['upper_arm', 'forearm', 'hand']]
        idle[side] = dict(Ru=Ru, Rf=Rf, u=(el - sh).normalized(), f=(wr - el).normalized(), hand_rel=Rf.inverted() @ Rh)
        line = (wr - sh).normalized()
        idle_pole = ((el - sh) - line * (el - sh).dot(line)).normalized()
        balance = Vector((sgn * .35, .85, -.20)).normalized()
        poles[side] = [(1, idle_pole, True), (4, balance, False), (33, balance, False), (LENGTH + 1, idle_pole, True)]
        out = [(1, wr - sh, True)]
        for r in ARMS_KEYS:
            o, fwd, d = r[column]
            out.append((r[0], Vector((sgn * o, -fwd, -d)).normalized() * reach * .93, r[3]))
        out.append((LENGTH + 1, wr - sh, True))
        rows[side] = out
    keep = [b.name for b in rig.data.bones]
    prev = {}
    foot_error = 0
    columns = range(1, 12)
    for f in range(1, LENGTH + 2):
        s.frame_set(1)
        bpy.context.view_layer.update()
        c = [hermite([(r[0], Vector((r[i], 0)), r[-1]) for r in BODY], f)[0] for i in columns]
        back, down, p_pelvis, p_spine, p_chest, p_neck, p_head, yaw, step, side_shift, roll = c
        M = pb['pelvis'].matrix.copy()
        M.translation = pelvis0 + Vector((side_shift, back, -down))
        pb['pelvis'].matrix = M
        bpy.context.view_layer.update()
        for name, deg in [('pelvis', p_pelvis), ('spine', p_spine), ('chest', p_chest), ('neck', p_neck), ('head', p_head)]:
            tip(rig, name, deg, 'X')
        for name in ['tunic.L', 'tunic.R']:
            tip(rig, name, HEM_TILT[label] * min(1, down / .065), 'X')
        tip(rig, 'spine', roll * .4, 'Y')
        tip(rig, 'chest', roll * .6, 'Y')
        tip(rig, 'neck', -roll * .3, 'Y')
        tip(rig, 'head', -roll * .3, 'Y')
        spin(rig, 'spine', yaw * .45)
        spin(rig, 'chest', yaw * .55)
        spin(rig, 'neck', -yaw * .3)
        spin(rig, 'head', -yaw * .3)
        arms.snapshot()
        lift = .05 * math.sin(math.pi * smooth(5, 9, f)) + .03 * math.sin(math.pi * smooth(28, 33, f))
        for side in 'LR':
            target = feet[side].translation.copy()
            if side == 'R':
                target += Vector((0, step, lift))
            foot_error = max(foot_error, leg(arms, side, target, feet[side].to_3x3()))
        flex = 12 * smooth(1, 4, f) * (1 - smooth(30, LENGTH + 1, f))
        for side in 'LR':
            shoulder = arms.base('upper_arm.' + side).translation
            solve_from_idle(arms, side, idle[side], shoulder + hermite(rows[side], f), hermite(poles[side], f), flex)
        bpy.context.view_layer.update()
        key_bones(rig, keep, f, prev)
    linear(a)
    strip = rig.animation_data.nla_tracks['TakeDamage'].strips[0]
    strip.action_frame_end = LENGTH + 1
    strip.frame_end = LENGTH + 1
    bpy.data.scenes['ANIM_REVIEW_TakeDamage'].frame_end = LENGTH
    report[label] = {'max_foot_error_m': round(foot_error, 4)}
    rig.animation_data.action = bpy.data.actions['Brother_Idle_v13' if label == 'Brother' else 'Sister_Idle_v3']
    s.frame_set(1)
result = report
