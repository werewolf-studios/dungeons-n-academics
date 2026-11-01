# Idle and damage refinement v4

Final Blender file: siblings-animation-v010-idle-damage-reviewed.blend.
The v009 file and earlier numbered stills are intermediate revisions.

Brother_Idle_v11 corrects only the brother's right upper-arm, forearm and hand
channels to give a straighter relaxed silhouette. Sister_Idle_v3 is unchanged.
Both TakeDamage_v11 actions now last 24 frames (1 second at 24 fps), with impact
at frame 4, asymmetric torso recoil, delayed head recoil, knee compression,
reacting arms and a slower settling recovery. Both feet remain planted. First
and last damage keys match their respective Idle frame 1 to floating-point tolerance.

All other delivered actions remain unchanged: Walk/Run v6, SwordIdle/SwordSlash v7,
SpearIdle/SpearThrust v3. Corrected sword socket rotation remains -90 X in Godot;
spear remains +90 X. No mesh, weight, UV, material or gameplay changes.

Runtime assets: Assets/Characters/Animated/v4/brother-animations-v4.glb and
sister-animations-v4.glb, eight clips each. Existing isolated preview script now
loads these files. Focus Godot, allow import, and restart the preview with F6.
Godot playback of this revision has not been independently confirmed.

Evidence: authoring-audit.json (zero unreachable IK targets), validation.json
(finite poses, matching loop endpoints, grounding, unchanged triangle counts,
zero unweighted vertices, max four influences), transition-check.json (Idle
endpoint match), and raw-glb-comparison.json (independent export pose comparison).
Reviewed review/TakeDamage.mp4 and review/TakeDamage-final-sheet.png; final impact
still is review/TakeDamage-delivery.png. review/Idle-1.png shows the arm correction.
The supplied user recording was sampled for comparison in user-recording-sheet.png.

Remaining limitations: no facial expression animation or physical hair movement;
the previously recorded sister rear-tunic intersection during Run remains outside
this change. Motion is authored in place, without gameplay knockback or hit logic.
