# Brother body and costume: lavender wrap tunic with plum trim, short wide sleeves, pointed
# skirt with a front slit, belt and pouch, baggy plum trousers gathered into cuffed boots.
import importlib, math, sys
sys.path.insert(0, 'D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/handmade-v1')
import bpy, bmesh
from mathutils import Vector, Matrix
import hmlib as H, body as B
importlib.reload(H); importlib.reload(B)

L = 'Brother'
M = {
    'nail': H.mat('HM_Brother_Nail', '#FBD2BC', 0.45),
    'skin': H.mat('HM_Brother_Skin', '#F9AE7E', 0.7),
    'tunic': H.mat('HM_Brother_Tunic', '#CB9FDB', 0.85),
    'trim': H.mat('HM_Brother_Trim', '#5D3368', 0.8),
    'belt': H.mat('HM_Brother_Belt', '#513254', 0.75),
    'pants': H.mat('HM_Brother_Pants', '#583542', 0.9),
    'boot': H.mat('HM_Brother_Boot', '#7A4A36', 0.7),
    'cuff': H.mat('HM_Brother_BootCuff', '#8D5A42', 0.7),
    'sole': H.mat('HM_Brother_Sole', '#5C405C', 0.8),
    'gold': H.mat('HM_Brother_Gold', '#BD874C', 0.4, 0.6),
    'pouch': H.mat('HM_Brother_Pouch', '#6B4430', 0.7),
    'flap': H.mat('HM_Brother_PouchFlap', '#5A3828', 0.7),
}
CY = -0.004

# ---- tunic body: rings from under the belt to the V neckline (last band is the collar trim)
bm = bmesh.new()
TORSO = [  # z, rx, df, db, front V depth
    (1.020, 0.118, 0.090, 0.078, 0.000),
    (1.080, 0.120, 0.092, 0.080, 0.000),
    (1.150, 0.127, 0.098, 0.083, 0.000),
    (1.215, 0.132, 0.100, 0.086, 0.000),
    (1.270, 0.140, 0.098, 0.088, 0.015),
    (1.318, 0.149, 0.093, 0.087, 0.040),
    (1.350, 0.142, 0.083, 0.081, 0.060),
    (1.378, 0.106, 0.073, 0.071, 0.075),
    (1.428, 0.055, 0.055, 0.054, 0.100),
]
rows = [B.ring(Vector((0, CY, z)), rx, df, db, 20, pf=2.3, vdepth=v) for z, rx, df, db, v in TORSO]
B.loft_rows(bm, rows, [0] * 7 + [1])
# sleeves: rounded shoulder cap, wide, ending at the elbow in a plum cuff with a turned-in lip
for side in (1, -1):
    spec = [(-0.03, 0.055), (0.15, 0.067), (0.40, 0.073), (0.62, 0.078), (0.74, 0.081),
            (0.93, 0.085), (0.91, 0.077), (0.74, 0.070)]
    B.sleeve(bm, L, side, spec, [0, 0, 0, 0, 1, 1, 1])
tunic = H.make(L, 'Tunic', bm, [M['tunic'], M['trim']], smooth=False)

# ---- skirt: open at the front slit, pointed hem, plum hem band folded inside
bm = bmesh.new()
SKIRT = [  # z, rx, df, db, hem dip, slit gap degrees, scale
    (1.068, 0.119, 0.091, 0.080, 0.000, 0, 1.0),
    (1.010, 0.142, 0.101, 0.089, 0.000, 0, 1.0),
    (0.940, 0.166, 0.112, 0.099, 0.000, 0, 1.0),
    (0.885, 0.180, 0.119, 0.105, 0.035, 5, 1.0),
    (0.862, 0.187, 0.124, 0.109, 0.080, 7, 1.0),
    (0.826, 0.195, 0.128, 0.112, 0.082, 8, 1.0),
    (0.830, 0.195, 0.128, 0.112, 0.082, 8, 0.955),
    (0.864, 0.187, 0.124, 0.109, 0.080, 7, 0.95),
]
srows = [B.ring(Vector((0, CY, z)), rx, df, db, 27, pf=2.2, vdepth=v, vk=2, gap=max(g, 0.01), scale=sc)
         for z, rx, df, db, v, g, sc in SKIRT]
vs = B.loft_rows(bm, list(reversed(srows[:5])), [0] * 4, closed=False)
vs += B.loft_rows(bm, srows[4:], [1, 1, 1], closed=False)
bmesh.ops.remove_doubles(bm, verts=[v for r in vs for v in r], dist=1e-6)
skirt = H.make(L, 'Skirt', bm, [M['tunic'], M['trim']], smooth=False)

# ---- belt, pouch and brooch
bm = bmesh.new()
B.band_ring(bm, Vector((0, CY, 0)), 0.123, 0.095, 0.083, 1.034, 1.074, 20, 0, out=0.007, pf=2.3)
rot = Matrix.Rotation(math.radians(-37), 3, 'Z')
B.box(bm, Vector((-0.116, -0.094, 0.990)), (0.068, 0.026, 0.074), rot, 1, bevel=0.006)
B.box(bm, Vector((-0.119, -0.104, 1.010)), (0.072, 0.010, 0.044), rot, 2, bevel=0.003)
B.box(bm, Vector((-0.123, -0.112, 0.994)), (0.012, 0.006, 0.012), rot, 3, bevel=0.002)
gem = [bm.verts.new(p) for p in [(0, -0.103, 1.318), (0.014, -0.100, 1.295), (0, -0.103, 1.272),
                                 (-0.014, -0.100, 1.295), (0, -0.111, 1.295), (0, -0.094, 1.295)]]
for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
    bm.faces.new((gem[a], gem[b], gem[4])).material_index = 3
    bm.faces.new((gem[b], gem[a], gem[5])).material_index = 3
acc = H.make(L, 'Accessories', bm, [M['belt'], M['pouch'], M['flap'], M['gold']], smooth=False)

# wrap edge: the outer panel's plum border runs from the brooch to the character's left hip
surf = H.Surface(tunic)
bm = bmesh.new()
H.decal_band(bm, surf, [(-0.004, 1.300), (0.030, 1.238), (0.066, 1.158), (0.104, 1.074)], 0.0125, 0.0035, 0, n=26)
H.make(L, 'TunicTrim', bm, [M['trim']], smooth=False, recalc=False)

# ---- arms: forearm skin from inside the sleeve to the wrist, then hands
bm = bmesh.new()
HAND = {'nail': 1, 'palm': (0.041, 0.0155), 'thumb_r': 0.0118, 'curl': [0.12, 0.22, 0.28],
        'fingers': [(0.029, [0.033, 0.025, 0.021], 0.0094), (0.0098, [0.037, 0.028, 0.023], 0.0097),
                    (-0.0098, [0.034, 0.026, 0.021], 0.0092), (-0.028, [0.027, 0.021, 0.017], 0.0083)]}
for side in (1, -1):
    sfx = '.L' if side > 0 else '.R'
    uh, ut = H.bone(L, 'upper_arm' + sfx)
    fh, ft = H.bone(L, 'forearm' + sfx)
    hh, ht = H.bone(L, 'hand' + sfx)
    pts = [hh + (ht - hh) * 0.08, ft, fh + (ft - fh) * 0.7, fh + (ft - fh) * 0.35, fh, uh + (ut - uh) * 0.7]
    radii = [(0.024, 0.021), (0.027, 0.023), (0.031, 0.027), (0.034, 0.030), (0.036, 0.033), (0.038, 0.035)]
    B.loft_rows(bm, B.tube(pts, radii, n=10), [0] * 5, cap0='ngon', cap1='ngon')
    B.hand(bm, L, side, HAND, 0)
H.make(L, 'Arms', bm, [M['skin'], M['nail']], smooth=True)

# ---- trousers: horizontal rings on the rest leg line, baggy at the calf, gathered at the boot
bm = bmesh.new()
# side sheet: the calf sits ~2 cm behind the bone line, the hem gathers into a tight band that rests
# on the boot cuff (0.30-0.34 m), then blouses out to a 0.10 m puff around 0.395 m
PANTS = [  # z, rx, df, db, y offset behind the bone line
    (0.200, 0.048, 0.048, 0.048, 0.022), (0.300, 0.058, 0.060, 0.058, 0.024), (0.338, 0.064, 0.066, 0.064, 0.024),
    (0.362, 0.086, 0.088, 0.086, 0.024), (0.395, 0.104, 0.100, 0.100, 0.022), (0.430, 0.101, 0.095, 0.095, 0.020),
    (0.470, 0.092, 0.087, 0.087, 0.016), (0.525, 0.086, 0.091, 0.086, 0.010), (0.610, 0.078, 0.084, 0.080, 0.000),
    (0.710, 0.077, 0.084, 0.078, 0.000), (0.810, 0.076, 0.082, 0.076, 0.000), (0.900, 0.072, 0.076, 0.068, 0.000),
    (1.040, 0.066, 0.070, 0.060, 0.000)]
for side in (1, -1):
    rows = []
    for z, rx, df, db, dy in PANTS:
        c = B.leg_centre(L, side, z)
        # tuck the hips in under the skirt; the legs still follow the thigh line below
        # tuck the hips in under the skirt; the shin follows the bone so the leg lands in the boot
        k = min(1.0, max(0.0, (z - 0.45) / 0.25))
        x = side * (abs(c.x) + k * (min(abs(c.x), 0.112 - 0.4 * max(0.0, z - 0.85)) - abs(c.x)))
        rows.append(B.ring(Vector((x, c.y + dy, z)), rx, df, db, 14, pf=2.0))
    B.loft_rows(bm, rows, [0] * (len(rows) - 1), cap0='ngon', cap1='ngon')
H.make(L, 'Pants', bm, [M['pants']], smooth=False)

# ---- boots
bm = bmesh.new()
# side sheet (1445 px = 1.8 m): toe at y -0.19, heel at +0.12, 6 cm platform sole on a heel block,
# instep climbing from the toe box (0.11 m) into the shaft, cuff 0.23-0.31 m, plum strap rising
# from the heel to the front of the ankle with a gold buckle on the outer side
BOOT = {
    'upper': [  # z, y back, y front, half width back, half width front
        (0.068, 0.106, -0.180, 0.047, 0.060), (0.085, 0.107, -0.176, 0.048, 0.062),
        (0.100, 0.105, -0.171, 0.049, 0.062), (0.113, 0.103, -0.160, 0.051, 0.061),
        (0.126, 0.100, -0.133, 0.053, 0.059), (0.141, 0.096, -0.098, 0.055, 0.058),
        (0.158, 0.091, -0.075, 0.057, 0.057), (0.186, 0.087, -0.054, 0.058, 0.058),
        (0.216, 0.085, -0.036, 0.059, 0.059), (0.250, 0.086, -0.035, 0.060, 0.060),
        (0.285, 0.087, -0.035, 0.060, 0.060)],
    'sole_grow': 0.010, 'sole_lift': 0.016, 'sole_h': 0.072, 'heel_from': 0.030, 'pad_to': -0.010,
    'cuff': (0.226, 0.312, 0.007, 0.013),
    'straps': [{'z': lambda a, side: 0.150 + 0.035 * math.sin(a), 'half': 0.014}],
    'ornaments': [{'kind': 'buckle', 'deg': 35, 'z': 0.150 + 0.035 * math.sin(math.radians(35)), 'out': 0.007,
                   'size': (0.024, 0.006, 0.034)}],
}
for side in (1, -1):
    B.boot(bm, L, side, BOOT, {'boot': 0, 'cuff': 1, 'sole': 2, 'strap': 2, 'buckle': 3})
H.make(L, 'Boots', bm, [M['boot'], M['cuff'], M['sole'], M['gold']], smooth=False)

result = {o.name: len(o.data.polygons) for o in H.coll(L).objects}
