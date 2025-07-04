# Arquivo: helper_generate_qrcodes.py - Helper para geração de QR Codes

import sqlite3
import qrcode
import os
import re
from config import QR_EVENT_CODE

# --- Configurações ---
DATABASE_FILE = "pobchecker.sqlite3"
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

def create_qr_event():
    """
    Gera o QR Code especial QR_EVENT para ativar/desativar o modo CEV.
    """
    print("Gerando QR Code especial QR_EVENT...")
    
    # Cria a pasta de saída se não existir
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # Nome do arquivo para o QR_EVENT
    filename = "QR_EVENT_CONTROL.png"
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    
    # Configuração do QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # Correção média para maior confiabilidade
        box_size=12,  # Tamanho maior para melhor leitura
        border=6,     # Borda maior para destaque
    )
    
    # Adiciona o código especial
    qr.add_data(QR_EVENT_CODE)
    qr.make(fit=True)
    
    # Cria a imagem do QR Code com cores diferentes para destaque
    img = qr.make_image(fill_color="red", back_color="white")
    
    # Salva a imagem
    img.save(filepath)
    
    print(f"  -> QR_EVENT gerado: {filename}")
    print(f"  -> Código: {QR_EVENT_CODE}")
    print(f"  -> Função: Ativar/Desativar modo CEV (Check Event)")
    
    return filepath

if __name__ == "__main__":
    create_qrcodes()
    create_qr_event()