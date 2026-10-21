import sqlite3

DB_PATH = "northwind.db"

def get_schema(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    tables = [r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    lines = []
    for t in tables:
        cols = cur.execute(f'PRAGMA table_info("{t}")').fetchall()
        fks = cur.execute(f'PRAGMA foreign_key_list("{t}")').fetchall()
        col_text = ", ".join(
            f"{c[1]} {c[2]}" + (" PK" if c[5] else "") for c in cols)
        lines.append(f"Table {t}: {col_text}")
        for fk in fks:
            lines.append(f"  FK: {t}.{fk[3]} -> {fk[2]}.{fk[4]}")
    conn.close()
    return "\n".join(lines)

if __name__ == "__main__":
    print(get_schema())