# -*- coding: utf-8 -*-
# Arquivo: config.py - Configurações do sistema

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# QR Code especial para ativar/desativar modo CEV (Check Event)
QR_EVENT_CODE = "QR_EVENT_CONTROL"

# Configurações de limpeza automática
AUTO_CLEANUP_MONTHS = 6

# Configurações de interface
DEFAULT_MODE = "CIO"  # CIO ou CEV

# Configurações de banco de dados
DATABASE_CONFIG = {
    'type': os.getenv('DATABASE_TYPE', 'sqlite'),  # sqlite ou postgresql
    'sqlite_file': os.getenv('SQLITE_FILE', 'pobchecker.sqlite3'),
    'postgresql': {
        'host': os.getenv('DATABASE_HOST', 'localhost'),
        'port': int(os.getenv('DATABASE_PORT', '5432')),
        'database': os.getenv('DATABASE_NAME', 'pobchecker_db'),
        'user': os.getenv('DATABASE_USER', 'pobchecker'),
        'password': os.getenv('DATABASE_PASSWORD', 'pobchecker')
    }
}

# Configurações de rede
NETWORK_CONFIG = {
    'consolidator_enabled': os.getenv('CONSOLIDATOR_ENABLED', 'false').lower() == 'true',
    'consolidator_host': os.getenv('CONSOLIDATOR_HOST', '0.0.0.0'),
    'consolidator_port': int(os.getenv('CONSOLIDATOR_PORT', '8000')),
    'api_key': os.getenv('API_KEY', 'consolidador-api-key-2025'),
    'mdns_service': os.getenv('MDNS_SERVICE_NAME', '_pobchecker._tcp.local.')
}

# Configurações de sincronização
SYNC_CONFIG = {
    'enabled': os.getenv('SYNC_ENABLED', 'true').lower() == 'true',
    'interval_seconds': int(os.getenv('SYNC_INTERVAL_SECONDS', '300')),
    'max_retries': int(os.getenv('SYNC_MAX_RETRIES', '3')),
    'timeout_seconds': int(os.getenv('SYNC_TIMEOUT_SECONDS', '10'))
}

# Configurações de sincronização de tempo
TIME_SYNC_CONFIG = {
    'enabled': os.getenv('TIME_SYNC_ENABLED', 'true').lower() == 'true',
    'primary_server': os.getenv('PRIMARY_NTP_SERVER', 'pool.ntp.org'),
    'backup_servers': [
        'time.google.com',
        'time.cloudflare.com',
        'time.nist.gov',
        'pool.ntp.br'
    ],
    'sync_interval': int(os.getenv('SYNC_INTERVAL_SECONDS', '3600')),
    'timeout': int(os.getenv('TIME_SYNC_TIMEOUT', '5'))
}

def get_database_connection():
    """
    Retorna uma conexão de banco de dados baseada na configuração.
    """
    if DATABASE_CONFIG['type'] == 'postgresql':
        try:
            from database_postgres import DatabasePostgres
            return DatabasePostgres()
        except ImportError:
            print("⚠️  PostgreSQL não disponível, usando SQLite")
            from database import Database
            return Database()
    else:
        from database import Database
        return Database()

def is_postgresql_available():
    """
    Verifica se o PostgreSQL está disponível e configurado.
    """
    try:
        import psycopg2
        
        # Tenta conectar
        conn = psycopg2.connect(
            host=DATABASE_CONFIG['postgresql']['host'],
            port=DATABASE_CONFIG['postgresql']['port'],
            database=DATABASE_CONFIG['postgresql']['database'],
            user=DATABASE_CONFIG['postgresql']['user'],
            password=DATABASE_CONFIG['postgresql']['password']
        )
        conn.close()
        return True
    except:
        return False
