from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import sqlite3
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

load_dotenv(override=True) 

EMAIL_SISTEMA = os.getenv("EMAIL_SISTEMA")
DB_PATH = os.getenv("DB_PATH")
AUTH_KEY = os.getenv("SENHA_ENVIO").replace(" ", "") if os.getenv("SENHA_ENVIO") else None

print(f"DEBUG - Email: {EMAIL_SISTEMA}")
print(f"DEBUG - Senha carregada: {AUTH_KEY}")

def open_connect():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Erro na função (open_connect): {e}")
        return None

def registrar_erro(tipo_erro, erro_msg, remetente):
    try:
        conn = open_connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO logs_erro (tipo_erro, remetente, data_hora) VALUES (?, ?, ?)",
                (tipo_erro, erro_msg, remetente, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            conn.commit()
            conn.close()
            print(f"ERRO DE AUTHENTICAÇAO SALVO NA TABELA: logs_erro")
    except Exception as e:
        print(f"Erro ao salvar o registro de ERRO DE AUTHENTICAÇAO: {e}")


def registrar_envio_sucesso(remetente, destinatario, senha_app, assunto, corpo):
    try:
        conn = open_connect()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO emails (remetente, destinatario, senha_app, assunto, corpo, data_hora) VALUES (?, ?, ?, ?, ?, ?)",
                (remetente, destinatario, senha_app, assunto, corpo, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            
            conn.commit()
            conn.close()
            print(f"ENVIO REGISTRADO NO BANCO: {destinatario}")
    except Exception as e:
        print(f"Erro ao salvar registro de sucesso: {e}")


@app.route('/api/enviar/email', methods=['POST'])
def enviar_email():
    data = request.get_json()
    email_destino = data.get('destinatario')

    try:
        senha = AUTH_KEY

        msg = MIMEMultipart()
        msg['From'] = EMAIL_SISTEMA
        msg['To'] = email_destino
        msg['Subject'] = data.get('assunto')
        
        corpo = data.get('corpo')
        msg.attach(MIMEText(corpo, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()      
        server.starttls() 
        server.ehlo()          
        server.login(EMAIL_SISTEMA, senha)
        server.send_message(msg)
        server.quit()

        rementente = EMAIL_SISTEMA
        senha_app = senha
        destinatario = email_destino
        
        registrar_envio_sucesso(rementente, destinatario, senha_app, data.get('assunto'), data.get('corpo'))

        return jsonify({"sucesso": "Email enviado com sucesso"}), 200
    

    except smtplib.SMTPAuthenticationError:
        erro_msg = "Credenciais de remetente inválidas.."
        registrar_erro("Erro de Autenticação", erro_msg, EMAIL_SISTEMA)
        return jsonify({"erro": erro_msg}), 401
        
    except Exception as e:
        erro_msg = f"Falha na operação: {str(e)}"
        registrar_erro("Erro Geral", erro_msg, EMAIL_SISTEMA)
        return jsonify({"erro": erro_msg}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=2200)