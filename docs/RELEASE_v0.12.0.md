# VoltPeer v0.12.0 Beta

当前源码与全部技能包包含 **16 个 `voltpeer-*` Skill**。首次绘图推荐 Starter：它只含一个绘图 Skill、固定程序与合成示例。

## 当前下载

2026-10-10 新增独立包修订 **`scientific-guidance-v1.2.2`**。主版本仍为 **0.12.0 Beta**，不是新的完整正式 GitHub Release。旧 `cycling-rule-v1.2.1` 与其他历史 ZIP 保留原名称、原始字节和校验值。

| 包类型 | 内容与入口 |
| --- | --- |
| 绘图 Starter | [一个绘图 Skill、固定 Python 程序及合成 Demo](assets/scientific-guidance-v1.2.2/starter/VoltPeer-Plot-Starter-v0.12.0.zip)；完整解压，先读 `plot_starter/AGENT_GUIDE.md` |
| 全部技能包 | [16 个 Skill 与安装器](downloads/v0.12.0-scientific-guidance-v1.2.2/VoltPeer-v0.12.0.zip)；按任务安装 |
| 单 Skill 包与 WorkBuddy 包 | [包名、字节数与 SHA-256 索引](downloads/v0.12.0-scientific-guidance-v1.2.2/download-index.json)；数据导入要出图还需绘图 Skill |
| 示例源码包 | [多面板示例源码与数据](assets/cycling-rule-v1.2.0/split-demos/integrated_study/integrated_study-source.zip)；供重画和学习，不代替技能安装 |

下载前需要 Python ≥3.10 和安装依赖的网络。Starter 不提供 Python 解释器，`setup` 会准备独立环境。文字流程不用安装绘图库。

推荐 Starter 为 **746,960 bytes**，SHA-256：

```text
d613f5e3780dc7e08faaaef678b23cc15de0d01740717aadac6c5d4a606146d8
```

全部技能包和 35 个分发归档的校验值见[本次索引](downloads/v0.12.0-scientific-guidance-v1.2.2/download-index.json)。Starter 校验值另见[Starter 注册表](assets/scientific-guidance-v1.2.2/starter/plot-starter.json)。校验记录置于被校验 ZIP 外，避免自引用。

## 本次修订

- 绘图与拼版及其引用说明统一：新生成的逐圈容量、库伦效率、保持率、倍率数据使用散点且不连线；连续电压、谱线、EIS 使用无点实线。
- 全电池使用同圈容量与 CE，保持率说明参考圈、参考容量与条件；缺少真实数据先补材料。Li‖Cu 不强加保持率，Aurbach 按独立测试协议处理。
- 拼版包纳入现有的真实坐标区对齐与保留源图比例的代码修订。
- 作者提供或文献原图保留原有编码；项目绘图约定不冒充所有期刊的通用规定。原始 Demo CSV 不改，异常值不截断或美化。
- 普通包、WorkBuddy 包、全部技能包与 Starter 使用同一套当前科学指导源；不同宿主的 frontmatter 适配分别保留。

## 状态与验证范围

当前下载身份、源码、GitHub 同步和 ECS 网站部署是分别记录的事件。[RELEASE_STATUS.json](RELEASE_STATUS.json) 标明本次本地修订；索引内的发布状态是打包快照，不证明已经部署到 ECS。

本次固定程序本地验证检查异常 CE 原值与逐圈点编码，并检查混合 PNG/PDF/SVG 拼版。脚本运行或 ZIP 结构通过，不能证明客户端已发现技能或模型行为已全面通过。当前原生桌面技能发现到交付、Flash/Pro 完整 69 项行为和 macOS 实机验证仍为 **NOT_RUN**。旧 0.10.1 与有限 API pilot 保留各自版本和范围。见[软件适配](COMPATIBILITY.md)。

GitHub 最近完整正式 Release 仍为 [v0.9.2](https://github.com/arrizabalagags-png/Voltpeer-skills/releases/tag/v0.9.2)。社区后台需单独安装，不会随静态网站 ZIP 自动运行。网站的配色、机理 SVG、教学示例和文献参考按各资源许可使用；示例条件不能补入自己的实验。

## 历史版本

[前一修订 0.12.0 Beta 全部技能包](downloads/v0.12.0-cycling-rule-v1.2.1/VoltPeer-v0.12.0.zip) · [前一 Starter](assets/cycling-rule-v1.2.1/starter/VoltPeer-Plot-Starter-v0.12.0.zip)

[0.11.0 版本说明](RELEASE_v0.11.0.md) · [0.11.0 绘图 Starter](downloads/v0.11.0/starter/VoltPeer-Plot-Starter-v0.11.0.zip) · [0.11.0 全部 15 个技能包](downloads/v0.11.0/VoltPeer-v0.11.0.zip)

[0.10.1 固定 Starter](https://github.com/arrizabalagags-png/Voltpeer-skills/raw/dfd46fcb4a3255b60826de8a4c721963adc4ff02/docs/downloads/starter/VoltPeer-Plot-Starter-v0.10.1.zip) · [0.10.1 版本说明](RELEASE_v0.10.1.md) · [0.9.2 正式发布](https://github.com/arrizabalagags-png/Voltpeer-skills/releases/tag/v0.9.2)

## English

The current source remains **0.12.0 Beta with 16 Skills**. This independent `scientific-guidance-v1.2.2` revision synchronizes plotting and assembly guidance, includes existing assembly alignment fixes, and preserves all original demo CSV and historical ZIP bytes. Starter contains one plotting Skill. The full package and individual archives are separate downloads; data preparation alone does not install the renderer.

Per-cycle quantities use unconnected markers; continuous signals use solid marker-free curves. This project convention does not rewrite published source figures or claim to be a universal journal requirement. Full-cell CE and retention need same-cycle data and an explicit reference basis. Native desktop discovery-to-delivery, full model behavior and macOS device validation remain **NOT_RUN**. Local fixed-program checks do not certify them. GitHub synchronization and ECS deployment are separate events; the latest full stable Release remains v0.9.2.
