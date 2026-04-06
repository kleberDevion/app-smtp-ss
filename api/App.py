import sqlite3
import smtplib
import re
import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS

# Importações dos controladores locais
from controladores.controle_usuario import criar_users, logar_user
from controladores.envio_de_email import envio_email
from controladores.dados_manager import (
    dashboard_main_dados, 
    inbox_mail_dados, 
    contar_falhas, 
    contar_total, 
    grafico_enviados, 
    trazer_logs, 
    deletar_item, 
    deletar_falha
)

app = Flask(__name__)
CORS(app, resources={r"/ss/*": {"origins": "*"}})

# Definição de métodos permitidos baseada na lógica 'permiser'
ALLOWED_METHODS = ['POST', 'GET', 'DELETE']

def check_method():
    if request.method not in ALLOWED_METHODS:
        return jsonify({"erro": "Erro, tipo de requisiçao nao aceita"}), 405
    return None

@app.route('/', methods=['GET'])
def index():
    return jsonify({"ola": "Conexao estabelecida com o servidor"}), 200

@app.route('/ss/criar/usuario', methods=['POST'])
def rota_criar_usuario():
    method_check = check_method()
    if method_check: return method_check
    
    data = request.get_json()
    print(f"REQUISIÇÃO ROTA: 'POST' : {datetime.now()}")
    
    result = criar_users(data)
    return result

@app.route('/ss/logar/usuario', methods=['POST'])
def rota_logar_usuario():
    method_check = check_method()
    if method_check: return method_check
    
    data = request.get_json()
    print(f"REQUISIÇÃO ROTA: 'POST' /ss/logar/usuario : {datetime.now()}")
    
    result = logar_user(data)
    return result

@app.route('/ss/enviar/email', methods=['POST'])
def rota_enviar_email():
    method_check = check_method()
    if method_check: return method_check
    
    data = request.get_json()
    print(f"REQUISIÇÃO ROTA: 'POST' /ss/enviar/email : {datetime.now()}")
    
    result = envio_email(data)
    return result

@app.route('/ss/buscar/envios', methods=['GET'])
def rota_buscar_envios():
    method_check = check_method()
    if method_check: return method_check
    
    print(f"REQUISIÇÃO ROTA: 'GET' /ss/buscar/envios : {datetime.now()}")
    
    result = dashboard_main_dados()
    return result

@app.route('/ss/inbox', methods=['GET'])
def rota_inbox():
    method_check = check_method()
    if method_check: return method_check
    
    print(f"REQUISIÇÃO ROTA: 'GET' /ss/inbox : {datetime.now()}")
    
    result = inbox_mail_dados()
    return result

@app.route('/ss/contar/falhas', methods=['GET'])
def rota_contar_falhas():
    method_check = check_method()
    if method_check: return method_check
    
    print(f"REQUISIÇÃO ROTA: 'GET' /ss/contar/falhas : {datetime.now()}")
    
    result = contar_falhas()
    return result

@app.route('/ss/contar/total', methods=['GET'])
def rota_contar_total():
    method_check = check_method()
    if method_check: return method_check
    
    print(f"REQUISIÇÃO ROTA: 'GET' /ss/contar/total : {datetime.now()}")
    
    result = contar_total()
    return result

@app.route('/ss/grafico/enviados', methods=['GET'])
def rota_grafico_enviados():
    method_check = check_method()
    if method_check: return method_check
    
    print(f"REQUISIÇÃO ROTA: 'GET' /ss/grafico/enviados : {datetime.now()}")
    
    result = grafico_enviados()
    return result

@app.route('/ss/trazer/logs_erro', methods=['GET'])
def rota_trazer_logs():
    method_check = check_method()
    if method_check: return method_check
    
    print(f"REQUISIÇÃO ROTA: 'GET' /ss/trazer/logs_erro : {datetime.now()}")
    
    result = trazer_logs()
    return result

@app.route('/ss/deletar/envio/<int:id>', methods=['DELETE'])
def rota_deletar_envio(id):
    method_check = check_method()
    if method_check: return method_check
    
    print(f"REQUISIÇÃO ROTA: 'DELETE' /ss/deletar/envio : {datetime.now()}")
    
    result = deletar_item(id)
    return result

@app.route('/ss/deletar/falhas/<int:id>', methods=['DELETE'])
def rota_deletar_falhas(id):
    method_check = check_method()
    if method_check: return method_check
    
    print(f"REQUISIÇÃO ROTA: 'DELETE' /ss/deletar/falhas : {datetime.now()}")
    
    result = deletar_falha(id)
    return result

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5500)