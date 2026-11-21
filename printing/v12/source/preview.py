from pathlib import Path
import json,math
from PIL import Image,ImageDraw
import cadquery as cq
R=Path(__file__).resolve().parent
ctx={'__file__':str(R/'reference/v10/render_base.py')}
exec((R/'reference/v10/render_base.py').read_text(),ctx)
parts=json.loads((R/'mesh-data.json').read_text())
P=json.loads((R/'params.json').read_text());T=P['body_depth']
def ref(k,w,h,t,x,y,z,c):
 o=cq.Workplane('XY').box(w,h,t,centered=(True,True,False)).translate((x,y,z));v,f=o.val().tessellate(.15,.25)
 return dict(key=k,color=c,explode=0,v=[[a.x,a.y,a.z] for a in v],f=[list(q) for q in f])
screen=ref('LCD_position',34.6,48,.04,-19.8,-.1,T-1.02,'#1f3946')
pcb=ref('PCB_placeholder',35.02,48.22,1.6,-19.8,0,T-6.7,'#4c7481')
battery=ref('battery_placeholder',34,50,6,19.5,0,1.5,'#e5d9ba')
ctx['im']=Image.new('RGB',(1900,1240),'#f7f5f0');ctx['draw']=ImageDraw.Draw(ctx['im']);t=ctx['text']
t(55,35,'念念 V12｜11.4 mm 主体 · 蓝色件一盘打印',44)
t(55,105,'蓝色外壳 · 白色花瓣 · 黄色花心 · 黑色花柄和叶片',26,'#647887')
for x in [35,970]:ctx['panel'](x,165,x+895,895)
t(65,190,'正面｜保留屏幕左、雏菊右',30)
ctx['parts']=parts+[screen]
ctx['render']((70,260,895,830),None,-.10,-.15)
t(1000,190,'打开后盖｜主板仓＋电池仓',30)
ctx['parts']=[p for p in parts if p['key'] not in ['C_rear_cover'] and not p['key'].startswith('D')]+[screen,pcb,battery]
ctx['render']((1000,260,1825,830),None,math.pi-.1,.26)
t(65,940,'取消：独立电池盒、盒盖和单独主板压框。',31)
t(65,995,'保留：整体壳、可拆后盖、两颗防脱按键帽、一块承托垫片。',29)
t(65,1050,'主体 11.4 mm；USB 下沿局部加强至 12 mm；电池垫片 2.8 mm。',26,'#647887')
t(65,1105,'真实 CAD 预览，硬件为占位示意；尚未实物验证 V12 适配与按键回弹。',24,'#9b634e')
ctx['im'].save(R/'views/V12_整体双仓预览.png')
print('Preview saved',flush=True)
