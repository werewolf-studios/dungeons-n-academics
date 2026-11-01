# Arm, spear and damage rework v10

Checkpoint: siblings-animation-v016-arm-refine.blend. v015 and Animated/v9 are untouched.
Runtime assets: Assets/Characters/Animated/v10. The preview script loads v10.
Status: reviewed playing in the Godot preview and approved by the user on 2026-10-31.
Blend files are deliberately not tracked in git, so the checkpoint exists only on the authoring machine.
They are not part of the build: this folder has a .gdignore and the game uses the exported GLBs.

## Rebuilt for both characters (actions `_v17`)
SwordIdle, SwordSlash, SpearIdle, SpearThrust, TakeDamage. Idle, Walk and Run are byte-identical
to v9 in the exported channels (glb-v9-v10-comparison.json).

- Legs and pelvis keep their motion in the sword and spear clips; TakeDamage rebuilds them too.
- TakeDamage is now 37 frames (was 24). The event stays on frame 4.
- SwordSlash contact stays on frame 19, SpearThrust on frame 13.

## Spear changes that affect runtime
The spear is flipped in the hand so both thumbs point at the tip, matching the sword. Godot sockets:
both weapons use -90 X. The spear also needs a per-character position in hand.R space:
brother (0.08, 0.07, 0), sister (0.07, 0.065, 0). The sword keeps (0.025, 0.085, 0). Anything
attaching a spear outside the preview scene must use these values (animation-manifest.json).

## Scripts
armlib.py (arm solver and helpers), refine_sword.py, refine_spear.py, refine_damage.py,
export_validate.py. Refine scripts need LABELS and OLD set before exec, and always rebuild from
the source action, so reruns are safe.

Checks: joint_limits.py (elbow, wrist, twist-jump and per-bone torso limits), hand_clearance.py,
fit_contact.py (grip search), compare_glb.py. review_grip.py and review_torso.py render close-ups.

## Lessons
- Check both penetration and gap for hand contact. A no-clipping score alone produced floating hands.
- Yaw must wrap to +/-180. A full-turn error split across two bones cancels in the total and wrecks the mesh.
- Blending bone rotations separately opens the elbow mid-blend. Carry the source orientation through instead.

## Known limitations
- Spear shaft is 8.5 cm thick, so hands overlap it: up to about 20 mm on Brother, 7 mm on Sister at idle.
  The left hand cradles rather than wraps. A slimmer shaft is the real fix.
- Thrust reach is reduced so the left hand can stay on the shaft.
- Sister's TakeDamage tips her tunic hem back 7 degrees; a tiny speck can show on the rear hem.
- hand_clearance.py fails on the sword mesh, so sword grips were checked by eye only.
- Combat does not play these clips yet; the preview scene is the only consumer.
- Godot MCP's run_project injects an autoload into project.godot. Use Godot's command line or F6 instead.
