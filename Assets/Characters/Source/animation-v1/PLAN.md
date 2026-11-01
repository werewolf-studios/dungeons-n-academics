# Animation milestone v1

Approved scope: both characters, Idle, Walk, Run, SwordSlash, TakeDamage,
SpearThrust. Include SwordIdle and SpearIdle for weapon-ready transitions.
Brother authored and reviewed first, then independently fit sister.

Preserve live unsaved state in a new checkpoint, make independent animation
meshes/armatures, retain original rigs/actions/materials. Use validated starter
sword and spear as detachable rigid hand props. All character travel is in-place.
Author foot contacts and two-handed spear contacts, add local grip corrections,
sample/bake tunic helpers. Review renders/movies and numerical contacts/loops.
Export animated GLBs and test in a separate Godot preview, without replacing
the live player or changing gameplay/combat code. No asset generation needed.
