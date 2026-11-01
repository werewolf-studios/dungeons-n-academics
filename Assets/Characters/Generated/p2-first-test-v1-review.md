# P2 first character test

Generated 2026-10-30 from the approved separate front A-pose references.
Model: CLI `tripo-p2`, API `P2-20260801`. One image-to-model task per character.
Requested `face_limit=6000`, `quad=true`, `texture=true`, `pbr=true`.
FBX preserves the generated mixed quad/triangle topology. No paid conversion,
rigging, animation, retopology, or rerolls were submitted.

## Results measured in Blender

| Measurement | Brother | Sister |
| --- | ---: | ---: |
| Vertices | 6,162 | 6,098 |
| Faces | 6,699 | 6,092 |
| Quads | 5,103 | 5,196 |
| Triangle faces | 1,596 | 896 |
| Quad percentage by face count | 76.18% | 85.29% |
| Triangles after triangulation | 11,802 | 11,288 |
| Connected mesh islands | 17 | 37 |
| Boundary edges | 492 | 881 |
| Non-manifold edges excluding boundaries | 0 | 20 |
| Near-zero-area faces (area < 1e-12) | 2 | 2 |
| Maximum vertex valence | 54 | 14 |
| UV layers | 1 | 1 |
| Materials | 1 | 1 |
| Armatures | 0 | 0 |

Both have embedded 2048x2048 color, roughness, metallic, and normal textures.
Both imported at approximately 1 Blender unit tall; intended gameplay height
and facing still need normalization before rigging/export.

These are useful visual candidates, not deformation-validated final characters.
The 6,000 setting did not produce an all-quad 6,000-face mesh: both include
triangles, with total triangulated counts below the intended 12,000 budget.
Disconnected islands and boundaries may represent separate clothing, hair,
or open shells and are not individually proof of a visible defect. Inspect
joint regions, intersecting surfaces, fingers, open boundaries, degenerate
faces, and the sister's non-manifold edges before skinning. A virtual weld at
1e-6 on analysis copies merged no vertices and left these counts unchanged.
No source mesh topology has been altered.

## Local artifacts

- Brother FBX: `tripo-out/brother-p2-test-v1-3cc91a2e/model.fbx`
- Sister FBX: `tripo-out/sister-p2-test-v1-457309d5/model.fbx`
- Each task folder includes `preview.png`, `rendered_image.webp`, and `task.json`.
- Blender review copy: `../Source/p2-first-test-v1.blend`.
- `Source/.gdignore` excludes editable source files from Godot's automatic import.
- Imported Blender collections: `P2_Test_Brother_v1` and `P2_Test_Sister_v1`.
- Review-only display rotation and spacing do not modify the downloaded FBXs.

## Actual billing

| Step | Task ID | API credits |
| --- | --- | ---: |
| Brother image-to-model | `3cc91a2e-8ad2-40cb-9244-f194e2138b01` | 110 |
| Sister image-to-model | `457309d5-778e-48bd-9193-48b082b3eeae` | 110 |
| Total | | 220 |

Verified balance after both tasks: 780 available, 0 frozen.
