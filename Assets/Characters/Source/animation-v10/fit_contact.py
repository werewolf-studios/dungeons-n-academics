# Read-only search for a shaft seat that touches the hand: small palm and fingertip gaps, shallow overlap.
# blender --background FILE --python fit_contact.py -- OUT_JSON
import bpy, json, math, sys
from mathutils import Quaternion
out_path = sys.argv[sys.argv.index('--') + 1]
RADIUS = .0426
s = bpy.data.scenes['ANIM_REVIEW_SpearIdle']
bpy.context.window.scene = s
s.frame_set(1)
BASE = [20, 30, 40, 50, 60, 70, 80]
TIP = [20, 35, 50, 65]
report = {}


def low(values, fraction):
    values = sorted(values)
    return values[int(len(values) * fraction)]


for label in ['Brother', 'Sister']:
    rig = bpy.data.objects[f'REVIEW_SpearIdle_{label}_Rig']
    ob = bpy.data.objects[f'REVIEW_SpearIdle_{label}_Mesh']
    names = {g.index: g.name for g in ob.vertex_groups}
    groups = {side: {'palm': [], 'base': [], 'tip': []} for side in 'LR'}
    for v in ob.data.vertices:
        for side in 'LR':
            w = {'palm': 0, 'base': 0, 'tip': 0}
            for g in v.groups:
                n = names.get(g.group, '')
                if n == 'hand.' + side:
                    w['palm'] += g.weight
                elif n == 'fingers_base.' + side:
                    w['base'] += g.weight
                elif n == 'fingers_tip.' + side:
                    w['tip'] += g.weight
            top = max(w, key=w.get)
            if w[top] > .5:
                groups[side][top].append(v.index)
    results = {'L': [], 'R': []}
    for base in BASE:
        for tip in TIP:
            for side, sgn in (('L', 1), ('R', -1)):
                rig.pose.bones['fingers_base.' + side].rotation_quaternion = Quaternion((0, 0, 1), math.radians(sgn * base))
                rig.pose.bones['fingers_tip.' + side].rotation_quaternion = Quaternion((0, 0, 1), math.radians(sgn * tip))
            bpy.context.view_layer.update()
            ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
            me = ev.to_mesh()
            for side in 'LR':
                H = (rig.matrix_world @ rig.pose.bones['hand.' + side].matrix).inverted() @ ev.matrix_world
                m = 1 if side == 'R' else -1
                pts = {k: [(p.x * m, p.y) for p in (H @ me.vertices[i].co for i in idx) if abs(p.z) < .09] for k, idx in groups[side].items()}
                # Palm verts on the palm side only; the back of the hand can never touch.
                pts['palm'] = [p for p in pts['palm'] if p[1] > .02]
                best = None
                for ix in range(30, 126, 5):
                    for iy in range(40, 131, 5):
                        x, y = ix / 1000, iy / 1000
                        d = {k: [math.hypot(a - x, b - y) - RADIUS for a, b in v] for k, v in pts.items()}
                        every = d['palm'] + d['base'] + d['tip']
                        deep = max(0, -min(every))
                        inside = sum(1 for e in every if e < -.004)
                        palm_gap = max(0, low(d['palm'], .03))
                        tip_gap = max(0, low(d['tip'], .05))
                        base_gap = max(0, low(d['base'], .05))
                        # Tips reaching past the shaft centre read as wrapping around it.
                        wrap = max(a for a, b in pts['tip'])
                        over = max(0, x - wrap)
                        cost = palm_gap * 2 + tip_gap * 2 + base_gap + deep * 1.2 + inside * .00004 + over * .5
                        if best is None or cost < best['cost']:
                            best = dict(cost=round(cost, 4), x=x, y=y, palm_gap_mm=round(palm_gap * 1000, 1), base_gap_mm=round(base_gap * 1000, 1),
                                        tip_gap_mm=round(tip_gap * 1000, 1), deep_mm=round(deep * 1000, 1), inside=inside, wrap_past_centre_mm=round((wrap - x) * 1000, 1))
                results[side].append(dict(base=base, tip=tip, **best))
            ev.to_mesh_clear()
    report[label] = {}
    for side in 'LR':
        results[side].sort(key=lambda r: r['cost'])
        report[label][side] = results[side][:5]
        print('FIT', label, side)
        for r in results[side][:5]:
            print('   ', r)
json.dump(report, open(out_path, 'w'), indent=1)
print('FIT_DONE')
