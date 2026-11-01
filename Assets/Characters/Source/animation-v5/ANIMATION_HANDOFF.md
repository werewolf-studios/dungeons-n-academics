# TakeDamage arm recovery v5

Final checkpoint: siblings-animation-v011-damage-recovery.blend.
Both TakeDamage actions use suffix v12. All other actions remain unchanged.

Replaced the changing elbow-pole solve with explicit quaternion interpolation
between neutral and recoil arm poses. Recovery follows one smooth path back to
Idle; quaternion signs remain consistent. Body/head recoil and one-second duration
remain unchanged. No geometry, material, weights or gameplay changes.

Runtime GLBs are in Assets/Characters/Animated/v5. Existing isolated preview now
loads v5. Focus Godot to import, then restart the preview with F6. Godot playback
of this revision is awaiting user review; no new editor process was launched.

Evidence: recovery-check.json checks frame-to-frame local arm rotation and Idle
endpoint equality. validation.json checks loops, finite poses, grounding and
weights. raw-glb-comparison.json compares exports against Blender. Visual review:
review/TakeDamage.mp4 and review/recovery-sheet.png.

Prior revisions remain intact. Known unrelated limitations (sister Run rear-tunic
intersection and no facial animation) remain as documented in prior handoffs.
