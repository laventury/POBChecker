#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reinicia o consolidador com suporte a mDNS
"""

import requests
import time
import subprocess
import os
import sys

def stop_current_server():
    """Tenta parar o servidor atual"""
    print("🛑 Tentando parar servidor atual...")
    
    try:
        # Tenta fazer uma requisição para verificar se está rodando
        response = requests.get("http://localhost:8000/api/v1/system/health", timeout=2)
        if response.status_code == 200:
            print("✅ Servidor atual está rodando")
        else:
            print("⚠️ Servidor atual não está respondendo adequadamente")
    except:
        print("❌ Servidor atual não está rodando")
        return False
    
    # Instrui o usuário a parar o servidor
    print("📝 INSTRUÇÕES:")
    print("1. Vá ao terminal onde o consolidador está rodando")
    print("2. Pressione Ctrl+C para parar o servidor")
    print("3. Aguarde esta mensagem e pressione Enter quando o servidor parar")
    
    input("Pressione Enter quando o servidor estiver parado...")
    
    # Verifica se realmente parou
    try:
        response = requests.get("http://localhost:8000/api/v1/system/health", timeout=2)
        if response.status_code == 200:
            print("⚠️ Servidor ainda está rodando. Tente novamente.")
            return False
    except:
        print("✅ Servidor parado com sucesso")
        return True

def start_server_with_mdns():
    """Inicia o servidor com suporte a mDNS"""
    print("🚀 Iniciando servidor com suporte a mDNS...")
    
    try:
        # Verifica se o zeroconf está disponível
        import zeroconf
        print("✅ Biblioteca zeroconf disponível")
        
        # Inicia o servidor
        print("📡 Iniciando servidor consolidador com mDNS...")
        print("   Execute: python pobchecker_server.py")
        print("   O servidor agora terá suporte a mDNS!")
        
        return True
        
    except ImportError:
        print("❌ Biblioteca zeroconf não está disponível")
        print("   Instale com: pip install zeroconf")
        return False

def main():
    print("🔄 REINICIALIZADOR DO CONSOLIDADOR COM mDNS")
    print("=" * 50)
    
    # Para servidor atual
    if not stop_current_server():
        print("❌ Falha ao parar servidor atual")
        return
    
    # Inicia servidor com mDNS
    if start_server_with_mdns():
        print("\n✅ Servidor pronto para iniciar com mDNS!")
        print("   Execute em outro terminal: python pobchecker_server.py")
    else:
        print("\n❌ Falha ao configurar servidor com mDNS")

if __name__ == "__main__":
    main()
