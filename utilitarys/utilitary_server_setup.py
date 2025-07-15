#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo: utilitary_server_setup.py
Descrição: Script utilitário para configurar e inicializar o consolidador
"""

import sys
import os
import json
import subprocess
import time

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show_menu():
    """Mostra o menu de opções do consolidador"""
    print("\n" + "=" * 60)
    print("POBCHECKER - CONFIGURAÇÃO DO CONSOLIDADOR")
    print("=" * 60)
    print("1. Configurar banco PostgreSQL")
    print("2. Testar conexão com banco")
    print("3. Configurar parâmetros do consolidador")
    print("4. Inicializar servidor consolidador")
    print("5. Verificar status do consolidador")
    print("6. Limpar dados do consolidador")
    print("0. Voltar")
    print("=" * 60)

def configure_postgresql():
    """Configura conexão PostgreSQL"""
    print("\nConfigurando PostgreSQL...")
    
    try:
        # Carrega configuração atual
        config_path = "consolidator_config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            print("❌ Arquivo de configuração não encontrado!")
            return False
            
        # Configurações PostgreSQL
        print("\nConfiguração do PostgreSQL:")
        print(f"Host atual: {config['consolidator_config']['database']['postgresql']['host']}")
        print(f"Porta atual: {config['consolidator_config']['database']['postgresql']['port']}")
        print(f"Banco atual: {config['consolidator_config']['database']['postgresql']['name']}")
        print(f"Usuário atual: {config['consolidator_config']['database']['postgresql']['user']}")
        
        # Pergunta se deseja alterar
        if input("\nDeseja alterar as configurações? (s/N): ").lower() == 's':
            config['consolidator_config']['database']['postgresql']['host'] = input("Novo host (Enter para manter atual): ") or config['consolidator_config']['database']['postgresql']['host']
            config['consolidator_config']['database']['postgresql']['port'] = int(input("Nova porta (Enter para manter atual): ") or config['consolidator_config']['database']['postgresql']['port'])
            config['consolidator_config']['database']['postgresql']['name'] = input("Nome do banco (Enter para manter atual): ") or config['consolidator_config']['database']['postgresql']['name']
            config['consolidator_config']['database']['postgresql']['user'] = input("Usuário (Enter para manter atual): ") or config['consolidator_config']['database']['postgresql']['user']
            
            # Senha (opcional)
            if input("Alterar senha? (s/N): ").lower() == 's':
                config['consolidator_config']['database']['postgresql']['password'] = input("Nova senha: ")
            
            # Salva configuração
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print("✅ Configurações salvas!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar PostgreSQL: {e}")
        return False

def test_database_connection():
    """Testa conexão com o banco"""
    print("\nTestando conexão com banco...")
    
    try:
        # Executa o script de configuração
        result = subprocess.run([sys.executable, "configure_consolidator_postgresql.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Conexão com banco estabelecida!")
            return True
        else:
            print(f"❌ Erro na conexão: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar conexão: {e}")
        return False

def configure_consolidator():
    """Configura parâmetros do consolidador"""
    print("\nConfigurando parâmetros do consolidador...")
    
    try:
        config_path = "consolidator_config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            print("❌ Arquivo de configuração não encontrado!")
            return False
        
        # Configurações do servidor
        print("\nConfiguração do servidor:")
        print(f"Host: {config['consolidator_config']['server']['host']}")
        print(f"Porta: {config['consolidator_config']['server']['port']}")
        print(f"Debug: {config['consolidator_config']['server']['debug']}")
        
        # Configurações de correlação
        print("\nConfiguração de correlação:")
        print(f"Tolerância (min): {config['consolidator_config']['correlation']['tolerance_minutes']}")
        print(f"Auto-correlação: {config['consolidator_config']['correlation']['auto_correlate']}")
        
        # Configurações de interface
        print("\nConfiguração de interface:")
        print(f"Tema: {config['consolidator_config']['interface']['theme']}")
        print(f"Auto-refresh (s): {config['consolidator_config']['interface']['auto_refresh_seconds']}")
        
        # Pergunta se deseja alterar
        if input("\nDeseja alterar alguma configuração? (s/N): ").lower() == 's':
            # Permite alterar algumas configurações básicas
            new_port = input(f"Nova porta do servidor (atual: {config['consolidator_config']['server']['port']}): ")
            if new_port:
                config['consolidator_config']['server']['port'] = int(new_port)
            
            new_tolerance = input(f"Nova tolerância em minutos (atual: {config['consolidator_config']['correlation']['tolerance_minutes']}): ")
            if new_tolerance:
                config['consolidator_config']['correlation']['tolerance_minutes'] = int(new_tolerance)
            
            new_refresh = input(f"Novo intervalo de refresh em segundos (atual: {config['consolidator_config']['interface']['auto_refresh_seconds']}): ")
            if new_refresh:
                config['consolidator_config']['interface']['auto_refresh_seconds'] = int(new_refresh)
            
            # Salva configuração
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print("✅ Configurações salvas!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar consolidador: {e}")
        return False

def start_consolidator():
    """Inicia o servidor consolidador"""
    print("\nIniciando servidor consolidador...")
    
    try:
        print("📡 Iniciando servidor POBChecker Consolidador...")
        print("   Dashboard: http://localhost:8000/dashboard")
        print("   API: http://localhost:8000/docs")
        print("\n⏹️  Pressione Ctrl+C para parar\n")
        
        # Executa o servidor
        subprocess.run([sys.executable, "run_server.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n⚠️ Servidor parado pelo usuário")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def check_consolidator_status():
    """Verifica status do consolidador"""
    print("\nVerificando status do consolidador...")
    
    try:
        # Verifica se os arquivos necessários existem
        files_to_check = [
            "consolidator_config.json",
            "pobchecker_server.py",
            "run_server.py",
            "models/consolidator_models.py"
        ]
        
        print("📋 Verificando arquivos:")
        for file in files_to_check:
            if os.path.exists(file):
                print(f"   ✅ {file}")
            else:
                print(f"   ❌ {file}")
        
        # Verifica dependências
        print("\n📦 Verificando dependências:")
        dependencies = ["fastapi", "uvicorn", "psycopg2", "zeroconf"]
        
        for dep in dependencies:
            try:
                __import__(dep)
                print(f"   ✅ {dep}")
            except ImportError:
                print(f"   ❌ {dep} (não instalado)")
        
        # Verifica configuração
        print("\n⚙️  Verificando configuração:")
        if os.path.exists("consolidator_config.json"):
            with open("consolidator_config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            print(f"   Tipo de banco: {config['consolidator_config']['database']['type']}")
            print(f"   Porta do servidor: {config['consolidator_config']['server']['port']}")
            print(f"   Auto-correlação: {config['consolidator_config']['correlation']['auto_correlate']}")
            print("   ✅ Configuração válida")
        else:
            print("   ❌ Arquivo de configuração não encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")
        return False

def clear_consolidator_data():
    """Limpa dados do consolidador"""
    print("\nLimpando dados do consolidador...")
    
    try:
        # Confirma a operação
        print("⚠️  Esta operação irá limpar todos os dados consolidados.")
        print("   • Eventos consolidados")
        print("   • Dados de correlação")
        print("   • Logs de sincronização")
        
        if input("\nDeseja continuar? (s/N): ").lower() != 's':
            print("Operação cancelada.")
            return False
        
        # Importa o servidor para acessar o banco
        from pobchecker_server import ConsolidatorServer
        
        server = ConsolidatorServer()
        
        # Limpa dados do banco do consolidador
        if hasattr(server.db, 'clear_all_data'):
            server.db.clear_all_data()
            print("✅ Dados do consolidador limpos!")
        else:
            print("❌ Método de limpeza não disponível no banco do consolidador")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao limpar dados: {e}")
        return False

def main():
    """Função principal"""
    print("POBCHECKER - SETUP DO CONSOLIDADOR")
    print("Sistema de Consolidação de Dados POB")
    
    while True:
        show_menu()
        
        try:
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "0":
                print("Voltando...")
                break
            elif choice == "1":
                configure_postgresql()
            elif choice == "2":
                test_database_connection()
            elif choice == "3":
                configure_consolidator()
            elif choice == "4":
                start_consolidator()
            elif choice == "5":
                check_consolidator_status()
            elif choice == "6":
                clear_consolidator_data()
            else:
                print("Opção inválida. Tente novamente.")
                
        except KeyboardInterrupt:
            print("\n\nSaindo...")
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()
