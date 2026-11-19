#!/usr/bin/env python3
"""Batch-generate standardized NSFC references from DOIs, arXiv IDs, OR Google Scholar BibTeX (.bib).

Pure Python implementation using Crossref & OpenAlex APIs plus built-in BibTeX parser
(no external binary dependencies). Lists ALL authors by default in NSFC format.

Usage:
    python generate_references.py dois.txt --format nsfc --output refs.txt
    python generate_references.py google_scholar_export.bib --format nsfc --output refs.txt
    python generate_references.py dois.txt --format bibtex --output refs.bib
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

USER_AGENT = "nsfc-grant-craft/1.0 (NSFC reference formatter)"


def _normalize_doi(identifier: str) -> str:
    ident = identifier.strip()
    ident = re.sub(r"^https?://(dx\.)?doi\.org/", "", ident, flags=re.IGNORECASE)
    if ident.lower().startswith("doi:"):
        ident = ident[4:].strip()
    if ident.lower().startswith("arxiv:"):
        arxiv_id = ident.split(":", 1)[1].strip()
        return f"10.48550/arXiv.{arxiv_id}"
    return ident


def _fetch_json(url: str) -> dict | None:
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def _clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _clean_bib_val(val: str) -> str:
    val = val.strip().rstrip(",").strip()
    while (val.startswith("{") and val.endswith("}")) or (val.startswith('"') and val.endswith('"')):
        val = val[1:-1].strip()
    return re.sub(r"\s+", " ", val.replace("{", "").replace("}", "")).strip()


def _normalize_bib_author(raw_author: str) -> str:
    """Convert 'Family, Given' (Google Scholar BibTeX default) to 'Given Family'."""
    raw_author = raw_author.strip()
    if "," in raw_author:
        parts = [p.strip() for p in raw_author.split(",", 1)]
        if parts[1]:
            return f"{parts[1]} {parts[0]}".strip()
        return parts[0]
    return raw_author


def parse_bibtex_file(text: str) -> list[dict]:
    """Parse standard BibTeX entries (including Google Scholar exports) without extra deps."""
    entries: list[dict] = []
    # Split on top-level @type{
    chunks = re.split(r"(?m)^(?=@\w+\s*\{)", text)
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk.startswith("@"):
            continue
        fields: dict[str, str] = {}
        # Match field = {value} or "value" or bare digits across lines
        for m in re.finditer(
            r"(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"[^\"]*\"|\d+)",
            chunk,
            flags=re.DOTALL,
        ):
            fields[m.group(1).lower()] = _clean_bib_val(m.group(2))
        if not fields:
            continue
        raw_authors = fields.get("author", "")
        authors = [
            _normalize_bib_author(a)
            for a in re.split(r"\s+and\s+", raw_authors, flags=re.IGNORECASE)
            if a.strip()
        ]
        entries.append(
            {
                "doi": _normalize_doi(fields.get("doi", "")) if fields.get("doi") else "",
                "authors": authors,
                "title": fields.get("title", ""),
                "journal": fields.get("journal") or fields.get("booktitle") or fields.get("publisher") or "",
                "year": fields.get("year", ""),
                "volume": fields.get("volume", ""),
                "issue": fields.get("number", ""),
                "pages": fields.get("pages", "").replace("--", "-"),
            }
        )
    return entries


def fetch_metadata(identifier: str) -> dict | None:
    doi = _normalize_doi(identifier)
    cr_url = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}"
    cr_data = _fetch_json(cr_url)
    if cr_data and isinstance(cr_data.get("message"), dict):
        msg = cr_data["message"]
        authors: list[str] = []
        for author in msg.get("author") or []:
            given = (author.get("given") or "").strip()
            family = (author.get("family") or "").strip()
            name = f"{given} {family}".strip() or (author.get("name") or "").strip()
            if name:
                authors.append(name)

        titles = msg.get("title") or []
        title = _clean_text(titles[0]) if titles else ""
        containers = msg.get("container-title") or msg.get("short-container-title") or []
        journal = _clean_text(containers[0]) if containers else ""

        year = None
        for date_field in ("published-print", "published-online", "issued", "created"):
            parts = (msg.get(date_field) or {}).get("date-parts") or []
            if parts and parts[0] and parts[0][0]:
                year = parts[0][0]
                break

        pages = (msg.get("page") or msg.get("article-number") or "").strip()
        return {
            "doi": msg.get("DOI") or doi,
            "authors": authors,
            "title": title,
            "journal": journal,
            "year": str(year) if year else "",
            "volume": (msg.get("volume") or "").strip(),
            "issue": (msg.get("issue") or "").strip(),
            "pages": pages,
        }

    oa_url = f"https://api.openalex.org/works/https://doi.org/{urllib.parse.quote(doi, safe='')}"
    oa_data = _fetch_json(oa_url)
    if oa_data and oa_data.get("id"):
        authors = [
            (a.get("author") or {}).get("display_name", "").strip()
            for a in (oa_data.get("authorships") or [])
            if (a.get("author") or {}).get("display_name")
        ]
        biblio = oa_data.get("biblio") or {}
        first_p = biblio.get("first_page") or ""
        last_p = biblio.get("last_page") or ""
        pages = f"{first_p}-{last_p}" if first_p and last_p and first_p != last_p else first_p
        source = (oa_data.get("primary_location") or {}).get("source") or {}
        return {
            "doi": (oa_data.get("doi") or doi).removeprefix("https://doi.org/"),
            "authors": authors,
            "title": _clean_text(oa_data.get("title") or ""),
            "journal": _clean_text(source.get("display_name") or ""),
            "year": str(oa_data.get("publication_year") or ""),
            "volume": str(biblio.get("volume") or ""),
            "issue": str(biblio.get("issue") or ""),
            "pages": pages,
        }

    return None


def format_nsfc(index: int, meta: dict) -> str:
    """Format in clean NSFC numbered style with ALL authors listed."""
    authors_str = ", ".join(meta["authors"]) if meta["authors"] else "Unknown Author"
    vol_issue = meta["volume"]
    if meta["volume"] and meta["issue"]:
        vol_issue = f"{meta['volume']}({meta['issue']})"
    tail_parts = [p for p in (meta["journal"], meta["year"]) if p]
    tail = ", ".join(tail_parts)
    if vol_issue:
        tail = f"{tail}, {vol_issue}" if tail else vol_issue
    if meta["pages"]:
        tail = f"{tail}: {meta['pages']}" if tail else meta["pages"]
    return f"[{index}] {authors_str}. {meta['title']}. {tail}."


def format_markdown(index: int, meta: dict) -> str:
    base = format_nsfc(index, meta)
    return f"{base} DOI: {meta['doi']}" if meta.get("doi") else base


def format_bibtex(index: int, meta: dict) -> str:
    first_author = meta["authors"][0].split()[-1] if meta["authors"] else f"ref{index}"
    cite_key = re.sub(r"[^A-Za-z0-9]", "", first_author) + (meta["year"] or str(index)) + f"_{index}"
    authors_bib = " and ".join(meta["authors"]) if meta["authors"] else "Unknown"
    lines = [
        f"@article{{{cite_key},",
        f"  author = {{{authors_bib}}},",
        f"  title = {{{{{meta['title']}}}}},",
        f"  journal = {{{meta['journal']}}},",
        f"  year = {{{meta['year']}}},",
    ]
    if meta["volume"]:
        lines.append(f"  volume = {{{meta['volume']}}},")
    if meta["issue"]:
        lines.append(f"  number = {{{meta['issue']}}},")
    if meta["pages"]:
        lines.append(f"  pages = {{{meta['pages']}}},")
    if meta["doi"]:
        lines.append(f"  doi = {{{meta['doi']}}},")
    lines.append("}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate standardized NSFC references from DOIs or Google Scholar BibTeX (.bib)"
    )
    parser.add_argument("input", type=Path, help="DOI list (.txt) or Google Scholar BibTeX (.bib)")
    parser.add_argument(
        "--format",
        "-f",
        default="nsfc",
        choices=["nsfc", "bibtex", "markdown"],
        help="Output citation format (default: nsfc)",
    )
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output file path")
    parser.add_argument(
        "--ignore-errors",
        action="store_true",
        help="Write partial results even if some identifiers fail",
    )
    args = parser.parse_args()

    raw_text = args.input.read_text(encoding="utf-8")
    formatter = {"nsfc": format_nsfc, "bibtex": format_bibtex, "markdown": format_markdown}[
        args.format
    ]

    formatted: list[str] = []
    failures = 0

    if args.input.suffix.lower() == ".bib" or re.search(r"(?m)^@\w+\s*\{", raw_text):
        entries = parse_bibtex_file(raw_text)
        if not entries:
            print("Error: no valid BibTeX entries found", file=sys.stderr)
            return 1
        for idx, meta in enumerate(entries, start=1):
            formatted.append(formatter(idx, meta))
        total = len(entries)
    else:
        identifiers = [
            stripped
            for line in raw_text.splitlines()
            if (stripped := line.strip()) and not stripped.startswith("#")
        ]
        if not identifiers:
            print("Error: input file contains no identifiers", file=sys.stderr)
            return 1
        total = len(identifiers)
        for idx, ident in enumerate(identifiers, start=1):
            print(f"[{idx}/{total}] Resolving {ident}...", file=sys.stderr)
            meta = fetch_metadata(ident)
            if meta is None:
                print(f"  FAILED: could not resolve {ident}", file=sys.stderr)
                failures += 1
                continue
            formatted.append(formatter(len(formatted) + 1, meta))

    if not formatted:
        print("Error: no references were resolved", file=sys.stderr)
        return 1
    if failures and not args.ignore_errors:
        print(
            f"Error: {failures} identifier(s) failed; rerun with --ignore-errors to allow partial output",
            file=sys.stderr,
        )
        return 1

    sep = "\n\n" if args.format == "bibtex" else "\n"
    result = sep.join(formatted) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
        print(f"Wrote {len(formatted)}/{total} references to {args.output}", file=sys.stderr)
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
