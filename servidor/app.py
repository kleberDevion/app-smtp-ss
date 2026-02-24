import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, 
     resources={r"/api/*": {"origins": "*"}},
     methods=['GET', 'POST', 'DELETE', 'PUT', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)

def get_db_connection():
    conn = sqlite3.connect('SSbanco.db')
    conn.row_factory = sqlite3.Row
    return conn

def verificar_req():
    """
    Verifica a autorização da requisição baseada no cabeçalho ou corpo.
    """
    try:
        user_agent = request.headers.get('User-Agent', '')
        if 'http' in user_agent or request.is_json:
            return True
        return False
    except Exception:
        return False

# ==================== ROTAS GET ====================
@app.route('/api/buscar/envios', methods=['GET', 'OPTIONS'])
def buscar_envios():
    if request.method == 'OPTIONS':
        return '', 200
    
    print(f"REQUISIÇÃO ROTA: 'GET' : {datetime.now()}")

    if not verificar_req():
        return jsonify({"message": "Requer autorização do proprietário."}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, remetente, destinatario, data_envio FROM emails')
        rows = cursor.fetchall()

        resultados = [dict(row) for row in rows]
        conn.close()

        return jsonify(resultados), 200

    except sqlite3.Error:
        return jsonify({"erro": "Dados inexistentes."}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ==================== ROTAS DELETE ====================
def deletar_item(id_item):
    conn = None
    try:
        conn = sqlite3.connect('SSbanco.db')
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM emails WHERE id = ?", (id_item,))
        if cursor.fetchone() is None:
            return {"erro": "Item não existe na tabela de dados."}, 404

        cursor.execute("DELETE FROM emails WHERE id = ?", (id_item,))
        conn.commit()
        return {"mensagem": "Item deletado com sucesso"}, 200
    except Exception as e:
        return {"erro": f"Erro ao deletar: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()

@app.route('/api/deletar/<int:id>', methods=['DELETE', 'OPTIONS'])
def route_delete(id):
    if request.method == 'OPTIONS':
        return '', 200
    
    resultado, status_code = deletar_item(id)
    return jsonify(resultado), status_code

# ==================== ROTAS POST ====================
@app.route('/api/postar/envios', methods=['POST', 'OPTIONS'])
def enviar_email():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        dados = request.get_json()
        
        if not all(k in dados for k in ['nome', 'remetente', 'destinatario', 'assunto']):
            return jsonify({"erro": "Campos obrigatórios faltando"}), 400
        
        conn = sqlite3.connect('SSbanco.db')
        cursor = conn.cursor()
        
        data_envio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
            INSERT INTO emails (nome, remetente, destinatario, assunto, data_envio)
            VALUES (?, ?, ?, ?, ?)
        """, (dados['nome'], dados['remetente'], dados['destinatario'], dados['assunto'], data_envio))
        
        conn.commit()
        conn.close()
        
        return jsonify({"mensagem": "Email salvo com sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5500)
