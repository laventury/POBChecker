#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo: utility_manage.py
Descrição: Sistema unificado de gerenciamento de utilitários POBChecker
"""

import os
import subprocess
import sys
import json
import time
from datetime import datetime

def show_main_menu():
    """Mostra o menu principal"""
    print("\n" + "=" * 70)
    print("POBCHECKER - SISTEMA DE GERENCIAMENTO DE UTILITÁRIOS")
    print("=" * 70)
    print("📋 FUNÇÕES GERAIS:")
    print("1. Executar POBChecker Terminal")
    print("2. Inicializar todos os dados")
    print("3. Listar dados do sistema")
    print("4. Gerar QR Codes")
    print("5. Visualizar QR Codes")
    print("6. Executar testes do sistema")
    print("")
    print("🖥️  FUNÇÕES DOS TERMINAIS:")
    print("7. Limpar dados dos terminais")
    print("8. Popular terminais com dados de teste")
    print("9. Gerenciar dados dos terminais")
    print("")
    print("🌐 FUNÇÕES DO CONSOLIDADOR:")
    print("10. Configurar consolidador")
    print("11. Iniciar servidor consolidador")
    print("12. Gerenciar dados do consolidador")
    print("13. Listar dados do consolidador")
    print("14. Executar testes do consolidador")
    print("")
    print("0. Sair")
    print("=" * 70)

def run_pobchecker_terminal():
    """Executa o script principal do POBChecker"""
    print("🚀 Executando POBChecker Terminal...")
    try:
        subprocess.run([sys.executable, "pobchecker_terminal.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar: {e}")
    except KeyboardInterrupt:
        print("⚠️  Execução interrompida pelo usuário")

def initialize_all_data():
    """Inicializa todos os dados do sistema"""
    print("🔄 Inicializando todos os dados do sistema...")
    
    try:
        # Verifica se existe o banco de dados
        if os.path.exists("pobchecker.sqlite3"):
            print("✅ Banco de dados local encontrado")
        else:
            print("⚠️  Banco de dados local não encontrado - será criado automaticamente")
        
        # Inicializa dados do terminal
        print("📋 Inicializando dados dos terminais...")
        subprocess.run([sys.executable, "utilitarys/utilitary_terminal_generate.py"], check=True)
        
        # Verifica configuração do consolidador
        print("🌐 Verificando configuração do consolidador...")
        if os.path.exists("consolidator_config.json"):
            print("✅ Configuração do consolidador encontrada")
        else:
            print("⚠️  Configuração do consolidador não encontrada")
        
        print("✅ Inicialização concluída!")
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")

def list_system_data():
    """Lista dados do sistema"""
    print("📊 Listando dados do sistema...")
    
    try:
        # Lista dados dos terminais
        print("\n🖥️  DADOS DOS TERMINAIS:")
        from database import Database
        db = Database()
        
        # Conta registros
        cursor = db.cursor
        cursor.execute("SELECT COUNT(*) FROM POB")
        people_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM POB WHERE Onshore = 0")
        pob_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM EVENTS")
        events_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM CHECK_EVENT")
        checks_count = cursor.fetchone()[0]
        
        print(f"   📋 Pessoas cadastradas: {people_count}")
        print(f"   🚢 Pessoas no POB: {pob_count}")
        print(f"   📅 Eventos: {events_count}")
        print(f"   ✅ Registros de check: {checks_count}")
        
        # Lista dados do consolidador
        print("\n🌐 DADOS DO CONSOLIDADOR:")
        try:
            from database_postgres import DatabasePostgres
            
            db_pg = DatabasePostgres()
            stats = db_pg.get_stats()
            
            print(f"   👥 Total de pessoas: {stats.get('total_persons', 0)}")
            print(f"   🚢 Pessoas no POB: {stats.get('pob_count', 0)}")
            print(f"   📅 Total de eventos: {stats.get('events', 0)}")
            print(f"   🔓 Eventos abertos: {stats.get('open_events', 0)}")
            print(f"   ✅ Total de checks: {stats.get('total_checks', 0)}")
            print(f"   🔄 Total de check-ins/outs: {stats.get('total_checkins', 0)}")
            print(f"   🖥️  Terminais conectados: {stats.get('terminals', 0)}")
            print(f"   🔄 Última sincronização: {stats.get('last_sync', 'N/A')}")
            
            db_pg.close()
                
        except ImportError:
            print("   ⚠️  Servidor consolidador não disponível")
        except Exception as e:
            print(f"   ❌ Erro ao acessar consolidador: {e}")
        
    except Exception as e:
        print(f"❌ Erro ao listar dados: {e}")

def generate_qrcodes():
    """Gera QR Codes"""
    print("🔳 Gerando QR Codes...")
    try:
        subprocess.run([sys.executable, "utilitarys/utilitary_system_generate_qrcodes.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao gerar QR Codes: {e}")

def show_qrcodes():
    """Mostra QR Codes gerados"""
    print("👁️  Visualizando QR Codes...")
    qr_folder = "qrcodes_cpf"
    
    if os.path.exists(qr_folder):
        files = [f for f in os.listdir(qr_folder) if f.endswith('.png')]
        print(f"\n📋 QR Codes encontrados ({len(files)} arquivos):")
        for i, file in enumerate(files[:10], 1):
            print(f"   {i}. {file}")
        if len(files) > 10:
            print(f"   ... e mais {len(files) - 10} arquivos")
        
        print(f"\n📂 Local: {os.path.abspath(qr_folder)}")
        print("📄 Formato: CPF|NOME")
        
        # Tenta abrir a pasta
        try:
            os.startfile(qr_folder)
            print("✅ Pasta aberta no explorador")
        except:
            print("⚠️  Para visualizar, acesse a pasta qrcodes_cpf/")
    else:
        print("❌ Pasta de QR Codes não encontrada. Execute primeiro a opção 4.")

def run_system_tests():
    """Executa testes do sistema"""
    print("🧪 Executando testes do sistema...")
    try:
        subprocess.run([sys.executable, "tests/run_all_tests.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro nos testes: {e}")

def clear_terminal_data():
    """Limpa dados dos terminais"""
    print("🗑️  Limpando dados dos terminais...")
    try:
        subprocess.run([sys.executable, "utilitarys/utilitary_terminal_clear.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao limpar dados: {e}")

def populate_terminal_data():
    """Popula terminais com dados de teste"""
    print("📋 Populando terminais com dados de teste...")
    try:
        subprocess.run([sys.executable, "utilitarys/utilitary_terminal_generate.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao popular dados: {e}")

def manage_terminal_data():
    """Gerencia dados dos terminais"""
    print("🔧 Gerenciando dados dos terminais...")
    try:
        subprocess.run([sys.executable, "utilitarys/utilitary_terminal_manage.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao gerenciar dados dos terminais: {e}")

def setup_consolidator():
    """Configura o consolidador"""
    print("⚙️  Configurando consolidador...")
    try:
        subprocess.run([sys.executable, "utilitarys/utilitary_server_setup.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao configurar consolidador: {e}")

def start_consolidator_server():
    """Inicia servidor do consolidador"""
    print("🚀 Iniciando servidor do consolidador...")
    try:
        print("📡 Servidor POBChecker Consolidador iniciando...")
        print("   🌐 Dashboard: http://localhost:8000/dashboard")
        print("   📋 API: http://localhost:8000/docs")
        print("\n⏹️  Pressione Ctrl+C para parar\n")
        
        subprocess.run([sys.executable, "run_server.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
    except KeyboardInterrupt:
        print("\n⚠️  Servidor parado pelo usuário")

def manage_consolidator_data():
    """Gerencia dados do consolidador"""
    print("📊 Gerenciando dados do consolidador...")
    try:
        subprocess.run([sys.executable, "utilitarys/utilitary_server_data.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao gerenciar dados do consolidador: {e}")

def list_consolidator_data():
    """Lista dados do consolidador"""
    print("📋 Listando dados do consolidador...")
    
    try:
        from database_postgres import DatabasePostgres
        
        db = DatabasePostgres()
        
        print("\n🌐 DADOS DO CONSOLIDADOR:")
        
        # Estatísticas principais
        stats = db.get_stats()
        print(f"   👥 Total de pessoas: {stats.get('total_persons', 0)}")
        print(f"   🚢 Pessoas no POB: {stats.get('pob_count', 0)}")
        print(f"   📅 Total de eventos: {stats.get('events', 0)}")
        print(f"   🔓 Eventos abertos: {stats.get('open_events', 0)}")
        print(f"   ✅ Total de checks: {stats.get('total_checks', 0)}")
        print(f"   🔄 Total de check-ins/outs: {stats.get('total_checkins', 0)}")
        print(f"   🖥️  Terminais conectados: {stats.get('terminals', 0)}")
        print(f"   🔄 Última sincronização: {stats.get('last_sync', 'N/A')}")
        
        # Verifica arquivos de configuração
        print("\n⚙️  CONFIGURAÇÃO:")
        if os.path.exists("consolidator_config.json"):
            with open("consolidator_config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"   🔧 Tipo de banco: {config['consolidator_config']['database']['type']}")
            print(f"   🌐 Porta: {config['consolidator_config']['server']['port']}")
            print(f"   🔄 Auto-correlação: {config['consolidator_config']['correlation']['auto_correlate']}")
        else:
            print("   ⚠️  Arquivo de configuração não encontrado")
        
        db.close()
        
    except ImportError:
        print("❌ Servidor consolidador não disponível")
    except Exception as e:
        print(f"❌ Erro ao listar dados: {e}")

def test_consolidator():
    """Testa o consolidador"""
    print("🧪 Testando consolidador...")
    try:
        subprocess.run([sys.executable, "utilitarys/utilitary_server_tests.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao testar consolidador: {e}")

def main():
    """Função principal"""
    print("POBCHECKER - SISTEMA DE GERENCIAMENTO DE UTILITÁRIOS v3.0")
    print("Sistema unificado para gerenciamento de terminais e consolidador")
    
    while True:
        show_main_menu()
        
        try:
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "0":
                print("👋 Saindo...")
                break
                
            # Funções gerais
            elif choice == "1":
                run_pobchecker_terminal()
            elif choice == "2":
                initialize_all_data()
            elif choice == "3":
                list_system_data()
            elif choice == "4":
                generate_qrcodes()
            elif choice == "5":
                show_qrcodes()
            elif choice == "6":
                run_system_tests()
                
            # Funções dos terminais
            elif choice == "7":
                clear_terminal_data()
            elif choice == "8":
                populate_terminal_data()
            elif choice == "9":
                manage_terminal_data()
                
            # Funções do consolidador
            elif choice == "10":
                setup_consolidator()
            elif choice == "11":
                start_consolidator_server()
            elif choice == "12":
                manage_consolidator_data()
            elif choice == "13":
                list_consolidator_data()
            elif choice == "14":
                test_consolidator()
                
            else:
                print("❌ Opção inválida. Tente novamente.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
