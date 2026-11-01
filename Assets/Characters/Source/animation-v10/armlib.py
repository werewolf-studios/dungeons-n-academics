# Anatomical arm solver for weapon and reaction clips.
# Elbows flex about a consistent hinge, and forearm twist is shared with the wrist
# because the rig has no twist bones. Rig faces -Y, +X is character-left, +Z is up.
import bpy, math
from mathutils import Vector, Matrix, Quaternion
ROOT = 'D:/GodotProjects/dungeons-n-academics'
BASE = ROOT + '/Assets/Characters/Source/animation-v10'
FORWARD = Vector((0, -1, 0))
BROTHER_SHOULDER = Vector((-.155, 0, 1.32))
BROTHER_REACH = .515
GRIP_OFFSET = {'R': Vector((.025, .085, 0)), 'L': Vector((-.025, .085, 0))}


def frame_map(a, b, a2, b2):
    A = Matrix((a, b, a.cross(b))).transposed()
    B = Matrix((a2, b2, a2.cross(b2))).transposed()
    return B @ A.transposed()


def orth(v, axis):
    return (v - axis * v.dot(axis)).normalized()


def hermite(keys, f):
    """Nonuniform Catmull-Rom. keys: [(frame, value, flat)], flat keys ease to zero velocity."""
    fs = [k[0] for k in keys]
    if f <= fs[0]:
        return keys[0][1]
    if f >= fs[-1]:
        return keys[-1][1]
    i = next(n for n in range(len(fs) - 1) if fs[n] <= f <= fs[n + 1])

    def tan(n):
        if keys[n][2] or n == 0 or n == len(keys) - 1:
            return keys[n][1] * 0
        return (keys[n + 1][1] - keys[n - 1][1]) / (fs[n + 1] - fs[n - 1])
    h = fs[i + 1] - fs[i]
    t = (f - fs[i]) / h
    return (2 * t**3 - 3 * t**2 + 1) * keys[i][1] + (t**3 - 2 * t**2 + t) * h * tan(i) \
        + (-2 * t**3 + 3 * t**2) * keys[i + 1][1] + (t**3 - t**2) * h * tan(i + 1)


def channel(rows, column, f):
    return hermite([(r[0], Vector(r[column]), r[-1]) for r in rows], f)


class Arms:
    def __init__(self, rig):
        self.rig = rig
        self.m = {}
        self.rest = {}
        for side in 'LR':
            B = {n: rig.data.bones[n + '.' + side] for n in ['upper_arm', 'forearm', 'hand']}
            ru, rf, rh = [B[n].matrix_local.to_3x3() for n in ['upper_arm', 'forearm', 'hand']]
            u0 = ru.col[1].normalized()
            f0 = rf.col[1].normalized()
            h0 = u0.cross(FORWARD).normalized()
            self.rest[side] = dict(ru=ru, rf=rf, rh=rh, u0=u0, f0=f0, h0=h0, hf0=orth(h0, f0),
                                   hand_rel=rf.inverted() @ rh, la=B['upper_arm'].length, lb=B['forearm'].length)
        arm = self.rest['R']
        self.reach = arm['la'] + arm['lb']
        self.shoulder = rig.data.bones['upper_arm.R'].head_local.copy()

    def fit(self, g):
        """Fit a Brother-space right-hand target to this character's shoulder and arm length."""
        return self.shoulder + (Vector(g) - BROTHER_SHOULDER) * (self.reach / BROTHER_REACH)

    def snapshot(self):
        self.m = {b.name: b.matrix.copy() for b in self.rig.pose.bones}

    def base(self, name):
        b = self.rig.data.bones[name]
        return self.m[b.parent.name] @ b.parent.matrix_local.inverted() @ b.matrix_local if b.parent else b.matrix_local.copy()

    def put(self, name, R, pos):
        M = R.to_4x4()
        M.translation = pos
        self.rig.pose.bones[name].matrix_basis = self.base(name).inverted() @ M
        self.m[name] = M

    def bend(self, side, wrist, pole):
        r = self.rest[side]
        root = self.base('upper_arm.' + side).translation
        v = Vector(wrist) - root
        d = min(v.length, r['la'] + r['lb'] - .001)
        n = orth(Vector(pole).normalized(), v.normalized())
        along = (r['la']**2 - r['lb']**2 + d**2) / (2 * d)
        elbow = root + v.normalized() * along + n * math.sqrt(max(0, r['la']**2 - along**2))
        end = root + v.normalized() * d
        u = (elbow - root).normalized()
        f = (end - elbow).normalized()
        return root, elbow, end, u, f

    def frames(self, side, u, f):
        r = self.rest[side]
        hinge = u.cross(f).normalized()
        Ru = frame_map(r['u0'], r['h0'], u, hinge) @ r['ru']
        Rf = frame_map(r['f0'], r['hf0'], f, hinge) @ r['rf']
        return Ru, Rf

    def solve_grip(self, side, grip, blade, pole, thumb_to_blade=True, share=.5, limit=40, prefer=None, seat=None):
        """Hammer-grip a shaft. The fingers wrap the shaft nearest the forearm's own direction.
        prefer biases the finger direction, which keeps the grip stable when the forearm nears the shaft line.
        seat is the shaft centre in hand space as (palm-side distance, along the hand)."""
        z = (-Vector(blade) if thumb_to_blade else Vector(blade)).normalized()
        offset = GRIP_OFFSET[side] if seat is None else Vector((seat[0] if side == 'R' else -seat[0], seat[1], 0))
        bias = Vector(prefer) if prefer is not None else Vector((0, 0, 0))
        wrist = Vector(grip) - Vector((0, 0, 0))
        for _ in range(6):
            root, elbow, end, u, f = self.bend(side, wrist, pole)
            y = orth(f + bias, z)
            R = Matrix((y.cross(z).normalized(), y, z)).transposed()
            wrist = Vector(grip) - R @ offset
        root, elbow, end, u, f = self.bend(side, wrist, pole)
        y = orth(f + bias, z)
        R = Matrix((y.cross(z).normalized(), y, z)).transposed()
        Ru, Rf = self.frames(side, u, f)
        W = (Rf.inverted() @ R @ self.rest[side]['hand_rel'].inverted()).to_quaternion()
        total = 2 * math.degrees(math.atan2(W.y, W.w))
        total = (total + 180) % 360 - 180
        tau = max(-limit, min(limit, total * share))
        Rf = Rf @ Quaternion((0, 1, 0), math.radians(tau)).to_matrix()
        self.put('upper_arm.' + side, Ru, root)
        self.put('forearm.' + side, Rf, elbow)
        self.put('hand.' + side, R, end)
        return {'twist_total': total, 'twist_forearm': tau, 'grip_error': (end + R @ offset - Vector(grip)).length}

    def solve_relaxed(self, side, wrist, pole, flex=8, twist=0):
        root, elbow, end, u, f = self.bend(side, wrist, pole)
        Ru, Rf = self.frames(side, u, f)
        Rf = Rf @ Quaternion((0, 1, 0), math.radians(twist)).to_matrix()
        sgn = 1 if side == 'L' else -1
        R = Rf @ self.rest[side]['hand_rel'] @ Quaternion((0, 0, 1), math.radians(sgn * flex)).to_matrix()
        self.put('upper_arm.' + side, Ru, root)
        self.put('forearm.' + side, Rf, elbow)
        self.put('hand.' + side, R, end)


def yaw_of(rig, name):
    """World yaw of a bone relative to its rest orientation, positive turns the right shoulder forward."""
    pb = rig.pose.bones[name]
    x = pb.matrix.to_3x3().col[0]
    x0 = rig.data.bones[name].matrix_local.to_3x3().col[0]
    # Wrapped to +/-180, since a full-turn error split across two bones cancels out and hides itself.
    return (math.degrees(math.atan2(x.y, x.x) - math.atan2(x0.y, x0.x)) + 180) % 360 - 180


def spin(rig, name, degrees):
    pb = rig.pose.bones[name]
    head = pb.matrix.translation.copy()
    M = pb.matrix.copy()
    M = Matrix.Translation(head) @ Matrix.Rotation(math.radians(degrees), 4, 'Z') @ Matrix.Translation(-head) @ M
    pb.matrix = M
    bpy.context.view_layer.update()


def set_torso_yaw(rig, chest_target, head_target):
    d = (chest_target - yaw_of(rig, 'chest') + 180) % 360 - 180
    spin(rig, 'spine', d * .45)
    spin(rig, 'chest', d * .55)
    d = (head_target - yaw_of(rig, 'head') + 180) % 360 - 180
    spin(rig, 'neck', d * .4)
    spin(rig, 'head', d * .6)


def key_bones(rig, names, f, previous):
    for n in names:
        b = rig.pose.bones[n]
        q = b.rotation_quaternion.copy()
        if n in previous and q.dot(previous[n]) < 0:
            q.negate()
            b.rotation_quaternion = q
        previous[n] = q.copy()
        b.keyframe_insert('rotation_quaternion', frame=f, group=n)
        b.keyframe_insert('location', frame=f, group=n)


def install(label, clip, old_name, new_name):
    """Copy an action, make it current on the rig, and point its NLA strip and review rig at it."""
    rig = bpy.data.objects[label + '_AnimRig_v1']
    old = bpy.data.actions[old_name]
    # Always rebuild from the source action so reruns cannot stack up on a previous result.
    rig.animation_data.action = old
    rig.animation_data.nla_tracks[clip].strips[0].action = old
    review_rig = bpy.data.objects['REVIEW_' + clip + '_' + label + '_Rig']
    review_rig.animation_data.action = old
    stale = bpy.data.actions.get(new_name)
    if stale:
        bpy.data.actions.remove(stale)
    a = old.copy()
    a.name = new_name
    a.use_fake_user = True
    rig.animation_data.action = a
    if a.slots:
        rig.animation_data.action_slot = a.slots[0]
    strip = rig.animation_data.nla_tracks[clip].strips[0]
    strip.action = a
    review = bpy.data.objects['REVIEW_' + clip + '_' + label + '_Rig']
    review.animation_data.action = a
    if a.slots:
        review.animation_data.action_slot = a.slots[0]
    return rig, a


def linear(a):
    for layer in a.layers:
        for st in layer.strips:
            for bag in st.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:
                        k.interpolation = 'LINEAR'
                    fc.update()
