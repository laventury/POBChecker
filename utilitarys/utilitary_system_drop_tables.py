#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo: utilitary_system_drop_tables.py
Descrição: Script utilitário para apagar a estrutura das tabelas dos bancos de dados
"""

import sys
import os
import sqlite3
import json

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show_menu():
    """Mostra o menu de opções"""
    print("\n" + "=" * 60)
    print("POBCHECKER - APAGAR ESTRUTURA DAS TABELAS")
    print("=" * 60)
    print("1. Apagar estrutura do banco de dados do TERMINAL (SQLite)")
    print("2. Apagar estrutura do banco de dados do CONSOLIDADOR (PostgreSQL)")
    print("3. Apagar estrutura de AMBOS os bancos de dados")
    print("4. Verificar estrutura dos bancos")
    print("0. Voltar")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Esta operação apagará TODAS as tabelas e estruturas!")
    print("⚠️  Todos os dados serão perdidos permanentemente!")

def check_database_structures():
    """Verifica e mostra a estrutura atual dos bancos de dados"""
    print("\n🔍 Verificando estrutura dos bancos de dados...")
    
    # Verifica SQLite (Terminal)
    print("\n📱 BANCO DE DADOS DO TERMINAL (SQLite):")
    sqlite_file = "pobchecker.sqlite3"
    
    if os.path.exists(sqlite_file):
        try:
            conn = sqlite3.connect(sqlite_file)
            cursor = conn.cursor()
            
            # Lista todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if tables:
                print(f"   ✅ Arquivo encontrado: {sqlite_file}")
                print(f"   📋 Tabelas encontradas ({len(tables)}):")
                for table in tables:
                    table_name = table[0]
                    try:
                        # Conta registros em cada tabela
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        print(f"      • {table_name}: {count} registros")
                    except Exception as e:
                        print(f"      • {table_name}: erro ao contar - {e}")
            else:
                print(f"   ✅ Arquivo encontrado: {sqlite_file}")
                print("   ⚠️  Nenhuma tabela encontrada no banco SQLite")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Erro ao acessar SQLite: {e}")
    else:
        print(f"   ❌ Arquivo SQLite não encontrado: {sqlite_file}")
        print("   💡 O banco será criado automaticamente quando o sistema for usado")
    
    # Verifica PostgreSQL (Consolidador) - conexão direta sem create_all
    print("\n🌐 BANCO DE DADOS DO CONSOLIDADOR (PostgreSQL):")
    try:
        from sqlalchemy import create_engine, text
        
        # Conecta diretamente sem usar DatabasePostgres
        try:
            with open('consolidator_config.json', 'r') as f:
                config = json.load(f)
            db_config = config['consolidator_config']['database']['postgresql']
            database_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['name']}"
        except Exception as config_error:
            print(f"   ⚠️  Erro ao carregar configuração: {config_error}")
            print("   💡 Usando configuração padrão...")
            database_url = os.getenv('DATABASE_URL', 'postgresql://pobchecker:pobchecker@localhost:5432/pobchecker_db')
        
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Lista todas as tabelas do schema público
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """))
            
            tables = result.fetchall()
            
            if tables:
                print("   ✅ Conexão PostgreSQL estabelecida")
                print(f"   📋 Tabelas encontradas ({len(tables)}):")
                
                for table in tables:
                    table_name = table[0]
                    try:
                        # Conta registros em cada tabela
                        count_result = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                        count = count_result.fetchone()[0]
                        print(f"      • {table_name}: {count} registros")
                    except Exception as e:
                        print(f"      • {table_name}: erro ao contar - {e}")
            else:
                print("   ✅ Conexão PostgreSQL estabelecida")
                print("   ⚠️  Nenhuma tabela encontrada no PostgreSQL")
                print("   💡 As tabelas serão criadas automaticamente quando necessário")
        
    except ImportError:
        print("   ❌ Módulo SQLAlchemy não disponível")
        print("   💡 Instale com: pip install sqlalchemy psycopg2")
    except Exception as e:
        print(f"   ❌ Erro ao acessar PostgreSQL: {e}")
        print("   💡 Verifique se o PostgreSQL está rodando e as credenciais estão corretas")

def drop_sqlite_tables():
    """Apaga todas as tabelas do banco SQLite (Terminal)"""
    print("\n🗑️  Apagando estrutura do banco de dados do TERMINAL...")
    
    sqlite_file = "pobchecker.sqlite3"
    
    if not os.path.exists(sqlite_file):
        print(f"   ❌ Arquivo SQLite não encontrado: {sqlite_file}")
        return False
    
    try:
        print("   📱 Conectando ao SQLite...")
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        
        # Lista todas as tabelas antes de apagar
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("   ⚠️  Nenhuma tabela encontrada para apagar")
            conn.close()
            return True
        
        print(f"   📋 Tabelas a serem apagadas: {[t[0] for t in tables]}")
        
        # Confirma a operação
        confirm = input("   ⚠️  Confirma a exclusão de TODAS as tabelas do Terminal? (digite 'CONFIRMAR'): ")
        
        if confirm != "CONFIRMAR":
            print("   ❌ Operação cancelada pelo usuário")
            conn.close()
            return False
        
        # Desabilita foreign keys para evitar problemas de dependência
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # Apaga cada tabela
        for table in tables:
            table_name = table[0]
            print(f"   🗑️  Apagando tabela: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        
        # Reabilita foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        conn.commit()
        conn.close()
        
        print("   ✅ Estrutura do banco SQLite apagada com sucesso!")
        print("   📝 O arquivo do banco foi mantido, mas sem tabelas")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao apagar estrutura SQLite: {e}")
        return False

def drop_postgresql_tables():
    """Apaga todas as tabelas do banco PostgreSQL (Consolidador)"""
    print("\n🗑️  Apagando estrutura do banco de dados do CONSOLIDADOR...")
    
    try:
        print("   🌐 Conectando ao PostgreSQL...")
        from sqlalchemy import create_engine, text
        
        # Conecta diretamente sem usar DatabasePostgres para evitar create_all()
        try:
            with open('consolidator_config.json', 'r') as f:
                config = json.load(f)
            db_config = config['consolidator_config']['database']['postgresql']
            database_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['name']}"
        except:
            database_url = os.getenv('DATABASE_URL', 'postgresql://pobchecker:pobchecker@localhost:5432/pobchecker_db')
        
        engine = create_engine(database_url)
        
        with engine.begin() as connection:
            # Lista todas as tabelas do schema público
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """))
            
            tables = result.fetchall()
            
            if not tables:
                print("   ⚠️  Nenhuma tabela encontrada para apagar")
                return True
            
            table_names = [t[0] for t in tables]
            print(f"   📋 Tabelas a serem apagadas: {table_names}")
            
            # Confirma a operação
            confirm = input("   ⚠️  Confirma a exclusão de TODAS as tabelas do Consolidador? (digite 'CONFIRMAR'): ")
            
            if confirm != "CONFIRMAR":
                print("   ❌ Operação cancelada pelo usuário")
                return False
            
            # Primeiro, remove todas as foreign key constraints para evitar problemas de dependência
            print("   🔧 Removendo constraints de foreign key...")
            try:
                # Desabilita todas as constraints temporariamente
                connection.execute(text("SET session_replication_role = replica;"))
            except Exception as e:
                print(f"   ⚠️  Aviso: Não foi possível desabilitar constraints: {e}")
            
            # Apaga cada tabela com CASCADE para forçar a remoção
            for table_name in table_names:
                try:
                    print(f"   🗑️  Apagando tabela: {table_name}")
                    connection.execute(text(f"DROP TABLE IF EXISTS \"{table_name}\" CASCADE;"))
                except Exception as e:
                    print(f"   ⚠️  Erro ao apagar tabela {table_name}: {e}")
            
            # Reabilita as constraints
            try:
                connection.execute(text("SET session_replication_role = DEFAULT;"))
            except Exception as e:
                print(f"   ⚠️  Aviso: Não foi possível reabilitar constraints: {e}")
            
            # Verifica se as tabelas foram realmente apagadas (com nova conexão)
            with engine.connect() as check_conn:
                result_check = check_conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name;
                """))
                
                remaining_tables = result_check.fetchall()
                
                if remaining_tables:
                    print(f"   ⚠️  Algumas tabelas ainda existem: {[t[0] for t in remaining_tables]}")
                    print("   🔄 Tentando remoção forçada...")
                    
                    # Tenta remover as tabelas restantes uma por uma
                    with engine.begin() as force_conn:
                        for table in remaining_tables:
                            table_name = table[0]
                            try:
                                print(f"   🗑️  Remoção forçada: {table_name}")
                                force_conn.execute(text(f"DROP TABLE \"{table_name}\" CASCADE;"))
                            except Exception as e:
                                print(f"   ❌ Falha na remoção forçada de {table_name}: {e}")
                    
                    # Verifica novamente
                    with engine.connect() as final_conn:
                        final_check = final_conn.execute(text("""
                            SELECT table_name 
                            FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_type = 'BASE TABLE'
                            ORDER BY table_name;
                        """))
                        
                        final_tables = final_check.fetchall()
                        
                        if final_tables:
                            print(f"   ❌ Tabelas que não puderam ser removidas: {[t[0] for t in final_tables]}")
                            return False
            
            print("   ✅ Estrutura do banco PostgreSQL apagada com sucesso!")
            return True
        
    except ImportError:
        print("   ❌ Módulo PostgreSQL não disponível")
        return False
    except Exception as e:
        print(f"   ❌ Erro ao apagar estrutura PostgreSQL: {e}")
        return False

def drop_all_tables():
    """Apaga a estrutura de ambos os bancos de dados"""
    print("\n🗑️  Apagando estrutura de AMBOS os bancos de dados...")
    
    # Confirma a operação para ambos
    print("   ⚠️  Esta operação apagará TODAS as tabelas de:")
    print("      • Banco do Terminal (SQLite)")
    print("      • Banco do Consolidador (PostgreSQL)")
    
    confirm = input("   ⚠️  Confirma a exclusão COMPLETA? (digite 'CONFIRMAR TUDO'): ")
    
    if confirm != "CONFIRMAR TUDO":
        print("   ❌ Operação cancelada pelo usuário")
        return False
    
    # Apaga SQLite
    print("\n📱 Processando banco do Terminal...")
    sqlite_success = True
    try:
        sqlite_file = "pobchecker.sqlite3"
        if os.path.exists(sqlite_file):
            conn = sqlite3.connect(sqlite_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if tables:
                cursor.execute("PRAGMA foreign_keys = OFF;")
                for table in tables:
                    table_name = table[0]
                    print(f"   🗑️  SQLite - Apagando: {table_name}")
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                cursor.execute("PRAGMA foreign_keys = ON;")
                
                conn.commit()
            conn.close()
            print("   ✅ SQLite - Estrutura apagada")
        else:
            print("   ⚠️  SQLite - Arquivo não encontrado")
    except Exception as e:
        print(f"   ❌ SQLite - Erro: {e}")
        sqlite_success = False
    
    # Apaga PostgreSQL
    print("\n🌐 Processando banco do Consolidador...")
    postgresql_success = True
    try:
        from sqlalchemy import create_engine, text
        
        # Conecta diretamente sem usar DatabasePostgres para evitar create_all()
        try:
            with open('consolidator_config.json', 'r') as f:
                config = json.load(f)
            db_config = config['consolidator_config']['database']['postgresql']
            database_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['name']}"
        except:
            database_url = os.getenv('DATABASE_URL', 'postgresql://pobchecker:pobchecker@localhost:5432/pobchecker_db')
        
        engine = create_engine(database_url)
        
        with engine.begin() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """))
            
            tables = result.fetchall()
            
            if tables:
                table_names = [t[0] for t in tables]
                
                # Desabilita constraints temporariamente
                try:
                    connection.execute(text("SET session_replication_role = replica;"))
                except Exception as e:
                    print(f"   ⚠️  PostgreSQL - Aviso constraints: {e}")
                
                for table_name in table_names:
                    try:
                        print(f"   🗑️  PostgreSQL - Apagando: {table_name}")
                        connection.execute(text(f"DROP TABLE IF EXISTS \"{table_name}\" CASCADE;"))
                    except Exception as e:
                        print(f"   ⚠️  PostgreSQL - Erro ao apagar {table_name}: {e}")
                
                # Reabilita constraints
                try:
                    connection.execute(text("SET session_replication_role = DEFAULT;"))
                except Exception as e:
                    print(f"   ⚠️  PostgreSQL - Aviso reabilitar constraints: {e}")
                
                print("   ✅ PostgreSQL - Estrutura apagada")
            else:
                print("   ⚠️  PostgreSQL - Nenhuma tabela encontrada")
        
    except ImportError:
        print("   ⚠️  PostgreSQL - Módulo não disponível")
        postgresql_success = False
    except Exception as e:
        print(f"   ❌ PostgreSQL - Erro: {e}")
        postgresql_success = False
    
    # Resultado final
    print(f"\n📊 RESULTADO DA OPERAÇÃO:")
    print(f"   📱 Terminal (SQLite): {'✅ Sucesso' if sqlite_success else '❌ Falhou'}")
    print(f"   🌐 Consolidador (PostgreSQL): {'✅ Sucesso' if postgresql_success else '❌ Falhou'}")
    
    if sqlite_success and postgresql_success:
        print("\n✅ Estrutura de ambos os bancos apagada com sucesso!")
        print("💡 Para recriar as tabelas, execute qualquer operação que acesse o banco")
        return True
    else:
        print("\n⚠️  Operação concluída com alguns erros")
        return False

def main():
    """Função principal"""
    print("POBCHECKER - UTILITÁRIO PARA APAGAR ESTRUTURA DAS TABELAS")
    print("Sistema para remoção completa da estrutura dos bancos de dados")
    
    while True:
        show_menu()
        
        try:
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "0":
                print("👋 Voltando ao menu principal...")
                break
            elif choice == "1":
                drop_sqlite_tables()
            elif choice == "2":
                drop_postgresql_tables()
            elif choice == "3":
                drop_all_tables()
            elif choice == "4":
                check_database_structures()
            else:
                print("❌ Opção inválida. Tente novamente.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Operação interrompida pelo usuário...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        # Pausa para o usuário ler as mensagens
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
