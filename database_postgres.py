# Arquivo: database_postgres.py

import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

# Carrega as variáveis de ambiente
load_dotenv()

Base = declarative_base()

# Definição das tabelas usando SQLAlchemy ORM
class POB(Base):
    __tablename__ = 'pob'
    
    CPF = Column('cpf', String(11), primary_key=True)
    Name = Column('name', String(255), nullable=False)
    Onshore = Column('onshore', Integer, default=1)
    Synced = Column('synced', Integer, default=0)
    
    # Relacionamentos
    check_events = relationship("CheckEvent", back_populates="person")
    check_in_outs = relationship("CheckInOut", back_populates="person")

class Events(Base):
    __tablename__ = 'events'
    
    ID = Column('id', Integer, primary_key=True, autoincrement=True)
    Open = Column('open', String(255), nullable=False)
    Close = Column('close', String(255), nullable=True)
    Closed = Column('closed', Integer, default=0)
    Synced = Column('synced', Integer, default=0)
    
    # Relacionamentos
    check_events = relationship("CheckEvent", back_populates="event")

class CheckEvent(Base):
    __tablename__ = 'check_event'
    
    ID = Column('id', Integer, primary_key=True, autoincrement=True)
    CPF = Column('cpf', String(11), ForeignKey('pob.cpf'))
    Name = Column('name', String(255))
    Timestamp = Column('timestamp', String(255), nullable=False)
    Event = Column('event', Integer, ForeignKey('events.id'))
    Synced = Column('synced', Integer, default=0)
    
    # Relacionamentos
    person = relationship("POB", back_populates="check_events")
    event = relationship("Events", back_populates="check_events")

class CheckInOut(Base):
    __tablename__ = 'check_in_out'
    
    ID = Column('id', Integer, primary_key=True, autoincrement=True)
    CPF = Column('cpf', String(11), ForeignKey('pob.cpf'))
    Name = Column('name', String(255))
    Type = Column('type', String(50), nullable=False)
    Timestamp = Column('timestamp', String(255), nullable=False)
    Synced = Column('synced', Integer, default=0)
    
    # Relacionamentos
    person = relationship("POB", back_populates="check_in_outs")

class DatabasePostgres:
    """
    Classe para gerenciar operações do banco de dados PostgreSQL usando SQLAlchemy.
    """
    def __init__(self, database_url=None):
        """
        Inicializa a conexão com PostgreSQL e cria as tabelas se necessário.
        """
        if database_url is None:
            try:
                # Tenta carregar da configuração
                with open('consolidator_config.json', 'r') as f:
                    config = json.load(f)
                db_config = config['consolidator_config']['database']['postgresql']
                database_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['name']}"
            except:
                # Fallback para configuração padrão
                database_url = os.getenv('DATABASE_URL', 'postgresql://pobchecker:pobchecker@localhost:5432/pobchecker_db')
        
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def insert_person(self, person_data):
        """
        Insere uma nova pessoa na tabela POB.
        """
        try:
            person = POB(
                CPF=person_data['cpf'],
                Name=person_data['nome'],
                Onshore=person_data['Onshore']
            )
            self.session.add(person)
            self.session.commit()
            return True
        except Exception as e:
            print(f"Erro ao inserir pessoa: {e}")
            self.session.rollback()
            return False

    def get_event(self, event_type="DEFAULT"):
        """
        Retorna o evento aberto mais recente ou cria um novo se não existir.
        """
        try:
            # Procura por evento aberto
            event = self.session.query(Events).filter_by(Closed=0).order_by(Events.ID.desc()).first()
            
            if event:
                return event.ID
            else:
                # Cria novo evento
                new_event = Events(
                    Open=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    Close=None,
                    Closed=0
                )
                self.session.add(new_event)
                self.session.commit()
                return new_event.ID
                
        except Exception as e:
            print(f"Erro ao obter evento: {e}")
            return None

    def close_event(self, event_id):
        """
        Fecha um evento específico.
        """
        try:
            event = self.session.query(Events).filter_by(ID=event_id).first()
            if event:
                event.Close = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                event.Closed = 1
                self.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Erro ao fechar evento: {e}")
            return False

    def insert_check_event(self, cpf, name, event_id):
        """
        Insere um registro de checagem no evento.
        """
        try:
            check = CheckEvent(
                CPF=cpf,
                Name=name,
                Timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                Event=event_id
            )
            self.session.add(check)
            self.session.commit()
            return True
        except Exception as e:
            print(f"Erro ao inserir check event: {e}")
            self.session.rollback()
            return False

    def insert_check_in_out(self, cpf, name, check_type):
        """
        Insere um registro de check in/out.
        """
        try:
            check = CheckInOut(
                CPF=cpf,
                Name=name,
                Type=check_type,
                Timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            self.session.add(check)
            self.session.commit()
            return True
        except Exception as e:
            print(f"Erro ao inserir check in/out: {e}")
            self.session.rollback()
            return False

    def get_all_persons(self):
        """
        Retorna todas as pessoas cadastradas.
        """
        try:
            persons = self.session.query(POB).all()
            return [{'cpf': p.CPF, 'nome': p.Name, 'Onshore': p.Onshore} for p in persons]
        except Exception as e:
            print(f"Erro ao obter pessoas: {e}")
            return []

    def get_person_by_cpf(self, cpf):
        """
        Busca uma pessoa pelo CPF.
        """
        try:
            person = self.session.query(POB).filter_by(CPF=cpf).first()
            if person:
                return {'cpf': person.CPF, 'nome': person.Name, 'Onshore': person.Onshore}
            return None
        except Exception as e:
            print(f"Erro ao buscar pessoa: {e}")
            return None

    def delete_person(self, cpf):
        """
        Remove uma pessoa do banco de dados.
        """
        try:
            person = self.session.query(POB).filter_by(CPF=cpf).first()
            if person:
                self.session.delete(person)
                self.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Erro ao deletar pessoa: {e}")
            self.session.rollback()
            return False

    def update_person(self, cpf, new_data):
        """
        Atualiza os dados de uma pessoa.
        """
        try:
            person = self.session.query(POB).filter_by(CPF=cpf).first()
            if person:
                person.Name = new_data.get('nome', person.Name)
                person.Onshore = new_data.get('Onshore', person.Onshore)
                self.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Erro ao atualizar pessoa: {e}")
            self.session.rollback()
            return False

    def get_unsynced_records(self, table_name):
        """
        Retorna registros não sincronizados de uma tabela específica.
        """
        try:
            if table_name == 'pob':
                records = self.session.query(POB).filter_by(Synced=0).all()
                return [{'cpf': r.CPF, 'nome': r.Name, 'Onshore': r.Onshore} for r in records]
            elif table_name == 'check_event':
                records = self.session.query(CheckEvent).filter_by(Synced=0).all()
                return [{'id': r.ID, 'cpf': r.CPF, 'nome': r.Name, 'timestamp': r.Timestamp, 'event': r.Event} for r in records]
            elif table_name == 'check_in_out':
                records = self.session.query(CheckInOut).filter_by(Synced=0).all()
                return [{'id': r.ID, 'cpf': r.CPF, 'nome': r.Name, 'type': r.Type, 'timestamp': r.Timestamp} for r in records]
            return []
        except Exception as e:
            print(f"Erro ao obter registros não sincronizados: {e}")
            return []

    def mark_as_synced(self, table_name, record_id):
        """
        Marca um registro como sincronizado.
        """
        try:
            if table_name == 'pob':
                record = self.session.query(POB).filter_by(CPF=record_id).first()
            elif table_name == 'check_event':
                record = self.session.query(CheckEvent).filter_by(ID=record_id).first()
            elif table_name == 'check_in_out':
                record = self.session.query(CheckInOut).filter_by(ID=record_id).first()
            else:
                return False
            
            if record:
                record.Synced = 1
                self.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Erro ao marcar como sincronizado: {e}")
            self.session.rollback()
            return False

    def get_event_summary(self, event_id):
        """
        Retorna um resumo do evento com todas as checagens.
        """
        try:
            event = self.session.query(Events).filter_by(ID=event_id).first()
            if not event:
                return None
            
            checks = self.session.query(CheckEvent).filter_by(Event=event_id).all()
            
            return {
                'event_id': event.ID,
                'open': event.Open,
                'close': event.Close,
                'closed': event.Closed,
                'total_checks': len(checks),
                'checks': [{'cpf': c.CPF, 'nome': c.Name, 'timestamp': c.Timestamp} for c in checks]
            }
        except Exception as e:
            print(f"Erro ao obter resumo do evento: {e}")
            return None

    def get_person_status(self, cpf):
        """
        Retorna o status atual de uma pessoa (IN/OUT).
        """
        try:
            # Busca o último check-in/out da pessoa
            last_check = self.session.query(CheckInOut).filter_by(CPF=cpf).order_by(CheckInOut.ID.desc()).first()
            
            if last_check:
                return last_check.Type
            else:
                # Se não tem check-in/out, verifica se está na tabela POB
                person = self.session.query(POB).filter_by(CPF=cpf).first()
                if person:
                    return "IN" if person.Onshore == 1 else "OUT"
                return "UNKNOWN"
        except Exception as e:
            print(f"Erro ao obter status da pessoa: {e}")
            return "UNKNOWN"

    def get_stats(self):
        """
        Retorna estatísticas do consolidador.
        """
        try:
            # Conta registros
            total_persons = self.session.query(POB).count()
            total_events = self.session.query(Events).count()
            total_checks = self.session.query(CheckEvent).count()
            total_checkins = self.session.query(CheckInOut).count()
            
            # Eventos abertos
            open_events = self.session.query(Events).filter_by(Closed=0).count()
            
            # Pessoas no POB (Onshore = 0)
            pob_count = self.session.query(POB).filter_by(Onshore=0).count()
            
            # Última sincronização (simula por enquanto)
            last_sync = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            return {
                'terminals': 1,  # Por enquanto simula 1 terminal
                'events': total_events,
                'last_sync': last_sync,
                'total_persons': total_persons,
                'total_checks': total_checks,
                'total_checkins': total_checkins,
                'open_events': open_events,
                'pob_count': pob_count
            }
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {}

    def get_consolidated_events(self):
        """
        Retorna eventos consolidados.
        """
        try:
            events = self.session.query(Events).all()
            return [{'id': e.ID, 'open': e.Open, 'close': e.Close, 'closed': e.Closed} for e in events]
        except Exception as e:
            print(f"Erro ao obter eventos consolidados: {e}")
            return []

    def get_terminal_status(self):
        """
        Retorna status dos terminais.
        """
        try:
            # Por enquanto simula um terminal
            return [{'id': 1, 'name': 'Terminal-001', 'status': 'online', 'last_sync': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]
        except Exception as e:
            print(f"Erro ao obter status dos terminais: {e}")
            return []

    def get_sync_logs(self):
        """
        Retorna logs de sincronização.
        """
        try:
            # Por enquanto simula logs
            return [{'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'action': 'sync', 'status': 'success'}]
        except Exception as e:
            print(f"Erro ao obter logs de sincronização: {e}")
            return []

    def close(self):
        """
        Fecha a conexão com o banco de dados.
        """
        self.session.close()

# Função para migração do SQLite para PostgreSQL
def migrate_from_sqlite(sqlite_file="pobchecker.sqlite3"):
    """
    Migra dados do SQLite para PostgreSQL.
    """
    try:
        import sqlite3
        
        # Conecta ao SQLite
        sqlite_conn = sqlite3.connect(sqlite_file)
        sqlite_cursor = sqlite_conn.cursor()
        
        # Conecta ao PostgreSQL
        pg_db = DatabasePostgres()
        
        print("Iniciando migração do SQLite para PostgreSQL...")
        
        # Migra POB
        sqlite_cursor.execute("SELECT CPF, Name, Onshore FROM POB")
        pob_data = sqlite_cursor.fetchall()
        
        for row in pob_data:
            person_data = {
                'cpf': row[0],
                'nome': row[1],
                'Onshore': row[2]
            }
            pg_db.insert_person(person_data)
        
        print(f"Migrados {len(pob_data)} registros da tabela POB")
        
        # Migra Events
        sqlite_cursor.execute("SELECT ID, Open, Close, Closed FROM EVENTS")
        events_data = sqlite_cursor.fetchall()
        
        for row in events_data:
            event = Events(
                ID=row[0],
                Open=row[1],
                Close=row[2],
                Closed=row[3]
            )
            pg_db.session.add(event)
        
        pg_db.session.commit()
        print(f"Migrados {len(events_data)} registros da tabela EVENTS")
        
        # Migra CHECK_EVENT
        sqlite_cursor.execute("SELECT ID, CPF, Name, Timestamp, Event FROM CHECK_EVENT")
        check_events_data = sqlite_cursor.fetchall()
        
        for row in check_events_data:
            check = CheckEvent(
                ID=row[0],
                CPF=row[1],
                Name=row[2],
                Timestamp=row[3],
                Event=row[4]
            )
            pg_db.session.add(check)
        
        pg_db.session.commit()
        print(f"Migrados {len(check_events_data)} registros da tabela CHECK_EVENT")
        
        # Migra CHECK_IN_OUT
        sqlite_cursor.execute("SELECT ID, CPF, Name, Type, Timestamp FROM CHECK_IN_OUT")
        check_io_data = sqlite_cursor.fetchall()
        
        for row in check_io_data:
            check = CheckInOut(
                ID=row[0],
                CPF=row[1],
                Name=row[2],
                Type=row[3],
                Timestamp=row[4]
            )
            pg_db.session.add(check)
        
        pg_db.session.commit()
        print(f"Migrados {len(check_io_data)} registros da tabela CHECK_IN_OUT")
        
        sqlite_conn.close()
        pg_db.close()
        
        print("Migração concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro durante a migração: {e}")
        return False

if __name__ == "__main__":
    # Teste da conexão PostgreSQL
    try:
        db = DatabasePostgres()
        print("Conexão com PostgreSQL estabelecida com sucesso!")
        
        # Teste básico
        test_person = {
            'cpf': '12345678901',
            'nome': 'Teste PostgreSQL',
            'Onshore': 1
        }
        
        if db.insert_person(test_person):
            print("Teste de inserção bem-sucedido!")
            
            # Busca a pessoa inserida
            person = db.get_person_by_cpf('12345678901')
            if person:
                print(f"Pessoa encontrada: {person}")
                
                # Remove a pessoa de teste
                if db.delete_person('12345678901'):
                    print("Pessoa de teste removida com sucesso!")
        
        db.close()
        
    except Exception as e:
        print(f"Erro ao testar PostgreSQL: {e}")
        print("Verifique se o PostgreSQL está rodando no WSL e se as credenciais estão corretas.")
