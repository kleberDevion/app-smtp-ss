import os
import smtplib
import jwt
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart

from email.mime.text import MIMEText
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify

# Importações presumidas do ambiente do usuário
from controladores.db_controle import db_connection
from classes.UserClass import UserProfile
from .validador_dados import validate_email

load_dotenv()

DB_PATH = os.getenv('DB_PATH')
EMAIL_SISTEMA = os.getenv('EMAIL_SISTEMA')
SENHA_ENVIO = os.getenv('SENHA_ENVIO')
SECRET_KEY = os.getenv('SECRET_WORD')

def criar_users(data):
    result = UserProfile(email=data['email'], senha=data['senha'], nome=data['nome'])
    erro_msg = "Erro interno no servidor...."

    if result is False:
        return jsonify({"erro": "Erro no formato dos seus dados!!."}), 400

    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    # Validação de email
    email_validate = validate_email(email)
    if not email_validate:
        return jsonify({"erro": "Seu email e invalido"}), 405

    try:
        conn = db_connection()
        cursor = conn.cursor()

        # Hash da senha
        senha_hash = generate_password_hash(senha)

        # Verificar se usuário já existe
        cursor.execute("SELECT id FROM usuarios WHERE nome = ? OR email = ?", (nome, email))
        existe = cursor.fetchone()

        if existe:
            conn.close()
            return jsonify({"erro": "Nome de usuario e email ja estao em uso"}), 409

        # Inserir novo usuário
        cursor.execute(
            "INSERT INTO usuarios (nome, senha, data_criacao, email) VALUES (?, ?, ?, ?)",
            (nome, senha_hash, datetime.now(), email)
        )
        conn.commit()
        conn.close()

        # Envio de Email de Boas-vindas
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_SISTEMA
            msg['To'] = email
            msg['Subject'] = "Email de nota de cadastro no app 'SS-Sender'"

            with open('templates/nota-aviso-login.html', 'r', encoding='utf-8') as file:
                html_body = file.read()

            html_body = html_body.replace("{{nome}}", nome)
            msg.attach(MIMEText(html_body, 'html'))

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(EMAIL_SISTEMA, SENHA_ENVIO)
                server.send_message(msg)
        except Exception as e:
            print(f"USUARIO CRIADO: EXCEPT ERROR SEND MAIL WELCOME: {e}")

        return jsonify({"status": "sucesso", "mensagem": "Usuário criado com sucesso"}), 201

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"erro": erro_msg}), 500

def logar_user(data):
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, nome, senha, email FROM usuarios WHERE nome = ? AND email = ?", (nome, email)
    )
    usuario = cursor.fetchone()
    conn.close()

    if usuario and check_password_hash(usuario[2], senha):
        payload = {
            "usuario_id": usuario[0],
            "email": usuario[3],
            "exp": datetime.utcnow() + timedelta(hours=12)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            "status": "sucesso",
            "mensagem": "Login realizado!",
            "usuario_id": usuario[0],
            "nome": usuario[1],
            "email": usuario[3],
            "token": token
        }), 200

    return jsonify({"erro": "Nome ou senha incorretos"}), 401

if __name__ == "__main__":
    # O código seria iniciado aqui se fosse um app Flask completo
    pass