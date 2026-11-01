exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v1/animlib.py').read(),'animlib','exec'))
import ast
tree=ast.parse(open(BASE+'/03_brother_actions.py').read());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='build');exec(compile(ast.unparse(node).replace("'_v1'","'_v3'").replace("'_Idle_v1'","'_Idle_v3'"),'build_v3','exec'))
result={}
for label in ['Brother','Sister']:
 result[label]=build(label);bpy.data.objects[label+'_AnimRig_v1']['clip_suffix']='v3'
for clip,frame,view in [('Idle',1,'front'),('Run',5,'front'),('SwordSlash',11,'front'),('SpearThrust',12,'side'),('TakeDamage',4,'front')]:render('Sister',clip,frame,BASE+'/sister-'+clip.lower()+'-v3.png',view)
path=BASE+'/siblings-animation-v003-both-clips.blend';assert not os.path.exists(path);bpy.ops.wm.save_as_mainfile(filepath=path,compress=True)
