exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
s=bpy.data.scenes['Sister_Rig_Validation_v1'];bpy.context.window.scene=s
ob=bpy.data.objects['Sister_RigMesh_v1'];rig=bpy.data.objects['Sister_Humanoid_v1'];reset_pose(rig)
# The generated tunic is fused to leggings along irregular junctions. Keep that
# authored topology intact and use a continuous hip field over both surfaces.
# The previous atlas split test is deliberately abandoned on this working copy.
src=bpy.data.objects['Sister_Clean_v1'];ob.data=src.data.copy();ob.data.name='Sister_RigMeshData_v2_ContinuousHip'
zmin=min(v.co.z for v in ob.data.vertices);zmax=max(v.co.z for v in ob.data.vertices);scale=1.8/(zmax-zmin)
ob.data.transform(Matrix(((0,scale,0,0),(-scale,0,0,0),(0,0,scale,-zmin*scale),(0,0,0,1))))
ob.data.update()
# Assign all original regions using the established sister-specific rules, without rendering yet.
code=open(BASE+'/10_sister_weights.py').read().split('json.dump(')[0]
exec(compile(code,'10_sister_weights_regions','exec'))
parts=shells(ob)
for i in parts[0]:
    v=ob.data.vertices[i];x,y,z=v.co;side='L' if x>0 else 'R'
    if z<1.34:
        central=mix({'pelvis':1},{'spine':1},smoothstep(1.13,1.22,z));central=mix(central,{'chest':1},smoothstep(1.21,1.33,z))
        set_weights(ob,i,mix(central,{'upper_arm.'+side:1},smoothstep(.115,.205,abs(x))))
for i in parts[3]:
    v=ob.data.vertices[i];x,y,z=v.co;side='L' if x>0 else 'R'
    helpers=mix({'tunic.R':1},{'tunic.L':1},smoothstep(-.035,.035,x))
    hip=mix({'pelvis':1},helpers,1-smoothstep(.98,1.105,z))
    leg=mix({'shin.'+side:1},{'thigh.'+side:1},smoothstep(.46,.59,z))
    ws=mix(leg,hip,smoothstep(.72,.94,z))
    set_weights(ob,i,ws)
for pi in [7,8,10,11,16,17,18,19,21,23,30,31,33,34]:
    for i in parts[pi]:
        v=ob.data.vertices[i];side='L' if v.co.x>0 else 'R'
        set_weights(ob,i,mix({'foot.'+side:1},{'shin.'+side:1},smoothstep(.19,.29,v.co.z)))
ob['local_topology_note']='Original topology restored after atlas-split experiment. Continuous hip/tunic field avoids tearing the fused generated waist surfaces. No topology edits in final mesh.'
for test,pos in [('legs',(3,-5,1.6)),('crouch',(3,-5,1.8))]:
    pose_world(rig,TESTS[test]);camera(s,pos);render(s,'sister-continuous-'+test)
reset_pose(rig)
result={'audit':audit(ob,rig),'uv_exact':signature(ob.data)['uv']==signature(src.data)['uv']}
