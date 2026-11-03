# Handmade sibling meshes v1 — November 2, 2026

The Tripo-generated Brother and Sister meshes are replaced with meshes modelled in Blender from
the front concept sheets (`~/Downloads/Brother_Character_Reference`, `Sister_Character_Reference`)
and the side sheets supplied for the refinement pass. Both are packed into the blend as
`*_ConceptFront` / `*_ConceptSide` image empties, scaled to 1.8 m and aligned to the rig (side
sheets: 1445 / 1432 px = 1.8 m, image x 488 / 485 px = rig y 0). The approved v10 rigs and all
eight clips are unchanged; only the skinned mesh differs.

Working file: `siblings-handmade-v1.blend` (saved from the open `dungeoncharacter.blend` session,
which was left untouched). Blend files are not tracked in git, and this folder sits under
`Source/.gdignore`.

## Runtime

`Assets/Characters/Animated/v11/` holds `brother-animations-v11.glb`, `sister-animations-v11.glb`
and a copy of the v10 manifest (sockets, timings and events identical). `Scenes/player.tscn`,
`Scripts/ExplorationCharacterVisual.cs` and the animation preview scene now load v11.
`Animated/v10` is untouched: pointing those three references back restores the Tripo look.

| | Brother | Sister |
| --- | ---: | ---: |
| Vertices / triangles | 6,313 / 11,316 | 9,065 / 16,754 |
| Materials (flat colour, no textures) | 28 | 29 |
| Joints / clips | 30 / 8 | 30 / 8 |
| GLB size (v10 was ~5 MB with 2K maps) | 1.3 MB | 1.9 MB |

Joint names and clip durations match v10 exactly. `validation-v11.json` records per-clip
finite poses and mesh floor clearance (no vertex below Z=0 in any frame) and the 4-influence,
zero-unweighted skin audit.

## How the meshes are built

All modelling is done in rig-local rest space (1.8 m, feet at Z=0, -Y forward) by scripts run
through the Blender MCP; each rerun rebuilds its objects in place.

- `hmlib.py`: superellipse vertex rings, lofting, curved clumps and long locks, decals snapped
  onto a surface (BVH ray cast, offset along the surface normal), materials.
- `parts.py`: head (neck-to-crown rings with chin, lip and nose shaping), ears, nose with alar
  wings and nostril pits, layered face decals (dark eye rim, white, two-tone iris, pupil, two
  glints, lower lid line, upper lid crease and lash band, brows, upper and lower lip shading
  round the mouth line with corner creases, blush), short spiky hair, long wavy hair.
  Polishing pass (Nov 2): the face and hand detail above was added on top of the first build.
- `body.py`: torso and neckline rings, sleeves (`sleeve`: each closed at the top by a rounded
  shoulder cap that continues back past the joint and sinks into the torso), forearms, hands, skirt with front slit and
  pointed hem, belts, boots. Hands (`hand` / `_digit`): a rounded back and lightly cupped palm,
  a thenar pad under the thumb, and jointed fingers along the finger bones with knuckle swell,
  finger pads, a slight splay and a bevelled nail on each tip (material `HM_*_Nail`). Each boot is one piece
  (`BootShape`): horizontal rings read from a side-profile table (back edge, front edge and
  half widths per height) so the front walks from the shaft down the instep to the toe box,
  turned with the rest-pose foot bone. Platform sole with a separate heel block and toe pad,
  folded cuff, and straps that follow the upper's surface (tilted or crossed loops).
- `brother_head.py`, `brother_hair.py`, `brother_body.py` and the matching `sister_*.py` hold
  every proportion and colour, taken from the concept sheets (1454 / 1435 px = 1.8 m).
- `skin.py`: `assemble(label)` joins the parts into `<Label>_HM_Mesh_v1` (collection `HM_Final`,
  with a Smart UV layout for future texture painting); `skin(label, dz)` transfers weights by
  nearest surface from the approved v10 meshes (`*_AnimMesh_v1`, kept hidden in `HM_TripoGhost`)
  so the tunic-helper, hem and joint blends carry over, then makes head, face and hair rigid to
  `head` with a height-based neck/chest blend, and limits each vertex to 4 normalised weights.
- `export_v11.py`: same glTF settings and NLA bake as `animation-v10/export_validate.py`.

Rebuild order: the six character scripts, then `skin.py` (`assemble` + `skin` per character,
`dz` 0 for Brother, 0.012 for Sister), then `export_v11.py`, then a Godot reimport.

Manual edits made directly on a part object (`HM_Brother` / `HM_Sister` collections) survive
`assemble`, but rerunning that part's script discards them.

## Known limitations

- Face, legs, boots and hair depth follow the side sheets; there is still no back-view art,
  so the back of the hair and costume is extrapolated.
- Sister's long hair is rigid to the head, as before; extreme head turns can touch the shoulders.
- Skirt and sleeve weights come from the v10 meshes. They hold in all eight clips, but deep
  crouch or seated poses were not cleared for the v10 rig and are not cleared here either.
- No facial rig; the face is decal geometry, so expressions would need blend shapes later.
- Faces are flat colour; a painted texture pass can use the UV layout already present.
