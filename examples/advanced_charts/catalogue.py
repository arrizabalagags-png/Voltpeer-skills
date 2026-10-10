# -*- coding: utf-8 -*-
"""Original chart examples; references describe methods, never demo measurements."""

REFERENCES = {
 'flow': ('ggalluvial: Layered Grammar for Alluvial Plots', '10.21105/joss.02017', '2020', 'https://joss.theoj.org/papers/10.21105/joss.02017', 'Figure 1; categorical flows'),
 'chord': ('Circos: An information aesthetic for comparative genomics', '10.1101/gr.092759.109', '2009', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC2752132/', 'Figures 1–3; circular ribbons'),
 'network': ('Cytoscape: A Software Environment for Integrated Models of Biomolecular Interaction Networks', '10.1101/gr.1239303', '2003', 'https://genome.cshlp.org/content/13/11/2498', 'Figures 2–4; attributed interaction networks'),
 'upset': ('UpSet: Visualization of Intersecting Sets', '10.1109/TVCG.2014.2346248', '2014', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4720993/', 'Figures 1, 4; intersections and set sizes'),
 'venn': ('Intervene: a tool for intersection and visualization of multiple gene or genomic region sets', '10.1186/s12859-017-1708-7', '2017', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5452382/', 'Figure 2a; three-set Venn example'),
 'volcano': ('VolcaNoseR is a web app for creating, exploring, labeling and sharing volcano plots', '10.1186/s12859-020-03843-8', '2020', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC7689420/', 'Figure 1; fold change versus significance'),
 'ma': ('Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2', '10.1186/s13059-014-0550-8', '2014', 'https://link.springer.com/article/10.1186/s13059-014-0550-8', 'Figure 2; abundance versus fold change; no DESeq2 claim for this fixture'),
 'enrichment': ('clusterProfiler 4.0: A universal enrichment tool for interpreting omics data', '10.1016/j.xinn.2021.100141', '2021', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC8454663/', 'Figures 4 and 5a; enrichment encodings, with an original single-list dot layout here'),
 'heatmap': ('Complex heatmaps reveal patterns and correlations in multidimensional genomic data', '10.1093/bioinformatics/btw313', '2016', 'https://academic.oup.com/bioinformatics/article/32/18/2847/1743594', 'Figure 1; dendrograms and annotations'),
 'gsea': ('Gene set enrichment analysis: A knowledge-based approach for interpreting genome-wide expression profiles', '10.1073/pnas.0506580102', '2005', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC1239896/', 'Figure 1 and enrichment score definition'),
 'violin': ('Violin Plots: A Box Plot-Density Trace Synergism', '10.1080/00031305.1998.10480559', '1998', 'https://www.tandfonline.com/doi/abs/10.1080/00031305.1998.10480559', 'Density trace and box summary method; conceptual reference'),
 'tsne': ('Visualizing Data using t-SNE', '', '2008', 'https://jmlr.org/papers/v9/vandermaaten08a.html', 'Figures 4–6; local-neighbourhood embeddings'),
 'pca': ('Principal component analysis: a review and recent developments', '10.1098/rsta.2015.0202', '2016', 'https://doi.org/10.1098/rsta.2015.0202', 'Principal components and variance explained; conceptual reference'),
 'roc': ('The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets', '10.1371/journal.pone.0118432', '2015', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC4349800/', 'Figures 1, 3, 5; ROC, PR and confusion definitions'),
 'confusion': ('Pneumonia detection in chest X-ray images using an ensemble of deep learning models', '10.1371/journal.pone.0256630', '2021', 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0256630', 'Figures 7–9; confusion matrices and ROC; no patient data reused'),
 'calibration': ('On Calibration of Modern Neural Networks', '', '2017', 'https://proceedings.mlr.press/v70/guo17a.html', 'Figure 1; reliability diagrams and section 2 ECE'),
 'forest': ('Forest plots: trying to see the wood and the trees', '10.1136/bmj.322.7300.1479', '2001', 'https://www.bmj.com/content/322/7300/1479', 'Effect estimates, confidence intervals and pooled diamond'),
 'attention': ('Attention Is All You Need', '', '2017', 'https://papers.nips.cc/paper/7181-attention-is-all-you-need', 'Section 3.2.1 and appendix attention visualizations; matrix is our own encoding'),
 'pareto': ('EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks', '', '2019', 'https://proceedings.mlr.press/v97/tan19a.html', 'Figures 1 and 5; accuracy versus resource cost'),
}

# kind, Chinese name, English name, group, plain use, required input, limit, files, reference
ROWS = [
 ('sankey','桑基图','Sankey diagram','relations','看对象在几个阶段之间如何分流。','来源、去向、数量；中间节点要能核对进出量。','演示是计数流；基因与通路的多重归属应写成关系数，不能当成物质守恒。',['flows.csv'],'flow'),
 ('chord','弦图','Chord diagram','relations','看几个类别之间的连接规模。','类别之间的非负权重矩阵或边表。','本例为无向网络；扇区和带宽都按连接权重计算，颜色不表示方向。',['chord.csv'],'chord'),
 ('network','关系网络图','Network graph','relations','看连接、分组和关键节点。','节点、分组、位置与带权连接表。','节点是虚构对象；没有真实蛋白互作，也不代表因果关系。',['nodes.csv','edges.csv'],'network'),
 ('upset','UpSet 交集图','UpSet intersections','relations','看多个名单各自有多少、重叠多少。','每个对象是否属于各名单的 0/1 表。','所有非空交集都保留；点阵表示确切交集，不是累加交集。',['sets.csv'],'upset'),
 ('venn','三集合韦恩图','Three-set Venn','relations','看三个名单的共有与独有对象。','三列集合归属，或七个互斥区域的计数。','圆形为示意，面积不按数量缩放；数量由随包的集合归属表实际计算。',['sets.csv'],'venn'),
 ('volcano','火山图','Volcano plot','omics','同时看差异大小和统计显著性。','两组逐样本数值，或效应量与调整后的 p 值。','演示使用连续 log2 数值的 Welch 检验和 BH 校正；不是 RNA-seq 的 DESeq2 分析。',['expression.csv'],'volcano'),
 ('ma','MA 图','MA plot','omics','看差异是否随平均丰度变化。','每个对象的平均丰度、组间差异和统计结果。','本例横轴是平均 log2 丰度；没有拟合 RNA-seq 离散度或做收缩估计。',['expression.csv'],'ma'),
 ('enrichment','富集气泡图','Enrichment dot plot','omics','看哪些集合包含较多候选对象。','背景全集、候选名单、集合成员关系。','超几何右尾检验与 BH 校正；集合是虚构的，不是已验证 GO 或 KEGG 通路。',['universe.csv','memberships.csv'],'enrichment'),
 ('heatmap','聚类热图','Clustered heatmap','omics','看样本和特征是否呈现共同模式。','数值矩阵、样本分组和标准化规则。','逐行 z-score；平均连接、欧氏距离。树由演示矩阵实际计算，不是装饰。',['heatmap.csv','sample_groups.csv'],'heatmap'),
 ('gsea','GSEA 富集曲线','GSEA running score','omics','看某个集合的成员集中在排名的哪一端。','完整排序及排序分数、集合成员。','只计算权重指数为 1 的原始 ES；没有置换，不能给出 NES、p 值或 FDR。',['ranked.csv','memberships.csv','universe.csv'],'gsea'),
 ('violin','小提琴与原始点','Violin with observations','distribution','看每组数值的分布、离散和中位数。','每一条观测的分组与数值。','每组 60 个合成观测；Scott KDE、中位数及四分位数，不代表实验重复。',['observations.csv'],'violin'),
 ('tsne','t-SNE 降维图','t-SNE embedding','distribution','把高维数据投到平面上，观察局部相似性。','对象 × 特征矩阵、分组和算法参数。','实际运行 t-SNE；组间距离、团块大小和方向不能直接解释为生物学差异。',['features.csv'],'tsne'),
 ('pca','PCA 得分图','PCA score plot','distribution','看主要变化方向，以及样本的大致分布。','对象 × 特征矩阵及标准化规则。','实际标准化后拟合 PCA；坐标标出解释方差，不用手画的点冒充降维结果。',['features.csv'],'pca'),
 ('roc','ROC 曲线','ROC curve','models','看不同阈值下检出与误报的关系。','每个对象的真实标签和预测分数。','600 个合成对象，阳性 20%；AUC 来自同一 CSV，不是模型实测成绩。',['predictions.csv'],'roc'),
 ('pr','Precision–Recall 曲线','Precision–recall curve','models','看少数类的检出率与预测准确程度。','真实标签、预测分数及阳性比例。','报告 Average Precision，不把它写成梯形 PR-AUC；虚线为阳性比例。',['predictions.csv'],'roc'),
 ('confusion','混淆矩阵','Confusion matrix','models','看预测错在了哪些类别。','真实标签、预测分数或标签、阈值。','模型 A，阈值 0.5；显示原始计数，颜色显示行内比例，分母明确。',['predictions.csv'],'confusion'),
 ('calibration','可靠性校准图','Reliability diagram','models','看预测的把握程度与实际正确率是否一致。','真实标签、预测类别和置信度。','等宽置信度分箱、按对象数加权的 ECE；空箱不画成零准确率。',['predictions.csv'],'calibration'),
 ('forest','森林图','Forest plot','distribution','比较效应量与区间，查看汇总结果。','每项效应的 log 比值和标准误。','虚构估计量，正态 95% CI，固定效应逆方差汇总；不是临床结论。',['effects.csv'],'forest'),
 ('attention','注意力权重热图','Attention weights','models','看一个位置如何分配对其他位置的权重。','查询、键矩阵，或经过说明的权重矩阵。','从合成 Q、K 实际计算 softmax(QKᵀ/√d)，因果遮罩；不是训练模型的可解释性结论。',['queries.csv','keys.csv'],'attention'),
 ('pareto','性能与成本图','Performance–cost frontier','models','看性能提升需要付出多少资源。','相同条件下的成本、指标和逐次结果。','5 个演示种子；均值 ± 1 SD，前沿按均值计算。毫秒值没有对应硬件测量。',['benchmarks.csv'],'pareto'),
]

def records():
    out=[]
    for kind,title,en,group,use,needs,limit,files,ref in ROWS:
        t,doi,year,url,loc=REFERENCES[ref]
        out.append(dict(id='advanced-'+kind,kind=kind,version='1.0.2',title=title,title_en=en,group=group,use=use,needs=needs,limit=limit,files=files,reference=dict(title=t,doi=doi,year=year,url=url,locator=loc),data_scope='synthetic mathematical demonstration',author='VoltPeer'))
    return out
