exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v1/animlib.py').read(),'animlib','exec'))
for label in ['Brother','Sister']:
 s=bpy.data.scenes[label+'_Animation_v1'];bpy.context.window.scene=s;rig=bpy.data.objects[label+'_AnimRig_v1'];mesh=bpy.data.objects[label+'_AnimMesh_v1'];activate(rig)
 assert not rig.data.bones.get('fingers_base.R')
 bpy.ops.object.mode_set(mode='EDIT')
 for side in ['R','L']:
  h=rig.data.edit_bones['hand.'+side];M=h.matrix.copy();sgn=1 if side=='R' else -1
  for name,head,tail,parent in [('fingers_base.',(0,.075,0),(0,.12,0),'hand.'),('fingers_tip.',(0,.12,0),(0,.17,0),'fingers_base.'),('thumb.',(sgn*.022,.045,-.035),(sgn*.05,.095,-.065),'hand.')]:
   b=rig.data.edit_bones.new(name+side);b.head=M@Vector(head);b.tail=M@Vector(tail);b.parent=rig.data.edit_bones[parent+side];b.align_roll(M.to_3x3()@Vector((0,0,1)))
 bpy.ops.object.mode_set(mode='OBJECT')
 for side in ['R','L']:
  inv=rig.data.bones['hand.'+side].matrix_local.inverted();sgn=1 if side=='R' else -1
  for v in mesh.data.vertices:
   ws={mesh.vertex_groups[g.group].name:g.weight for g in v.groups};hand=ws.get('hand.'+side,0)
   if hand<.05:continue
   local=inv@v.co;thumb=(1-smooth(-.055,-.025,local.z))*smooth(.015,.05,local.x*sgn)*(1-smooth(.105,.13,local.y))
   finger=smooth(.055,.095,local.y)*(1-thumb);tip=smooth(.105,.14,local.y)
   ws['hand.'+side]=hand*(1-max(thumb,finger));ws['thumb.'+side]=hand*thumb;ws['fingers_base.'+side]=hand*finger*(1-tip);ws['fingers_tip.'+side]=hand*finger*tip
   ws={k:w for k,w in sorted(ws.items(),key=lambda v:v[1],reverse=True)[:4] if w>1e-6};total=sum(ws.values())
   for g in list(v.groups):mesh.vertex_groups[g.group].remove([v.index])
   for name,w in ws.items():
    vg=mesh.vertex_groups.get(name) or mesh.vertex_groups.new(name=name);vg.add([v.index],w/total,'REPLACE')
 # Fixed bone-local prop transform. Bone parenting adds a bone-length translation.
 hand=rig.data.bones['hand.R'];offset=Vector((.025,.085,0));local=Matrix.Identity(4);local.translation=offset
 for w in ['Sword','Spear']:
  ob=bpy.data.objects[label+'_Anim_'+w];ob.parent=rig;ob.parent_type='BONE';ob.parent_bone='hand.R';ob.matrix_parent_inverse=Matrix.Identity(4)
  ob.matrix_basis=Matrix.Translation((0,-hand.length,0))@local
  ob['attachment']='hand.R; local shaft axis +Z; grip center (+.025,.085,0) in hand coordinates'
result={'hand_rig_bones':{label:len(bpy.data.objects[label+'_AnimRig_v1'].data.bones) for label in ['Brother','Sister']}}
