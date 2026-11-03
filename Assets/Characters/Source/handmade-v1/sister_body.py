# Sister body and costume: crimson tunic with a square plum neckline, lavender side panels,
# gold leaf pendant, flared half sleeves, pointed skirt with a front slit, slim leggings and
# crimson boots with crossed lavender straps on lavender soles.
import importlib, math, sys
sys.path.insert(0, 'D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/handmade-v1')
import bpy, bmesh
from mathutils import Vector, Matrix
import hmlib as H, body as B
importlib.reload(H); importlib.reload(B)

L = 'Sister'
M = {
    'nail': H.mat('HM_Sister_Nail', '#FBD2BC', 0.45),
    'skin': H.mat('HM_Sister_Skin', '#F7A877', 0.7),
    'tunic': H.mat('HM_Sister_Tunic', '#8C3740', 0.85),
    'trim': H.mat('HM_Sister_Trim', '#563161', 0.8),
    'panel': H.mat('HM_Sister_Panel', '#A679B8', 0.85),
    'belt': H.mat('HM_Sister_Belt', '#4F2E54', 0.75),
    'legs': H.mat('HM_Sister_Leggings', '#4A3341', 0.9),
    'boot': H.mat('HM_Sister_Boot', '#8E3442', 0.7),
    'cuff': H.mat('HM_Sister_BootCuff', '#7E2C3A', 0.7),
    'strap': H.mat('HM_Sister_Strap', '#B48CD0', 0.75),
    'sole': H.mat('HM_Sister_Sole', '#AF81BF', 0.8),
    'gold': H.mat('HM_Sister_Gold', '#AE7F4A', 0.4, 0.6),
}
CY = -0.006
PANELS = [(6, 36), (144, 174), (186, 216), (324, 354)]   # degrees, 0 = +X, 90 = front


def paint_panels(bm, cy, ranges, src, dst, zmax=9.0):
    for f in bm.faces:
        if f.material_index != src:
            continue
        c = f.calc_center_median()
        if c.z > zmax:
            continue
        a = math.degrees(math.atan2(-(c.y - cy), c.x)) % 360
        if any(lo <= a <= hi for lo, hi in ranges):
            f.material_index = dst


def square_neck(depth, w, ramp=0.012):
    def warp(a, x, y, z):
        if math.sin(a) > 0:
            z -= depth * min(1.0, max(0.0, (w + ramp - abs(x)) / ramp))
        return x, y, z
    return warp


# ---- tunic body with a square neckline; the top band is the plum trim
bm = bmesh.new()
TORSO = [  # z, rx, df, db, neckline depth, neckline half width
    (1.060, 0.104, 0.078, 0.070, 0.000, 0.0),
    (1.110, 0.104, 0.080, 0.071, 0.000, 0.0),
    (1.170, 0.112, 0.090, 0.075, 0.000, 0.0),
    (1.230, 0.120, 0.095, 0.078, 0.000, 0.0),
    (1.285, 0.128, 0.093, 0.080, 0.000, 0.0),
    (1.320, 0.140, 0.087, 0.080, 0.012, 0.100),
    (1.352, 0.138, 0.080, 0.077, 0.035, 0.095),
    (1.380, 0.104, 0.071, 0.068, 0.058, 0.075),
    (1.425, 0.064, 0.058, 0.053, 0.080, 0.052),
]
rows = [B.ring(Vector((0, CY, z)), rx, df, db, 28, pf=2.3, warp=square_neck(d, w) if d else None)
        for z, rx, df, db, d, w in TORSO]
B.loft_rows(bm, rows, [0] * 7 + [1])
paint_panels(bm, CY, PANELS, 0, 2, zmax=1.255)
# sleeves are added after painting so they stay crimson
for side in (1, -1):
    spec = [(-0.03, 0.050), (0.15, 0.058), (0.40, 0.064), (0.60, 0.069), (0.72, 0.072),
            (0.95, 0.077), (0.93, 0.070), (0.72, 0.064)]
    B.sleeve(bm, L, side, spec, [0, 0, 0, 0, 1, 1, 1])
tunic = H.make(L, 'Tunic', bm, [M['tunic'], M['trim'], M['panel']], smooth=False)

# ---- skirt: lavender side panels, crimson front and back, pointed hem, front slit
bm = bmesh.new()
SKIRT = [  # z, rx, df, db, hem dip, slit gap, scale
    (1.112, 0.106, 0.081, 0.072, 0.000, 0, 1.0),
    (1.050, 0.128, 0.093, 0.082, 0.000, 0, 1.0),
    (0.985, 0.153, 0.105, 0.092, 0.000, 0, 1.0),
    (0.935, 0.174, 0.114, 0.100, 0.030, 5, 1.0),
    (0.890, 0.192, 0.122, 0.106, 0.090, 8, 1.0),
    (0.894, 0.192, 0.122, 0.106, 0.090, 8, 0.955),
    (0.922, 0.183, 0.118, 0.103, 0.080, 7, 0.95),
]
srows = [B.ring(Vector((0, CY, z)), rx, df, db, 31, pf=2.2, vdepth=v, vk=2, gap=max(g, 0.01), scale=sc)
         for z, rx, df, db, v, g, sc in SKIRT]
B.loft_rows(bm, list(reversed(srows)), [0] * 6, closed=False)
paint_panels(bm, CY, [(0, 40), (140, 220), (320, 360)], 0, 1)
skirt = H.make(L, 'Skirt', bm, [M['tunic'], M['panel']], smooth=False)

# ---- belt and pendant
bm = bmesh.new()
B.band_ring(bm, Vector((0, CY, 0)), 0.108, 0.084, 0.075, 1.092, 1.128, 28, 0, out=0.007, pf=2.3)
leaf = [bm.verts.new(p) for p in [(0, -0.103, 1.326), (0.016, -0.100, 1.300), (0, -0.103, 1.268),
                                  (-0.016, -0.100, 1.300), (0, -0.111, 1.300), (0, -0.094, 1.300)]]
for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
    bm.faces.new((leaf[a], leaf[b], leaf[4])).material_index = 1
    bm.faces.new((leaf[b], leaf[a], leaf[5])).material_index = 1
H.make(L, 'Accessories', bm, [M['belt'], M['gold']], smooth=False)

# ---- arms and hands
bm = bmesh.new()
HAND = {'nail': 1, 'palm': (0.037, 0.014), 'thumb_r': 0.0105, 'curl': [0.12, 0.22, 0.28],
        'fingers': [(0.026, [0.031, 0.023, 0.019], 0.0085), (0.0088, [0.034, 0.026, 0.021], 0.0088),
                    (-0.0088, [0.032, 0.024, 0.019], 0.0084), (-0.025, [0.025, 0.019, 0.016], 0.0076)]}
for side in (1, -1):
    sfx = '.L' if side > 0 else '.R'
    uh, ut = H.bone(L, 'upper_arm' + sfx)
    fh, ft = H.bone(L, 'forearm' + sfx)
    hh, ht = H.bone(L, 'hand' + sfx)
    pts = [hh + (ht - hh) * 0.08, ft, fh + (ft - fh) * 0.7, fh + (ft - fh) * 0.35, fh, uh + (ut - uh) * 0.7]
    radii = [(0.021, 0.019), (0.024, 0.021), (0.027, 0.024), (0.030, 0.027), (0.032, 0.029), (0.034, 0.031)]
    B.loft_rows(bm, B.tube(pts, radii, n=10), [0] * 5, cap0='ngon', cap1='ngon')
    B.hand(bm, L, side, HAND, 0)
H.make(L, 'Arms', bm, [M['skin'], M['nail']], smooth=True)

# ---- leggings
bm = bmesh.new()
# side sheet: the calf sits ~3 cm behind the bone line and steps straight into the boot top
LEGS = [  # z, rx, df, db, y offset behind the bone line
    (0.220, 0.050, 0.050, 0.050, 0.026), (0.360, 0.053, 0.053, 0.053, 0.030), (0.440, 0.058, 0.060, 0.061, 0.030),
    (0.525, 0.055, 0.058, 0.057, 0.022), (0.620, 0.058, 0.060, 0.058, 0.004), (0.720, 0.064, 0.072, 0.066, 0.000),
    (0.820, 0.069, 0.078, 0.072, 0.000), (0.920, 0.070, 0.074, 0.066, 0.000), (1.000, 0.066, 0.066, 0.058, 0.000),
    (1.090, 0.060, 0.062, 0.054, 0.000)]
for side in (1, -1):
    rows = []
    for z, rx, df, db, dy in LEGS:
        c = B.leg_centre(L, side, z)
        k = min(1.0, max(0.0, (z - 0.45) / 0.25))     # hip tuck fades out above the knee
        x = side * (abs(c.x) + k * (min(abs(c.x), 0.100 - 0.35 * max(0.0, z - 0.88)) - abs(c.x)))
        rows.append(B.ring(Vector((x, c.y + dy, z)), rx, df, db, 14, pf=2.0))
    B.loft_rows(bm, rows, [0] * (len(rows) - 1), cap0='ngon', cap1='ngon')
H.make(L, 'Leggings', bm, [M['legs']], smooth=False)

# ---- boots
bm = bmesh.new()
# side sheet (1432 px = 1.8 m): toe at y -0.19, heel at +0.11, 6 cm lavender platform on a heel block,
# a lavender band round the top with a keeper, two straps crossing over the front of the ankle and
# rising to the back, and a gold gem on the outer ankle
BOOT = {
    'upper': [  # z, y back, y front, half width back, half width front
        (0.072, 0.102, -0.172, 0.047, 0.060), (0.090, 0.104, -0.170, 0.048, 0.061),
        (0.104, 0.102, -0.163, 0.049, 0.061), (0.116, 0.099, -0.150, 0.051, 0.060),
        (0.128, 0.096, -0.120, 0.053, 0.058), (0.142, 0.093, -0.091, 0.055, 0.057),
        (0.160, 0.090, -0.075, 0.057, 0.057), (0.186, 0.088, -0.057, 0.059, 0.059),
        (0.216, 0.087, -0.047, 0.061, 0.061), (0.260, 0.089, -0.043, 0.063, 0.063),
        (0.300, 0.091, -0.042, 0.064, 0.064)],
    'sole_grow': 0.011, 'sole_lift': 0.018, 'sole_h': 0.076, 'heel_from': 0.025, 'pad_to': -0.020,
    'cuff': (0.298, 0.345, 0.005, 0.010),
    'straps': [
        {'z': lambda a, side: 0.270, 'half': 0.015},
        {'z': lambda a, side: 0.188 + 0.034 * math.cos(a) * side - 0.032 * math.sin(a), 'half': 0.011},
        {'z': lambda a, side: 0.188 - 0.034 * math.cos(a) * side - 0.032 * math.sin(a), 'half': 0.011, 'out': 0.007},
    ],
    'ornaments': [{'kind': 'gem', 'deg': 0, 'z': 0.168, 'out': 0.010, 'size': (0.016, 0.010)},
                  {'kind': 'keeper', 'deg': -45, 'z': 0.270, 'out': 0.008, 'size': (0.024, 0.010, 0.036)}],
}
for side in (1, -1):
    B.boot(bm, L, side, BOOT, {'boot': 0, 'cuff': 1, 'sole': 2, 'strap': 3, 'buckle': 4})
boots = H.make(L, 'Boots', bm, [M['boot'], M['cuff'], M['sole'], M['strap'], M['gold']], smooth=False)
old = bpy.data.objects.get(L + '_BootStraps')       # projected straps from the first pass, now modelled
if old is not None:
    me = old.data
    bpy.data.objects.remove(old, do_unlink=True)
    bpy.data.meshes.remove(me)

result = {o.name: len(o.data.polygons) for o in H.coll(L).objects}
