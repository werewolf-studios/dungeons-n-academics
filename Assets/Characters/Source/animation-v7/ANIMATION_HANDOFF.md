# Stable Brother tunic v7

Final checkpoint: siblings-animation-v013-stable-tunic.blend.
Brother Walk/Run use v14 actions. All other actions remain as in v6.
The independent leg-driven panel translations caused the observed expansion.
Both helpers now hold constant local clearance transforms throughout each cycle,
following the pelvis without alternating panel extension. This deliberately uses
a steady forward clearance pose rather than cloth flutter. Mesh, UVs, weights,
materials and body animation are unchanged; earlier revisions remain intact.

Runtime: Assets/Characters/Animated/v7. The existing Godot preview loads v7.
Focus editor, allow imports, restart with F6. Godot visual approval is pending.
Blender cycle renders: review/Walk.mp4 and review/Run.mp4; run-cycle.png shows all
run frames. Standard loop, grounding, weights and raw export comparison reports
are alongside this file. These are not exhaustive cloth collision checks for
arbitrary animation blending. Sister's previously documented rear Run clipping
is unchanged and outside this Brother-only refinement.
