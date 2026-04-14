import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
from flask import jsonify
from controladores.db_controle import db_connection

load_dotenv()

EMAIL_SISTEMA = os.getenv('EMAIL_SISTEMA')
SENHA_ENVIO = os.getenv('SENHA_ENVIO')

def scan_data(data):
    if not data or not all(key in data for key in ['nome', 'email', 'senha']):
        return jsonify({"erro": "Dados incompletos."}), 405

    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    try:
        conn = db_connection()
        cursor = conn.cursor()
        
        query = "SELECT nome, email, senha FROM admins_logins"
        cursor.execute(query)
        resultados = cursor.fetchall()
        conn.close()

        usuario_valido = any(
            res['nome'] == nome and res['email'] == email and res['senha'] == senha 
            for res in resultados
        )

        if not usuario_valido:
            return jsonify({"erro": "Dados inexistentes"}), 401

    except Exception as e:
        return jsonify({
            "erro": "Instabilidade no servidor, tente novamente mais tarde.",
            "type_error": str(e)
        }), 500

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SISTEMA
        msg['To'] = email
        msg['Subject'] = f"Você fez login em SsErp.com {nome}"

        #template_path = os.path.join('templates_welcome', 'new_login.html')
        #with open(template_path, 'r', encoding='utf-8') as file:
            #template_html = file.read()

        #msg.attach(MIMEText(template_html, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SISTEMA, SENHA_ENVIO)
        server.send_message(msg)
        server.quit()

        print(f"Email de boas-vindas enviado: {datetime.now()}")
    except Exception as e:
        print(f"Erro no envio de email de boas-vindas: {datetime.now()} - {str(e)}")

    return jsonify({"sucesso": "Redirecionando usuário..."}), 200