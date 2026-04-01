import os
import sqlite3
from flask import Flask, jsonify
from controladores.db_controle import db_connection

app = Flask(__name__)

def dashboard_main_dados():
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nome, remetente, destinatario, data_envio FROM emails"
        )
        rows = cursor.fetchall()
        # Assume-se que o cursor está configurado para retornar Row objects ou dicts
        resultados = [dict(row) for row in rows]
        conn.close()
        return jsonify(resultados), 200

    except sqlite3.Error:
        return jsonify({"erro": "Sem nada por enquanto"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def inbox_mail_dados():
    try:
        conn = db_connection()
        cursor = conn.cursor()
        # Corrigido o SQL para sintaxe válida
        cursor.execute(
            "SELECT id, remetente, destinatario, assunto, corpo, data_hora FROM emails"
        )
        rows = cursor.fetchall()
        resultados = [dict(row) for row in rows]
        conn.close()
        return jsonify(resultados), 200
    except Exception as e:
        print(f"ERRO AO ENVIAR DADOS PARA INBOX: {e}")
        return jsonify({"erro": str(e)}), 500

def contar_falhas():
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM logs_erro")
        resultado = cursor.fetchone()
        total = resultado['total'] if isinstance(resultado, dict) else resultado[0]
        conn.close()
        return jsonify(total), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def contar_total():
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as total FROM emails')
        resultado = cursor.fetchone()
        total = resultado['total'] if isinstance(resultado, dict) else resultado[0]
        conn.close()
        return jsonify(total), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def grafico_enviados():
    try:
        conn = db_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                strftime('%m/%Y', data_envio) as id, 
                COUNT(*) as total 
            FROM emails 
            GROUP BY id
            ORDER BY data_envio ASC
        """
        cursor.execute(query)
        dados = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(dados), 200
    except Exception as e:
        print(f"ERRO NO SERVIDOR: {str(e)}")
        return jsonify({"erro": str(e)}), 500

def trazer_logs():
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, tipo_erro, mensagem, remetente, data_hora FROM logs_erro')
        rows = cursor.fetchall()
        resultado = [dict(row) for row in rows]
        conn.close()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def deletar_item(id):
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM emails WHERE id = ?", (id,))
        deletado = cursor.rowcount
        if deletado == 0:
            return jsonify({"erro": "Item não encontrado."}), 404
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Item deletado com sucesso"}), 200
    except Exception as e:
        print(f"ERRO NO BANCO: {str(e)}")
        return jsonify({"erro": "Erro interno no servidor"}), 500

def deletar_falha(id):
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM logs_erro WHERE id = ?", (id,))
        deletados_logs = cursor.rowcount
        if deletados_logs == 0:
            return jsonify({"erro": "Erro: Item nao existe"}), 404
        conn.commit()
        conn.close()
        return jsonify({"mensagem": "Item deletado com sucesso"}), 200
    except Exception as e:
        print(f"ERRO NO BANCO: {str(e)}")
        return jsonify({"erro": "Erro interno no servidor"}), 500

if __name__ == "__main__":
    app.run(debug=True)