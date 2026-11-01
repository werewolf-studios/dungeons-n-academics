# Brother locomotion tunic clearance v6

Final checkpoint: siblings-animation-v012-brother-tunic.blend.
Runtime: Assets/Characters/Animated/v6/{brother,sister}-animations-v6.glb.
The existing isolated Godot preview now loads v6; focus the editor for import,
then restart with F6. Godot visual approval of this revision is pending.

Brother's tunic helpers have additional 4.5 cm forward and 1.2 cm outward local
clearance in Walk and Run. This fixes the visible front-panel breakthrough in the
supplied recording without changing the body/limb motion, geometry or materials.
Existing evaluated tunic driver motion is baked into Brother actions ending v13;
tunic drivers are muted on Brother animation/review rigs to avoid double motion.
Other Brother clips retain their previously evaluated helper motion. Sister's
actions and drivers are unchanged. Do not re-enable Brother tunic drivers while
playing these baked actions.

Visual evidence: review/Walk.mp4, Run.mp4, both all-frame contact sheets, and
Run-back.png. All front-view cycle frames were reviewed for the reported clipping;
rear passing pose also checked. This is visual clearance review, not a general
mesh collision guarantee for arbitrary future motion or animation blends.

validation.json and raw-glb-comparison.json record grounding, loop, weight and
independent export checks. Original meshes, UVs, embedded textures and triangle
counts remain unchanged. Earlier checkpoints remain intact. The known sister
rear-tunic Run intersection remains outside this Brother-only correction.
