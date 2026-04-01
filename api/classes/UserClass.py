class UserProfile:
    def __init__(self, nome, email, senha):
        self.nome = str(nome)
        self.email = str(email)
        self.senha = str(senha)

    def validate_data(self, data):
        """
        Compara os itens de um dicionário ou objeto 'data' com os valores do perfil.
        """
        profile_values = [self.nome, self.email, self.senha]
        
        # Tenta acessar .items() se for um dicionário, caso contrário usa o atributo direto
        data_items = data.items() if hasattr(data, 'items') else data.items

        if data_items == profile_values:
            return None
        else:
            return False