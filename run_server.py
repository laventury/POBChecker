#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Inicializa servidor e abre dashboard no navegador.
"""

import sys
import webbrowser
import time

def main():
    print("🚀 Iniciando Servidor POBChecker")
    print("=" * 35)
    
    try:
        from pobchecker_server import ConsolidatorServer
        
        print("Criando servidor...")
        server = ConsolidatorServer()
        
        print(f"✅ Servidor configurado!")
        print(f"   Banco: {server.db.db_type}")
        print(f"   Host: 0.0.0.0:8000")
        
        # Abre dashboard no navegador após 3 segundos
        def open_dashboard():
            time.sleep(3)
            webbrowser.open('http://localhost:8000/dashboard')
        
        import threading
        dashboard_thread = threading.Thread(target=open_dashboard, daemon=True)
        dashboard_thread.start()
        
        print("\n🌐 Iniciando servidor...")
        print("   Dashboard: http://localhost:8000/dashboard")
        print("   API: http://localhost:8000/docs")
        print("\n⏹️  Pressione Ctrl+C para parar\n")
        
        # Inicia servidor
        server.start()
        
    except KeyboardInterrupt:
        print("\n⚠️ Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
