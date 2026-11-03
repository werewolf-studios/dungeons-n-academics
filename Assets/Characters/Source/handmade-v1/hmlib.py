# Hand-modelling helpers for the handmade sibling meshes (handmade-v1).
# Everything is authored in rig-local rest space, matching *_AnimRig_v1:
# +Z up, -Y forward, +X is character-left, feet at Z=0, 1.8 m tall.
# Ring angle convention: 0 = +X side, 90 = front (-Y), 180 = -X side, 270 = back (+Y).
import bpy, bmesh, math
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

TAU = 2 * math.pi
ROOT = 'D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/handmade-v1'


def srgb(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]


def mat(name, hexcol, rough=0.8, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    c = srgb(hexcol)
    bsdf.inputs['Base Color'].default_value = (*c, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    m.diffuse_color = (*c, 1)
    m.roughness = rough
    return m


def rig(label):
    return bpy.data.objects[label + '_AnimRig_v1']


def bone(label, name):
    b = rig(label).data.bones[name]
    return b.head_local.copy(), b.tail_local.copy()


def coll(label):
    name = 'HM_' + label
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.data.collections['Handmade_v1'].children.link(c)
    return c


def make(label, name, bm, mats, smooth=False, recalc=True):
    """Write bm into <label>_<name>, rebuilding in place so reruns keep the object."""
    full = label + '_' + name
    obj = bpy.data.objects.get(full)
    if obj is None:
        obj = bpy.data.objects.new(full, bpy.data.meshes.new(full))
        coll(label).objects.link(obj)
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = obj.data
    # Slots first: clearing slots afterwards would reset every polygon's material index.
    me.materials.clear()
    for m in mats:
        me.materials.append(m)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = smooth
    obj.parent = rig(label)
    obj.matrix_parent_inverse.identity()
    obj.matrix_basis.identity()
    return obj


def sx(a, p):
    """Signed superellipse component."""
    return math.copysign(abs(a) ** (2 / p), a)


def section(c, rx, df, db=None, n=16, pf=2.0, pb=None, tilt=0.0, frame=None, rot=0.0, warp=None):
    """Superellipse ring around c. df/db are front/back depths, pf/pb front/back squareness.
    tilt raises the back and lowers the front (z offset +-tilt). warp(i, a, x, y, z) -> (x, y, z)."""
    db = df if db is None else db
    pb = pf if pb is None else pb
    xa, ya = frame if frame else (Vector((1, 0, 0)), Vector((0, -1, 0)))
    za = ya.cross(xa).normalized()
    pts = []
    for i in range(n):
        a = rot + TAU * i / n
        ca, sa = math.cos(a), math.sin(a)
        p = pf if sa >= 0 else pb
        x = sx(ca, p) * rx
        y = sx(sa, p) * (df if sa >= 0 else db)
        z = -sa * tilt
        if warp:
            x, y, z = warp(i, a, x, y, z)
        pts.append(c + xa * x + ya * y + za * z)
    return pts


def limb_frame(d, front=Vector((0, -1, 0))):
    """Ring axes for a limb running along d (bottom-to-top): xa sideways, ya toward front."""
    d = d.normalized()
    ya = (front - d * front.dot(d)).normalized()
    xa = d.cross(ya).normalized()
    return xa, ya


def loft(bm, rings, cap0=None, cap1=None, closed=True, mat=0, faces_out=None):
    """Bridge rings (bottom to top, angles increasing). cap: None, 'ngon' or an apex Vector."""
    vs = [[bm.verts.new(p) for p in r] for r in rings]
    n = len(rings[0])
    out = [] if faces_out is None else faces_out
    for a, b in zip(vs, vs[1:]):
        for i in range(n if closed else n - 1):
            j = (i + 1) % n
            f = bm.faces.new((a[i], b[i], b[j], a[j]))
            f.material_index = mat
            out.append(f)
    for ring, cap, top in ((vs[0], cap0, False), (vs[-1], cap1, True)):
        if cap is None:
            continue
        if cap == 'ngon':
            f = bm.faces.new(list(reversed(ring)) if top else ring)
            f.material_index = mat
            out.append(f)
        else:
            apex = bm.verts.new(cap)
            for i in range(n if closed else n - 1):
                j = (i + 1) % n
                f = bm.faces.new((ring[j], ring[i], apex) if top else (ring[i], ring[j], apex))
                f.material_index = mat
                out.append(f)
    return vs, out


def bezier(p0, p1, p2, t):
    return p0 * (1 - t) ** 2 + p1 * 2 * (1 - t) * t + p2 * t * t


def strand(bm, p0, p1, p2, widths, thick, normal, sides=4, segs=5, mat=0, twist=0.0):
    """Tapered clump along a quadratic bezier. widths/thick are (root, tip) pairs or callables of t.
    normal flattens the cross-section: thickness runs along it, width across."""
    rings = []
    for s in range(segs + 1):
        t = s / segs
        p = bezier(p0, p1, p2, t)
        tan = (bezier(p0, p1, p2, min(1, t + 1e-3)) - bezier(p0, p1, p2, max(0, t - 1e-3))).normalized()
        nz = (normal - tan * normal.dot(tan)).normalized()
        nx = tan.cross(nz).normalized()
        w = widths(t) if callable(widths) else widths[0] + (widths[1] - widths[0]) * t
        th = thick(t) if callable(thick) else thick[0] + (thick[1] - thick[0]) * t
        ring = []
        for k in range(sides):
            a = TAU * k / sides + twist * t
            ring.append(p + nx * math.cos(a) * w + nz * math.sin(a) * th)
        rings.append(ring)
    tip = rings.pop()
    apex = sum(tip, Vector()) / len(tip)
    loft(bm, rings, cap0='ngon', cap1=apex, mat=mat)


def catmull(ctrl, n):
    """n samples along a Catmull-Rom spline through ctrl points."""
    pts = [ctrl[0] * 2 - ctrl[1]] + list(ctrl) + [ctrl[-1] * 2 - ctrl[-2]]
    segs = len(ctrl) - 1
    out = []
    for k in range(n):
        u = k / (n - 1) * segs
        i = min(int(u), segs - 1)
        t = u - i
        p0, p1, p2, p3 = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    return out


def lock(bm, ctrl, width, thick, centre, n=8, sides=5, mat=0, flat_to=None):
    """Long hair lock through control points. width/thick: callables of t (0 root .. 1 tip).
    The cross-section lies flat against the hair mass (thickness points away from centre)."""
    path = catmull(ctrl, n)
    rings = []
    for k, p in enumerate(path[:-1]):
        t = k / (n - 1)
        tan = (path[k + 1] - path[max(k - 1, 0)]).normalized()
        out = (p - centre) if flat_to is None else flat_to(p)
        nz = (out - tan * out.dot(tan)).normalized()
        nx = tan.cross(nz).normalized()
        w, th = width(t), thick(t)
        rings.append([p + nx * math.cos(TAU * s / sides) * w + nz * math.sin(TAU * s / sides) * th for s in range(sides)])
    loft(bm, rings, cap0='ngon', cap1=path[-1], mat=mat)


class Surface:
    """BVH over a built object (rig-local coordinates) for projecting decals onto it."""

    def __init__(self, obj):
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        self.tree = BVHTree.FromBMesh(bm)
        bm.free()

    def hit(self, x, z, y0=-0.5, direction=Vector((0, 1, 0))):
        loc, nrm, idx, dist = self.tree.ray_cast(Vector((x, y0, z)), direction)
        return loc, nrm

    def project(self, pts2d, lift, direction=Vector((0, 1, 0))):
        out = []
        for x, z in pts2d:
            loc, nrm = self.hit(x, z, direction=direction)
            if loc is None:
                raise ValueError('decal point missed surface at %.3f %.3f' % (x, z))
            if nrm.dot(direction) > 0:
                nrm = -nrm
            out.append(loc + nrm * lift)
        return out


def ellipse2d(cx, cz, rx, rz, n=16, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    pts = []
    for i in range(n):
        a = TAU * i / n
        x, z = rx * math.cos(a), rz * math.sin(a)
        pts.append((cx + x * c - z * s, cz + x * s + z * c))
    return pts


def band2d(path, half):
    """Closed outline around a 2D polyline with per-point half thickness (list or float)."""
    half = half if isinstance(half, (list, tuple)) else [half] * len(path)
    top, bot = [], []
    for i, (x, z) in enumerate(path):
        a = path[max(i - 1, 0)]
        b = path[min(i + 1, len(path) - 1)]
        tx, tz = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(tx, tz) or 1
        nx, nz = -tz / ln, tx / ln
        top.append((x + nx * half[i], z + nz * half[i]))
        bot.append((x - nx * half[i], z - nz * half[i]))
    return top + list(reversed(bot))


def _grid(bm, surf, rows, lift, mat, direction, closed):
    """rows: lists of 2D points of equal length; every vertex is snapped onto surf."""
    vs = [[bm.verts.new(p) for p in surf.project(r, lift, direction)] for r in rows]
    n = len(rows[0])
    for a, b in zip(vs, vs[1:]):
        for i in range(n if closed else n - 1):
            j = (i + 1) % n
            f = bm.faces.new((a[i], a[j], b[j], b[i]))
            f.material_index = mat
            f.normal_update()
            if f.normal.dot(direction) > 0:
                f.normal_flip()
    return vs


def decal(bm, surf, pts2d, lift, mat, direction=Vector((0, 1, 0)), rings=3):
    """Fill a closed 2D outline (front-view x,z) with concentric rings toward its centroid,
    projected onto surf so the patch hugs the curvature."""
    cx = sum(p[0] for p in pts2d) / len(pts2d)
    cz = sum(p[1] for p in pts2d) / len(pts2d)
    rows = []
    for k in range(rings, 0, -1):
        s = k / rings
        rows.append([(cx + (x - cx) * s, cz + (z - cz) * s) for x, z in pts2d])
    vs = _grid(bm, surf, rows, lift, mat, direction, True)
    centre = bm.verts.new(surf.project([(cx, cz)], lift, direction)[0])
    inner = vs[-1]
    for i in range(len(inner)):
        f = bm.faces.new((inner[i], inner[(i + 1) % len(inner)], centre))
        f.material_index = mat
        f.normal_update()
        if f.normal.dot(direction) > 0:
            f.normal_flip()
    return vs


def resample(path, n):
    """Even resample of a 2D polyline (with optional per-point values in a parallel list)."""
    seg = [math.dist(a, b) for a, b in zip(path, path[1:])]
    total = sum(seg)
    out = []
    for k in range(n):
        d = total * k / (n - 1)
        i = 0
        while i < len(seg) - 1 and d > seg[i]:
            d -= seg[i]
            i += 1
        t = d / seg[i] if seg[i] else 0
        out.append((i, t))
    return out


def decal_band(bm, surf, path, half, lift, mat, n=14, direction=Vector((0, 1, 0))):
    """Strip along a 2D polyline with per-point half widths, as a 3-row grid snapped to surf."""
    half = half if isinstance(half, (list, tuple)) else [half] * len(path)
    pts, hs = [], []
    for i, t in resample(path, n):
        a, b = path[i], path[min(i + 1, len(path) - 1)]
        pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        hs.append(half[i] + (half[min(i + 1, len(half) - 1)] - half[i]) * t)
    rows = [[], [], []]
    for i, (x, z) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        tx, tz = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(tx, tz) or 1
        nx, nz = -tz / ln, tx / ln
        for r, s in enumerate((-1, 0, 1)):
            rows[r].append((x + nx * hs[i] * s, z + nz * hs[i] * s))
    return _grid(bm, surf, rows, lift, mat, direction, False)


def mirror2d(pts, cx=0.0):
    return [(2 * cx - x, z) for x, z in reversed(pts)]


def shade_flat(obj):
    for p in obj.data.polygons:
        p.use_smooth = False
