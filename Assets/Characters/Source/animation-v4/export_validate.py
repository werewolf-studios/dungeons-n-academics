ROOT='D:/GodotProjects/dungeons-n-academics'
PREV=ROOT+'/Assets/Characters/Source/animation-v2'
DEST=ROOT+'/Assets/Characters/Source/animation-v4'
code=open(PREV+'/export_validate.py').read()
code=code.replace("BASE='"+PREV+"'", "BASE='"+DEST+"'")
code=code.replace("OLD=BASE.replace('animation-v2','animation-v1')", "OLD='"+ROOT+"/Assets/Characters/Source/animation-v1'")
code=code.replace("open(BASE+'/refine.py')", "open('"+PREV+"/refine.py')")
code=code.replace("refs={};audit={}", "BASE='"+DEST+"'\nSPECS['TakeDamage']=(24,False,None)\nrefs={};audit={}")
code=code.replace("('_v6' if clip in ['Walk','Run','SwordSlash'] else '_v3')", "('_v11' if clip=='TakeDamage' or (clip=='Idle' and label=='Brother') else '_v7' if clip in ['SwordIdle','SwordSlash'] else '_v6' if clip in ['Walk','Run'] else '_v3')")
code=code.replace("if clip in ['Walk','Run','SwordSlash']:","if clip in ['Idle','Walk','Run','SwordSlash','TakeDamage']:")
code=code.replace('Animated/v2','Animated/v4').replace('-animations-v2.glb','-animations-v4.glb')
code=code.replace("OUT.replace('/v2','/v1')", "'"+ROOT+"/Assets/Characters/Animated/v3'")
code=code.replace("manifest['revision']='v2: Walk, Run and stepping SwordSlash refined; other five clips unchanged.'", "manifest['revision']='v4: Brother right-arm Idle correction and stronger TakeDamage for both.'\nmanifest['clips']['TakeDamage'].update(duration=1.0,event_frame=4,event_time_seconds=.125)")
code=code.replace('v1 preview confirmed working by user; v2 awaiting user visual review.','v3 preview confirmed by user; v4 idle and damage refinements awaiting visual review.')
exec(compile(code,'export_validate_v4','exec'))

