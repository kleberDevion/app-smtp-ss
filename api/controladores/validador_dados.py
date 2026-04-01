import re

def validate_email(email):
    """
    Valida se o formato do e-mail é válido usando regex.
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_assunto(assunto):
    """
    Valida se o assunto contém apenas caracteres alfanuméricos e espaços.
    """
    pattern = r'^[A-Za-z0-9\s]+$'
    return re.match(pattern, assunto) is not None

if __name__ == "__main__":
    # Exemplo de uso das funções validadoras
    test_email = "exemplo@dominio.com"
    test_assunto = "Assunto 123"
    
    print(f"E-mail válido: {validate_email(test_email)}")
    print(f"Assunto válido: {validate_assunto(test_assunto)}")