# Changelog

All notable changes to `nsfc-grant-craft` will be documented in this file.

## [1.0.0] - 2026-11-19

### Added
- **Progressive-disclosure Agent Skill (`SKILL.md` + 6 modular `references/`)**:
  - 2026+ NSFC "瘦身提质" policy guide, SWJTU submission norms, 3-category direct budget template (`设备费/业务费/劳务费`), and formal red-line checklist.
  - Pixel-level grant writing playbook (`What – So What – How`, 25-char title formula, 400-char abstract loop, funnel-shaped justification, scientific vs. engineering problems, 5-dimension feasibility, separated features vs. innovations).
  - Domain-specific high-scoring exemplar DNA tailored for catalysis, combustion kinetics, gas-solid interfacial reactions, in-situ diagnostics (e.g., SVUV-PIMS/spectroscopy), DFT/MD, and microkinetic modeling (MKM/Cantera/Chemkin-Pro).
  - Dual-reviewer (specialist + generalist) 100-point mock peer-review rubric, exemplar benchmarking, line-by-line polishing guide, and banned-phrase list.
  - 7-dimension pre-submission formal & cross-consistency checklist.
- **Dual-track Editable Technical Roadmap Toolchain (`scripts/`)**:
  - `generate_roadmap_pptx.py`: generates native editable PowerPoint (`.pptx`) roadmaps from JSON, with `--also-drawio` to simultaneously produce and validate a synchronized `.drawio` file.
  - `generate_roadmap.py`, `validate_drawio.py`, `check_export_metadata.py`: uncompressed `.drawio` XML generation, structural validation, and SVG/PNG embedded-source leak detection.
- **Multi-source Literature & Reference Toolchain (`scripts/`)**:
  - `search_literature.py`: OpenAlex, Crossref, and Semantic Scholar API search (returning abstracts & keywords even for paywalled journals) plus compliant Google Scholar direct-search URL generator (`--gscholar-links`).
  - `generate_references.py`: zero-dependency Python formatter supporting both DOI/arXiv lists (`.txt`) and Google Scholar BibTeX exports (`.bib`) into full-author NSFC numbered references, BibTeX, or Markdown.
- **Automated Proposal Auditor (`scripts/audit_proposal.py`)**:
  - Checks abstract length (≤400 chars), title risk, high-risk/banned phrases with exact line numbers & context, figure numbering & cross-references, and bidirectional `[n]` citation alignment.
- **Global Multi-Agent Installer (`install-global.ps1`)**:
  - Installs cleanly into `~/.gemini/config/skills`, `~/.agents/skills`, `~/.claude/skills`, and `~/.codex/skills`.
