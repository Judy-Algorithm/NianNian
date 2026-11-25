"""V12: 11.4 mm two-bay body, locally reinforced USB lip, rear-loading caps.

The nominal geometry is a fit prototype, not a physically verified production fit.
All units are mm. The V10 manufacturer reference is used without mirroring hardware.
"""
from pathlib import Path
import cadquery as cq
import json, shutil, math

R=Path(__file__).resolve().parent
REF=R/'reference/v10'
P=json.loads((REF/'params.json').read_text())
P.update(button_hole_width=2.5,button_hole_height=1.8,
         button_shaft_width=1.8,button_shaft_height=1.2,
         button_rest_gap=.35,button_max_travel=.50,
         battery_rear_gap=.5,battery_front_pad=.3)
if (R/'params.json').exists():P.update(json.loads((R/'params.json').read_text()))
P['battery_spacer_height']=round(P['body_depth']-P['rear_skin']-P['front_skin']
    -P['battery_thickness']-P['battery_front_pad']-P['battery_rear_gap'],3)
assert P['battery_spacer_height']>=.8
(R/'params.json').write_text(json.dumps(P,ensure_ascii=False,indent=2)+'\n')

# Reuse the measured board envelope, screen bezel and original removable-cover fit.
# Rear-loading U slots allow the double-ended caps to be assembled without force.
prefix=(REF/'base/build.py').read_text().split('# Ordinary ten-petal daisy')[0]
prefix=prefix.replace("P=json.loads((R/'params.json').read_text())","P=params_override")
start=prefix.index('# Four battery-cartridge seats.')
end=prefix.index('# USB-C cable jacket clearance;')
prefix=prefix[:start]+prefix[end:]
start=prefix.index('def service_cuts(o):')
end=prefix.index('main=service_cuts(main)')
prefix=prefix[:start]+'''def service_cuts(o):
 o=o.cut(box(P['usb_width'],8,P['usb_height'],bx,-H/2,z=P['usb_center_z']-P['usb_height']/2,r=.5))
 for dx in [P['boot_vendor_x'],P['reset_vendor_x']]:
  floor=P['button_actuator_z']-P['button_hole_height']/2
  o=o.cut(box(P['button_hole_width'],8,S+.5-floor,bx+dx,-H/2,z=floor,r=.15))
 return o
'''+prefix[end:]
start=prefix.index('# Separate complete battery cartridge,')
end=prefix.index('# Rear cover nests on the perimeter;')
prefix=prefix[:start]+prefix[end:]
prefix=prefix.replace("for y in [-18,18]:rear=rear.union(box(8,4,.6,tx,y,S-.6))", "# Battery retention uses the removable spacer and a measured soft pad.")
prefix=prefix.replace('rear=service_cuts(rear.union(lip))',
 'rear=rear.union(lip).cut(box(P["usb_width"],8,P["usb_height"],bx,-H/2,z=P["usb_center_z"]-P["usb_height"]/2,r=.5))')
ctx={'__file__':str(REF/'base/build.py'),'params_override':P}
exec(prefix,ctx)
box=ctx['box'];cyl=ctx['cyl'];main=ctx['main'];rear=ctx['rear']
W=P['body_width'];H=P['body_height'];T=P['body_depth'];F=P['front_skin'];S=T-P['rear_skin']
bx=P['board_x'];tx=P['battery_x']

# Closing tongues are part of the removable cover. Leave clearance above the shaft.
slot_top=P['button_actuator_z']+P['button_hole_height']/2+.15
for dx in [P['boot_vendor_x'],P['reset_vendor_x']]:
 rear=rear.union(box(P['button_hole_width']-.3,P['wall']-.3,S+.2-slot_top,
    bx+dx,-H/2+P['wall']/2,slot_top,r=.1))

# Integral right-hand battery location: no separate battery box or battery-box lid.
# The bay does not squeeze the pouch. All edges remain outside a 34.8 x 50.8 envelope.
bw=P['battery_width']+.8;bh=P['battery_height']+.8
for x in [tx-bw/2-.3,tx+bw/2+.3]:
 for y in [-16,16]:main=main.union(box(.6,8,8,x,y,F,r=.15))
for y in [-bh/2-.3,bh/2+.3]:
 for dx in [-10,10]:main=main.union(box(7,.6,8,tx+dx,y,F,r=.15))
# Continuous electrical separation with a generous wire pass near the middle.
divider=box(.8,H-2*P['wall'],S-F,0.8,0,F)
divider=divider.cut(box(4,9,4,0.8,0,S-3.9,r=.3))
# Clearance for the rear-cover registration lip at BOTH ends of the divider.
# Without these notches the original V12 had 0.896 mm^3 hard interference.
for y in [-H/2+P['wall']+.6,H/2-P['wall']-.6]:
 divider=divider.cut(box(1.4,2.0,1.2,.8,y,S-.9))
main=main.union(divider).clean()

# The rear cover itself retains the board over its copper spacers; no loose retainer.
# The modeled gap is 0.2 mm; a thin soft insulating pad may remove slack after fitting.
contact=P['module_front_z']+P['copper_rear_offset']+P['retainer_contact_gap']
for dx in [-P['board_hole_dx'],P['board_hole_dx']]:
 for dy in [-P['board_hole_dy'],P['board_hole_dy']]:
  rear=rear.union(cyl(3,S-contact,bx+dx,dy,contact))

# Keep the existing rear-only hanging bridge and pig, without a front-facing loop.
# Existing cover is used only for its already checked external reinforcement.
oldrear=cq.importers.importStep(str(REF/'cad/C_pig_rear_hidden_loop.step'))
oldnative=oldrear.mirror('XY',(0,0,T/2))
external=oldnative.intersect(box(W+2,H+2,8,z=S+.999))
rear=rear.union(external).clean()
# Spread the hanging load outside the enclosure, keeping the battery bay unobstructed.
lx=P['rear_loop_x'];ly=P['rear_loop_y']
pad=box(P['rear_pad_width'],P['rear_pad_length'],.6,lx,ly,T,r=1)
rib=box(lx-P['screw_x']+2.8,3.2,.6,(lx+P['screw_x'])/2,ly,T,r=.7)
for x,y in ctx['fast']:
 pad=pad.cut(cyl(3.4,1,x,y,T-.1));rib=rib.cut(cyl(3.4,1,x,y,T-.1))
rear=rear.union(pad).union(rib).clean()
# The retained 14x7 cable opening would leave only 0.25 mm at the rear lip after
# thinning the body. Reinforce just this small exterior region, not the entire body.
usb_rim=box(P['usb_width']+2.4,P['wall']+.8,P['usb_rear_rim_extra'],
 bx,-H/2+(P['wall']+.8)/2,T,r=.35)
rear=rear.union(usb_rim).clean()
assert T-P['usb_center_z']-P['usb_height']/2+P['usb_rear_rim_extra']>=.8

# A flat spacer supports the battery. The battery connects by its wire, not pressure.
spacer=box(P['battery_width']+.2,P['battery_height']+.2,P['battery_spacer_height'],tx,0,F,r=.8)

def button(dx,name):
 x=bx+dx;z=P['button_actuator_z'];outer=-H/2;inner=outer+P['wall']
 face_y=-23.802 if name=='BOOT' else -23.827
 tip=face_y-P['button_rest_gap'];head_inner=outer-P['button_max_travel']
 shaft=box(P['button_shaft_width'],tip-head_inner,P['button_shaft_height'],x,(tip+head_inner)/2,z-P['button_shaft_height']/2,r=.1)
 head=box(3.8,1.0,3.6,x,head_inner-.5,z-1.8,r=.4)
 collar=box(3.6,.7,2.8,x,inner+.4+.35,z-1.4,r=.2)
 # Collar lies inside the shell; the exterior head limits inward travel to 0.5 mm.
 return shaft.union(head).union(collar).clean()
boot=button(P['boot_vendor_x'],'BOOT');reset=button(P['reset_vendor_x'],'RST')

objects={'A_main_two_bay':main,'C_rear_cover':rear,'E_battery_spacer':spacer,
         'K_BOOT_cap':boot,'K_RST_cap':reset}
colors={k:'#79b4d9' for k in objects}
# Full-screen locating trial replaces the ambiguous pair of small edge strips.
leftclip=box(W/2-.3,H+1,T+3,x=-W/4-.15,z=-.1)
objects['T_full_board_frame']=main.intersect(leftclip).clean()
objects['T_full_board_cover']=rear.intersect(leftclip).clean()
colors.update(T_full_board_frame='#79b4d9',T_full_board_cover='#a6c5dc')

def canonical(o):return o.mirror('XY',(0,0,T/2))
assy=cq.Assembly(name='NianNian_V12_11p4mm')
mesh=[];checks=[]
for k,o in objects.items():
 assert o.val().isValid() and len(o.solids().vals())==1,(k,'invalid/multiple solids')
 real=canonical(o)
 cq.exporters.export(real,str(R/'cad'/(k+'.step')))
 back=cq.importers.importStep(str(R/'cad'/(k+'.step')))
 assert back.val().isValid() and len(back.solids().vals())==1,(k,'STEP roundtrip')
 # Main opening up; cover and caps in their own manufacturing poses.
 if k.startswith('K_'):po=real.rotate((0,0,0),(1,0,0),90)
 elif k in ['A_main_two_bay','T_full_board_frame','E_battery_spacer']:
  po=real.rotate((0,0,0),(1,0,0),180)
 else:po=real.rotate((0,0,0),(1,0,0),180) # pig/lug face upward; supports needed below cover
 po=po.translate((0,0,-po.val().BoundingBox().zmin))
 cq.exporters.export(po,str(R/'print'/(k+'.stl')),tolerance=.03,angularTolerance=.15)
 if k.startswith('T_'):continue
 assy.add(real,name=k,color=cq.Color(colors[k]))
 v,f=real.val().tessellate(.12,.25)
 mesh.append(dict(key=k,color=colors[k],group='shell',explode=0,
  v=[[a.x,a.y,a.z] for a in v],f=[list(q) for q in f]))

vendor=cq.importers.importStep(str(REF/'reference/vendor.step'))
keep=[];clip=box(100,100,50,z=-6.1)
for i,s in enumerate(vendor.solids().vals()):keep.append(s.intersect(clip.val()) if i in [309,310] else s)
hardware=cq.Workplane('XY').newObject([cq.Compound.makeCompound(keep)]).translate((bx,1.7,T-P['module_front_z']-2.1))
cellnative=box(P['battery_width'],P['battery_height'],P['battery_thickness'],tx,0,
 F+P['battery_spacer_height']+P['battery_front_pad'],r=.6)
cell=canonical(cellnative)
for name,o in [('hardware',hardware),('battery',cell)]:
 cq.exporters.export(o,str(R/'cad'/(name+'_reference.step')))
 assy.add(o,name=name,color=cq.Color('#365d67' if name=='hardware' else '#c8bfa8'))
 for k in ['A_main_two_bay','C_rear_cover','E_battery_spacer','K_BOOT_cap','K_RST_cap']:
  vol=canonical(objects[k]).val().intersect(o.val()).Volume()
  checks.append(dict(pair=k+'/'+name,volume_mm3=round(vol,6),pass_check=vol<.01))

# Caps must clear the case throughout their sliding travel and not collide with USB.
for k in ['K_BOOT_cap','K_RST_cap']:
 for t in [0,P['button_max_travel']]:
  shifted=objects[k].translate((0,t,0))
  for name,o in [('body',main),('cover',rear),('other_cap',reset if k=='K_BOOT_cap' else boot)]:
   vol=shifted.val().intersect(o.val()).Volume()
   checks.append(dict(pair=k+'/'+name,travel=t,volume_mm3=round(vol,6),pass_check=vol<.001))
  # The pressed position may intentionally meet the tactile actuator. Never USB metal.
  for i in [112,133]:
   usb=cq.Workplane('XY').newObject([vendor.solids().vals()[i]]).translate((bx,1.7,T-P['module_front_z']-2.1))
   vol=canonical(shifted).val().intersect(usb.val()).Volume()
   checks.append(dict(pair=k+'/USB_'+str(i),travel=t,volume_mm3=round(vol,6),pass_check=vol<.001))
 for direction,t in [('outward_capture',-.6),('inward_stop',.7)]:
  vol=objects[k].translate((0,t,0)).val().intersect(main.val()).Volume()
  checks.append(dict(pair=k+'/'+direction,travel=t,contact_volume_mm3=round(vol,6),pass_check=vol>.01))
 # Verify the actual assembly path from the rear, with the cover removed.
 for dz in [0,.5,1,2,4,6,8]:
  vol=objects[k].translate((0,0,dz)).val().intersect(main.val()).Volume()
  checks.append(dict(pair=k+'/rear_loading_path',z_offset=dz,volume_mm3=round(vol,6),pass_check=vol<.001))
 vol=objects[k].translate((0,0,.7)).val().intersect(rear.val()).Volume()
 checks.append(dict(pair=k+'/cover_vertical_capture',z_offset=.7,contact_volume_mm3=round(vol,6),pass_check=vol>.01))

for k in ['D_daisy_petals','D2_daisy_center','D3_stem_leaves']:
 shutil.copy2(REF/'print'/(k+'.stl'),R/'print'/(k+'.stl'))
 o=cq.importers.importStep(str(REF/'cad'/(k+'.step'))).translate((0,0,T-12.0))
 cq.exporters.export(o,str(R/'cad'/(k+'.step')))
 c={'D_daisy_petals':'#fffdf4','D2_daisy_center':'#f0cb3a','D3_stem_leaves':'#202022'}[k]
 assy.add(o,name=k,color=cq.Color(c));v,f=o.val().tessellate(.12,.25)
 mesh.append(dict(key=k,color=c,group='decoration',explode=0,v=[[a.x,a.y,a.z] for a in v],f=[list(q) for q in f]))
# Audit every printable pair, including the body/cover fit, not only electronics.
import itertools
all_real={k:canonical(v) for k,v in objects.items() if not k.startswith('T_')}
for k in ['D_daisy_petals','D2_daisy_center','D3_stem_leaves']:
 all_real[k]=cq.importers.importStep(str(R/'cad'/(k+'.step')))
for a,b in itertools.combinations(all_real,2):
 vol=all_real[a].val().intersect(all_real[b].val()).Volume()
 checks.append(dict(pair=a+'/'+b,volume_mm3=round(vol,6),pass_check=vol<.01))
report=dict(revision='V12.1',body_mm=[W,H,T],usb_local_depth_mm=T+P['usb_rear_rim_extra'],battery_spacer_height=P['battery_spacer_height'],
 production_parts=8,fit_confirmed=False,button_mechanics_physical_tested=False,
 checks=checks,all_pass=all(q['pass_check'] for q in checks))
(R/'checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
assert report['all_pass'],'Resolve geometry collisions before handing off'
(R/'mesh-data.json').write_text(json.dumps(mesh,separators=(',',':')))
assy.export(str(R/'cad/NianNian_V12_assembly.step'))
print('V12 export complete',flush=True)
