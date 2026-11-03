# Exploration integration — November 1, 2026

The playable entry point is now `Scenes/player_controller_test.tscn` (F5).
The isolated animation review remains at
`Scenes/CharacterAnimationPreview/v1/character_animation_preview.tscn` (F6).

## Approved assets

Both actors instance `Assets/Characters/Animated/v11/*-animations-v11.glb` (updated
November 2): handmade meshes on the unchanged v10 rigs and clips, see
`Assets/Characters/Source/handmade-v1/HANDMADE_HANDOFF.md`. `Animated/v10` is kept as a fallback.
The approved animation checkpoint is still
`Assets/Characters/Source/animation-v10/siblings-animation-v016-arm-refine.blend`.
No GLB, source checkpoint, animation tracks, skin weights or source materials were edited.
The imported model's +Z forward is rotated 180 degrees to match Player's -Z forward.
Native 1.8 m character height, feet at origin, and the existing 2 m capsule are retained.

## Exploration behavior

- WASD/gamepad: existing movement, normalization, collision and gravity.
- Hold Shift / left shoulder: Walk, at 0.37457144 of existing movement speed.
- Normal movement: Run. Release movement or remain blocked at a wall: Idle.
- C: existing press-once sibling toggle, retaining `Player.IsCharacterMale`.
- Left mouse / gamepad X: existing interaction. Push blocks keep existing behavior.
- Both actors keep the same locomotion state while swapping.
- The test map camera has a 45 degree elevated view and 55 degree FOV.
  The shared camera scene and its following/blocking code were not edited.

`ExplorationCharacterVisual.cs` handles presentation. `Player.cs` still owns travel,
interaction, pushing and selection. Locomotion loop flags are applied to independent
animation copies under the `Exploration` library. Actual horizontal velocity selects
Idle versus locomotion, while Walk/Run retain the approved 1x playback timing.
Scene-manager process disabling also freezes the visual subtree.

The pre-existing speed is intentionally retained: 10 m/s in the test map and
14 m/s as the controller default. An initial velocity/reference-speed multiplier
played both gaits at about 5.7x speed in the test map. The user found this too fast;
playback now stays at 1x, independently of traversal speed. No authored animation
was retimed. This preserves the tested gameplay pace rather than enforcing the
source clips' physical stride distance; some foot sliding is a tradeoff at this pace.

## Weapons and combat boundary

Socket configuration is read directly from the v11 `animation-manifest.json` (same values as v10):
`hand.R`; sword (0.025, 0.085, 0); spear brother (0.08, 0.07, 0),
sister (0.07, 0.065, 0); both rotations (-90, 0, 0).
Sword and spear instances are prepared under hidden sockets. Idle/Walk/Run do not
have weapon grips, so these locomotion clips do not display hand-held weapons.
This does not implement ownership, acquisition, equipping or combat animation playback.
Ensure this JSON is included as a non-resource export file when export presets are added.

**User requirement:** the player starts with the sword after the opening cutscene.
Cutscene support is a future session. Other weapons and their combat roles require
the user's explanation and a review of the existing turn-based, mathematics-driven
combat system before a plan is created. Combat code/scenes were not changed here.
Existing encounters remain available; this integration does not disable them in the map.
Character selection still flows to existing combat through `IsCharacterMale`.

## Validation and preservation

`Tests/Exploration/exploration_validation.tscn` tests the actual Player,
InteractionTest and PushBlock components in an isolated physics fixture.
Run it with the Godot 4.7 .NET executable and `--headless --path <project>`.
Build the C# project first. Success prints `EXPLORATION_VALIDATION_PASS`;
the assertion list is saved to `Tests/Exploration/validation-results.txt`.
Final result after the playback correction: build succeeded with zero warnings/errors;
all 31 runtime checks passed, including normal Walk/Run playback for both siblings.

`Tests/Exploration/exploration_world_review.tscn` captures the actual rendered map
and camera with both characters; temporary review-only enemy processing suppression
does not change the saved map. Four PNG captures are stored alongside it.
The actual exploration entry point was also smoke-tested headlessly with encounters intact.

Original copies of the four approved-to-edit files are under
`IntegrationBackups/exploration-v10-20261101/` as `.original` files, with `.gdignore`.
That folder also contains logs and isolated editor/user state for validation;
tests do not use the user's normal game save directory.
Godot automatically changed six v10 texture import sidecars during rendered review.
Those metadata-only changes were reverted to their clean task-entry contents;
the generated copies are retained in the backup folder. Approved texture pixels
and exported animation data were never modified.

Godot in the filesystem sandbox failed to load its installed .NET assemblies.
Running the same executable outside the sandbox with `DOTNET_ROOT` set to the
installed dotnet location succeeded. Avoid MCP `run_project`, which injects
an autoload into `project.godot`.
