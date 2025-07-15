#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Inicializador do POBChecker Terminal.
Este script testa se o terminal pode ser inicializado e oferece opções.
"""

import sys
import os

def main():
    """
    Função principal.
    """
    print("🚀 POBChecker Terminal")
    print("=" * 30)
    
    try:
        # Verifica se pode importar
        from pobchecker_terminal import AttendanceChecker
        print("✓ Módulo carregado com sucesso")
        
        # Pergunta se quer inicializar
        print("\nOpções:")
        print("1. Inicializar Terminal (Interface Gráfica)")
        print("2. Testar apenas inicialização")
        print("3. Cancelar")
        
        choice = input("\nEscolha (1-3): ").strip()
        
        if choice == '1':
            print("🖥️ Iniciando interface gráfica...")
            app = AttendanceChecker()
            app.mainloop()
            
        elif choice == '2':
            print("🔍 Testando inicialização sem interface...")
            app = AttendanceChecker()
            print("✓ Terminal inicializado com sucesso!")
            print(f"  Modo: {app.current_mode}")
            print(f"  Grupo: {app.current_group}")
            print(f"  Rede: {'✓' if app.network_available else '✗'}")
            
        else:
            print("Operação cancelada.")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Operação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
