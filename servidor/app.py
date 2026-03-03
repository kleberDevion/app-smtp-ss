import sqlite3
import smtplib
import re
import os
from flask_socketio import SocketIO, emit
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

CORS(app, 
     resources={r"/api/*": {"origins": "*"}},
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)

def get_db_connection():
    conn = sqlite3.connect('SSbanco.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.getcwd(), filename)

# ==================== ROTAS GET ====================
@app.route('/api/buscar/envios', methods=['GET', 'OPTIONS'])
def buscar_envios():
    if request.method == 'OPTIONS':
        return '', 200
    
    print(f"REQUISIÇÃO ROTA: 'GET' : {datetime.now()}")

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

@app.route('/api/contar/envios', methods=['GET', 'OPTIONS'])
def contar_envios():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as total FROM emails')
        resultado = cursor.fetchone()
        total = resultado['total']
        conn.close()

        return jsonify({"total": total}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@app.route('/api/contar/falhas', methods=['GET', 'OPTIONS'])
def contar_falhas():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as total FROM logs_erro')
        resultado = cursor.fetchone()
        total = resultado['total']
        conn.close()

        return jsonify({"total": total}), 200
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/contar/total', methods=['GET'])
def contar_dados():
    if request.method == 'OPTIONS':
        return '', 200
    try:
       conn = get_db_connection()
       cursor = conn.cursor()
       cursor.execute('SELECT COUNT(*) as total FROM emails')
       total_emails = cursor.fetchone()['total']
       conn.close()
        
       return jsonify({"total": total_emails})

    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"erro": str(e)}), 500
    
    
@app.route('/api/grafico/enviados', methods=['GET'])
def grafico_tabela():
    conn = None
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row 
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
        return jsonify(dados)

    except Exception as e:
        if conn:
            conn.close()
        print(f"ERRO NO SERVIDOR: {str(e)}") 
        return jsonify({"erro": str(e)}), 500

@app.route('/api/trazer/logs_erro', methods=['GET', 'OPTIONS'])
def trazer_logs():
    if request.method == 'OPTIONS':
        return '', 200  
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, tipo_erro, mensagem, remetente, data_hora FROM logs_erro')
        rows = cursor.fetchall()

        resultado = [dict(row) for row in rows]
        conn.close()

        return jsonify(resultado), 200
    
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"erro": str(e)}), 500


# ==================== ROTAS DELETE ====================
def deletar_item(id_item):
    conn = None
    try:
        conn = sqlite3.connect('SSbanco.db')
        cursor = conn.cursor()

        cursor.execute("DELETE FROM emails WHERE id = ?", (id_item,))
        deletados_emails = cursor.rowcount

        cursor.execute("DELETE FROM logs_erro WHERE id = ?", (id_item,))
        deletados_logs = cursor.rowcount

        if deletados_emails == 0 and deletados_logs == 0:
            return {"erro": "Item não existe em nenhuma tabela."}, 404

        conn.commit()
        return {"mensagem": "Item deletado com sucesso"}, 200

    except Exception as e:
        if conn: conn.rollback()
        return {"erro": f"Erro ao deletar: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()

@app.route('/api/deletar/<int:id>', methods=['DELETE', 'OPTIONS'])
def route_delete(id):

    print(f"REQUISIÇÃO ROTA: 'DELETE' : {datetime.now()}")

    if request.method == 'OPTIONS':
        return '', 200
    
    resultado, status_code = deletar_item(id)
    return jsonify(resultado), status_code

@app.route('/api/deletar/falhas/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_falha(id):

    print(f"REQUISIÇÃO ROTA: 'DELETE' : {datetime.now()}")

    if request.method == 'OPTIONS':
        return '', 200
    
    resultado, status_code = deletar_item(id)
    return jsonify(resultado), status_code

# ==================== ROTAS POST ====================

def validate_nome(nome):
    return re.match(r'^[A-Za-zÀ-ÿ\s]+$', nome) is not None
        
def validate_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None
        
def validate_senha_app(senha):
    return re.match(r'^[A-Za-z\s]+$', senha) is not None
        
def validate_assunto(assunto):
    return re.match(r'^[A-Za-z0-9\s]+$', assunto) is not None

def registrar_erro(tipo_erro, erro_msg, remetente):
    try:
        conn = sqlite3.connect('SSbanco.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_erro (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_erro TEXT,
                erro_msg TEXT,
                remetente TEXT,
                data_hora TEXT
            )
        ''')
        cursor.execute('''
            INSERT INTO logs_erro (tipo_erro, erro_msg, remetente, data_hora)
            VALUES (?, ?, ?, ?)
        ''', (tipo_erro, erro_msg, remetente, str(datetime.now())))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Falha crítica ao salvar log: {e}")

@app.route('/api/postar/envios', methods=['POST', 'OPTIONS'])
def postar_envios():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    print(f"REQUISIÇÃO ROTA: 'POST' : {datetime.now()}")
    
    required_fields = ["nome", "remetente", "destinatario", "senha_app", "assunto"]
    if not all(field in data for field in required_fields):
        return jsonify({"erro": "Está faltando informações"}), 400

    senha = data['senha_app'].replace(" ", "")
    
    try:
        msg = MIMEMultipart()
        msg['From'] = data['remetente']
        msg['To'] = data['destinatario']
        msg['Subject'] = data['assunto']

        html_body = f"""
          <div style="font-family:sans-serif;max-width:600px;margin:0 auto;border:1px solid #ddd;padding:20px;border-radius:8px">
            <h2 style="color:#333">Relatório de Execução</h2>
            <p style="color:#555">O processo foi finalizado com sucesso para {data['nome']}.</p>
            <a href="#" style="background:#4CAF50;color:white;padding:10px 20px;text-decoration:none;border-radius:5px">Ver Detalhes</a>
        </div>
        """
        msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(data['remetente'], senha)
        server.send_message(msg)
        server.quit()

        conn = sqlite3.connect('SSbanco.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO emails (nome, remetente, destinatario, senha_app, assunto, data_envio)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['nome'], data['remetente'], data['destinatario'], senha, data['assunto'], str(datetime.now())))
        conn.commit()
        conn.close()

        socketio.emit('atualizar_notificacao', {'status': 'sucesso', 'nome': data['nome']})

        return jsonify({"status": "sucesso", "mensagem": "Email enviado e registrado"}), 200

    except smtplib.SMTPAuthenticationError:
        erro_msg = "Credenciais de remetente inválidas.."
        socketio.emit('atualizar_notificacao', {'status': 'erro', 'msg': 'Falha de login'})
        registrar_erro("Erro de Autenticação", erro_msg, data.get('remetente'))
        return jsonify({"erro": erro_msg}), 401
        
    except Exception as e:
        erro_msg = f"Falha na operação: {str(e)}"
        registrar_erro("Erro Geral", erro_msg, data.get('remetente'))
        return jsonify({"erro": erro_msg}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5500)
