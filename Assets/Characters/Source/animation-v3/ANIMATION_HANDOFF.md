# Sword grip correction v3

Final file: siblings-animation-v008-sword-grip.blend.
Live dirty v006 state was preserved as siblings-animation-v007-live-checkpoint.blend.

Both characters' SwordIdle and SwordSlash use new `_v7` actions. Only upper_arm.R,
forearm.R and hand.R animation channels changed. Other actions, slash timing,
forward step, original meshes, weights, UVs and materials are preserved.

The right thumb is on hand-local -Z. The previous sword alignment pointed the
blade along +Z, producing an inverted grip. The corrected hand points its thumb
toward the blade; the forearm carries the hand's roll, and the wrist lies behind
the grip rather than in front. The sword prop rotates 180 degrees about local X
in Blender to preserve its world blade direction with the corrected hand.

Godot preview now loads Assets/Characters/Animated/v3/{brother,sister}-animations-v3.glb.
Sword socket rotation is (-90,0,0) degrees; spear remains (90,0,0). Both use
hand.R and the original (.025,.085,0) socket translation. Do not apply the sword
socket correction to spear equipment. animation-manifest.json records both.

grip-audit.json: every frame of both revised clips preserves the grip target to
under 0.001 mm. validation.json checks finite poses, loop closure, grounding and
weights. raw-glb-comparison.json checks exported bone positions against Blender.
Rendered idle, windup, contact and follow-through stills are in review/.

Godot playback of this revision still needs user review: focus the existing editor,
allow imports, then restart the same preview scene with F6. No new Godot editor
process was launched. The previously documented sister rear-tunic intersection
in Run is outside this grip correction and remains a known limitation.
