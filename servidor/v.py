import sqlite3

conn = sqlite3.connect('SSbanco.db')
cursor = conn.cursor()

# 1. Desativa verificações de chave estrangeira temporariamente
cursor.execute("PRAGMA foreign_keys = OFF")

# 2. Deleta a tabela inteira (Isso remove ela da sqlite_sequence automaticamente)
cursor.execute("DROP TABLE IF EXISTS logs_erro")

# 3. Recria a tabela do zero (Copie o seu CREATE TABLE original aqui)
cursor.execute("""
    CREATE TABLE logs_erro (
        id INTEGER PRIMARY KEY,
        tipo_erro,
        erro_msg,
        remetente,
        data_hora TEXT DEFAULT (datetime('now', 'localtime'))
    )
""")

# 4. Limpa a sujeira do arquivo e reseta tudo
cursor.execute("VACUUM")

conn.commit()
conn.close()
print("Tabela recriada e IDs resetados com força bruta!")
