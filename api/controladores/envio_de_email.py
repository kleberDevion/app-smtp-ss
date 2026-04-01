import os
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import jsonify
from dotenv import load_dotenv
from controladores.db_controle import db_connection, registrar_erro

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def envio_email(data):
    """
    Função para processar o envio de e-mails via SMTP e registrar no banco de dados.
    """
    # Validação básica dos campos obrigatórios no dicionário 'data'
    required_fields = ["destinatario", "assunto", "corpo"]
    if not all(field in data for field in required_fields):
        return jsonify({"erro": "Erro no formato dos seus dados!!."}), 400

    try:
        # Configuração da mensagem
        msg = MIMEMultipart()
        msg['From'] = os.getenv('EMAIL_SISTEMA')
        msg['To'] = data.get('destinatario')
        msg['Subject'] = data.get('assunto')
        msg.attach(MIMEText(data.get('corpo'), 'plain'))

        # Configuração e conexão com o servidor SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(os.getenv('EMAIL_SISTEMA'), os.getenv('SENHA_ENVIO'))
        server.send_message(msg)
        server.quit()

        # Log de sucesso no console
        print(f"ENVIO DE EMAIL BEM SUCEDIDO: DESTINO {data.get('destinatario')} em {datetime.now(timezone.utc).isoformat()}")

        # Persistência no banco de dados
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO emails (remetente, destinatario, senha_app, assunto, corpo, data_envio) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                os.getenv('EMAIL_SISTEMA'), 
                data.get('destinatario'), 
                os.getenv('SENHA_ENVIO'), 
                data.get('assunto'), 
                data.get('corpo'), 
                datetime.now(timezone.utc).isoformat()
            )
        )
        conn.commit()
        conn.close()

        return jsonify({"sucesso": f"Email enviado para {data.get('destinatario')}"}), 200
        
    except smtplib.SMTPAuthenticationError:
        erro_msg = "Credenciais de remetente inválidas.."
        registrar_erro("Erro de Autenticação", erro_msg, data.get('destinatario'))
        return jsonify({"erro": erro_msg}), 401

    except Exception as e:
        erro_msg = f"Falha na operação: {str(e)}"
        registrar_erro("Erro Geral", erro_msg, data.get('destinatario'))
        return jsonify({"erro": erro_msg}), 500

if __name__ == "__main__":
    # O código original sugere a execução de um arquivo principal
    print("Servidor de e-mail carregado. Aguardando chamadas da API...")