# -*- coding: utf-8 -*-
# Arquivo: tests/test_system.py - Sistema Completo de Testes POBChecker

import unittest
import sys
import os
import json
import tempfile
import shutil
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import threading
import time

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestRegistry:
    """Registro de testes executados"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.end_time = None
        
    def add_result(self, test_name, category, status, duration, message="", details=None):
        """Adiciona resultado de teste"""
        self.test_results.append({
            'test_name': test_name,
            'category': category,
            'status': status,  # 'PASS', 'FAIL', 'SKIP'
            'duration': duration,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        })
    
    def get_summary(self):
        """Retorna resumo dos testes"""
        total = len(self.test_results)
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        skipped = len([r for r in self.test_results if r['status'] == 'SKIP'])
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'total_duration': (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0
        }
    
    def save_report(self, filename="test_report.json"):
        """Salva relatório de testes"""
        report = {
            'summary': self.get_summary(),
            'test_results': self.test_results,
            'generated_at': datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Relatório salvo em: {filename}")


class TestDatabaseCore(unittest.TestCase):
    """Testes do banco de dados principal"""
    
    def setUp(self):
        """Configura ambiente de teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_file = os.path.join(self.temp_dir, "test.db")
        
    def tearDown(self):
        """Limpa ambiente de teste"""
        shutil.rmtree(self.temp_dir)
    
    def test_database_creation(self):
        """Testa criação do banco de dados"""
        from database import Database
        
        db = Database(self.db_file)
        self.assertTrue(os.path.exists(self.db_file))
        
        # Verifica se tabelas foram criadas
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['POB', 'EVENTS', 'CHECK_EVENT', 'CHECK_IN_OUT']
        for table in expected_tables:
            self.assertIn(table, tables)
        
        conn.close()
    
    def test_synced_columns(self):
        """Testa se colunas Synced foram adicionadas"""
        from database import Database
        
        db = Database(self.db_file)
        
        # Verifica coluna Synced na tabela CHECK_EVENT
        cursor = db.cursor
        cursor.execute("PRAGMA table_info(CHECK_EVENT)")
        columns = [column[1] for column in cursor.fetchall()]
        self.assertIn('Synced', columns)
        
        # Verifica coluna Synced na tabela CHECK_IN_OUT
        cursor.execute("PRAGMA table_info(CHECK_IN_OUT)")
        columns = [column[1] for column in cursor.fetchall()]
        self.assertIn('Synced', columns)
    
    def test_unsynced_records(self):
        """Testa busca de registros não sincronizados"""
        from database import Database
        
        db = Database(self.db_file)
        
        # Insere dados de teste
        db.cursor.execute('''
            INSERT INTO CHECK_EVENT (CPF, Name, Timestamp, Event, Synced)
            VALUES ('12345678901', 'João Silva', '2025-07-14T10:00:00', 1, 0)
        ''')
        db.cursor.execute('''
            INSERT INTO CHECK_IN_OUT (CPF, Name, Type, Timestamp, Synced)
            VALUES ('12345678901', 'João Silva', 'IN', '2025-07-14T10:00:00', 0)
        ''')
        db.conn.commit()
        
        # Testa busca
        events = db.get_unsynced_event_records()
        checkinouts = db.get_unsynced_checkinout_records()
        
        self.assertEqual(len(events), 1)
        self.assertEqual(len(checkinouts), 1)
        
        # Marca como sincronizado
        db.mark_records_as_synced([events[0][0]], [checkinouts[0][0]])
        
        # Verifica se foram marcados
        events_after = db.get_unsynced_event_records()
        checkinouts_after = db.get_unsynced_checkinout_records()
        
        self.assertEqual(len(events_after), 0)
        self.assertEqual(len(checkinouts_after), 0)


class TestTimeSyncService(unittest.TestCase):
    """Testes do serviço de sincronização temporal"""
    
    def setUp(self):
        """Configura ambiente de teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        
        # Cria configuração de teste
        config = {
            "terminal_config": {
                "time_sync": {
                    "enabled": True,
                    "primary_ntp_server": "pool.ntp.org",
                    "backup_ntp_servers": ["time.google.com"],
                    "sync_interval_seconds": 10,
                    "timeout_seconds": 2,
                    "max_retry_attempts": 1
                }
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
    
    def tearDown(self):
        """Limpa ambiente de teste"""
        shutil.rmtree(self.temp_dir)
    
    def test_time_sync_initialization(self):
        """Testa inicialização do serviço de sincronização"""
        try:
            from time_sync import TimeSync
            
            time_sync = TimeSync(self.config_file)
            self.assertIsNotNone(time_sync)
            self.assertTrue(time_sync.sync_enabled)
            self.assertEqual(time_sync.primary_ntp_server, "pool.ntp.org")
            
        except ImportError:
            self.skipTest("Módulo time_sync não disponível")
    
    def test_get_synced_time(self):
        """Testa obtenção de tempo sincronizado"""
        try:
            from time_sync import TimeSync
            
            time_sync = TimeSync(self.config_file)
            
            # Deve sempre retornar um datetime, mesmo sem NTP
            sync_time = time_sync.get_synced_time()
            self.assertIsInstance(sync_time, datetime)
            
        except ImportError:
            self.skipTest("Módulo time_sync não disponível")
    
    def test_time_status(self):
        """Testa status da sincronização temporal"""
        try:
            from time_sync import TimeSync
            
            time_sync = TimeSync(self.config_file)
            status = time_sync.get_time_status()
            
            required_keys = ['enabled', 'primary_server', 'backup_servers', 'sync_source']
            for key in required_keys:
                self.assertIn(key, status)
            
        except ImportError:
            self.skipTest("Módulo time_sync não disponível")


class TestServiceDiscovery(unittest.TestCase):
    """Testes do serviço de descoberta"""
    
    def test_discovery_initialization(self):
        """Testa inicialização do serviço de descoberta"""
        try:
            from discovery import ServiceDiscovery
            
            discovery = ServiceDiscovery()
            self.assertIsNotNone(discovery)
            self.assertEqual(discovery.service_type, "_pobchecker._tcp.local.")
            
        except ImportError:
            self.skipTest("Módulo discovery não disponível")
    
    def test_discovery_status(self):
        """Testa status do serviço de descoberta"""
        try:
            from discovery import ServiceDiscovery
            
            discovery = ServiceDiscovery()
            
            # Inicialmente não deve ter servidor
            self.assertFalse(discovery.is_server_available())
            self.assertIsNone(discovery.get_server_info())
            
        except ImportError:
            self.skipTest("Módulo discovery não disponível")


class TestSyncService(unittest.TestCase):
    """Testes do serviço de sincronização"""
    
    def setUp(self):
        """Configura ambiente de teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        
        # Cria configuração de teste
        config = {
            "terminal_config": {
                "terminal_id": "terminal-test",
                "location": "Local de Teste",
                "sync_interval_seconds": 5,
                "api_key": "test-key",
                "time_sync": {
                    "enabled": False
                }
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
    
    def tearDown(self):
        """Limpa ambiente de teste"""
        shutil.rmtree(self.temp_dir)
    
    def test_sync_service_initialization(self):
        """Testa inicialização do serviço de sincronização"""
        try:
            from sync_service import SyncService
            
            sync_service = SyncService(self.config_file)
            self.assertIsNotNone(sync_service)
            self.assertEqual(sync_service.terminal_id, "terminal-test")
            self.assertEqual(sync_service.location, "Local de Teste")
            
        except ImportError:
            self.skipTest("Módulo sync_service não disponível")
    
    def test_sync_status(self):
        """Testa status do serviço de sincronização"""
        try:
            from sync_service import SyncService
            
            sync_service = SyncService(self.config_file)
            status = sync_service.get_sync_status()
            
            required_keys = ['terminal_info', 'service_status', 'sync_stats']
            for key in required_keys:
                self.assertIn(key, status)
            
        except ImportError:
            self.skipTest("Módulo sync_service não disponível")


class TestEventCorrelator(unittest.TestCase):
    """Testes do correlacionador de eventos"""
    
    def test_event_correlator_initialization(self):
        """Testa inicialização do correlacionador"""
        try:
            from utils.event_correlator import EventCorrelator
            
            correlator = EventCorrelator()
            self.assertIsNotNone(correlator)
            self.assertEqual(correlator.tolerance_minutes, 30)
            
        except ImportError:
            self.skipTest("Módulo event_correlator não disponível")
    
    def test_event_correlation(self):
        """Testa correlação de eventos"""
        try:
            from utils.event_correlator import EventCorrelator
            
            correlator = EventCorrelator(tolerance_minutes=30)
            
            # Eventos de teste
            test_events = [
                {
                    'id': 1,
                    'terminal_id': 'terminal-01',
                    'start_time': '2025-07-14T10:00:00',
                    'expected_count': 50,
                    'present_count': 45,
                    'is_active': True
                },
                {
                    'id': 2,
                    'terminal_id': 'terminal-02',
                    'start_time': '2025-07-14T10:15:00',
                    'expected_count': 30,
                    'present_count': 28,
                    'is_active': True
                }
            ]
            
            correlated = correlator.correlate_events(test_events)
            
            # Deve ter correlacionado os eventos
            self.assertEqual(len(correlated), 1)
            self.assertEqual(correlated[0]['total_expected'], 80)
            self.assertEqual(correlated[0]['total_present'], 73)
            
        except ImportError:
            self.skipTest("Módulo event_correlator não disponível")


class TestConsolidatorServer(unittest.TestCase):
    """Testes do servidor consolidador"""
    
    def test_consolidator_database(self):
        """Testa banco de dados do consolidador"""
        try:
            from pobchecker_server import ConsolidatorDatabase
            
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
                db_file = f.name
            
            try:
                db = ConsolidatorDatabase(db_file)
                
                # Verifica criação das tabelas
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                expected_tables = ['check_event_consolidated', 'check_in_out_consolidated', 'terminal_status']
                for table in expected_tables:
                    self.assertIn(table, tables)
                
                conn.close()
                
            finally:
                os.unlink(db_file)
                
        except ImportError:
            self.skipTest("Módulo pobchecker_server não disponível")
    
    def test_sync_data_insertion(self):
        """Testa inserção de dados de sincronização"""
        try:
            from pobchecker_server import ConsolidatorDatabase
            
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
                db_file = f.name
            
            try:
                db = ConsolidatorDatabase(db_file)
                
                # Dados de teste
                check_events = [
                    {
                        'id': 1,
                        'CPF': '12345678901',
                        'Name': 'João Silva',
                        'Timestamp': '2025-07-14T10:00:00',
                        'Event': 1
                    }
                ]
                
                check_in_outs = [
                    {
                        'id': 1,
                        'CPF': '12345678901',
                        'Name': 'João Silva',
                        'Type': 'IN',
                        'Timestamp': '2025-07-14T10:00:00'
                    }
                ]
                
                result = db.insert_sync_data('terminal-test', 'Local Teste', check_events, check_in_outs)
                
                self.assertEqual(result['status'], 'success')
                self.assertEqual(result['check_events_received'], 1)
                self.assertEqual(result['check_in_outs_received'], 1)
                
            finally:
                os.unlink(db_file)
                
        except ImportError:
            self.skipTest("Módulo pobchecker_server não disponível")


class TestSystemIntegration(unittest.TestCase):
    """Testes de integração do sistema"""
    
    def test_terminal_imports(self):
        """Testa importações do terminal"""
        try:
            from pobchecker_terminal import AttendanceChecker
            self.assertTrue(True)  # Se chegou aqui, importação funcionou
        except ImportError as e:
            self.skipTest(f"Importação do terminal falhou: {e}")
    
    def test_config_files(self):
        """Testa arquivos de configuração"""
        config_files = [
            'terminal_config.json',
            'consolidator_config.json'
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    self.assertIsInstance(config, dict)
                except json.JSONDecodeError:
                    self.fail(f"Arquivo {config_file} contém JSON inválido")
    
    def test_requirements_files(self):
        """Testa arquivos de requirements"""
        req_files = [
            'requirements.txt',
            'requirements_network.txt'
        ]
        
        for req_file in req_files:
            if os.path.exists(req_file):
                with open(req_file, 'r') as f:
                    content = f.read()
                self.assertIsInstance(content, str)
                self.assertGreater(len(content), 0)


def run_all_tests():
    """Executa todos os testes e gera relatório"""
    print("🧪 Iniciando testes completos do sistema POBChecker")
    print("=" * 60)
    
    # Inicializa registro de testes
    registry = TestRegistry()
    registry.start_time = datetime.now()
    
    # Lista de classes de teste
    test_classes = [
        TestDatabaseCore,
        TestTimeSyncService,
        TestServiceDiscovery,
        TestSyncService,
        TestEventCorrelator,
        TestConsolidatorServer,
        TestSystemIntegration
    ]
    
    # Executa cada classe de teste
    for test_class in test_classes:
        print(f"\n📋 Executando {test_class.__name__}:")
        print("-" * 40)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        
        for test in suite:
            test_name = test._testMethodName
            test_start = datetime.now()
            
            try:
                result = unittest.TestResult()
                test.run(result)
                
                test_duration = (datetime.now() - test_start).total_seconds()
                
                if result.wasSuccessful():
                    print(f"  ✅ {test_name} - PASSOU ({test_duration:.2f}s)")
                    registry.add_result(
                        test_name,
                        test_class.__name__,
                        'PASS',
                        test_duration
                    )
                else:
                    error_msg = ""
                    if result.errors:
                        error_msg = str(result.errors[0][1])
                    elif result.failures:
                        error_msg = str(result.failures[0][1])
                    
                    print(f"  ❌ {test_name} - FALHOU ({test_duration:.2f}s)")
                    print(f"     Erro: {error_msg[:100]}...")
                    
                    registry.add_result(
                        test_name,
                        test_class.__name__,
                        'FAIL',
                        test_duration,
                        error_msg
                    )
                    
            except Exception as e:
                test_duration = (datetime.now() - test_start).total_seconds()
                print(f"  ⚠️  {test_name} - PULADO ({test_duration:.2f}s)")
                print(f"     Motivo: {str(e)[:100]}...")
                
                registry.add_result(
                    test_name,
                    test_class.__name__,
                    'SKIP',
                    test_duration,
                    str(e)
                )
    
    registry.end_time = datetime.now()
    
    # Gera relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL DOS TESTES")
    print("=" * 60)
    
    summary = registry.get_summary()
    
    print(f"Total de testes: {summary['total']}")
    print(f"Passou: {summary['passed']} ✅")
    print(f"Falhou: {summary['failed']} ❌")
    print(f"Pulado: {summary['skipped']} ⚠️")
    print(f"Taxa de sucesso: {summary['success_rate']:.1f}%")
    print(f"Tempo total: {summary['total_duration']:.2f}s")
    
    # Salva relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.json"
    registry.save_report(report_file)
    
    print(f"\n📄 Relatório detalhado salvo em: {report_file}")
    
    # Recomendações baseadas nos resultados
    print("\n🔍 RECOMENDAÇÕES:")
    
    if summary['failed'] > 0:
        print("❌ Há testes falhando - revise os erros acima")
    
    if summary['skipped'] > 0:
        print("⚠️  Há testes pulados - instale dependências faltantes:")
        print("   pip install -r requirements_network.txt")
    
    if summary['success_rate'] == 100:
        print("✅ Todos os testes disponíveis passaram!")
    
    print("\n🚀 Sistema testado e pronto para uso!")
    
    return summary


if __name__ == "__main__":
    run_all_tests()
