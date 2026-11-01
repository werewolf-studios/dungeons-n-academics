# Brother smooth-tunic repair v2

Requested change: remove the diagonal raised front band and rectangular rear patch.

Saved file: `p2-cleanup-v2-smooth-tunic.blend`.
Working object: `Brother_SmoothTunic_v2`, in `P2_Tunic_Repair_v2`.
`Brother_Clean_v1` and all original generated meshes remain available, hidden.
The sister is unchanged.

## Geometry and UV handling

The band was integrated with the upper garment rather than a detachable strap.
Rebuilt the upper tunic and matching sleeve topology from the smooth opposite half,
retaining the collar, separate clasp, belt, pouch, split hem, head, hair, and lower body.
Joined the reconstructed upper garment at z=0.095 in original mesh coordinates,
matching the retained lower edge; maximum seam adjustment was 0.002627 mesh units.
Smoothed eleven vertices around the residual rear ridge using surrounding cloth
as a surface reference. Recomputed shading normals on the repaired back.
Separated two single-point surface connections created near the garment seam.

Copied/mirrored the intact cloth UVs along with its geometry. This intentionally
reuses UV space for the matching upper-garment halves. Existing texture images
were not painted, replaced, or resized. A separate material copy uses the same
four embedded PBR images and the standard normal-map connection; no custom shader
mask is required. Original UVs are not globally unwrapped.

Verified all 3,081 faces entirely below z=0.09 retain exactly the same vertex-position
and UV-corner signatures. The untouched source character's geometry and materials
remain available separately.

## Final checks

- 6,229 vertices; 6,829 faces; 5,081 quads.
- 11,910 runtime triangles, below the 12,000 target.
- Zero zero-area faces, overconnected edges, bow-tie vertices, wire edges, or
  inconsistent manifold edge winding.
- One UV layer, with finite UV coordinates; all original PBR images retained.
- 522 open boundary edges remain on the character's separate/open game-art shells.
- Front and back before/after renders were visually checked. Left is the previous
  cleanup version; right is the repaired version.

Comparison images: `brother-tunic-repair-v2-front.png` and
`brother-tunic-repair-v2-back.png`. Blender comparison scene:
`P2_Tunic_Repair_Validation_v2`.

This source file remains excluded from automatic Godot import by `.gdignore`.
Rigging, skinning, and deformation validation remain subsequent steps.
No Tripo or Genex credits were spent.
