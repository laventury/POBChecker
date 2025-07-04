# -*- coding: utf-8 -*-
# Arquivo: demo_system.py - Demonstração do sistema POBChecker reorganizado

import os
import subprocess
import sys

def show_menu():
    """Mostra o menu de opções"""
    print("\n" + "=" * 60)
    print("POBCHECKER - SISTEMA REORGANIZADO - MENU DEMO")
    print("=" * 60)
    print("1. Executar POBChecker Terminal (Script Principal)")
    print("2. Gerar novos QR Codes (formato CPF|Nome)")
    print("3. Visualizar QR Codes gerados")
    print("4. Testar Sistema (tests)")
    print("5. Limpar dados de teste")
    print("6. Popular banco com dados de teste")
    print("0. Sair")
    print("=" * 60)

def run_pobchecker_terminal():
    """Executa o script principal do POBChecker"""
    print("Executando POBChecker Terminal (script principal)...")
    try:
        subprocess.run([sys.executable, "pobchecker_terminal.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar: {e}")
    except KeyboardInterrupt:
        print("Execução interrompida pelo usuário")

def generate_qrcodes():
    """Gera QR Codes usando o helper"""
    print("Gerando QR Codes com formato CPF|Nome...")
    try:
        subprocess.run([sys.executable, "helper/helper_generate_qrcodes.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao gerar QR Codes: {e}")

def show_qrcodes():
    """Mostra informações sobre QR Codes gerados"""
    qr_folder = "qrcodes_cpf"
    if os.path.exists(qr_folder):
        files = [f for f in os.listdir(qr_folder) if f.endswith('.png')]
        print(f"\nQR Codes encontrados ({len(files)} arquivos):")
        for i, file in enumerate(files[:10], 1):  # Mostra apenas os primeiros 10
            print(f"  {i}. {file}")
        if len(files) > 10:
            print(f"  ... e mais {len(files) - 10} arquivos")
        print(f"\nLocal: {os.path.abspath(qr_folder)}")
        print("Formato dos QR Codes: CPF|NOME")
        
        # Tenta abrir a pasta no Windows
        try:
            os.startfile(qr_folder)
            print("Pasta aberta no explorador de arquivos")
        except:
            print("Para visualizar os QR Codes, acesse a pasta qrcodes_cpf/")
    else:
        print("Pasta de QR Codes não encontrada. Execute primeiro a opção 2.")

def show_qrcodes():
    """Mostra informações sobre QR Codes gerados"""
    qr_folder = "qrcodes_cpf"
    if os.path.exists(qr_folder):
        files = [f for f in os.listdir(qr_folder) if f.endswith('.png')]
        print(f"\nQR Codes encontrados ({len(files)} arquivos):")
        for i, file in enumerate(files[:10], 1):  # Mostra apenas os primeiros 10
            print(f"  {i}. {file}")
        if len(files) > 10:
            print(f"  ... e mais {len(files) - 10} arquivos")
        print(f"\nLocal: {os.path.abspath(qr_folder)}")
        print("Formato dos QR Codes: CPF|NOME")
        
        # Tenta abrir a pasta no Windows
        try:
            os.startfile(qr_folder)
            print("Pasta aberta no explorador de arquivos")
        except:
            print("Para visualizar os QR Codes, acesse a pasta qrcodes_cpf/")
    else:
        print("Pasta de QR Codes não encontrada. Execute primeiro a opção 2.")

def run_tests():
    """Executa testes do sistema"""
    print("Executando testes do sistema...")
    try:
        subprocess.run([sys.executable, "tests/run_all_tests.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro nos testes: {e}")

def clear_test_data():
    """Limpa dados de teste"""
    print("Limpando dados de teste...")
    try:
        subprocess.run([sys.executable, "helper/helper_clear_data.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao limpar dados: {e}")

def populate_test_data():
    """Popula banco com dados de teste"""
    print("Populando banco com dados de teste...")
    try:
        subprocess.run([sys.executable, "helper/helper_pob_generate.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao popular dados: {e}")

def main():
    """Função principal"""
    print("POBCHECKER - SISTEMA DE CONTROLE POB v2.0 - REORGANIZADO")
    print("Arquivos principais:")
    print("- pobchecker_terminal.py (script principal)")
    print("- helper/helper_generate_qrcodes.py (geração de QR codes)")
    print("- Removidos: main_launcher.py, personnel_manager.py")
    
    while True:
        show_menu()
        
        try:
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "0":
                print("Saindo...")
                break
            elif choice == "1":
                run_pobchecker_terminal()
            elif choice == "2":
                generate_qrcodes()
            elif choice == "3":
                show_qrcodes()
            elif choice == "4":
                run_tests()
            elif choice == "5":
                clear_test_data()
            elif choice == "6":
                populate_test_data()
            else:
                print("Opção inválida. Tente novamente.")
                
        except KeyboardInterrupt:
            print("\n\nSaindo...")
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()
