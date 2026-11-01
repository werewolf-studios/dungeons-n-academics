import os
ROOT='D:/GodotProjects/dungeons-n-academics'
PREV=ROOT+'/Assets/Characters/Source/animation-v2'
DEST=ROOT+'/Assets/Characters/Source/animation-v3'
code=open(PREV+'/export_validate.py').read()
code=code.replace("BASE='"+PREV+"'", "BASE='"+DEST+"'")
code=code.replace("OLD=BASE.replace('animation-v2','animation-v1')", "OLD='"+ROOT+"/Assets/Characters/Source/animation-v1'")
code=code.replace("open(BASE+'/refine.py')", "open('"+PREV+"/refine.py')")
code=code.replace("refs={};audit={}", "BASE='"+DEST+"'\nrefs={};audit={}")
code=code.replace("('_v6' if clip in ['Walk','Run','SwordSlash'] else '_v3')", "('_v7' if clip in ['SwordIdle','SwordSlash'] else '_v6' if clip in ['Walk','Run'] else '_v3')")
code=code.replace("Animated/v2", "Animated/v3").replace('-animations-v2.glb','-animations-v3.glb')
code=code.replace("OUT.replace('/v2','/v1')", "'"+ROOT+"/Assets/Characters/Animated/v2'")
code=code.replace("manifest['revision']='v2: Walk, Run and stepping SwordSlash refined; other five clips unchanged.'", "manifest['revision']='v3: corrected thumb-side sword grip and forearm roll for SwordIdle and SwordSlash; other six clips unchanged.'\nmanifest['socket']['sword_rotation_degrees']=[-90,0,0]\nmanifest['socket']['spear_rotation_degrees']=[90,0,0]")
code=code.replace("v1 preview confirmed working by user; v2 awaiting user visual review.","v2 preview confirmed by user; v3 grip correction awaiting Godot visual review.")
exec(compile(code,'export_validate_v3','exec'))
