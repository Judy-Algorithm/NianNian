"""Check exported binary STL topology, units/bounds, and bed placement without external mesh packages."""
from pathlib import Path
from collections import Counter
import struct,json,math

ROOT=Path(__file__).resolve().parent
results=[]
for path in sorted((ROOT/'print').glob('*.stl')):
    raw=path.read_bytes();count=struct.unpack_from('<I',raw,80)[0]
    assert len(raw)==84+50*count, f'Unexpected STL encoding: {path.name}'
    edges=Counter();points=[];zero_faces=0;volume=0.0
    for n in range(count):
        chunk=struct.unpack_from('<12fH',raw,84+50*n)
        v=[tuple(round(x,5) for x in chunk[3+i*3:6+i*3]) for i in range(3)]
        points.extend(v)
        for a,b in [(v[0],v[1]),(v[1],v[2]),(v[2],v[0])]: edges[tuple(sorted((a,b)))]+=1
        a,b,c=v
        cross=((b[1]-a[1])*(c[2]-a[2])-(b[2]-a[2])*(c[1]-a[1]),
               (b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2]),
               (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))
        zero_faces+=math.sqrt(sum(x*x for x in cross))<1e-9
        volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
    lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
    bad_edges=sum(x!=2 for x in edges.values())
    row={'file':path.name,'triangles':count,'watertight':bad_edges==0,'non_manifold_or_boundary_edges':bad_edges,
         'degenerate_faces':zero_faces,'positive_volume':volume>0,
         'bounding_box_mm':[round(hi[i]-lo[i],3) for i in range(3)],'bed_z_min':lo[2]}
    row['pass']=row['watertight'] and not zero_faces and row['positive_volume'] and abs(lo[2])<.001
    results.append(row)
(ROOT/'mesh-check-report.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
assert all(x['pass'] for x in results), 'STL validation failed'
