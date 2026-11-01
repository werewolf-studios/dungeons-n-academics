ROOT='D:/GodotProjects/dungeons-n-academics'
wrapper=open(ROOT+'/Assets/Characters/Source/animation-v4/export_validate.py').read()
exec(compile(wrapper.rsplit('exec(compile(code',1)[0],'setup','exec'))
code=code.replace('animation-v4','animation-v6').replace('Animated/v4','Animated/v6').replace('-animations-v4.glb','-animations-v6.glb')
lines=code.splitlines()
for i,line in enumerate(lines):
 if line.startswith('def action('):lines[i]="def action(label,clip):return bpy.data.actions[label+'_'+clip+('_v13' if label=='Brother' else '_v12' if clip=='TakeDamage' else '_v7' if clip in ['SwordIdle','SwordSlash'] else '_v6' if clip in ['Walk','Run'] else '_v3')]"
code='\n'.join(lines)
code=code.replace('v4: Brother right-arm Idle correction and stronger TakeDamage for both.','v6: Brother tunic clearance in Walk and Run; existing motion preserved.')
exec(compile(code,'export_v6','exec'))
