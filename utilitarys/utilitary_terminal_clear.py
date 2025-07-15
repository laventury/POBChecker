#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo: utilitary_terminal_clear.py
Descrição: Script utilitário para limpeza de dados dos terminais
"""

import sys
import os

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

def show_menu():
    """Mostra o menu de opções"""
    print("\n" + "=" * 50)
    print("POBCHECKER - LIMPEZA DE DADOS DOS TERMINAIS")
    print("=" * 50)
    print("1. Limpar TODOS os dados (POB + Eventos + Pessoas)")
    print("2. Limpar apenas registros de presença (POB)")
    print("3. Limpar apenas eventos")
    print("4. Limpar dados do consolidador")
    print("5. Mostrar estatísticas do banco")
    print("6. Sair")
    print("=" * 50)

def show_stats(db):
    """Mostra estatísticas do banco de dados"""
    try:
        # Conta registros em cada tabela usando consultas SQL diretas
        cursor = db.cursor
        
        # Conta pessoas cadastradas
        cursor.execute("SELECT COUNT(*) FROM POB")
        people_count = cursor.fetchone()[0]
        
        # Conta pessoas no POB atual (onshore = 0)
        cursor.execute("SELECT COUNT(*) FROM POB WHERE Onshore = 0")
        pob_count = cursor.fetchone()[0]
        
        # Conta eventos
        cursor.execute("SELECT COUNT(*) FROM EVENTS")
        events_count = cursor.fetchone()[0]
        
        # Conta registros de check_event
        cursor.execute("SELECT COUNT(*) FROM CHECK_EVENT")
        checks_count = cursor.fetchone()[0]
        
        # Conta registros CHECK_IN_OUT
        try:
            cursor.execute("SELECT COUNT(*) FROM CHECK_IN_OUT")
            checkin_out_count = cursor.fetchone()[0]
        except:
            checkin_out_count = 0
        
        print(f"\n📊 ESTATÍSTICAS DO BANCO DE DADOS")
        print(f"   Total de pessoas cadastradas: {people_count}")
        print(f"   Pessoas no POB atualmente: {pob_count}")
        print(f"   Total de eventos: {events_count}")
        print(f"   Total de registros de check: {checks_count}")
        print(f"   Total de registros check in/out: {checkin_out_count}")
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")

def clear_all_data(db):
    """Limpa todos os dados do banco"""
    print("🗑️  Limpando TODOS os dados...")
    try:
        cursor = db.cursor
        
        # Limpa todas as tabelas
        cursor.execute("DELETE FROM CHECK_EVENT")
        cursor.execute("DELETE FROM CHECK_IN_OUT")
        cursor.execute("DELETE FROM EVENTS")
        cursor.execute("DELETE FROM POB")
        
        # Reseta os contadores de ID automático
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('POB', 'EVENTS', 'CHECK_EVENT', 'CHECK_IN_OUT')")
        
        db.conn.commit()
        print("✅ Todos os dados foram removidos com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao limpar dados: {e}")

def clear_pob_only(db):
    """Limpa apenas registros de presença (POB)"""
    print("🗑️  Limpando registros de presença...")
    try:
        cursor = db.cursor
        
        # Primeiro remove os registros relacionados
        cursor.execute("DELETE FROM CHECK_EVENT")
        cursor.execute("DELETE FROM CHECK_IN_OUT")
        
        # Depois remove o POB
        cursor.execute("DELETE FROM POB")
        
        # Reseta os contadores
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('POB', 'CHECK_EVENT', 'CHECK_IN_OUT')")
        print("✅ IDs de POB, CHECK_EVENT e CHECK_IN_OUT resetados")
        
        db.conn.commit()
        print("✅ Registros de presença removidos com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao limpar registros de presença: {e}")

def clear_events_only(db):
    """Limpa apenas eventos"""
    print("🗑️  Limpando eventos...")
    try:
        cursor = db.cursor
        
        # Remove check_events primeiro (integridade referencial)
        cursor.execute("DELETE FROM CHECK_EVENT")
        cursor.execute("DELETE FROM EVENTS")
        
        # Reseta contadores
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('EVENTS', 'CHECK_EVENT')")
        
        db.conn.commit()
        print("✅ Eventos removidos com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao limpar eventos: {e}")

def clear_consolidator_data():
    """Limpa dados do consolidador"""
    print("🗑️  Limpando dados do consolidador...")
    
    try:
        # Tenta importar e limpar dados do consolidador
        from pobchecker_server import ConsolidatorServer
        
        print("⚠️  Esta operação irá limpar todos os dados do consolidador.")
        print("   • Eventos consolidados")
        print("   • Status dos terminais")
        print("   • Correlações")
        print("   • Logs de sincronização")
        
        confirm = input("\nDeseja continuar? (digite 'SIM'): ")
        if confirm.upper() != 'SIM':
            print("❌ Operação cancelada.")
            return
        
        server = ConsolidatorServer()
        
        # Limpa dados do consolidador
        if hasattr(server.db, 'clear_all_data'):
            server.db.clear_all_data()
            print("✅ Dados do consolidador limpos!")
        else:
            print("⚠️  Método de limpeza não disponível no consolidador")
            
    except ImportError:
        print("⚠️  Consolidador não disponível (pobchecker_server não encontrado)")
    except Exception as e:
        print(f"❌ Erro ao limpar dados do consolidador: {e}")

def main():
    """Função principal"""
    print("🚀 POBCHECKER - LIMPEZA DE DADOS v2.0")
    
    # Conecta ao banco
    try:
        db = Database()
        print("✅ Conectado ao banco de dados")
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "1":
                confirm = input("⚠️  ATENÇÃO: Isso irá remover TODOS os dados. Confirma? (digite 'SIM'): ")
                if confirm.upper() == "SIM":
                    clear_all_data(db)
                else:
                    print("❌ Operação cancelada")
                    
            elif choice == "2":
                confirm = input("⚠️  Confirma limpar registros de presença? (digite 'SIM'): ")
                if confirm.upper() == "SIM":
                    clear_pob_only(db)
                else:
                    print("❌ Operação cancelada")
                    
            elif choice == "3":
                confirm = input("⚠️  Confirma limpar eventos? (digite 'SIM'): ")
                if confirm.upper() == "SIM":
                    clear_events_only(db)
                else:
                    print("❌ Operação cancelada")
                    
            elif choice == "4":
                clear_consolidator_data()
                
            elif choice == "5":
                show_stats(db)
                
            elif choice == "6":
                print("👋 Saindo...")
                break
                
            else:
                print("❌ Opção inválida")
                
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    # Fecha conexão
    db.conn.close()

if __name__ == "__main__":
    main()
