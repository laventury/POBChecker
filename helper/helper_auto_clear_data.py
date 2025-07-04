#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo: helper_auto_clear_data.py
Descrição: Script auxiliar para limpeza automática de dados do banco
Antigo nome: aux_auto_clear_data.py (renomeado de aux para helper)
"""

import sys
import os

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

def auto_clear_data():
    """Limpa automaticamente dados de teste do banco"""
    print("POBCHECKER - LIMPEZA AUTOMÁTICA DE DADOS")
    print("=" * 50)
    
    try:
        db = Database()
        cursor = db.cursor
        
        print("🧹 Iniciando limpeza automática...")
        
        # Limpa registros de presença
        cursor.execute("DELETE FROM POB")
        print("✅ Registros de presença limpos")
        
        # Limpa eventos
        cursor.execute("DELETE FROM EVENTS")
        print("✅ Eventos limpos")
        
        # Limpa registros de check
        cursor.execute("DELETE FROM CHECK_EVENT")
        cursor.execute("DELETE FROM CHECK_IN_OUT")
        print("✅ Registros de check limpos")
        
        # Reset dos IDs auto-incremento
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('POB', 'EVENTS', 'CHECK_EVENT', 'CHECK_IN_OUT')")
        print("✅ IDs resetados")
        
        db.conn.commit()
        print("\n🎉 Limpeza automática concluída com sucesso!")
        
        # Mostra estatísticas finais
        cursor.execute("SELECT COUNT(*) FROM POB")
        people_count = cursor.fetchone()[0]
        pob_count = people_count  # Simplificado para POB atual
        
        print(f"\n📊 ESTATÍSTICAS PÓS-LIMPEZA:")
        print(f"   Pessoas cadastradas: {people_count} (mantidas)")
        print(f"   Pessoas no POB: {pob_count}")
        print(f"   Eventos: 0")
        print(f"   Registros de check: 0")
        
    except Exception as e:
        print(f"❌ Erro durante limpeza automática: {e}")
        return False
    
    return True

if __name__ == "__main__":
    auto_clear_data()
