import re
import sqlite3
import time
from pathlib import Path
from nl2sql import generate_sql
from charts import recommend_chart

BANNED = re.compile(
    r"\b(insert|update|delete|drop|alter|create|attach|detach|pragma|truncate|vacuum)\b", re.I)

class UnsafeSQL(Exception):
    pass

def validate(sql: str) -> str:
    s = sql.strip().rstrip(";").strip()
    if ";" in s:
        raise UnsafeSQL("Only one statement is allowed.")
    if not re.match(r"(?is)^(select|with)\b", s):
        raise UnsafeSQL("Only SELECT queries are allowed.")
    if BANNED.search(s):
        raise UnsafeSQL("Query contains a blocked keyword.")
    return s

def execute(db_path, sql, max_rows=500, timeout_s=5):
    s = validate(sql)
    conn = sqlite3.connect(f"{Path(db_path).resolve().as_uri()}?mode=ro", uri=True)
    deadline = time.time() + timeout_s
    conn.set_progress_handler(lambda: 1 if time.time() > deadline else 0, 10000)
    try:
        cur = conn.execute(s)
        cols = [d[0] for d in cur.description]
        rows = [["<binary>" if isinstance(v, (bytes, bytearray)) else v for v in r]
                for r in cur.fetchmany(max_rows)]
        return cols, rows
    finally:
        conn.close()

def run_query(question, schema, db_path, history=None, max_retries=2):
    sql = generate_sql(question, schema, history=history)
    for attempt in range(max_retries + 1):
        if sql == "CANNOT_ANSWER":
            return {"sql": sql, "error": "That question can't be answered from this database."}
        try:
            cols, rows = execute(db_path, sql)
            return {"sql": sql, "columns": cols, "rows": rows,
                    "chart": recommend_chart(cols, rows)}
        except UnsafeSQL as e:
            return {"sql": sql, "error": str(e)}
        except sqlite3.Error as e:
            if attempt == max_retries:
                return {"sql": sql, "error": f"Query failed: {e}"}
            sql = generate_sql(question, schema, history=history,
                               error=str(e), previous_sql=sql)