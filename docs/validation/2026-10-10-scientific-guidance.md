# Skills 最终审核 — 2026-10-10

结论：`scientific-guidance-v1.2.2` 独立 Beta 修订已生成并冻结。主版本仍为 0.12.0，16 个 Skill。当前 private/public Skills 所有文件字节一致；本次检查的 3312 个历史 ZIP 的 SHA-256 未改变，30 个归档内 CSV 成员逐字节保留。

## 本轮实际修复

- `voltpeer-assemble` 明确继承 `voltpeer-plot`：逐圈容量、CE、保持率和倍率只画点，不连线；连续电压、EIS、光谱使用无点实线。
- 修复 atlas、grammar 与拼版内镜像引用，补全全电池同圈 CE、参考圈/参考容量与一致条件；保留 Li‖Cu 与 Aurbach 区分。
- 新包同时纳入此前已完成但旧 ZIP 未含的拼版对齐代码，并补入被新版 CLI 调用、此前遗漏的 `svg_export.py` 模块。
- 下载和公开说明切换到独立的新修订。Starter 仍只含一个绘图技能；单独数据导入不含绘图器。明确 Python ≥3.10、网络安装依赖和宿主实际发现步骤。
- 科学约定只作用于本项目新生成图。作者上传或文献原图保留原有编码，不冒充期刊通用规定。

## 真实局部验证

- 35 个归档结构、字节/SHA、canonical Skill 全成员、WorkBuddy 适配和集合内嵌 ZIP 一致性通过。
- 新 Starter 解压后用实际 `start.py demo` 执行成功。
- 新解压绘图代码重画合成异常 CE：100.5% 与 101.125% 等原值完整保留，空心点，无连线；全电池同圈 CE 与参考保持率通过，缺 CE、错误参考容量、跨工况计算均停止。
- 六种不同长宽比的 PNG×2/PDF×2/SVG×2 在新解压拼版程序实际组合。9 个真实坐标区边缘比较通过；人为错位被 strict 模式阻止。源图字节不变、无裁剪、同比缩放、PDF 180×214 mm、300 dpi PNG 和可编辑配对 SVG 通过。已看实际 PNG，坐标、文字、几何标尺夹具完整。
- 单元回归：绘图 7 项、拼版 13 项通过。修正两个过时编码断言及一个把自身参考圈设为 90% 的不合法合成输入。

验证全部使用合成工程夹具，不代表实验科学结论或任何期刊接受。原生桌面发现到交付、完整 Flash/Pro 行为和 macOS 实机仍为 NOT_RUN。Github 同步与 ECS 部署由主发布流程另行记录。

证据：`skills-review.json`、`skills-runtime-verification.json`。


## 交叉审查补修

入口审查发现新下载索引的 `plot_starter` 字段仍指旧包。已修新索引和生成器，并在两套镜像核对新 Starter URL、实际字节/SHA、注册表、两个当前指针和解压 manifest；35 ZIP 与 Starter 字节均未改变。证据：`2026-10-10-starter-index-followup.json`。
