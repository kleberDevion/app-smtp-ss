import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def get_db_connection():
    conn = sqlite3.connect('SSbanco.db')
    conn.row_factory = sqlite3.Row
    return conn

def verificar_req():
    """
    Verifica a autorização da requisição baseada no cabeçalho ou corpo.
    Simula a lógica de validação de IP/Browser do PoolScript.
    """
    try:
        # Simulação da lógica de validação de origem/dispositivo
        user_agent = request.headers.get('User-Agent', '')
        if 'http' in user_agent or request.is_json:
            return True
        return False
    except Exception:
        return False

@app.route('/api/buscar/envios', methods=['GET'])
def buscar_envios():
    print(f"REQUISIÇÃO ROTA: 'GET' : {datetime.now()}")

    if not verificar_req():
        return jsonify({"message": "Requer autorização do proprietário."}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT nome, remetente, destinatario, data_envio FROM emails')
        rows = cursor.fetchall()

        # Converte linhas do banco para lista de dicionários
        resultados = [dict(row) for row in rows]
        conn.close()

        return jsonify(resultados), 200

    except sqlite3.Error:
        return jsonify({"erro": "Dados inexistentes."}), 404
    except Exception:
        return jsonify({"erro": "CONEXÃO DE INTERNET FRACA."}), 500

if __name__ == '__main__':
    host = 'localhost'
    port = 6006
    status = True
    print(f"SERVIDOR RODANDO NA PORTA: {port}, URL: http://{host}:{port}/api/ss status: {status}")
    app.run(host=host, port=port)