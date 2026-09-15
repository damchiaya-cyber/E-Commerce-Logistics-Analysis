"""
Executes sql/business_queries.sql against ecommerce.db and writes the
results to reports/sql_findings.md as readable tables.

Run: python run_queries.py
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = "ecommerce.db"
QUERIES_PATH = Path("sql/business_queries.sql")
REPORT_PATH = Path("reports/sql_findings.md")


def split_queries(sql_text: str):
    """Split the .sql file into (comment_title, query) pairs."""
    blocks = re.split(r"\n\s*\n", sql_text.strip())
    parsed = []
    for block in blocks:
        lines = block.strip().splitlines()
        comment_lines = [l[2:].strip() for l in lines if l.strip().startswith("--")]
        query_lines = [l for l in lines if not l.strip().startswith("--")]
        query = "\n".join(query_lines).strip()
        if query:
            title = comment_lines[0] if comment_lines else "Query"
            parsed.append((title, query))
    return parsed


def main():
    conn = sqlite3.connect(DB_PATH)
    sql_text = QUERIES_PATH.read_text(encoding="utf-8")
    queries = split_queries(sql_text)

    report_lines = ["# SQL Findings", ""]
    for title, query in queries:
        df = pd.read_sql_query(query, conn)
        report_lines.append(f"## {title}")
        report_lines.append(df.to_markdown(index=False))
        report_lines.append("")

    REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")
    conn.close()
    print(f"Wrote {len(queries)} query results to {REPORT_PATH}")


if __name__ == "__main__":
    main()
