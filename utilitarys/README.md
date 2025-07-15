# Utilitários POBChecker

Sistema unificado de gerenciamento de utilitários para POBChecker.

## Estrutura dos Arquivos

### Scripts Utilitários

#### Sistema Geral (`utilitary_system_*`)
- **`utilitary_system_generate_qrcodes.py`** - Geração de QR codes para pessoas

#### Terminais (`utilitary_terminal_*`)
- **`utilitary_terminal_generate.py`** - Geração de dados de teste para terminais
- **`utilitary_terminal_clear.py`** - Limpeza de dados dos terminais
- **`utilitary_terminal_manage.py`** - Gerenciamento completo de dados dos terminais

#### Servidor/Consolidador (`utilitary_server_*`)
- **`utilitary_server_setup.py`** - Configuração do consolidador
- **`utilitary_server_data.py`** - Gerenciamento de dados do consolidador
- **`utilitary_server_tests.py`** - Testes das funcionalidades do consolidador

### Script Principal
- **`utility_manage.py`** - Interface unificada para todos os utilitários

## Como Usar

### Execução Principal
```bash
python utility_manage.py
```

### Execução Individual
```bash
python utilitarys/utilitary_terminal_generate.py
python utilitarys/utilitary_server_setup.py
# etc...
```

## Funcionalidades

### 📋 Funções Gerais
1. **Executar POBChecker Terminal** - Inicia o sistema principal
2. **Inicializar todos os dados** - Configura sistema completo
3. **Listar dados do sistema** - Exibe estatísticas completas
4. **Gerar QR Codes** - Cria códigos QR para pessoas
5. **Visualizar QR Codes** - Abre pasta com QR codes gerados
6. **Executar testes do sistema** - Roda todos os testes

### 🖥️ Funções dos Terminais
7. **Limpar dados dos terminais** - Remove dados locais
8. **Popular terminais com dados de teste** - Adiciona dados de exemplo
9. **Gerenciar dados dos terminais** - Interface completa de gerenciamento

### 🌐 Funções do Consolidador
10. **Configurar consolidador** - Setup inicial do servidor
11. **Iniciar servidor consolidador** - Executa o servidor
12. **Gerenciar dados do consolidador** - Administração de dados
13. **Listar dados do consolidador** - Visualização de dados consolidados
14. **Executar testes do consolidador** - Testes específicos do servidor

## Banco de Dados

- **Terminal**: SQLite (`pobchecker.sqlite3`)
- **Consolidador**: PostgreSQL (configurado via `consolidator_config.json`)

## Configuração

### Terminais
- Configuração automática via SQLite
- Dados de teste com Faker

### Consolidador
- Arquivo: `consolidator_config.json`
- Banco PostgreSQL
- Servidor FastAPI na porta 8000

## Dependências

```
fastapi
uvicorn
psycopg2-binary
requests
qrcode[pil]
faker
zeroconf
```

## Estrutura do Projeto

```
POBChecker/
├── utility_manage.py           # Interface principal
├── utilitarys/                 # Scripts utilitários
│   ├── utilitary_system_*      # Funções gerais
│   ├── utilitary_terminal_*    # Funções dos terminais
│   └── utilitary_server_*      # Funções do consolidador
├── pobchecker_terminal.py      # Sistema principal
├── pobchecker_server.py        # Servidor consolidador
├── database.py                 # Banco SQLite
├── database_postgres.py        # Banco PostgreSQL
└── ...
```

## Changelog

### v3.0 (atual)
- Unificação de `demo_system.py` e `demo_consolidator.py`
- Renomeação de `helper/` para `utilitarys/`
- Padronização de prefixos: `utilitary_system_`, `utilitary_terminal_`, `utilitary_server_`
- Interface unificada com `utility_manage.py`
- Funções organizadas por categoria
- Implementação completa de listagem de dados
- Remoção de arquivos temporários

### v2.0
- Adição de suporte ao consolidador
- Scripts separados para terminal e servidor

### v1.0
- Sistema básico com helpers para terminais
# Configurar consolidador
python helper/helper_consolidator_setup.py

# Gerenciar dados do consolidador
python helper/helper_consolidator_data.py

# Testar consolidador
python helper/helper_consolidator_tests.py
```

### Execução via Menu Principal
```bash
# Menu principal do sistema
python demo_system.py

# Opções do consolidador:
# 7. Configurar Consolidador
# 8. Gerenciar Dados do Consolidador
# 9. Iniciar Servidor Consolidador
# 10. Testar Consolidador
```

## Histórico

Estes scripts foram anteriormente localizados na pasta `aux` com prefixo `aux_`. Foram renomeados para `helper` com prefixo `helper_` para melhor organização e compatibilidade com rotinas de backup.

## Dependências Adicionais para Consolidador

Para usar os scripts do consolidador, instale as dependências:

```bash
pip install fastapi uvicorn psycopg2-binary zeroconf requests
```

## Arquivos de Configuração

- `consolidator_config.json` - Configuração principal do consolidador
- `terminal_config.json` - Configuração dos terminais
- `database_postgres.py` - Modelos do banco PostgreSQL
- `models/consolidator_models.py` - Modelos de dados do consolidador
