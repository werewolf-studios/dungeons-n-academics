# Read-only search: where the shaft should sit in each hand and how far the fingers should curl.
# blender --background FILE --python fit_grip.py -- OUT_JSON
import bpy, json, math, statistics, sys
from mathutils import Vector, Quaternion
out_path = sys.argv[sys.argv.index('--') + 1]
s = bpy.data.scenes['ANIM_REVIEW_SpearIdle']
bpy.context.window.scene = s
s.frame_set(1)
report = {}
BASE = [10, 20, 30, 40, 50, 60]
TIP = [10, 25, 40, 55, 70]
THUMB = [0, .5, 1]


def set_curl(rig, base, tip, thumb):
    for side, sgn in (('L', 1), ('R', -1)):
        rig.pose.bones['fingers_base.' + side].rotation_quaternion = Quaternion((0, 0, 1), math.radians(sgn * base))
        rig.pose.bones['fingers_tip.' + side].rotation_quaternion = Quaternion((0, 0, 1), math.radians(sgn * tip))
        q = Quaternion((1, 0, 0), math.radians(20 * thumb)) @ Quaternion((0, 1, 0), math.radians(sgn * 25 * thumb)) @ Quaternion((0, 0, 1), math.radians(sgn * 15 * thumb))
        rig.pose.bones['thumb.' + side].rotation_quaternion = q


for label in ['Brother', 'Sister']:
    rig = bpy.data.objects[f'REVIEW_SpearIdle_{label}_Rig']
    ob = bpy.data.objects[f'REVIEW_SpearIdle_{label}_Mesh']
    wpn = bpy.data.objects[f'REVIEW_SpearIdle_{label}_Spear']
    # True shaft section from the undeformed weapon mesh, sampled along its length.
    sections = {}
    for z in [-.4, -.2, 0, .2, .4, .6]:
        pts = []
        for e in wpn.data.edges:
            a, b = wpn.data.vertices[e.vertices[0]].co, wpn.data.vertices[e.vertices[1]].co
            if (a.z - z) * (b.z - z) < 0:
                pts.append(a.lerp(b, (z - a.z) / (b.z - a.z)))
        if pts:
            c = sum(pts, Vector()) / len(pts)
            r = [(p - c).to_2d().length for p in pts]
            sections[z] = [len(pts), round(statistics.median(r), 4), round(max(r), 4)]
    radius = statistics.median([v[1] for v in sections.values()])
    names = {g.index: g.name for g in ob.vertex_groups}
    sets = {}
    for v in ob.data.vertices:
        for side in 'LR':
            w = sum(g.weight for g in v.groups if names.get(g.group, '') in (f'hand.{side}', f'fingers_base.{side}', f'fingers_tip.{side}', f'thumb.{side}'))
            if w > .5:
                sets.setdefault(side, []).append(v.index)
    results = {'L': [], 'R': []}
    for base in BASE:
        for tip in TIP:
            for thumb in THUMB:
                set_curl(rig, base, tip, thumb)
                bpy.context.view_layer.update()
                dg = bpy.context.evaluated_depsgraph_get()
                ev = ob.evaluated_get(dg)
                me = ev.to_mesh()
                for side in 'LR':
                    H = (rig.matrix_world @ rig.pose.bones['hand.' + side].matrix).inverted() @ ev.matrix_world
                    P = [H @ me.vertices[i].co for i in sets[side]]
                    mirror = 1 if side == 'R' else -1
                    pts = [(p.x * mirror, p.y) for p in P if -.09 < p.z < .09]
                    best = None
                    for ix in range(0, 131, 5):
                        for iy in range(30, 151, 5):
                            x, y = ix / 1000, iy / 1000
                            ds = [math.hypot(a - x, b - y) for a, b in pts]
                            deep = max(radius - min(ds), 0)
                            bad = sum(1 for d in ds if d < radius - .004)
                            contact = sum(1 for d in ds if radius - .004 <= d < radius + .012)
                            score = (bad, deep, -contact)
                            if best is None or score < best['score']:
                                best = {'score': score, 'x': x, 'y': y, 'bad': bad, 'deep_mm': round(deep * 1000, 1), 'contact': contact}
                    results[side].append(dict(base=base, tip=tip, thumb=thumb, **{k: best[k] for k in ['x', 'y', 'bad', 'deep_mm', 'contact']}))
                ev.to_mesh_clear()
    report[label] = {'radius': radius, 'sections': sections, 'hand_verts': {k: len(v) for k, v in sets.items()}}
    for side in 'LR':
        results[side].sort(key=lambda r: (r['bad'], r['deep_mm'], -r['contact']))
        report[label][side] = results[side][:6]
        print('FIT', label, side, 'radius', radius, sections if side == 'L' else '')
        for row in results[side][:6]:
            print('   ', row)
json.dump(report, open(out_path, 'w'), indent=1)
print('FIT_DONE')
