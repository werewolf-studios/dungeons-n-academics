exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
s=bpy.data.scenes['Brother_Rig_Validation_v1'];bpy.context.window.scene=s
ob=bpy.data.objects['Brother_RigMesh_v1'];rig=bpy.data.objects['Brother_Humanoid_v1'];reset_pose(rig)
with bpy.data.libraries.load(BASE+'/brother-rig-v001-auto.blend',link=False) as (src,dst):dst.objects=['Brother_RigMesh_v1']
heat=dst.objects[0]
heat_weights=[{heat.vertex_groups[g.group].name:g.weight for g in v.groups if heat.vertex_groups[g.group].name!='root'} for v in heat.data.vertices]
add_tunic_bones(rig)
parts=shells(ob)
for i in parts[0]:
    v=ob.data.vertices[i];x,y,z=v.co;side='L' if x>0 else 'R'
    original=heat_weights[i];total=sum(original.values());original={k:w/total for k,w in original.items()}
    # Retain heat-derived arm transitions, replacing only the central garment weights.
    arm={k:w for k,w in original.items() if any(k.startswith(p) for p in ['clavicle.','upper_arm.','forearm.','hand.'])}
    arm_amount=sum(arm.values())
    central=mix({'pelvis':1},{'tunic.'+side:1},1-smoothstep(.94,1.065,z)) if z<1.105 else mix({'pelvis':1},{'spine':1},smoothstep(1.105,1.20,z))
    central=mix(central,{'chest':1},smoothstep(1.18,1.30,z))
    if z>1.31:central=mix(central,{'neck':1},smoothstep(1.32,1.43,z)*.3)
    ws={k:w*(1-arm_amount) for k,w in central.items()}
    for k,w in arm.items():ws[k]=ws.get(k,0)+w
    if abs(x)>.36 and z<.94:ws=mix({'hand.'+side:1},{'forearm.'+side:1},smoothstep(.825,.925,z))
    set_weights(ob,i,ws)
# This temporary datablock was loaded by this script, never linked to a user scene.
bpy.data.objects.remove(heat,do_unlink=True)
pose_world(rig,TESTS['legs']);camera(s,(3,-5,1.6));render(s,'brother-refined-legs')
pose_world(rig,TESTS['torso']);camera(s,(3,5,1.8));render(s,'brother-refined-torso-back')
pose_world(rig,TESTS['shoulders']);camera(s,(0,-5,1.2));render(s,'brother-refined-shoulders')
reset_pose(rig)
result={'audit':audit(ob,rig)}
