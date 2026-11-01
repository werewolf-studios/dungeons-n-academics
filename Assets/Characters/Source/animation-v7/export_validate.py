ROOT='D:/GodotProjects/dungeons-n-academics'
script=open(ROOT+'/Assets/Characters/Source/animation-v6/export_validate.py').read()
script=script.replace("code=code.replace('animation-v4','animation-v6')", "code=code.replace('animation-v4','animation-v7')").replace("'Animated/v6'","'Animated/v7'").replace("'-animations-v6.glb'","'-animations-v7.glb'")
script=script.replace("'_v13' if label=='Brother'", "'_v14' if label=='Brother' and clip in ['Walk','Run'] else '_v13' if label=='Brother'")
script=script.replace('v6: Brother tunic clearance in Walk and Run; existing motion preserved.','v7: steady Brother locomotion tunic panels without alternating expansion.')
exec(compile(script,'export_v7','exec'))
