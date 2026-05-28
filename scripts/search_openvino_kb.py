#!/usr/bin/env python3
"""Search the local OpenVINO Chroma knowledge base with SQLite metadata."""

from __future__ import annotations

import argparse
import os
import re
import sqlite3
import sys
from pathlib import Path

from path_utils import normalize_path

DEFAULT_DB = normalize_path(os.environ.get("OPENVINO_KB_DB", r"D:\knowledge-base\chroma_data\chroma.sqlite3"))
DEFAULT_COLLECTION = "openvino-kb"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search local Chroma collection documents for OpenVINO SOP evidence."
    )
    parser.add_argument("query", help="Keyword query. Terms are matched with case-insensitive LIKE.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Path to chroma.sqlite3.")
    parser.add_argument("--collection", default=DEFAULT_COLLECTION, help="Chroma collection name.")
    parser.add_argument("--limit", type=int, default=6, help="Maximum results to print.")
    parser.add_argument("--source-like", help="Only include sources containing this substring.")
    parser.add_argument("--any", action="store_true", help="Match any query term instead of all terms.")
    parser.add_argument("--context", type=int, default=900, help="Maximum snippet characters.")
    return parser.parse_args()


def terms_from_query(query: str) -> list[str]:
    terms = [term.lower() for term in re.findall(r"[A-Za-z0-9_./:+-]+", query)]
    result: list[str] = []
    for term in terms:
        if term and term not in result:
            result.append(term)
    return result


def snippet(text: str, terms: list[str], width: int) -> str:
    lower = text.lower()
    positions = [lower.find(term) for term in terms if lower.find(term) >= 0]
    if positions:
        start = max(0, min(positions) - width // 5)
        out = text[start : start + width]
        if start:
            out = "..." + out
    else:
        out = text[:width]
    return re.sub(r"\s+", " ", out).strip()


def main() -> int:
    args = parse_args()
    if not args.db.exists():
        print(f"DB not found: {args.db}", file=sys.stderr)
        return 2

    terms = terms_from_query(args.query)
    if not terms:
        print("Query did not contain searchable terms.", file=sys.stderr)
        return 2

    filter_joiner = " OR " if args.any else " AND "
    term_filters: list[str] = []
    filter_params: list[object] = []
    for term in terms:
        term_filters.append("lower(d.string_value) LIKE ?")
        filter_params.append(f"%{term}%")
    source_filter = ""
    source_params: list[object] = []
    if args.source_like:
        source_filter = " AND lower(coalesce(src.string_value, '')) LIKE ?"
        source_params.append(f"%{args.source_like.lower()}%")

    score_expr = " + ".join(
        ["CASE WHEN lower(d.string_value) LIKE ? THEN 1 ELSE 0 END" for _ in terms]
    )
    score_params = [f"%{term}%" for term in terms]

    sql = f"""
    WITH metadata_segments AS (
      SELECT s.id
      FROM segments s
      JOIN collections c ON c.id = s.collection
      WHERE c.name = ? AND s.scope = 'METADATA'
    )
    SELECT
      e.embedding_id,
      coalesce(src.string_value, '') AS source,
      coalesce(title.string_value, '') AS title,
      coalesce(ci.int_value, -1) AS chunk_index,
      coalesce(tc.int_value, -1) AS total_chunks,
      d.string_value AS document,
      ({score_expr}) AS score
    FROM embeddings e
    JOIN metadata_segments ms ON ms.id = e.segment_id
    JOIN embedding_metadata d ON d.id = e.id AND d.key = 'chroma:document'
    LEFT JOIN embedding_metadata src ON src.id = e.id AND src.key = 'source'
    LEFT JOIN embedding_metadata title ON title.id = e.id AND title.key = 'title'
    LEFT JOIN embedding_metadata ci ON ci.id = e.id AND ci.key = 'chunk_index'
    LEFT JOIN embedding_metadata tc ON tc.id = e.id AND tc.key = 'total_chunks'
    WHERE ({filter_joiner.join(term_filters)}){source_filter}
    ORDER BY score DESC, source, chunk_index
    LIMIT ?
    """

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        sql, [args.collection] + score_params + filter_params + source_params + [args.limit]
    ).fetchall()
    if not rows:
        print("No matches.")
        return 1

    for idx, row in enumerate(rows, 1):
        chunk = ""
        if row["chunk_index"] >= 0 and row["total_chunks"] >= 0:
            chunk = f" chunk {row['chunk_index'] + 1}/{row['total_chunks']}"
        print(f"\n[{idx}] {row['source']}{chunk} score={row['score']}")
        if row["title"]:
            print(f"    title: {row['title']}")
        print(f"    id: {row['embedding_id']}")
        print(f"    {snippet(row['document'], terms, args.context)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
