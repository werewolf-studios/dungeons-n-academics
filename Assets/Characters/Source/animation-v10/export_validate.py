# Exports both characters to Animated/v10 and records validation evidence. Uses the established
# glTF settings. Weapons are not exported; Godot attaches them to hand.R.
import bpy, json, math, os
ROOT = 'D:/GodotProjects/dungeons-n-academics'
BASE = ROOT + '/Assets/Characters/Source/animation-v10'
OLD = ROOT + '/Assets/Characters/Source/animation-v1'
OUT = ROOT + '/Assets/Characters/Animated/v10'
PREVIOUS = ROOT + '/Assets/Characters/Animated/v9'
os.makedirs(OUT, exist_ok=True)
SPECS = {'Idle': (72, True), 'Walk': (28, True), 'Run': (18, True), 'SwordIdle': (48, True), 'SpearIdle': (48, True),
         'SwordSlash': (36, False), 'SpearThrust': (26, False), 'TakeDamage': (37, False)}
ACTIONS = {
    'Brother': {'Idle': 'v13', 'Walk': 'v15', 'Run': 'v15'},
    'Sister': {'Idle': 'v3', 'Walk': 'v6', 'Run': 'v6'},
}
REWORKED = ['SwordIdle', 'SwordSlash', 'SpearIdle', 'SpearThrust', 'TakeDamage']


def action(label, clip):
    return bpy.data.actions[f"{label}_{clip}_{'v17' if clip in REWORKED else ACTIONS[label][clip]}"]


refs = {}
audit = {}
for label in ['Brother', 'Sister']:
    s = bpy.data.scenes[label + '_Animation_v1']
    bpy.context.window.scene = s
    rig = bpy.data.objects[label + '_AnimRig_v1']
    mesh = bpy.data.objects[label + '_AnimMesh_v1']
    refs[label.lower()] = {}
    audit[label] = {}
    for clip, (length, loop) in SPECS.items():
        a = action(label, clip)
        strip = rig.animation_data.nla_tracks[clip].strips[0]
        assert strip.action == a, (label, clip, strip.action.name)
        assert int(a.frame_range[1]) == length + 1, (label, clip, a.frame_range[1])
        strip.action_frame_start, strip.action_frame_end = 1, length + 1
        strip.frame_start, strip.frame_end = 1, length + 1
        for t in rig.animation_data.nla_tracks:
            t.mute = True
        rig.animation_data.action = a
        rig.animation_data.action_slot = a.slots[0]
        poses = []
        finite = True
        minz = 100
        for f in range(1, length + 2):
            s.frame_set(f)
            bpy.context.view_layer.update()
            poses.append({b.name: b.matrix.copy() for b in rig.pose.bones})
            finite = finite and all(math.isfinite(v) for b in rig.pose.bones for row in b.matrix for v in row)
            if not loop or clip in ['Walk', 'Run']:
                ev = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
                minz = min(minz, min((ev.matrix_world @ v.co).z for v in ev.data.vertices))
        end_error = max(abs(poses[0][n][i][j] - poses[-1][n][i][j]) for n in poses[0] for i in range(4) for j in range(4))
        assert finite and (not loop or end_error < 1e-4), (label, clip, end_error)
        audit[label][clip] = {'action': a.name, 'finite': finite, 'first_last_matrix_error': end_error, 'mesh_min_z': minz if minz < 100 else None}
        samples = []
        for t in [0, .25, .5, .75, 1]:
            f = 1 + t * length
            s.frame_set(int(f), subframe=f - int(f))
            bpy.context.view_layer.update()
            points = {}
            for name in ['pelvis', 'head', 'hand.R', 'hand.L', 'foot.R', 'foot.L', 'tunic.R', 'tunic.L']:
                p = rig.pose.bones[name].matrix.translation
                points[name] = [p.x, p.z, -p.y]
            samples.append({'fraction': t, 'points': points})
        refs[label.lower()][clip] = samples
    mesh.data.calc_loop_triangles()
    audit[label]['mesh'] = {'triangles': len(mesh.data.loop_triangles), 'vertices': len(mesh.data.vertices),
                            'max_influences': max(len([g for g in v.groups if g.weight > 1e-6]) for v in mesh.data.vertices),
                            'unweighted': sum(not any(g.weight > 1e-6 for g in v.groups) for v in mesh.data.vertices)}
    rig.animation_data.action = None
    for t in rig.animation_data.nla_tracks:
        t.mute = False
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = mesh
    s.frame_set(1)
    bpy.ops.export_scene.gltf(filepath=OUT + '/' + label.lower() + '-animations-v10.glb', export_format='GLB', use_selection=True, use_active_scene=True,
                              export_animations=True, export_animation_mode='NLA_TRACKS', export_force_sampling=True, export_bake_animation=True,
                              export_anim_slide_to_zero=True, export_frame_step=1, export_optimize_animation_size=False, export_skins=True,
                              export_influence_nb=4, export_all_influences=False, export_def_bones=False, export_leaf_bone=False, export_yup=True,
                              export_materials='EXPORT', export_rest_position_armature=True)
    for t in rig.animation_data.nla_tracks:
        t.mute = True
    rig.animation_data.action = action(label, 'Idle')
    s.frame_set(1)
json.dump(refs, open(BASE + '/pose-reference.json', 'w'), indent=2)
json.dump(audit, open(BASE + '/validation.json', 'w'), indent=2)
manifest = json.load(open(PREVIOUS + '/animation-manifest.json'))
manifest['clips']['TakeDamage'].update(duration=37 / 24, event_frame=4, event_time_seconds=.125)
manifest['socket']['spear_rotation_degrees'] = [-90, 0, 0]
manifest['socket']['weapon_rotation_degrees'] = [-90, 0, 0]
manifest['socket']['spear_position'] = {'brother': [.08, .07, 0], 'sister': [.07, .065, 0]}
manifest['revision'] = 'v10: SwordIdle, SwordSlash, SpearIdle, SpearThrust and TakeDamage rebuilt for both characters; Idle, Walk and Run unchanged.'
manifest['godot_runtime_status'] = 'v10 awaiting user visual review in the preview scene.'
json.dump(manifest, open(OUT + '/animation-manifest.json', 'w'), indent=2)
code = open(OLD + '/08_glb_compare.py').read()
code = code.replace('refs=json.load', "BASE='" + BASE + "'\nrefs=json.load")
code = code.replace('Animated/v1/', 'Animated/v10/').replace('-animations-v1.glb', '-animations-v10.glb')
exec(compile(code, 'raw_comparison', 'exec'))
result = {'audit': {l: {k: (v if k == 'mesh' else {'min_z': v['mesh_min_z'], 'end': round(v['first_last_matrix_error'], 6)}) for k, v in audit[l].items()} for l in audit},
          'files': os.listdir(OUT)}
