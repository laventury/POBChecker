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

def main():
    """Função principal para executar testes"""
    print("🧪 POBChecker - Sistema de Testes")
    print("=" * 50)
    
    try:
        # Importa e executa sistema completo de testes
        from test_system import run_all_tests
        
        print("Executando sistema completo de testes...")
        result = run_all_tests()
        
        # Código de saída baseado no resultado
        if result['failed'] > 0:
            sys.exit(1)  # Falha
        elif result['skipped'] > 0:
            sys.exit(2)  # Parcialmente executado
        else:
            sys.exit(0)  # Sucesso
            
    except ImportError as e:
        print(f"❌ Erro ao importar sistema de testes: {e}")
        print("Executando testes básicos...")
        
        # Fallback para testes básicos
        run_basic_tests()
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

def run_basic_tests():
    """Executa testes básicos se sistema completo não estiver disponível"""
    print("\n📋 Executando testes básicos:")
    print("-" * 30)
    
    tests_passed = 0
    total_tests = 0
    
    # Teste de importações básicas
    print("1. Testando importações básicas...")
    total_tests += 1
    
    try:
        from config import QR_EVENT_CODE, DEFAULT_MODE
        from database import Database
        import camera_manager
        import audio_manager
        print("   ✅ Importações básicas OK")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Falha nas importações: {e}")
    
    # Teste de banco de dados
    print("2. Testando banco de dados...")
    total_tests += 1
    
    try:
        import tempfile
        import sqlite3
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_file = f.name
        
        try:
            db = Database(db_file)
            
            # Verifica tabelas
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            expected_tables = ['POB', 'EVENTS', 'CHECK_EVENT', 'CHECK_IN_OUT']
            if all(table in tables for table in expected_tables):
                print("   ✅ Banco de dados OK")
                tests_passed += 1
            else:
                print("   ❌ Tabelas faltando no banco")
                
        finally:
            os.unlink(db_file)
            
    except Exception as e:
        print(f"   ❌ Falha no banco: {e}")
    
    # Teste de arquivos de configuração
    print("3. Testando arquivos de configuração...")
    total_tests += 1
    
    try:
        config_files = ['terminal_config.json', 'consolidator_config.json']
        config_ok = True
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    import json
                    with open(config_file, 'r') as f:
                        json.load(f)
                except json.JSONDecodeError:
                    config_ok = False
                    break
        
        if config_ok:
            print("   ✅ Arquivos de configuração OK")
            tests_passed += 1
        else:
            print("   ❌ Erro nos arquivos de configuração")
            
    except Exception as e:
        print(f"   ❌ Falha na configuração: {e}")
    
    # Teste de funcionalidades de rede (opcional)
    print("4. Testando funcionalidades de rede...")
    total_tests += 1
    
    try:
        from sync_service import SyncService
        from time_sync import TimeSync
        from discovery import ServiceDiscovery
        print("   ✅ Funcionalidades de rede OK")
        tests_passed += 1
    except ImportError:
        print("   ⚠️  Funcionalidades de rede não disponíveis (opcional)")
        tests_passed += 1  # Conta como sucesso pois é opcional
    except Exception as e:
        print(f"   ❌ Erro nas funcionalidades de rede: {e}")
    
    # Relatório final
    print("\n" + "=" * 50)
    print("📊 RELATÓRIO BÁSICO")
    print("=" * 50)
    
    success_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total de testes: {total_tests}")
    print(f"Passou: {tests_passed} ✅")
    print(f"Falhou: {total_tests - tests_passed} ❌")
    print(f"Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate >= 75:
        print("\n✅ Sistema básico funcionando!")
    else:
        print("\n❌ Sistema tem problemas básicos")
    
    print("\n💡 Para testes completos, instale as dependências:")
    print("   pip install -r requirements_network.txt")
    print("   python tests/test_system.py")


if __name__ == "__main__":
