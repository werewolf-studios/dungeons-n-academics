ROOT='D:/GodotProjects/dungeons-n-academics'
script=open(ROOT+'/Assets/Characters/Source/animation-v6/export_validate.py').read()
script=script.replace("code=code.replace('animation-v4','animation-v6')", "code=code.replace('animation-v4','animation-v8')").replace("'Animated/v6'","'Animated/v8'").replace("'-animations-v6.glb'","'-animations-v8.glb'")
script=script.replace("'_v13' if label=='Brother'", "'_v15' if label=='Brother' and clip in ['Walk','Run'] else '_v13' if label=='Brother'")
script=script.replace('v6: Brother tunic clearance in Walk and Run; existing motion preserved.','v8: Brother natural tunic drape with upper-trouser support weights.')
exec(compile(script,'export_v8','exec'))
