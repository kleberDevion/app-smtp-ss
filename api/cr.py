import sqlite3

conexao = sqlite3.connect('SSbanco.db')
cursor = conexao.cursor()

# 2. Comando SQL para criar a tabela
cursor.execute('''
CREATE TABLE IF NOT EXISTS chat_suporte_dados_total (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT,
    msg TEXT,
    email_user TEXT,
    data_envio DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conexao.commit()
conexao.close()

print("tabela criada")
