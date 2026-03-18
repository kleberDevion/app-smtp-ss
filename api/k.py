import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
ROUTE_DB = os.getenv("DB_PATH")

def criar_tabelas():
    try:
        conn = sqlite3.connect(ROUTE_DB)
        cursor = conn.cursor()
        
        # SQL para criar a tabela de envios realizados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails_w_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destinatario TEXT NOT NULL,
                assunto TEXT,
                corpo TEXT,
                data_hora TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Tabela 'envios_sucesso' criada ou já existente!")
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")

if __name__ == "__main__":
    criar_tabelas()
