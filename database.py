# Arquivo: database.py

import sqlite3
from datetime import datetime, timedelta


class Database:
    """
    Classe para gerenciar todas as operações do banco de dados SQLite.
    Isso centraliza a lógica do banco de dados em um único lugar.
    """
    def __init__(self, db_file="pobchecker.sqlite3"):
        """
        Inicializa a conexão com o banco de dados e cria as tabelas se não existirem.
        """
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """
        Cria as tabelas 'POB','EVENTS','CHECK_EVENT','CHECK_IN_OUT' se elas ainda não existirem no banco.
        """
        # Tabela de Pessoas a Bordo (POB)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS POB (
                CPF TEXT PRIMARY KEY,
                Name TEXT NOT NULL,
                GroupNumber INTEGER NOT NULL,
                Onshore INTEGER DEFAULT 1
            )
        ''')
        
        # Migra a coluna Group para GroupNumber se necessário
        self._migrate_group_column()

        # Tabela de registro de eventos (sem campo nome, com Open e Close)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS EVENTS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Open TEXT NOT NULL,
                Close TEXT NULL,
                Closed INTEGER DEFAULT 0   
            )
        ''')

        # Tabela de registro de checagem de pessoas nos eventos (CEV mode)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS CHECK_EVENT (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                CPF TEXT,
                Name TEXT,
                Timestamp TEXT NOT NULL,
                Event INTEGER,
                FOREIGN KEY (CPF) REFERENCES POB (CPF),
                FOREIGN KEY (Event) REFERENCES EVENTS (ID)       
            )
        ''')

        # Tabela de registro de check in/out (CIO mode)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS CHECK_IN_OUT (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                CPF TEXT,
                Name TEXT,
                Type TEXT NOT NULL,
                Timestamp TEXT NOT NULL,
                FOREIGN KEY (CPF) REFERENCES POB (CPF)     
            )
        ''')
        
        self.conn.commit()

    def insert_person(self, person_data):
        """
        Insere uma nova pessoa na tabela POB.
        """
        try:
            self.cursor.execute('''
                INSERT INTO POB (CPF, Name, GroupNumber, Onshore)
                VALUES (?, ?, ?, ?)
            ''', (
                person_data['cpf'],
                person_data['nome'],
                person_data['grupo'],
                person_data['Onshore']
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao inserir pessoa: {e}")
            return False

    def get_event(self, event_type="DEFAULT"):
        """
        Método mantido para compatibilidade - agora sempre retorna o evento ativo atual.
        """
        return self.get_active_event()

    def person_check(self, cpf, nome, event):
        """
        Método mantido para compatibilidade - redireciona para record_check_event.
        """
        if event:
            return self.record_check_event(cpf, nome, event)
        return False
            

    def get_people_by_group(self, group_number):
        """
        Retorna uma lista de todas as pessoas de um determinado grupo.
        """
        self.cursor.execute("SELECT CPF, Name, GroupNumber FROM POB WHERE GroupNumber = ? ORDER BY Name", (group_number,))
        return self.cursor.fetchall()

    def clean_cpf(self, cpf):
        """Remove qualquer formatação do CPF e retorna apenas os números."""
        return cpf.replace(".", "").replace("-", "").replace(" ", "").strip()

    def validate_cpf(self, cpf):
        """Valida se o CPF está no formato correto (apenas números e com 11 dígitos)."""
        cpf_clean = self.clean_cpf(cpf)
        return cpf_clean.isdigit() and len(cpf_clean) == 11

    def find_person_by_cpf(self, cpf):
        """
        Busca e retorna os dados de uma pessoa pelo CPF.
        """
        # Limpa e valida o CPF
        cpf_clean = self.clean_cpf(cpf)
        if not self.validate_cpf(cpf_clean):
            return None
            
        self.cursor.execute("SELECT CPF, Name, GroupNumber FROM POB WHERE CPF = ?", (cpf_clean,))
        return self.cursor.fetchone()

    def find_people_by_search(self, search_term):
        """
        Busca pessoas pelo nome ou CPF que correspondam ao termo de pesquisa.
        """
        query = "%" + search_term + "%"
        
        # Se o termo de busca parece ser um CPF, limpa ele para busca
        if search_term.replace(".", "").replace("-", "").replace(" ", "").isdigit():
            cpf_clean = self.clean_cpf(search_term)
            self.cursor.execute("SELECT CPF, Name, GroupNumber FROM POB WHERE Name LIKE ? OR CPF LIKE ?", (query, cpf_clean))
        else:
            self.cursor.execute("SELECT CPF, Name, GroupNumber FROM POB WHERE Name LIKE ?", (query,))
        return self.cursor.fetchall()

    def add_person_to_pob(self, cpf, nome, grupo=1):
        """
        Adiciona uma pessoa à tabela POB (People On Board) e registra check-in.
        """
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO POB (CPF, Name, GroupNumber, Onshore)
                VALUES (?, ?, ?, 0)
            ''', (cpf, nome, grupo))
            
            # Registra o check-in
            self.record_check_in_out(cpf, nome, "IN")
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao adicionar pessoa ao POB: {e}")
            return False

    def remove_person_from_pob(self, cpf):
        """
        Remove uma pessoa da tabela POB e registra check-out.
        """
        try:
            # Busca o nome da pessoa antes de remover
            person = self.find_person_by_cpf(cpf)
            if not person:
                return False
                
            nome = person[1]
            
            self.cursor.execute("DELETE FROM POB WHERE CPF = ?", (cpf,))
            
            if self.cursor.rowcount > 0:
                # Registra o check-out
                self.record_check_in_out(cpf, nome, "OUT")
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Erro ao remover pessoa do POB: {e}")
            return False

    def parse_qr_data(self, qr_data):
        """
        Extrai CPF e nome dos dados do QR Code.
        Formato esperado: CPF|NOME
        """
        try:
            if '|' in qr_data:
                parts = qr_data.split('|', 1)  # Split apenas no primeiro |
                cpf = self.clean_cpf(parts[0])
                nome = parts[1].strip()
                return cpf, nome
            else:
                # Fallback para QR Codes antigos que só contêm CPF
                cpf = self.clean_cpf(qr_data)
                if self.validate_cpf(cpf):
                    person_data = self.find_person_by_cpf(cpf)
                    if person_data:
                        return cpf, person_data[1]  # CPF, Name
                return cpf, None
        except Exception as e:
            print(f"Erro ao processar dados do QR Code: {e}")
            return None, None

    def clean_old_records(self):
        """
        Remove registros com mais de 6 meses das tabelas CHECK_EVENT e CHECK_IN_OUT.
        """
        six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # Limpa CHECK_EVENT
            self.cursor.execute("DELETE FROM CHECK_EVENT WHERE Timestamp < ?", (six_months_ago,))
            removed_events = self.cursor.rowcount
            
            # Limpa CHECK_IN_OUT
            self.cursor.execute("DELETE FROM CHECK_IN_OUT WHERE Timestamp < ?", (six_months_ago,))
            removed_checkinout = self.cursor.rowcount
            
            self.conn.commit()
            print(f"Limpeza automática: {removed_events} registros de CHECK_EVENT e {removed_checkinout} registros de CHECK_IN_OUT removidos")
            
        except Exception as e:
            print(f"Erro na limpeza automática: {e}")

    def create_event(self):
        """
        Cria um novo evento e retorna seu ID.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("INSERT INTO EVENTS (Open) VALUES (?)", (timestamp,))
        self.conn.commit()
        return self.cursor.lastrowid

    def close_event(self, event_id):
        """
        Fecha um evento específico.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
            UPDATE EVENTS 
            SET Close = ?, Closed = 1 
            WHERE ID = ?
        ''', (timestamp, event_id))
        self.conn.commit()

    def get_active_event(self):
        """
        Retorna o ID do evento ativo (não fechado) mais recente, ou None se não houver.
        """
        self.cursor.execute('''
            SELECT ID FROM EVENTS 
            WHERE Closed = 0 
            ORDER BY ID DESC 
            LIMIT 1
        ''')
        result = self.cursor.fetchone()
        return result[0] if result else None

    def record_check_in_out(self, cpf, nome, tipo):
        """
        Registra uma operação de check in/out.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
            INSERT INTO CHECK_IN_OUT (CPF, Name, Type, Timestamp)
            VALUES (?, ?, ?, ?)
        ''', (cpf, nome, tipo, timestamp))
        self.conn.commit()

    def record_check_event(self, cpf, nome, event_id):
        """
        Registra a presença de uma pessoa em um evento.
        Armazena o CPF, nome e o timestamp atual.
        """
        # Garante que a mesma pessoa não seja registrada múltiplas vezes no mesmo evento
        self.cursor.execute('''
            SELECT 1 FROM CHECK_EVENT WHERE CPF = ? AND Event = ?
        ''', (cpf, event_id))
        
        if self.cursor.fetchone():
            return False  # Já foi registrado no evento

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
            INSERT INTO CHECK_EVENT (CPF, Name, Timestamp, Event) 
            VALUES (?, ?, ?, ?)
        ''', (cpf, nome, timestamp, event_id))
        self.conn.commit()
        return True

    def get_checks_in_event(self, event_id):
        """
        Retorna um conjunto de CPFs de todas as pessoas que já tiveram a presença no evento
        """
        if not event_id:
            return set()
        self.cursor.execute("SELECT CPF FROM CHECK_EVENT WHERE Event = ?", (event_id,))
        return {row[0] for row in self.cursor.fetchall()}

    def is_person_checked_in_event(self, cpf, event_id):
        """
        Verifica se uma pessoa já teve a presença registrada em um evento específico.
        """
        if not event_id:
            return False
        self.cursor.execute("SELECT 1 FROM CHECK_EVENT WHERE CPF = ? AND Event = ?", (cpf, event_id))
        return self.cursor.fetchone() is not None

    def remove_check_event(self, cpf, event_id):
        """
        Remove o registro de presença de uma pessoa em um evento (estorno de checagem).
        Retorna True se o registro foi removido com sucesso, False caso contrário.
        """
        if not event_id:
            return False
            
        # Verifica se existe o registro antes de tentar remover
        self.cursor.execute("SELECT 1 FROM CHECK_EVENT WHERE CPF = ? AND Event = ?", (cpf, event_id))
        if not self.cursor.fetchone():
            return False
            
        # Remove o registro
        self.cursor.execute("DELETE FROM CHECK_EVENT WHERE CPF = ? AND Event = ?", (cpf, event_id))
        self.conn.commit()
        return True

    def is_person_in_pob(self, cpf):
        """
        Verifica se uma pessoa está atualmente na tabela POB.
        """
        cpf_clean = self.clean_cpf(cpf)
        self.cursor.execute("SELECT 1 FROM POB WHERE CPF = ? AND Onshore = 0", (cpf_clean,))
        return self.cursor.fetchone() is not None

    def update_person(self, cpf, person_data):
        """
        Atualiza os dados de uma pessoa existente no banco de dados.
        """
        try:
            self.cursor.execute('''
                UPDATE POB 
                SET Name = ?, GroupNumber = ?
                WHERE CPF = ?
            ''', (
                person_data['nome'],
                person_data['grupo'],
                cpf
            ))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao atualizar pessoa: {e}")
            return False

    def delete_person(self, cpf):
        """
        Remove uma pessoa do banco de dados.
        """
        try:
            # Primeiro remove os registros de CHECK_EVENT associados
            self.cursor.execute("DELETE FROM CHECK_EVENT WHERE CPF = ?", (cpf,))
            # Remove registros de CHECK_IN_OUT associados
            self.cursor.execute("DELETE FROM CHECK_IN_OUT WHERE CPF = ?", (cpf,))
            # Depois remove a pessoa da tabela POB
            self.cursor.execute("DELETE FROM POB WHERE CPF = ?", (cpf,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao excluir pessoa: {e}")
            return False

    def check_person_exists(self, cpf):
        """
        Verifica se uma pessoa existe no banco de dados.
        """
        cpf_clean = self.clean_cpf(cpf)
        self.cursor.execute("SELECT 1 FROM POB WHERE CPF = ?", (cpf_clean,))
        return self.cursor.fetchone() is not None

    def get_person_details(self, cpf):
        """
        Retorna todos os detalhes de uma pessoa pelo CPF.
        """
        cpf_clean = self.clean_cpf(cpf)
        self.cursor.execute("SELECT CPF, Name, GroupNumber FROM POB WHERE CPF = ?", (cpf_clean,))
        return self.cursor.fetchone()

    def _migrate_group_column(self):
        """
        Migra a coluna 'Group' para 'GroupNumber' se a tabela já existir com a estrutura antiga.
        """
        try:
            # Verifica se a coluna 'Group' existe
            self.cursor.execute("PRAGMA table_info(POB)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            if 'Group' in columns and 'GroupNumber' not in columns:
                # Precisa migrar: renomear Group para GroupNumber
                # SQLite não suporta ALTER COLUMN, então precisamos recriar a tabela
                
                # 1. Criar tabela temporária com nova estrutura
                self.cursor.execute('''
                    CREATE TABLE POB_temp (
                        CPF TEXT PRIMARY KEY,
                        Name TEXT NOT NULL,
                        GroupNumber INTEGER NOT NULL,
                        Onshore INTEGER DEFAULT 1
                    )
                ''')
                
                # 2. Copiar dados da tabela original
                self.cursor.execute('''
                    INSERT INTO POB_temp (CPF, Name, GroupNumber, Onshore)
                    SELECT CPF, Name, [Group], Onshore FROM POB
                ''')
                
                # 3. Remover tabela original
                self.cursor.execute('DROP TABLE POB')
                
                # 4. Renomear tabela temporária
                self.cursor.execute('ALTER TABLE POB_temp RENAME TO POB')
                
                self.conn.commit()
                print("Migração concluída: coluna 'Group' renomeada para 'GroupNumber'")
                
        except Exception as e:
            print(f"Erro durante migração da coluna Group: {e}")
            # Em caso de erro, tenta reverter se possível
            try:
                self.cursor.execute('DROP TABLE IF EXISTS POB_temp')
                self.conn.commit()
            except:
                pass

    def __del__(self):
        """
        Fecha a conexão com o banco de dados quando o objeto é destruído.
        """
        try:
            self.conn.close()
        except Exception:
            pass