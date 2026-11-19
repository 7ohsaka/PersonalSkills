---
name: nsfc-grant-craft
version: 1.0.0
description: >-
  Comprehensive Chinese National Natural Science Foundation (NSFC / 国家自然科学基金)
  grant proposal assistant tailored for Youth (青C), General (面上), Key (重点), and
  Joint Fund (联合基金) applications, with specialized adaptations for SWJTU
  (西南交通大学) submission practices and multi-scale physical chemistry, catalysis,
  combustion kinetics, in-situ diagnostics, and computational modeling research.
  Supports dual-track PowerPoint (.pptx) & Draw.io (.drawio) editable technical
  roadmaps, multi-source literature search (OpenAlex, Crossref, Semantic Scholar,
  and Google Scholar entry), automated formal auditing, and 100-point mock peer
  review. Use this skill whenever the user asks to plan, draft, refine, polish,
  review, benchmark, budget, check, draw technical roadmaps for, or search/format
  references for an NSFC grant proposal (基金申报书/国自然本子).
---

# NSFC 国家自然科学基金申报专属辅助指南 (`nsfc-grant-craft` v1.0)

本 Skill 融合了 **2026+ 基金委“瘦身提质”新政**、**天津大学钟澄教授“像素级”写作体系**、**西南交通大学校级申报实战经验与填报规范**、**多尺度催化/燃烧/表界面反应机理高分中标范本写作 DNA**，以及**双轨可编辑路线图（PPT + Draw.io）与多源文献检索/自动体检脚本**，覆盖从选题凝练到提交前形式与逻辑双审查的全生命周期。

---

## 核心铁律（执行任何任务前必须遵守）

1. **官方提纲一字不改**：正文必须严格使用当年基金系统下载的最新模板，**绝对禁止修改、删减或自创一级/二级提纲标题**（含“报告正文”字样及括号内提示文字），仅允许在固定提纲下使用三级标题（如 `1.1`、`2.1`）组织内容。
2. **双同行可读原则**：**让小同行感觉深刻**（现状掌握透彻、不漏关键文献、科学问题精准），**让大同行看得明白**（结构清晰、逻辑闭环、语言平实不堆砌晦涩术语）。通讯评审专家平均仅用 **15–20 分钟**审阅一份本子，题目、摘要与第一张概念图决定第一印象。
3. **灵魂三问逻辑闭环**：全书每一段都必须服务于 `What（研究什么/价值） → So What（为什么做/关键科学问题与瓶颈） → How（怎么做/方案可行性） → Why You（为什么你能做成/研究基础）`。
4. **科研诚信与 AI 合规红线**：严禁编造数据、虚构文献或直接套用未经核实的生成文本；任何文献检索结果必须核对真实 DOI/作者/年份；遵守申报年度基金委关于生成式 AI 辅助工具的使用与声明规定；严格区分“辅助撰写/逻辑诊断/润色”与“代写”。
5. **不越界替代学术判断**：所有机理假设、参数范围、前期数据、实验条件及预期指标必须以用户提供的真实科研基础为准；信息不足处以 `【待补充：具体内容】` 明确标出，绝不杜撰实验数据或论文业绩。

---

## 任务路由表（按需按阶段加载参考文档）

根据用户当前需求，先读取对应的 `references/` 模块再开展工作（遵循渐进加载原则，避免一次性读入无关长文）：

| 用户任务 / 阶段 | 必读参考文档 | 配合脚本 / 模板 | 核心交付物 |
| :--- | :--- | :--- | :--- |
| **政策速查、限项、预算、简历与 SWJTU 填报规范** | [01-policy-and-swjtu-rules.md](./references/01-policy-and-swjtu-rules.md) | — | 资格/限项核对、3大科目预算表与测算说明、简历与附件规范 |
| **选题定位、题目打磨、科学问题凝练与属性选择** | [02-writing-playbook.md](./references/02-writing-playbook.md) | [proposal-outline-2026.md](./assets/proposal-outline-2026.md) | 题目候选（≤25字）、科学问题属性论证、关键科学问题（2–3个） |
| **立项依据 / 研究内容 / 目标 / 方案 / 可行性 / 特色创新 / 年度计划撰写或重构** | [02-writing-playbook.md](./references/02-writing-playbook.md) + [03-domain-exemplars-dna.md](./references/03-domain-exemplars-dna.md) | [proposal-outline-2026.md](./assets/proposal-outline-2026.md) | 逻辑框架图 + 对应章节精写稿 + 一致性映射表 |
| **中英文摘要（≤400字）与关键词提炼** | [02-writing-playbook.md](./references/02-writing-playbook.md) | [audit_proposal.py](./scripts/audit_proposal.py) | 精准≤400字中文摘要、地道英文意译摘要、5个递进关键词 |
| **模拟通讯评审（100分制）、对标分析与逐段语言润色** | [04-review-and-polish-rubric.md](./references/04-review-and-polish-rubric.md) + [03-domain-exemplars-dna.md](./references/03-domain-exemplars-dna.md) | [audit_proposal.py](./scripts/audit_proposal.py) | 函评意见报告（40/30/20/10评分+分级修改清单）或逐段润色对照 |
| **提交前全维度形式 + 逻辑一致性终审** | [05-pre-submission-checklist.md](./references/05-pre-submission-checklist.md) + [01-policy-and-swjtu-rules.md](./references/01-policy-and-swjtu-rules.md) | [audit_proposal.py](./scripts/audit_proposal.py) | 自动化脚本审计结果 + 逐项核查报告（未通过/警告/通过） |
| **技术路线图 / 概念图制作（PPT + Draw.io 双轨同步）** | [06-figure-and-literature-guide.md](./references/06-figure-and-literature-guide.md) | [generate_roadmap_pptx.py](./scripts/generate_roadmap_pptx.py), [generate_roadmap.py](./scripts/generate_roadmap.py), [validate_drawio.py](./scripts/validate_drawio.py), [check_export_metadata.py](./scripts/check_export_metadata.py), [roadmap-template.json](./assets/roadmap-template.json) | 同源 JSON 同步生成原生可编辑 `.pptx`（优先便于日常微调）与未压缩 `.drawio` 矢量源图 |
| **多源文献检索（OpenAlex/Crossref/Google Scholar）与引用格式化** | [06-figure-and-literature-guide.md](./references/06-figure-and-literature-guide.md) | [search_literature.py](./scripts/search_literature.py), [generate_references.py](./scripts/generate_references.py) | 真实可溯源文献清单（含闭源文献摘要/关键词）+ 统一全作者 NSFC 编号参考文献 |

---

## 标准端到端工作流

当用户从零构思或整体打磨一份基金申请书时，推荐按以下五阶段推进（也可随时切入任意单点任务）：

```text
阶段 1：定锚（选题 + 题目 + 科学问题 + 科学问题属性 + 申请代码/关键词）
   ↓
阶段 2：立骨（立项依据漏斗逻辑链 + 多源真实文献补全[含Google Scholar入口] + 概念图设计）
   ↓
阶段 3：填肉（研究目标 ↔ 研究内容 ↔ 关键科学问题 ↔ 研究方案 ↔ PPT/Draw.io双轨路线图 ↔ 五维可行性）
   ↓
阶段 4：亮剑（特色与创新分开提炼 + 年度计划与预期成果联动 + 研究基础支撑链 + 3科目预算 + ≤400字中英摘要）
   ↓
阶段 5：验收（逐段润色 → 100分制双同行模拟函评 → audit_proposal.py自动化体检 → 提交前终审清单）
```

---

## 专属学科适配说明（催化 / 燃烧 / 气-固反应动力学 / 多尺度建模）

当申请书属于物理化学、能源动力、催化/燃烧反应机理、原位质谱/光谱诊断、DFT/MD 计算与微动力学建模（MKM）等交叉方向时，务必结合 [03-domain-exemplars-dna.md](./references/03-domain-exemplars-dna.md) 中的高分范式：

- **方法论闭环**：强调用“**原位/在线实验探测（如 SVUV-PIMS/光谱/JSR/PBR）→ 关键活泼中间体/自由基捕获 → 量子化学/第一性原理计算（DFT/CI-NEB/速率理论）→ 气-固耦合微动力学建模（Cantera/Chemkin-Pro/SA/ROP/DRC）→ 模型反向指导实验/调控**”形成闭环，而非“实验+计算两张皮”。
- **变量解耦思维**：面对多因素耦合复杂体系（如温度/压力/多组分/晶面与缺陷/气相与表面耦合），显式设计“单因素解耦 → 多因素耦合 → 动力学定量模型”的递进逻辑。
- **物理量与符号规范**：自由基、中间体、工况参数（温度、压力、停留时间、检测限、力收敛标准、计算精度）表述严谨统一，不写空泛的“开展一系列实验/计算”。

---

## 常用可执行脚本速查

所有脚本位于本技能的 `scripts/` 目录，支持标准 Python 3.10+ 直接运行：

1. **申请书草稿自动化体检（字数 / 摘要 / 禁词 / 图表与参考文献双向对齐）**：
   ```bash
   python scripts/audit_proposal.py path/to/draft.md --type general
   # --type 可选: youth (青C) | general (面上) | key (重点)
   ```
2. **多源学术文献检索（覆盖闭源期刊摘要与关键词 + Google Scholar 直达入口）**：
   ```bash
   # OpenAlex/Crossref/Semantic Scholar 检索（即使闭源期刊也能获取标题、全作者、DOI、关键词与摘要）
   python scripts/search_literature.py "oxidative coupling of methane N2O radical" --limit 15 --year-from 2021 --sort cited_by_count --compact --show-abstract --gscholar-links
   # 切换 Crossref 检索（对 Elsevier/ACS/Wiley/RSC 闭源顶刊与最新在线发表覆盖极强）
   python scripts/search_literature.py "methane oxidative coupling La2O3" --source crossref --limit 10 --compact --show-abstract
   ```
   > **Google Scholar 协同原则**：Agent 在对话中可结合 `search_web`（限定 `scholar.google.com`）与 `--gscholar-links` 检索闭源/中文核心文献的关键词与摘要；用户从 Google Scholar 导出的 BibTeX（`.bib`）可直接喂给下方脚本格式化，严禁对 Google Scholar 实施违规反爬抓取。
3. **DOI 列表或 Google Scholar BibTeX 批量生成全作者标准 NSFC 参考文献**：
   ```bash
   python scripts/generate_references.py dois.txt --format nsfc --output refs.txt
   python scripts/generate_references.py scholar_export.bib --format nsfc --output refs.txt
   # --format 可选: nsfc | bibtex | markdown
   ```
4. **同源 JSON 双轨生成原生可编辑 PowerPoint (`.pptx`) + Draw.io (`.drawio`) 技术路线图**：
   ```bash
   # 一步同步输出 PPT（习惯用 PowerPoint/WPS 自由微调）与 Draw.io（精确矢量布线与校验）
   python scripts/generate_roadmap_pptx.py --config assets/roadmap-template.json --output roadmap.pptx --also-drawio roadmap.drawio
   # 单独生成/校验 Draw.io，并在官方 Draw.io 导出 SVG/PNG 后检查是否意外嵌入编辑源（防泄密）
   python scripts/generate_roadmap.py --config assets/roadmap-template.json --output roadmap.drawio
   python scripts/validate_drawio.py roadmap.drawio
   python scripts/check_export_metadata.py roadmap.svg
   ```

---

## 输出文件命名与验证规范

- 在撰写、模拟评审、润色或终审完成后，若输出独立报告文件，建议按 `<项目简称>-<阶段名>.md` 保存（例如 `N2O-OCM-模拟评审.md`、`N2O-OCM-提交前检查.md`）。
- **交付前自检**：
  - 所有建议均需引用申请书原文具体位置，不作空洞点评；
  - 每次生成或改写摘要，必须实测精确字符数（中文≤400字含标点，英文≤4000字符）；
  - 每次生成路线图时，默认提供 `.pptx` 与 `.drawio` 双轨选项（或按用户偏好生成），对 `.drawio` 必须运行 `validate_drawio.py` 验证通过，并提醒用户在本地 PowerPoint 或 Draw.io Desktop 打开做最终视觉验收。
