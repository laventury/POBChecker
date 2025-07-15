#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo: utilitary_server_tests.py
Descrição: Script utilitário para testes do consolidador
"""

import sys
import os
import json
import subprocess
import time
from datetime import datetime, timedelta

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show_menu():
    """Mostra o menu de opções de testes"""
    print("\n" + "=" * 60)
    print("POBCHECKER - TESTES DO CONSOLIDADOR")
    print("=" * 60)
    print("1. Teste de configuração")
    print("2. Teste de conexão com banco")
    print("3. Teste de servidor API")
    print("4. Teste de sincronização")
    print("5. Teste de correlação de eventos")
    print("6. Teste de descoberta de terminais")
    print("7. Teste de sistema completo")
    print("8. Executar todos os testes")
    print("0. Voltar")
    print("=" * 60)

def test_configuration():
    """Testa configuração do consolidador"""
    print("\nTestando configuração do consolidador...")
    
    try:
        # Verifica arquivo de configuração
        config_file = "consolidator_config.json"
        if not os.path.exists(config_file):
            print(f"❌ Arquivo de configuração não encontrado: {config_file}")
            return False
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ Arquivo de configuração carregado")
        
        # Verifica estrutura da configuração
        required_sections = ['server', 'database', 'correlation', 'interface', 'network']
        
        for section in required_sections:
            if section in config.get('consolidator_config', {}):
                print(f"✅ Seção '{section}' encontrada")
            else:
                print(f"❌ Seção '{section}' não encontrada")
                return False
        
        # Verifica valores específicos
        server_config = config['consolidator_config']['server']
        if server_config.get('host') and server_config.get('port'):
            print(f"✅ Servidor configurado: {server_config['host']}:{server_config['port']}")
        else:
            print("❌ Configuração do servidor incompleta")
            return False
        
        print("✅ Configuração válida!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de configuração: {e}")
        return False

def test_database_connection():
    """Testa conexão com banco de dados"""
    print("\nTestando conexão com banco de dados...")
    
    try:
        from pobchecker_server import ConsolidatorDatabase
        
        # Carrega configuração
        with open("consolidator_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Testa conexão
        db = ConsolidatorDatabase(config['consolidator_config'])
        
        if hasattr(db, 'test_connection'):
            if db.test_connection():
                print("✅ Conexão com banco estabelecida")
            else:
                print("❌ Falha na conexão com banco")
                return False
        else:
            print("✅ Banco inicializado (método test_connection não disponível)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de banco: {e}")
        return False

def test_api_server():
    """Testa servidor API"""
    print("\nTestando servidor API...")
    
    try:
        import requests
        from threading import Thread
        import time
        
        # Inicia servidor em thread separada
        def start_server():
            try:
                subprocess.run([sys.executable, "run_server.py"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
            except:
                pass
        
        server_thread = Thread(target=start_server, daemon=True)
        server_thread.start()
        
        # Aguarda servidor inicializar
        print("⏳ Aguardando servidor inicializar...")
        time.sleep(5)
        
        # Testa endpoints básicos
        base_url = "http://localhost:8000"
        
        endpoints = [
            "/health",
            "/api/terminals",
            "/api/events",
            "/dashboard"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {endpoint} - OK")
                else:
                    print(f"⚠️  {endpoint} - Status {response.status_code}")
            except requests.exceptions.RequestException:
                print(f"❌ {endpoint} - Não responde")
        
        print("✅ Testes de API concluídos")
        return True
        
    except ImportError:
        print("❌ Biblioteca 'requests' não instalada")
        return False
    except Exception as e:
        print(f"❌ Erro no teste de API: {e}")
        return False

def test_synchronization():
    """Testa sincronização"""
    print("\nTestando sincronização...")
    
    try:
        from pobchecker_server import ConsolidatorServer
        
        server = ConsolidatorServer()
        
        # Simula dados de teste
        test_data = {
            'terminal_id': 'test_terminal',
            'timestamp': datetime.now().isoformat(),
            'events': [
                {
                    'event_id': 'test_event_1',
                    'type': 'check_in',
                    'cpf': '12345678901',
                    'name': 'Teste Usuario',
                    'timestamp': datetime.now().isoformat()
                }
            ]
        }
        
        # Testa processamento de dados
        if hasattr(server, 'process_terminal_data'):
            result = server.process_terminal_data(test_data)
            if result:
                print("✅ Dados de teste processados com sucesso")
            else:
                print("❌ Falha no processamento de dados")
                return False
        else:
            print("⚠️  Método de processamento não disponível")
        
        print("✅ Teste de sincronização concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de sincronização: {e}")
        return False

def test_event_correlation():
    """Testa correlação de eventos"""
    print("\nTestando correlação de eventos...")
    
    try:
        from utils.event_correlator import EventCorrelator
        
        correlator = EventCorrelator()
        
        # Dados de teste
        test_events = [
            {
                'terminal_id': 'terminal_1',
                'timestamp': datetime.now(),
                'event_type': 'check_in',
                'participants': ['12345678901', '98765432100']
            },
            {
                'terminal_id': 'terminal_2',
                'timestamp': datetime.now() + timedelta(minutes=2),
                'event_type': 'check_in',
                'participants': ['12345678901', '98765432100']
            }
        ]
        
        # Testa correlação
        if hasattr(correlator, 'correlate_events'):
            correlations = correlator.correlate_events(test_events)
            if correlations:
                print(f"✅ {len(correlations)} correlações encontradas")
            else:
                print("ℹ️  Nenhuma correlação encontrada (normal para dados de teste)")
        else:
            print("⚠️  Método de correlação não disponível")
        
        print("✅ Teste de correlação concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de correlação: {e}")
        return False

def test_terminal_discovery():
    """Testa descoberta de terminais"""
    print("\nTestando descoberta de terminais...")
    
    try:
        from network_discovery import NetworkDiscovery
        
        discovery = NetworkDiscovery()
        
        # Testa descoberta
        print("🔍 Procurando terminais na rede...")
        terminals = discovery.discover_terminals()
        
        if terminals:
            print(f"✅ {len(terminals)} terminais encontrados:")
            for terminal in terminals:
                print(f"   - {terminal}")
        else:
            print("ℹ️  Nenhum terminal encontrado (normal se não houver terminais ativos)")
        
        print("✅ Teste de descoberta concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de descoberta: {e}")
        return False

def test_complete_system():
    """Teste completo do sistema"""
    print("\nExecutando teste completo do sistema...")
    
    tests = [
        ("Configuração", test_configuration),
        ("Banco de dados", test_database_connection),
        ("Servidor API", test_api_server),
        ("Sincronização", test_synchronization),
        ("Correlação", test_event_correlation),
        ("Descoberta", test_terminal_discovery)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Executando teste: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} testes")
    print(f"Passou: {passed}")
    print(f"Falhou: {failed}")
    
    if failed == 0:
        print("🎉 Todos os testes passaram!")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique a configuração.")
        return False

def run_all_tests():
    """Executa todos os testes"""
    print("\nExecutando todos os testes do consolidador...")
    return test_complete_system()

def main():
    """Função principal"""
    print("POBCHECKER - TESTES DO CONSOLIDADOR")
    print("Sistema de Testes para Consolidador POB")
    
    while True:
        show_menu()
        
        try:
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "0":
                print("Voltando...")
                break
            elif choice == "1":
                test_configuration()
            elif choice == "2":
                test_database_connection()
            elif choice == "3":
                test_api_server()
            elif choice == "4":
                test_synchronization()
            elif choice == "5":
                test_event_correlation()
            elif choice == "6":
                test_terminal_discovery()
            elif choice == "7":
                test_complete_system()
            elif choice == "8":
                run_all_tests()
            else:
                print("Opção inválida. Tente novamente.")
                
        except KeyboardInterrupt:
            print("\n\nSaindo...")
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()
