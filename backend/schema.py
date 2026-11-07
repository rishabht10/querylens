from sqlalchemy import create_engine, inspect, text

def get_schema_text(db_url: str, sample_rows: int = 2) -> str:
    engine = create_engine(db_url)
    insp = inspect(engine)
    lines = []
    with engine.connect() as conn:
        for table in insp.get_table_names():
            cols = [f"{c['name']} {c['type']}" for c in insp.get_columns(table)]
            lines.append(f'TABLE "{table}" ({", ".join(cols)})')
            for fk in insp.get_foreign_keys(table):
                lines.append(f'  FK "{table}"({", ".join(fk["constrained_columns"])}) -> '
                             f'"{fk["referred_table"]}"({", ".join(fk["referred_columns"])})')
            try:
                for r in conn.execute(text(f'SELECT * FROM "{table}" LIMIT {sample_rows}')):
                    lines.append(f"  SAMPLE: {[str(v)[:30] for v in r]}")
            except Exception:
                pass
    return "\n".join(lines)

if __name__ == "__main__":
    print(get_schema_text("sqlite:///northwind.db"))