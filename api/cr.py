from controladores.db_controle import db_connection

def resetar_usuarios():
    try:
        conn = db_connection()
        cursor = conn.cursor()
        
        # Executa o delete
        cursor.execute("DELETE FROM chat_suporte_dados_total")
        
        # OBRIGATÓRIO PARA SQLITE: Salvar as alterações
        conn.commit()
        
        # Verifica se limpou mesmo
        cursor.execute("SELECT count(*) FROM usuarios")
        total = cursor.fetchone()[0]
        
        print(f"Limpeza concluída! Total de usuários agora: {total}")
        
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        conn.close()

resetar_usuarios()
