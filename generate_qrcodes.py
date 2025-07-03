# Arquivo: generate_qrcodes.py

import sqlite3
import qrcode
import os
import re

# --- Configurações ---
DATABASE_FILE = "pob_db.sqlite3"
OUTPUT_FOLDER = "qrcodes_cpf"

def sanitize_filename(name):
    """
    Limpa o nome para ser usado como um nome de arquivo seguro.
    Remove caracteres inválidos e substitui espaços por underscores.
    """
    # Substitui espaços por underscores
    name = name.replace(" ", "_")
    # Remove qualquer caractere que não seja letra, número, underscore ou hífen
    name = re.sub(r'[^a-zA-Z0-9_-]', '', name)
    return name

def create_qrcodes():
    """
    Função principal para ler o banco de dados e gerar os QR Codes.
    QR Codes agora contêm CPF|Nome para melhor identificação.
    """
    print("Iniciando a geração de QR Codes...")

    # 1. Verifica se o arquivo de banco de dados existe
    if not os.path.exists(DATABASE_FILE):
        print(f"Erro: O arquivo de banco de dados '{DATABASE_FILE}' não foi encontrado.")
        print("Por favor, execute o script 'pob_test_data.py' primeiro para criar e popular o banco.")
        return

    # 2. Cria a pasta de saída para os QR Codes, se ela não existir
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print(f"Salvando os arquivos na pasta: '{OUTPUT_FOLDER}/'")

    # 3. Conecta ao banco de dados e busca os dados
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT Nome, CPF FROM POB")
        people = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao ler o banco de dados: {e}")
        conn.close()
        return
        
    conn.close()
    
    if not people:
        print("Nenhuma pessoa encontrada no banco de dados.")
        return

    # 4. Itera sobre cada pessoa e cria o QR Code
    count = 0
    for person in people:
        nome, cpf = person
        
        # Cria um nome de arquivo limpo e seguro
        filename = f"{sanitize_filename(nome)}_{cpf}.png"
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        
        # Configuração do QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Adiciona o dado no formato CPF|NOME ao QR Code
        qr_data = f"{cpf}|{nome}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Cria a imagem do QR Code
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Salva a imagem no arquivo
        img.save(filepath)
        
        print(f"  -> Gerado QR Code para: {nome} (CPF: {cpf})")
        count += 1

    print(f"\nProcesso concluído! {count} QR Codes foram gerados com sucesso.")
    print("Formato dos QR Codes: CPF|NOME")

if __name__ == "__main__":
    create_qrcodes()