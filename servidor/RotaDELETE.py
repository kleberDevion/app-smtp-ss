import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

def deletar_item(id_item):
    conn = None
    try:
        conn = sqlite3.connect('SSbanco.db')
        cursor = conn.cursor()

        # Verifica se o item existe antes de deletar
        cursor.execute("SELECT 1 FROM emails WHERE id = ?", (id_item,))
        if cursor.fetchone() is None:
            return {"erro": "Item não existe na tabela de dados.."}, 404

        # Executa a deleção
        cursor.execute("DELETE FROM emails WHERE id = ?", (id_item,))
        conn.commit()
        return True, 200
    except Exception as e:
        return {"erro": "Erro ao receber ID para atualizar as informações.."}, 400
    finally:
        if conn:
            conn.close()

@app.route('/api/deletar/<int:id>', methods=['DELETE'])
def route_delete(id):
    resultado, status_code = deletar_item(id)

    if isinstance(resultado, bool) and resultado:
        return jsonify({"success": True}), 200
    else:
        return jsonify(resultado), status_code

if __name__ == '__main__':
    app.run()
