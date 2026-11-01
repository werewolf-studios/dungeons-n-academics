exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
import numpy as np
s=bpy.data.scenes['Sister_Rig_Validation_v1'];bpy.context.window.scene=s
ob=bpy.data.objects['Sister_RigMesh_v1'];col=bpy.data.collections['Sister_Rig_Working_v1']
fit={'shoulder':(.14,-.015,1.33),'elbow':(.273,-.025,1.105),'wrist':(.375,-.025,.91),'hand':(.423,-.035,.775),
 'hip':(.09,0,.95),'knee':(.143,-.025,.525),'ankle':(.175,.015,.175),'ball':(.19,-.155,.058),'toe':(.193,-.26,.05)}
rig=make_rig('Sister',col,fit)
activate(rig);bpy.ops.object.mode_set(mode='EDIT')
for name,h,t in [('pelvis',(0,0,.95),(0,0,1.10)),('spine',(0,0,1.10),(0,0,1.21)),('chest',(0,0,1.21),(0,0,1.34)),('neck',(0,0,1.34),(0,0,1.445)),('head',(0,0,1.445),(0,0,1.73))]:
    b=rig.data.edit_bones[name];b.head=h;b.tail=t;b.align_roll(Vector((0,1,0)))
for side in ['L','R']:rig.data.edit_bones['clavicle.'+side].head=(0,0,1.32)
bpy.ops.object.mode_set(mode='OBJECT')
activate(ob);rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.parent_set(type='ARMATURE_AUTO')
for m in ob.modifiers:
    if m.type=='ARMATURE':m.use_deform_preserve_volume=True
initial=audit(ob,rig)
weights=[{ob.vertex_groups[g.group].name:g.weight for g in v.groups} for v in ob.data.vertices]
json.dump(weights,open(BASE+'/sister-auto-weights.json','w'))
json.dump(initial,open(BASE+'/sister-auto-weights-audit.json','w'),indent=2)
add_tunic_bones(rig)
parts=shells(ob)
# Sample atlas colors to distinguish the connected lower tunic from opaque leggings.
image=next(n.image for n in ob.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.image.name.endswith('_0'))
pix=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(pix);pix=pix.reshape(image.size[1],image.size[0],4)
colors=np.zeros((len(ob.data.vertices),3));counts=np.zeros(len(ob.data.vertices))
for loop in ob.data.loops:
    uv=ob.data.uv_layers.active.data[loop.index].uv;u=int(uv.x*(image.size[0]-1));v=int(uv.y*(image.size[1]-1))
    colors[loop.vertex_index]+=pix[v,u,:3];counts[loop.vertex_index]+=1
colors/=np.maximum(counts,1)[:,None]
json.dump(colors.tolist(),open(BASE+'/sister-vertex-colors.json','w'))
color_report=[]
for i in parts[3]:
    v=ob.data.vertices[i]
    if .78<v.co.z<1.09:color_report.append({'id':i,'co':[round(c,4) for c in v.co],'rgb':[round(c,4) for c in colors[i]]})
json.dump(color_report,open(BASE+'/sister-lower-garment-samples.json','w'),indent=2)
pose_world(rig,TESTS['legs']);camera(s,(3,-5,1.6));render(s,'sister-auto-legs')
reset_pose(rig)
path=BASE+'/siblings-rig-v005-sister-auto.blend';assert not os.path.exists(path);bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
result={'saved':path,'initial_audit':initial,'color_examples':color_report[::max(1,len(color_report)//16)]}
