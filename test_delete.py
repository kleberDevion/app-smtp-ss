import requests
import json

# Testando a rota DELETE
try:
    print("Testando DELETE na porta 5001...")
    response = requests.delete('http://localhost:5001/api/deletar/1', 
                              headers={'Content-Type': 'application/json'})
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
except Exception as e:
    print(f"Erro: {str(e)}")
    print("O servidor pode não estar rodando na porta 5001")
