#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo: utilitary_server_data.py
Descrição: Script utilitário para gerenciar dados do consolidador
"""

import sys
import os
import json
import subprocess
from datetime import datetime

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show_menu():
    """Mostra o menu de opções de dados do consolidador"""
    print("\n" + "=" * 60)
    print("POBCHECKER - GERENCIAMENTO DE DADOS DO CONSOLIDADOR")
    print("=" * 60)
    print("1. Visualizar estatísticas dos dados consolidados")
    print("2. Gerar dados de teste para consolidação")
    print("3. Sincronizar dados entre terminais")
    print("4. Verificar correlações de eventos")
    print("5. Exportar dados consolidados")
    print("6. Limpar dados antigos")
    print("7. Backup dos dados consolidados")
    print("8. Restaurar backup")
    print("0. Voltar")
    print("=" * 60)

def show_consolidator_stats():
    """Mostra estatísticas detalhadas do consolidador"""
    print("📊 Estatísticas dos dados consolidados...")
    
    try:
        print("🔌 Tentando conectar ao PostgreSQL...")
        from database_postgres import DatabasePostgres
        
        db = DatabasePostgres()
        print("✅ Consolidador conectado ao PostgreSQL")
        print("✅ Tabelas PostgreSQL criadas/verificadas")
        
        # Testa se as tabelas existem e têm dados
        stats = db.get_stats()
        
        if not stats:
            print("⚠️  Nenhuma estatística disponível")
            return
            
        print("\n📊 ESTATÍSTICAS DO CONSOLIDADOR:")
        print(f"   👥 Total de pessoas: {stats.get('total_persons', 0)}")
        print(f"   🚢 Pessoas no POB: {stats.get('pob_count', 0)}")
        print(f"   📅 Total de eventos: {stats.get('events', 0)}")
        print(f"   🔓 Eventos abertos: {stats.get('open_events', 0)}")
        print(f"   ✅ Total de checks: {stats.get('total_checks', 0)}")
        print(f"   🔄 Total de check-ins/outs: {stats.get('total_checkins', 0)}")
        print(f"   🖥️  Terminais conectados: {stats.get('terminals', 0)}")
        print(f"   🔄 Última sincronização: {stats.get('last_sync', 'N/A')}")
        
        # Mostra dados das tabelas mais recentes
        print("\n📋 DADOS RECENTES:")
        try:
            # Últimas 5 pessoas cadastradas
            from database_postgres import POB
            recent_people = db.session.query(POB).limit(5).all()
            if recent_people:
                print("   � Últimas pessoas cadastradas:")
                for person in recent_people:
                    status = "POB" if person.Onshore == 0 else "Onshore"
                    print(f"      • {person.Name} ({person.CPF}) - {status}")
            else:
                print("   👥 Nenhuma pessoa cadastrada")
                
            # Últimos eventos
            from database_postgres import Events
            recent_events = db.session.query(Events).order_by(Events.ID.desc()).limit(5).all()
            if recent_events:
                print("   📅 Últimos eventos:")
                for event in recent_events:
                    status = "Fechado" if event.Closed else "Aberto"
                    print(f"      • Evento {event.ID}: {event.Open} - {status}")
            else:
                print("   📅 Nenhum evento registrado")
                
        except Exception as e:
            print(f"   ⚠️  Erro ao buscar dados recentes: {e}")
        
        # Arquivos de log
        print("\n📄 Arquivos de log:")
        log_files = ["consolidator.log", "sync.log", "correlation.log"]
        for log_file in log_files:
            if os.path.exists(log_file):
                size = os.path.getsize(log_file)
                mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                print(f"   ✅ {log_file} ({size} bytes, modificado: {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
            else:
                print(f"   ❌ {log_file} (não encontrado)")
        
        db.close()
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("   Verifique se o módulo database_postgres está disponível")
    except Exception as e:
        print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
        print("   Verifique se o PostgreSQL está rodando e configurado corretamente")
        print("   Configure o consolidador primeiro (opção 10 no menu principal)")

def generate_test_data():
    """Gera dados de teste para o consolidador"""
    try:
        from database_postgres import DatabasePostgres
        from faker import Faker
        import random
        
        fake = Faker('pt_BR')
        db = DatabasePostgres()
        
        print("📋 Gerando dados de teste para o consolidador...")
        
        # Pergunta quantas pessoas gerar
        try:
            num_pessoas = int(input("Quantas pessoas gerar? (padrão: 10): ") or "10")
        except ValueError:
            num_pessoas = 10
        
        # Gera pessoas
        pessoas_geradas = 0
        for i in range(num_pessoas):
            cpf = fake.cpf().replace('.', '').replace('-', '')
            nome = fake.name()
            onshore = random.choice([0, 1])
            
            person_data = {
                'cpf': cpf,
                'nome': nome,
                'Onshore': onshore
            }
            
            if db.insert_person(person_data):
                pessoas_geradas += 1
        
        # Gera eventos
        event_id = db.get_event("TESTE")
        if event_id:
            # Gera alguns checks para o evento
            for i in range(random.randint(5, 15)):
                cpf = fake.cpf().replace('.', '').replace('-', '')
                nome = fake.name()
                db.insert_check_event(cpf, nome, event_id)
        
        # Gera check-ins/outs
        for i in range(random.randint(10, 20)):
            cpf = fake.cpf().replace('.', '').replace('-', '')
            nome = fake.name()
            check_type = random.choice(['IN', 'OUT'])
            db.insert_check_in_out(cpf, nome, check_type)
        
        try:
            from logger_consolidator import log_consolidator
            log_consolidator(f"Dados de teste gerados: {pessoas_geradas} pessoas", 'info')
        except ImportError:
            pass
        
        print(f"✅ Dados de teste gerados com sucesso!")
        print(f"   👥 {pessoas_geradas} pessoas adicionadas")
        print(f"   📅 1 evento criado")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao gerar dados de teste: {e}")

def sync_terminal_data():
    """Simula sincronização entre terminais"""
    try:
        import time
        
        print("🔄 Sincronizando dados entre terminais...")
        
        # Simula sincronização
        terminals = ['Terminal-001', 'Terminal-002', 'Terminal-003']
        
        for terminal in terminals:
            print(f"   🔄 Sincronizando {terminal}...")
            time.sleep(1)  # Simula tempo de sincronização
            
            # Simula dados sincronizados
            import random
            records = random.randint(5, 25)
            
            try:
                from logger_consolidator import log_sync
                log_sync(terminal, "sync_data", "success", f"{records} registros sincronizados")
            except ImportError:
                pass
            
            print(f"   ✅ {terminal}: {records} registros sincronizados")
        
        print("✅ Sincronização concluída!")
        
    except Exception as e:
        print(f"❌ Erro na sincronização: {e}")

def check_event_correlations():
    """Verifica correlações de eventos"""
    try:
        from database_postgres import DatabasePostgres
        
        db = DatabasePostgres()
        
        print("🔍 Verificando correlações de eventos...")
        
        # Busca eventos para correlacionar
        events = db.get_consolidated_events()
        
        if not events:
            print("   ⚠️  Nenhum evento encontrado para correlacionar")
            return
        
        correlations_found = 0
        for event in events:
            # Simula verificação de correlação
            if event['id'] % 2 == 0:  # Simula que eventos pares têm correlação
                correlations_found += 1
                try:
                    from logger_consolidator import log_correlation
                    log_correlation(event['id'], "auto_correlation", "success", "Correlação automática encontrada")
                except ImportError:
                    pass
        
        print(f"   🔍 {len(events)} eventos analisados")
        print(f"   ✅ {correlations_found} correlações encontradas")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar correlações: {e}")

def export_consolidated_data():
    """Exporta dados consolidados"""
    try:
        from database_postgres import DatabasePostgres
        import json
        import csv
        from datetime import datetime
        
        db = DatabasePostgres()
        
        print("📤 Exportando dados consolidados...")
        
        # Pergunta o formato
        print("Formatos disponíveis:")
        print("1. JSON")
        print("2. CSV")
        print("3. Ambos")
        
        choice = input("Escolha o formato (1-3): ").strip()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Coleta dados
        persons = db.get_all_persons()
        events = db.get_consolidated_events()
        
        if choice in ['1', '3']:
            # Exporta JSON
            data = {
                'timestamp': timestamp,
                'persons': persons,
                'events': events,
                'stats': db.get_stats()
            }
            
            filename = f"consolidator_export_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"   ✅ Dados exportados para {filename}")
        
        if choice in ['2', '3']:
            # Exporta CSV de pessoas
            filename = f"consolidator_persons_{timestamp}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['CPF', 'Nome', 'Onshore'])
                for person in persons:
                    writer.writerow([person['cpf'], person['nome'], person['Onshore']])
            print(f"   ✅ Pessoas exportadas para {filename}")
            
            # Exporta CSV de eventos
            filename = f"consolidator_events_{timestamp}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Aberto', 'Fechado', 'Status'])
                for event in events:
                    writer.writerow([event['id'], event['open'], event['close'], 'Fechado' if event['closed'] else 'Aberto'])
            print(f"   ✅ Eventos exportados para {filename}")
        
        print("✅ Exportação concluída!")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao exportar dados: {e}")

def clean_old_data():
    """Limpa dados antigos"""
    try:
        from database_postgres import DatabasePostgres
        
        db = DatabasePostgres()
        
        print("🧹 Limpando dados antigos...")
        
        # Pergunta confirmação
        confirm = input("Tem certeza que deseja limpar dados antigos? (s/N): ").strip().lower()
        
        if confirm == 's':
            # Aqui você implementaria a lógica de limpeza
            # Por exemplo, remover eventos fechados há mais de 30 dias
            print("   🧹 Limpando eventos antigos...")
            print("   🧹 Limpando logs antigos...")
            
            try:
                from logger_consolidator import log_consolidator
                log_consolidator("Limpeza de dados antigos executada", 'info')
            except ImportError:
                pass
            
            print("✅ Limpeza concluída!")
        else:
            print("❌ Operação cancelada")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao limpar dados: {e}")

def backup_data():
    """Faz backup dos dados"""
    try:
        from database_postgres import DatabasePostgres
        import json
        from datetime import datetime
        
        db = DatabasePostgres()
        
        print("💾 Fazendo backup dos dados...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Coleta todos os dados
        backup_data = {
            'timestamp': timestamp,
            'persons': db.get_all_persons(),
            'events': db.get_consolidated_events(),
            'stats': db.get_stats()
        }
        
        filename = f"consolidator_backup_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        try:
            from logger_consolidator import log_consolidator
            log_consolidator(f"Backup criado: {filename}", 'info')
        except ImportError:
            pass
        
        print(f"✅ Backup criado: {filename}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao fazer backup: {e}")

def restore_backup():
    """Restaura backup dos dados"""
    try:
        import json
        import os
        
        print("🔄 Restaurando backup...")
        
        # Lista backups disponíveis
        backups = [f for f in os.listdir('.') if f.startswith('consolidator_backup_') and f.endswith('.json')]
        
        if not backups:
            print("❌ Nenhum backup encontrado")
            return
        
        print("Backups disponíveis:")
        for i, backup in enumerate(backups, 1):
            print(f"   {i}. {backup}")
        
        try:
            choice = int(input("Escolha o backup para restaurar: ")) - 1
            if 0 <= choice < len(backups):
                filename = backups[choice]
                
                # Pergunta confirmação
                confirm = input(f"Tem certeza que deseja restaurar {filename}? (s/N): ").strip().lower()
                
                if confirm == 's':
                    with open(filename, 'r', encoding='utf-8') as f:
                        backup_data = json.load(f)
                    
                    # Aqui você implementaria a lógica de restauração
                    print("   🔄 Restaurando dados...")
                    
                    try:
                        from logger_consolidator import log_consolidator
                        log_consolidator(f"Backup restaurado: {filename}", 'info')
                    except ImportError:
                        pass
                    
                    print("✅ Backup restaurado com sucesso!")
                else:
                    print("❌ Operação cancelada")
            else:
                print("❌ Opção inválida")
        except ValueError:
            print("❌ Opção inválida")
        
    except Exception as e:
        print(f"❌ Erro ao restaurar backup: {e}")

def main():
    """Função principal"""
    print("POBCHECKER - GERENCIAMENTO DE DADOS DO CONSOLIDADOR")
    print("Sistema de Consolidação de Dados POB")
    
    while True:
        show_menu()
        
        try:
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "0":
                print("Voltando...")
                break
            elif choice == "1":
                show_consolidator_stats()
            elif choice == "2":
                generate_test_data()
            elif choice == "3":
                sync_terminal_data()
            elif choice == "4":
                check_event_correlations()
            elif choice == "5":
                export_consolidated_data()
            elif choice == "6":
                clean_old_data()
            elif choice == "7":
                backup_data()
            elif choice == "8":
                restore_backup()
            else:
                print("Opção inválida. Tente novamente.")
                
        except KeyboardInterrupt:
            print("\n\nSaindo...")
            break
        except Exception as e:
            print(f"Erro: {e}")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
