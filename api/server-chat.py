import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from controladores.db_controle import db_connection

load_dotenv(override=True)

OWNER = os.getenv('OWNER_SOFTWARE')

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, methods=["POST", "GET"])
socketio = SocketIO(app, cors_allowed_origins="*") 

@app.route('/chat-ss', methods=['POST'])
def post_chat_message():
    data = request.get_json()
    
    mensagem = data.get('msg')
    usuario = data.get('user_name')
    email_usuario = data.get('email_user')
    data_envio = datetime.now()

    try:
        conn = db_connection()
        cursor = conn.cursor()
        
        query = "INSERT INTO chat_suporte_dados_total (user_name, msg, email_user, data_envio) VALUES (?, ?, ?, ?)"
        valores = (usuario, mensagem, email_usuario, datetime.now())
        
        cursor.execute(query, valores)
        conn.commit()
        cursor.close()
        conn.close()

        socketio.emit('nova_mensagem_global', {
            "user_name": usuario,
            "msg": mensagem,
            "email_user": email_usuario,
            "data_envio": str(data_envio),
            "is_dev": email_usuario == OWNER
        })

        return jsonify({"status": "Enviado"}), 200

    except Exception as e:
        return jsonify({"erro": "Falha no envio", "detalhes": str(e)}), 400

@app.route('/tunnek/msg', methods=['GET'])
def get_chat_messages():
    try:
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_name, msg, email_user, data_envio FROM chat_suporte_dados_total")

        PERFIL_OWNER = OWNER
        
        rows = cursor.fetchall()
        resultados = []
        for row in rows:
            resultados.append({
                "id": row[0],
                "user_name": row[1],
                "msg": row[2],
                "email_user": row[3],
                "data_envio": str(row[4]),
                "status": "Enviado",
                "is_dev": row[3] == PERFIL_OWNER
            })
        
        cursor.close()
        conn.close()

        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"erro": "Erro no envio ao carregar conversa"}), 400

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5507)