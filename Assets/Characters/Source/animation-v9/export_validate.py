ROOT='D:/GodotProjects/dungeons-n-academics'
script=open(ROOT+'/Assets/Characters/Source/animation-v6/export_validate.py').read()
script=script.replace("code=code.replace('animation-v4','animation-v6')", "code=code.replace('animation-v4','animation-v9')").replace("'Animated/v6'","'Animated/v9'").replace("'-animations-v6.glb'","'-animations-v9.glb'")
script=script.replace("'_v13' if label=='Brother'", "'_v16' if clip in ['SpearIdle','SpearThrust'] else '_v15' if label=='Brother' and clip in ['Walk','Run'] else '_v13' if label=='Brother'")
script=script.replace('v6: Brother tunic clearance in Walk and Run; existing motion preserved.','v9: corrected right wrist and forearm alignment in both spear clips for both characters.')
exec(compile(script,'export_v9','exec'))
