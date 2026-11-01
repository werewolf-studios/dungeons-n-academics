# Brother natural tunic drape v8

Checkpoint: siblings-animation-v014-natural-tunic-drape.blend.
Runtime assets: Assets/Characters/Animated/v8/{brother,sister}-animations-v8.glb.
Existing isolated Godot preview loads v8. Focus the editor for import, then F6.
Playback approval in Godot is pending; no extra editor process was launched.

The prior constant clearance pose projected the whole tunic far forward. The new
Brother Walk/Run v15 actions use only 2 cm forward helper clearance. Upper trouser
weights underneath the tunic are progressively supported by pelvis: 191 vertices
between Z=.68 and .88 m, using a smooth height ramp capped at 95%. This restrains
upper-leg cloth protrusion while leaving knee/lower-leg animation unchanged.
These weights also apply to the other Brother clips; their actions are unchanged.
The animation mesh was copied before weight edits, preserving the previous mesh.
Sister is unchanged. Topology, vertex positions, UVs and PBR materials are unchanged.

Evidence: full front Walk/Run videos and frame sheets; isolated Brother side Run
video, Side-cycle.png, and rear passing-pose still. SwordSlash, SpearThrust and
TakeDamage weight-check stills check representative loaded poses after repainting.
weight-check.json confirms normalized weights (error <1e-7) and at most four
influences. validation.json and raw-glb-comparison.json record standard loop,
grounding, skinning and export checks. No general arbitrary-pose cloth collision
guarantee is claimed. The prior unrelated Sister rear Run limitation remains.
