# Sister hair: long, voluminous and wavy, reaching the shoulders. Concept targets: crown at 1.80 m,
# hair mass +-0.20 m wide between 1.62 and 1.45 m, tips around collar height (1.34-1.38 m),
# a side-swept fringe and locks framing both cheeks.
import importlib, sys
sys.path.insert(0, 'D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/handmade-v1')
import bpy
import hmlib as H, parts
importlib.reload(H); importlib.reload(parts)

L = 'Sister'
HAIR = H.mat('HM_Sister_Hair', '#7E4630', 0.85)
HAIR_DARK = H.mat('HM_Sister_HairDark', '#5A2F1F', 0.9)

P = {
    'hair_centre': (0, -0.022, 1.585),
    'hairline': [(0, 0), (25, -10), (45, 12), (65, 32), (90, 44), (115, 32), (135, 12), (155, -10), (180, 0),
                 (200, 2), (220, -35), (250, -58), (270, -60), (290, -58), (320, -35), (340, 2)],
    'cap_t': 0.036,
    'seed': 5,
    'face': (42, 138),
    'max_front': 18,        # generated locks fall sideways or back from the temples      # layers circle the whole head except this face window
    'layers': [
        # crown: short chunky locks that build the rounded top and the width above the ears
        {'phi': 78, 'start': 0, 'end': 360, 'step': 14, 'w': (0.026, 0.032), 't': 0.019, 'wave': 0.012,
         'path': [(1.71, 0.140, 1.0), (1.65, 0.188, 1.0)], 'tip': (1.585, 0.210), 'flick': 0.025},
        # outer layer: from high on the head out to the full width, then curling in at the tips
        {'phi': 60, 'start': 0, 'end': 360, 'step': 11, 'w': (0.024, 0.030), 't': 0.017, 'wave': 0.022,
         'path': [(1.63, 0.190, 1.0), (1.55, 0.215, 1.0), (1.46, 0.205, 1.0)], 'tip': (1.37, 0.190), 'flick': 0.04, 'back_bulge': 0.03, 'back_drop': 0.08},
        # middle layer
        {'phi': 38, 'start': 0, 'end': 360, 'step': 13, 'w': (0.024, 0.028), 't': 0.016, 'wave': 0.018,
         'path': [(1.57, 0.180, 1.0), (1.49, 0.195, 1.0), (1.42, 0.185, 1.0)], 'tip': (1.35, 0.170), 'flick': 0.03, 'back_bulge': 0.025, 'back_drop': 0.07},
        # under layer filling the nape
        {'phi': 10, 'start': 0, 'end': 360, 'step': 16, 'w': (0.022, 0.027), 't': 0.015, 'wave': 0.010,
         'path': [(1.51, 0.140, 1.0), (1.44, 0.150, 1.0)], 'tip': (1.36, 0.140), 'back_bulge': 0.015, 'back_drop': 0.05},
    ],
    'locks': [
        # side-swept fringe toward her right brow, plus a lock to the left temple
        {'root': (100, 74), 'ctrl': [(-0.020, -0.145, 1.706), (-0.042, -0.143, 1.652), (-0.070, -0.134, 1.624),
                                     (-0.093, -0.113, 1.602)], 'w': 0.023, 't': 0.014},
        {'root': (92, 66), 'ctrl': [(-0.004, -0.140, 1.668), (-0.018, -0.144, 1.636), (-0.030, -0.142, 1.610)],
         'w': 0.018, 't': 0.012},
        {'root': (80, 72), 'ctrl': [(0.024, -0.145, 1.708), (0.052, -0.141, 1.668), (0.082, -0.128, 1.640),
                                    (0.104, -0.104, 1.614)], 'w': 0.022, 't': 0.014},
        # thin locks falling in front of the ears (side sheet), then the side curtains behind them
        {'root': (42, 46), 'ctrl': [(0.108, -0.070, 1.600), (0.112, -0.050, 1.530), (0.125, -0.040, 1.450),
                                    (0.140, -0.030, 1.372)], 'w': 0.020, 't': 0.014, 'n': 9},
        {'root': (138, 46), 'ctrl': [(-0.108, -0.070, 1.600), (-0.112, -0.050, 1.530), (-0.125, -0.040, 1.450),
                                     (-0.140, -0.030, 1.372)], 'w': 0.020, 't': 0.014, 'n': 9},
        {'root': (30, 30), 'ctrl': [(0.125, -0.040, 1.570), (0.150, -0.030, 1.490), (0.168, -0.020, 1.410),
                                    (0.170, -0.010, 1.350)], 'w': 0.025, 't': 0.016, 'n': 9},
        {'root': (150, 30), 'ctrl': [(-0.125, -0.040, 1.570), (-0.150, -0.030, 1.490), (-0.168, -0.020, 1.410),
                                     (-0.170, -0.010, 1.350)], 'w': 0.025, 't': 0.016, 'n': 9},
    ],
}

head = bpy.data.objects[L + '_Head']
hair = parts.long_hair(L, P, head, HAIR, HAIR_DARK)
result = {'hair_faces': len(hair.data.polygons)}
