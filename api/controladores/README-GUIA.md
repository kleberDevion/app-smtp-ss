# SS — Arquitetura de Controladores

## Estrutura

```
api/
├── app.py                          # Rotas + inicialização do servidor
├── SMTPmain.py                     # Servidor de envio simplificado
├── SSbanco.db
└── controladores/
    ├── controle_usuario.pool       # Lógica de usuário
        ├── db_controle.pool            # Conexão com banco
            ├── envio_de_email.pool         # Lógica de envio e busca de emails
                └── envios_de_dados.pool        # Logs e dados auxiliares
                ```

                ---

                ## O que cada controlador faz e o que precisa

                ### `db_controle.pool`
                Responsável pela conexão com o banco de dados.

                Imports necessários: `sqlite3`, variável `ROUTE_DB` do `.env`

                Funções: `get_db_connection`

                ---

                ### `controle_usuario.pool`
                Responsável por tudo relacionado a usuário — criação, login e validação de token.

                Imports necessários: `jwt`, `werkzeug`, `smtplib`, `MIMEMultipart`, `MIMEText`, `os`, `datetime`, `timedelta`, `get_db_connection`

                Funções: `verifica_token`, `criar_user`, `login`

                ---

                ### `envio_de_email.pool`
                Responsável pelo envio de emails e consulta da caixa de entrada.

                Imports necessários: `smtplib`, `MIMEMultipart`, `MIMEText`, `sqlite3`, `datetime`, `get_db_connection`

                Funções: `postar_envios`, `buscar_envios`, `buscar_inbox`, `grafico_tabela`, `pesquisa_tabela`, `deletar_item`

                ---

                ### `envios_de_dados.pool`
                Responsável pelos logs de erro e dados auxiliares.

                Imports necessários: `get_db_connection`, `datetime`

                Funções: `registrar_erro`, `trazer_logs`, `deletar_falha`

                ---

                ## O que fica no `app.py`

                Imports: `Flask`, `CORS`, `request`, `jsonify`, `send_from_directory`, `make_response`, `load_dotenv`, `os`

                Imports dos controladores: todos os 4 acima

                Responsabilidade: declaração das rotas chamando as funções dos controladores, e `app.run()` dentro do `if __name__ == '__main__'`

                ---

                ## Regra geral

                Nenhuma lógica de negócio fica no `app.py`. Ele só recebe a requisição, chama o controlador certo e devolve a resposta.
                