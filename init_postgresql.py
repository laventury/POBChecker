#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de inicialização do POBChecker com PostgreSQL.
Este script configura o banco de dados e migra dados se necessário.
"""

import os
import sys
import json
from datetime import datetime

def check_requirements():
    """
    Verifica se todos os requisitos estão instalados.
    """
    print("🔍 Verificando requisitos...")
    
    required_packages = [
        'sqlalchemy',
        'fastapi',
        'uvicorn',
        'psycopg2',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} - não encontrado")
    
    if missing_packages:
        print(f"\n❌ Pacotes faltando: {', '.join(missing_packages)}")
        print("Execute: pip install -r requirements_network.txt")
        return False
    
    return True

def check_wsl_postgresql():
    """
    Verifica se o PostgreSQL está rodando no WSL.
    """
    print("\n🔍 Verificando PostgreSQL no WSL...")
    
    try:
        import psycopg2
        from config import DATABASE_CONFIG
        
        conn = psycopg2.connect(
            host=DATABASE_CONFIG['postgresql']['host'],
            port=DATABASE_CONFIG['postgresql']['port'],
            database=DATABASE_CONFIG['postgresql']['database'],
            user=DATABASE_CONFIG['postgresql']['user'],
            password=DATABASE_CONFIG['postgresql']['password']
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print(f"✓ PostgreSQL conectado: {version[:50]}...")
        
        # Verifica se as tabelas existem
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name IN ('pob', 'events', 'check_event', 'check_in_out');
        """)
        
        table_count = cursor.fetchone()[0]
        print(f"✓ Tabelas existentes: {table_count}/4")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Erro PostgreSQL: {e}")
        return False

def initialize_database():
    """
    Inicializa o banco de dados PostgreSQL.
    """
    print("\n🔧 Inicializando banco de dados...")
    
    try:
        from database_postgres import DatabasePostgres
        
        db = DatabasePostgres()
        print("✓ Banco de dados inicializado com sucesso!")
        
        # Testa funcionalidade básica
        test_person = {
            'cpf': '00000000000',
            'nome': 'Teste Inicialização',
            'grupo': 999,
            'Onshore': 1
        }
        
        if db.insert_person(test_person):
            print("✓ Teste de inserção bem-sucedido")
            
            # Remove o teste
            if db.delete_person('00000000000'):
                print("✓ Teste de remoção bem-sucedido")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Erro ao inicializar banco: {e}")
        return False

def migrate_sqlite_data():
    """
    Migra dados do SQLite para PostgreSQL se necessário.
    """
    sqlite_file = "pobchecker.sqlite3"
    
    if not os.path.exists(sqlite_file):
        print(f"\n⚠️  Arquivo SQLite '{sqlite_file}' não encontrado. Pulando migração.")
        return True
    
    print(f"\n🔄 Migrando dados do SQLite...")
    
    try:
        from database_postgres import migrate_from_sqlite
        
        if migrate_from_sqlite(sqlite_file):
            print("✓ Migração concluída com sucesso!")
            
            # Faz backup do SQLite
            backup_file = f"{sqlite_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(sqlite_file, backup_file)
            print(f"✓ Backup criado: {backup_file}")
            
            return True
        else:
            print("✗ Erro na migração")
            return False
            
    except Exception as e:
        print(f"✗ Erro durante migração: {e}")
        return False

def create_service_configs():
    """
    Cria arquivos de configuração dos serviços.
    """
    print("\n📝 Criando configurações dos serviços...")
    
    # Atualiza consolidator_config.json para PostgreSQL
    consolidator_config = {
        "consolidator_config": {
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": False
            },
            "correlation": {
                "tolerance_minutes": 30,
                "auto_correlate": True
            },
            "interface": {
                "theme": "light",
                "auto_refresh_seconds": 20,
                "pagination_size": 50,
                "date_format": "dd/mm/yyyy",
                "timezone": "America/Sao_Paulo"
            },
            "database": {
                "type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "name": "pobchecker_db",
                "user": "pobchecker",
                "password": "pobchecker"
            },
            "network": {
                "mdns_service_name": "_pobchecker._tcp.local.",
                "api_key": "consolidador-api-key-2025"
            },
            "time_sync": {
                "enabled": True,
                "primary_ntp_server": "pool.ntp.org",
                "backup_ntp_servers": [
                    "time.google.com",
                    "time.cloudflare.com",
                    "time.nist.gov",
                    "pool.ntp.br"
                ],
                "sync_interval_seconds": 3600,
                "timeout_seconds": 5,
                "max_offset_tolerance": 300,
                "fallback_to_local": True,
                "retry_failed_servers": True,
                "max_retry_attempts": 3
            }
        }
    }
    
    with open('consolidator_config.json', 'w', encoding='utf-8') as f:
        json.dump(consolidator_config, f, indent=2, ensure_ascii=False)
    
    print("✓ consolidator_config.json atualizado")
    
    # Verifica se terminal_config.json existe
    if os.path.exists('terminal_config.json'):
        print("✓ terminal_config.json já existe")
    else:
        terminal_config = {
            "terminal_config": {
                "terminal_id": "TERMINAL_001",
                "location": "Escritório Principal",
                "operation_mode": "CIO",
                "database": {
                    "type": "postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "name": "pobchecker_db",
                    "user": "pobchecker",
                    "password": "pobchecker"
                },
                "network": {
                    "consolidator_discovery": True,
                    "sync_enabled": True,
                    "sync_interval_seconds": 300,
                    "api_key": "consolidador-api-key-2025"
                },
                "interface": {
                    "theme": "dark",
                    "fullscreen": False,
                    "auto_clear_seconds": 30,
                    "beep_enabled": True
                },
                "time_sync": {
                    "enabled": True,
                    "primary_ntp_server": "pool.ntp.org",
                    "sync_interval_seconds": 3600,
                    "timeout_seconds": 5
                }
            }
        }
        
        with open('terminal_config.json', 'w', encoding='utf-8') as f:
            json.dump(terminal_config, f, indent=2, ensure_ascii=False)
        
        print("✓ terminal_config.json criado")
    
    return True

def start_services():
    """
    Inicia os serviços do POBChecker.
    """
    print("\n🚀 Serviços disponíveis:")
    print("1. Terminal POBChecker: python pobchecker_terminal.py")
    print("2. Servidor Consolidador: python pobchecker_server.py")
    print("3. Executar Testes: python tests/run_all_tests.py")
    
    choice = input("\nDeseja iniciar algum serviço? (1/2/3/n): ").strip()
    
    if choice == '1':
        os.system('python pobchecker_terminal.py')
    elif choice == '2':
        os.system('python pobchecker_server.py')
    elif choice == '3':
        os.system('python tests/run_all_tests.py')
    else:
        print("Sistema configurado e pronto para uso!")

def main():
    """
    Função principal de inicialização.
    """
    print("🔧 POBChecker - Inicialização PostgreSQL")
    print("=" * 50)
    
    # Verifica requisitos
    if not check_requirements():
        sys.exit(1)
    
    # Verifica PostgreSQL
    if not check_wsl_postgresql():
        print("\n❌ PostgreSQL não está disponível.")
        print("Verifique se:")
        print("1. PostgreSQL está rodando no WSL: wsl -e bash -c 'sudo service postgresql start'")
        print("2. Banco 'pobchecker_db' existe")
        print("3. Usuário 'pobchecker' tem permissões")
        sys.exit(1)
    
    # Inicializa banco de dados
    if not initialize_database():
        sys.exit(1)
    
    # Cria configurações
    if not create_service_configs():
        sys.exit(1)
    
    # Pergunta sobre migração
    if os.path.exists("pobchecker.sqlite3"):
        migrate_choice = input("\n🔄 Deseja migrar dados do SQLite? (s/n): ").strip().lower()
        
        if migrate_choice in ['s', 'sim', 'y', 'yes']:
            if not migrate_sqlite_data():
                print("⚠️  Migração falhou, mas sistema pode continuar com PostgreSQL vazio.")
    
    print("\n✅ Inicialização concluída!")
    print("PostgreSQL está configurado e pronto para uso.")
    
    # Oferece para iniciar serviços
    start_services()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Inicialização cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
