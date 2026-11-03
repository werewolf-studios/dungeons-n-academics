# Sister head, ears and face. Heights from the concept sheet (1435 px = 1.8 m):
# chin 1.453, mouth 1.502, nose tip 1.524, eyes 1.579, brows 1.628.
# Depths come from the side sheet (1432 px = 1.8 m): face front at the eyes y -0.139, nose tip
# -0.162 at 1.525, lips -0.146, chin -0.133.
import importlib, sys
sys.path.insert(0, 'D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/handmade-v1')
import hmlib as H, parts
importlib.reload(H); importlib.reload(parts)

L = 'Sister'
SKIN = H.mat('HM_Sister_Skin', '#F7A877', 0.7)

HEAD = {
    # z, tilt, cy, rx, df, db, pf, pb
    'rings': [
        (1.290, 0.000, 0.000, 0.074, 0.084, 0.052, 2.4, 2.0),   # upper chest, fills the square neckline
        (1.385, 0.000, -0.004, 0.050, 0.060, 0.050, 2.0, 2.0),
        (1.440, 0.000, -0.007, 0.046, 0.050, 0.054, 2.0, 2.0),
        (1.455, 0.000, -0.035, 0.050, 0.096, 0.083, 1.5, 2.0),    # chin underside
        (1.471, 0.000, -0.030, 0.062, 0.104, 0.090, 1.8, 2.1),
        (1.493, 0.000, -0.025, 0.080, 0.119, 0.096, 2.0, 2.2),    # lips
        (1.521, 0.000, -0.022, 0.090, 0.121, 0.103, 2.05, 2.3),   # nose tip, cheeks
        (1.546, 0.000, -0.022, 0.092, 0.119, 0.106, 2.1, 2.4),
        (1.577, 0.000, -0.022, 0.094, 0.117, 0.108, 2.15, 2.4),   # eyes
        (1.606, 0.000, -0.022, 0.095, 0.117, 0.108, 2.15, 2.4),   # brow ridge
        (1.634, 0.000, -0.022, 0.092, 0.111, 0.106, 2.1, 2.3),
        (1.663, 0.000, -0.022, 0.087, 0.100, 0.099, 2.1, 2.2),
        (1.692, 0.000, -0.022, 0.076, 0.084, 0.086, 2.05, 2.1),
        (1.714, 0.000, -0.022, 0.059, 0.063, 0.065, 2.0, 2.0),
        (1.728, 0.000, -0.022, 0.033, 0.034, 0.036, 2.0, 2.0),
    ],
    'apex': (0, -0.022, 1.734),
    'push': {(3, 6): 0.003, (4, 6): 0.003, (5, 6): 0.004,
             (6, 6): 0.004,
             (8, 4): -0.004, (8, 8): -0.004,                       # shallow eye sockets
             (9, 6): 0.003, (9, 5): 0.002, (9, 7): 0.002, (9, 4): 0.002, (9, 8): 0.002},
    # nose: centre y, rows of (z, half width, front depth, back depth); rounded tip at y -0.159
    'nose': (-0.138, [(1.509, 0.007, 0.008, 0.006), (1.515, 0.0125, 0.016, 0.006), (1.524, 0.0130, 0.021, 0.006),
                      (1.535, 0.0095, 0.015, 0.006), (1.547, 0.0060, 0.009, 0.006), (1.558, 0.0040, 0.004, 0.006)]),
    'ear_center': (0.102, 0.008, 1.545), 'ear_size': (0.021, 0.034, 0.011), 'ear_yaw': 38,
}

FACE = {
    'eye': (0.050, 1.579),
    'sclera': [(-0.021, -0.004), (-0.016, 0.008), (-0.007, 0.0145), (0.004, 0.0165), (0.014, 0.015), (0.021, 0.010),
               (0.025, 0.004), (0.022, -0.006), (0.015, -0.0125), (0.005, -0.015), (-0.006, -0.014), (-0.014, -0.0105),
               (-0.019, -0.007)],
    'iris_c': (0.001, -0.0015), 'iris_r': 0.0150, 'glint': (0.005, 0.0055, 0.0036),
    # upper lid line with a small wing at the outer corner
    'lash': [(-0.022, -0.003), (-0.016, 0.0105), (-0.006, 0.0165), (0.005, 0.0185), (0.016, 0.0165), (0.024, 0.011),
             (0.031, 0.0125), (0.036, 0.016)],
    'lash_w': [0.0012, 0.0024, 0.0030, 0.0033, 0.0034, 0.0030, 0.0020, 0.0008],
    'brow': [(-0.022, 0.044), (-0.010, 0.051), (0.004, 0.053), (0.018, 0.050), (0.030, 0.043)],
    'brow_w': [0.0034, 0.0042, 0.0041, 0.0035, 0.0020],
    'blush': (0.012, -0.033, 0.017, 0.0095),
    'mouth': [(-0.029, 1.508), (-0.018, 1.5025), (-0.006, 1.5), (0.006, 1.5), (0.018, 1.5025), (0.029, 1.508)],
    'mouth_w': [0.0005, 0.0009, 0.0011, 0.0011, 0.0009, 0.0005],
}

FACE_M = {
    'sclera': H.mat('HM_Sister_EyeWhite', '#FBF4EC', 0.4),
    'iris': H.mat('HM_Sister_Iris', '#5A2C17', 0.3),
    'pupil': H.mat('HM_Sister_Pupil', '#1E0F08', 0.3),
    'glint': H.mat('HM_Sister_Glint', '#FFFFFF', 0.2),
    'lash': H.mat('HM_Sister_Lash', '#24120B', 0.6),
    'brow': H.mat('HM_Sister_Brow', '#4C281B', 0.8),
    'rim': H.mat('HM_Sister_EyeRim', '#3A1F14', 0.6),
    'iris_dark': H.mat('HM_Sister_IrisDark', '#3E1C0F', 0.3),
    'lidline': H.mat('HM_Sister_LidLine', '#D6835E', 0.7),
    'crease': H.mat('HM_Sister_LidCrease', '#D6835E', 0.75),
    'lip_upper': H.mat('HM_Sister_LipUpper', '#E58E6E', 0.65),
    'lip_lower': H.mat('HM_Sister_LipLower', '#F5A08E', 0.55),
    'mouth': H.mat('HM_Sister_Mouth', '#8F4A40', 0.6),
    'blush': H.mat('HM_Sister_Blush', '#F4A285', 0.75),
}

head = parts.head(L, HEAD, SKIN)
parts.ear(L, HEAD, SKIN, None)
parts.nose(L, HEAD, SKIN, H.mat('HM_Sister_Nostril', '#B8664A', 0.8))
parts.face(L, FACE, head, FACE_M)
result = {'head_verts': len(head.data.vertices)}
