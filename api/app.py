import sqlite3
import smtplib
import re
import os
import jwt
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

SECRET_WORD = os.getenv("SECRET_WORD")
ROUTE_DB = os.getenv("DB_PATH")

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})

app.route('/')
def ola():
    return "Server ta on!!"

def verifica_token(token_recebido):
    try:
        dados = jwt.decode(token_recebido, SECRET_WORD, algorithms=["HS256"])
        return dados
    except:
        return None

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.getcwd(), filename)


def get_db_connection():
    conn = sqlite3.connect(ROUTE_DB)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== ROTAS GET ====================
@app.route('/api/buscar/envios', methods=['GET'])
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
    
@app.route('/api/buscar/inbox', methods=['GET'])
def buscar_inbox():
    dados = request.get_json()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT id, remetente, destinatario, assunto, corpo, data_hora 
            FROM emails 
            WHERE remetente = ? OR destinatario = ?
            ORDER BY data_hora DESC
        """
        cursor.execute(query, (dados['email'], dados['email']))
        
        rows = cursor.fetchall()
        resultados = [dict(row) for row in rows]
        conn.close()
        
        return jsonify(resultados), 200

    except Exception as e:
        print(f"ERRO NA BUSCA INBOX: {e}") 
        return jsonify({"erro": str(e)}), 500

    
@app.route('/api/contar/falhas', methods=['GET'])
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
       # conn.row_factory = sqlite3.Row 
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
    
@app.route('/api/emails/enviados', methods=['GET'])
def pesquisa_tabela():
    conn = None
    try:
        conn = get_db_connection()
       # conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
    
        query = """
            SELECT id, remetente FROM emails
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


@app.route('/api/trazer/logs_erro', methods=['GET'])
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM emails WHERE id = ?", (id_item,))
        deletados_emails = cursor.rowcount
        
        if deletados_emails == 0:
            return {"erro": "Item não encontrado em nenhuma tabela."}, 404

        conn.commit()
        return {"mensagem": "Item deletado com sucesso"}, 200

    except Exception as e:
        if conn: 
            conn.rollback()
        print(f"ERRO CRÍTICO NO BANCO: {str(e)}") 
        return {"erro": f"Erro interno no banco: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()

def deletar_falha(id_item):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM logs_erro WHERE id = ?", (id_item,))
        deletados_logs = cursor.rowcount

        if deletados_logs == 0:
            return {"erro": "Item não encontrado em nenhuma tabela."}, 404

        conn.commit()
        return {"mensagem": "Item deletado com sucesso"}, 200

    except Exception as e:
        if conn: 
            conn.rollback()
        print(f"ERRO CRÍTICO NO BANCO: {str(e)}") 
        return {"erro": f"Erro interno no banco: {str(e)}"}, 500
    finally:
        if conn:
            conn.close()

@app.route('/api/deletar/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete(id):

    print(f"REQUISIÇÃO ROTA: 'DELETE' : {datetime.now()}")

    if request.method == 'OPTIONS':
        return '', 200
    
    resultado, status_code = deletar_item(id)
    return jsonify(resultado), status_code

@app.route('/api/deletar/falhas/<int:id>', methods=['DELETE'])
def delete_falha(id):

    print(f"REQUISIÇÃO ROTA: 'DELETE' : {datetime.now()}")

    if request.method == 'OPTIONS':
        return '', 200
    
    resultado, status_code = deletar_falha(id)
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_erro (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_erro TEXT,
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
    
    required_fields = ["nome", "remetente", "destinatario", "senha_app", "assunto", "template"]
    if not all(field in data for field in required_fields):
        return jsonify({"erro": "Está faltando informações"}), 400

    senha = data['senha_app'].replace(" ", "")
    
    try:
        msg = MIMEMultipart()
        msg['From'] = data['remetente']
        msg['To'] = data['destinatario']
        msg['Subject'] = data['assunto']

        nome_template = data.get('template')

        msg.attach(MIMEText(nome_template, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(data['remetente'], senha)
        server.send_message(msg)
        server.quit()

        conn = sqlite3.connect("SSbanco.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO emails (nome, remetente, destinatario, senha_app, assunto, data_envio)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['nome'], data['remetente'], data['destinatario'], senha, data['assunto'], str(datetime.now())))
        conn.commit()
        conn.close()

        return jsonify({"status": "sucesso", "mensagem": "Email enviado e registrado"}), 200

    except smtplib.SMTPAuthenticationError:
        erro_msg = "Credenciais de remetente inválidas.."
        registrar_erro("Erro de Autenticação", erro_msg, data.get('remetente'))
        return jsonify({"erro": erro_msg}), 401
        
    except Exception as e:
        erro_msg = f"Falha na operação: {str(e)}"
        registrar_erro("Erro Geral", erro_msg, data.get('remetente'))
        return jsonify({"erro": erro_msg}), 500



@app.route('/api/criar/usuario', methods=['POST'])
def criar_user():
    data = request.get_json()
    result = criar_users(data)

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        response = make_response('', 204)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    data = request.get_json()
    nome = data.get('nome')
    senha = data.get('senha')
    email = data.get('email')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, nome, senha, email FROM usuarios WHERE nome = ? AND email = ?', (nome, email))
    usuario = cursor.fetchone()
    conn.close()

    if usuario and check_password_hash(usuario[2], senha):
       payload = {
        "usuario_id": usuario[0],
        "email": usuario[3],
        "exp": datetime.utcnow() + timedelta(hours=12)
       }
       token = jwt.encode(payload, SECRET_WORD, algorithm="HS256")
       return jsonify({
          "status": "sucesso",
          "mensagem": "Login realizado!",
          "usuario_id": usuario[0],
          "nome": usuario[1],
          "email": usuario[3],
          "token": token
       }), 200
    
    return jsonify({"erro": "Nome ou senha incorretos"}), 401

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5500)