#!/usr/bin/env python3
"""Multi-source academic literature search for NSFC proposals.

Supports:
- OpenAlex API (default, free, returns titles, authors, journals, DOIs, citation
  counts, keywords/concepts, and abstracts even for paywalled/closed-access papers)
- Crossref API (free, strong coverage of Elsevier/ACS/Wiley/RSC/Springer journals)
- Semantic Scholar API (free, returns abstracts & citation counts)
- Google Scholar query URL generator (--gscholar-links) for compliant manual/browser
  inspection, Cited-by tracking, and Chinese core journals without bot scraping.

Usage:
    python search_literature.py "oxidative coupling of methane N2O" --limit 15 --year-from 2021 --compact
    python search_literature.py "methane oxidative coupling La2O3" --source crossref --limit 10 --compact
    python search_literature.py "甲烷氧化偶联 N2O 机理" --gscholar-links
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OPENALEX_API = "https://api.openalex.org/works"
CROSSREF_API = "https://api.crossref.org/works"
S2_API = "https://api.semanticscholar.org/graph/v1/paper/search"
USER_AGENT = "nsfc-grant-craft/1.0 (NSFC literature helper)"


def _clean_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def _parse_openalex(work: dict) -> dict:
    authors = [
        (a.get("author") or {}).get("display_name") or ""
        for a in (work.get("authorships") or [])
        if (a.get("author") or {}).get("display_name")
    ]
    doi = (work.get("doi") or "").removeprefix("https://doi.org/")

    abstract_index = work.get("abstract_inverted_index") or {}
    word_positions = [
        (pos, word) for word, positions in abstract_index.items() for pos in positions
    ]
    word_positions.sort()
    abstract = " ".join(word for _, word in word_positions)

    keywords = [
        kw.get("display_name")
        for kw in (work.get("keywords") or [])[:6]
        if kw.get("display_name")
    ]
    if not keywords:
        keywords = [
            c.get("display_name")
            for c in (work.get("concepts") or [])[:5]
            if c.get("display_name")
        ]

    source = (work.get("primary_location") or {}).get("source") or {}
    oa_info = work.get("open_access") or {}
    return {
        "source_api": "openalex",
        "title": work.get("title") or "",
        "doi": doi,
        "authors": authors,
        "year": work.get("publication_year"),
        "cited_by_count": work.get("cited_by_count") or 0,
        "journal": source.get("display_name") or "",
        "is_oa": bool(oa_info.get("is_oa")),
        "keywords": keywords,
        "abstract": abstract[:600],
    }


def search_openalex(
    query: str,
    limit: int = 10,
    year_from: int | None = None,
    sort: str = "relevance_score",
    mailto: str | None = None,
) -> list[dict]:
    filters = [
        f"to_publication_date:{datetime.now(timezone.utc).date().isoformat()}",
        "primary_location.source.type:journal|conference",
    ]
    if year_from:
        filters.append(f"from_publication_date:{year_from}-01-01")

    params = {"search": query, "per_page": limit, "filter": ",".join(filters)}
    if mailto:
        params["mailto"] = mailto
    if sort != "relevance_score":
        params["sort"] = f"{sort}:desc"

    url = f"{OPENALEX_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return [_parse_openalex(w) for w in data.get("results") or []]


def search_crossref(
    query: str,
    limit: int = 10,
    year_from: int | None = None,
    sort: str = "relevance_score",
    mailto: str | None = None,
) -> list[dict]:
    params: dict[str, Any] = {"query": query, "rows": limit}
    if year_from:
        params["filter"] = f"from-pub-date:{year_from}-01-01,type:journal-article"
    else:
        params["filter"] = "type:journal-article"
    if sort == "cited_by_count":
        params["sort"] = "is-referenced-by-count"
        params["order"] = "desc"
    elif sort == "publication_date":
        params["sort"] = "published"
        params["order"] = "desc"
    if mailto:
        params["mailto"] = mailto

    url = f"{CROSSREF_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    results = []
    for item in (data.get("message") or {}).get("items") or []:
        authors = []
        for a in item.get("author") or []:
            name = f"{a.get('given', '')} {a.get('family', '')}".strip() or a.get("name", "")
            if name:
                authors.append(name)
        year = None
        for df in ("published-print", "published-online", "issued"):
            parts = (item.get(df) or {}).get("date-parts") or []
            if parts and parts[0] and parts[0][0]:
                year = parts[0][0]
                break
        titles = item.get("title") or []
        journals = item.get("container-title") or []
        results.append(
            {
                "source_api": "crossref",
                "title": _clean_html(titles[0]) if titles else "",
                "doi": item.get("DOI") or "",
                "authors": authors,
                "year": year,
                "cited_by_count": item.get("is-referenced-by-count") or 0,
                "journal": _clean_html(journals[0]) if journals else "",
                "is_oa": False,
                "keywords": (item.get("subject") or [])[:6],
                "abstract": _clean_html(item.get("abstract") or "")[:600],
            }
        )
    return results


def search_semanticscholar(query: str, limit: int = 10, year_from: int | None = None) -> list[dict]:
    params = {
        "query": query,
        "limit": min(limit, 50),
        "fields": "title,authors,year,venue,citationCount,externalIds,abstract,fieldsOfStudy,isOpenAccess",
    }
    if year_from:
        params["year"] = f"{year_from}-"
    url = f"{S2_API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    results = []
    for item in data.get("data") or []:
        ext = item.get("externalIds") or {}
        results.append(
            {
                "source_api": "semanticscholar",
                "title": item.get("title") or "",
                "doi": ext.get("DOI") or "",
                "authors": [a.get("name", "") for a in (item.get("authors") or []) if a.get("name")],
                "year": item.get("year"),
                "cited_by_count": item.get("citationCount") or 0,
                "journal": item.get("venue") or "",
                "is_oa": bool(item.get("isOpenAccess")),
                "keywords": (item.get("fieldsOfStudy") or [])[:6],
                "abstract": (item.get("abstract") or "")[:600],
            }
        )
    return results


def build_google_scholar_links(query: str, year_from: int | None = None) -> dict[str, str]:
    now_year = datetime.now(timezone.utc).year
    q_enc = urllib.parse.quote_plus(query)
    links = {
        "all_time_relevance": f"https://scholar.google.com/scholar?q={q_enc}&hl=zh-CN",
        f"recent_5y_{now_year - 4}_plus": f"https://scholar.google.com/scholar?q={q_enc}&as_ylo={now_year - 4}&hl=zh-CN",
        f"latest_{now_year - 1}_plus": f"https://scholar.google.com/scholar?q={q_enc}&as_ylo={now_year - 1}&scisbd=1&hl=zh-CN",
    }
    if year_from:
        links[f"custom_{year_from}_plus"] = f"https://scholar.google.com/scholar?q={q_enc}&as_ylo={year_from}&hl=zh-CN"
    return links


def main() -> int:
    parser = argparse.ArgumentParser(description="Multi-source academic literature search for NSFC")
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--source",
        default="openalex",
        choices=["openalex", "crossref", "semanticscholar"],
        help="Metadata API backend (default: openalex)",
    )
    parser.add_argument("--limit", type=int, default=10, help="Number of results (1-50)")
    parser.add_argument("--year-from", type=int, default=None, help="Filter papers from this year")
    parser.add_argument(
        "--sort",
        default="relevance_score",
        choices=["relevance_score", "cited_by_count", "publication_date"],
        help="Sort order",
    )
    parser.add_argument("--compact", action="store_true", help="Compact one-line-per-paper output")
    parser.add_argument(
        "--show-abstract", action="store_true", help="Include abstract & keywords in compact output"
    )
    parser.add_argument(
        "--gscholar-links",
        action="store_true",
        help="Print ready-to-open Google Scholar search URLs (no scraping) and exit if --links-only",
    )
    parser.add_argument("--links-only", action="store_true", help="Only print Google Scholar URLs")
    parser.add_argument("--mailto", default=None, help="Contact email for API polite pool")
    args = parser.parse_args()

    query = args.query.strip()
    if not query:
        print("Error: query must not be empty", file=sys.stderr)
        return 1

    if args.gscholar_links or args.links_only:
        links = build_google_scholar_links(query, args.year_from)
        print("=== Google Scholar 检索入口（浏览器直达，支持摘要/关键词/施引追踪与 BibTeX 导出） ===")
        for label, url in links.items():
            print(f"  [{label}] {url}")
        if args.links_only:
            return 0
        print()

    try:
        if args.source == "openalex":
            results = search_openalex(query, args.limit, args.year_from, args.sort, args.mailto)
        elif args.source == "crossref":
            results = search_crossref(query, args.limit, args.year_from, args.sort, args.mailto)
        else:
            results = search_semanticscholar(query, args.limit, args.year_from)
    except (ValueError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"Error: {args.source} search failed: {exc}", file=sys.stderr)
        return 1

    if args.compact:
        for r in results:
            authors_str = ", ".join(r["authors"][:3])
            if len(r["authors"]) > 3:
                authors_str += " et al."
            oa_tag = "OA" if r["is_oa"] else "Closed"
            print(
                f"[{r['year']}] {r['title']} | {authors_str} | {r['journal']} | "
                f"DOI:{r['doi']} | Cited:{r['cited_by_count']} | {oa_tag}"
            )
            if args.show_abstract:
                if r["keywords"]:
                    print(f"    Keywords: {', '.join(r['keywords'])}")
                if r["abstract"]:
                    print(f"    Abstract: {r['abstract']}")
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
