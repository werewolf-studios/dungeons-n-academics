# Character animation milestone v1

Latest editable file: `siblings-animation-v005-reviewed.blend` in this directory.
The live unsaved rig session was preserved first as
`siblings-animation-v001-live-checkpoint.blend`. The previous rigging checkpoint,
approved source meshes, source materials, and weapon source files were preserved.

## Review in Blender

Select one of the scenes named `ANIM_REVIEW_<clip>` in the Scene dropdown, then
press Space to play both characters together. Each scene has the correct weapon,
action and frame range already selected. These are review copies.

Author on `Brother_Animation_v1` / `Sister_Animation_v1`, using
`Brother_AnimRig_v1` / `Sister_AnimRig_v1` and their independent animation meshes.
The final actions are `<Brother|Sister>_<clip>_v3`. Older blocking actions remain
for comparison; they are not included in the runtime exports. Export NLA tracks
are muted for authoring. Unmute them and clear the active action only when
re-exporting with the supplied scripts; otherwise they layer over each other.

## Clips (24 fps)

| Clip | Duration | Playback frames | Loop | Weapon |
| --- | ---: | --- | --- | --- |
| Idle | 3.000 s | 1–72 | yes | none |
| Walk | 1.167 s | 1–28 | yes | none |
| Run | 0.750 s | 1–18 | yes | none |
| SwordIdle | 2.000 s | 1–48 | yes | sword |
| SpearIdle | 2.000 s | 1–48 | yes | spear |
| SwordSlash | 0.917 s | 1–22 | no | sword |
| SpearThrust | 1.083 s | 1–26 | no | spear |
| TakeDamage | 0.667 s | 1–16 | no | none |

Every action includes one extra terminal key at the next frame. Loop endpoints
match exactly. The attacks begin/end at their corresponding weapon-ready idle;
TakeDamage begins/ends at Idle. Damage has a quick asymmetric torso/head recoil,
knee compression and raised hands. Facial expressions are not animated.

Suggested future contact cues: SwordSlash frame 12 (0.458 s), SpearThrust frame 13
(0.500 s). These are animation timing references, not implemented damage events.
Gameplay hitboxes, enemy reactions, knockback, sounds and attack input remain unwired.

## Authored motion and grip

Both bodies use the same 30-bone hierarchy: the previous 24 bones plus grouped
finger-base, finger-tip and thumb controls for each hand. This is a simple grip
rig, not a full individual-finger or facial rig. Deform weights remain normalized,
with no unweighted vertices and at most four influences. The original rigs were
not altered; the new controls and weights belong to the animation copies.

Foot targets and analytic two-bone solving were baked into editable bone keys.
No runtime IK or animation-generation service is required. Feet follow authored
stance/swing paths, with ground contact in place. Stance feet move backward in
the stationary animation so they can stay planted when the controller moves the
character forward. All root travel is zero. Reference movement speeds are about
0.657 m/s for Walk and 1.754 m/s for Run at original playback rate. Player.cs
currently uses Speed=14; movement scale/cadence must be reconciled during later
integration rather than treating these cycles as a 14 m/s match.

The sword and spear are rigid bone-parented props, using their validated original
dimensions and materials. Spear hands maintain a 0.28 m separation along the shaft.
The rear hand drives the thrust; the body follows with a small forward weight
shift while the feet remain planted. The run and attacks use compact hip angles
to avoid the known deep-crouch tunic problem. No deep crouch or seated clip is
included. Hair remains rigidly attached to the head.

## Exports

Runtime files are outside Source, in `Assets/Characters/Animated/v1/`:

- brother-animations-v1.glb
- sister-animations-v1.glb
- animation-manifest.json

Each GLB contains all eight named clips, a 30-joint skeleton, skinning, original
UVs and embedded 2K PBR textures. Triangle counts are unchanged: brother 11,910,
sister 11,280. Tunic helper motion is sampled into animation channels; the GLBs
do not depend on Blender drivers. Clips have zero-based timing, avoiding an
unintended first-frame pause. Metallic/roughness textures are combined for glTF;
the original four packed images remain unchanged in the Blender material.
Sampler warning settings were checked previously and are compatible.

Props are intentionally separate from the character GLBs. The included Godot
preview attaches the existing weapon scenes through hand.R. Socket position in
bone-local space is (0.025, 0.085, 0); rotate the weapon scene +90 degrees about
local X to align its +Y shaft with the hand's +Z grip axis. The existing Grip/Tip/
Butt markers remain available for later gameplay work.

## Validation and evidence

- animation-validation-v2.json: frame-by-frame Blender contact/loop/weight checks.
- pose-reference.json: sampled Blender bone positions converted to glTF axes.
- raw-glb-comparison.json: independent GLB hierarchy/channel evaluation against
  the Blender references. Maximum sampled positional difference is under 0.7 mm.
- review/*.mp4: all eight side-by-side motion review videos, 960×640 at 24 fps.
- review/*-review.png and Sister-Run-back.png: additional visual evidence.

Numerical checks found no non-finite poses, meaningful ground penetration,
unweighted vertices or excess influences. Authored spear contact error is below
0.001 mm; foot-target errors are below 0.003 mm. These contact checks do not imply
complete mesh collision detection. Fine finger/shaft intersection and garment
silhouettes may need further polish in close-up or more extreme future clips.

## Godot verification limitation

An isolated preview scene was added at
`Scenes/CharacterAnimationPreview/v1/character_animation_preview.tscn`.
It offers clip selection, front/side/back views, replay, pause and playback speed,
and attaches the existing sword/spear scenes. It does not replace the player.

Verification launches produced .NET assemblies-not-found popups, even though the
referenced DLL files exist. The full editor import also crashed during startup.
All launched Godot processes were stopped after the user reported the popups;
no further Godot launches were attempted. The installation was not changed.

A minimal runtime test loaded all clips and checked spear contacts, but later
cross-clip pose checks exposed stale omitted-channel state after switching clips.
The preview and validation script now reset bone poses before switching; that
change has NOT been re-verified in Godot because of the popup issue. The historical
godot-validation-v1.json is retained as a diagnostic, not a passing approval.
Use the independent raw-GLB checks as the completed export verification. Final
Godot editor/playback approval remains pending .NET launch troubleshooting.

Godot loop flags are applied from the manifest by the preview (glTF does not
standardize looping). Later gameplay integration should use an AnimationTree or
explicit RESET handling to prevent omitted static channels retaining an old pose.

## Next integration work

Preserve movement, interaction, pushing, debug character swapping and combat
selection. Resolve the documented Pivot/Male-Character node-path mismatch, check
model forward yaw and controller scale/cadence, then wire animation state changes,
weapon visibility and combat events. None of that existing gameplay code was
modified in this milestone. TakeDamage is the base unarmed reaction; weapon-specific
hit reactions and additional attack directions are not included.

No paid generation was used. Future model generation preference remains Tripo,
with Genex as fallback; Blender owns rigging and animation.
