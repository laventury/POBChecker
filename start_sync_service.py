#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Iniciador do serviço de sincronização automática
"""

import time
import signal
import sys
from sync_service import SyncService

# Controle do serviço
sync_service = None

def signal_handler(signum, frame):
    """Handler para parar o serviço graciosamente"""
    global sync_service
    print("\n🛑 Recebido sinal para parar o serviço...")
    if sync_service:
        sync_service.stop_sync_service()
    sys.exit(0)

def main():
    global sync_service
    
    print("🔄 INICIANDO SERVIÇO DE SINCRONIZAÇÃO AUTOMÁTICA")
    print("=" * 50)
    
    # Configura handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Inicializa serviço
        sync_service = SyncService()
        
        # Mostra configuração
        print(f"Terminal ID: {sync_service.terminal_id}")
        print(f"Localização: {sync_service.location}")
        print(f"API Key: {'Configurada' if sync_service.api_key else 'Não configurada'}")
        print(f"Intervalo: {sync_service.sync_interval}s")
        print("-" * 50)
        
        # Inicia serviço
        sync_service.start_sync_service()
        
        print("✅ Serviço de sincronização iniciado!")
        print("   Pressione Ctrl+C para parar")
        print("   Aguardando sincronizações...")
        
        # Loop principal
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Serviço parado pelo usuário")
        if sync_service:
            sync_service.stop_sync_service()
    except Exception as e:
        print(f"❌ Erro no serviço: {e}")
        import traceback
        traceback.print_exc()
        if sync_service:
            sync_service.stop_sync_service()

if __name__ == "__main__":
    main()
