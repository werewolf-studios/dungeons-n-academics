# Body and costume primitives shared by both siblings: torso rings with necklines, limb tubes
# that follow the rest-pose bones, hands with separate fingers, banded trims and boots.
import bmesh, math
from mathutils import Vector, Matrix
import hmlib as H

FRONT = Vector((0, -1, 0))


def ring(c, rx, df, db, n, pf=2.2, pb=None, vdepth=0.0, vk=4, gap=0.0, scale=1.0, frame=None, warp=None):
    """Ring starting at the front centre. vdepth dips the front (necklines, pointed hems);
    gap (degrees) opens the ring at the front for slits, giving n open points."""
    pb = pf if pb is None else pb
    xa, ya = frame or (Vector((1, 0, 0)), FRONT)
    za = ya.cross(xa).normalized()
    g = math.radians(gap)
    pts = []
    for i in range(n):
        a = math.pi / 2 + (g / 2 + (H.TAU - g) * i / (n - 1) if gap > 0 else H.TAU * i / n)
        ca, sa = math.cos(a), math.sin(a)
        p = pf if sa >= 0 else pb
        x = H.sx(ca, p) * rx * scale
        y = H.sx(sa, p) * (df if sa >= 0 else db) * scale
        z = -vdepth * max(0.0, sa) ** vk
        if warp:
            x, y, z = warp(a, x, y, z)
        pts.append(c + xa * x + ya * y + za * z)
    return pts


def loft_rows(bm, rows, mats, closed=True, cap0=None, cap1=None):
    """Loft rows bottom-to-top; mats[k] is the material of the band between rows k and k+1."""
    vs = [[bm.verts.new(p) for p in r] for r in rows]
    n = len(rows[0])
    for k, (a, b) in enumerate(zip(vs, vs[1:])):
        for i in range(n if closed else n - 1):
            j = (i + 1) % n
            f = bm.faces.new((a[i], b[i], b[j], a[j]))
            f.material_index = mats[k]
    for ring, cap, top, m in ((vs[0], cap0, False, mats[0]), (vs[-1], cap1, True, mats[-1])):
        if cap is None:
            continue
        if cap == 'ngon':
            f = bm.faces.new(list(reversed(ring)) if top else ring)
            f.material_index = m
        else:
            apex = bm.verts.new(cap)
            for i in range(n if closed else n - 1):
                j = (i + 1) % n
                f = bm.faces.new((ring[j], ring[i], apex) if top else (ring[i], ring[j], apex))
                f.material_index = m
    return vs


def lerp_bone(h, t, s):
    return h + (t - h) * s


def tube(points, radii, n=10, front=FRONT, pf=2.0):
    """Rings along a polyline (bottom to top). radii: (rx, ry) per point."""
    rings = []
    for i, p in enumerate(points):
        d = (points[min(i + 1, len(points) - 1)] - points[max(i - 1, 0)]).normalized()
        frame = H.limb_frame(d, front)
        rx, ry = radii[i]
        rings.append(H.section(p, rx, ry, ry, n=n, pf=pf, frame=frame))
    return rings


def _digit(bm, pts, rad, pn, mat, nail_mat, taper=0.12, nail=True):
    """Jointed finger along pts (base, joint, joint, tip). Joints swell, the shaft between them
    narrows, the pad fills out toward the palm and a nail sits on the back of the last segment."""
    path, radii = [], []
    for k, p in enumerate(pts):
        r = rad * (1 - taper * k)
        if k == 0:
            path.append(p); radii.append((r * 0.98, r * 0.92))
        else:
            a = pts[k - 1]
            mid = (a + p) / 2
            rm = radii[-1][0] * 0.94
            path.append(mid); radii.append((rm, rm * 0.9))
            if k < len(pts) - 1:
                path.append(p); radii.append((r * 1.08, r * 1.0))    # knuckle
            else:
                path.append(p); radii.append((r * 0.9, r * 0.85))    # tip
    rings = tube(path, radii, n=8, front=pn)
    # finger pads: push the palm side of each ring outward a little, more toward the tip
    for ring, p in zip(rings, path):
        for v in ring:
            s = (v - p).dot(pn)
            if s > 0:
                v += pn * s * 0.25
    d_end = (pts[-1] - pts[-2]).normalized()
    loft_rows(bm, rings, [mat] * (len(rings) - 1), cap0=pts[0] - (pts[1] - pts[0]).normalized() * 0.004,
              cap1=pts[-1] + d_end * radii[-1][0] * 0.9)
    if nail:
        seg = pts[-1] - pts[-2]
        # the surface radius at the nail is between the last mid ring and the tip ring
        r_local = radii[-2][1] + (radii[-1][1] - radii[-2][1]) * 0.62
        c = pts[-2] + seg * 0.62 - pn * (r_local * 1.02)
        x = seg.normalized().cross(pn).normalized()
        rot = Matrix((x, seg.normalized(), -pn)).transposed()
        box(bm, c, (radii[-1][0] * 1.15, seg.length * 0.5, 0.0024), rot, nail_mat, bevel=0.0007)


def hand(bm, label, side, P, mat):
    """Palm, four fingers and thumb from the hand, fingers_base and thumb bones.
    The palm faces the body (rest A-pose), the thumb sits at the front."""
    sfx = '.L' if side > 0 else '.R'
    wh, wt = H.bone(label, 'hand' + sfx)
    kh, kt = H.bone(label, 'fingers_base' + sfx)
    _, ft = H.bone(label, 'fingers_tip' + sfx)
    th, tt = H.bone(label, 'thumb' + sfx)
    nail_mat = P.get('nail', mat)
    d = (kh - wh).normalized()
    inward = Vector((-side, 0, 0))
    pn = (inward - d * inward.dot(d)).normalized()           # palm normal
    fw = (FRONT - d * FRONT.dot(d) - pn * FRONT.dot(pn)).normalized()
    pw, pt = P['palm']                                        # half width, half thickness

    def prow(c, w, t, n=10, dorsal=0.0, hollow=0.0):
        out = []
        for i in range(n):
            a = H.TAU * i / n
            x = math.cos(a) * w
            y = H.sx(math.sin(a), 2.6) * t
            if y < 0:
                y -= dorsal * (1 - (x / w) ** 2)            # rounded back of the hand
            else:
                y -= hollow * (1 - (x / w) ** 2)            # slightly cupped palm
            out.append(c + fw * x + pn * y)
        return out
    # every piece is a closed shell; make() recalculates normals, so winding is free here
    rows = [prow(wh - d * 0.012, pw * 0.60, pt * 0.9),
            prow(wh + d * 0.012, pw * 0.82, pt, dorsal=0.002),
            prow(wh + d * 0.04, pw * 0.96, pt * 1.05, dorsal=0.004, hollow=0.002),
            prow(kh - d * 0.016, pw * 1.02, pt * 1.0, dorsal=0.005, hollow=0.001),
            prow(kh - d * 0.004, pw * 1.0, pt * 0.9, dorsal=0.004)]
    loft_rows(bm, rows, [mat] * 4, cap0=wh - d * 0.02, cap1=kh + d * 0.004)
    # thenar pad: the fleshy mound at the base of the thumb
    res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    tdir = (tt - th).normalized()
    pc = th + tdir * 0.012 + pn * pt * 0.15 - fw * 0.003
    frame = Matrix((fw, tdir, pn)).transposed()
    Mt = Matrix.Translation(pc) @ frame.to_4x4() @ Matrix.Diagonal((0.010, 0.016, pt * 0.8, 1))
    bmesh.ops.transform(bm, matrix=Mt, verts=res['verts'])
    for f in {f for v in res['verts'] for f in v.link_faces}:
        f.material_index = mat
    fdir = (ft - kh).normalized()
    for off, lens, rad in P['fingers']:
        pts = [kh + fw * off - d * 0.006]
        dirn = fdir.copy()
        for k, ln in enumerate(lens):
            # curl toward the palm a little more at each joint; outer fingers splay a touch
            dirn = (dirn + pn * P['curl'][k] + fw * off * 0.25).normalized()
            pts.append(pts[-1] + dirn * ln)
        _digit(bm, pts, rad, pn, mat, nail_mat)
    tb = th - tdir * 0.012
    tdir2 = (tdir + pn * 0.35).normalized()
    tpts = [tb, tb + tdir * 0.03, tb + tdir * 0.055]
    tpts.append(tpts[-1] + tdir2 * 0.024)
    _digit(bm, tpts, P['thumb_r'] * 1.05, pn, mat, nail_mat, taper=0.08)


def band_ring(bm, c, rx, df, db, z0, z1, n, mat, out=0.006, pf=2.2, vdepth=0.0, vk=4):
    """Closed thick band (belts, straps): inner/outer surfaces between heights z0 and z1."""
    cz0 = Vector((c.x, c.y, z0))
    cz1 = Vector((c.x, c.y, z1))
    s = (rx + out) / rx
    rows = [ring(cz0, rx, df, db, n, pf=pf, vdepth=vdepth, vk=vk),
            ring(cz0, rx, df, db, n, pf=pf, scale=s, vdepth=vdepth, vk=vk),
            ring(cz1, rx, df, db, n, pf=pf, scale=s, vdepth=vdepth, vk=vk),
            ring(cz1, rx, df, db, n, pf=pf, vdepth=vdepth, vk=vk)]
    rows.append(rows[0])
    vs = loft_rows(bm, rows, [mat] * 4)
    bmesh.ops.remove_doubles(bm, verts=[v for r in vs for v in r], dist=1e-6)


def box(bm, centre, size, rot, mat, bevel=0.0):
    """Oriented box (size = full extents) with an optional bevel, rot is a 3x3 Matrix."""
    res = bmesh.ops.create_cube(bm, size=1.0)
    vs = res['verts']
    M = Matrix.Translation(centre) @ rot.to_4x4() @ Matrix.Diagonal((*size, 1))
    bmesh.ops.transform(bm, matrix=M, verts=vs)
    faces = list({f for v in vs for f in v.link_faces})
    for f in faces:
        f.material_index = mat
    if bevel:
        edges = list({e for v in vs for e in v.link_edges})
        geo = bmesh.ops.bevel(bm, geom=edges, offset=bevel, segments=1, affect='EDGES', profile=0.5)
        for f in geo['faces']:
            f.material_index = mat
    return vs


def leg_centre(label, side, z):
    """Point on the rest-pose thigh/shin line at height z (extrapolated above the hip)."""
    sfx = '.L' if side > 0 else '.R'
    th, tt = H.bone(label, 'thigh' + sfx)
    sh, st = H.bone(label, 'shin' + sfx)
    if z >= tt.z:
        a, b = th, tt
    else:
        a, b = sh, st
    s = (z - a.z) / (b.z - a.z)
    return a + (b - a) * s


def _profile(rows, z):
    """Interpolate a boot side-profile table [(z, y_back, y_front, half_width_back, half_width_front)]."""
    if z <= rows[0][0]:
        return rows[0][1:]
    for a, b in zip(rows, rows[1:]):
        if a[0] <= z <= b[0]:
            s = (z - a[0]) / (b[0] - a[0])
            return tuple(u + (v - u) * s for u, v in zip(a[1:], b[1:]))
    return rows[-1][1:]


def _clip_y(poly, c, keep_back):
    """Clip a convex 2D polygon to y >= c (keep_back) or y <= c."""
    inside = (lambda p: p[1] >= c) if keep_back else (lambda p: p[1] <= c)
    out = []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        if inside(p):
            out.append(p)
        if inside(p) != inside(q):
            t = (c - p[1]) / (q[1] - p[1])
            out.append((p[0] + (q[0] - p[0]) * t, c))
    return out


class BootShape:
    """One continuous boot upper read from a side-profile table: horizontal rings whose front edge
    walks forward from the shaft, down the instep, to the toe box. Rings sit on the shin line and
    turn with the rest-pose foot bone, so the toe points where the foot does."""

    def __init__(self, label, side, rows, p=2.4):
        sfx = '.L' if side > 0 else '.R'
        self.fh, _ = H.bone(label, 'foot' + sfx)
        _, tt = H.bone(label, 'toe' + sfx)
        d = tt - self.fh
        self.yaw = math.atan2(d.x, -d.y)
        self.label, self.side, self.rows, self.p = label, side, rows, p

    def outer(self, deg):
        """Ring angle for a direction measured from the outer side of the foot toward the front."""
        return math.radians(deg) if self.side > 0 else math.pi - math.radians(deg)

    def point(self, a, z, grow=0.0):
        yb, yf, rxb, rxf = _profile(self.rows, z)
        yc = (yb + yf) / 2
        ca, sa = math.cos(a), math.sin(a)
        front = sa >= 0
        x = H.sx(ca, self.p) * ((rxf if front else rxb) + grow)
        y = yc - H.sx(sa, self.p) * ((yc - yf if front else yb - yc) + grow)
        cx = leg_centre(self.label, self.side, z).x if z >= self.fh.z else self.fh.x
        dx, dy = cx + x - self.fh.x, y - self.fh.y
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        return Vector((self.fh.x + dx * c - dy * s, self.fh.y + dx * s + dy * c, z))

    def ring(self, z, n=20, grow=0.0):
        return [self.point(math.pi / 2 + H.TAU * i / n, z, grow) for i in range(n)]

    def strap(self, bm, zfn, half, out, mat, n=24):
        """Closed strap following zfn(a) around the upper, standing off the surface by out."""
        angles = [math.pi / 2 + H.TAU * i / n for i in range(n)]
        rows = [[self.point(a, zfn(a) + dz, g) for a in angles]
                for dz, g in ((-half, 0.001), (-half, out), (half, out), (half, 0.001))]
        rows.append(rows[0])
        vs = loft_rows(bm, rows, [mat] * 4)
        bmesh.ops.remove_doubles(bm, verts=[v for r in vs for v in r], dist=1e-6)

    def facing(self, a, z):
        """Rotation whose local +Y points out of the upper at ring angle a, local +Z up."""
        n = (self.point(a, z, 0.01) - self.point(a, z, -0.01)).normalized()
        x = n.cross(Vector((0, 0, 1))).normalized()
        return Matrix((x, n, x.cross(n))).transposed()


def gem(bm, centre, rot, size, depth, mat):
    """Faceted diamond ornament (pendants, brooches, boot gems); local +Y faces outward."""
    pts = [(0, 0, size), (size * 0.62, 0, 0), (0, 0, -size), (-size * 0.62, 0, 0), (0, depth, 0), (0, -depth * 0.3, 0)]
    v = [bm.verts.new(centre + rot @ Vector(p)) for p in pts]
    for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
        bm.faces.new((v[a], v[b], v[4])).material_index = mat
        bm.faces.new((v[b], v[a], v[5])).material_index = mat


def boot(bm, label, side, P, m):
    """Single-piece boot: upper from the side-profile rows, chunky platform sole with a separate
    heel block and toe pad, folded cuff, straps and ornaments. m maps roles to material indices."""
    S = BootShape(label, side, P['upper'])
    rows = [S.ring(r[0]) for r in P['upper']]
    loft_rows(bm, rows, [m['boot']] * (len(rows) - 1), cap0='ngon', cap1='ngon')
    # platform sole: the lowest ring of the upper, grown outward
    outline = [(p.x, p.y) for p in S.ring(P['upper'][0][0], n=28, grow=P['sole_grow'])]
    lift, top = P['sole_lift'], P['sole_h']
    slab = [[Vector((x, y, lift)) for x, y in outline], [Vector((x, y, top)) for x, y in outline]]
    loft_rows(bm, slab, [m['sole']], cap0='ngon', cap1='ngon')
    for c, back in ((P['heel_from'], True), (P['pad_to'], False)):
        poly = _clip_y(outline, c, back)
        block = [[Vector((x, y, 0.0)) for x, y in poly], [Vector((x, y, lift + 0.002)) for x, y in poly]]
        loft_rows(bm, block, [m['sole']], cap0='ngon', cap1='ngon')
    # folded cuff, following the shaft shape
    z0, z1, g0, g1 = P['cuff']
    rows = [S.ring(z0, 18, g0), S.ring(z1, 18, g1), S.ring(z1 + 0.004, 18, g1 - 0.010), S.ring(z1 - 0.03, 18, g0 - 0.004)]
    loft_rows(bm, rows, [m['cuff']] * 3)
    for k, st in enumerate(P['straps']):
        S.strap(bm, lambda a, st=st: st['z'](a, side), st['half'], st.get('out', 0.005), m[st.get('mat', 'strap')])
    for o in P.get('ornaments', []):
        a = S.outer(o['deg'])
        z = o['z']
        rot = S.facing(a, z)
        c = S.point(a, z, o.get('out', 0.008))
        if o['kind'] == 'buckle':
            box(bm, c, o['size'], rot, m['buckle'], bevel=0.0015)
        elif o['kind'] == 'keeper':
            box(bm, c, o['size'], rot, m[o.get('mat', 'strap')], bevel=0.002)
        else:
            gem(bm, c, rot, o['size'][0], o['size'][1], m['buckle'])
