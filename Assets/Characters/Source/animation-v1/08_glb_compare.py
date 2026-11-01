exec(compile(open('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Source/animation-v1/animlib.py').read(),'animlib','exec'))
import bisect
def load_glb(path):
 raw=open(path,'rb').read();ln=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+ln]);offset=20+ln;binlen=struct.unpack_from('<I',raw,offset)[0];binary=raw[offset+8:offset+8+binlen]
 def access(i):
  a=doc['accessors'][i];bv=doc['bufferViews'][a['bufferView']];n={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']];fmt='<'+str(n)+'f';start=bv.get('byteOffset',0)+a.get('byteOffset',0);stride=bv.get('byteStride',n*4)
  return [struct.unpack_from(fmt,binary,start+j*stride) for j in range(a['count'])]
 return doc,access
refs=json.load(open(BASE+'/pose-reference.json'));result={}
for label in ['brother','sister']:
 doc,access=load_glb('D:/GodotProjects/dungeons-n-academics/Assets/Characters/Animated/v1/'+label+'-animations-v1.glb');parents={c:i for i,n in enumerate(doc['nodes']) for c in n.get('children',[])};out={}
 for a in doc['animations']:
  channels=[];end=0
  for c in a['channels']:
   sam=a['samplers'][c['sampler']];times=[x[0] for x in access(sam['input'])];values=access(sam['output']);channels.append((c['target']['node'],c['target']['path'],times,values));end=max(end,times[-1])
  errs=[]
  for sample in refs[label][a['name']]:
   t=sample['fraction']*end;trs={i:{'translation':list(n.get('translation',[0,0,0])),'rotation':list(n.get('rotation',[0,0,0,1])),'scale':list(n.get('scale',[1,1,1]))} for i,n in enumerate(doc['nodes'])}
   for ni,path,times,values in channels:
    j=max(0,min(len(times)-2,bisect.bisect_right(times,t)-1));f=max(0,min(1,(t-times[j])/(times[j+1]-times[j]))) if len(times)>1 else 0
    if path=='rotation':
     av=values[j];bv=values[min(j+1,len(values)-1)];qa=Quaternion((av[3],*av[:3]));qb=Quaternion((bv[3],*bv[:3]));q=qa.slerp(qb,f);trs[ni][path]=[q.x,q.y,q.z,q.w]
    else:trs[ni][path]=[x+(y-x)*f for x,y in zip(values[j],values[min(j+1,len(values)-1)])]
   world={}
   def wm(i):
    if i in world:return world[i]
    tr=trs[i];q=tr['rotation'];M=Matrix.LocRotScale(Vector(tr['translation']),Quaternion((q[3],*q[:3])),Vector(tr['scale']))
    if 'matrix' in doc['nodes'][i]:M=Matrix([doc['nodes'][i]['matrix'][j:j+4] for j in range(0,16,4)]).transposed()
    world[i]=wm(parents[i])@M if i in parents else M;return world[i]
   bybone={}
   for name,point in sample['points'].items():
    ni=next(i for i,n in enumerate(doc['nodes']) if n.get('name')==name);bybone[name]=(wm(ni).translation-Vector(point)).length
   errs.append({'fraction':sample['fraction'],'errors_m':bybone})
  out[a['name']]={'duration':end,'samples':errs}
 result[label]=out
json.dump(result,open(BASE+'/raw-glb-comparison.json','w'),indent=2)
result={label:{clip:{'max_error':max(max(s['errors_m'].values()) for s in c['samples']),'worst_bone':max(c['samples'][0]['errors_m'],key=c['samples'][0]['errors_m'].get)} for clip,c in clips.items()} for label,clips in result.items()}
