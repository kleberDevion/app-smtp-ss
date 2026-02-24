import sqlite3
import re
import smtplib
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def init_db(): 
    conn = sqlite3.connect('SSbanco.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            remetente TEXT NOT NULL,
            destinatario TEXT NOT NULL,
            senha_app TEXT NOT NULL,
            assunto TEXT NOT NULL,
            data_envio TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def validate_nome(nome):
    if nome and re.match(r'^[a-zA-Z\s\u00C0-\u00FF]+$', nome):
        return True
    return False

def validate_email(email):
    # Simulação da validação externa e regex de email
    regex_email = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return bool(re.match(regex_email, email))

@app.route('/api/postar/envios', methods=['POST'])
def postar_envios():
    data = request.get_json()
    print(f"REQUISICAO RECEBIDA: {datetime.now()}")

    # Validação de campos obrigatórios
    required_fields = ["nome", "remetente", "destinatario", "senha_app", "assunto"]
    if not all(field in data for field in required_fields):
        return jsonify({"erro": "Esta faltando informações"}), 400

    # Validações específicas
    if not validate_nome(data['nome']):
        return jsonify({"erro": "Nome com carácteres inválidos ou vazio."}), 400

    if not validate_email(data['remetente']) or not validate_email(data['destinatario']):
        return jsonify({"erro": "Este endereço Email não é valido."}), 400

    senha = data['senha_app'].replace(" ", "")
    if len(senha) != 16:
        return jsonify({"erro": "Sua senha de app não contém um formato válido (16 dígitos).!!"}), 400

    if len(data['assunto']) > 300:
        return jsonify({"erro": "Assunto excede o limite de caracteres."}), 400

    # Configuração e Envio de E-mail
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

        # Salvar no Banco de Dados de forma segura
        try:
            with sqlite3.connect('SSbanco.db') as conn:
                conn.execute('PRAGMA journal_mode=WAL;')  # Garante modo seguro nesta conexão
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO emails (nome, remetente, destinatario, senha_app, assunto, data_envio)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (data['nome'], data['remetente'], data['destinatario'], senha, data['assunto'], str(datetime.now())))
                # O commit é automático ao sair do bloco 'with' se não houver erro
        except sqlite3.Error as e:
            return jsonify({"erro": f"Falha crítica no banco de dados: {str(e)}"}), 500

        return jsonify({"status": "sucesso", "mensagem": "Email enviado e registrado"}), 200

    except smtplib.SMTPAuthenticationError:
        return jsonify({"erro": "Credenciais de remetente inválidas.."}), 401
    except Exception as e:
        return jsonify({"erro": f"Conexão com servidor SMTP falhou: {str(e)}"}), 500

if __name__ == '__main__':
    init_db()
    print("SERVIDOR RODANDO NA PORTA: 7001, URL: http://localhost:7001/api/postar/envios")
    app.run(port=7001, host='localhost')