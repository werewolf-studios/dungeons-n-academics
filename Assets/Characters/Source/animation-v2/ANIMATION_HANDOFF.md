# Animation refinement v2

Editable checkpoint: `siblings-animation-v006-locomotion-slash.blend`.
Previous v005 and all v1 exports remain intact. Working rigs/meshes retain their
existing names. Revised Walk, Run and SwordSlash actions have suffix `_v6` for both
characters. The other five clips retain their approved `_v3` actions.

Walk and Run now use shoulder-led opposing arm swings, animated elbow flexion,
relaxed grouped fingers, hip/chest counter-rotation, lateral weight shifts and
vertical motion. Walk stays 28 frames and Run 18 frames at 24 fps. Both remain
in-place loops with the original reference travel speeds.

SwordSlash is now 36 frames / 1.5 seconds. Left lead foot lifts and advances 24 cm,
plants before the cut, and stays planted through contact/follow-through. Pelvis
advances up to 14 cm; rear foot stays planted. Recovery lifts the lead foot back
into SwordIdle. Root remains stationary: this is a local step-and-recover attack,
not permanent world displacement. Suggested hit cue is frame 19 / 0.75 seconds.

Review scenes: ANIM_REVIEW_Walk, ANIM_REVIEW_Run, ANIM_REVIEW_SwordSlash.
Videos: review/Walk.mp4, review/Run.mp4, review/SwordSlash.mp4.
Additional final stills show the side step and front/back locomotion silhouettes.
Earlier numbered stills are intermediate work, not the delivered actions.

Runtime assets: Assets/Characters/Animated/v2/{brother,sister}-animations-v2.glb.
Both contain all eight clips. The existing isolated preview scene at
Scenes/CharacterAnimationPreview/v1/character_animation_preview.tscn now loads v2.
No player-scene or gameplay integration was performed.

Validation: authoring-audit.json reports no unreachable IK targets in the revised
clips. validation.json checks all animation matrices and exact loop closure,
evaluated mesh grounding, triangle counts (11910 / 11280), zero unweighted vertices,
and at most four influences. Raw GLB channel sampling in raw-glb-comparison.json
matches Blender references; the complete set remains below 0.7 mm maximum error.
Original topology, UVs and packed PBR textures were not edited.

Remaining visual limitation: the sister has a small rear-tunic intersection in
the run passing pose, visible in review/Run-back-refined.png. Reduced compression
helps but does not fully resolve the underlying garment deformation. Treat this
revision as ready for motion review, not a final garment/collision sign-off. No
automatic mesh collision proof or full finger collision check is claimed.

The user confirmed v1 preview loads and plays in Godot after its parser fix.
For v2, Computer Use app approval timed out before the existing editor could be
focused. No extra Godot process was launched, and no v2 import/playback success
is claimed. Focus the existing editor to allow its filesystem scan/import, then
restart the same preview with F6. If the preview is already running, stop it first.

The scripts in this folder are authoring/export records. refine.py creates new
actions and intentionally refuses to overwrite existing action names; do not
blindly rerun it in the delivered file.
