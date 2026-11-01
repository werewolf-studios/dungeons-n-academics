exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/rigging-v1/riglib.py').read(),'riglib.py','exec'))
import ast
def load_function(file,name):
    tree=ast.parse(open(BASE+'/'+file).read()); node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    exec(compile(ast.Module(body=[node],type_ignores=[]),file,'exec'),globals())
load_function('07_brother_validate.py','evaluate_tests')
ob=bpy.data.objects['Brother_RigMesh_v1'];rig=bpy.data.objects['Brother_Humanoid_v1'];s=bpy.data.scenes['Brother_Rig_Validation_v1'];bpy.context.window.scene=s
report=json.load(open(BASE+'/brother-validation-v003.json'));report['deformations']=evaluate_tests(ob,rig)
report['preexisting_near_zero_triangle_polygons']=[872,1826,4740]
report['new_collapsed_triangles']=0
report['limitations'].append('Three near-collinear triangles are present before binding (two boot details and a collar detail); these are not new joint collapses. Source topology retained.')
report['visual_review']['waist_final']='Removed residual upper-arm influence from central waist band z=1.045..1.115; band follows pelvis rigidly.'
rig.animation_data.action=bpy.data.actions['Brother_DEFORM_TEST_v1'];s.frame_set(1)
camera(s,(0,-5,1));render(s,'brother-final-bind')
json.dump(report,open(BASE+'/brother-validation-v004.json','w'),indent=2)
path=BASE+'/brother-rig-v004-final.blend';assert not os.path.exists(path);bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
# Only after brother validation: prepare an independent sister scene and body fit.
load_function('01_prepare.py','prepare')
ss,so,col=prepare('Sister','Sister_Clean_v1');bpy.context.window.scene=ss
parts=shells(so);info=[]
for i,ids in enumerate(parts):
    vs=[so.data.vertices[j].co for j in ids]
    info.append({'id':i,'count':len(ids),'bounds':[[round(min(v[k] for v in vs),4),round(max(v[k] for v in vs),4)] for k in range(3)],'center':[round(sum(v[k] for v in vs)/len(vs),4) for k in range(3)]})
json.dump(info,open(BASE+'/sister-shells.json','w'),indent=2)
render(ss,'sister-bind-front')
result={'brother_saved':path,'brother_waist_max_stretch':max(r['waist_band_stretch_max'] for r in report['deformations']),'sister_shells':info}
