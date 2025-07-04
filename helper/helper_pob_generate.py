#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo: helper_pob_generate.py
Descrição: Script auxiliar para popular o banco de dados com dados de teste usando Faker
Antigo nome: aux_pob_generate.py (renomeado de aux para helper)
"""

import sys
import os
from faker import Faker
from faker.providers import person
import random

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

def generate_cpf():
    """Gera um CPF válido aleatório"""
    cpf_base = [random.randint(0, 9) for _ in range(9)]
    
    # Calcula primeiro dígito verificador
    sum1 = sum(cpf_base[i] * (10 - i) for i in range(9))
    digit1 = 11 - (sum1 % 11)
    if digit1 >= 10:
        digit1 = 0
    
    # Calcula segundo dígito verificador
    cpf_with_first_digit = cpf_base + [digit1]
    sum2 = sum(cpf_with_first_digit[i] * (11 - i) for i in range(10))
    digit2 = 11 - (sum2 % 11)
    if digit2 >= 10:
        digit2 = 0
    
    cpf = cpf_base + [digit1, digit2]
    return ''.join(map(str, cpf))

def populate_database():
    """Popula o banco de dados com dados de teste"""
    print("POBCHECKER - GERADOR DE DADOS DE TESTE")
    print("=" * 50)
    
    try:
        # Conecta ao banco
        db = Database()
        fake = Faker('pt_BR')
        
        # Número de pessoas para gerar
        num_people = int(input("Quantas pessoas deseja gerar? (padrão: 20): ") or "20")
        
        print(f"\nGerando {num_people} pessoas...")
        
        generated_cpfs = set()
        
        for i in range(num_people):
            # Gera CPF único
            while True:
                cpf = generate_cpf()
                if cpf not in generated_cpfs:
                    generated_cpfs.add(cpf)
                    break
            
            # Gera dados da pessoa
            nome = fake.name()
            grupo = random.randint(1, 5)  # Grupos de 1 a 5
            onshore = random.choice([0, 1])  # 0 = Offshore, 1 = Onshore
            
            person_data = {
                'cpf': cpf,
                'nome': nome,
                'grupo': grupo,
                'Onshore': onshore
            }
            
            # Insere no banco
            success = db.insert_person(person_data)
            if success:
                print(f"✓ {i+1:2d}. {nome} (CPF: {cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}) - Grupo {grupo}")
            else:
                print(f"✗ Erro ao inserir: {nome}")
        
        print(f"\n✅ Processo concluído! {num_people} pessoas geradas.")
        
        # Mostra estatísticas
        cursor = db.cursor
        cursor.execute("SELECT COUNT(*) FROM POB")
        total_people = cursor.fetchone()[0]
        print(f"📊 Total de pessoas no banco: {total_people}")
        
    except Exception as e:
        print(f"❌ Erro ao popular banco de dados: {e}")
        return False
    
    return True

if __name__ == "__main__":
    populate_database()
