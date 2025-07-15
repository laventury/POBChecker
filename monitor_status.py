#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor de status do sistema POBChecker
"""

import time
import requests
import json
import os
import sys
from datetime import datetime

def clear_screen():
    """Limpa a tela"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_terminal_status():
    """Obtém status do terminal"""
    try:
        from database import Database
        db = Database()
        cursor = db.conn.cursor()
        
        # Contadores
        cursor.execute("SELECT COUNT(*) FROM check_in_out")
        checkin_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM check_event")
        event_count = cursor.fetchone()[0]
        
        # Último check-in
        cursor.execute("SELECT CPF, Name, Type, Timestamp FROM check_in_out ORDER BY Timestamp DESC LIMIT 1")
        last_checkin = cursor.fetchone()
        
        return {
            'status': 'online',
            'checkin_count': checkin_count,
            'event_count': event_count,
            'last_checkin': last_checkin
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def get_consolidator_status():
    """Obtém status do consolidador"""
    try:
        response = requests.get("http://localhost:8000/api/v1/pob/status", timeout=2)
        if response.status_code == 200:
            pob_data = response.json()
            
            # Status dos terminais
            terminals_response = requests.get("http://localhost:8000/api/v1/terminals/status", timeout=2)
            terminals = terminals_response.json() if terminals_response.status_code == 200 else []
            
            return {
                'status': 'online',
                'pob_total': pob_data.get('pob_total', 0),
                'people_count': len(pob_data.get('people_status', {})),
                'terminals': terminals
            }
        else:
            return {'status': 'error', 'error': f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {'status': 'offline', 'error': str(e)}

def get_sync_status():
    """Obtém status da sincronização"""
    try:
        from sync_service import SyncService
        sync_service = SyncService()
        
        # Testa descoberta
        sync_service.discovery.start_discovery()
        time.sleep(1)
        server_info = sync_service.discovery.get_server_info()
        sync_service.discovery.stop_discovery()
        
        return {
            'terminal_id': sync_service.terminal_id,
            'location': sync_service.location,
            'api_key_configured': bool(sync_service.api_key),
            'sync_interval': sync_service.sync_interval,
            'server_discovered': server_info is not None,
            'server_info': server_info if server_info else None,
            'is_running': sync_service.is_running
        }
        
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def display_status():
    """Exibe status completo"""
    clear_screen()
    
    print("🔍 MONITOR DE STATUS POBChecker")
    print("=" * 60)
    print(f"Atualizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Status do Terminal
    print("\n📱 TERMINAL:")
    terminal_status = get_terminal_status()
    if terminal_status['status'] == 'online':
        print(f"   Status: ✅ Online")
        print(f"   Check-ins: {terminal_status['checkin_count']}")
        print(f"   Eventos: {terminal_status['event_count']}")
        if terminal_status['last_checkin']:
            last = terminal_status['last_checkin']
            print(f"   Último check-in: {last[1]} ({last[2]}) - {last[3]}")
    else:
        print(f"   Status: ❌ Erro - {terminal_status.get('error', 'Desconhecido')}")
    
    # Status do Consolidador
    print("\n🌐 CONSOLIDADOR:")
    consolidator_status = get_consolidator_status()
    if consolidator_status['status'] == 'online':
        print(f"   Status: ✅ Online")
        print(f"   POB Total: {consolidator_status['pob_total']}")
        print(f"   Pessoas no sistema: {consolidator_status['people_count']}")
        print(f"   Terminais conectados: {len(consolidator_status['terminals'])}")
        
        for terminal in consolidator_status['terminals']:
            print(f"     - {terminal['terminal_id']}: {terminal['status']}")
    else:
        print(f"   Status: ❌ {consolidator_status['status'].title()}")
        if 'error' in consolidator_status:
            print(f"   Erro: {consolidator_status['error']}")
    
    # Status da Sincronização
    print("\n🔄 SINCRONIZAÇÃO:")
    sync_status = get_sync_status()
    if 'error' not in sync_status:
        print(f"   Terminal ID: {sync_status['terminal_id']}")
        print(f"   Localização: {sync_status['location']}")
        print(f"   API Key: {'✅' if sync_status['api_key_configured'] else '❌'}")
        print(f"   Intervalo: {sync_status['sync_interval']}s")
        print(f"   Descoberta mDNS: {'✅' if sync_status['server_discovered'] else '❌'}")
        print(f"   Serviço ativo: {'✅' if sync_status['is_running'] else '❌'}")
        
        if sync_status['server_info']:
            print(f"   Servidor descoberto: {sync_status['server_info'][0]}:{sync_status['server_info'][1]}")
    else:
        print(f"   Status: ❌ Erro - {sync_status['error']}")
    
    print("\n" + "=" * 60)
    print("Pressione Ctrl+C para sair | Atualização automática a cada 5s")

def main():
    """Função principal"""
    try:
        while True:
            display_status()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no monitor: {e}")

if __name__ == "__main__":
    main()
