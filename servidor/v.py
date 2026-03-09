import sqlite3

conn = sqlite3.connect('SSbanco.db')
cursor = conn.cursor()

cursor.execute("DELETE FROM emails WHERE id BETWEEN 1 AND 23")

conn.commit()
conn.close()
print("Registros deletados com sucesso!")
