import sqlite3
import sys
from schema import get_schema_text
from nl2sql import generate_sql

DB_PATH = "northwind.db"
MAX_ROWS = 50

def is_safe(sql: str) -> bool:
    s = sql.strip().rstrip(";").lower()
    banned = ("insert", "update", "delete", "drop", "alter", "create", "attach", "pragma", "truncate")
    return s.startswith(("select", "with")) and ";" not in s and not any(
        f" {w} " in f" {s} " for w in banned)

def run_sql(sql: str):
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)   # read-only
    try:
        cur = conn.execute(sql)
        cols = [d[0] for d in cur.description]
        return cols, cur.fetchmany(MAX_ROWS)
    finally:
        conn.close()

def print_table(cols, rows):
    if not rows:
        print("(no rows)")
        return
    widths = [max(len(str(c)), *(len(str(r[i])) for r in rows)) for i, c in enumerate(cols)]
    print(" | ".join(str(c).ljust(w) for c, w in zip(cols, widths)))
    print("-+-".join("-" * w for w in widths))
    for r in rows:
        print(" | ".join(str(v).ljust(w) for v, w in zip(r, widths)))

def ask(question: str, schema: str):
    sql = generate_sql(question, schema)
    for attempt in range(3):                      # first try + 2 retries
        print(f"\nSQL: {sql}\n")
        if sql == "CANNOT_ANSWER":
            print("That can't be answered from this database.")
            return
        if not is_safe(sql):
            print("Blocked: only a single SELECT is allowed.")
            return
        try:
            print_table(*run_sql(sql))
            return
        except sqlite3.Error as e:
            print(f"DB error: {e}")
            if attempt == 2:
                return
            sql = generate_sql(question, schema, error=str(e), previous_sql=sql)

if __name__ == "__main__":
    schema = get_schema_text(f"sqlite:///{DB_PATH}")
    if len(sys.argv) > 1:
        ask(" ".join(sys.argv[1:]), schema)
    else:
        print("QueryLens CLI. Type a question, or 'exit'.")
        while True:
            q = input("\n> ").strip()
            if q.lower() in ("exit", "quit", ""):
                break
            ask(q, schema)