# -*- coding: utf-8 -*-
# Arquivo: network_discovery.py - Descoberta de Rede Simplificada

import threading
import time
import requests
import socket
from zeroconf import Zeroconf, ServiceListener, ServiceBrowser
from typing import Optional, Dict, List
import ipaddress
import concurrent.futures

class NetworkDiscoveryService:
    """
    Serviço de descoberta de rede simplificado com múltiplos fallbacks:
    1. mDNS (Zeroconf)
    2. HTTP direto em IPs conhecidos
    3. Network Scan automático
    """
    
    def __init__(self, timeout=5):
        self.timeout = timeout
        self.server_info = None
        self.is_running = False
        self.discovery_thread = None
        self.zeroconf = None
        self.service_listener = None
        self.lock = threading.Lock()
        
        # Configurações padrão
        self.service_name = "_pobchecker._tcp.local."
        self.known_ips = ["127.0.0.1", "192.168.0.170", "192.168.1.1", "192.168.0.1"]
        self.common_ports = [8000, 8080, 3000, 5000]
        self.network_ranges = ["192.168.0.0/24", "192.168.1.0/24", "10.0.0.0/24"]
        
    def start_discovery(self):
        """Inicia descoberta de rede"""
        if self.is_running:
            return
            
        self.is_running = True
        self.discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
        self.discovery_thread.start()
        print("🔍 Descoberta de rede iniciada")
        
    def stop_discovery(self):
        """Para descoberta de rede"""
        self.is_running = False
        
        if self.zeroconf:
            self.zeroconf.close()
            self.zeroconf = None
            
        if self.discovery_thread and self.discovery_thread.is_alive():
            self.discovery_thread.join(timeout=2)
            
        print("🛑 Descoberta de rede parada")
        
    def get_server_info(self) -> Optional[Dict]:
        """Retorna informações do servidor descoberto"""
        with self.lock:
            return self.server_info.copy() if self.server_info else None
            
    def _discovery_loop(self):
        """Loop principal de descoberta"""
        while self.is_running:
            try:
                if not self.server_info:
                    self._perform_discovery()
                time.sleep(10)  # Verifica a cada 10 segundos
            except Exception as e:
                print(f"❌ Erro na descoberta: {e}")
                time.sleep(5)
                
    def _perform_discovery(self):
        """Executa descoberta com múltiplos fallbacks"""
        print("🔍 Iniciando descoberta de servidor...")
        
        # Fallback 1: mDNS
        if self._try_mdns_discovery():
            return
            
        # Fallback 2: HTTP direto em IPs conhecidos
        if self._try_direct_http_discovery():
            return
            
        # Fallback 3: Network Scan
        if self._try_network_scan():
            return
            
        print("❌ Nenhum servidor POBChecker encontrado")
        
    def _try_mdns_discovery(self) -> bool:
        """Tenta descoberta via mDNS"""
        try:
            print("🔍 Tentando descoberta mDNS...")
            
            class POBServiceListener(ServiceListener):
                def __init__(self, parent):
                    self.parent = parent
                    
                def add_service(self, zeroconf, type, name):
                    info = zeroconf.get_service_info(type, name)
                    if info:
                        self.parent._process_mdns_service(info)
                        
            self.zeroconf = Zeroconf()
            self.service_listener = POBServiceListener(self)
            browser = ServiceBrowser(self.zeroconf, self.service_name, self.service_listener)
            
            # Aguarda por descoberta
            time.sleep(3)
            
            browser.cancel()
            
            return self.server_info is not None
            
        except Exception as e:
            print(f"⚠️ mDNS falhou: {e}")
            return False
            
    def _process_mdns_service(self, info):
        """Processa serviço descoberto via mDNS"""
        try:
            ip = socket.inet_ntoa(info.addresses[0])
            port = info.port
            
            if self._validate_server(ip, port):
                with self.lock:
                    self.server_info = {
                        'ip': ip,
                        'port': port,
                        'url': f"http://{ip}:{port}",
                        'method': 'mDNS'
                    }
                print(f"✅ Servidor encontrado via mDNS: {ip}:{port}")
                
        except Exception as e:
            print(f"⚠️ Erro ao processar serviço mDNS: {e}")
            
    def _try_direct_http_discovery(self) -> bool:
        """Tenta descoberta HTTP direta em IPs conhecidos"""
        print("🔍 Tentando descoberta HTTP direta...")
        
        for ip in self.known_ips:
            for port in self.common_ports:
                if self._validate_server(ip, port):
                    with self.lock:
                        self.server_info = {
                            'ip': ip,
                            'port': port,
                            'url': f"http://{ip}:{port}",
                            'method': 'HTTP-direto'
                        }
                    print(f"✅ Servidor encontrado via HTTP direto: {ip}:{port}")
                    return True
                    
        return False
        
    def _try_network_scan(self) -> bool:
        """Tenta descoberta via network scan"""
        print("🔍 Tentando network scan...")
        
        for network_range in self.network_ranges:
            try:
                network = ipaddress.ip_network(network_range, strict=False)
                
                # Limita scan a 50 IPs por range
                ips_to_scan = list(network.hosts())[:50]
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                    future_to_ip = {}
                    
                    for ip in ips_to_scan:
                        for port in self.common_ports:
                            future = executor.submit(self._validate_server, str(ip), port)
                            future_to_ip[future] = (str(ip), port)
                            
                    for future in concurrent.futures.as_completed(future_to_ip, timeout=30):
                        ip, port = future_to_ip[future]
                        try:
                            if future.result():
                                with self.lock:
                                    self.server_info = {
                                        'ip': ip,
                                        'port': port,
                                        'url': f"http://{ip}:{port}",
                                        'method': 'Network-scan'
                                    }
                                print(f"✅ Servidor encontrado via network scan: {ip}:{port}")
                                return True
                        except Exception as e:
                            continue
                            
            except Exception as e:
                print(f"⚠️ Erro no scan da rede {network_range}: {e}")
                continue
                
        return False
        
    def _validate_server(self, ip: str, port: int) -> bool:
        """Valida se o IP:porta é um servidor POBChecker válido"""
        try:
            url = f"http://{ip}:{port}/api/v1/system/health"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('status') == 'healthy'
                
        except Exception:
            pass
            
        return False
        
    def force_rediscovery(self):
        """Força nova descoberta"""
        with self.lock:
            self.server_info = None
        print("🔄 Forçando nova descoberta...")
