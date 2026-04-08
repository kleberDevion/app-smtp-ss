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

CORS(app, resources={r"/*": {"origins": "*"}}, methods=["POST", "GET", "DELETE"])
socketio = SocketIO(app, cors_allowed_origins="*") 

@app.route('/chat-ss', methods=['POST'])
def post_chat_message():
    data = request.get_json()
    
    mensagem = data.get('msg')
    usuario = data.get('user_name')
    email_usuario = data.get('email_user')
    data_envio = datetime.now()
    destinatario = data.get('email_destinatario')

    try:
        conn = db_connection()
        cursor = conn.cursor()
        
        query = "INSERT INTO chat_suporte_dados_total (user_name, msg, email_user, email_destinatario, data_envio) VALUES (?, ?, ?, ?, ?)"
        valores = (usuario, mensagem, email_usuario, destinatario, datetime.now())
        
        cursor.execute(query, valores)
        conn.commit()
        cursor.close()
        conn.close()

        socketio.emit('nova_mensagem_global', {
            "user_name": usuario,
            "msg": mensagem,
            "email_user": email_usuario,
            "email_destinatario": destinatario,
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
        conn.row_factory = lambda cursor, row: {col[0]: row[i] for i, col in enumerate(cursor.description)}
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM chat_suporte_dados_total")
        rows = cursor.fetchall()
        
        resultados = []
        for row in rows:
            resultados.append({
                "id": row.get('id'),
                "user_name": row.get('user_name'),
                "msg": row.get('msg'),
                "email_user": row.get('email_user'),
                "email_destinatario": row.get('email_destinatario') or "",
                "data_envio": str(row.get('data_envio')),
                "is_dev": row.get('email_user') == OWNER
            })
        
        cursor.close()
        conn.close()
        return jsonify(resultados), 200
    except Exception as e:
        print(f"ERRO NO TERMINAL: {e}")
        return jsonify({"erro": str(e)}), 400
    
@app.route('/remove/item/<int:id>', methods=['DELETE'])
def deletar_item(id):
    
    try:
      conn = db_connection()
      cursor = conn.cursor()

      cursor.execute("DELETE FROM chat_suporte_dados_total WHERE id = ?", (id,))
      conn.commit()
      conn.close()

      return jsonify({"sucesso": "Item deletado"}), 200

    except Exception as e:
        return jsonify({"falha": "Erro interno no servidor"}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5507)