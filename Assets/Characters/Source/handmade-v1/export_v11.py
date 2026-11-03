# Export the handmade siblings to Animated/v11 with the approved v10 clips and glTF settings
# (see animation-v10/export_validate.py). Only the rig and the handmade mesh are exported;
# the rig is moved back to the origin for the export and restored afterwards.
import bpy, json, math, os
ROOT = 'D:/GodotProjects/dungeons-n-academics'
OUT = ROOT + '/Assets/Characters/Animated/v11'
PREVIOUS = ROOT + '/Assets/Characters/Animated/v10'
os.makedirs(OUT, exist_ok=True)
SPECS = {'Idle': (72, True), 'Walk': (28, True), 'Run': (18, True), 'SwordIdle': (48, True), 'SpearIdle': (48, True),
         'SwordSlash': (36, False), 'SpearThrust': (26, False), 'TakeDamage': (37, False)}

audit = {}
scene = bpy.context.scene
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
for label in ['Brother', 'Sister']:
    rig = bpy.data.objects[label + '_AnimRig_v1']
    mesh = bpy.data.objects[label + '_HM_Mesh_v1']
    rig.hide_set(False)                 # hidden objects cannot be selected for export
    mesh.hide_set(False)
    home = rig.location.copy()
    rig.location = (0, 0, 0)
    rig.data.pose_position = 'POSE'
    ad = rig.animation_data
    saved_action = ad.action
    audit[label] = {}
    for clip, (length, loop) in SPECS.items():
        strip = ad.nla_tracks[clip].strips[0]
        assert int(strip.action.frame_range[1]) == length + 1, (label, clip)
        for t in ad.nla_tracks:
            t.mute = True
        ad.action = strip.action
        ad.action_slot = strip.action.slots[0]
        minz, finite = 100.0, True
        for f in range(1, length + 2):
            scene.frame_set(f)
            ev = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
            zs = [(ev.matrix_world @ v.co).z for v in ev.data.vertices]
            finite = finite and all(math.isfinite(z) for z in zs)
            minz = min(minz, min(zs))
        audit[label][clip] = {'action': strip.action.name, 'frames': length + 1, 'finite': finite,
                              'mesh_min_z': round(minz, 4)}
    ad.action = None
    for t in ad.nla_tracks:
        t.mute = False
    me = mesh.data
    me.calc_loop_triangles()
    audit[label]['mesh'] = {
        'vertices': len(me.vertices), 'triangles': len(me.loop_triangles), 'materials': [m.name for m in me.materials],
        'max_influences': max(len([g for g in v.groups if g.weight > 1e-6]) for v in me.vertices),
        'unweighted': sum(not any(g.weight > 1e-6 for g in v.groups) for v in me.vertices)}
    # select_all skips hidden objects, and the appended Tripo ghosts arrived selected
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    mesh.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = mesh
    scene.frame_set(1)
    bpy.ops.export_scene.gltf(filepath=OUT + '/' + label.lower() + '-animations-v11.glb', export_format='GLB',
                              use_selection=True, use_active_scene=True, export_animations=True,
                              export_animation_mode='NLA_TRACKS', export_force_sampling=True, export_bake_animation=True,
                              export_anim_slide_to_zero=True, export_frame_step=1, export_optimize_animation_size=False,
                              export_skins=True, export_influence_nb=4, export_all_influences=False,
                              export_def_bones=False, export_leaf_bone=False, export_yup=True,
                              export_materials='EXPORT', export_rest_position_armature=True)
    for t in ad.nla_tracks:
        t.mute = True
    ad.action = saved_action
    rig.location = home
    scene.frame_set(1)

manifest = json.load(open(PREVIOUS + '/animation-manifest.json'))
manifest['revision'] = ('v11: handmade Blender meshes (handmade-v1) replace the Tripo meshes on the unchanged v10 rigs; '
                        'all eight clips, timings, events and sockets are identical to v10.')
manifest['godot_runtime_status'] = 'v11 awaiting user visual review.'
json.dump(manifest, open(OUT + '/animation-manifest.json', 'w'), indent=2)
json.dump(audit, open(ROOT + '/Assets/Characters/Source/handmade-v1/validation-v11.json', 'w'), indent=2)
result = {'audit': audit, 'files': sorted(os.listdir(OUT))}
