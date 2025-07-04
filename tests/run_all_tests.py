#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo: run_all_tests.py
Executa todos os testes do sistema POBChecker
"""

import sys
import os
from datetime import datetime

# Adiciona o diretório pai ao path para importar os módulos do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("Testando importações dos módulos...")
    tests_passed = 0
    total_tests = 4
    
    try:
        from config import QR_EVENT_CODE, AUTO_CLEANUP_MONTHS, DEFAULT_MODE
        print("✓ Config importado com sucesso")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Erro ao importar config: {e}")
    
    try:
        from database import Database
        print("✓ Database importado com sucesso")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Erro ao importar database: {e}")
    
    try:
        import camera_manager
        print("✓ Camera manager importado com sucesso")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Erro ao importar camera_manager: {e}")
    
    try:
        import audio_manager
        print("✓ Audio manager importado com sucesso")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Erro ao importar audio_manager: {e}")
    
    return tests_passed, total_tests

def test_file_structure():
    """Testa se os arquivos principais existem"""
    print("\nTestando estrutura de arquivos...")
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_files = [
        "pobchecker_terminal.py",
        "demo_system.py",
        "database.py",
        "config.py",
        "camera_manager.py",
        "audio_manager.py",
        "requirements.txt"
    ]
    
    tests_passed = 0
    for file_name in main_files:
        file_path = os.path.join(root_dir, file_name)
        if os.path.exists(file_path):
            print(f"✓ {file_name} encontrado")
            tests_passed += 1
        else:
            print(f"✗ {file_name} não encontrado")
    
    # Verifica diretórios
    directories = ["helper", "qrcodes_cpf"]
    for dir_name in directories:
        dir_path = os.path.join(root_dir, dir_name)
        if os.path.exists(dir_path):
            print(f"✓ Diretório {dir_name}/ encontrado")
            tests_passed += 1
        else:
            print(f"✗ Diretório {dir_name}/ não encontrado")
    
    return tests_passed, len(main_files) + len(directories)

def test_database_functionality():
    """Testa funcionalidades básicas do banco de dados"""
    print("\nTestando funcionalidades do banco de dados...")
    
    try:
        from database import Database
        
        # Cria um banco temporário para teste
        test_db_file = "test_temp_pobchecker.sqlite3"
        db = Database(test_db_file)
        tests_passed = 0
        total_tests = 4
        
        # Teste 1: Adição de pessoa
        try:
            result = db.add_person_to_pob("12345678901", "João Teste", 1)
            if result:
                print("✓ Adição de pessoa funcionando")
                tests_passed += 1
            else:
                print("✗ Falha na adição de pessoa")
        except Exception as e:
            print(f"✗ Erro na adição de pessoa: {e}")
        
        # Teste 2: Busca de pessoa
        try:
            person = db.find_person_by_cpf("12345678901")
            if person and person[1] == "João Teste":
                print("✓ Busca de pessoa funcionando")
                tests_passed += 1
            else:
                print("✗ Falha na busca de pessoa")
        except Exception as e:
            print(f"✗ Erro na busca de pessoa: {e}")
        
        # Teste 3: Validação de CPF
        try:
            valid_cpf = db.validate_cpf("12345678901")
            if valid_cpf:
                print("✓ Validação de CPF funcionando")
                tests_passed += 1
            else:
                print("✗ Falha na validação de CPF")
        except Exception as e:
            print(f"✗ Erro na validação de CPF: {e}")
        
        # Teste 4: Limpeza de CPF
        try:
            cleaned = db.clean_cpf("123.456.789-01")
            if cleaned == "12345678901":
                print("✓ Limpeza de CPF funcionando")
                tests_passed += 1
            else:
                print("✗ Falha na limpeza de CPF")
        except Exception as e:
            print(f"✗ Erro na limpeza de CPF: {e}")
        
        # Limpa o arquivo de teste
        db.conn.close()
        if os.path.exists(test_db_file):
            os.remove(test_db_file)
        
        return tests_passed, total_tests
        
    except Exception as e:
        print(f"✗ Erro geral no teste de banco: {e}")
        return 0, 4

def test_config_values():
    """Testa se as configurações estão corretas"""
    print("\nTestando valores de configuração...")
    
    try:
        from config import QR_EVENT_CODE, AUTO_CLEANUP_MONTHS, DEFAULT_MODE
        tests_passed = 0
        total_tests = 3
        
        if isinstance(QR_EVENT_CODE, str) and len(QR_EVENT_CODE) > 0:
            print("✓ QR_EVENT_CODE está correto")
            tests_passed += 1
        else:
            print("✗ QR_EVENT_CODE inválido")
        
        if isinstance(AUTO_CLEANUP_MONTHS, int) and AUTO_CLEANUP_MONTHS > 0:
            print("✓ AUTO_CLEANUP_MONTHS está correto")
            tests_passed += 1
        else:
            print("✗ AUTO_CLEANUP_MONTHS inválido")
        
        if DEFAULT_MODE in ["CIO", "CEV"]:
            print("✓ DEFAULT_MODE está correto")
            tests_passed += 1
        else:
            print("✗ DEFAULT_MODE inválido")
        
        return tests_passed, total_tests
        
    except Exception as e:
        print(f"✗ Erro ao testar configurações: {e}")
        return 0, 3

def run_all_tests():
    """Executa todos os testes"""
    print("=" * 60)
    print("POBCHECKER - EXECUÇÃO DE TESTES")
    print("=" * 60)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    total_passed = 0
    total_tests = 0
    
    # Executa todos os testes
    test_functions = [
        test_imports,
        test_file_structure,
        test_database_functionality,
        test_config_values
    ]
    
    for test_func in test_functions:
        passed, total = test_func()
        total_passed += passed
        total_tests += total
    
    # Resumo
    print()
    print("=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    print(f"Total de testes: {total_tests}")
    print(f"Sucessos: {total_passed}")
    print(f"Falhas: {total_tests - total_passed}")
    
    success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
    print(f"Taxa de sucesso: {success_rate:.1f}%")
    
    if total_passed == total_tests:
        print("\n🎉 Todos os testes passaram!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} testes falharam")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    print("\nTestes concluídos.")
    sys.exit(exit_code)
