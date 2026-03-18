import smtplib

# COLOQUE SEUS DADOS AQUI PARA TESTE RÁPIDO
EMAIL = "klebersantanadeoliveira07@gmail.com"
SENHA = "pszh wqjm gqjy jixw".replace(" ", "") # Remove os espaços

try:
    print("Conectando ao Gmail...")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    print("Tentando login...")
    server.login(EMAIL, SENHA)
    print("SUCESSO! O login funcionou.")
    server.quit()
except Exception as e:
    print(f"ERRO IDENTIFICADO: {e}")
