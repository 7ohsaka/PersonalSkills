# 双轨技术路线图制作（PPT + Draw.io）与多源文献工作流指南

本指南覆盖 **PowerPoint (`.pptx`) + Draw.io (`.drawio`) 同源双轨可编辑路线图生成**，以及 **OpenAlex + Crossref + Semantic Scholar + Google Scholar 多源文献检索与格式化工作流**。

---

## 一、双轨技术路线图与概念图制作规范（PPT 优先 + Draw.io 同步）

### 1. 工具分工策略
- **PowerPoint（`.pptx`，日常精修主力）**：原生形状与文本框，完全适配个人 PPT 编辑习惯——可直接在 PowerPoint / WPS 中微调字体、拖拽对齐、叠加化学反应式/实验装置照片/分子模型图，再导出高分辨率 PNG（≥300 DPI）或 EMF/SVG 插入 Word 申请书。
- **Draw.io（`.drawio`，矢量布线与版本控制同步）**：未压缩 XML 源图，支持精确正交自动布线与结构自动化验证，极适合纯逻辑流程图与团队 Git 审阅；本地 Draw.io Desktop 可导出无损 SVG/PDF。
- **同源单一真相（Single Source of Truth）**：二者共用同一份 JSON 配置文件（见 [assets/roadmap-template.json](../assets/roadmap-template.json)），改一次内容即可同步生成 `.pptx` 与 `.drawio`。
- 🚫 **不适用场景**：纯实验/仿真曲线数据图仍由 Python/Matplotlib/Origin 绘制。

### 2. 先选逻辑关系，再定版式（一图只表达一个主关系）

| 主要科学逻辑 | 推荐版式 | 禁忌 |
| :--- | :--- | :--- |
| **阶段递进（如：探测 → 计算 → 建模 → 验证）** | 左到右 3–4 栏横向路线，横向主箭头递进，底部向下汇聚至综合目标 | 无先后依赖的内容强行画单向箭头 |
| **并列支撑** | 同宽多栏并列，底部共同指向核心科学目标 | 本质为串行依赖却画成平行无连接 |
| **变量解耦 → 多因素耦合** | 左侧多路单因素解耦分支 → 中间耦合机制模块 → 右侧模型验证与调控 | 把整段正文直接复制进方框 |
| **实验—计算—模型闭环迭代** | 主路径实线清晰，反馈验证使用次要虚线回路 | 正文并无反馈校正却硬画闭环箭头 |
| **年度进度安排** | 甘特图或任务—年份矩阵 | 与机理技术路线图混为一图 |

### 3. 视觉与排版铁律
- **文字极简两级制**：卡片标题用动宾短语（如“原位中间体探测”“DFT 势能面解析”），说明文字控制在 **3 栏 ≤ 45 汉字 / 4 栏 ≤ 35 汉字**，同一层级动词结构保持一致。
- **克制学术配色**：1 个中性深灰文字/边框 + 不超过 4 个语义强调色（橙 `#E67E22`、绿 `#2E9D50`、蓝 `#2F80ED`、紫 `#8E5CC7`），白底卡片置于浅色（90% 淡化）面板内，颜色用于区分研究阶段而非装饰。
- **字体与可读性**：中文用 `Microsoft YaHei`（微软雅黑）或思源黑体，英文数字用 `Arial`；缩放到 Word 实际页面宽度（约 15–16 cm）后，最小字号不小于 **8 pt**。
- **数据安全与隐私**：涉及未公开申请书内容，**严禁将 `.pptx` 或 `.drawio` 上传至未经授权的第三方在线转换网站**；一律使用本地 PowerPoint 或 Draw.io Desktop 打开与导出。

### 4. 标准双轨生成、校验与导出流水线

**步骤 1：准备路线图 JSON 配置**  
复制并修改 [assets/roadmap-template.json](../assets/roadmap-template.json)，包含 `title`、`subtitle`、`stages`（2–4 个阶段，每阶段含 `title`、`summary`、`tasks[1..4]`、`output`、可选 `color`）和 `final_outcome`。所有节点内容必须严格来源于正文，绝不虚构研究内容。

**步骤 2：一键同步生成可编辑 `.pptx` 与 `.drawio`（推荐）**
```bash
python scripts/generate_roadmap_pptx.py \
  --config my_roadmap.json \
  --output roadmap.pptx \
  --also-drawio roadmap.drawio
```
- 如仅需单独生成/校验 Draw.io：
  ```bash
  python scripts/generate_roadmap.py --config my_roadmap.json --output roadmap.drawio
  python scripts/validate_drawio.py roadmap.drawio
  ```

**步骤 3：本地精修与高清导出**
- **PowerPoint 路径**：用 PowerPoint / WPS 打开 `roadmap.pptx`，微调细节或叠加装置/机理小图后，全选组合 → 右键“另存为图片”（选 SVG 或 300+ DPI PNG；或导出 PDF 后转高清图）。
- **Draw.io 路径**：用本地 Draw.io Desktop 打开 `roadmap.drawio` 检查排版并导出：
  ```bash
  drawio --export --format svg --output roadmap.svg roadmap.drawio
  drawio --export --format png --scale 2 --border 20 --output roadmap.png roadmap.drawio
  ```
  > 正式提交版**不要使用 `--embed-diagram`**，导出后运行防泄密检测：
  ```bash
  python scripts/check_export_metadata.py roadmap.svg roadmap.png
  ```

---

## 二、多源文献检索（含 Google Scholar）与 NSFC 引用格式化工作流

### 1. 参考文献配置标准
- **数量**：青C **30–50 篇**，面上 **50–80 篇**。
- **结构**：国际权威顶刊（CNS 及学科顶刊）为主 + 少量高质量中文期刊文献为辅 + 申请人及团队前期代表作（可在文末或文中适当标示）。
- **时效**：近 5 年文献为主体，务必纳入**申报前一年与申报当年最新文献**，同时保留奠基性经典高引文献（绝不遗漏领域大牛代表作）。
- **格式统一**：全书采用 `[1], [2]...` 顺序编号；**作者姓名务必列全**（SWJTU 形式审查明确要求），期刊名、年份与卷期页码格式全篇统一。

### 2. 三轨互补检索策略（兼顾闭源论文摘要/关键词与中文文献）

1. **轨道 A — OpenAlex / Crossref / Semantic Scholar API（自动化批量检索主力）**
   - 无需 API Key，**即使对于 Elsevier / ACS / Wiley / Springer / Nature 等闭源付费期刊，依然可直接获取标题、全作者、期刊、DOI、引用数、关键词与摘要**，足以支撑立项依据文献筛选与脉络梳理：
   ```bash
   # 1. 鲸吞法（OpenAlex）：按高引排序找领域经典与权威综述，同时输出关键词与摘要
   python scripts/search_literature.py "oxidative coupling of methane kinetic modeling" --limit 20 --sort cited_by_count --compact --show-abstract

   # 2. 追前沿（OpenAlex）：近 3–5 年新进展 + 同步输出 Google Scholar 直达链接
   python scripts/search_literature.py "N2O oxidative coupling methane La2O3" --limit 20 --year-from 2022 --compact --show-abstract --gscholar-links

   # 3. 补闭源顶刊与最新在线发表（Crossref）：对燃烧/催化顶刊在线首发极敏感
   python scripts/search_literature.py "oxidative coupling methane radical mechanism" --source crossref --year-from 2023 --limit 15 --compact --show-abstract
   ```

2. **轨道 B — Google Scholar（谷歌学术入口：施引追踪 + 中文核心 + 摘要关键词补漏）**
   - **合规定位**：Google Scholar 具有严格反爬与 CAPTCHA 机制，**严禁使用脚本绕过验证码高频爬取**；应采用以下三种稳定合规方式发挥其优势：
     - **方式 1（Agent 交互检索）**：在对话中要求 Agent 使用内置 `search_web` 检索 `scholar.google.com` 相关条目，快速读取公开展示的标题、作者、摘要片段、关键词与施引关系；
     - **方式 2（一键直达检索链接）**：运行 `python scripts/search_literature.py "<关键词>" --gscholar-links --links-only`，自动生成按相关性、近 5 年、当年最新排列的 Google Scholar 直达 URL，供人工顺着“被引用次数（Cited by）”开展“钓鱼法”深挖；
     - **方式 3（Google Scholar BibTeX 无缝导入）**：在 Google Scholar 点击“引用 → BibTeX”收集选中文献至 `scholar_export.bib`，直接交给 `generate_references.py` 转为全作者标准 NSFC 编号格式。

3. **轨道 C — 人工核实闭环**
   - 闭源论文通过摘要/关键词可判断研究主题与相关性，但正式写入立项依据引用其具体数值或机理结论前，务必通过高校图书馆（如西南交大图书馆机构权限）或论文全文核实无误，严禁“仅凭摘要臆测结论”。

### 3. 批量生成全作者标准 NSFC 编号参考文献（零依赖纯 Python）
同时支持 **DOI/arXiv 列表（`.txt`）** 和 **Google Scholar 导出的 BibTeX（`.bib`）**：

```bash
# 从 DOI 列表生成全作者 NSFC 编号文献
python scripts/generate_references.py dois.txt --format nsfc --output refs_nsfc.txt

# 直接从 Google Scholar 导出的 BibTeX 转为统一全作者 NSFC 编号文献
python scripts/generate_references.py scholar_export.bib --format nsfc --output refs_nsfc.txt

# 如需 BibTeX 或带 DOI 的 Markdown 清单
python scripts/generate_references.py dois.txt --format bibtex --output refs.bib
python scripts/generate_references.py dois.txt --format markdown --output refs.md
```
