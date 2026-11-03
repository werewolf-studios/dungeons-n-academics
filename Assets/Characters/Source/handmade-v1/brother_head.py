# Brother head, ears and face. Heights are read from the concept sheet (1454 px = 1.8 m):
# chin 1.452, mouth 1.499, nose tip 1.519, eyes 1.568, brows 1.612, hairline 1.66.
# Depths come from the side sheet (1445 px = 1.8 m): face front at the eyes y -0.135, brow -0.14,
# nose tip -0.16, lips -0.14, chin -0.13; the rounder front lets the eyes wrap round in profile.
import importlib, sys
sys.path.insert(0, 'D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/handmade-v1')
import hmlib as H, parts
importlib.reload(H); importlib.reload(parts)

L = 'Brother'
SKIN = H.mat('HM_Brother_Skin', '#F9AE7E', 0.7)

HEAD = {
    # z, tilt, cy, rx, df, db, pf, pb
    'rings': [
        (1.290, 0.000, 0.000, 0.062, 0.078, 0.052, 2.2, 2.0),   # upper chest, fills the V neck
        (1.380, 0.000, -0.003, 0.050, 0.058, 0.052, 2.0, 2.0),
        (1.436, 0.000, -0.006, 0.048, 0.050, 0.056, 2.0, 2.0),
        (1.452, 0.000, -0.035, 0.050, 0.092, 0.085, 1.45, 2.0),   # chin underside
        (1.468, 0.000, -0.030, 0.059, 0.101, 0.092, 1.7, 2.1),
        (1.490, 0.000, -0.025, 0.078, 0.115, 0.098, 1.95, 2.2),   # lips
        (1.517, 0.000, -0.022, 0.089, 0.118, 0.103, 2.05, 2.3),   # nose tip, cheeks
        (1.540, 0.000, -0.022, 0.093, 0.116, 0.106, 2.1, 2.4),
        (1.568, 0.000, -0.022, 0.095, 0.113, 0.108, 2.15, 2.4),   # eyes
        (1.596, 0.000, -0.022, 0.095, 0.114, 0.108, 2.15, 2.4),   # brow ridge
        (1.624, 0.000, -0.022, 0.093, 0.109, 0.106, 2.1, 2.3),
        (1.654, 0.000, -0.022, 0.088, 0.099, 0.099, 2.1, 2.2),
        (1.684, 0.000, -0.022, 0.077, 0.083, 0.086, 2.05, 2.1),
        (1.707, 0.000, -0.022, 0.060, 0.062, 0.065, 2.0, 2.0),
        (1.722, 0.000, -0.022, 0.034, 0.034, 0.036, 2.0, 2.0),
    ],
    'apex': (0, -0.022, 1.728),
    # (ring, vert): forward push (negative sinks). 6 = front centre, 5/7 its neighbours, 4/8 under the eyes.
    'push': {(3, 6): 0.004, (4, 6): 0.003,
             (5, 6): 0.004,
             (6, 6): 0.004,
             (8, 4): -0.004, (8, 8): -0.004,                       # shallow eye sockets
             (9, 6): 0.004, (9, 5): 0.002, (9, 7): 0.002, (9, 4): 0.002, (9, 8): 0.002},
    # nose: centre y, rows of (z, half width, front depth, back depth); rounded tip at y -0.157
    'nose': (-0.135, [(1.503, 0.008, 0.009, 0.006), (1.509, 0.0145, 0.017, 0.006), (1.517, 0.0145, 0.022, 0.006),
                      (1.528, 0.0110, 0.017, 0.006), (1.541, 0.0075, 0.011, 0.006), (1.555, 0.0055, 0.005, 0.006)]),
    'ear_center': (0.104, 0.008, 1.540), 'ear_size': (0.022, 0.036, 0.012), 'ear_yaw': 40,
}

FACE = {
    'eye': (0.047, 1.568),
    'sclera': [(-0.021, -0.003), (-0.015, 0.009), (-0.006, 0.0145), (0.004, 0.016), (0.013, 0.0145), (0.020, 0.010),
               (0.024, 0.003), (0.021, -0.006), (0.014, -0.012), (0.004, -0.0145), (-0.006, -0.0135), (-0.014, -0.010),
               (-0.019, -0.006)],
    'iris_c': (0.001, -0.001), 'iris_r': 0.0145, 'glint': (0.005, 0.0055, 0.0035),
    'lash': [(-0.022, -0.002), (-0.016, 0.0105), (-0.006, 0.016), (0.005, 0.0175), (0.015, 0.016), (0.022, 0.0115),
             (0.028, 0.0075)],
    'lash_w': [0.0012, 0.0022, 0.0028, 0.0030, 0.0030, 0.0026, 0.0012],
    'brow': [(-0.024, 0.040), (-0.012, 0.046), (0.002, 0.048), (0.016, 0.047), (0.028, 0.042)],
    'brow_w': [0.0045, 0.0055, 0.0055, 0.005, 0.0035],
    'mouth': [(-0.030, 1.505), (-0.020, 1.4995), (-0.008, 1.497), (0.004, 1.4968), (0.016, 1.498), (0.028, 1.502),
              (0.033, 1.505)],
    'mouth_w': [0.0005, 0.0009, 0.0011, 0.0011, 0.0011, 0.0009, 0.0005],
}

FACE_M = {
    'sclera': H.mat('HM_Brother_EyeWhite', '#FBF4EC', 0.4),
    'iris': H.mat('HM_Brother_Iris', '#5B2F1A', 0.3),
    'pupil': H.mat('HM_Brother_Pupil', '#1E0F08', 0.3),
    'glint': H.mat('HM_Brother_Glint', '#FFFFFF', 0.2),
    'lash': H.mat('HM_Brother_Lash', '#2B160E', 0.6),
    'brow': H.mat('HM_Brother_Brow', '#5E301F', 0.8),
    'rim': H.mat('HM_Brother_EyeRim', '#3A1F14', 0.6),
    'iris_dark': H.mat('HM_Brother_IrisDark', '#3E1C0F', 0.3),
    'lidline': H.mat('HM_Brother_LidLine', '#D9875F', 0.7),
    'crease': H.mat('HM_Brother_LidCrease', '#D9875F', 0.75),
    'lip_upper': H.mat('HM_Brother_LipUpper', '#E4906C', 0.65),
    'lip_lower': H.mat('HM_Brother_LipLower', '#F2A58A', 0.55),
    'mouth': H.mat('HM_Brother_Mouth', '#8F4A3C', 0.6),
}

head = parts.head(L, HEAD, SKIN)
parts.ear(L, HEAD, SKIN, None)
parts.nose(L, HEAD, SKIN, H.mat('HM_Brother_Nostril', '#B8664A', 0.8))
parts.face(L, FACE, head, FACE_M)
result = {'head_verts': len(head.data.vertices)}
