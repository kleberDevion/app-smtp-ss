import sqlite3

# 1. Conecta ao banco de dados
conexao = sqlite3.connect('SSbanco.db')
cursor = conexao.cursor()

# 2. Comando para adicionar a coluna 'email' do tipo 'TEXT'
# Sintaxe: ALTER TABLE nome_da_tabela ADD COLUMN nome_da_coluna tipo_de_dado
cursor.execute("ALTER TABLE emails ADD COLUMN corpo TEXT")

# 3. Salva as alterações e fecha
conexao.commit()
conexao.close()
