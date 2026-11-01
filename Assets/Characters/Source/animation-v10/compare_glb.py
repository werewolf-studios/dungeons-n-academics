# Compares raw animation channels between the v9 and v10 GLBs, standard library only.
import json, os, struct
ROOT = 'D:/GodotProjects/dungeons-n-academics/Assets/Characters/Animated/'
OUT = 'D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v10/glb-v9-v10-comparison.json'
COMPONENTS = {'SCALAR': 1, 'VEC3': 3, 'VEC4': 4}


def load(path):
    with open(path, 'rb') as f:
        data = f.read()
    length = struct.unpack('<I', data[12:16])[0]
    doc = json.loads(data[20:20 + length])
    return doc, data[20 + length + 8:]


def read(doc, blob, index):
    acc = doc['accessors'][index]
    view = doc['bufferViews'][acc['bufferView']]
    start = view.get('byteOffset', 0) + acc.get('byteOffset', 0)
    n = COMPONENTS[acc['type']]
    return struct.unpack_from('<%df' % (n * acc['count']), blob, start), n


def clips(doc, blob):
    names = [n.get('name') for n in doc['nodes']]
    out = {}
    for anim in doc['animations']:
        channels = {}
        for c in anim['channels']:
            sampler = anim['samplers'][c['sampler']]
            times, _ = read(doc, blob, sampler['input'])
            values, n = read(doc, blob, sampler['output'])
            channels[(names[c['target']['node']], c['target']['path'])] = (times, values, n)
        out[anim['name']] = channels
    return out


report = {}
for label in ['brother', 'sister']:
    a_doc, a_blob = load(ROOT + f'v9/{label}-animations-v9.glb')
    b_doc, b_blob = load(ROOT + f'v10/{label}-animations-v10.glb')
    a, b = clips(a_doc, a_blob), clips(b_doc, b_blob)
    report[label] = {'clip_names_v10': sorted(b), 'node_count_same': len(a_doc['nodes']) == len(b_doc['nodes'])}
    for name in sorted(b):
        worst = 0
        changed = set()
        for key, (times, values, n) in b[name].items():
            if key not in a.get(name, {}):
                changed.add(key[0])
                worst = 9
                continue
            t0, v0, _ = a[name][key]
            if len(v0) != len(values):
                changed.add(key[0])
                worst = 9
                continue
            d = max((abs(p - q) for p, q in zip(values, v0)), default=0)
            worst = max(worst, d)
            if d > 1e-4:
                changed.add(key[0])
        duration = max(c[0][-1] for c in b[name].values())
        report[label][name] = {'duration_s': round(duration, 4), 'frames': round(duration * 24), 'max_channel_difference': round(worst, 6), 'bones_changed': len(changed)}
json.dump(report, open(OUT, 'w'), indent=2)
for label, rows in report.items():
    print(label, rows['clip_names_v10'], 'nodes same', rows['node_count_same'])
    for name, row in rows.items():
        if isinstance(row, dict):
            print('  ', name, row)
