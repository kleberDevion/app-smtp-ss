import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
from controladores.db_controle import db_connection

# Carrega variáveis de ambiente
load_dotenv(override=True)

app = Flask(__name__)

# Configuração de CORS baseada na intenção do PoolScript
CORS(app, resources={r"/*": {"origins": "*"}}, methods=["POST", "GET"])

@app.route('/chat-ss', methods=['POST'])
def post_chat_message():
    data = request.get_json()
    
    mensagem = data.get('msg')
    usuario = data.get('user_name')
    email_usuario = data.get('email_user')

    try:
        conn = db_connection()
        cursor = conn.cursor()
        
        query = "INSERT INTO chat_suporte_dados_total (user_name, msg, email_user, data_envio) VALUES (?, ?, ?, ?)"
        valores = (usuario, mensagem, email_usuario, datetime.now())
        
        cursor.execute(query, valores)
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "Enviado"}), 200

    except Exception as e:
        return jsonify({"erro": "Falha no envio", "detalhes": str(e)}), 400

@app.route('/tunnek/msg', methods=['GET'])
def get_chat_messages():
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_name, msg, email_user, data_envio FROM chat_suporte_dados_total")
        
        rows = cursor.fetchall()
        resultados = []
        for row in rows:
            resultados.append({
                "id": row[0],
                "user_name": row[1],
                "msg": row[2],
                "email_user": row[3],
                "data_envio": str(row[4]),
                "status": "Enviado"
            })
        
        cursor.close()
        conn.close()

        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"erro": "Erro no envio ao carregar conversa"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5507)