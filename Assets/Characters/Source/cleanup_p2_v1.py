import bpy
import bmesh
from collections import Counter, defaultdict
from mathutils import Vector

source_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH' and obj.name.startswith(('Brother_P2_', 'Sister_P2_'))]
if len(source_objects) != 2:
    raise RuntimeError('Expected exactly the two original P2 test meshes')
if bpy.data.collections.get('P2_Cleanup_v1'):
    raise RuntimeError('Cleanup collection already exists; inspect before rerunning')

def coordinate_key(co):
    return tuple(round(float(value), 8) for value in co)

def corner_key(mesh, loop):
    uv = mesh.uv_layers.active.data[loop.index].uv if mesh.uv_layers.active else (0,0)
    return coordinate_key(mesh.vertices[loop.vertex_index].co) + tuple(round(float(value),8) for value in uv)

def measure(mesh):
    mesh.calc_loop_triangles()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    result = {
        'vertices':len(mesh.vertices), 'faces':len(mesh.polygons),
        'quads':sum(len(face.vertices)==4 for face in mesh.polygons),
        'triangle_faces':sum(len(face.vertices)==3 for face in mesh.polygons),
        'ngons':sum(len(face.vertices)>4 for face in mesh.polygons),
        'runtime_triangles':len(mesh.loop_triangles),
        'zero_area_faces':sum(face.calc_area()<1e-12 for face in bm.faces),
        'overconnected_edges':sum(len(edge.link_faces)>2 for edge in bm.edges),
        'boundary_edges':sum(edge.is_boundary for edge in bm.edges),
        'wire_edges':sum(not edge.link_faces for edge in bm.edges),
        'loose_vertices':sum(not vertex.link_edges for vertex in bm.verts),
        'inconsistent_winding_edges':sum(edge.is_manifold and not edge.is_contiguous for edge in bm.edges),
        'uv_layers':len(mesh.uv_layers), 'custom_normals':mesh.has_custom_normals,
    }
    bm.free()
    return result

collection = bpy.data.collections.new('P2_Cleanup_v1')
bpy.context.scene.collection.children.link(collection)
report = []
for source in sorted(source_objects,key=lambda obj:obj.name):
    label = 'Brother' if source.name.startswith('Brother') else 'Sister'
    source_mesh = source.data
    before = measure(source_mesh)
    source_coordinates = set(coordinate_key(vertex.co) for vertex in source_mesh.vertices)
    original_corners = defaultdict(list)
    corners_by_position = defaultdict(list)
    for polygon in source_mesh.polygons:
        for index in polygon.loop_indices:
            loop = source_mesh.loops[index]
            original_corners[corner_key(source_mesh,loop)].append(
                (source_mesh.corner_normals[index].vector.copy(),polygon.normal.copy()))
            uv = source_mesh.uv_layers.active.data[index].uv.copy()
            corners_by_position[coordinate_key(source_mesh.vertices[loop.vertex_index].co)].append((uv,source_mesh.corner_normals[index].vector.copy(),polygon.normal.copy()))
    working = source.copy()
    working.data = source_mesh.copy()
    working.name = label + '_Clean_v1'
    working.data.name = label + '_CleanMesh_v1'
    collection.objects.link(working)
    bm = bmesh.new()
    bm.from_mesh(working.data)
    redundant = []
    for face in bm.faces:
        if len(face.verts)!=3:
            continue
        candidates = set(face.verts[0].link_faces)
        for vertex in face.verts[1:]:
            candidates.intersection_update(vertex.link_faces)
        if any(len(other.verts)==4 and face.normal.dot(other.normal)>.99 for other in candidates):
            redundant.append(face)
    removed_count = len(redundant)
    if redundant:
        bmesh.ops.delete(bm,geom=redundant,context='FACES_ONLY')
    bmesh.ops.dissolve_degenerate(bm,dist=0.000001,edges=list(bm.edges))
    ngons = [face for face in bm.faces if len(face.verts)>4]
    retriangulated_count = len(ngons)
    if ngons:
        bmesh.ops.triangulate(bm,faces=ngons,quad_method='BEAUTY',ngon_method='EAR_CLIP')
    branching = [edge for edge in bm.edges if len(edge.link_faces)>2]
    split_count = len(branching)
    if branching:
        bmesh.ops.split_edges(bm,edges=branching)
    wire = [edge for edge in bm.edges if not edge.link_faces]
    if wire:
        bmesh.ops.delete(bm,geom=wire,context='EDGES')
    loose = [vertex for vertex in bm.verts if not vertex.link_faces]
    if loose:
        bmesh.ops.delete(bm,geom=loose,context='VERTS')
    bm.normal_update()
    bm.to_mesh(working.data)
    bm.free()
    working.data.update()
    restored_normals = [None]*len(working.data.loops)
    unmatched_uv_corners = 0
    restored_uv_corners = 0
    for polygon in working.data.polygons:
        for index in polygon.loop_indices:
            loop = working.data.loops[index]
            candidates = original_corners.get(corner_key(working.data,loop),[])
            if candidates:
                normal, _ = max(candidates,key=lambda pair:pair[1].dot(polygon.normal))
                restored_normals[index] = tuple(normal)
            else:
                position_candidates = corners_by_position.get(coordinate_key(working.data.vertices[loop.vertex_index].co),[])
                if position_candidates:
                    current_uv = working.data.uv_layers.active.data[index].uv
                    uv, normal, _ = min(position_candidates,key=lambda item:(item[0]-current_uv).length_squared)
                    working.data.uv_layers.active.data[index].uv = uv
                    restored_normals[index] = tuple(normal)
                    restored_uv_corners += 1
                else:
                    restored_normals[index] = tuple(polygon.normal)
                    unmatched_uv_corners += 1
    working.data.normals_split_custom_set(restored_normals)
    working.data.update()
    after = measure(working.data)
    moved_vertices = sum(coordinate_key(vertex.co) not in source_coordinates for vertex in working.data.vertices)
    checks = {
        'new_or_moved_vertex_positions':moved_vertices,
        'unmatched_uv_corners':unmatched_uv_corners,
        'interpolated_uv_corners_restored':restored_uv_corners,
        'original_mesh_unchanged':measure(source_mesh)==before,
        'materials_preserved':[slot.material for slot in source.material_slots]==[slot.material for slot in working.material_slots],
    }
    if moved_vertices or unmatched_uv_corners or after['zero_area_faces'] or after['overconnected_edges'] or after['ngons'] or after['runtime_triangles']>12000:
        raise RuntimeError('Cleanup validation failed for '+label+': '+str(checks)+' '+str(after))
    working['cleanup_source_object'] = source.name
    working['cleanup_source_task'] = '3cc91a2e-8ad2-40cb-9244-f194e2138b01' if label=='Brother' else '457309d5-778e-48bd-9193-48b082b3eeae'
    working['cleanup_version'] = 'v1'
    source.hide_set(True)
    source.hide_render = True
    working.hide_set(False)
    working.hide_render = False
    report.append({'character':label,'source_object':source.name,'clean_object':working.name,
        'changes':{'removed_redundant_triangles':removed_count,'degenerate_dissolve_tolerance':0.000001,
        'retriangulated_local_ngons':retriangulated_count,'split_branching_edges':split_count},
        'before':before,'after':after,'checks':checks})
for obj in bpy.context.selected_objects:
    obj.select_set(False)
active = bpy.data.objects['Brother_Clean_v1']
active.select_set(True)
bpy.context.view_layer.objects.active = active
bpy.context.view_layer.update()
result = {'cleanup':report,'source_geometry_preserved':True,'paid_operations':0}

