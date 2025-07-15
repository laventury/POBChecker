#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de sincronização entre terminal e consolidador
"""

import sys
import os
import json
import requests
import time
from datetime import datetime

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_terminal_database():
    """Testa se há dados no banco do terminal"""
    try:
        from database import Database
        db = Database()
        
        print("=== DADOS DO TERMINAL ===")
        
        # Verifica check_in_out
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM check_in_out")
        checkin_count = cursor.fetchone()[0]
        print(f"Total de check-ins/outs: {checkin_count}")
        
        if checkin_count > 0:
            cursor.execute("SELECT CPF, Name, Type, Timestamp FROM check_in_out ORDER BY Timestamp DESC LIMIT 5")
            recent_checkins = cursor.fetchall()
            print("Últimos check-ins/outs:")
            for row in recent_checkins:
                print(f"  {row[0]} - {row[1]} - {row[2]} - {row[3]}")
        
        # Verifica check_event
        cursor.execute("SELECT COUNT(*) FROM check_event")
        event_count = cursor.fetchone()[0]
        print(f"Total de eventos: {event_count}")
        
        if event_count > 0:
            cursor.execute("SELECT CPF, Name, Event, Timestamp FROM check_event ORDER BY Timestamp DESC LIMIT 5")
            recent_events = cursor.fetchall()
            print("Últimos eventos:")
            for row in recent_events:
                print(f"  {row[0]} - {row[1]} - Evento {row[2]} - {row[3]}")
        
        return {'checkin_count': checkin_count, 'event_count': event_count}
        
    except Exception as e:
        print(f"Erro ao acessar banco do terminal: {e}")
        return None

def test_consolidator_database():
    """Testa se há dados no banco do consolidador"""
    try:
        consolidator_url = "http://localhost:8000"
        
        print("\n=== DADOS DO CONSOLIDADOR ===")
        
        # Testa status POB
        response = requests.get(f"{consolidator_url}/api/v1/pob/status", timeout=5)
        if response.status_code == 200:
            pob_data = response.json()
            print(f"POB Total: {pob_data['pob_total']}")
            print(f"Pessoas no sistema: {len(pob_data['people_status'])}")
            
            if pob_data['people_status']:
                print("Pessoas registradas:")
                for cpf, info in list(pob_data['people_status'].items())[:5]:
                    print(f"  {cpf} - {info['name']} - {info['status']}")
        
        # Testa eventos ativos
        response = requests.get(f"{consolidator_url}/api/v1/events/active", timeout=5)
        if response.status_code == 200:
            events = response.json()
            print(f"Eventos ativos: {len(events)}")
            
        # Testa status dos terminais
        response = requests.get(f"{consolidator_url}/api/v1/terminals/status", timeout=5)
        if response.status_code == 200:
            terminals = response.json()
            print(f"Terminais registrados: {len(terminals)}")
            for terminal in terminals:
                print(f"  {terminal['terminal_id']} - {terminal['status']} - Última sync: {terminal['last_sync']}")
        
        return True
        
    except Exception as e:
        print(f"Erro ao acessar consolidador: {e}")
        return False

def test_sync_service():
    """Testa o serviço de sincronização"""
    try:
        print("\n=== TESTE DO SERVIÇO DE SYNC ===")
        
        from sync_service import SyncService
        sync_service = SyncService()
        
        # Verifica configuração
        print(f"Terminal ID: {sync_service.terminal_id}")
        print(f"Localização: {sync_service.location}")
        print(f"API Key: {'Configurada' if sync_service.api_key else 'Não configurada'}")
        print(f"Intervalo de sync: {sync_service.sync_interval}s")
        
        # Testa descoberta de serviço
        print("\nTestando descoberta de serviço...")
        try:
            # Inicia descoberta
            sync_service.discovery.start_discovery()
            time.sleep(2)  # Aguarda descoberta
            
            server_info = sync_service.discovery.get_server_info()
            if server_info:
                print(f"Servidor descoberto: {server_info[0]}:{server_info[1]}")
            else:
                print("Nenhum servidor descoberto via mDNS")
                
            # Para descoberta
            sync_service.discovery.stop_discovery()
        except Exception as e:
            print(f"Erro na descoberta: {e}")
            
        # Testa sincronização manual
        print("\nTestando sincronização manual...")
        try:
            result = sync_service.force_sync()
            print(f"Resultado da sincronização: {result}")
        except Exception as e:
            print(f"Erro na sincronização: {e}")
        
        return True
        
    except Exception as e:
        print(f"Erro no teste de sincronização: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manual_sync():
    """Testa sincronização manual com dados de teste"""
    try:
        print("\n=== TESTE DE SINCRONIZAÇÃO MANUAL ===")
        
        # Carrega configuração
        with open("terminal_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        terminal_config = config['terminal_config']
        
        consolidator_url = "http://localhost:8000"
        terminal_id = terminal_config['terminal_id']
        location = terminal_config['location']
        api_key = terminal_config.get('network', {}).get('api_key', '')
        
        print(f"Enviando para: {consolidator_url}")
        print(f"Terminal ID: {terminal_id}")
        print(f"Localização: {location}")
        
        # Prepara dados de teste
        test_data = {
            'terminal_id': terminal_id,
            'location': location,
            'check_events': [],
            'check_in_outs': []
        }
        
        # Pega dados reais do banco
        from database import Database
        db = Database()
        cursor = db.conn.cursor()
        
        # Dados de check_in_out
        cursor.execute("SELECT id, CPF, Name, Type, Timestamp FROM check_in_out ORDER BY Timestamp DESC LIMIT 10")
        checkins = cursor.fetchall()
        
        for row in checkins:
            test_data['check_in_outs'].append({
                'id': row[0],
                'CPF': row[1],
                'Name': row[2],
                'Type': row[3],
                'Timestamp': row[4]
            })
        
        # Dados de check_event
        cursor.execute("SELECT id, CPF, Name, Event, Timestamp FROM check_event ORDER BY Timestamp DESC LIMIT 10")
        events = cursor.fetchall()
        
        for row in events:
            test_data['check_events'].append({
                'id': row[0],
                'CPF': row[1],
                'Name': row[2],
                'Event': row[3],
                'Timestamp': row[4]
            })
        
        print(f"Enviando {len(test_data['check_in_outs'])} check-ins/outs")
        print(f"Enviando {len(test_data['check_events'])} eventos")
        
        # Envia dados
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['X-API-Key'] = api_key
        
        response = requests.post(
            f"{consolidator_url}/sync",
            json=test_data,
            headers=headers,
            timeout=30
        )
        
        print(f"Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Eventos recebidos: {result.get('check_events_received', 0)}")
            print(f"Check-ins recebidos: {result.get('check_in_outs_received', 0)}")
            print("✅ Sincronização bem-sucedida!")
        else:
            print(f"❌ Erro na sincronização: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Erro na sincronização manual: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 DIAGNÓSTICO DE SINCRONIZAÇÃO POBChecker")
    print("=" * 50)
    
    # Testa banco do terminal
    terminal_data = test_terminal_database()
    
    # Testa banco do consolidador
    consolidator_ok = test_consolidator_database()
    
    # Testa serviço de sync
    sync_ok = test_sync_service()
    
    # Testa sincronização manual
    manual_sync_ok = test_manual_sync()
    
    print("\n" + "=" * 50)
    print("RESUMO DO DIAGNÓSTICO:")
    print(f"Terminal com dados: {'✅' if terminal_data and (terminal_data['checkin_count'] > 0 or terminal_data['event_count'] > 0) else '❌'}")
    print(f"Consolidador acessível: {'✅' if consolidator_ok else '❌'}")
    print(f"Serviço de sync: {'✅' if sync_ok else '❌'}")
    print(f"Sincronização manual: {'✅' if manual_sync_ok else '❌'}")
    
    if not consolidator_ok:
        print("\n🔧 SOLUÇÕES POSSÍVEIS:")
        print("1. Verificar se o consolidador está rodando (python pobchecker_server.py)")
        print("2. Verificar se a URL está correta")
        print("3. Verificar firewall/proxy")
    
    if terminal_data and (terminal_data['checkin_count'] > 0 or terminal_data['event_count'] > 0) and not manual_sync_ok:
        print("\n🔧 PROBLEMA DE SINCRONIZAÇÃO:")
        print("1. Verificar configuração da API key")
        print("2. Verificar logs do consolidador")
        print("3. Verificar se o serviço de descoberta está funcionando")

if __name__ == "__main__":
    main()
