# -*- coding: utf-8 -*-
# Arquivo: time_sync.py - Módulo de Sincronização Temporal

import ntplib
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, List
import json

class TimeSync:
    """
    Classe para gerenciar sincronização temporal com servidores NTP.
    Sistema não-bloqueante que sempre funciona mesmo sem conectividade.
    """
    def __init__(self, config_file=None):
        # Carrega configuração do arquivo
        self.config = self._load_config(config_file)
        
        # Configurações NTP
        self.primary_ntp_server = self.config.get('primary_ntp_server', 'pool.ntp.org')
        self.backup_ntp_servers = self.config.get('backup_ntp_servers', [
            'time.google.com',
            'time.cloudflare.com',
            'time.nist.gov',
            'pool.ntp.br'
        ])
        
        # Configurações de sincronização
        self.retry_interval = self.config.get('sync_interval_seconds', 3600)
        self.timeout = self.config.get('timeout_seconds', 5)
        self.max_retry_attempts = self.config.get('max_retry_attempts', 3)
        self.retry_failed_servers = self.config.get('retry_failed_servers', True)
        
        # Estado da sincronização
        self.last_sync = None
        self.time_offset = 0
        self.sync_enabled = self.config.get('enabled', True)
        self.sync_thread = None
        self.is_ntp_available = False
        self.current_server = None
        self.failed_servers = set()
        
    def _load_config(self, config_file):
        """Carrega configuração do arquivo JSON"""
        if config_file:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    full_config = json.load(f)
                    # Extrai configuração time_sync baseado no tipo de arquivo
                    if 'consolidator_config' in full_config:
                        return full_config['consolidator_config'].get('time_sync', {})
                    elif 'terminal_config' in full_config:
                        return full_config['terminal_config'].get('time_sync', {})
                    else:
                        return full_config.get('time_sync', {})
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"⚠️ Erro ao carregar configuração NTP: {e}. Usando valores padrão.")
                return {}
        return {}
    
    def _get_server_list(self) -> List[str]:
        """Retorna lista de servidores NTP ordenada por prioridade"""
        servers = [self.primary_ntp_server] + self.backup_ntp_servers
        
        # Remove servidores que falharam recentemente se retry estiver desabilitado
        if not self.retry_failed_servers:
            servers = [s for s in servers if s not in self.failed_servers]
            
        return servers
    
    def start_sync_service(self):
        """Inicia o serviço de sincronização em background"""
        if not self.sync_enabled:
            print("🕐 Sincronização NTP desabilitada na configuração")
            return
            
        if self.sync_thread is None or not self.sync_thread.is_alive():
            self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
            self.sync_thread.start()
            print(f"🕐 Serviço de sincronização NTP iniciado")
            print(f"    Servidor principal: {self.primary_ntp_server}")
            print(f"    Servidores backup: {', '.join(self.backup_ntp_servers)}")
    
    def _sync_loop(self):
        """Loop de sincronização periódica (não-bloqueante)"""
        while self.sync_enabled:
            try:
                success = self.sync_time_with_fallback()
                if success:
                    self.is_ntp_available = True
                    print(f"✅ Sincronização NTP realizada com sucesso.")
                    print(f"    Servidor: {self.current_server}")
                    print(f"    Offset: {self.time_offset:.2f}s")
                else:
                    self.is_ntp_available = False
                    print("⚠️ Falha na sincronização NTP. Usando tempo local.")
                    
            except Exception as e:
                self.is_ntp_available = False
                print(f"❌ Erro na sincronização NTP: {e}. Sistema continuará com tempo local.")
            
            # Aguarda próxima tentativa (não-bloqueante)
            time.sleep(self.retry_interval)
    
    def sync_time_with_fallback(self) -> bool:
        """
        Tenta sincronizar com servidores NTP usando fallback
        Retorna True se bem-sucedido, False caso contrário
        """
        servers = self._get_server_list()
        
        for server in servers:
            for attempt in range(self.max_retry_attempts):
                try:
                    success = self._sync_with_server(server)
                    if success:
                        self.current_server = server
                        # Remove servidor da lista de falhas se sync foi bem-sucedido
                        self.failed_servers.discard(server)
                        return True
                        
                except Exception as e:
                    print(f"Tentativa {attempt + 1}/{self.max_retry_attempts} falhou para {server}: {e}")
                    if attempt == self.max_retry_attempts - 1:
                        # Adiciona servidor à lista de falhas
                        self.failed_servers.add(server)
                        print(f"❌ Servidor {server} marcado como falhando")
        
        return False
    
    def _sync_with_server(self, server: str) -> bool:
        """Sincroniza com um servidor NTP específico"""
        try:
            ntp_client = ntplib.NTPClient()
            response = ntp_client.request(server, timeout=self.timeout)
            
            ntp_time = datetime.fromtimestamp(response.tx_time)
            local_time = datetime.now()
            
            self.time_offset = (ntp_time - local_time).total_seconds()
            self.last_sync = local_time
            
            return True
            
        except (ntplib.NTPException, OSError, Exception) as e:
            raise e
    
    def get_synced_time(self) -> datetime:
        """
        Retorna tempo sincronizado se disponível, caso contrário tempo local
        NUNCA falha - sempre retorna um datetime válido
        """
        try:
            if self.last_sync and self.is_ntp_available:
                # Calcula se a sincronização ainda é válida (máximo 2 horas)
                sync_age = datetime.now() - self.last_sync
                if sync_age.total_seconds() < 7200:  # 2 horas
                    return datetime.now() + timedelta(seconds=self.time_offset)
            
            # Fallback para tempo local se NTP não disponível ou muito antigo
            return datetime.now()
            
        except Exception:
            # Em caso de qualquer erro, retorna tempo local
            return datetime.now()
    
    def get_time_status(self) -> dict:
        """Retorna status detalhado da sincronização temporal"""
        return {
            'ntp_available': self.is_ntp_available,
            'enabled': self.sync_enabled,
            'current_server': self.current_server,
            'primary_server': self.primary_ntp_server,
            'backup_servers': self.backup_ntp_servers,
            'failed_servers': list(self.failed_servers),
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'time_offset': self.time_offset,
            'current_time': self.get_synced_time().isoformat(),
            'sync_source': 'NTP' if self.is_ntp_available else 'LOCAL',
            'sync_interval': self.retry_interval,
            'timeout': self.timeout
        }
    
    def reload_config(self, config_file=None):
        """Recarrega configuração sem reiniciar o serviço"""
        old_enabled = self.sync_enabled
        self.config = self._load_config(config_file)
        
        # Atualiza configurações
        self.primary_ntp_server = self.config.get('primary_ntp_server', 'pool.ntp.org')
        self.backup_ntp_servers = self.config.get('backup_ntp_servers', [])
        self.retry_interval = self.config.get('sync_interval_seconds', 3600)
        self.timeout = self.config.get('timeout_seconds', 5)
        self.sync_enabled = self.config.get('enabled', True)
        
        # Limpa lista de servidores falhando
        self.failed_servers.clear()
        
        print(f"🔄 Configuração NTP recarregada")
        print(f"    Servidor principal: {self.primary_ntp_server}")
        print(f"    Servidores backup: {', '.join(self.backup_ntp_servers)}")
        
        # Reinicia serviço se necessário
        if not old_enabled and self.sync_enabled:
            self.start_sync_service()
        elif old_enabled and not self.sync_enabled:
            print("🛑 Sincronização NTP desabilitada")
    
    def stop_sync_service(self):
        """Para o serviço de sincronização"""
        self.sync_enabled = False
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=1)
        print("🛑 Serviço de sincronização NTP parado")
