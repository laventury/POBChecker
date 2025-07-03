# Arquivo: database.py

import sqlite3
from datetime import datetime

class Database:
    """
    Classe para gerenciar todas as operações do banco de dados SQLite.
    Isso centraliza a lógica do banco de dados em um único lugar.
    """
    def __init__(self, db_file="pob_db.sqlite3"):
        """
        Inicializa a conexão com o banco de dados e cria as tabelas se não existirem.
        """
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """
        Cria as tabelas 'POB','EVENTS','checks' se elas ainda não existirem no banco.
        """
        # Tabela de Pessoas a Bordo (POB)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS POB (
                CPF TEXT PRIMARY KEY,
                Matricula INTEGER,
                Nome TEXT NOT NULL,
                Grupo INTEGER NOT NULL,
                Onshore INTEGER DEFAULT 1
            )
        ''')

        # Tabela de registro de eventos (alerta, embarque, etc.)
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS EVENTS (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                Timestamp TEXT NOT NULL,
                                EventType TEXT NOT NULL,
                                Closed INTEGER DEFAULT 0,
                                Closed_Timestamp TEXT NULL    
                            )
                            ''')
        self.conn.commit()

        # Tabela de registro de checagem de pessoas nos eventos
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS CHECKS (
                                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                CPF TEXT,
                                Nome TEXT,
                                Timestamp TEXT NOT NULL,
                                Event INTEGER,
                                FOREIGN KEY (CPF) REFERENCES POB (CPF),
                                FOREIGN KEY (Event) REFERENCES EVENTS (ID)       
                            )
                            ''')
        
        # Migração automática: adiciona coluna Nome se não existir
        try:
            self.cursor.execute("SELECT Nome FROM CHECKS LIMIT 1")
        except sqlite3.OperationalError:
            # Coluna Nome não existe, adiciona ela
            print("Database: Migrando tabela CHECKS - adicionando coluna Nome")
            self.cursor.execute("ALTER TABLE CHECKS ADD COLUMN Nome TEXT")
            
        self.conn.commit()

    def insert_person(self, person_data):
        """
        Insere uma nova pessoa na tabela POB.
        """
        try:
            self.cursor.execute('''
                INSERT INTO POB (CPF, Matricula, Nome, Grupo, Onshore)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                person_data['cpf'],
                person_data.get('matricula'),
                person_data['nome'],
                person_data['grupo'],
                person_data['Onshore']
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao inserir pessoa: {e}")
            return False

    def get_event(self, event_type):
        """
        Insere um novo evento na tabela EVENTS com o tipo especificado.
        """

        # Garante que não exista evento aberto do mesmo tipo        
        self.cursor.execute("""
            SELECT MAX(ID) FROM EVENTS WHERE EventType = ? AND Closed = 0
        """, (event_type,))

        row = self.cursor.fetchone()
        if row and row[0] is not None:
            return row[0]

        # Registra novo evento
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("INSERT INTO EVENTS (Timestamp, EventType) VALUES (?, ?)", (timestamp, event_type))
        self.conn.commit()
        return self.cursor.lastrowid
            

    def get_people_by_group(self, group_number):
        """
        Retorna uma lista de todas as pessoas de um determinado grupo.
        """
        self.cursor.execute("SELECT CPF, Nome, Grupo FROM POB WHERE Grupo = ? ORDER BY Nome", (group_number,))
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
            
        self.cursor.execute("SELECT CPF, Nome, Grupo FROM POB WHERE CPF = ?", (cpf_clean,))
        return self.cursor.fetchone()

    def find_people_by_search(self, search_term):
        """
        Busca pessoas pelo nome ou CPF que correspondam ao termo de pesquisa.
        """
        query = "%" + search_term + "%"
        
        # Se o termo de busca parece ser um CPF, limpa ele para busca
        if search_term.replace(".", "").replace("-", "").replace(" ", "").isdigit():
            cpf_clean = self.clean_cpf(search_term)
            self.cursor.execute("SELECT CPF, Nome, Grupo FROM POB WHERE Nome LIKE ? OR CPF LIKE ?", (query, cpf_clean))
        else:
            self.cursor.execute("SELECT CPF, Nome, Grupo FROM POB WHERE Nome LIKE ?", (query,))
        return self.cursor.fetchall()

    def person_check(self, cpf, nome, event):
        """
        Registra a presença de uma pessoa na tabela CHECKS.
        Armazena o CPF, nome e o timestamp atual.
        """
        # Garante que a mesma pessoa não seja registrada múltiplas vezes no mesmo evento
        self.cursor.execute("""
            SELECT 1 FROM CHECKS WHERE CPF = ? AND Event = ?
        """, (cpf, event))
        
        if self.cursor.fetchone():
            return # Já foi registrado no evento

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("INSERT INTO CHECKS (CPF, Nome, Timestamp, Event) VALUES (?, ?, ?, ?)", (cpf, nome, timestamp, event))
        self.conn.commit()

    def add_person_to_pob(self, cpf, nome, grupo=1):
        """
        Adiciona uma pessoa à tabela POB (People On Board).
        """
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO POB (CPF, Nome, Grupo, Onshore)
                VALUES (?, ?, ?, 0)
            ''', (cpf, nome, grupo))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao adicionar pessoa ao POB: {e}")
            return False

    def remove_person_from_pob(self, cpf):
        """
        Remove uma pessoa da tabela POB.
        """
        try:
            self.cursor.execute("DELETE FROM POB WHERE CPF = ?", (cpf,))
            self.conn.commit()
            return self.cursor.rowcount > 0
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
                        return cpf, person_data[1]  # CPF, Nome
                return cpf, None
        except Exception as e:
            print(f"Erro ao processar dados do QR Code: {e}")
            return None, None

    def get_checks_in_event(self, event):
        """
        Retorna um conjunto de CPFs de todas as pessoas que já tiveram a presença no evento
        """
        self.cursor.execute("SELECT CPF FROM CHECKS WHERE Event = ?", (event,))
        return {row[0] for row in self.cursor.fetchall()}

    def update_person(self, cpf, person_data):
        """
        Atualiza os dados de uma pessoa existente no banco de dados.
        """
        try:
            self.cursor.execute('''
                UPDATE POB 
                SET Matricula = ?, Nome = ?, Grupo = ?
                WHERE CPF = ?
            ''', (
                person_data.get('matricula'),
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
            # Primeiro remove os registros de CHECKS associados
            self.cursor.execute("DELETE FROM CHECKS WHERE CPF = ?", (cpf,))
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
        self.cursor.execute("SELECT CPF, Matricula, Nome, Grupo FROM POB WHERE CPF = ?", (cpf_clean,))
        return self.cursor.fetchone()

    def __del__(self):
        """
        Fecha a conexão com o banco de dados quando o objeto é destruído.
        """
        try:
            self.conn.close()
        except Exception:
            pass