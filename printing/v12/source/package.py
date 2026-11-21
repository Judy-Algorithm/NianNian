from pathlib import Path
import xml.etree.ElementTree as ET,zipfile,struct,json
R=Path(__file__).resolve().parent
ctx={'__file__':str(R/'package.py')}
exec((R/'reference/v10/package.py').read_text().split("plate('00_")[0],ctx)
parts=['A_main_two_bay.stl','C_rear_cover.stl','E_battery_spacer.stl','K_BOOT_cap.stl','K_RST_cap.stl']
fn='V12_蓝色全套5件_纯模型.3mf';ctx['plate'](fn,parts)
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
p=R/'print'/fn
with zipfile.ZipFile(p) as z:contents={n:z.read(n) for n in z.namelist()}
root=ET.fromstring(contents['3D/3dmodel.model']);objs=root.findall('m:resources/m:object',ns);items=root.findall('m:build/m:item',ns)
for item in items:
 tr=[float(q) for q in item.attrib['transform'].split()];tr[9]+=15;tr[10]+=25;item.set('transform',' '.join(str(q) for q in tr))
for j in [3,4]:
 vs=objs[j].findall('m:mesh/m:vertices/m:vertex',ns)
 lo=[min(float(v.attrib[a]) for v in vs) for a in ['x','y','z']]
 items[j].set('transform',f'1 0 0 0 1 0 0 0 1 {25+(j-3)*20-lo[0]} {110-lo[1]} {-lo[2]}')
contents['3D/3dmodel.model']=ET.tostring(root,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
 for k,v in contents.items():z.writestr(k,v)
ctx['plate']('V12_仅前壳后盖垫片_纯模型.3mf',parts[:3])
for fn,k in [('花瓣_白色.3mf','D_daisy_petals.stl'),('花心_黄色.3mf','D2_daisy_center.stl'),('花柄叶片_黑色.3mf','D3_stem_leaves.stl')]:ctx['plate'](fn,[k])
print('Prepared 5-part one-plate model and optional single-color flower files')
