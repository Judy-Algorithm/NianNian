from pathlib import Path
import json, shutil, zipfile
R=Path(__file__).resolve().parent
REF=R/'reference/v10'
# Geometry-only 3MF: keep the actual printer/material settings in Bambu Studio.
ctx={'__file__':str(R/'package.py')}
exec((REF/'package.py').read_text().split("plate('00_")[0],ctx)
for filename,parts in [
 ('00_整板定位与按键帽试装.3mf',['T_full_board_frame.stl','T_full_board_cover.stl','K_BOOT_cap.stl','K_RST_cap.stl']),
 ('01_整体双仓前壳_蓝色.3mf',['A_main_two_bay.stl']),
 ('02_可拆后盖_蓝色.3mf',['C_rear_cover.stl']),
 ('03_两个按键帽与电池垫片_蓝色.3mf',['K_BOOT_cap.stl','K_RST_cap.stl','E_battery_spacer.stl']),
 ('04_花瓣_白色.3mf',['D_daisy_petals.stl']),
 ('05_花心_黄色.3mf',['D2_daisy_center.stl']),
 ('06_花柄叶片_黑色.3mf',['D3_stem_leaves.stl']),
 ('07_剩余蓝色三件合打一盘_V11p1.3mf',['A_main_two_bay.stl','C_rear_cover.stl','E_battery_spacer.stl'])]:ctx['plate'](filename,parts)
print('Packaged 8 geometry plates')
