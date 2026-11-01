# Character pipeline handoff

Updated: October 30, 2026. Project: `D:/GodotProjects/dungeons-n-academics`.

## Next task and approved direction

Continue in Blender with rigging, weight painting, and deformation tests for both
approved characters. Complete and validate the brother first, then reuse the
proven bone hierarchy and approach for the sister. Rigging has not started:
the meshes have no armatures, skin weights, or animations.

The user approved the designs, initial P2 models, cleanup, and the brother's final
smooth-tunic repair. Do not regenerate or redesign the characters. The latest
approval was: "The male character looks great now."

The game is a Godot educational dungeon crawler. The heroes are teenage siblings:
stylized/cartoon proportions, warm brown loose hair, similar faces, light tunics,
distinct shoes, matching gold leaf clasps. Brother: lavender/deep purple, trousers,
brown cuffed boots and side pouch. Sister: burgundy/violet, opaque leggings,
burgundy/violet strapped high-top footwear. The approved style is simplified
game art, with chunky shapes rather than cinematic animated-film detail.

## Approved source of truth

Canonical project snapshot containing BOTH approved meshes:

`D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/p2-cleanup-v2-smooth-tunic.blend`

| Character | Approved object | Collection | Runtime triangles |
| --- | --- | --- | ---: |
| Brother | `Brother_SmoothTunic_v2` | `P2_Tunic_Repair_v2` | 11,910 |
| Sister | `Sister_Clean_v1` | `P2_Cleanup_v1` | 11,280 |

Do NOT rig `Brother_Clean_v1`: it is the previous model with the unwanted diagonal
band and rear patch. Original generated meshes and earlier cleanup objects remain
hidden for comparison. Validation-scene objects also reference the character mesh
data: do not mistake those review duplicates for the approved working objects.
Make independent working mesh copies for rigging so saved checkpoints stay intact.

At handoff, Blender MCP confirmed that the live file is
`C:/Users/Chris/Documents/Blender/Projects/dungeoncharacter.blend`, saved and not
dirty. It contains the approved objects; the brother is active, and both approved
objects are visible in scene `Scene`. Recheck this on entry rather than opening
or saving over the user's live file blindly. The project snapshot above is the
portable checkpoint; the live file was subsequently saved by the user.

The meshes originally imported at approximately one unit tall, with their origins
around body center and feet near local Z=-0.5. Review display positions are about
X=-0.4/+0.4, with Z rotation approximately -90 degrees. These are review transforms,
not settled bind/export transforms. Before binding, inspect dimensions, orientation,
grounding, and the existing Godot capsule/camera; agree a consistent scale and
feet-at-origin convention. Do not bake review spacing into the rig.

## Materials, UVs, and topology

Each character uses one UV layer and one material with four embedded 2048x2048
PBR images: base color, roughness, metallic, normal. Preserve UVs, image packing,
material connections, and shading. Mixed quads/triangles are expected. Target is
approximately 12,000 runtime triangles per character, not 12,000 quads.

Both passed cleanup checks for zero-area faces, branching non-manifold edges,
bow-tie vertices, loose/wire geometry, and inconsistent manifold edge winding.
They retain open boundaries and disconnected shells for facial details, hair,
clothing, shoes, etc. They are not watertight printing meshes. Do not indiscriminately
fill holes, globally weld, remesh, decimate, or rerun cleanup scripts. Their
topology has NOT yet been validated under deformation.

Brother v2: 6,229 vertices, 6,829 faces, 5,081 quads, 522 boundary edges.
The diagonal band was fused into the tunic; the user explicitly chose to REMOVE
it and have a smooth tunic. Upper tunic and matching sleeve topology were rebuilt
using the smooth opposite half. Cloth UVs were copied/mirrored with the geometry,
intentionally sharing atlas space. No image was repainted or replaced. Collar,
clasp, belt, pouch, split hem, head, hair, and lower body were retained. All 3,081
faces entirely below original mesh Z=0.09 passed exact position/UV-signature checks.
The repaired garment joins near original mesh Z=0.095; inspect that waist seam in
torso/hip bending. Eleven back vertices were smoothed and back shading normals
recomputed. The final material is standard PBR, without a custom shader mask.

Sister: 6,106 vertices, 6,086 faces, 5,194 quads, 884 boundary edges. Cleanup removed
eight redundant mouth triangles, repaired degenerate faces, and separated branching
edges and single-point surface connections. Inspect mouth and clothing shells
when assigning rigid head/accessory weights.

Detailed notes and audits, all under `Assets/Characters/Source/`:

- `p2-cleanup-v1-notes.md`, `p2-cleanup-v1-audit.json`
- `brother-tunic-repair-v2-notes.md`, `brother-tunic-repair-v2-audit.json`
- `brother-tunic-repair-v2-front.png`, `brother-tunic-repair-v2-back.png`
  (before on left, repaired on right)
- `p2-cleanup-v1.blend` and `p2-first-test-v1.blend`: earlier checkpoints only.

`Assets/Characters/Source/.gdignore` deliberately excludes editable sources and
review files from Godot's automatic import. Put eventual runtime exports outside
this folder, in a new versioned project asset directory.

## Tools and generation policy

Blender 5.1.2 uses Blender Lab's official MCP add-on 1.0.3, originally installed from
`C:/Users/Chris/Documents/Blender/Addons/mcp-1.0.3.zip`. Its bridge is localhost:9876.
The registered Codex server is `blender`, launching
`C:/Users/Chris/.codex/mcp/blender-lab-1.0.3/venv/Scripts/python.exe -m blmcp`.
It has been tested through native `mcp__blender` tools. Prefer purpose-built tools;
use `execute_blender_code` for mesh/rig operations without dedicated tools. Bundled
API documentation is available through `get_python_api_docs` and under
`C:/Users/Chris/.codex/mcp/blender-lab-1.0.3/server/blmcp/data/api/`.
Window screenshots once returned black; deterministic Blender renders worked.

Godot MCP is connected; project identified as Godot 4.7 .NET, C#/.NET 8.
The Tripo Godot DCC Bridge 1.0.1 is installed/enabled under
`addons/Tripo3d_Godot_Bridge/`; localhost:60650 was reachable. It receives assets
from Tripo Studio into `res://TripoModels`. An actual Studio transfer is untested.
These CLI models were imported directly into Blender as FBX.

The user prefers their Tripo subscription/API for model creation first; Genex model
generation is a fallback if Tripo is inadequate. Genex's other skills remain usable.
GPT Image was used for design/reference images. Tripo CLI 0.7.2 is installed and
authenticated through device login, profile `default`, international region `ov`.
Do not read, print, or put credentials in files/chat. Studio and API balances are
separate. User reported $20 Pro with 2,540 Studio credits; last verified API balance
was 780 available/0 frozen after spending 220. Recheck before any future paid work.
No paid generation is necessary for the immediate rigging task.

Original P2 jobs (model `P2-20260801`, requested 6,000 quads, textured/PBR):

| Job | Task ID | Actual API credits |
| --- | --- | ---: |
| Brother image-to-model | `3cc91a2e-8ad2-40cb-9244-f194e2138b01` | 110 |
| Sister image-to-model | `457309d5-778e-48bd-9193-48b082b3eeae` | 110 |

FBXs, previews and `task.json` are in
`Assets/Characters/Generated/tripo-out/brother-p2-test-v1-3cc91a2e/` and
`Assets/Characters/Generated/tripo-out/sister-p2-test-v1-457309d5/`.
Read the Tripo skills before any future paid task; they require an explicit plan
and confirmation. Never resubmit a running generation to check its status.
Genex is already configured; use its lane skill and `npx genex doctor` when needed.

## Godot integration context (later stage)

Relevant files:

- `Scenes/player.tscn`, `Scripts/Player.cs`
- `Scenes/CombatSystem/combat_player.tscn`
- `Scripts/CombatPlayerScripts/CombatPlayer.cs`, `Scripts/SceneManager.cs`
- `ARCHITECTURE.md` (helpful overview, but inspect actual files; some details lag).

Movement/interaction, pushing, and debug character swapping already exist. The
controller faces `Pivot` with `Basis.LookingAt(direction)`, uses `MoveAndSlide`,
and has default Speed=14. C toggles `(Temporary) Swap Character`; the code expects
`Pivot/Male-Character` and `Pivot/Female-Character`. Actual current scene has an
empty `Male-Character` at the ROOT and an older female GLB under `Pivot`. Fix this
hierarchy mismatch during integration. The generated characters are not wired in.

Combat still references older male/female GLBs. `CombatPlayer.SetCharacterMale`
controls visibility and `SceneManager` passes `Player.IsCharacterMale` into battle.
Reuse the approved visuals/animations in exploration and combat while preserving
that behavior. Future locomotion should be in-place; gameplay code controls travel.
Match animation cadence to actual controller speed after scale is settled.

## Suggested execution and acceptance checks for the next session

1. Read repository AGENTS.md and this handoff; inspect live Blender state and the
   approved source objects. Save a NEW rigging checkpoint inside the project.
2. Establish scale, axes and feet-at-origin before binding. Create a consistent
   humanoid bone naming/hierarchy for both characters, fitting each body separately.
   Do not assume generated hands support a detailed finger rig; inspect them.
3. Rig and weight the brother first. Keep accessory shells attached appropriately
   (head details/hair to head, pouch to an appropriate hip/torso attachment), and
   preserve tunic overlaps, straps, shoe cuffs, and UVs. Automatic weights are a
   starting point, not validation. Check normalized weights and unweighted vertices;
   target no more than four meaningful bone influences per vertex for export.
4. Create deformation test poses/actions for shoulders, elbows, wrists, hips,
   knees, ankles, spine, and neck. Check extremes and transitions for collapsing
   joints, cracks, detached islands, clothing clipping, and waist-seam separation.
   Repair weights/local topology as actually needed and stay near the triangle budget.
5. Apply the validated approach to the sister, with independent weight corrections.
   Show visual evidence, save versioned rigged blend files, and record limitations.
6. Only after deformation tests pass, proceed to production idle/locomotion clips
   and the later Godot export/integration milestone. A basic export round-trip can
   validate skeleton/material compatibility without replacing the live player yet.

## Workspace preservation

The working tree is dirty and contains user changes, including modifications to
`Scenes/player.tscn`, `project.godot`, `.gitignore`, deleted older character assets,
and untracked tools/artifacts. Do not reset, restore, clean, or stage/commit all.
Read AGENTS.md; preserve prior checkpoints and originals. Save new versioned
artifacts and avoid overwriting the user's external live blend file. No subagents
were requested. Do not publish, regenerate assets, or start paid rigging services
as a substitute for the agreed Blender workflow.
