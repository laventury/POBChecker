#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo: helper_clear_data.py
Descrição: Script auxiliar para limpeza interativa de dados do banco
Antigo nome: aux_clear_data.py (renomeado de aux para helper)
"""

import sys
import os

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

def show_menu():
    """Mostra o menu de opções"""
    print("\n" + "=" * 50)
    print("POBCHECKER - LIMPEZA DE DADOS")
    print("=" * 50)
    print("1. Limpar TODOS os dados (POB + Eventos + Pessoas)")
    print("2. Limpar apenas registros de presença (POB)")
    print("3. Limpar apenas eventos")
    print("4. Mostrar estatísticas do banco")
    print("5. Sair")
    print("=" * 50)

def show_stats(db):
    """Mostra estatísticas do banco de dados"""
    try:
        # Conta registros em cada tabela usando consultas SQL diretas
        cursor = db.cursor
        
        # Conta pessoas cadastradas
        cursor.execute("SELECT COUNT(*) FROM POB")
        people_count = cursor.fetchone()[0]
        
        # Conta pessoas no POB atual (assumindo que POB é a tabela atual)
        pob_count = people_count  # Simplificado
        
        # Conta eventos
        cursor.execute("SELECT COUNT(*) FROM EVENTS")
        events_count = cursor.fetchone()[0]
        
        # Conta registros de check
        cursor.execute("SELECT COUNT(*) FROM CHECKS")
        checks_count = cursor.fetchone()[0]
        
        print(f"\n📊 ESTATÍSTICAS DO BANCO DE DADOS")
        print(f"   Pessoas cadastradas: {people_count}")
        print(f"   Pessoas no POB atual: {pob_count}")
        print(f"   Total de eventos: {events_count}")
        print(f"   Total de registros de check: {checks_count}")
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")

def clear_all_data(db):
    """Limpa todos os dados do banco"""
    print("\n⚠️  ATENÇÃO: Esta operação irá remover TODOS os dados!")
    confirm = input("Digite 'CONFIRMAR' para prosseguir: ")
    
    if confirm != "CONFIRMAR":
        print("❌ Operação cancelada.")
        return
    
    try:
        cursor = db.cursor
        
        # Limpa todas as tabelas
        cursor.execute("DELETE FROM POB")
        cursor.execute("DELETE FROM EVENTS")
        cursor.execute("DELETE FROM CHECKS")
        # Nota: Não há tabela PERSONNEL, só POB
        
        # Reset dos IDs auto-incremento
        cursor.execute("DELETE FROM sqlite_sequence")
        
        db.conn.commit()
        print("✅ Todos os dados foram removidos com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao limpar dados: {e}")

def clear_pob_only(db):
    """Limpa apenas os registros de presença"""
    print("\n⚠️  Esta operação irá remover apenas os registros de presença (POB).")
    confirm = input("Confirmar? (s/N): ")
    
    if confirm.lower() != 's':
        print("❌ Operação cancelada.")
        return
    
    try:
        cursor = db.cursor
        cursor.execute("DELETE FROM POB")
        db.conn.commit()
        print("✅ Registros de presença removidos com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao limpar POB: {e}")

def clear_events_only(db):
    """Limpa apenas os eventos"""
    print("\n⚠️  Esta operação irá remover apenas os eventos.")
    confirm = input("Confirmar? (s/N): ")
    
    if confirm.lower() != 's':
        print("❌ Operação cancelada.")
        return
    
    try:
        cursor = db.cursor
        cursor.execute("DELETE FROM EVENTS")
        db.conn.commit()
        print("✅ Eventos removidos com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao limpar eventos: {e}")

def main():
    """Função principal"""
    try:
        db = Database()
        
        while True:
            show_menu()
            show_stats(db)
            
            choice = input("\nEscolha uma opção: ")
            
            if choice == "1":
                clear_all_data(db)
            elif choice == "2":
                clear_pob_only(db)
            elif choice == "3":
                clear_events_only(db)
            elif choice == "4":
                show_stats(db)
            elif choice == "5":
                print("👋 Saindo...")
                break
            else:
                print("❌ Opção inválida!")
                
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")

if __name__ == "__main__":
    main()
