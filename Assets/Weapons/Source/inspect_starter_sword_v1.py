import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(r'D:\GodotProjects\dungeons-n-academics')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT / 'Assets/Weapons/Generated/tripo-out/starter-sword-v1-ec14d3ea/model.glb'))
report = {'objects': [], 'images': []}
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    mesh = obj.data
    mesh.calc_loop_triangles()
    points = [obj.matrix_world @ v.co for v in mesh.vertices]
    lo = [min(p[i] for p in points) for i in range(3)]
    hi = [max(p[i] for p in points) for i in range(3)]
    longest = max(range(3), key=lambda i: hi[i]-lo[i])
    bins = []
    for j in range(20):
        a = lo[longest] + (hi[longest]-lo[longest])*j/20
        b = lo[longest] + (hi[longest]-lo[longest])*(j+1)/20
        subset = [p for p in points if a <= p[longest] <= b]
        bins.append({'interval': [a,b], 'count': len(subset), 'widths': [max(p[i] for p in subset)-min(p[i] for p in subset) if subset else 0 for i in range(3)]})
    report['objects'].append({'name':obj.name, 'vertices':len(mesh.vertices), 'triangles':len(mesh.loop_triangles), 'bounds':[lo,hi], 'long_axis':longest, 'axis_bins':bins, 'materials':[m.name for m in mesh.materials], 'uv_layers':len(mesh.uv_layers)})
report['images'] = [{'name':image.name,'size':list(image.size),'packed':bool(image.packed_file)} for image in bpy.data.images]
(ROOT / 'Assets/Weapons/Source/starter-sword-v1-raw-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
