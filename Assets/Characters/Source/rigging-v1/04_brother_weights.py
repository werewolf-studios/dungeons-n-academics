exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
s=bpy.data.scenes['Brother_Rig_Validation_v1'];bpy.context.window.scene=s
ob=bpy.data.objects['Brother_RigMesh_v1'];rig=bpy.data.objects['Brother_Humanoid_v1'];reset_pose(rig)
before=audit(ob,rig);parts=shells(ob)
corrections={}
for pi,ids in enumerate(parts):
    for i in ids:
        v=ob.data.vertices[i];x,y,z=v.co;side='L' if x>0 else 'R';ax=abs(x)
        ws={ob.vertex_groups[g.group].name:g.weight for g in v.groups if ob.vertex_groups[g.group].name!='root'}
        reason='normalize_limit'
        if pi in [1,9,10,12,13,15,16]:ws={'head':1};reason='rigid_head_shell'
        elif pi==2:
            ws=mix({'chest':1},{'neck':1},smoothstep(1.30,1.37,z))
            ws=mix(ws,{'head':1},smoothstep(1.36,1.445,z));reason='neck_face_transition'
        elif pi in [8,14]:ws={'pelvis':1};reason='rigid_pouch'
        elif pi==11:ws={'chest':1};reason='rigid_clasp'
        elif pi in [4,5,6,7]:
            # Keep cuff on shin, heel on foot, and toe hinge away from heel.
            ws=mix({'foot.'+side:1},{'shin.'+side:1},smoothstep(.135,.24,z))
            toe=(1-smoothstep(.075,.115,z))*(1-smoothstep(-.18,-.12,y))*.8
            ws=mix(ws,{'toe.'+side:1},toe);reason='shoe_cuff_ankle'
        elif pi==0 and z<1.115 and ax<.28:
            # Lower split tunic follows the matching thigh; exact pelvis band over repaired seam.
            t=1-smoothstep(.84,1.035,z)
            ws=mix({'pelvis':1},{'thigh.'+side:1},t);reason='tunic_seam_hem'
        elif pi==0 and z<1.24 and ax<.18:
            ws=mix({'pelvis':1},{'spine':1},smoothstep(1.105,1.19,z))
            ws=mix(ws,{'chest':1},smoothstep(1.18,1.29,z));reason='torso_waist_blend'
        elif pi==0 and ax>.36 and z<.94:
            ws=mix({'hand.'+side:1},{'forearm.'+side:1},smoothstep(.825,.925,z));reason='hand_wrist'
        set_weights(ob,i,ws); corrections[reason]=corrections.get(reason,0)+1
after=audit(ob,rig)
json.dump({'before':before,'after':after,'vertex_corrections':corrections},open(BASE+'/brother-corrected-weights-audit.json','w'),indent=2)
pose_world(rig,TESTS['legs']);camera(s,(3,-5,1.6));render(s,'brother-corrected-legs')
pose_world(rig,TESTS['torso']);camera(s,(3,5,1.8));render(s,'brother-corrected-torso-back')
pose_world(rig,TESTS['shoulders']);camera(s,(0,-5,1.2));render(s,'brother-corrected-shoulders')
reset_pose(rig)
result={'audit':after,'corrections':corrections}
