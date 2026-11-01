# Starter prompt for the next chat

Continue the Dungeons N Academics character pipeline in this project:
`D:/GodotProjects/dungeons-n-academics`.

Read `AGENTS.md` and `CHARACTER_PIPELINE_HANDOFF.md` first, then carry out rigging,
weight painting, and deformation tests in Blender using the connected Blender MCP.
Start with the approved brother, validate his rig/weights, then apply the proven
approach to the sister. Proceed with the work rather than stopping at a plan.

The approved source snapshot contains both characters:
`D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/p2-cleanup-v2-smooth-tunic.blend`.
Use `Brother_SmoothTunic_v2` and `Sister_Clean_v1`. Do not use the earlier male
mesh with the diagonal strap/back patch, regenerate the models, or redesign them.

Blender may already have
`C:/Users/Chris/Documents/Blender/Projects/dungeoncharacter.blend` open with these
objects. Inspect the live state before opening files or saving. Preserve originals
and save NEW versioned rigging files in the project.

Use a compatible humanoid bone hierarchy for both bodies, preserve the existing
UVs and embedded 2K PBR materials, and keep meshes near 12,000 runtime triangles
each. Resolve scale, facing, and grounding before binding. Test bending at the
major joints and torso; pay attention to separate accessory/clothing shells and
the brother's repaired waist seam. Correct weights based on visible deformation,
including unweighted vertices and excessive influences.

Report the saved files, validation evidence, and any remaining limitations. Keep
production animation and player-scene replacement for the subsequent milestone.
The handoff records Godot's existing movement, interaction, and debug-swap logic,
including a node-path mismatch to address during integration.

Tripo is preferred for any FUTURE model generation, Genex is the fallback, and
Blender owns rigging/animation. No additional paid generation is needed now.
