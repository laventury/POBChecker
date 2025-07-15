#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo: configure_consolidator_postgresql.py
Descrição: Script para configurar e inicializar o PostgreSQL para o consolidador
"""

import sys
import os
import json
import subprocess

# Importações para PostgreSQL
try:
    import psycopg2
    from psycopg2 import sql
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

def load_config():
    """Carrega configuração do consolidador"""
    config_file = "consolidator_config.json"
    
    if not os.path.exists(config_file):
        print(f"❌ Arquivo de configuração não encontrado: {config_file}")
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config['consolidator_config']
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        return None

def test_postgresql_connection(config):
    """Testa conexão com PostgreSQL"""
    if not POSTGRESQL_AVAILABLE:
        print("❌ psycopg2 não está instalado. Execute: pip install psycopg2-binary")
        return False
    
    db_config = config['database']['postgresql']
    
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ Conexão PostgreSQL estabelecida")
        print(f"   Versão: {version[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Erro na conexão PostgreSQL: {e}")
        return False

def create_database_if_not_exists(config):
    """Cria o banco de dados se não existir"""
    if not POSTGRESQL_AVAILABLE:
        return False
    
    db_config = config['database']['postgresql']
    
    try:
        # Conecta ao PostgreSQL sem especificar banco
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database='postgres',  # Banco padrão
            user=db_config['user'],
            password=db_config['password']
        )
        
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Verifica se banco existe
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_config['name'],)
        )
        
        if cursor.fetchone():
            print(f"✅ Banco '{db_config['name']}' já existe")
        else:
            # Cria banco
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(db_config['name'])
                )
            )
            print(f"✅ Banco '{db_config['name']}' criado")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Erro ao criar banco: {e}")
        return False

def create_tables(config):
    """Cria tabelas do consolidador"""
    if not POSTGRESQL_AVAILABLE:
        return False
    
    db_config = config['database']['postgresql']
    
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        cursor = conn.cursor()
        
        # Tabela de eventos consolidados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consolidated_events (
                id SERIAL PRIMARY KEY,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                participating_terminals TEXT[] NOT NULL,
                total_expected INTEGER NOT NULL,
                total_present INTEGER NOT NULL,
                completion_percentage DECIMAL(5,2) NOT NULL,
                is_active BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                original_events JSONB
            )
        """)
        
        # Tabela de status dos terminais
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS terminal_status (
                terminal_id VARCHAR(50) PRIMARY KEY,
                location VARCHAR(255),
                status VARCHAR(20) NOT NULL,
                last_sync TIMESTAMP,
                last_heartbeat TIMESTAMP,
                config JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de correlações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_correlations (
                id SERIAL PRIMARY KEY,
                consolidated_event_id INTEGER REFERENCES consolidated_events(id),
                terminal_events JSONB NOT NULL,
                correlation_score DECIMAL(5,4) NOT NULL,
                time_difference_seconds INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de logs de sincronização
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_logs (
                id SERIAL PRIMARY KEY,
                terminal_id VARCHAR(50) NOT NULL,
                operation VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL,
                message TEXT,
                data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Tabelas criadas com sucesso")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def setup_indices(config):
    """Cria índices para melhor performance"""
    if not POSTGRESQL_AVAILABLE:
        return False
    
    db_config = config['database']['postgresql']
    
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        cursor = conn.cursor()
        
        # Índices para consolidated_events
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_consolidated_events_start_time 
            ON consolidated_events (start_time)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_consolidated_events_is_active 
            ON consolidated_events (is_active)
        """)
        
        # Índices para terminal_status
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_terminal_status_last_sync 
            ON terminal_status (last_sync)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_terminal_status_status 
            ON terminal_status (status)
        """)
        
        # Índices para sync_logs
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sync_logs_terminal_id 
            ON sync_logs (terminal_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sync_logs_created_at 
            ON sync_logs (created_at)
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Índices criados com sucesso")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Erro ao criar índices: {e}")
        return False

def main():
    """Função principal"""
    print("POBCHECKER - CONFIGURAÇÃO POSTGRESQL PARA CONSOLIDADOR")
    print("=" * 60)
    
    # Carrega configuração
    config = load_config()
    if not config:
        return False
    
    # Verifica se PostgreSQL está disponível
    if not POSTGRESQL_AVAILABLE:
        print("❌ PostgreSQL não está disponível")
        print("   Instale com: pip install psycopg2-binary")
        return False
    
    # Testa conexão
    print("\n1. Testando conexão...")
    if not test_postgresql_connection(config):
        print("❌ Falha na conexão. Verifique as configurações.")
        return False
    
    # Cria banco se necessário
    print("\n2. Verificando/criando banco...")
    if not create_database_if_not_exists(config):
        print("❌ Falha ao criar banco.")
        return False
    
    # Cria tabelas
    print("\n3. Criando tabelas...")
    if not create_tables(config):
        print("❌ Falha ao criar tabelas.")
        return False
    
    # Cria índices
    print("\n4. Criando índices...")
    if not setup_indices(config):
        print("❌ Falha ao criar índices.")
        return False
    
    print("\n✅ Configuração PostgreSQL concluída com sucesso!")
    print("   O consolidador está pronto para uso.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
