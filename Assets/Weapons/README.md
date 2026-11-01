# Starter weapons

Prepared Godot scenes:

| Weapon | Scene | Length | Triangles |
| --- | --- | ---: | ---: |
| Sword | `res://Scenes/Weapons/starter_sword.tscn` | 0.85 m | 957 |
| Spear | `res://Scenes/Weapons/starter_spear.tscn` | 1.8 m | 916 |

## Starter sword v1

Created October 31, 2026. Simple one-handed sword for the approved academy
adventurer characters: broad silver blade, purple guard, brown grip, gold pommel.

## Ready-to-use asset

- Godot scene: `res://Scenes/Weapons/starter_sword.tscn`
- Runtime mesh: `res://Assets/Weapons/Runtime/starter-sword-v1.glb`
- Editable source: `Source/starter-sword-v1.blend`
- Prepared preview: `Source/starter-sword-v1-prepared.png`
- Audit: `Source/starter-sword-v1-audit.json`

The scene has a grip-centered origin and direct `Grip` and `Tip` Marker3D children.
The default length is 0.85 metres from pommel to blade tip. Blade direction is
Godot +Y, with broad faces approximately facing +/-Z. The tip marker is at
local `(0, 0.7381387353, 0)` relative to the grip. The grip-to-pommel distance is
approximately 0.11186 m. Attach the scene root to a hand socket later and adjust
the socket rotation/scale to match the final character hand pose.

No player, rig, animation, collision, damage, or equipment logic was modified.
The sword is a rigid prop; no skinning is needed for ordinary hand attachment.

## Preparation and checks

- 957 triangles, 1,256 Blender vertices (UV/normal splits included).
- No zero-area faces; one unchanged UV map.
- One PBR material with embedded 2048x2048 base-color, normal, and combined
  occlusion/roughness/metallic images.
- Blade axis aligned using the steel surface; grip center identified from the
  brown grip and moved to the origin. Rotation/scale are applied to the mesh.
- Original Tripo download is preserved in `Generated/tripo-out/`.
- Prepared GLB was checked for embedded images and base-color, normal, and
  metallic/roughness texture connections. Godot MCP read the wrapper scene.
- Compared sampler export warning against the GLB: the prepared file uses one
  common sampler, all three images remain embedded, and PBR slots are retained.
- Source folder is excluded from Godot automatic import with `.gdignore`.

Preparation ran in a separate background Blender process because the live editor
had newer unsaved character rigging work open. The live character file was not
loaded, saved, or edited by the sword preparation scripts.

## Generation and billing

Tripo CLI 0.7.2, `tripo-p1` / API `P1-20260311`.
One `POST /v3/generation/text-to-model` call; requested `face_limit=1000`,
`texture=true`, `pbr=true`. No paid processing/conversion or rerolls.

Task: `ec14d3ea-a6bd-4fce-b9ea-4426066de0fa`.
Actual text-to-model cost: 40 API credits. Total: 40 API credits.
Verified remaining balance after generation: 740 available, 0 frozen.

Raw model, generation prompt, preview, and task record:
`Generated/tripo-out/starter-sword-v1-ec14d3ea/`.

The current character work has progressed beyond the older character handoff:
Blender was open on `Assets/Characters/Source/rigging-v1/siblings-rig-v010-reviewed.blend`
in `Brother_Rig_Validation_v1`, Pose Mode. Inspect live state before any later
attachment work; do not revert to the unrigged character checkpoint automatically.

## Starter spear v1

Created October 31, 2026 in the same weapon palette: silver spearhead, purple socket
and small guard, brown shaft, gold butt cap.

- Godot scene: `res://Scenes/Weapons/starter_spear.tscn`
- Runtime mesh: `res://Assets/Weapons/Runtime/starter-spear-v1.glb`
- Editable source: `Source/starter-spear-v1.blend`
- Prepared preview: `Source/starter-spear-v1-prepared.png`
- Audit: `Source/starter-spear-v1-audit.json`

Length is 1.8 metres, with the attachment origin on the shaft 0.6 m above the butt.
The scene exposes `Grip`, `Tip`, and `Butt` markers at `(0,0,0)`, `(0,1.2,0)`, and
`(0,-0.6,0)` respectively in Godot coordinates. The shaft/head point along +Y;
the head's width lies along X. Choose socket rotation and character hand poses
during attachment/animation work. This is a rigid prop with no skinning.

Validated: 916 triangles, 794 Blender vertices, zero zero-area faces, one unchanged
UV layer, one PBR material, and three embedded 2048x2048 images for base color,
normal, and combined occlusion/roughness/metallic. Exported GLB was checked for
all texture connections, one common sampler, and the expected marker positions.
The full prepared preview was visually inspected and the wrapper scene was read
through Godot MCP. Original download is preserved. Preparation used an isolated
background Blender process, preserving the live character rigging session.

Tripo CLI 0.7.2, `tripo-p1` / API `P1-20260311`; one text-to-model call with
`face_limit=1000`, `texture=true`, `pbr=true`.
Task: `a4f6bb68-fd9c-46c4-bf1b-bbe931739d84`.
Actual text-to-model cost: 40 API credits. Spear total: 40 API credits.
Verified balance after spear generation: 700 available, 0 frozen.
No paid conversion, rerolls, or mesh processing.

Raw files and generation prompt/task record:
`Generated/tripo-out/starter-spear-v1-a4f6bb68/`.

The sword and spear together cost 80 API credits. Neither has yet been attached
to the player or given combat/equipment logic.
