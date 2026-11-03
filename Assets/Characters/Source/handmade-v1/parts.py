# Shared body parts for the handmade siblings. Each builder takes a label and a parameter dict
# so Brother and Sister share topology but keep their own proportions.
import bmesh, math
from mathutils import Vector, Matrix
import hmlib as H

HEAD_N = 24  # verts per head ring; index 6 is the front centre, 18 the back centre


def head(label, P, skin):
    """Neck-to-crown loft. P['rings'] rows: (z, tilt, cy, rx, df, db, pf, pb).
    P['push'] maps (ring, vert) -> forward push in metres (nose, lips, chin)."""
    bm = bmesh.new()
    rings = []
    for r, (z, tilt, cy, rx, df, db, pf, pb) in enumerate(P['rings']):
        def warp(i, a, x, y, zz, r=r):
            push = P['push'].get((r, i), 0.0)
            return x, y + push, zz
        rings.append(H.section(Vector((0, cy, z)), rx, df, db, n=HEAD_N, pf=pf, pb=pb, tilt=tilt, warp=warp))
    H.loft(bm, rings, cap0='ngon', cap1=Vector(P['apex']))
    return H.make(label, 'Head', bm, [skin], smooth=True)


def ear(label, P, skin, inner):
    """Ear shells: a flattened ellipsoid with a dished inner bowl, mirrored to both sides."""
    bm = bmesh.new()
    cx, cy, cz = P['ear_center']
    w, h, t = P['ear_size']      # depth (front-back), height, thickness
    yaw = math.radians(P['ear_yaw'])
    dish = 1.4 * t

    def place(lx, ly, lz, side):
        # yaw swings the rear rim away from the skull
        x = lx * math.cos(yaw) + ly * math.sin(yaw)
        y = -lx * math.sin(yaw) + ly * math.cos(yaw)
        return Vector((side * (cx + x), cy + y, cz + lz))

    for side in (1, -1):
        rings = []
        for k in range(1, 6):
            v = -math.cos(math.pi * k / 6)          # -1 (skull side) .. 1 (outer face)
            s = math.sqrt(max(0.0, 1 - v * v))
            lx = v * t - dish * max(0.0, v) ** 4    # sink the middle of the outer face into a bowl
            rings.append([place(lx, math.cos(H.TAU * i / 10) * w * s, math.sin(H.TAU * i / 10) * h * s, side)
                          for i in range(10)])
        H.loft(bm, rings, cap0=place(-t, 0, 0, side), cap1=place(t - dish, 0, 0, side))
    return H.make(label, 'Ears', bm, [skin], smooth=True)


def face(label, P, head_obj, M):
    """Eyes, brows and mouth as layered decals projected onto the head from the front.
    M: dict of materials sclera, iris, pupil, glint, lash, brow, mouth (+ blush optional)."""
    surf = H.Surface(head_obj)
    bm = bmesh.new()
    order = ['rim', 'sclera', 'iris_dark', 'iris', 'pupil', 'glint', 'lidline', 'crease', 'lash', 'brow',
             'lip_upper', 'mouth', 'lip_lower'] + (['blush'] if 'blush' in M else [])
    idx = {k: i for i, k in enumerate(order)}
    ex, ez = P['eye']                       # left eye centre (x>0), z
    cx = sum(p[0] for p in P['sclera']) / len(P['sclera'])
    cz = sum(p[1] for p in P['sclera']) / len(P['sclera'])
    for side in (1, -1):
        def w(pts, side=side):
            # eye-local (outward x, up z) -> front-view world (x, z)
            out = [(side * (ex + x), ez + z) for x, z in pts]
            return out if side > 0 else list(reversed(out))
        # dark outline a little larger than the white, so the eye reads at distance
        H.decal(bm, surf, w([(cx + (x - cx) * 1.1, cz + (z - cz) * 1.12) for x, z in P['sclera']]), 0.0005,
                idx['rim'], rings=2)
        H.decal(bm, surf, w(P['sclera']), 0.0008, idx['sclera'])
        ir = P['iris_r']
        ix, iz = P['iris_c']
        H.decal(bm, surf, w(H.ellipse2d(ix, iz, ir * 0.92, ir, 16)), 0.0013, idx['iris_dark'], rings=2)
        H.decal(bm, surf, w(H.ellipse2d(ix, iz - 0.001, ir * 0.72, ir * 0.78, 16)), 0.0017, idx['iris'], rings=2)
        H.decal(bm, surf, w(H.ellipse2d(ix, iz - 0.0005, ir * 0.42, ir * 0.47, 12)), 0.0021, idx['pupil'], rings=1)
        gx, gz, gr = P['glint']
        H.decal(bm, surf, w(H.ellipse2d(ix + gx, iz + gz, gr, gr, 8)), 0.0027, idx['glint'], rings=1)
        H.decal(bm, surf, w(H.ellipse2d(ix - gx * 0.9, iz - gz * 1.1, gr * 0.45, gr * 0.45, 8)), 0.0027,
                idx['glint'], rings=1)
        # lower lid: a thin soft line along the bottom edge of the white
        lower = [p for p in P['sclera'] if p[1] < cz - 0.003]
        lower.sort(key=lambda p: p[0])
        H.decal_band(bm, surf, w([(x, z - 0.0008) for x, z in lower]), 0.0011, 0.0024, idx['lidline'], n=10)
        # upper lid: lash band with a soft crease above it
        H.decal_band(bm, surf, w([(x, z + 0.0045) for x, z in P['lash']]), [v * 1.1 for v in P['lash_w']],
                     0.0018, idx['crease'], n=12)
        H.decal_band(bm, surf, w(P['lash']), P['lash_w'], 0.0024, idx['lash'], n=12)
        H.decal_band(bm, surf, w(P['brow']), P['brow_w'], 0.0009, idx['brow'], n=12)
        if 'blush' in M:
            bx, bz, brx, brz = P['blush']
            H.decal(bm, surf, w(H.ellipse2d(bx, bz, brx, brz, 14)), 0.0005, idx['blush'], rings=2)
    # lips: upper lip shade above the line, fuller lower lip below, dimples at the corners
    mouth = P['mouth']
    mw = P['mouth_w']
    n = len(mouth)
    full = [math.sin(math.pi * i / (n - 1)) for i in range(n)]
    H.decal_band(bm, surf, [(x, z + 0.0015 + 0.0012 * f) for (x, z), f in zip(mouth, full)],
                 [0.0012 + 0.0018 * f for f in full], 0.0006, idx['lip_upper'], n=14)
    H.decal_band(bm, surf, [(x, z - 0.0022 - 0.0022 * f) for (x, z), f in zip(mouth, full)],
                 [0.0010 + 0.0030 * f for f in full], 0.0006, idx['lip_lower'], n=14)
    H.decal_band(bm, surf, mouth, mw, 0.0009, idx['mouth'], n=14)
    for (x, z) in (mouth[0], mouth[-1]):
        # small crease hooking down from each corner of the smile
        dx = 0.0008 if x > 0 else -0.0008
        rot = -0.9 if x > 0 else 0.9
        H.decal(bm, surf, H.ellipse2d(x + dx, z - 0.0012, 0.0008, 0.0019, 8, rot=rot), 0.0009, idx['mouth'], rings=1)
    return H.make(label, 'Face', bm, [M[k] for k in order], smooth=False, recalc=False)


def _scalp(head_obj, centre):
    surf = H.Surface(head_obj)

    def at(theta, phi):
        t, p = math.radians(theta), math.radians(phi)
        d = Vector((math.cos(t) * math.cos(p), -math.sin(t) * math.cos(p), math.sin(p)))
        loc, nrm, _, _ = surf.tree.ray_cast(centre, d)
        if nrm.dot(d) < 0:
            nrm = -nrm
        return loc, nrm
    return at


def _interp(table, theta):
    """Periodic linear interpolation over [(theta, value), ...] sorted by theta in [0, 360)."""
    theta %= 360
    pts = table + [(table[0][0] + 360, table[0][1])]
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if a <= theta <= b:
            return va + (vb - va) * (theta - a) / (b - a)
    return table[0][1]


def hair(label, P, head_obj, m_hair, m_dark):
    """Scalp cap (dark, follows the skull) plus faceted clumps.
    P['hairline']: [(theta, lowest phi)], P['cap_t']: cap thickness. Clumps are dicts:
    th/ph root on the scalp, tip (offset) or to (absolute end), bend, w (width), t (thickness).
    P['strands'] are hand-placed; P['flow'](theta, phi, rng) adds clumps over P['fill'] roots."""
    import random
    centre = Vector(P['hair_centre'])
    at = _scalp(head_obj, centre)
    bm = bmesh.new()
    seg, rows = 32, 9
    grid = []
    for r in range(rows):
        ring = []
        for i in range(seg):
            theta = 360 * i / seg
            lo = _interp(P['hairline'], theta)
            f = r / rows
            phi = lo + (88 - lo) * f
            loc, n = at(theta, phi)
            t = P['cap_t'] * min(1.0, 0.15 + f * 3)     # taper into the skin at the hairline
            ring.append(loc + n * t)
        grid.append(ring)
    apex_loc, apex_n = at(0, 90)
    H.loft(bm, grid, cap1=apex_loc + apex_n * P['cap_t'], mat=1)
    rng = random.Random(P.get('seed', 7))
    specs = list(P['strands'])
    for theta, phi in P.get('fill', []):
        s = P['flow'](theta, phi, rng)
        if s:
            specs.append(s)
    for s in specs:
        loc, n = at(s['th'], s['ph'])
        p0 = loc + n * P['cap_t'] * 0.3
        p2 = Vector(s['to']) if 'to' in s else p0 + Vector(s['tip'])
        p1 = (p0 + p2) / 2 + n * s.get('bend', 0.0)
        H.strand(bm, p0, p1, p2, (s['w'], s['w'] * 0.12), (s['t'], s['t'] * 0.3), n,
                 sides=4, segs=s.get('segs', 4), mat=s.get('mat', 0))
    return H.make(label, 'Hair', bm, [m_hair, m_dark], smooth=False)


def long_hair(label, P, head_obj, m_hair, m_dark):
    """Scalp cap plus long locks. P['locks'] are lists of control points whose first entry is
    (theta, phi) on the scalp; P['layers'] generate wavy locks around the head."""
    import random
    centre = Vector(P['hair_centre'])
    at = _scalp(head_obj, centre)
    bm = bmesh.new()
    seg, rows = 32, 9
    grid = []
    for r in range(rows):
        ring = []
        for i in range(seg):
            theta = 360 * i / seg
            lo = _interp(P['hairline'], theta)
            f = r / rows
            loc, n = at(theta, lo + (88 - lo) * f)
            ring.append(loc + n * P['cap_t'] * min(1.0, 0.15 + f * 3))
        grid.append(ring)
    apex_loc, apex_n = at(0, 90)
    H.loft(bm, grid, cap1=apex_loc + apex_n * P['cap_t'], mat=1)
    rng = random.Random(P.get('seed', 3))
    axis = lambda z: Vector((0, centre.y, z))

    def flat(p):
        q = p - axis(p.z)
        q.z = 0
        return q if q.length > 1e-6 else Vector((0, 1, 0))

    def root(theta, phi):
        loc, n = at(theta, phi)
        return loc + n * P['cap_t'] * 0.4, n

    for L in P['layers']:
        theta = L['start']
        while theta < L['end']:
            th = theta + rng.uniform(-3, 3)
            if not (P['face'][0] < th % 360 < P['face'][1]):
                p0, n = root(th, L['phi'] + rng.uniform(-4, 4))
                t = math.radians(th + rng.uniform(-6, 6))
                # locks rooted near the temples fall sideways and back, never forward over the cheeks
                lim = math.radians(P.get('max_front', 90))
                if math.sin(t) > math.sin(lim):
                    t = lim if math.cos(t) > 0 else math.pi - lim
                h = Vector((math.cos(t), -math.sin(t), 0))
                side = Vector((math.sin(t), math.cos(t), 0))
                w = rng.uniform(-1, 1) * L['wave']
                # the side sheet carries more volume behind the head and lets it fall lower there
                back = max(0.0, -math.sin(t))
                bulge, drop = L.get('back_bulge', 0.0) * back, L.get('back_drop', 0.0) * back
                ctrl = [p0, p0 + n * 0.035 + Vector((0, 0, -0.012))]
                for k, (z, rad, wave) in enumerate(L['path']):
                    f = (k + 1) / len(L['path'])
                    ctrl.append(axis(z - drop * f) + h * (rad + bulge + rng.uniform(-0.01, 0.01)) + side * w * wave)
                    w = -w
                tip_z = L['tip'][0] - drop + rng.uniform(-0.025, 0.02)
                # every other lock flicks its tip outward, like the curls on the concept sheet
                flick = L.get('flick', 0.0) * rng.choice((0.0, 0.6, 1.0))
                ctrl.append(axis(tip_z + flick * 0.6) + h * (L['tip'][1] + flick) + side * w * 0.6)
                wr = rng.uniform(*L['w'])
                H.lock(bm, ctrl, lambda t, wr=wr: wr * (1 - 0.8 * t) + 0.004, lambda t: L['t'] * (1 - 0.6 * t) + 0.002,
                       centre, n=9, sides=5, mat=0, flat_to=flat)
            theta += L['step']
    for spec in P['locks']:
        (th, ph), rest = spec['root'], spec['ctrl']
        p0, n = root(th, ph)
        ctrl = [p0] + [Vector(c) for c in rest]
        wr, tr = spec['w'], spec['t']
        H.lock(bm, ctrl, lambda t, wr=wr: wr * (1 - 0.8 * t) + 0.003, lambda t, tr=tr: tr * (1 - 0.6 * t) + 0.002,
               centre, n=spec.get('n', 8), sides=5, mat=0, flat_to=flat)
    return H.make(label, 'Hair', bm, [m_hair, m_dark], smooth=False)


def nose(label, P, skin, nostril=None):
    """Small rounded nose sunk into the face. P['nose']: (centre y, [(z, rx, df, db), ...]).
    The two lowest rows flare into alar wings; nostrils are dark pits under the tip."""
    cy, rows = P['nose']
    bm = bmesh.new()
    rings = []
    for k, (z, rx, df, db) in enumerate(rows):
        def warp(i, a, x, y, zz, k=k):
            # alar wings: the second row bulges sideways and the tip row rounds forward
            if k == 1:
                x *= 1.12
            if k == 2 and abs(math.cos(a)) < 0.4 and math.sin(a) > 0:
                y -= 0.0015
            return x, y, zz
        rings.append(H.section(Vector((0, cy, z)), rx, df, db, n=10, pf=2.0, pb=2.0, warp=warp))
    z0, z1 = rows[0][0], rows[-1][0]
    H.loft(bm, rings, cap0=Vector((0, cy - rows[0][2] * 0.4, z0 - 0.003)), cap1=Vector((0, cy - rows[-1][2] * 0.3, z1 + 0.004)))
    mats = [skin]
    if nostril is not None:
        mats.append(nostril)
        # nostrils: small dark ellipsoids on the underside, just inside the wings
        for side in (1, -1):
            res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
            c = Vector((side * rows[1][1] * 0.55, cy - rows[1][2] * 0.45, z0 + 0.0015))
            M = Matrix.Translation(c) @ Matrix.Diagonal((0.0035, 0.0045, 0.0022, 1))
            bmesh.ops.transform(bm, matrix=M, verts=res['verts'])
            for f in {f for v in res['verts'] for f in v.link_faces}:
                f.material_index = 1
    return H.make(label, 'Nose', bm, mats, smooth=True)
