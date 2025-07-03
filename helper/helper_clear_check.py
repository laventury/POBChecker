#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo: helper_clear_check.py
Descrição: Script auxiliar para limpeza apenas dos registros de presença
Antigo nome: aux_clear_check.py (renomeado de aux para helper)
"""

import sys
import os

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

def clear_check_records():
    """Limpa apenas os registros de presença (check in/out)"""
    print("POBCHECKER - LIMPEZA DE REGISTROS DE PRESENÇA")
    print("=" * 50)
    
    try:
        db = Database()
        cursor = db.cursor
        
        # Mostra estatísticas antes
        cursor.execute("SELECT COUNT(*) FROM POB")
        pob_count_before = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM CHECKS")
        checks_count_before = cursor.fetchone()[0]
        
        print(f"📊 Antes da limpeza:")
        print(f"   Pessoas no POB: {pob_count_before}")
        print(f"   Registros de check: {checks_count_before}")
        
        # Confirma a operação
        print(f"\n⚠️  Esta operação irá limpar apenas os registros de presença.")
        print(f"   • Pessoas cadastradas: MANTIDAS")
        print(f"   • Eventos: MANTIDOS")
        print(f"   • Registros de check: REMOVIDOS")
        print(f"   • POB atual: ZERADO")
        
        confirm = input("\nConfirmar limpeza? (s/N): ")
        
        if confirm.lower() != 's':
            print("❌ Operação cancelada.")
            return False
        
        print("\n🧹 Iniciando limpeza...")
        
        # Limpa registros de presença
        cursor.execute("DELETE FROM POB")
        print("✅ Registros de POB limpos")
        
        # Limpa registros de check
        cursor.execute("DELETE FROM CHECKS")
        print("✅ Registros de check limpos")
        
        # Reset dos IDs auto-incremento apenas para essas tabelas
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('POB', 'CHECKS')")
        print("✅ IDs de POB e CHECKS resetados")
        
        db.conn.commit()
        
        # Mostra estatísticas depois
        cursor.execute("SELECT COUNT(*) FROM POB")
        people_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM EVENTS")
        events_count = cursor.fetchone()[0]
        
        print(f"\n🎉 Limpeza concluída com sucesso!")
        print(f"\n📊 Após a limpeza:")
        print(f"   Pessoas cadastradas: {people_count} (mantidas)")
        print(f"   Pessoas no POB: 0")
        print(f"   Eventos: {events_count} (mantidos)")
        print(f"   Registros de check: 0")
        
    except Exception as e:
        print(f"❌ Erro durante limpeza: {e}")
        return False
    
    return True

if __name__ == "__main__":
    clear_check_records()
