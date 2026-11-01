exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v1/animlib.py').read(),'animlib','exec'))
import ast
tree=ast.parse(open(BASE+'/03_brother_actions.py').read());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='build')
code=ast.unparse(node).replace("'_v1'","'_v2'")
exec(compile(code,'build_v2','exec'))
result={'Brother':build('Brother')};bpy.data.objects['Brother_AnimRig_v1']['clip_suffix']='v2'
for clip,frame,view in [('Idle',1,'front'),('SwordSlash',11,'front'),('SpearThrust',12,'side'),('Walk',8,'side')]:render('Brother',clip,frame,BASE+'/brother-'+clip.lower()+'-refined.png',view)
