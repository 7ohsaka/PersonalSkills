# `nsfc-grant-craft` — 国家自然科学基金（NSFC）申报专属 Agent Skill

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](./CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-orange.svg)](https://agentskills.io)

遵循 [Agent Skills](https://agentskills.io) 渐进式披露规范构建的中国国家自然科学基金（NSFC）申报辅助技能，面向**青年科学基金（青C）、面上项目、重点项目与联合基金**，深度融合 **2026+“瘦身提质”新政**、**像素级写作方法论**、**西南交通大学填报与校级评审实战经验**，并针对**催化 / 燃烧 / 气-固反应动力学 / 原位诊断 / 多尺度建模**等交叉方向提供专属范式与可执行自动化工具链。

---

## 核心特性

1. **全流程渐进式知识库（`references/`）**
   - **政策与实务红线**：2026+ 正文 ≤ 30 页与三大块结构、代表作个人贡献与署名规范、AI 使用合规声明、限项（高职 2 项 / 非高职 1+2）、新版三科目直接经费预算（设备费 / 业务费 / 劳务费）、简历时间轴与附件避坑。
   - **像素级写作手册**：灵魂三问（What–So What–How）、25 字题目公式、400 字中英摘要闭环、立项依据漏斗推进、破解“综而不述”与“a+b 拼盘创新”、四类科学问题属性、五维可行性、**“特色讲不同，创新讲高明”**、研究基础“防过度完成”控制。
   - **专属学科高分写作 DNA**：实验原位探测（如 SVUV-PIMS/光谱/JSR/PBR）+ 量子化学/DFT + 气-固耦合微动力学建模（MKM/Cantera/Chemkin-Pro）四阶闭环范式与变量解耦模板。
   - **100 分制双同行模拟函评 & 提交前终审**：40/30/20/10 评分权重、小同行深度与大同行可读性双视角、逐段润色与禁词黑名单、七大维度形式与逻辑一致性核查。

2. **双轨原生可编辑技术路线图（PPT + Draw.io）**
   - 共用同一份 JSON 配置（[assets/roadmap-template.json](./assets/roadmap-template.json)），一键同步生成：
     - **原生可编辑 PowerPoint (`.pptx`)**：每个色块、卡片、编号章、箭头均为 PPT 原生形状，方便在 PowerPoint / WPS 中自由排版与叠加实验/机理图；
     - **未压缩可编辑 Draw.io (`.drawio`)**：精确正交布线，自动通过 XML 结构校验与导出防泄密检测。

3. **多源学术文献检索（覆盖闭源摘要/关键词 + Google Scholar 入口）**
   - 支持 **OpenAlex / Crossref / Semantic Scholar API** 批量检索（闭源付费期刊亦可拿到标题、全作者、DOI、引用数、关键词与摘要）；
   - 集成 **Google Scholar 合规协同工作流**（自动生成直达检索链接 + 支持 Google Scholar 导出 `.bib` 与 DOI 列表零依赖转为**全作者标准 NSFC 编号参考文献**）。

4. **自动化草稿体检脚本（`audit_proposal.py`）**
   - 自动检测摘要是否超 400 字、题目字数与工程化词风险、高风险禁词精确定位（含行号与上下文）、图注编号连续与漏引、正文 `[n]` 与参考文献列表 100% 双向对齐。

---

## 目录结构

```text
nsfc-grant-craft/
├── SKILL.md                                 # 技能主入口与任务路由
├── README.md                                # 仓库说明
├── CHANGELOG.md                             # 版本迭代记录
├── LICENSE                                  # MIT 许可证
├── install-global.ps1                       # Windows 一键全局安装脚本（支持多 Agent）
├── references/                              # 6 份按需加载参考手册
│   ├── 01-policy-and-swjtu-rules.md
│   ├── 02-writing-playbook.md
│   ├── 03-domain-exemplars-dna.md
│   ├── 04-review-and-polish-rubric.md
│   ├── 05-pre-submission-checklist.md
│   └── 06-figure-and-literature-guide.md
├── scripts/                                 # 6 个可直接运行的 Python 自动化脚本
│   ├── audit_proposal.py                    # 申请书草稿自动化体检
│   ├── generate_roadmap_pptx.py             # 同源生成可编辑 PPT (+可选同步 Draw.io)
│   ├── generate_roadmap.py                  # 生成可编辑 Draw.io 路线图
│   ├── validate_drawio.py                   # Draw.io XML 结构校验
│   ├── check_export_metadata.py             # SVG/PNG 导出防泄密检测
│   ├── search_literature.py                 # 多源文献检索 + Google Scholar 入口
│   └── generate_references.py               # DOI / Google Scholar BibTeX → 全作者 NSFC 引用
└── assets/                                  # 写作与绘图脚手架
    ├── proposal-outline-2026.md             # 2026+“瘦身提质”版提纲脚手架
    └── roadmap-template.json                # 多尺度反应机理三阶段路线图模板
```

---

## 快速安装与使用

### 1. 全局安装（支持 Antigravity / Claude Code / Codex / 通用 `.agents`）

在 Windows PowerShell 中运行：

```powershell
.\install-global.ps1
```

或在任意 Agent 支持的全局技能目录下直接克隆本仓库，例如：

```bash
git clone <your-repo-url> ~/.gemini/config/skills/nsfc-grant-craft
```

### 2. 常用脚本示例

依赖：Python 3.10+；仅生成 `.pptx` 需要 `python-pptx`（`pip install python-pptx`），其余脚本均纯标准库零依赖。

```bash
# 1) 申请书草稿自动化体检
python scripts/audit_proposal.py draft.md --type general

# 2) 多源检索文献（含闭源文献摘要/关键词 + Google Scholar 直达链接）
python scripts/search_literature.py "oxidative coupling methane N2O" --limit 15 --year-from 2021 --compact --show-abstract --gscholar-links

# 3) 从 DOI 列表或 Google Scholar 导出的 .bib 生成全作者 NSFC 参考文献
python scripts/generate_references.py dois.txt --format nsfc --output refs.txt
python scripts/generate_references.py scholar_export.bib --format nsfc --output refs.txt

# 4) 同源 JSON 一键双轨生成可编辑 PowerPoint (.pptx) + Draw.io (.drawio) 技术路线图
python scripts/generate_roadmap_pptx.py --config assets/roadmap-template.json --output roadmap.pptx --also-drawio roadmap.drawio
```

---

## 免责声明与科研诚信

- 本工具仅用于科研逻辑梳理、结构诊断、规范核查与图示/文献效率辅助，**不替代申请人的学术判断，亦不保证项目获批**。
- 政策、限项、资助强度与模板提纲以申报年度国家自然科学基金委员会官方《项目指南》及系统提示为准。
- 严格遵守科研诚信与生成式 AI 使用规定：所有数据、机理与文献必须人工逐条核实，严禁使用 AI 直接生成或虚构申报材料。
