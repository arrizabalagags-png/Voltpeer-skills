# 20 种文献图型的原创演示 / 20 original reference charts

参考生信、统计和计算机论文里的图型与表达方法。所有 CSV 都是明确标注的合成输入；不包含论文原图、论文实验数据或用户实验文件。图型来源与具体方法见 `catalogue.py`，每次绘图会输出计算结果和输入 SHA256。

## 重画一张图

将网页下载的源码包和 CSV 包解压到同一个**新文件夹**，保留 `inputs/` 目录。先创建项目 Python 环境，再安装依赖：

```sh
python -m pip install -r requirements.txt
python render.py --kind sankey --inputs inputs --output results-01
```

把 `sankey` 换成下表的图型编号。已有图件不会被覆盖。程序只读取 CSV；重画时不会重新生成示例数据，也不会访问网络。替换成自己的数据之前，先核对字段、单位、分组、统计方法和参数。当前源码是演示的重画入口，不代表已经完成任意真实数据的自动分析。

| 图型编号 | 图型 | 主要用途 |
|---|---|---|
| sankey | 桑基图 | 阶段之间的分流 |
| chord | 弦图 | 类别之间的连接规模 |
| network | 关系网络 | 节点、连接和分组 |
| upset | UpSet | 多个集合的确切交集 |
| venn | 三集合韦恩图 | 三个集合的共有与独有对象 |
| volcano | 火山图 | 差异大小与显著性 |
| ma | MA 图 | 丰度与组间差异 |
| enrichment | 富集气泡图 | 候选对象与背景集合 |
| heatmap | 聚类热图 | 数值模式与层次聚类 |
| gsea | GSEA 富集曲线 | 排名中集合成员的位置 |
| violin | 小提琴与原始点 | 数值分布、中位数与四分位数 |
| tsne | t-SNE | 高维对象的局部相似性 |
| pca | PCA 得分图 | 主要变化方向与解释方差 |
| roc | ROC | 阈值、检出与误报 |
| pr | Precision–Recall | 少数类检出与预测精确率 |
| confusion | 混淆矩阵 | 固定阈值下的分类结果 |
| calibration | 可靠性校准图 | 置信度与实际正确率 |
| forest | 森林图 | 效应量、区间与汇总 |
| attention | 注意力权重热图 | 有因果遮罩的权重矩阵 |
| pareto | 性能与成本图 | 成本与性能之间的取舍 |

## 数据与统计口径

- 每份数据包的 `INPUT_MANIFEST.json` 列出字段、行数、哈希、合成数据身份和必要限制。
- 桑基图为守恒计数流。基因与通路的重复归属应使用“关系数”，不能写成物质守恒。
- 火山图与 MA 使用连续 log2 数值的双侧 Welch 检验与 BH 校正。没有拟合 DESeq2、负二项分布或 RNA-seq 离散度。
- 富集例子的背景、候选和集合成员都保留；使用超几何右尾检验与 BH 校正。集合为虚构，不是真实 GO/KEGG 注释。
- GSEA 只计算 p=1 的原始 ES，没有置换，不给 NES、p 值和 FDR。
- 聚类由数值矩阵实际计算。热图逐行 z-score，使用样本标准差；PCA 和 t-SNE 在相同的标准化矩阵上拟合。t-SNE 的组间距离不作定量解释。
- ROC、PR、混淆矩阵与校准使用同一份 600 对象、20% 阳性的 CSV。PR 标注 AP；混淆矩阵保留计数与行内比例；ECE 按各箱对象数加权。
- 森林图使用虚构的 log 比值与标准误，正态 95% CI，固定效应逆方差汇总。性能成本图为 5 个合成种子的均值 ± 1 个样本 SD，没有实际硬件基准。
- 注意力来自合成 Q/K 的缩放点积、因果遮罩和逐行 softmax，不是训练模型的解释结论。

## 输出与检查

每张图为 180 × 120 mm，导出 300 dpi PNG、PDF 和 SVG，当前最终图中文字不小于 8 pt。SVG 使用文字与矢量图元，热图单元格也可编辑。图型标题和合成数据身份放在网页、说明和清单中，图版保留数据标注。`render-report.json` 记录指标、输入与图件哈希、绘图区位置和运行库版本。该演示尺寸不是期刊投稿保证；投稿前按目标期刊和最终版面检查字号。PNG 用于预览，不承诺满足要求 TIFF 或 600 dpi 的投稿系统。

分开的下载：源码、CSV、PNG/SVG/PDF、提示词。文献来源在网页和包内；学习图型与方法后独立绘制，没有描摹论文的具体构图或移植论文数据。

The fixtures are synthetic and the figures are original. Extract source and data components into a new folder, install requirements in a project environment and run the command above. Replay never creates data or accesses the network. Adapt the input contract and statistical method before using author data. All four classification plots share the same predictions. Cross-platform font/library changes may change file bytes; the input identities and computed meanings remain auditable.

## 许可 / Licences

本目录原创代码、合成输入和原创图件使用 MIT，见 `LICENSE`。`figure_style.py` 来自 figure-style Skill 的 `kernel.py`，其 Apache-2.0 许可与来源见 `LICENSE-Apache-2.0.txt` 和 `NOTICE`。引用论文的许可不转移到本原创演示；下载包不分发论文文本和原图。
