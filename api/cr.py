import glob
import subprocess

def run_files():
    user_input = input('EXECUTE OS SERVERS: ~$ ')
    
    if user_input.strip().lower() == "run":
        # Busca os arquivos seguindo o padrão de globbing
        files_to_run = glob.glob('**/api/server-chat.py', recursive=True)
        
        # Executa cada arquivo encontrado usando o interpretador python
        for file in files_to_run:
            try:
                subprocess.run(['python', file], check=True)
            except Exception as e:
                print(f"Erro ao executar {file}: {e}")
        
        return None

if __name__ == "__main__":
    run_files()