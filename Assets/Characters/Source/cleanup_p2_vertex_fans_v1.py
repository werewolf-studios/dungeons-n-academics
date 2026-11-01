import bpy
import bmesh
from collections import defaultdict

def face_fans(vertex):
    remaining=set(vertex.link_faces)
    fans=[]
    while remaining:
        fan=[]
        pending=[remaining.pop()]
        while pending:
            face=pending.pop()
            fan.append(face)
            for edge in face.edges:
                if vertex not in edge.verts:
                    continue
                for adjacent in edge.link_faces:
                    if adjacent in remaining:
                        remaining.remove(adjacent)
                        pending.append(adjacent)
        fans.append(fan)
    return fans

def coord_key(co):
    return tuple(round(float(value),8) for value in co)

result={'vertex_fan_cleanup':[]}
for name in ['Brother_Clean_v1','Sister_Clean_v1']:
    obj=bpy.data.objects[name]
    mesh=obj.data
    original_positions=set(coord_key(v.co) for v in mesh.vertices)
    corner_data=defaultdict(list)
    position_data=defaultdict(list)
    for polygon in mesh.polygons:
        for index in polygon.loop_indices:
            loop=mesh.loops[index]
            position=coord_key(mesh.vertices[loop.vertex_index].co)
            uv=mesh.uv_layers.active.data[index].uv.copy()
            normal=mesh.corner_normals[index].vector.copy()
            key=position+coord_key(uv)
            corner_data[key].append((normal,polygon.normal.copy()))
            position_data[position].append((uv,normal,polygon.normal.copy()))
    bm=bmesh.new()
    bm.from_mesh(mesh)
    bowties=[v for v in bm.verts if len(face_fans(v))>1]
    for vertex in bowties:
        for fan in face_fans(vertex)[1:]:
            separated=[bmesh.utils.face_vert_separate(face,vertex) for face in fan]
            bmesh.ops.pointmerge(bm,verts=separated,merge_co=vertex.co)
    remaining_bowties=sum(len(face_fans(vertex))>1 for vertex in bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    normals=[None]*len(mesh.loops)
    unmatched=0
    for polygon in mesh.polygons:
        for index in polygon.loop_indices:
            loop=mesh.loops[index]
            position=coord_key(mesh.vertices[loop.vertex_index].co)
            uv=mesh.uv_layers.active.data[index].uv
            candidates=corner_data.get(position+coord_key(uv),[])
            if candidates:
                normals[index]=tuple(max(candidates,key=lambda pair:pair[1].dot(polygon.normal))[0])
            else:
                uv,normal,_=min(position_data[position],key=lambda item:(item[0]-uv).length_squared)
                mesh.uv_layers.active.data[index].uv=uv
                normals[index]=tuple(normal)
                unmatched+=1
    mesh.normals_split_custom_set(normals)
    mesh.update()
    mesh.calc_loop_triangles()
    bm=bmesh.new()
    bm.from_mesh(mesh)
    audit={'object':name,'separated_bowtie_vertices':len(bowties),'remaining_bowtie_vertices':remaining_bowties,
        'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'quads':sum(len(p.vertices)==4 for p in mesh.polygons),
        'runtime_triangles':len(mesh.loop_triangles),'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),
        'overconnected_edges':sum(len(e.link_faces)>2 for e in bm.edges),
        'boundary_edges':sum(e.is_boundary for e in bm.edges),
        'new_or_moved_vertex_positions':sum(coord_key(v.co) not in original_positions for v in mesh.vertices),
        'restored_interpolated_uv_corners':unmatched,'custom_normals':mesh.has_custom_normals}
    bm.free()
    if audit['remaining_bowtie_vertices'] or audit['new_or_moved_vertex_positions'] or audit['zero_area_faces'] or audit['overconnected_edges']:
        raise RuntimeError('Vertex fan cleanup validation failed: '+str(audit))
    result['vertex_fan_cleanup'].append(audit)

