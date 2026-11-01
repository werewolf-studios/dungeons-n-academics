import bpy, math, json, os, hashlib, struct
from mathutils import Vector, Matrix
from mathutils import Quaternion
BASE='D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1'
def activate(ob):
    if bpy.context.object and bpy.context.object.mode!='OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT'); ob.hide_set(False); ob.select_set(True); bpy.context.view_layer.objects.active=ob
def shells(ob):
    adj=[[] for v in ob.data.vertices]
    for e in ob.data.edges:
        a,b=e.vertices; adj[a].append(b); adj[b].append(a)
    seen=set(); parts=[]
    for v in ob.data.vertices:
        if v.index in seen: continue
        ids=[]; todo=[v.index]; seen.add(v.index)
        while todo:
            i=todo.pop(); ids.append(i)
            for j in adj[i]:
                if j not in seen: seen.add(j); todo.append(j)
        parts.append(ids)
    return sorted(parts,key=len,reverse=True)
def signature(mesh):
    return {'vertices':len(mesh.vertices),'faces':len(mesh.polygons),
      'coords':hashlib.sha256(b''.join(struct.pack('3f',*v.co) for v in mesh.vertices)).hexdigest(),
      'uv':hashlib.sha256(b''.join(struct.pack('2f',*d.uv) for d in mesh.uv_layers.active.data)).hexdigest()}
def make_rig(label, col, fit=None):
    data=bpy.data.armatures.new(label+'_HumanoidData_v1'); rig=bpy.data.objects.new(label+'_Humanoid_v1',data); col.objects.link(rig)
    rig.show_in_front=True; data.display_type='OCTAHEDRAL'; activate(rig); bpy.ops.object.mode_set(mode='EDIT')
    specs=[('root',(0,0,0),(0,0,.15),None,False),
       ('pelvis',(0,0,.9),(0,0,1.04),'root',True),
       ('spine',(0,0,1.04),(0,0,1.16),'pelvis',True),
       ('chest',(0,0,1.16),(0,0,1.32),'spine',True),
       ('neck',(0,0,1.32),(0,0,1.43),'chest',True),
       ('head',(0,0,1.43),(0,0,1.72),'neck',True)]
    fit=fit or {}
    for side,sgn in [('L',1),('R',-1)]:
        def p(x,y,z): return (sgn*x,y,z)
        shoulder=p(*fit.get('shoulder',(.155,0,1.32)))
        elbow=p(*fit.get('elbow',(.298,-.005,1.077)))
        wrist=p(*fit.get('wrist',(.399,-.015,.867)))
        hand=p(*fit.get('hand',(.429,-.02,.728)))
        hip=p(*fit.get('hip',(.102,0,.91)))
        knee=p(*fit.get('knee',(.173,-.018,.51)))
        ankle=p(*fit.get('ankle',(.212,.012,.145)))
        ball=p(*fit.get('ball',(.223,-.125,.062)))
        toe=p(*fit.get('toe',(.225,-.205,.05)))
        specs += [('clavicle.'+side,(0,0,1.30),shoulder,'chest',True),
        ('upper_arm.'+side,shoulder,elbow,'clavicle.'+side,True),
        ('forearm.'+side,elbow,wrist,'upper_arm.'+side,True),
        ('hand.'+side,wrist,hand,'forearm.'+side,True),
        ('thigh.'+side,hip,knee,'pelvis',True),
        ('shin.'+side,knee,ankle,'thigh.'+side,True),
        ('foot.'+side,ankle,ball,'shin.'+side,True),
        ('toe.'+side,ball,toe,'foot.'+side,True)]
    for name,h,t,parent,deform in specs:
        b=data.edit_bones.new(name); b.head=h; b.tail=t; b.use_deform=deform
        if parent:b.parent=data.edit_bones[parent]
        # Orient local X consistently for flexion; arm bend axes are inspected in test renders.
        b.align_roll(Vector((0,1,0)))
    bpy.ops.object.mode_set(mode='OBJECT')
    rig['hierarchy']='DNA_Humanoid_v1'; rig['axes']='Blender +Z up / -Y forward -> glTF +Y up / +Z forward'
    rig['purpose']='FK deformation rig; diagnostic actions only, no production locomotion'
    return rig
def audit(ob,rig):
    ob.data.calc_loop_triangles()
    counts=[]; sums=[]; empty=[]; bad=[]
    deform={b.name for b in rig.data.bones if b.use_deform}
    for v in ob.data.vertices:
        ws=[g.weight for g in v.groups if ob.vertex_groups[g.group].name in deform and g.weight>1e-6]
        counts.append(len(ws)); sums.append(sum(ws))
        if not ws:empty.append(v.index)
        if abs(sum(ws)-1)>1e-5:bad.append(v.index)
    return {'vertices':len(ob.data.vertices),'triangles':len(ob.data.loop_triangles),'unweighted':len(empty),
      'non_normalized':len(bad),'max_influences':max(counts),'over_four':sum(c>4 for c in counts),
      'weight_sum_range':[min(sums),max(sums)],'bones':len(rig.data.bones),'deform_bones':len(deform)}
def add_tunic_bones(rig):
    activate(rig);bpy.ops.object.mode_set(mode='EDIT')
    for side in ['L','R']:
        if rig.data.edit_bones.get('tunic.'+side):continue
        thigh=rig.data.edit_bones['thigh.'+side]
        b=rig.data.edit_bones.new('tunic.'+side);b.head=thigh.head+Vector((0,0,.125));b.tail=b.head+(thigh.tail-thigh.head);b.roll=thigh.roll;b.parent=rig.data.edit_bones['pelvis']
    bpy.ops.object.mode_set(mode='OBJECT')
    for side in ['L','R']:
        pb=rig.pose.bones['tunic.'+side]
        for c in list(pb.constraints):pb.constraints.remove(c)
        # A translated hem avoids folding a short split tunic back on itself at high hip flexion.
        forward=pb.bone.matrix_local.to_3x3().inverted() @ Vector((.02 if side=='L' else -.02,-.30,.065))
        backward=pb.bone.matrix_local.to_3x3().inverted() @ Vector((.01 if side=='L' else -.01,.10,.025))
        for axis in range(3):
            pb.driver_remove('location',axis)
            fc=pb.driver_add('location',axis);d=fc.driver;d.type='SCRIPTED'
            v=d.variables.new();v.name='r';v.type='TRANSFORMS';t=v.targets[0];t.id=rig;t.bone_target='thigh.'+side;t.transform_type='ROT_X';t.transform_space='LOCAL_SPACE'
            d.expression=f'{forward[axis]:.8f}*max(0,min(1,-r/0.96))+{backward[axis]:.8f}*max(0,min(1,r/0.52))'
    rig['cloth_notes']='Translated tunic hem drivers follow local thigh flexion, limited at 55deg forward/30deg backward. Bake helper transforms on future animation export; no cloth physics.'
def set_weights(ob,i,weights):
    weights={k:w for k,w in weights.items() if w>1e-5}
    weights=dict(sorted(weights.items(),key=lambda kv:kv[1],reverse=True)[:4]); total=sum(weights.values())
    assert total>0
    for g in list(ob.data.vertices[i].groups): ob.vertex_groups[g.group].remove([i])
    for k,w in weights.items():
        vg=ob.vertex_groups.get(k) or ob.vertex_groups.new(name=k); vg.add([i],w/total,'REPLACE')
def smoothstep(a,b,x):
    t=max(0,min(1,(x-a)/(b-a))); return t*t*(3-2*t)
def mix(a,b,t):
    out={k:v*(1-t) for k,v in a.items()}
    for k,v in b.items():out[k]=out.get(k,0)+v*t
    return out
def reset_pose(rig):
    for b in rig.pose.bones:b.rotation_mode='XYZ';b.rotation_euler=(0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
    bpy.context.view_layer.update()
def camera(s,pos,target=(0,0,.9),scale=2.12):
    s.camera.location=pos; s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale
def render(s,name):
    s.render.filepath=BASE+'/'+name+'.png'; bpy.ops.render.render(write_still=True)
    return s.render.filepath
def pose_world(rig, rotations):
    reset_pose(rig)
    for name, xyz in rotations.items():
        pb=rig.pose.bones[name]; pb.rotation_mode='QUATERNION'
        q=Quaternion((1,0,0,0))
        for axis,deg in zip([(1,0,0),(0,1,0),(0,0,1)],xyz):
            vec=pb.bone.matrix_local.to_3x3().inverted() @ Vector(axis)
            q=Quaternion(vec,math.radians(deg)) @ q
        pb.rotation_quaternion=q
    bpy.context.view_layer.update()
TESTS={
 'arms':{'upper_arm.L':(-35,-15,0),'upper_arm.R':(-25,15,0),'forearm.L':(-95,0,0),'forearm.R':(-80,0,0),'hand.L':(0,20,20),'hand.R':(0,-20,-20)},
 'legs':{'thigh.L':(-55,0,-8),'shin.L':(95,0,0),'foot.L':(-20,0,0),'toe.L':(20,0,0),'thigh.R':(15,0,8),'shin.R':(20,0,0),'foot.R':(15,0,0)},
 'torso':{'pelvis':(8,0,0),'spine':(18,8,12),'chest':(12,8,12),'neck':(10,-10,15),'head':(-10,0,20)},
 'shoulders':{'upper_arm.L':(0,-65,0),'upper_arm.R':(0,65,0),'clavicle.L':(0,-8,0),'clavicle.R':(0,8,0),'forearm.L':(-30,0,0),'forearm.R':(-30,0,0)},
 'crouch':{'pelvis':(12,0,0),'spine':(12,0,0),'chest':(-8,0,0),'thigh.L':(-60,0,-8),'thigh.R':(-60,0,8),'shin.L':(100,0,0),'shin.R':(100,0,0),'foot.L':(-30,0,0),'foot.R':(-30,0,0)},
 'stride':{'thigh.L':(-30,0,0),'shin.L':(55,0,0),'foot.L':(-15,0,0),'thigh.R':(20,0,0),'shin.R':(15,0,0),'foot.R':(10,0,0),'upper_arm.L':(15,0,0),'upper_arm.R':(-20,0,0),'forearm.L':(-20,0,0),'forearm.R':(-30,0,0)},
 'wrists_ankles':{'hand.L':(25,10,20),'hand.R':(-25,-10,-20),'foot.L':(20,0,10),'foot.R':(-20,0,-10),'neck':(0,15,15),'head':(10,0,15)},
}
