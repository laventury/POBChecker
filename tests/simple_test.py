#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo: simple_test.py
Teste simples para verificar se o sistema está funcionando
"""

import sys
import os

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Testa as importações básicas"""
    print("Testando importações...")
    
    try:
        from config import QR_EVENT_CODE
        print("✓ Config importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar config: {e}")
        return False
    
    try:
        from database import Database
        print("✓ Database importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar database: {e}")
        return False
    
    try:
        import camera_manager
        print("✓ Camera manager importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar camera_manager: {e}")
        return False
    
    try:
        import audio_manager
        print("✓ Audio manager importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar audio_manager: {e}")
        return False
    
    return True

def test_files():
    """Testa se os arquivos principais existem"""
    print("\nTestando arquivos...")
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files_to_check = [
        "pobchecker_terminal.py",
        "demo_system.py", 
        "database.py",
        "config.py",
        "requirements.txt"
    ]
    
    all_good = True
    for file_name in files_to_check:
        file_path = os.path.join(root_dir, file_name)
        if os.path.exists(file_path):
            print(f"✓ {file_name} encontrado")
        else:
            print(f"✗ {file_name} não encontrado")
            all_good = False
    
    return all_good

def test_database():
    """Testa funcionalidade básica do banco"""
    print("\nTestando banco de dados...")
    
    try:
        from database import Database
        
        # Cria um banco temporário
        test_db = Database("test_temp.sqlite3")
        print("✓ Banco de teste criado")
        
        # Testa adicionar pessoa
        result = test_db.add_person("12345678900", "Teste Silva", 1)
        if result:
            print("✓ Pessoa adicionada com sucesso")
        else:
            print("✗ Erro ao adicionar pessoa")
            return False
        
        # Testa buscar pessoa
        person = test_db.get_person("12345678900")
        if person:
            print("✓ Pessoa encontrada no banco")
        else:
            print("✗ Pessoa não encontrada")
            return False
        
        # Limpa o arquivo de teste
        test_db.close()
        if os.path.exists("test_temp.sqlite3"):
            os.remove("test_temp.sqlite3")
            print("✓ Arquivo de teste removido")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro no teste de banco: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 50)
    print("POBCHECKER - TESTE SIMPLES")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    if test_imports():
        tests_passed += 1
    
    if test_files():
        tests_passed += 1
    
    if test_database():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print("RESULTADO DOS TESTES")
    print("=" * 50)
    print(f"Testes aprovados: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✓ Todos os testes passaram!")
        return 0
    else:
        print("✗ Alguns testes falharam")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
