# Read-only: measures hand skin against the weapon shaft, in hand-bone space, on the evaluated mesh.
# blender --background FILE --python hand_clearance.py -- OUT_JSON Clip.Frame.Weapon [...]
import bpy, json, math, sys
from mathutils import Vector
args = sys.argv[sys.argv.index('--') + 1:]
out_path = args[0]
report = {}
for spec in args[1:]:
    clip, frame, weapon = spec.split('.')
    s = bpy.data.scenes['ANIM_REVIEW_' + clip]
    bpy.context.window.scene = s
    s.frame_set(int(frame))
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    for label in ['Brother', 'Sister']:
        rig = bpy.data.objects[f'REVIEW_{clip}_{label}_Rig']
        mesh_ob = bpy.data.objects[f'REVIEW_{clip}_{label}_Mesh']
        wpn = bpy.data.objects[f'REVIEW_{clip}_{label}_{weapon}']
        ev = mesh_ob.evaluated_get(dg)
        me = ev.to_mesh()
        wm = ev.matrix_world
        names = {g.index: g.name for g in mesh_ob.vertex_groups}
        verts = {}
        for v in mesh_ob.data.vertices:
            for side in 'LR':
                w = sum(g.weight for g in v.groups if names.get(g.group, '') in
                        (f'hand.{side}', f'fingers_base.{side}', f'fingers_tip.{side}', f'thumb.{side}'))
                if w > .5:
                    verts.setdefault(side, []).append(v.index)
        wev = wpn.evaluated_get(dg)
        wme = wev.to_mesh()
        for side in 'LR':
            H = (rig.matrix_world @ rig.pose.bones['hand.' + side].matrix).inverted()
            P = [H @ (wm @ me.vertices[i].co) for i in verts.get(side, [])]
            W = [H @ (wev.matrix_world @ v.co) for v in wme.vertices]
            # Shaft direction in hand space from the weapon's long axis, then the section around the hand.
            axis = (H.to_3x3() @ wev.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
            org = H @ wev.matrix_world.translation
            # Cross-section of the weapon where its long axis meets the hand, from mesh edges.
            cz = sum((p - org).dot(axis) for p in P) / len(P)
            local_axis = Vector((0, 0, 1))
            near = []
            for e in wme.edges:
                a, b = wme.vertices[e.vertices[0]].co, wme.vertices[e.vertices[1]].co
                if (a.z - cz) * (b.z - cz) < 0:
                    near.append(H @ (wev.matrix_world @ a.lerp(b, (cz - a.z) / (b.z - a.z))))
            c = sum(near, Vector()) / len(near)
            radius = max((p - c).length for p in near)
            pen = []
            for p in P:
                t = (p - c).dot(axis)
                d = ((p - c) - axis * t).length
                pen.append(d)
            inside = sum(1 for d in pen if d < radius)
            # Empty-hole search: best shaft centre in the hand's x-y plane for this skin.
            best = None
            pts = [(p.x, p.y) for p in P if abs(p.z) < .05]
            for ix in range(-40, 41, 2):
                for iy in range(0, 151, 2):
                    x, y = ix / 1000, iy / 1000
                    ds = [math.hypot(a - x, b - y) for a, b in pts]
                    bad = sum(1 for d in ds if d < radius)
                    near_skin = sum(1 for d in ds if d < radius + .012)
                    score = (bad, -near_skin)
                    if best is None or score < best[0]:
                        best = (score, x, y)
            report[f'{label}.{clip}.{frame}.{side}'] = {
                'hand_verts': len(P), 'shaft_radius': round(radius, 4), 'shaft_centre_hand_xy': [round(c.x, 4), round(c.y, 4)],
                'skin_inside_shaft': inside, 'deepest_mm': round((radius - min(pen)) * 1000, 1),
                'best_centre_xy': [best[1], best[2]], 'best_inside': best[0][0], 'best_contact': -best[0][1],
                'skin_x_range': [round(min(p.x for p in P), 3), round(max(p.x for p in P), 3)],
                'skin_y_range': [round(min(p.y for p in P), 3), round(max(p.y for p in P), 3)],
                'skin_z_range': [round(min(p.z for p in P), 3), round(max(p.z for p in P), 3)]}
        ev.to_mesh_clear()
        wev.to_mesh_clear()
json.dump(report, open(out_path, 'w'), indent=1)
for k, v in report.items():
    print('CLEAR', k, v)
print('CLEARANCE_DONE')
