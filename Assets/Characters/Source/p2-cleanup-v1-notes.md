# P2 character cleanup v1

Cleaned working copies: `Brother_Clean_v1` and `Sister_Clean_v1`, in collection
`P2_Cleanup_v1`. The original generated meshes remain in their original collections,
hidden for comparison. Original FBXs and the first-test blend are preserved.

## Changes

- Resolved two zero-area faces per character with local degenerate dissolve.
- Retriangulated only the local n-gons created by that repair; retained the rest of
  the mixed quad/triangle topology.
- Removed eight redundant sister mouth triangles whose vertex sets were contained
  in existing, similarly oriented quads.
- Separated the sister's two remaining branching edges, and four bow-tie vertices
  where otherwise separate surface fans touched at one vertex.
- Preserved all vertex positions. Separation added eight coincident vertices to
  the sister; no silhouette vertices were moved or removed.
- Preserved one UV layer, one material, embedded 2K PBR textures, and original
  custom shading normals per character. Restored five UV corners to their original
  source values after the local degenerate dissolve interpolated them.
- Retained intentional/open surface boundaries and separate hair, facial,
  clothing, and footwear shells. No blanket hole fill, decimation, smoothing,
  global weld, remesh, or texture rebake was applied.

## Validation

| Measurement | Brother | Sister |
| --- | ---: | ---: |
| Vertices | 6,162 | 6,106 |
| Faces | 6,699 | 6,086 |
| Quads | 5,103 | 5,194 |
| Triangle faces | 1,596 | 892 |
| Runtime triangles | 11,802 | 11,280 |
| Zero-area faces | 0 | 0 |
| Edges shared by more than two faces | 0 | 0 |
| Bow-tie vertices | 0 | 0 |
| Inconsistent manifold edge winding | 0 | 0 |
| Loose vertices / wire edges | 0 / 0 | 0 / 0 |
| Open boundary edges | 492 | 884 |
| Vertex positions moved | 0 | 0 |

Both remain under 12,000 runtime triangles. These are open game-character shells,
not watertight printing meshes. Rigging, weight painting, and deformation tests
are still required; cleanup alone does not validate bending at joints.

## Review artifacts

- `p2-cleanup-v1.blend`: saved copy with originals and cleaned working copies.
- `p2-cleanup-v1-before.png` / `p2-cleanup-v1-after.png`: matching studio renders,
  visually checked for preserved silhouettes, materials, and texture appearance.
- Blender scene `P2_Cleanup_Validation`: repeatable comparison camera and lights,
  with Before/After copies sharing the respective source or clean mesh data.
- `p2-cleanup-v1-audit.json`: machine-readable before/after measurements.
- Reproduction scripts: run `cleanup_p2_v1.py` on the original review scene, then
  `cleanup_p2_vertex_fans_v1.py`. The first script refuses to run if its cleanup
  collection already exists. Do not run on already cleaned meshes.

The editable Source folder is excluded from Godot import by `.gdignore`.
No game logic, rigging, animation, or paid generation was changed in this step.
Additional Tripo/Genex credits spent: 0. Last verified Tripo balance: 780.
