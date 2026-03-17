import sqlite3

def restaurar_banco():
    try:
        conn = sqlite3.connect('SSbanco.db')
        cursor = conn.cursor()

        # Cria a tabela logs_erro se ela não existir
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_erro (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_erro TEXT,
                mensagem TEXT,
                remetente TEXT,
                data_hora TEXT
            )
        ''')

        conn.commit()
        print("✅ Tabela 'logs_erro' criada ou já existente com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    restaurar_banco()
