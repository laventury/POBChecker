#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo: utilitary_terminal_manage.py
Descrição: Gerenciamento de dados dos terminais POBChecker
"""

import sys
import os

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

def show_menu():
    """Mostra o menu de opções"""
    print("\n" + "=" * 60)
    print("POBCHECKER - GERENCIAMENTO DE DADOS DOS TERMINAIS")
    print("=" * 60)
    print("1. Visualizar estatísticas dos terminais")
    print("2. Listar pessoas cadastradas")
    print("3. Listar pessoas no POB atual")
    print("4. Listar eventos ativos")
    print("5. Listar histórico de check-ins/outs")
    print("6. Backup dos dados dos terminais")
    print("7. Verificar integridade dos dados")
    print("8. Compactar banco de dados")
    print("0. Voltar")
    print("=" * 60)

def show_terminal_stats():
    """Mostra estatísticas dos terminais"""
    print("\n📊 Estatísticas dos terminais...")
    
    try:
        db = Database()
        cursor = db.cursor
        
        # Estatísticas básicas
        cursor.execute("SELECT COUNT(*) FROM POB")
        total_people = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM POB WHERE Onshore = 0")
        people_onboard = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM POB WHERE Onshore = 1")
        people_onshore = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM EVENTS")
        total_events = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM EVENTS WHERE Closed = 0")
        active_events = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM CHECK_EVENT")
        total_checks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM CHECK_IN_OUT")
        total_movements = cursor.fetchone()[0]
        
        print(f"📋 PESSOAS:")
        print(f"   Total cadastradas: {total_people}")
        print(f"   🚢 No POB (offshore): {people_onboard}")
        print(f"   🏠 Em terra (onshore): {people_onshore}")
        
        print(f"\n📅 EVENTOS:")
        print(f"   Total de eventos: {total_events}")
        print(f"   ⚡ Eventos ativos: {active_events}")
        
        print(f"\n✅ ATIVIDADES:")
        print(f"   Registros de check: {total_checks}")
        print(f"   Movimentações (in/out): {total_movements}")
        
        # Estatísticas por grupo
        cursor.execute("SELECT GroupNumber, COUNT(*) FROM POB GROUP BY GroupNumber ORDER BY GroupNumber")
        groups = cursor.fetchall()
        
        if groups:
            print(f"\n👥 DISTRIBUIÇÃO POR GRUPO:")
            for group_num, count in groups:
                cursor.execute("SELECT COUNT(*) FROM POB WHERE GroupNumber = ? AND Onshore = 0", (group_num,))
                onboard_count = cursor.fetchone()[0]
                print(f"   Grupo {group_num}: {count} pessoas ({onboard_count} no POB)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")
        return False

def list_registered_people():
    """Lista pessoas cadastradas"""
    print("\n👥 Listando pessoas cadastradas...")
    
    try:
        db = Database()
        cursor = db.cursor
        
        cursor.execute("SELECT CPF, Name, GroupNumber, Onshore FROM POB ORDER BY Name")
        people = cursor.fetchall()
        
        if people:
            print(f"\n📋 {len(people)} pessoas cadastradas:")
            for cpf, name, group, onshore in people:
                status = "🏠 Em terra" if onshore else "🚢 No POB"
                print(f"   {name} | CPF: {cpf} | Grupo: {group} | {status}")
        else:
            print("ℹ️  Nenhuma pessoa cadastrada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao listar pessoas: {e}")
        return False

def list_people_onboard():
    """Lista pessoas no POB atual"""
    print("\n🚢 Listando pessoas no POB atual...")
    
    try:
        db = Database()
        cursor = db.cursor
        
        cursor.execute("SELECT CPF, Name, GroupNumber FROM POB WHERE Onshore = 0 ORDER BY Name")
        people = cursor.fetchall()
        
        if people:
            print(f"\n📋 {len(people)} pessoas no POB:")
            for cpf, name, group in people:
                print(f"   {name} | CPF: {cpf} | Grupo: {group}")
        else:
            print("ℹ️  Nenhuma pessoa no POB atualmente")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao listar pessoas no POB: {e}")
        return False

def list_active_events():
    """Lista eventos ativos"""
    print("\n📅 Listando eventos ativos...")
    
    try:
        db = Database()
        cursor = db.cursor
        
        cursor.execute("SELECT ID, Open, Close, Closed FROM EVENTS WHERE Closed = 0 ORDER BY ID DESC")
        events = cursor.fetchall()
        
        if events:
            print(f"\n📋 {len(events)} eventos ativos:")
            for event_id, open_time, close_time, closed in events:
                print(f"   Evento {event_id}: {open_time}")
                
                # Conta participantes
                cursor.execute("SELECT COUNT(*) FROM CHECK_EVENT WHERE Event = ?", (event_id,))
                participants = cursor.fetchone()[0]
                print(f"      👥 {participants} participantes")
        else:
            print("ℹ️  Nenhum evento ativo")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao listar eventos: {e}")
        return False

def list_movement_history():
    """Lista histórico de movimentações"""
    print("\n📋 Listando histórico de check-ins/outs...")
    
    try:
        db = Database()
        cursor = db.cursor
        
        cursor.execute("SELECT CPF, Name, Movement, Timestamp FROM CHECK_IN_OUT ORDER BY Timestamp DESC LIMIT 20")
        movements = cursor.fetchall()
        
        if movements:
            print(f"\n📋 Últimas 20 movimentações:")
            for cpf, name, movement, timestamp in movements:
                direction = "🚢 Embarcou" if movement == "IN" else "🏠 Desembarcou"
                print(f"   {timestamp} | {name} | {direction}")
        else:
            print("ℹ️  Nenhuma movimentação registrada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao listar movimentações: {e}")
        return False

def backup_terminal_data():
    """Faz backup dos dados dos terminais"""
    print("\n💾 Fazendo backup dos dados dos terminais...")
    
    try:
        import shutil
        from datetime import datetime
        
        # Nome do arquivo de backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"pobchecker_backup_{timestamp}.sqlite3"
        
        # Copia o arquivo
        shutil.copy2("pobchecker.sqlite3", backup_file)
        
        print(f"✅ Backup criado: {backup_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao fazer backup: {e}")
        return False

def check_data_integrity():
    """Verifica integridade dos dados"""
    print("\n🔍 Verificando integridade dos dados...")
    
    try:
        db = Database()
        cursor = db.cursor
        
        # Verifica integridade das tabelas
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]
        
        if integrity == "ok":
            print("✅ Integridade do banco: OK")
        else:
            print(f"⚠️  Problema de integridade: {integrity}")
        
        # Verifica consistência dos dados
        cursor.execute("SELECT COUNT(*) FROM CHECK_EVENT ce LEFT JOIN EVENTS e ON ce.Event = e.ID WHERE e.ID IS NULL")
        orphaned_checks = cursor.fetchone()[0]
        
        if orphaned_checks > 0:
            print(f"⚠️  {orphaned_checks} registros de check órfãos encontrados")
        else:
            print("✅ Consistência dos dados: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar integridade: {e}")
        return False

def compact_database():
    """Compacta o banco de dados"""
    print("\n🗜️  Compactando banco de dados...")
    
    try:
        db = Database()
        cursor = db.cursor
        
        # Executa VACUUM para compactar
        cursor.execute("VACUUM")
        
        print("✅ Banco de dados compactado com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao compactar banco: {e}")
        return False

def main():
    """Função principal"""
    print("POBCHECKER - GERENCIAMENTO DE DADOS DOS TERMINAIS")
    print("Sistema de gerenciamento de dados dos terminais POB")
    
    while True:
        show_menu()
        
        try:
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "0":
                print("👋 Voltando...")
                break
            elif choice == "1":
                show_terminal_stats()
            elif choice == "2":
                list_registered_people()
            elif choice == "3":
                list_people_onboard()
            elif choice == "4":
                list_active_events()
            elif choice == "5":
                list_movement_history()
            elif choice == "6":
                backup_terminal_data()
            elif choice == "7":
                check_data_integrity()
            elif choice == "8":
                compact_database()
            else:
                print("❌ Opção inválida. Tente novamente.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
