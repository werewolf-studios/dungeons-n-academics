# Spear right-arm correction v9

Checkpoint: siblings-animation-v015-spear-arm.blend.
Both characters' SpearIdle and SpearThrust actions use v16. Only right upper-arm,
forearm and hand channels changed. The rear hand now extends from the forearm
across the shaft instead of folding downward against an upward forearm. Forearm
roll follows the grip; the elbow uses a lower outward bend direction.

The rear grip positions and shaft directions are preserved. Left arm keys are
unchanged; hand separation remains 0.28 m. Shaft roll follows the corrected hand,
so the decorative spearhead/guard may rotate around the shaft. No socket rotation
change is required (spear still +90 X, sword -90 X in the Godot preview).
All previous tunic/locomotion and damage fixes remain in the delivered actions.

Runtime assets: Assets/Characters/Animated/v9. Existing preview script loads v9.
Focus Godot for import, then restart F6; Godot review is pending. No new editor
process was launched.

Evidence: grip-check.json preserves authored rear grip targets to under 0.001 mm.
spear-motion-check.json samples four times per frame for two-hand contact and arm
rotation continuity. validation.json and raw-glb-comparison.json contain standard
loop, grounding, skinning and export checks. review/SpearIdle.mp4,
SpearThrust.mp4 and Thrust-cycle.png show the delivered motion. Fine individual
finger collision and arbitrary blends remain outside these checks.
