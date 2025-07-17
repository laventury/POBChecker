# -*- coding: utf-8 -*-
# Arquivo: sync_service.py - Serviço de Sincronização com Servidor Central

import threading
import time
import json
import requests
from datetime import datetime
from typing import Optional, Dict, List
from database import Database
from network_discovery import NetworkDiscoveryService
from time_sync import TimeSync

class SyncService:
    """
    Serviço de sincronização que roda em background para enviar dados
    não sincronizados para o servidor central.
    """
    
    def __init__(self, config_file="terminal_config.json"):
        self.config = self._load_config(config_file)
        
        # Configurações
        self.terminal_id = self.config.get('terminal_id', 'terminal-desconhecido')
        self.sync_interval = self.config.get('sync_interval_seconds', 20)
        self.api_key = self.config.get('network', {}).get('api_key', '')
        self.location = self.config.get('location', 'Local não especificado')
        
        # Componentes
        self.db = Database()
        self.discovery = NetworkDiscoveryService()
        self.time_sync = TimeSync(config_file)
        
        # Estado do serviço
        self.is_running = False
        self.sync_thread = None
        self.stats = {
            'total_syncs': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'last_sync_time': None,
            'last_sync_status': None,
            'records_synced': 0
        }
        
    def _load_config(self, config_file):
        """Carrega configuração do arquivo JSON"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                full_config = json.load(f)
                return full_config.get('terminal_config', {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ Erro ao carregar configuração: {e}. Usando valores padrão.")
            return {}
    
    def start_sync_service(self):
        """Inicia o serviço de sincronização"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # Inicia descoberta de serviço
        self.discovery.start_discovery()
        
        # Inicia sincronização temporal
        self.time_sync.start_sync_service()
        
        # Inicia thread de sincronização
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        
        print(f"🔄 Serviço de sincronização iniciado")
        print(f"    Terminal ID: {self.terminal_id}")
        print(f"    Localização: {self.location}")
        print(f"    Intervalo: {self.sync_interval}s")
    
    def stop_sync_service(self):
        """Para o serviço de sincronização"""
        self.is_running = False
        
        # Para componentes
        self.discovery.stop_discovery()
        self.time_sync.stop_sync_service()
        
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=2)
            
        print("🛑 Serviço de sincronização parado")
    
    def _sync_loop(self):
        """Loop principal de sincronização"""
        while self.is_running:
            try:
                self._perform_sync()
                time.sleep(self.sync_interval)
            except Exception as e:
                print(f"❌ Erro no loop de sincronização: {e}")
                time.sleep(5)  # Aguarda antes de tentar novamente
    
    def _perform_sync(self):
        """Executa uma tentativa de sincronização"""
        self.stats['total_syncs'] += 1
        
        # 1. Verifica se há servidor disponível
        server_info = self.discovery.get_server_info()
        if not server_info:
            # Se não há servidor descoberto, força uma descoberta
            print("🔍 Nenhum servidor conhecido, iniciando descoberta...")
            self.discovery._perform_discovery()
            server_info = self.discovery.get_server_info()
            
        if not server_info:
            self.stats['last_sync_status'] = 'Servidor não encontrado'
            return

        # 2. Coleta dados não sincronizados (baseado em versão)
        event_records = self.db.get_unsynced_event_records()
        checkinout_records = self.db.get_unsynced_checkinout_records()
        events_records = self.db.get_unsynced_events()
        
        if not event_records and not checkinout_records and not events_records:
            self.stats['last_sync_status'] = 'Nenhum dado para sincronizar'
            return

        # 3. Prepara dados para envio
        sync_data = self._prepare_sync_data(event_records, checkinout_records, events_records)
        
        # 4. Envia dados para o servidor
        success = self._send_to_server(server_info, sync_data)
        
        if success:
            # 5. Com sistema baseado em versão, não precisa marcar como sincronizado
            self.stats['successful_syncs'] += 1
            self.stats['records_synced'] += len(event_records) + len(checkinout_records) + len(events_records)
            self.stats['last_sync_status'] = f'Sucesso - {len(events_records)} eventos, {len(event_records)} check-events, {len(checkinout_records)} check-ins/outs'
            print(f"✅ Sincronização realizada com sucesso")
        else:
            self.stats['failed_syncs'] += 1
            self.stats['last_sync_status'] = 'Falha ao enviar dados para servidor'
        
        self.stats['last_sync_time'] = self.time_sync.get_synced_time().isoformat()
    
    def _prepare_sync_data(self, event_records, checkinout_records, events_records=None):
        """Prepara dados para envio ao servidor com novo formato baseado em versão"""
        sync_data = {
            'terminal_id': self.terminal_id,
            'location': self.location,
            'sync_timestamp': self.time_sync.get_synced_time().isoformat(),
            'events': [],
            'check_events': [],
            'check_in_outs': []
        }
        
        # Formata eventos (nova funcionalidade)
        if events_records:
            for record in events_records:
                sync_data['events'].append({
                    'id': record[0],
                    'Open': record[1],
                    'Close': record[2],
                    'Closed': record[3],
                    'version': record[4],
                    'last_modified': record[5]
                })
        
        # Formata registros de check_events com novo formato
        for record in event_records:
            sync_data['check_events'].append({
                'id': record[0],
                'CPF': record[1],
                'Name': record[2],
                'Timestamp': record[3],
                'Event': record[4],
                'Status': record[5],
                'version': record[6],
                'last_modified': record[7]
            })
        
        # Formata registros de check in/out com novo formato
        for record in checkinout_records:
            sync_data['check_in_outs'].append({
                'id': record[0],
                'CPF': record[1],
                'Name': record[2],
                'Type': record[3],
                'Timestamp': record[4],
                'version': record[5],
                'last_modified': record[6]
            })
        
        return sync_data
    
    def _send_to_server(self, server_info, sync_data):
        """Envia dados para o servidor central"""
        try:
            ip = server_info['ip']
            port = server_info['port']
            url = f"http://{ip}:{port}/sync"
            
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': self.api_key
            }
            
            response = requests.post(
                url,
                json=sync_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Dados enviados com sucesso: {result}")
                return True
            else:
                print(f"❌ Falha ao enviar dados: HTTP {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Erro na requisição: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado ao enviar dados: {e}")
            return False
    
    def get_sync_status(self) -> Dict:
        """Retorna status detalhado da sincronização"""
        server_info = self.discovery.get_server_info()
        
        status = {
            'terminal_info': {
                'id': self.terminal_id,
                'location': self.location,
                'sync_interval': self.sync_interval
            },
            'service_status': {
                'running': self.is_running,
                'server_discovered': server_info is not None,
                'server_info': {
                    'address': f"{server_info['ip']}:{server_info['port']}" if server_info else None,
                    'method': server_info.get('method') if server_info else None,
                    'url': server_info.get('url') if server_info else None
                }
            },
            'sync_stats': self.stats.copy(),
            'time_sync_status': self.time_sync.get_time_status(),
            'pending_records': {
                'events': len(self.db.get_unsynced_events()),
                'check_events': len(self.db.get_unsynced_event_records()),
                'check_in_outs': len(self.db.get_unsynced_checkinout_records())
            }
        }
        
        return status
    
    def force_sync(self):
        """Força uma sincronização imediata"""
        if not self.is_running:
            print("⚠️ Serviço de sincronização não está rodando")
            return False
            
        print("🔄 Forçando sincronização...")
        self._perform_sync()
        return True
    
    def reload_config(self, config_file="terminal_config.json"):
        """Recarrega configuração"""
        self.config = self._load_config(config_file)
        
        # Atualiza configurações
        old_terminal_id = self.terminal_id
        self.terminal_id = self.config.get('terminal_id', 'terminal-desconhecido')
        self.sync_interval = self.config.get('sync_interval_seconds', 20)
        self.api_key = self.config.get('network', {}).get('api_key', '')
        self.location = self.config.get('location', 'Local não especificado')
        
        # Recarrega configuração de sincronização temporal
        self.time_sync.reload_config(config_file)
        
        print(f"🔄 Configuração de sincronização recarregada")
        if old_terminal_id != self.terminal_id:
            print(f"    Terminal ID alterado: {old_terminal_id} -> {self.terminal_id}")


def test_sync_service():
    """Função de teste para o serviço de sincronização"""
    sync_service = SyncService()
    
    print("Iniciando teste do serviço de sincronização...")
    sync_service.start_sync_service()
    
    try:
        time.sleep(60)  # Testa por 1 minuto
        
        status = sync_service.get_sync_status()
        print(f"Status final: {json.dumps(status, indent=2)}")
        
    finally:
        sync_service.stop_sync_service()


if __name__ == "__main__":
    test_sync_service()
