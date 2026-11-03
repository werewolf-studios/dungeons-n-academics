# Assemble each sibling's handmade parts into one skinned mesh on the existing *_AnimRig_v1.
# Clothing and limb weights are transferred (barycentric, nearest surface) from the approved
# v10 Tripo meshes, so the validated tunic-helper, hem and joint blends carry over. Head, face
# and hair are then made rigid to the head with a painted neck blend, and every vertex is
# limited to 4 normalized influences (linear blend skinning, as Godot uses).
import importlib, sys
sys.path.insert(0, 'D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/handmade-v1')
import bpy, bmesh
from mathutils.bvhtree import BVHTree
from mathutils.interpolate import poly_3d_calc
import hmlib as H
importlib.reload(H)

PART_IDS = {'Head': 1, 'Ears': 2, 'Face': 3, 'Nose': 4, 'Hair': 5, 'Tunic': 6, 'TunicTrim': 7, 'Skirt': 8,
            'Accessories': 9, 'Arms': 10, 'Pants': 11, 'Leggings': 11, 'Boots': 12, 'BootStraps': 13}
HEAD_PARTS = {2, 3, 4, 5}
FINAL = 'HM_Final'


def final_collection():
    c = bpy.data.collections.get(FINAL)
    if c is None:
        c = bpy.data.collections.new(FINAL)
        bpy.data.collections['Handmade_v1'].children.link(c)
    # joining needs selectable objects, so the collection must be visible in the view layer
    stack = [bpy.context.view_layer.layer_collection]
    while stack:
        lc = stack.pop()
        if lc.collection == c:
            lc.hide_viewport = False
            lc.exclude = False
        stack.extend(lc.children)
    return c


def assemble(label):
    rig = H.rig(label)
    name = label + '_HM_Mesh_v1'
    # objects created by this script on a previous run (the joined mesh and any unjoined copies)
    for old in [o for o in bpy.data.objects if o.name == name or o.name.startswith(name + '_')]:
        me = old.data
        bpy.data.objects.remove(old, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    copies = []
    for part, pid in PART_IDS.items():
        src = bpy.data.objects.get(label + '_' + part)
        if src is None:
            continue
        me = src.data.copy()
        a = me.attributes.new('hm_part', 'INT', 'POINT')
        a.data.foreach_set('value', [pid] * len(me.vertices))
        ob = bpy.data.objects.new(name if not copies else name + '_' + part, me)
        final_collection().objects.link(ob)
        copies.append(ob)
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for ob in copies:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    bpy.ops.object.join()
    ob = copies[0]
    ob.name = name
    ob.data.name = name
    ob.parent = rig
    ob.matrix_parent_inverse.identity()
    ob.matrix_basis.identity()
    # light UV layout so the materials can later be swapped for painted textures
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.004)
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob


def head_blend(z, dz):
    """Weights for the head mesh (neck, upper chest) by height; dz shifts for the sister rig."""
    z -= dz
    if z <= 1.30:
        return {'chest': 0.8, 'neck': 0.2}
    if z <= 1.38:
        s = (z - 1.30) / 0.08
        return {'chest': 0.8 * (1 - s), 'neck': 0.2 + 0.8 * s}
    if z <= 1.44:
        s = (z - 1.38) / 0.06
        return {'neck': 1 - 0.6 * s, 'head': 0.6 * s}
    if z <= 1.47:
        s = (z - 1.44) / 0.03
        return {'neck': 0.4 * (1 - s), 'head': 0.6 + 0.4 * s}
    return {'head': 1.0}


def skin(label, dz=0.0):
    ob = bpy.data.objects[label + '_HM_Mesh_v1']
    rig = H.rig(label)
    ghost = bpy.data.objects[label + '_AnimMesh_v1']
    gnames = [g.name for g in ghost.vertex_groups]
    gb = bmesh.new()
    gb.from_mesh(ghost.data)
    gb.faces.ensure_lookup_table()
    dl = gb.verts.layers.deform.active
    tree = BVHTree.FromBMesh(gb)
    part = ob.data.attributes['hm_part'].data
    weights = []
    for v in ob.data.vertices:
        pid = part[v.index].value
        if pid in HEAD_PARTS:
            w = {'head': 1.0}
        elif pid == 1:
            w = head_blend(v.co.z, dz)
        else:
            loc, nrm, fi, d = tree.find_nearest(v.co)
            f = gb.faces[fi]
            bary = poly_3d_calc([l.vert.co for l in f.loops], loc)
            w = {}
            for b, l in zip(bary, f.loops):
                for gi, gw in l.vert[dl].items():
                    w[gnames[gi]] = w.get(gnames[gi], 0.0) + gw * b
        top = sorted(((k, x) for k, x in w.items() if x > 0.01), key=lambda kv: -kv[1])[:4]
        s = sum(x for _, x in top)
        weights.append([(k, x / s) for k, x in top])
    gb.free()
    ob.vertex_groups.clear()
    for b in rig.data.bones:
        if b.use_deform:
            ob.vertex_groups.new(name=b.name)
    for v, ws in zip(ob.data.vertices, weights):
        for k, x in ws:
            ob.vertex_groups[k].add([v.index], x, 'REPLACE')
    ob.modifiers.clear()
    m = ob.modifiers.new('Armature', 'ARMATURE')
    m.object = rig
    m.use_deform_preserve_volume = False
    m.use_vertex_groups = True
    unweighted = sum(1 for ws in weights if not ws)
    return {'verts': len(ob.data.vertices), 'unweighted': unweighted,
            'max_influences': max(len(ws) for ws in weights)}
