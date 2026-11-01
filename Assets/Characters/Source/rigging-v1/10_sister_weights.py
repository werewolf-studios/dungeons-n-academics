exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
s=bpy.data.scenes['Sister_Rig_Validation_v1'];bpy.context.window.scene=s
ob=bpy.data.objects['Sister_RigMesh_v1'];rig=bpy.data.objects['Sister_Humanoid_v1'];reset_pose(rig)
parts=shells(ob);heat=json.load(open(BASE+'/sister-auto-weights.json'));colors=json.load(open(BASE+'/sister-vertex-colors.json'))
headparts=[4,5,6,12,13,14,15,22,24,25,26,27,28,29,32,35,36]
shoeparts=[7,8,10,11,16,17,18,19,21,23,30,31,33,34]
reasons={};garment=[]
for pi,ids in enumerate(parts):
    for i in ids:
        v=ob.data.vertices[i];x,y,z=v.co;side='L' if x>0 else 'R';r,g,b=colors[i]
        ws={k:w for k,w in heat[i].items() if k!='root'};reason='normalized_heat'
        if pi in headparts:ws={'head':1};reason='rigid_head_hair_mouth'
        elif pi==37:ws={'chest':1};reason='rigid_clasp'
        elif pi==20:ws={'pelvis':1};reason='rigid_belt'
        elif pi==9:ws=mix({'chest':1},{'neck':1},smoothstep(1.33,1.40,z)*.25);reason='collar'
        elif pi in shoeparts:
            ws=mix({'foot.'+side:1},{'shin.'+side:1},smoothstep(.16,.27,z))
            toe=(1-smoothstep(.07,.11,z))*(1-smoothstep(-.23,-.15,y))*.8
            ws=mix(ws,{'toe.'+side:1},toe);reason='shoe_strap_cuff'
        elif pi in [1,2]:
            if z<.96:ws=mix({'hand.'+side:1},{'forearm.'+side:1},smoothstep(.86,.96,z))
            reason='arm_hand_wrist'
        elif pi==0:
            if z>=1.445:ws={'head':1};reason='rigid_face'
            elif z>1.34:
                ws=mix({'chest':1},{'neck':1},smoothstep(1.32,1.38,z))
                ws=mix(ws,{'head':1},smoothstep(1.37,1.445,z));reason='neck_face_transition'
            else:
                total=sum(ws.values());original={k:w/total for k,w in ws.items()}
                arm={k:w for k,w in original.items() if any(k.startswith(p) for p in ['clavicle.','upper_arm.','forearm.','hand.'])}
                arm={k:w*smoothstep(.15,.22,abs(x)) for k,w in arm.items()};amount=sum(arm.values())
                central=mix({'pelvis':1},{'spine':1},smoothstep(1.13,1.22,z))
                central=mix(central,{'chest':1},smoothstep(1.21,1.33,z))
                ws={k:w*(1-amount) for k,w in central.items()}
                for k,w in arm.items():ws[k]=ws.get(k,0)+w
                reason='torso_sleeve_waist'
        elif pi==3:
            is_cloth=z>.78 and (r>.37 or b>.38 or (r>.30 and r/max(g,.01)>1.65))
            if is_cloth:
                ws=mix({'pelvis':1},{'tunic.'+side:1},1-smoothstep(1.0,1.10,z));reason='lower_tunic';garment.append(i)
            else:
                leg=mix({'shin.'+side:1},{'thigh.'+side:1},smoothstep(.46,.59,z))
                ws=mix(leg,{'pelvis':1},smoothstep(.86,1.015,z));reason='leggings_knee_hip'
        set_weights(ob,i,ws);reasons[reason]=reasons.get(reason,0)+1
json.dump({'weights':audit(ob,rig),'regions':reasons,'tunic_vertex_ids':garment},open(BASE+'/sister-corrected-weights-audit.json','w'),indent=2)
for test,pos in [('arms',(3,-5,1.9)),('legs',(3,-5,1.6)),('torso',(3,5,1.8)),('shoulders',(0,-5,1.2)),('crouch',(3,-5,1.8))]:
    pose_world(rig,TESTS[test]);camera(s,pos);render(s,'sister-corrected-'+test)
reset_pose(rig)
result={'audit':audit(ob,rig),'corrections':reasons}
