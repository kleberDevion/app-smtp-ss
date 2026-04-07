import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'SSbanco.db') 

def db_connection():
    """
    Estabelece uma conexão com o banco de dados SQLite.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def registrar_erro(tipo_erro, remetente):
    """
    Registra um log de erro no banco de dados.
    """
    try:
        conn = db_connection()
        if conn is None:
            return
            
        cursor = conn.cursor()
        # Obtém o timestamp atual no formato ISO
        data_hora = datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO logs_erro (tipo_erro, remetente, data_hora) VALUES (?, ?, ?)",
            (tipo_erro, remetente, data_hora)
        )
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Falha ao salvar log: {e}")

if __name__ == "__main__":
    # Simulação da intenção de execução principal
    print("Controlador de Banco de Dados iniciado.")