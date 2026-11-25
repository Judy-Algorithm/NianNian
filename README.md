# 念念 · V12.1 复核修正版

**旧 V12 先不要打印。复核发现中间隔挡与后盖定位边有硬干涉，V12.1 已修正隔挡两端避让。**

[下载修正后的一盘打印工程](https://raw.githubusercontent.com/Judy-Algorithm/NianNian/main/printing/v12_1/project/打开这个_V12p1_复核修正版_PETG.3mf)

已预设 X1 Carbon、0.4 mm 喷嘴、纹理 PEI、Generic PETG；五个蓝色件同盘，后盖带支撑，小帽子带附着边。重新导入并切片验证通过，约 55 分钟、21 g。

[完整打印包](https://raw.githubusercontent.com/Judy-Algorithm/NianNian/main/downloads/NianNian_V12p1_printing.zip) · [完整 CAD 与源文件](https://raw.githubusercontent.com/Judy-Algorithm/NianNian/main/downloads/NianNian_V12p1_CAD.zip) · [装配说明](printing/v12_1/README.md) · [复核报告](printing/v12_1/validation/summary.json)

## 这次实际检查了什么

- 找出旧 V12 前后壳约 0.896 mm³ 的硬干涉，修正后全部 28 组打印件配合检查通过。
- 复核主板从后方放入的路径、12×6 mm 参考线头插入空间、按键帽装入及止挡。
- 重新切片并核对五件的首层路径、后盖支撑、两颗帽子的附着边，以及平台禁入区域。
- 网格检查通过。主体仍为 11.4 mm，USB 下沿局部 12 mm，电池垫片为 2.8 mm。

**这不等于已实物打印或装配成功。** 真实线头宽厚、电池整包及出线空间尚未测量；主板区名义最小后方余量只有约 0.3 mm。PETG 首层附着、实际收缩、合盖、按键触发与回弹仍需实物确认，不能承诺一次打印就免修整装好。

花件、后盖、帽子、垫片形状未因这次隔挡避让修改而改变；若已打印旧 V12，只需更换前壳，不必把其余件全部重打。

[旧 V12 存档](printing/v12/)仅用于追溯。
