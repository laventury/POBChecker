#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Inicializador do Servidor Consolidador POBChecker.
"""

import sys
import os

def main():
    """
    Função principal.
    """
    print("🚀 Servidor Consolidador POBChecker")
    print("=" * 40)
    
    try:
        # Verifica configuração
        with open('consolidator_config.json', 'r') as f:
            import json
            config = json.load(f)
            db_type = config.get('consolidator_config', {}).get('database', {}).get('type', 'sqlite')
            print(f"Configuração: {db_type}")
        
        # Inicia servidor
        from pobchecker_server import ConsolidatorServer
        
        print("Iniciando servidor...")
        server = ConsolidatorServer()
        
        print(f"✅ Servidor iniciado com sucesso!")
        print(f"   Banco: {server.db.db_type}")
        print(f"   Acesse: http://localhost:8000")
        
        # Inicia o servidor
        server.start()
        
    except KeyboardInterrupt:
        print("\n⚠️ Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Operação cancelada pelo usuário.")
        sys.exit(1)
