# Starter weapons

Prepared Godot scenes:

| Weapon | Scene | Length | Triangles |
| --- | --- | ---: | ---: |
| Sword | `res://Scenes/Weapons/starter_sword.tscn` | 0.85 m | 957 |
| Spear | `res://Scenes/Weapons/starter_spear.tscn` | 1.8 m | 916 |
| Bow v3 | `res://Scenes/Weapons/starter_bow.tscn` | 1.2 m high | 1,026 frame + 32 string |
| Arrow | `res://Scenes/Weapons/starter_arrow.tscn` | 0.65 m | 150 |

## Current bow: v3 (Tripo Workspace)

Integrated November 1, 2026 from the user's cleaner Workspace model at
`Generated/tripo-out/starter-bow-v3/starter_bow_v3.glb`. The supplied file is
unchanged. V3 supersedes v2 because the user found texture distortions in v2.

- Scene: `res://Scenes/Weapons/starter_bow.tscn`
- Prepared runtime: `res://Assets/Weapons/Runtime/starter-bow-v3.glb`
- Editable source: `Source/starter-bow-v3.blend`
- Previews: `Source/starter-bow-v3-prepared.png`, `Source/starter-bow-v3-back.png`,
  `Source/starter-bow-v3-end-on.png`
- Measurements: `Source/starter-bow-v3-audit.json`
- Reproduction: `Source/prepare_bow_v3.py` (refuses to overwrite outputs)

The frame retains all 1,026 triangles, 825 Blender vertices, its original UV map,
and three embedded 2048x2048 PBR images. Texture image payloads were verified
byte-for-byte identical after export. No decimation, unwrap, repaint, or paid API
processing was performed. Both frame and string have zero zero-area faces.

Height is 1.2 m, grip at origin, height along Godot +Y, firing along -Z, and draw
toward +Z. A separate 32-triangle string brings the total to 1,058 triangles.
Its `Draw` morph defaults to zero and moves the nock 0.25 m toward +Z at full draw,
keeping endpoints fixed. Grip, ArrowRest, StringNock, StringUpper, and StringLower
wrapper markers match v3. Markers are static and must follow draw state during
later gameplay integration. Limb deformation, player attachment, and archery
gameplay remain pending.

Preparation used isolated background Blender, preserving the live character
session. Workspace generation settings/cost were not supplied. Integration used
no API credits. Earlier v1/v2 file paths below are historical and may no longer
exist after the user's duplicate cleanup.

## Historical bow: v2 (image-based retry)

Created November 1, 2026. The user found a crosswise arrow fused through the v1
bow grip; that defect was missed in the initial review. V1 is superseded. The new
model was generated from the user-approved, bow-frame-only GPT Image reference,
then checked from front, back, and end-on angles for unwanted grip protrusions.

- Main scene (now points to v2): `res://Scenes/Weapons/starter_bow.tscn`
- Explicit v2 scene: `res://Scenes/Weapons/starter_bow_v2.tscn`
- Runtime: `res://Assets/Weapons/Runtime/starter-bow-v2.glb`
- Source: `Source/starter-bow-v2.blend`
- Previews: `Source/starter-bow-v2-prepared.png`, `Source/starter-bow-v2-back.png`,
  `Source/starter-bow-v2-end-on.png`
- Measurements: `Source/starter-bow-v2-audit.json`
- Approved input: `References/starter-bow-v2-frame.png`
- GPT Image prompt: `References/starter-bow-v2-frame-prompt.txt`

The 1.2 m bow frame has 962 triangles, 802 Blender vertices, one UV layer, and no
zero-area faces. Its generated UV coordinates are exactly preserved; no decimation,
new unwrap, or texture repaint was needed. The separate 32-triangle string brings
the total to 994. The runtime GLB retains embedded PBR images and a `Draw` string
morph, saved at weight 0. Bow height is Godot +Y and firing direction -Z; full
Draw moves the nocking point 0.25 m toward +Z. Limb deformation and character
animations are still pending.

Main and explicit v2 scenes have matching updated Grip, ArrowRest, StringNock,
StringUpper, and StringLower markers. Rest nock is approximately
`(0.003593, 0.035, 0.322613)`; arrow rest is `(0.003593, 0.035, 0)`. As in v1, these
wrapper markers are static and need to follow animation/gameplay draw state later.

The v1 GLB/source remain intact. Its original wrapper is preserved as
`res://Scenes/Weapons/starter_bow_v1.tscn` for reference only. The sword, spear,
arrow, and live character rigging session were not modified by the retry.

Tripo `tripo-p1` / `P1-20260311`, one image-to-model task:
`a9192e29-afd3-4c1a-85c2-9f910f7dd22b`. Actual cost: 50 API credits; local
preparation cost: 0. Verified remaining balance: 570 available, 0 frozen.
Raw download/task record: `Generated/tripo-out/starter-bow-v2-a9192e29/`.
Total API spend on all weapon generations including this retry: 210 credits.

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

## Starter bow and arrow v1

Historical generation record: the bow in this section is superseded by v2 above
because it contained a fused arrow. The locally corrected arrow remains current.

Created November 1, 2026 to match the brown, purple, silver, and gold weapon set.

### Bow

- Legacy scene: `res://Scenes/Weapons/starter_bow_v1.tscn`
- Runtime: `res://Assets/Weapons/Runtime/starter-bow-v1.glb`
- Source: `Source/starter-bow-v1.blend`
- Preview: `Source/starter-bow-v1-prepared.png`
- Measurements/markers: `Source/starter-bow-v1-audit.json`

The bow is 1.2 m tall, with grip at the root, height along Godot +Y, firing along
Godot -Z, and draw motion toward +Z. The generated frame was 1,012 triangles,
slightly over the requested 1,000, so a small free local budget reduction produced
984 triangles. Its UV map and embedded 2K base-color/normal/ORM textures are retained;
the reduction interpolates affected UV corners, rather than globally re-unwrapping.
The original download is preserved. A separate flax-colored 32-triangle bowstring
brings the combined bow to 1,016 triangles, within the approved frame-plus-string
budget. Neither mesh has zero-area faces.

The `BowString` mesh in the runtime GLB has a `Draw` blend shape: 0 is straight/rest,
1 moves the center 0.25 m toward Godot +Z while keeping the limb endpoints fixed.
Both the source and GLB are saved at 0. Export checks confirmed the morph target,
zero default weight, and expected displacement bounds. This is a string-only
preparation: limb deformation and an actual character draw/release animation have
not been authored.

Stable wrapper markers: `Grip`, `ArrowRest`, `StringNock`, `StringUpper`, `StringLower`.
Rest nock is approximately `(0, 0.035, 0.20638)` and arrow rest `(0, 0.035, 0)`.
The wrapper markers are static: later animation/gameplay must update the nock
position along with the Draw weight when positioning an arrow on the drawn string.

### Arrow

- Scene: `res://Scenes/Weapons/starter_arrow.tscn`
- Runtime: `res://Assets/Weapons/Runtime/starter-arrow-v1.glb`
- Source: `Source/starter-arrow-v1.blend`
- Preview: `Source/starter-arrow-v1-prepared.png`
- Audit: `Source/starter-arrow-v1-audit.json`

Tripo's paid result put the purple fletching near the arrowhead and was unsuitable
as a runtime arrow. It was not silently rerolled. The final small prop was rebuilt
locally in Blender in the matching palette, with a straight shaft, triangular steel
head, three purple tail vanes, and a genuinely notched gold nock. The rejected raw
download remains for provenance. The final arrow uses 150 triangles, 93 vertices,
one material, one UV map, and compact embedded 64x64 base-color and ORM palette
atlases. This local correction differs from the generated 2K-textured result and
cost no additional credits.

Length is 0.65 m; nock is the root origin and flight direction is Godot -Z.
Wrapper markers: `Nock` at origin, `Tip` at `(0,0,-0.65)`, `Grip` at `(0,0,-0.3)`.
To show an arrow on the bow, align the arrow root/nock with the bow's string nock;
both already share the same forward convention. Set socket rotation for the
character hand during integration.

### Archery validation and billing

Both source files and runtime GLBs were prepared in isolated background Blender
processes. The live character rigging session was not edited or saved. Prepared
previews were visually inspected, embedded GLB images/materials/markers checked,
and wrapper scenes read through Godot MCP. The draw morph was checked in the GLB.
The assets have no projectile, collision, damage, or equipment scripts yet.

| Tripo P1 text-to-model step | Task ID | Actual API credits |
| --- | --- | ---: |
| Bow | `288f15aa-d82e-4dc8-a95f-34f7c4c790b5` | 40 |
| Arrow | `ad1b4ba5-f006-48e0-a29e-6eaf3fc09d7a` | 40 |
| Archery pair total | | 80 |

Verified balance after these jobs: 620 available, 0 frozen. All four starter weapon
generations together cost 160 API credits. No paid processing or rerolls were used.

Raw downloads and prompts/task records:
`Generated/tripo-out/starter-bow-v1-288f15aa/` and
`Generated/tripo-out/starter-arrow-v1-ad1b4ba5/`.
Reproduction scripts: `Source/prepare_archery_v1.py`, then `Source/align_bow_v1.py`
on the bow source. The preparation script refuses to overwrite its existing outputs;
use new versioned destinations for future changes.
