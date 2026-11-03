# Brother hair: short, messy and spiky. Silhouette targets from the concept sheet:
# crown spikes reach 1.80 m, side tufts reach +-0.17 m at 1.65 m, the fringe tip sits
# between the brows at about 1.594 m and side locks frame both temples.
import importlib, math, sys
sys.path.insert(0, 'D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/handmade-v1')
import bpy
from mathutils import Vector
import hmlib as H, parts
importlib.reload(H); importlib.reload(parts)

L = 'Brother'
HAIR = H.mat('HM_Brother_Hair', '#6E3725', 0.85)
HAIR_DARK = H.mat('HM_Brother_HairDark', '#4E2418', 0.9)


def flow(theta, phi, rng):
    if 45 < theta < 135 and phi > 18:
        return None                       # fringe is placed by hand
    t, p = math.radians(theta), math.radians(phi)
    r = Vector((math.cos(t) * math.cos(p), -math.sin(t) * math.cos(p), math.sin(p)))
    up = Vector((-math.sin(p) * math.cos(t), math.sin(p) * math.sin(t), math.cos(p)))  # along the scalp
    back = Vector((0, 1, 0))
    j = Vector([rng.uniform(-0.2, 0.2) for _ in range(3)])
    if phi > 58:                          # crown: clumps radiate from the whorl and flick up
        d, ln = -up + r * 0.6 + back * 0.4 + j, rng.uniform(0.08, 0.10)
    elif phi > 18:                        # upper sides: sweep down the scalp and kick out
        d, ln = -up * 0.8 + r * 0.65 + back * 0.25 + j, rng.uniform(0.075, 0.09)
    else:                                 # lower sides and nape: lie close and hang
        d, ln = -up + r * 0.3 + j, rng.uniform(0.06, 0.075)
    behind = max(0.0, -math.sin(t))       # 1 at the back of the head: the side sheet sweeps these back
    d = d + back * 0.5 * behind
    ln *= 1 + 0.3 * behind
    return {'th': theta + rng.uniform(-5, 5), 'ph': phi + rng.uniform(-3, 3), 'tip': tuple(d.normalized() * ln),
            'bend': ln * 0.18, 'w': rng.uniform(0.040, 0.050), 't': rng.uniform(0.016, 0.021)}


fill = []
for ph in range(-48, 86, 14):
    count = max(3, int(15 * math.cos(math.radians(ph))))
    for k in range(count):
        th = (360 * k / count + (ph * 7) % 23) % 360
        if ph > parts._interp(HAIRLINE := [(0, 2), (25, -12), (45, 10), (65, 34), (90, 46), (115, 34), (135, 10),
                                           (155, -12), (180, 2), (200, 4), (220, -30), (250, -52), (270, -56),
                                           (290, -52), (320, -30), (340, 4)], th) + 5:
            fill.append((th, ph))

P = {
    'hair_centre': (0, -0.022, 1.575),
    'hairline': HAIRLINE,
    'cap_t': 0.028,
    'seed': 11,
    'flow': flow,
    'fill': fill,
    'strands': [
        # fringe, sweeping from the character's left toward the centre of the brow
        {'th': 70, 'ph': 64, 'to': (0.004, -0.143, 1.592), 'bend': 0.028, 'w': 0.052, 't': 0.016},
        {'th': 98, 'ph': 62, 'to': (-0.038, -0.140, 1.614), 'bend': 0.024, 'w': 0.048, 't': 0.015},
        {'th': 84, 'ph': 74, 'to': (0.026, -0.141, 1.638), 'bend': 0.022, 'w': 0.050, 't': 0.015},
        {'th': 112, 'ph': 70, 'to': (-0.014, -0.140, 1.644), 'bend': 0.022, 'w': 0.050, 't': 0.015},
        {'th': 122, 'ph': 52, 'to': (-0.074, -0.127, 1.602), 'bend': 0.020, 'w': 0.046, 't': 0.014},
        {'th': 140, 'ph': 42, 'to': (-0.099, -0.101, 1.596), 'bend': 0.016, 'w': 0.040, 't': 0.013},
        {'th': 56, 'ph': 54, 'to': (0.048, -0.138, 1.620), 'bend': 0.022, 'w': 0.046, 't': 0.014},
        {'th': 40, 'ph': 42, 'to': (0.088, -0.115, 1.600), 'bend': 0.018, 'w': 0.042, 't': 0.013},
        {'th': 25, 'ph': 26, 'to': (0.104, -0.085, 1.588), 'bend': 0.012, 'w': 0.034, 't': 0.012},
        {'th': 155, 'ph': 26, 'to': (-0.104, -0.085, 1.590), 'bend': 0.012, 'w': 0.034, 't': 0.012},
        {'th': 90, 'ph': 80, 'to': (-0.060, -0.135, 1.640), 'bend': 0.022, 'w': 0.048, 't': 0.015},
        {'th': 66, 'ph': 80, 'to': (0.070, -0.131, 1.648), 'bend': 0.022, 'w': 0.048, 't': 0.015},
        # tufts sweeping up and forward over the forehead (side sheet)
        {'th': 90, 'ph': 78, 'tip': (0.000, -0.066, 0.046), 'bend': 0.016, 'w': 0.050, 't': 0.018},
        {'th': 70, 'ph': 72, 'tip': (0.022, -0.060, 0.036), 'bend': 0.014, 'w': 0.046, 't': 0.017},
        {'th': 110, 'ph': 72, 'tip': (-0.022, -0.060, 0.036), 'bend': 0.014, 'w': 0.046, 't': 0.017},
        # crown tufts that set the 1.80 m silhouette
        {'th': 70, 'ph': 80, 'tip': (0.012, 0.022, 0.068), 'bend': 0.012, 'w': 0.052, 't': 0.018},
        {'th': 150, 'ph': 76, 'tip': (-0.040, 0.032, 0.048), 'bend': 0.012, 'w': 0.050, 't': 0.018},
        {'th': 20, 'ph': 70, 'tip': (0.048, 0.032, 0.040), 'bend': 0.012, 'w': 0.050, 't': 0.018},
    ],
}

head = bpy.data.objects[L + '_Head']
hair = parts.hair(L, P, head, HAIR, HAIR_DARK)
result = {'hair_faces': len(hair.data.polygons), 'clumps': len(P['strands']) + len(fill)}
