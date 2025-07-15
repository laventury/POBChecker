#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração automática para descoberta de rede
"""

import json
import os
import shutil

def setup_network_discovery():
    """Configura o sistema para usar descoberta de rede"""
    
    print("🔧 CONFIGURANDO DESCOBERTA DE REDE")
    print("=" * 50)
    
    # 1. Backup do sync_service.py original
    if os.path.exists("sync_service.py"):
        if not os.path.exists("sync_service.py.backup"):
            shutil.copy("sync_service.py", "sync_service.py.backup")
            print("✅ Backup do sync_service.py criado")
    
    # 2. Atualiza import no sync_service.py
    try:
        with open("sync_service.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substitui import
        content = content.replace(
            "from hybrid_discovery import HybridServiceDiscovery",
            "from network_discovery_simplified import NetworkDiscoveryService"
        )
        
        content = content.replace(
            "self.discovery = HybridServiceDiscovery()",
            "self.discovery = NetworkHybridDiscovery()"
        )
        
        with open("sync_service.py", 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ sync_service.py atualizado para usar descoberta de rede")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar sync_service.py: {e}")
    
    # 3. Cria script de teste específico
    test_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Teste da descoberta de rede atualizada

from network_discovery_simplified import NetworkDiscoveryService
import time

def test_updated_discovery():
    print("🔍 TESTANDO DESCOBERTA DE REDE ATUALIZADA")
    print("=" * 50)
    
    discovery = NetworkDiscoveryService()
    discovery.start_discovery()
    
    print("Aguardando descoberta...")
    time.sleep(20)
    
    server_info = discovery.get_server_info()
    if server_info:
        print(f"✅ Servidor encontrado: {server_info[0]}:{server_info[1]}")
        details = discovery.get_server_details()
        print(f"   Método: {details.get('properties', {}).get('discovered_via', 'mDNS')}")
    else:
        print("❌ Nenhum servidor encontrado")
    
    discovery.stop_discovery()
    
    return server_info is not None

if __name__ == "__main__":
    test_updated_discovery()
"""
    
    with open("test_network_updated.py", 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ Script de teste criado: test_network_updated.py")
    
    # 4. Informações finais
    print("\n" + "=" * 50)
    print("CONFIGURAÇÃO CONCLUÍDA!")
    print("\nPara testar entre máquinas diferentes:")
    print("1. Máquina A: python pobchecker_server.py")
    print("2. Máquina B: python test_network_updated.py")
    print("3. Máquina B: python start_sync_service.py")
    
    print("\nRecursos habilitados:")
    print("✅ Descoberta mDNS (se disponível)")
    print("✅ Descoberta HTTP local")
    print("✅ Descoberta HTTP rede (scan de IP)")
    print("✅ Funcionamento entre máquinas diferentes")
    
    print("\nRanges de rede que serão escaneados:")
    print("- 192.168.0.0/24")
    print("- 192.168.1.0/24")
    print("- 10.0.0.0/24")
    print("- 172.16.0.0/24")
    print("- Range detectado automaticamente")

if __name__ == "__main__":
    setup_network_discovery()
