#!/usr/bin/env python3
"""Generate a native, fully editable PowerPoint (.pptx) technical roadmap.

Consumes the exact same JSON schema as `generate_roadmap.py` (2-4 stages) so
applicants can edit the roadmap directly in Microsoft PowerPoint / WPS while
optionally generating a synchronized Draw.io (.drawio) vector source via
`--also-drawio`.

Usage:
    python generate_roadmap_pptx.py --config assets/roadmap-template.json --output roadmap.pptx
    python generate_roadmap_pptx.py --config assets/roadmap-template.json --output roadmap.pptx --also-drawio roadmap.drawio
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from generate_roadmap import PALETTE, build_document, validate_config
from validate_drawio import validate_file

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FONT_CN = "Microsoft YaHei"
FONT_EN = "Arial"


def _rgb(hex_color: str) -> RGBColor:
    h = hex_color.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _tint_rgb(hex_color: str, white_ratio: float = 0.90) -> RGBColor:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return RGBColor(
        round(r * (1 - white_ratio) + 255 * white_ratio),
        round(g * (1 - white_ratio) + 255 * white_ratio),
        round(b * (1 - white_ratio) + 255 * white_ratio),
    )


def _set_round_rect(
    slide,
    left: float,
    top: float,
    width: float,
    height: float,
    *,
    fill_rgb: RGBColor,
    line_rgb: RGBColor | None,
    line_pt: float = 1.25,
    corner_radius: float = 0.06,
):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height),
    )
    if shape.adjustments:
        shape.adjustments[0] = corner_radius
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    if line_rgb is not None:
        shape.line.color.rgb = line_rgb
        shape.line.width = Pt(line_pt)
    else:
        shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def _add_two_level_text(
    shape,
    title: str,
    detail: str,
    *,
    title_rgb: RGBColor,
    title_pt: float,
    detail_rgb: RGBColor,
    detail_pt: float,
    align: PP_ALIGN = PP_ALIGN.LEFT,
    margin_lr: float = 0.12,
    margin_tb: float = 0.07,
):
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(margin_lr)
    tf.margin_right = Inches(margin_lr)
    tf.margin_top = Inches(margin_tb)
    tf.margin_bottom = Inches(margin_tb)

    p1 = tf.paragraphs[0]
    p1.alignment = align
    p1.space_after = Pt(2)
    r1 = p1.add_run()
    r1.text = title
    r1.font.name = FONT_CN
    r1.font.size = Pt(title_pt)
    r1.font.bold = True
    r1.font.color.rgb = title_rgb

    p2 = tf.add_paragraph()
    p2.alignment = align
    p2.space_before = Pt(1)
    r2 = p2.add_run()
    r2.text = detail
    r2.font.name = FONT_CN
    r2.font.size = Pt(detail_pt)
    r2.font.bold = False
    r2.font.color.rgb = detail_rgb


def build_pptx(config: dict[str, Any], output_path: Path) -> None:
    validate_config(config)
    stages: list[dict[str, Any]] = config["stages"]
    n_stages = len(stages)

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank layout

    # Clean white slide background
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = RGBColor(255, 255, 255)

    # 1. Top Title Card
    title_w = 10.6 if n_stages == 4 else 9.6
    title_x = (13.333 - title_w) / 2
    title_box = _set_round_rect(
        slide,
        title_x,
        0.24,
        title_w,
        0.86,
        fill_rgb=RGBColor(255, 255, 255),
        line_rgb=_rgb("#AAB7C4"),
        line_pt=1.5,
        corner_radius=0.10,
    )
    _add_two_level_text(
        title_box,
        config["title"],
        config["subtitle"],
        title_rgb=_rgb("#243746"),
        title_pt=18,
        detail_rgb=_rgb("#60717E"),
        detail_pt=11.5,
        align=PP_ALIGN.CENTER,
        margin_lr=0.16,
        margin_tb=0.06,
    )

    # 2. Stage Lanes
    margin_x = 0.35
    lane_gap = 0.32 if n_stages <= 3 else 0.24
    lane_w = (13.333 - 2 * margin_x - lane_gap * (n_stages - 1)) / n_stages
    lane_y = 1.30
    lane_h = 4.92

    task_title_pt = 11.5 if n_stages <= 3 else 10.5
    task_detail_pt = 10.0 if n_stages <= 3 else 9.0
    summary_pt = 10.5 if n_stages <= 3 else 9.5
    output_pt = 10.5 if n_stages <= 3 else 9.5

    stage_centers: list[float] = []

    for idx, stage in enumerate(stages, start=1):
        accent_hex = stage.get("color", PALETTE[(idx - 1) % len(PALETTE)])
        accent = _rgb(accent_hex)
        lane_x = margin_x + (idx - 1) * (lane_w + lane_gap)
        stage_centers.append(lane_x + lane_w / 2)

        # Stage outer panel
        _set_round_rect(
            slide,
            lane_x,
            lane_y,
            lane_w,
            lane_h,
            fill_rgb=_tint_rgb(accent_hex, 0.91),
            line_rgb=accent,
            line_pt=1.5,
            corner_radius=0.04,
        )

        # Number badge
        badge_d = 0.36
        badge = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(lane_x + 0.16),
            Inches(lane_y + 0.16),
            Inches(badge_d),
            Inches(badge_d),
        )
        badge.fill.solid()
        badge.fill.fore_color.rgb = accent
        badge.line.fill.background()
        btf = badge.text_frame
        btf.clear()
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        bp = btf.paragraphs[0]
        bp.alignment = PP_ALIGN.CENTER
        br = bp.add_run()
        br.text = str(idx)
        br.font.name = FONT_EN
        br.font.size = Pt(13)
        br.font.bold = True
        br.font.color.rgb = RGBColor(255, 255, 255)

        # Stage header title
        header = slide.shapes.add_textbox(
            Inches(lane_x + 0.58),
            Inches(lane_y + 0.12),
            Inches(lane_w - 0.72),
            Inches(0.44),
        )
        htf = header.text_frame
        htf.clear()
        htf.word_wrap = True
        htf.vertical_anchor = MSO_ANCHOR.MIDDLE
        hp = htf.paragraphs[0]
        hp.alignment = PP_ALIGN.LEFT
        hr = hp.add_run()
        hr.text = stage["title"]
        hr.font.name = FONT_CN
        hr.font.size = Pt(14 if n_stages <= 3 else 12.5)
        hr.font.bold = True
        hr.font.color.rgb = accent

        # Summary box
        inner_x = lane_x + 0.15
        inner_w = lane_w - 0.30
        summary_h = 0.86
        summary_box = _set_round_rect(
            slide,
            inner_x,
            lane_y + 0.64,
            inner_w,
            summary_h,
            fill_rgb=RGBColor(255, 255, 255),
            line_rgb=_tint_rgb(accent_hex, 0.55),
            line_pt=1.0,
            corner_radius=0.08,
        )
        _add_two_level_text(
            summary_box,
            "阶段目标",
            stage["summary"],
            title_rgb=accent,
            title_pt=11,
            detail_rgb=_rgb("#3C4B55"),
            detail_pt=summary_pt,
        )

        # Tasks area
        tasks: list[dict[str, str]] = stage["tasks"]
        tasks_top = lane_y + 1.62
        tasks_area_h = 2.48
        t_gap = 0.10
        t_h = min(1.02, (tasks_area_h - t_gap * (len(tasks) - 1)) / len(tasks))
        for t_idx, task in enumerate(tasks):
            t_y = tasks_top + t_idx * (t_h + t_gap)
            t_box = _set_round_rect(
                slide,
                inner_x,
                t_y,
                inner_w,
                t_h,
                fill_rgb=RGBColor(255, 255, 255),
                line_rgb=_rgb("#D6DEE3"),
                line_pt=1.0,
                corner_radius=0.08,
            )
            _add_two_level_text(
                t_box,
                task["title"],
                task["detail"],
                title_rgb=_rgb("#243746"),
                title_pt=task_title_pt,
                detail_rgb=_rgb("#52616B"),
                detail_pt=task_detail_pt,
            )

        # Stage Output pill
        out_box = _set_round_rect(
            slide,
            inner_x,
            lane_y + lane_h - 0.68,
            inner_w,
            0.54,
            fill_rgb=_tint_rgb(accent_hex, 0.78),
            line_rgb=accent,
            line_pt=1.4,
            corner_radius=0.14,
        )
        otf = out_box.text_frame
        otf.clear()
        otf.word_wrap = True
        otf.vertical_anchor = MSO_ANCHOR.MIDDLE
        otf.margin_left = Inches(0.10)
        otf.margin_right = Inches(0.10)
        op = otf.paragraphs[0]
        op.alignment = PP_ALIGN.CENTER
        orr = op.add_run()
        orr.text = f"阶段产出｜{stage['output']}"
        orr.font.name = FONT_CN
        orr.font.size = Pt(output_pt)
        orr.font.bold = True
        orr.font.color.rgb = accent

        # Inter-stage progression arrow
        if idx < n_stages:
            arrow_w = lane_gap - 0.06
            arrow_h = 0.24
            arrow = slide.shapes.add_shape(
                MSO_SHAPE.RIGHT_ARROW,
                Inches(lane_x + lane_w + 0.03),
                Inches(lane_y + lane_h * 0.48),
                Inches(arrow_w),
                Inches(arrow_h),
            )
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = _rgb("#95A5B4")
            arrow.line.fill.background()

    # 3. Downward converging arrows from stages to final outcome
    for center_x in stage_centers:
        d_arrow = slide.shapes.add_shape(
            MSO_SHAPE.DOWN_ARROW,
            Inches(center_x - 0.13),
            Inches(lane_y + lane_h + 0.07),
            Inches(0.26),
            Inches(0.28),
        )
        d_arrow.fill.solid()
        d_arrow.fill.fore_color.rgb = _rgb("#95A5B4")
        d_arrow.line.fill.background()

    # 4. Bottom Final Outcome Card
    final_box = _set_round_rect(
        slide,
        title_x,
        6.62,
        title_w,
        0.62,
        fill_rgb=RGBColor(255, 255, 255),
        line_rgb=_rgb("#4F6475"),
        line_pt=1.75,
        corner_radius=0.14,
    )
    ftf = final_box.text_frame
    ftf.clear()
    ftf.word_wrap = True
    ftf.vertical_anchor = MSO_ANCHOR.MIDDLE
    ftf.margin_left = Inches(0.18)
    ftf.margin_right = Inches(0.18)
    fp = ftf.paragraphs[0]
    fp.alignment = PP_ALIGN.CENTER
    fr = fp.add_run()
    fr.text = f"综合目标｜{config['final_outcome']}"
    fr.font.name = FONT_CN
    fr.font.size = Pt(13.5)
    fr.font.bold = True
    fr.font.color.rgb = _rgb("#243746")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a native editable PowerPoint (.pptx) NSFC technical roadmap"
    )
    parser.add_argument("--config", required=True, type=Path, help="Roadmap JSON config")
    parser.add_argument("--output", required=True, type=Path, help="Output .pptx path")
    parser.add_argument(
        "--also-drawio",
        type=Path,
        default=None,
        help="Optional path to simultaneously generate and validate a synchronized .drawio file",
    )
    args = parser.parse_args()

    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise TypeError("top-level JSON value must be an object")
        build_pptx(config, args.output)
        print(f"Generated editable PowerPoint roadmap: {args.output}")

        if args.also_drawio is not None:
            tree = build_document(config)
            args.also_drawio.parent.mkdir(parents=True, exist_ok=True)
            tree.write(args.also_drawio, encoding="utf-8", xml_declaration=True)
            report = validate_file(args.also_drawio)
            if report.errors:
                for err in report.errors:
                    print(f"Error (drawio): {err}", file=sys.stderr)
                return 1
            print(
                f"Generated synchronized Draw.io roadmap: {args.also_drawio} "
                f"({report.vertices} vertices, {report.edges} edges)"
            )
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
