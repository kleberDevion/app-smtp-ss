import sqlite3

db_path = "SSbanco.db"
table = "usuarios"

with sqlite3.connect(db_path) as conn:
    conn.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    print(f"[ok] tabela '{table}' deletada.")