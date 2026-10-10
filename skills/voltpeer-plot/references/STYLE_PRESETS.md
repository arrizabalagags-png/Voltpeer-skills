# 选一套图的颜色风格

![Six original style previews made with invented values](../assets/style-preview.svg)

这张预览只用**虚构数值**展示线条、图例和配色，不是电池实验结果。具体颜色在 [figure_theme.json](../assets/figure_theme.json)，每套都有适合折线的深色序列和完整色卡。浅粉、浅蓝、浅黄主要作区域底色；细折线和小字要用对比度更高的颜色。

还可以看[同一份全电池演示 CSV 的六套实际画法](https://github.com/arrizabalagags-png/Voltpeer-skills/blob/79b4238a5a7dfc963bafc0aefacd2337f9795ba8/examples/showcase/style_presets/figure.svg)：六格共用数据、单位和坐标范围，只改变颜色及 A/B 线型。每格还有独立 SVG/PDF/PNG 可下载；先看整体，再按用途选一套。旧预览继续保留作快速色卡。

| 选择时说这个名字 | 适合的图 | 代码值 |
| --- | --- | --- |
| 深海蓝绿 | 通用电池综述、复杂多面板；默认库风格 | `forge` |
| 玫蓝渐层 | 两类电解液/策略对照、热图和层次较多的图 | `rose_blue` |
| 珊瑚冰蓝 | 温和的暖冷对照；背景大面积留白 | `peach_ice` |
| 暖冷对照 | 强调两组差异、温度或失效过程 | `thermal_balance` |
| 期刊极简 | 投稿尺寸较小、需要少色且信息密集的面板 | `journal_minimal` |
| 清晰对比 | 多条曲线、柱图、需要明显区分类别的图 | `crisp_contrast` |

**小白先三选一：**“你喜欢清爽期刊风、柔和综述风，还是高对比展示风？不确定我可以推荐。”默认对应 `journal_minimal`、`peach_ice`、`crisp_contrast`。其余三套在“更多风格”里展示，不要一次抛出六个术语。若作者已给色号或选过项目风格，就沿用并把选择写到图的配置和来源记录。若作者授权“你来选”，按读者要区分的类别、彩色/灰度使用场景和投稿尺寸决定，并说明选择。颜色只表达预先声明的语义；同一个样品在各面板保持同色，另用线型/符号辅助区分。任何配色都不能替代图例、数据来源或测试条件。

截图中的三组配色在本库里分别是 `rose_blue`、`peach_ice` 和 `thermal_balance`。截图的浅色被保留为色卡/背景；定量线条采用对比更强的同色系颜色，以免缩到论文栏宽后消失。`journal_minimal` 和 `crisp_contrast` 则提供两种不同的论文量化图取向。预设不是任何期刊的官方规范；最终尺寸、字体和文件格式应以目标期刊当期要求及实际印样为准。

列出风格，再把 `style` 写进上传数据的映射 JSON：

```bash
python scripts/plot_uploaded.py styles
```

```json
{"kind": "coulombic_efficiency", "style": "rose_blue", "claim": "..."}
```

原创 SVG 示意图库也可按同一风格重配色：

```bash
python scripts/render_template.py --list
python scripts/render_template.py \
  --template battery-lab-primitives --style rose_blue --out figures/lab.svg
```

重配色只处理本库原创 SVG 的颜色，不会碰作者的原始显微图、已发表图片或实验数值。`scripts/preview_styles.py --out path/style-preview` 可重新生成预览。

## 文献配色与完整 Figure 示例

网站上的文献配色附 `palette.json` 和 `palette.lock.json`。作者已经选定时，保留 `community:<id>@<version>`，不要再问一遍风格，也不要自动下载其他版本。先核对本地锁文件的 SHA256、ID、版本和颜色数量，再将真实样品绑定到颜色；原论文样品名不自动套用到作者数据。

```bash
python scripts/plot_uploaded.py inspect --data path/to/author.csv
python scripts/plot_uploaded.py plot \
  --data path/to/author.csv --metadata path/to/mapping.json \
  --out path/to/new-output
```

在已经核对的映射 JSON 中写入 `style: "community:<id>@<version>"` 与 `community_style_lock: "palette.lock.json"`。锁文件的相对路径以映射 JSON 所在目录为基准。实际参数与输入契约以 `plot_uploaded.py --help` 及 [上传数据说明](UPLOADED_DATA.md) 为准。配色锁只改变样式，不会让缺单位或条件的数据自动合格。样品多于颜色时不能循环复用；先换够用的配色或确认分图方案。

仓库根目录 `examples/paper_figures/` 提供循环、溶剂化方法与原位结构三套解析模型。先重画包内 CSV，再为作者文件建立真实映射。谱峰、RDF 和晶格公式只用于说明图件关系；不能替换为任意 Excel 后宣称识别成功。容量、CE、保持率及倍率测试逐圈用点；连续电压、阻抗和光谱用无点实线；全电池保持率写明参考圈和容量，图轴保留四边框。

文献原色与白底细线用色分开记录；原色、调整理由、DOI 和图号一同保留。网页深浅主题不会改变白底论文图或 CSV。文献配色不是期刊官方规范，也未做色觉认证。

## English

Choose a named preset once per manuscript figure set. Record its code in plotting metadata; the CLI refuses to draw a final chart without that choice. The three warm/cool palettes preserve the user's supplied swatch families, while plotted lines use darker members for final-size contrast. Schematic recoloring applies only to this project's original editable SVGs.
