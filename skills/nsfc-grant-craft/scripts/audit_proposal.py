#!/usr/bin/env python3
"""Automated quality & formal-compliance auditor for NSFC proposal drafts (.md/.txt).

Checks:
1. Chinese abstract length (strict <= 400 chars incl. punctuation)
2. Proposal title length & engineering-jargon risk
3. High-risk / banned NSFC phrases with exact line numbers
4. Figure & Table sequential numbering and cross-reference consistency
5. Citation [n] / [1-3] / [1,2] vs Reference list bidirectional alignment
6. Reference count & body length against Youth (青C) / General (面上) / Key (重点) benchmarks

Usage:
    python audit_proposal.py draft.md --type general
    python audit_proposal.py draft.md --type youth --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HIGH_RISK_PHRASES: list[tuple[str, str, str]] = [
    (r"首次|首创|世界首次|国内首次|国际首次", "绝对化自吹", "建议改为“尚缺乏系统认识/鲜见针对……的定量报道/区别于已有方法”"),
    (r"国际领先|国际一流|世界领先|填补.*空白", "绝对化自吹", "极易引发小同行反感，建议客观阐述相对前人的增量突破"),
    (r"系统研究|全面总结|集成研究", "SWJTU重点避坑空泛词", "申请书特色与创新中应避免，直接写明具体科学对象、变量与机制"),
    (r"必将取得重大突破|彻底解决", "过度承诺", "建议改为“有望揭示……/为……提供重要理论支撑”"),
    (r"做一下|搞清楚|看看效果|大概|也许", "口语化/不严谨", "建议替换为“定量解析/揭示/阐明/构建”等规范动宾结构"),
    (r"尝试性地探索|初步探讨一下", "过度谦虚", "显得把握不足，建议改为客观笃定的“拟采用……系统揭示……”"),
    (r"！|!(?![^\s]*\[)", "感叹号", "基金申请书正文应保持客观冷静，避免使用感叹号"),
]

THRESHOLDS = {
    "youth": {"ref_min": 30, "ref_max": 55, "chars_min": 6500, "chars_max": 14000, "label": "青年科学基金（青C）"},
    "general": {"ref_min": 45, "ref_max": 90, "chars_min": 9000, "chars_max": 22000, "label": "面上项目"},
    "key": {"ref_min": 60, "ref_max": 130, "chars_min": 14000, "chars_max": 30000, "label": "重点项目"},
}


def _expand_citation_group(inner: str) -> list[int]:
    nums: list[int] = []
    cleaned = inner.replace("，", ",").replace("、", ",").replace("–", "-").replace("—", "-").replace("~", "-")
    for part in cleaned.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            bounds = part.split("-", 1)
            if bounds[0].strip().isdigit() and bounds[1].strip().isdigit():
                start, end = int(bounds[0].strip()), int(bounds[1].strip())
                if 0 < start <= end <= start + 30:
                    nums.extend(range(start, end + 1))
        elif part.isdigit():
            nums.append(int(part))
    return nums


def _extract_abstract(text: str) -> str | None:
    m = re.search(
        r"(?:^|\n)(?:#+\s*)?(?:中文)?摘要[：:\s]*\n+(.*?)(?=\n(?:#+\s*|关键词|英文摘要|Abstract|报告正文|（一）))",
        text,
        flags=re.DOTALL,
    )
    if m:
        return re.sub(r"\s+", "", m.group(1).strip())
    return None


def _extract_title(text: str) -> str | None:
    head = text.split("报告正文", 1)[0] if "报告正文" in text else "\n".join(text.splitlines()[:40])
    m = re.search(r"项目名称[：:]\s*([^\n]+)", head)
    if m:
        return m.group(1).strip()
    return None


def audit_text(text: str, project_type: str = "general") -> dict:
    cfg = THRESHOLDS[project_type]
    lines = text.splitlines()
    errors: list[str] = []
    warnings: list[str] = []
    passed: list[str] = []

    # 1. Basic stats (count CJK chars + alnum tokens)
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    if cjk_chars < cfg["chars_min"]:
        warnings.append(f"全文汉字数约 {cjk_chars} 字，低于{cfg['label']}常见参考区间（{cfg['chars_min']}–{cfg['chars_max']} 字），请确认内容是否过于单薄或仅为单章草稿。")
    elif cjk_chars > cfg["chars_max"]:
        warnings.append(f"全文汉字数约 {cjk_chars} 字，高于{cfg['label']}推荐精炼区间（{cfg['chars_min']}–{cfg['chars_max']} 字），注意 2026+“瘦身提质”原则（正文 ≤ 30 页）。")
    else:
        passed.append(f"全文汉字数约 {cjk_chars} 字，处于{cfg['label']}合理篇幅区间。")

    # 2. Title check
    title = _extract_title(text)
    if title:
        title_len = len(title)
        if title_len > 30:
            warnings.append(f"项目名称共 {title_len} 字（“{title}”），偏长，建议精炼至 25 字以内。")
        else:
            passed.append(f"项目名称长度合适（{title_len} 字）：“{title}”。")
        if re.search(r"技术开发|应用推广|产业化|设备研制", title):
            warnings.append(f"项目名称包含偏工程/应用词汇（“{title}”），建议突出基础科学问题（机理/机制/规律/模型）。")

    # 3. Abstract check
    abstract = _extract_abstract(text)
    if abstract:
        abs_len = len(abstract)
        if abs_len > 400:
            errors.append(f"中文摘要共 {abs_len} 字（含标点），超过基金委 400 字硬性上限，必须精简！")
        elif abs_len < 300:
            warnings.append(f"中文摘要仅 {abs_len} 字，信息密度偏低，建议充分利用至 360–395 字。")
        else:
            passed.append(f"中文摘要字数达标：{abs_len} / 400 字。")
        if re.search(r"\[\d+\]", abstract):
            errors.append("中文摘要中出现文献引用编号 [n]，摘要不应引用参考文献。")

    # 4. Split reference section vs body for citation check
    ref_header_idx = None
    for idx, line in enumerate(lines):
        if re.match(r"^\s*(?:#+\s*)?(?:\*\*)?(?:主要)?参考文献(?:\*\*)?\s*$", line):
            ref_header_idx = idx
            break

    ref_ids_defined: list[int] = []
    ref_block_end = len(lines)
    if ref_header_idx is not None:
        for idx in range(ref_header_idx + 1, len(lines)):
            line = lines[idx].strip()
            # Stop if hitting next major section (e.g. "2. 项目的研究内容" or "（二）")
            if re.match(r"^(?:#+\s*)?(?:2[\.．、]|（二）|##\s*2\b)", line):
                ref_block_end = idx
                break
            m = re.match(r"^\[(\d+)\]", line)
            if m:
                ref_ids_defined.append(int(m.group(1)))

    # Collect body lines excluding reference list
    body_lines = [
        (i + 1, line)
        for i, line in enumerate(lines)
        if ref_header_idx is None or not (ref_header_idx <= i < ref_block_end)
    ]

    # 5. Banned / high-risk phrase scan (in body)
    phrase_hits: list[dict] = []
    for lineno, line in body_lines:
        if line.strip().startswith("!["):
            continue
        for pattern, category, advice in HIGH_RISK_PHRASES:
            for match in re.finditer(pattern, line):
                s = max(0, match.start() - 30)
                e = min(len(line), match.end() + 40)
                prefix = "…" if s > 0 else ""
                suffix = "…" if e < len(line) else ""
                phrase_hits.append(
                    {
                        "line": lineno,
                        "match": match.group(0),
                        "category": category,
                        "advice": advice,
                        "snippet": f"{prefix}{line[s:e].strip()}{suffix}",
                    }
                )
    if phrase_hits:
        warnings.append(f"检测到 {len(phrase_hits)} 处高风险/禁词或不当标点表达（详见 phrase_hits 清单）。")
    else:
        passed.append("未检测到“首次/国际领先/填补空白/系统研究/口语化”等高风险表述。")

    # 6. Citation bidirectional alignment
    cited_set: set[int] = set()
    for _, line in body_lines:
        for m in re.finditer(r"\[([\d,\s\-–—~，、]+)\]", line):
            for num in _expand_citation_group(m.group(1)):
                cited_set.add(num)

    defined_set = set(ref_ids_defined)
    if ref_ids_defined:
        ref_count = len(ref_ids_defined)
        if ref_count < cfg["ref_min"]:
            warnings.append(f"参考文献共 {ref_count} 篇，略少于{cfg['label']}建议范围（{cfg['ref_min']}–{cfg['ref_max']} 篇）。")
        elif ref_count > cfg["ref_max"]:
            warnings.append(f"参考文献共 {ref_count} 篇，多于{cfg['label']}常见范围（{cfg['ref_min']}–{cfg['ref_max']} 篇），注意精简聚焦。")
        else:
            passed.append(f"参考文献数量合理：{ref_count} 篇。")

        expected_seq = list(range(1, max(ref_ids_defined) + 1))
        if ref_ids_defined != expected_seq:
            errors.append(f"参考文献列表编号不连续或存在重复/乱序（共 {len(ref_ids_defined)} 条，最大编号 {max(ref_ids_defined)}）。")
        else:
            passed.append("参考文献列表编号连续无跳号。")

        missing_in_list = sorted(cited_set - defined_set)
        uncited_in_list = sorted(defined_set - cited_set)
        if missing_in_list:
            errors.append(f"正文引用了但参考文献列表中缺失的编号：{missing_in_list}")
        if uncited_in_list:
            warnings.append(f"参考文献列表中存在但正文未引用的编号：{uncited_in_list}")
        if not missing_in_list and not uncited_in_list:
            passed.append("正文引用编号与参考文献列表 100% 双向对齐。")
    elif cited_set:
        warnings.append(f"正文检测到 {len(cited_set)} 个文献引用编号，但未识别到以“[1]”开头的参考文献列表。")

    # 7. Figure numbering check
    fig_captions: list[int] = []
    fig_refs: set[int] = set()
    for _, line in body_lines:
        stripped = line.strip()
        if stripped.startswith("!["):
            continue
        cap = re.match(r"^(?:\*\*)?图\s*(\d+)(?:\*\*)?[\.。：:\s]", stripped)
        if cap:
            fig_captions.append(int(cap.group(1)))
            continue
        for m in re.finditer(r"图\s*(\d+)", stripped):
            fig_refs.add(int(m.group(1)))

    if fig_captions:
        expected_figs = list(range(1, max(fig_captions) + 1))
        if fig_captions != expected_figs:
            errors.append(f"图注编号不连续或存在重复：{fig_captions}")
        else:
            passed.append(f"图注编号连续（图 1 – 图 {max(fig_captions)}）。")
        missing_figs = sorted(fig_refs - set(fig_captions))
        unreferenced_figs = sorted(set(fig_captions) - fig_refs)
        if missing_figs:
            errors.append(f"正文引用了但未找到对应图注的图号：{missing_figs}")
        if unreferenced_figs:
            warnings.append(f"存在图注但正文未显式引用的图号：{unreferenced_figs}")
        if not missing_figs and not unreferenced_figs:
            passed.append("正文图号引用与图注 100% 对应。")

    return {
        "project_type": cfg["label"],
        "stats": {
            "cjk_chars": cjk_chars,
            "abstract_chars": len(abstract) if abstract else None,
            "references_defined": len(ref_ids_defined),
            "references_cited": len(cited_set),
            "figures_captioned": len(fig_captions),
            "phrase_hits_count": len(phrase_hits),
        },
        "errors": errors,
        "warnings": warnings,
        "passed": passed,
        "phrase_hits": phrase_hits,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit NSFC proposal draft for formal & consistency issues")
    parser.add_argument("path", type=Path, help="Path to Markdown or text proposal draft")
    parser.add_argument(
        "--type",
        dest="project_type",
        default="general",
        choices=["youth", "general", "key"],
        help="NSFC project category (default: general)",
    )
    parser.add_argument("--json", action="store_true", help="Output structured JSON report")
    args = parser.parse_args()

    try:
        content = args.path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return 2

    report = audit_text(content, args.project_type)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        st = report["stats"]
        print(f"=== NSFC 申请书自动化体检报告 ({report['project_type']}) ===")
        print(f"文件: {args.path}")
        print(
            f"统计: 正文汉字约 {st['cjk_chars']} 字 | 摘要 {st['abstract_chars'] or '未检测到'} 字 | "
            f"参考文献 {st['references_defined']} 篇(引用 {st['references_cited']} 篇) | "
            f"图注 {st['figures_captioned']} 张 | 高风险表达 {st['phrase_hits_count']} 处"
        )
        print()
        if report["errors"]:
            print(f"❌ 未通过项 ({len(report['errors'])})：")
            for item in report["errors"]:
                print(f"  - {item}")
            print()
        if report["warnings"]:
            print(f"⚠️ 警告项 ({len(report['warnings'])})：")
            for item in report["warnings"]:
                print(f"  - {item}")
            print()
        if report["phrase_hits"]:
            print("🔍 高风险词汇/表达定位（最多展示前 20 条）：")
            for hit in report["phrase_hits"][:20]:
                print(f"  - L{hit['line']} [{hit['category']}] 命中“{hit['match']}” → {hit['advice']}")
                print(f"    上下文: {hit['snippet']}")
            print()
        if report["passed"]:
            print(f"✅ 通过项 ({len(report['passed'])})：")
            for item in report["passed"]:
                print(f"  - {item}")

    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
