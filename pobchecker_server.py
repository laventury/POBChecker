# -*- coding: utf-8 -*-
# Arquivo: pobchecker_server.py - Servidor Central POBChecker

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
import threading
import time
import os

# Importações para PostgreSQL
try:
    import psycopg2
    from psycopg2 import sql
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

# Importação para mDNS
try:
    from zeroconf import Zeroconf, ServiceInfo
    import socket
    MDNS_AVAILABLE = True
except ImportError:
    MDNS_AVAILABLE = False

# Importações locais
from time_sync import TimeSync
from utils.event_correlator import EventCorrelator

# Configurações
CONFIG_FILE = "consolidator_config.json"

class ConsolidatorDatabase:
    """Banco de dados do consolidador (SQLite ou PostgreSQL)"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.db_type = self.config.get('database', {}).get('type', 'sqlite')
        self._lock = threading.Lock()
        
        if self.db_type == 'postgresql' and POSTGRESQL_AVAILABLE:
            self._init_postgresql()
        else:
            self._init_sqlite()
    
    def _init_postgresql(self):
        """Inicializa conexão PostgreSQL"""
        db_config = self.config.get('database', {}).get('postgresql', {})
        
        try:
            self.conn = psycopg2.connect(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 5432),
                database=db_config.get('name', 'pobchecker_db'),
                user=db_config.get('user', 'pobchecker'),
                password=db_config.get('password', 'pobchecker')
            )
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            print("✅ Consolidador conectado ao PostgreSQL")
        except Exception as e:
            print(f"❌ Erro ao conectar PostgreSQL: {e}")
            print("   Usando SQLite como fallback")
            self._init_sqlite()
            return
        
        self._create_tables_postgresql()
    
    def _init_sqlite(self):
        """Inicializa conexão SQLite"""
        db_file = self.config.get('database', {}).get('sqlite_file', 'consolidator.sqlite3')
        self.db_type = 'sqlite'
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        print(f"✅ Consolidador usando SQLite: {db_file}")
        self._create_tables_sqlite()
    
    def _create_tables_postgresql(self):
        """Cria tabelas PostgreSQL"""
        try:
            # Tabela de eventos consolidados
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS check_event_consolidated (
                    id SERIAL PRIMARY KEY,
                    "terminal_id" VARCHAR(255) NOT NULL,
                    "original_id" INTEGER NOT NULL,
                    "CPF" VARCHAR(11),
                    "Name" VARCHAR(255),
                    "Timestamp" VARCHAR(255) NOT NULL,
                    "Event" INTEGER,
                    "sync_timestamp" VARCHAR(255) NOT NULL,
                    UNIQUE("terminal_id", "original_id")
                )
            ''')
            
            # Tabela de check in/out consolidados
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS check_in_out_consolidated (
                    id SERIAL PRIMARY KEY,
                    "terminal_id" VARCHAR(255) NOT NULL,
                    "original_id" INTEGER NOT NULL,
                    "CPF" VARCHAR(11),
                    "Name" VARCHAR(255),
                    "Type" VARCHAR(50) NOT NULL,
                    "Timestamp" VARCHAR(255) NOT NULL,
                    "sync_timestamp" VARCHAR(255) NOT NULL,
                    UNIQUE("terminal_id", "original_id")
                )
            ''')
            
            # Tabela de status dos terminais
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS terminal_status (
                    "terminal_id" VARCHAR(255) PRIMARY KEY,
                    "location" VARCHAR(255),
                    "last_sync" VARCHAR(255),
                    "status" VARCHAR(50) DEFAULT 'offline',
                    "sync_count" INTEGER DEFAULT 0
                )
            ''')
            
            print("✅ Tabelas PostgreSQL criadas/verificadas")
            
        except Exception as e:
            print(f"❌ Erro ao criar tabelas PostgreSQL: {e}")
    
    def _create_tables_sqlite(self):
        """Cria tabelas SQLite"""
        # Tabela de eventos consolidados
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS check_event_consolidated (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                terminal_id TEXT NOT NULL,
                original_id INTEGER NOT NULL,
                CPF TEXT,
                Name TEXT,
                Timestamp TEXT NOT NULL,
                Event INTEGER,
                sync_timestamp TEXT NOT NULL,
                UNIQUE(terminal_id, original_id)
            )
        ''')
        
        # Tabela de check in/out consolidados
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS check_in_out_consolidated (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                terminal_id TEXT NOT NULL,
                original_id INTEGER NOT NULL,
                CPF TEXT,
                Name TEXT,
                Type TEXT NOT NULL,
                Timestamp TEXT NOT NULL,
                sync_timestamp TEXT NOT NULL,
                UNIQUE(terminal_id, original_id)
            )
        ''')
        
        # Tabela de status dos terminais
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS terminal_status (
                terminal_id TEXT PRIMARY KEY,
                location TEXT,
                last_sync TEXT,
                status TEXT DEFAULT 'offline',
                sync_count INTEGER DEFAULT 0
            )
        ''')        
        self.conn.commit()
        print("✅ Tabelas SQLite criadas/verificadas")
    
    def insert_sync_data(self, terminal_id: str, location: str, check_events: List[Dict], check_in_outs: List[Dict]) -> Dict:
        """Insere dados de sincronização"""
        with self._lock:
            sync_timestamp = datetime.now().isoformat()
            events_received = 0
            checkinouts_received = 0
            
            try:
                # Insere eventos
                for event in check_events:
                    try:
                        if self.db_type == 'postgresql':
                            self.cursor.execute('''
                                INSERT INTO check_event_consolidated 
                                ("terminal_id", "original_id", "CPF", "Name", "Timestamp", "Event", "sync_timestamp")
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT ("terminal_id", "original_id") DO NOTHING
                            ''', (
                                terminal_id,
                                event['id'],
                                event.get('CPF', ''),
                                event.get('Name', ''),
                                event.get('Timestamp', ''),
                                event.get('Event', 0),
                                sync_timestamp
                            ))
                        else:
                            self.cursor.execute('''
                                INSERT OR IGNORE INTO check_event_consolidated 
                                (terminal_id, original_id, CPF, Name, Timestamp, Event, sync_timestamp)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                terminal_id,
                                event['id'],
                                event.get('CPF', ''),
                                event.get('Name', ''),
                                event.get('Timestamp', ''),
                                event.get('Event', 0),
                                sync_timestamp
                            ))
                        if self.cursor.rowcount > 0:
                            events_received += 1
                    except Exception as e:
                        print(f"Erro ao inserir evento {event.get('id')}: {e}")
                
                # Insere check in/outs
                for checkinout in check_in_outs:
                    try:
                        if self.db_type == 'postgresql':
                            self.cursor.execute('''
                                INSERT INTO check_in_out_consolidated 
                                ("terminal_id", "original_id", "CPF", "Name", "Type", "Timestamp", "sync_timestamp")
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT ("terminal_id", "original_id") DO NOTHING
                            ''', (
                                terminal_id,
                                checkinout['id'],
                                checkinout.get('CPF', ''),
                                checkinout.get('Name', ''),
                                checkinout.get('Type', ''),
                                checkinout.get('Timestamp', ''),
                                sync_timestamp
                            ))
                        else:
                            self.cursor.execute('''
                                INSERT OR IGNORE INTO check_in_out_consolidated 
                                (terminal_id, original_id, CPF, Name, Type, Timestamp, sync_timestamp)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                terminal_id,
                                checkinout['id'],
                                checkinout.get('CPF', ''),
                                checkinout.get('Name', ''),
                                checkinout.get('Type', ''),
                                checkinout.get('Timestamp', ''),
                                sync_timestamp
                            ))
                        if self.cursor.rowcount > 0:
                            checkinouts_received += 1
                    except Exception as e:
                        print(f"Erro ao inserir check in/out {checkinout.get('id')}: {e}")
                
                # Atualiza status do terminal
                if self.db_type == 'postgresql':
                    self.cursor.execute('''
                        INSERT INTO terminal_status 
                        ("terminal_id", "location", "last_sync", "status", "sync_count")
                        VALUES (%s, %s, %s, 'online', 1)
                        ON CONFLICT ("terminal_id") DO UPDATE SET
                            "location" = EXCLUDED."location",
                            "last_sync" = EXCLUDED."last_sync",
                            "status" = EXCLUDED."status",
                            "sync_count" = terminal_status."sync_count" + 1
                    ''', (terminal_id, location, sync_timestamp))
                else:
                    self.cursor.execute('''
                        INSERT OR REPLACE INTO terminal_status 
                        (terminal_id, location, last_sync, status, sync_count)
                        VALUES (?, ?, ?, 'online', 
                                COALESCE((SELECT sync_count FROM terminal_status WHERE terminal_id = ?), 0) + 1)
                    ''', (terminal_id, location, sync_timestamp, terminal_id))
                
                self.conn.commit()
                
                return {
                    'status': 'success',
                    'check_events_received': events_received,
                    'check_in_outs_received': checkinouts_received,
                    'sync_timestamp': sync_timestamp
                }
                
            except Exception as e:
                self.conn.rollback()
                raise e
    
    def get_terminals_status(self) -> List[Dict]:
        """Retorna status de todos os terminais"""
        with self._lock:
            self.cursor.execute('''
                SELECT terminal_id, location, last_sync, status, sync_count
                FROM terminal_status
                ORDER BY terminal_id
            ''')
            
            terminals = []
            for row in self.cursor.fetchall():
                terminals.append({
                    'terminal_id': row[0],
                    'location': row[1],
                    'last_sync': row[2],
                    'status': row[3],
                    'sync_count': row[4]
                })
            
            return terminals
    
    def get_pob_status(self) -> Dict:
        """Retorna status consolidado do POB"""
        with self._lock:
            # Busca o último status de cada pessoa
            if self.db_type == 'postgresql':
                self.cursor.execute('''
                    SELECT DISTINCT ON ("CPF") "CPF", "Name", "Type", "Timestamp"
                    FROM check_in_out_consolidated
                    ORDER BY "CPF", "Timestamp" DESC
                ''')
            else:
                self.cursor.execute('''
                    SELECT CPF, Name, Type, Timestamp
                    FROM check_in_out_consolidated c1
                    WHERE Timestamp = (
                        SELECT MAX(Timestamp) 
                        FROM check_in_out_consolidated c2 
                        WHERE c1.CPF = c2.CPF
                    )
                    ORDER BY Timestamp DESC
                ''')
            
            people_status = {}
            for row in self.cursor.fetchall():
                people_status[row[0]] = {
                    'name': row[1],
                    'status': row[2],
                    'last_timestamp': row[3]
                }
            
            # Conta pessoas a bordo
            pob_count = sum(1 for p in people_status.values() if p['status'] == 'IN')
            
            return {
                'pob_total': pob_count,
                'people_status': people_status,
                'last_update': datetime.now().isoformat()
            }
    
    def get_active_events(self) -> List[Dict]:
        """Retorna eventos ativos"""
        with self._lock:
            # Por simplicidade, considera eventos das últimas 24 horas como ativos
            if self.db_type == 'postgresql':
                self.cursor.execute('''
                    SELECT DISTINCT "Event", COUNT(*) as participants
                    FROM check_event_consolidated
                    WHERE "Timestamp"::timestamp > NOW() - INTERVAL '1 day'
                    GROUP BY "Event"
                    ORDER BY "Event"
                ''')
            else:
                self.cursor.execute('''
                    SELECT DISTINCT Event, COUNT(*) as participants
                    FROM check_event_consolidated
                    WHERE datetime(Timestamp) > datetime('now', '-1 day')
                    GROUP BY Event
                    ORDER BY Event
                ''')
            
            events = []
            for row in self.cursor.fetchall():
                events.append({
                    'event_id': row[0],
                    'participants': row[1],
                    'status': 'active'
                })
            
            return events

    def clear_all_data(self):
        """Limpa todos os dados do consolidador"""
        with self._lock:
            try:
                # Limpa dados consolidados
                self.cursor.execute("DELETE FROM check_event_consolidated")
                self.cursor.execute("DELETE FROM check_in_out_consolidated")
                self.cursor.execute("DELETE FROM terminal_status")
                
                # Reset dos IDs auto-incremento para SQLite
                if self.db_type == 'sqlite':
                    self.cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('check_event_consolidated', 'check_in_out_consolidated', 'terminal_status')")
                
                self.conn.commit()
                print("✅ Dados do consolidador limpos com sucesso!")
                
            except Exception as e:
                print(f"❌ Erro ao limpar dados do consolidador: {e}")
                raise


class ConsolidatorServer:
    """Servidor consolidador principal"""
    
    def __init__(self):
        self.app = FastAPI(title="POBChecker Consolidador", version="1.0.0")
        self.config = self._load_config()
        
        # Componentes
        self.db = ConsolidatorDatabase(self.config)
        self.time_sync = TimeSync(CONFIG_FILE)
        self.event_correlator = EventCorrelator(
            tolerance_minutes=self.config.get('correlation', {}).get('tolerance_minutes', 30)
        )
        
        # Configuração CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Rotas
        self._setup_routes()
        
        # Serviço mDNS
        self.mdns_service = None
        self.zeroconf = None
        if MDNS_AVAILABLE:
            self._setup_mdns()
        
        print("🚀 Servidor consolidador inicializado")
    
    def _load_config(self) -> Dict:
        """Carrega configuração do servidor"""
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f).get('consolidator_config', {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ Erro ao carregar configuração: {e}. Usando padrões.")
            return {}
    
    def _setup_routes(self):
        """Configura rotas da API"""
        
        @self.app.post("/sync")
        async def sync_data(
            data: Dict[str, Any],
            x_api_key: Optional[str] = Header(None)
        ):
            """Endpoint para sincronização de dados dos terminais"""
            
            # Validação da API key
            expected_key = self.config.get('network', {}).get('api_key', '')
            if expected_key and x_api_key != expected_key:
                raise HTTPException(status_code=401, detail="API key inválida")
            
            # Validação dos dados
            if not data.get('terminal_id'):
                raise HTTPException(status_code=400, detail="terminal_id é obrigatório")
            
            terminal_id = data['terminal_id']
            location = data.get('location', 'Local não especificado')
            check_events = data.get('check_events', [])
            check_in_outs = data.get('check_in_outs', [])
            
            try:
                result = self.db.insert_sync_data(terminal_id, location, check_events, check_in_outs)
                
                print(f"✅ Sincronização de {terminal_id}:")
                print(f"   Eventos: {result['check_events_received']}")
                print(f"   Check-ins/outs: {result['check_in_outs_received']}")
                
                return result
                
            except Exception as e:
                print(f"❌ Erro na sincronização de {terminal_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
        
        @self.app.get("/api/v1/pob/status")
        async def get_pob_status():
            """Retorna status consolidado do POB"""
            return self.db.get_pob_status()
        
        @self.app.get("/api/v1/terminals/status")
        async def get_terminals_status():
            """Retorna status de todos os terminais"""
            return self.db.get_terminals_status()
        
        @self.app.get("/api/v1/events/active")
        async def get_active_events():
            """Retorna eventos ativos"""
            return self.db.get_active_events()
        
        @self.app.get("/api/v1/dashboard/summary")
        async def get_dashboard_summary():
            """Retorna resumo do dashboard"""
            pob_status = self.db.get_pob_status()
            terminals = self.db.get_terminals_status()
            active_events = self.db.get_active_events()
            
            return {
                'pob_total': pob_status['pob_total'],
                'events_active': len(active_events),
                'terminals_online': len([t for t in terminals if t['status'] == 'online']),
                'terminals_offline': len([t for t in terminals if t['status'] == 'offline']),
                'last_update': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        
        @self.app.get("/api/v1/system/time-status")
        async def get_time_status():
            """Retorna status da sincronização temporal"""
            return self.time_sync.get_time_status()
        
        @self.app.get("/api/v1/system/health")
        async def get_system_health():
            """Retorna status de saúde do sistema"""
            return {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'services': {
                    'database': 'online',
                    'time_sync': 'online' if self.time_sync.is_ntp_available else 'local',
                    'event_correlator': 'online'
                }
            }
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            """Página principal do dashboard"""
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>POBChecker - Consolidador Central</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .header { background: #2196F3; color: white; padding: 20px; border-radius: 8px; }
                    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
                    .stat-card { background: #f5f5f5; padding: 20px; border-radius: 8px; text-align: center; }
                    .stat-value { font-size: 2em; font-weight: bold; color: #2196F3; }
                    .api-links { margin-top: 20px; }
                    .api-links a { display: inline-block; margin: 5px; padding: 10px 15px; background: #4CAF50; color: white; text-decoration: none; border-radius: 4px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>POBChecker - Consolidador Central</h1>
                    <p>Sistema de consolidação de dados de múltiplos terminais</p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value" id="pob-total">-</div>
                        <div>Pessoas a Bordo</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="events-active">-</div>
                        <div>Eventos Ativos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="terminals-online">-</div>
                        <div>Terminais Online</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="last-update">-</div>
                        <div>Última Atualização</div>
                    </div>
                </div>
                
                <div class="api-links">
                    <h3>Endpoints da API:</h3>
                    <a href="/api/v1/dashboard/summary">Dashboard Summary</a>
                    <a href="/api/v1/pob/status">Status POB</a>
                    <a href="/api/v1/terminals/status">Status Terminais</a>
                    <a href="/api/v1/events/active">Eventos Ativos</a>
                    <a href="/api/v1/system/health">Saúde do Sistema</a>
                    <a href="/api/v1/system/time-status">Status NTP</a>
                    <a href="/docs">Documentação da API</a>
                </div>
                
                <script>
                    async function updateDashboard() {
                        try {
                            const response = await fetch('/api/v1/dashboard/summary');
                            const data = await response.json();
                            
                            document.getElementById('pob-total').textContent = data.pob_total;
                            document.getElementById('events-active').textContent = data.events_active;
                            document.getElementById('terminals-online').textContent = data.terminals_online;
                            document.getElementById('last-update').textContent = data.last_update;
                        } catch (error) {
                            console.error('Erro ao atualizar dashboard:', error);
                        }
                    }
                    
                    // Atualiza dashboard a cada 20 segundos
                    updateDashboard();
                    setInterval(updateDashboard, 20000);
                </script>
            </body>
            </html>
            """
    
    def _setup_mdns(self):
        """Configura serviço mDNS para descoberta automática"""
        try:
            # Configuração do serviço
            service_type = "_pobchecker._tcp.local."
            service_name = "POBChecker-Consolidator._pobchecker._tcp.local."
            server_config = self.config.get('server', {})
            port = server_config.get('port', 8000)
            
            # Obter IP local
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Informações do serviço
            info = ServiceInfo(
                service_type,
                service_name,
                addresses=[socket.inet_aton(local_ip)],
                port=port,
                properties={
                    b'version': b'1.0',
                    b'type': b'consolidator',
                    b'api_version': b'v1'
                }
            )
            
            # Inicia zeroconf
            self.zeroconf = Zeroconf()
            self.zeroconf.register_service(info)
            self.mdns_service = info
            
            print(f"📡 Serviço mDNS publicado: {service_name}")
            print(f"   IP: {local_ip}:{port}")
            
        except Exception as e:
            print(f"⚠️ Erro ao configurar mDNS: {e}")
            import traceback
            traceback.print_exc()
            
    def _stop_mdns(self):
        """Para o serviço mDNS"""
        if self.zeroconf and self.mdns_service:
            try:
                self.zeroconf.unregister_service(self.mdns_service)
                self.zeroconf.close()
                print("📡 Serviço mDNS parado")
            except Exception as e:
                print(f"⚠️ Erro ao parar mDNS: {e}")
    
    def start_server(self):
        """Inicia o servidor"""
        # Inicia sincronização temporal
        self.time_sync.start_sync_service()
        
        # Configuração do servidor
        server_config = self.config.get('server', {})
        host = server_config.get('host', '0.0.0.0')
        port = server_config.get('port', 8000)
        debug = server_config.get('debug', False)
        
        print(f"🌐 Iniciando servidor consolidador em {host}:{port}")
        
        # Inicia servidor
        uvicorn.run(self.app, host=host, port=port, log_level="info" if debug else "warning")


def main():
    """Função principal"""
    server = ConsolidatorServer()
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
        server._stop_mdns()
    except Exception as e:
        print(f"❌ Erro no servidor: {e}")
        server._stop_mdns()


if __name__ == "__main__":
    main()
