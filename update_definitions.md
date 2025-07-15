# Atualização do Sistema POBChecker - Consolidador

## Resumo das Alterações

### 📁 Novos Arquivos Criados

#### Helper Scripts para Consolidador:
1. **`helper/helper_consolidator_setup.py`**
   - Configuração do PostgreSQL
   - Teste de conexão com banco
   - Configuração de parâmetros do consolidador
   - Inicialização do servidor
   - Verificação de status
   - Limpeza de dados do consolidador

2. **`helper/helper_consolidator_data.py`**
   - Visualização de estatísticas consolidadas
   - Geração de dados de teste
   - Sincronização entre terminais
   - Verificação de correlações
   - Exportação de dados (JSON, CSV, Excel)
   - Backup e restauração

3. **`helper/helper_consolidator_tests.py`**
   - Teste de configuração
   - Teste de conexão com banco
   - Teste de servidor API
   - Teste de sincronização
   - Teste de correlação de eventos
   - Teste de descoberta de terminais
   - Teste completo do sistema

4. **`demo_consolidator.py`**
   - Demonstração das funcionalidades do consolidador
   - Fluxo de configuração
   - Verificação de dependências

#### Arquivos de Configuração:
5. **`configure_consolidator_postgresql.py`**
   - Script para configurar PostgreSQL
   - Criação de banco e tabelas
   - Configuração de índices

### 📝 Arquivos Atualizados

#### 1. **`demo_system.py`**
**Novas opções adicionadas:**
- `7. Configurar Consolidador`
- `8. Gerenciar Dados do Consolidador`
- `9. Iniciar Servidor Consolidador`
- `10. Testar Consolidador`

**Novas funções:**
- `setup_consolidator()`
- `manage_consolidator_data()`
- `start_consolidator_server()`
- `test_consolidator()`

#### 2. **`helper/helper_clear_data.py`**
**Novas opções adicionadas:**
- `4. Limpar dados do consolidador`

**Nova função:**
- `clear_consolidator_data()`

#### 3. **`helper/README.md`**
**Documentação atualizada:**
- Adicionada seção "Scripts do Consolidador"
- Documentação das funcionalidades
- Instruções de uso
- Dependências adicionais

## 🎯 Funcionalidades Implementadas

### Sistema de Consolidação
- **Agregação de dados** de múltiplos terminais
- **Correlação automática** de eventos por tempo
- **Dashboard web** em tempo real
- **Sincronização temporal** entre terminais
- **API REST** para integração

### Gerenciamento de Dados
- **Backup automático** e restauração
- **Exportação** em múltiplos formatos
- **Limpeza** de dados antigos
- **Estatísticas** em tempo real

### Testes e Validação
- **Testes automatizados** de todos os componentes
- **Verificação** de configuração
- **Validação** de conectividade
- **Testes** de performance

## 🔧 Como Usar

### Configuração Inicial
```bash
# 1. Execute o menu principal
python demo_system.py

# 2. Escolha "7. Configurar Consolidador"
# 3. Configure PostgreSQL (se necessário)
# 4. Teste a configuração
```

### Executar Consolidador
```bash
# 1. No menu principal, escolha "9. Iniciar Servidor Consolidador"
# 2. Acesse http://localhost:8000/dashboard
# 3. Use a API em http://localhost:8000/docs
```

### Gerenciar Dados
```bash
# 1. No menu principal, escolha "8. Gerenciar Dados do Consolidador"
# 2. Explore as opções de backup, exportação e limpeza
```

### Executar Testes
```bash
# 1. No menu principal, escolha "10. Testar Consolidador"
# 2. Execute testes individuais ou completos
```

## 🌐 Acesso Web

- **Dashboard**: http://localhost:8000/dashboard
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📦 Dependências Adicionais

Para usar o consolidador, instale:
```bash
pip install fastapi uvicorn psycopg2-binary zeroconf requests
```

## 🏗️ Arquitetura

```
Terminal 1 ────┐
Terminal 2 ────┤ → Consolidador → Dashboard/API
Terminal 3 ────┘
```

## 📊 Dados Consolidados

- **Eventos correlacionados** por tempo
- **Status** de todos os terminais
- **Estatísticas agregadas**
- **Histórico** de sincronização
- **Logs** de operações

## ✅ Status da Implementação

- [x] Helpers de configuração
- [x] Helpers de gerenciamento de dados
- [x] Helpers de testes
- [x] Integração com menu principal
- [x] Documentação atualizada
- [x] Script de configuração PostgreSQL
- [x] Demo do consolidador

## 🚀 Próximos Passos

1. **Configurar PostgreSQL** (se necessário)
2. **Executar demo_system.py** para acessar todas as funcionalidades
3. **Testar o consolidador** com dados reais
4. **Configurar terminais** para enviar dados
5. **Monitorar dashboard** em tempo real

---

**Atualização concluída!** O sistema POBChecker agora inclui funcionalidades completas de consolidação com interface web, API REST e gerenciamento avançado de dados.

---

### **Especificação Técnica Original: Arquitetura Distribuída do POBChecker**

#### 1. Resumo Executivo

Este documento detalha os requisitos técnicos para a evolução do sistema **POBChecker** de uma aplicação de terminal único para uma arquitetura distribuída. O objetivo é permitir que múltiplos terminais operem de forma autônoma e resiliente, sincronizando seus dados com um servidor central de forma automática e transparente.

Os princípios fundamentais desta nova arquitetura são:

  * **Operação Offline-First:** Os terminais devem ser 100% funcionais sem conexão de rede.
  * **Consolidação Central:** Um servidor central (pobchecker_server.py) agregará os dados de todos os terminais para monitoramento e geração de relatórios.
  * **Sincronização Assíncrona:** Os dados são transmitidos para o servidor apenas quando uma conexão de rede estiver disponível, sem interromper a operação local.
  * **Rede Plug and Play:** Novos terminais devem se conectar à rede e começar a operar sem necessidade de configuração manual de endereço de servidor.

#### 2. Visão Geral da Arquitetura

O sistema será composto por dois componentes principais:

1.  **Terminal POBChecker (Cliente - pobchecker_terminal.py):** A aplicação existente (`pobchecker_terminal.py`), modificada para incluir lógica de sincronização e descoberta de serviço.
2.  **Servidor Central POBChecker (Consolidador - pobchecker_server.py):** Uma nova aplicação responsável por receber, armazenar e disponibilizar os dados consolidados.

 *(Nota: Diagrama conceitual)*
`[Terminal 1] ---> [Rede Local (LAN)] <--- [Terminal 2]`
`      |                   ^                   | `
`  (Sync via mDNS)         |              (Sync via mDNS) `
`      |                   |                   | `
`      +-----------------> [Servidor Central] <-----------------+ `

-----

### **3. Especificações para o Terminal POBChecker (Cliente)**

O projeto `pobchecker_terminal.py` deve ser modificado para incorporar as seguintes funcionalidades.

**3.1. Alterações no Banco de Dados Local (SQLite)**

Nas tabelas que armazenam os registros de check de presença de eventos e check in/out, uma nova coluna deve ser adicionada para controlar o estado da sincronização.

  * **Tabela `CHECK_EVENT`:**
      * **Adicionar Coluna:** `Synced`
          * **Tipo:** `INTEGER`
          * **Valor Padrão:** `0`
          * **Lógica:** O valor será `0` para registros novos ou não sincronizados e `1` para registros já enviados com sucesso ao servidor.

  * **Tabela `CHECK_IN_OUT`:**
      * **Adicionar Coluna:** `Synced`
          * **Tipo:** `INTEGER`
          * **Valor Padrão:** `0`
          * **Lógica:** O valor será `0` para registros novos ou não sincronizados e `1` para registros já enviados com sucesso ao servidor.

**3.2. Novo Módulo: Serviço de Sincronização (`sync_service.py`)**

Este módulo rodará em uma thread separada em segundo plano.

  * **Gatilho:** Execução periódica (a cada 20 segundos).
  * **Lógica de Execução:**
    1.  **Descobrir Servidor:** Utilizar o módulo de descoberta de serviço (ver item 3.3) para encontrar o IP e a porta do Servidor Central na rede. Se não encontrar, encerrar o ciclo e tentar novamente na próxima execução.
    2.  **Coletar Dados:** Executar queries no banco de dados local:
        * `SELECT ID, CPF, Name, Timestamp, Event FROM CHECK_EVENT WHERE Synced = 0;`
        * `SELECT ID, CPF, Name, Type, Timestamp FROM CHECK_IN_OUT WHERE Synced = 0;`
    3.  **Enviar Dados:** Se houver registros a serem sincronizados, formatá-los em JSON e enviá-los via uma requisição `POST` para o endpoint `/sync` da API do Servidor Central.
    4.  **Processar Resposta:**
          * **Sucesso (HTTP 200 OK):** O servidor confirmou o recebimento. Executar um `UPDATE` no banco de dados local para definir `Synced = 1` para todos os registros que foram enviados.
          * **Falha (Outro Código HTTP ou Timeout):** Não fazer nada. Os registros permanecerão com `Synced = 0` e a sincronização será tentada novamente no próximo ciclo.
  * **Dependências:** `requests`

**3.3. Novo Módulo: Descoberta de Serviço (`discovery.py`)**

Este módulo implementará a funcionalidade "plug and play".

  * **Tecnologia:** **Zeroconf** (via biblioteca Python `zeroconf`).
  * **Lógica:**
      * O terminal deverá "escutar" (browse) na rede local por um serviço específico.
      * **Nome do Serviço:** `_pobchecker._tcp.local.`
      * Quando o serviço for encontrado, o módulo extrairá o endereço IP e a porta do servidor e os disponibilizará para o `sync_service`.
  * **Dependências:** `zeroconf`

-----

### **4. Especificações para o Servidor Central POBChecker (Consolidador)**

Esta é uma **nova aplicação** a ser desenvolvida do zero.

**4.1. Tecnologias Recomendadas**

  * **Linguagem:** Python 3
  * **Framework Web/API:** **FastAPI** (recomendado pela performance e documentação automática) ou Flask.
  * **Banco de Dados:** **PostgreSQL** (recomendado pela robustez) ou MySQL.
  * **Descoberta de Serviço:** Biblioteca `zeroconf`.

**4.2. Banco de Dados Central (PostgreSQL)**

Deverá conter tabelas para consolidar os registros de ambos os modos de operação.

  * **Tabela:** `check_event_consolidated`
  * **Colunas:**
      * `id` (PK, Serial)
      * `terminal_id` (VARCHAR(255), para identificar de qual terminal veio o dado)
      * `original_id` (INTEGER, ID original do registro no terminal)
      * `CPF` (VARCHAR)
      * `Name` (VARCHAR)
      * `Timestamp` (TIMESTAMP, data e hora do evento)
      * `Event` (INTEGER, ID do evento)
      * `sync_timestamp` (TIMESTAMP, data e hora que o registro foi recebido pelo servidor)

  * **Tabela:** `check_in_out_consolidated`
  * **Colunas:**
      * `id` (PK, Serial)
      * `terminal_id` (VARCHAR(255), para identificar de qual terminal veio o dado)
      * `original_id` (INTEGER, ID original do registro no terminal)
      * `CPF` (VARCHAR)
      * `Name` (VARCHAR)
      * `Type` (VARCHAR, 'IN' ou 'OUT')
      * `Timestamp` (TIMESTAMP, data e hora do evento)
      * `sync_timestamp` (TIMESTAMP, data e hora que o registro foi recebido pelo servidor)

**4.3. API Endpoints (Contrato de Comunicação)**

O servidor deverá expor os seguintes endpoints RESTful:

  * **`POST /sync`**

      * **Função:** Receber um lote de registros de um terminal.
      * **Corpo da Requisição (JSON):**
        ```json
        {
          "terminal_id": "terminal-sala-controle-01",
          "check_events": [
            {
              "id": 1,
              "CPF": "12345678901",
              "Name": "João Silva Santos",
              "Timestamp": "2025-07-05T18:30:00Z",
              "Event": 1
            }
          ],
          "check_in_outs": [
            {
              "id": 2,
              "CPF": "12345678901",
              "Name": "João Silva Santos",
              "Type": "IN",
              "Timestamp": "2025-07-05T18:25:00Z"
            }
          ]
        }
        ```
      * **Lógica de Negócios:** Para cada registro recebido, verificar se já existe uma entrada idêntica (`terminal_id`, `original_id`) para evitar duplicatas (idempotência). Se não existir, inserir na tabela correspondente.
      * **Resposta de Sucesso:** `HTTP 200 OK` com um corpo JSON `{ "status": "success", "check_events_received": 1, "check_in_outs_received": 1 }`.
      * **Resposta de Erro:** `HTTP 400 Bad Request` se o formato dos dados for inválido.

  * **`GET /pob/status`**

      * **Função:** Fornecer uma visão geral do POB atual consolidado.
      * **Resposta:** JSON contendo o número total de pessoas a bordo e, opcionalmente, a lista de quem está a bordo baseado nos últimos check-ins/check-outs.

  * **`GET /records`**

      * **Função:** Permitir a consulta de registros com filtros (por data, CPF, terminal, etc.).
      * **Exemplo:** `GET /records?start_date=2025-07-01&CPF=12345678901&terminal_id=terminal-01`

  * **`GET /events`**

      * **Função:** Consultar registros de eventos específicos.
      * **Exemplo:** `GET /events?event_id=1&terminal_id=terminal-01`

**4.4. Serviço de Anúncio (mDNS)**

O servidor, ao iniciar, deve anunciar sua presença na rede.

  * **Tecnologia:** `zeroconf`
  * **Lógica:** Criar e registrar um `ServiceInfo` com os seguintes dados:
      * **Tipo:** `_pobchecker._tcp.local.`
      * **Nome:** `Servidor POBChecker Central._pobchecker._tcp.local.`
      * **Endereço:** O endereço IP do servidor na rede local.
      * **Porta:** A porta onde a API está rodando (ex: 8000).

-----

### **5. Requisitos Não-Funcionais**

  * **Segurança:** A comunicação entre terminal e servidor deve ser protegida. Recomenda-se o uso de uma chave de API (API Key) simples, enviada no cabeçalho de cada requisição, para garantir que apenas terminais autorizados possam enviar dados.
  * **Logging:** Ambos, terminal e servidor, devem gerar logs detalhados de suas operações, especialmente das tentativas de sincronização, sucessos e falhas. Isso é crucial para depuração.
  * **Configuração:** O `terminal_id` de cada terminal deve ser definido em um arquivo de configuração simples no dispositivo para que seja facilmente identificável no servidor.

### **6. Plano de Implementação Sugerido (Milestones)**

1.  **Fase 1: Backend**

      * [ ] Desenvolver a aplicação do Servidor Central com FastAPI.
      * [ ] Configurar o banco de dados PostgreSQL e o schema das tabelas.
      * [ ] Implementar o endpoint `POST /sync` e sua lógica de negócio.
      * [ ] Implementar o Serviço de Anúncio mDNS no servidor.

2.  **Fase 2: Frontend (Terminal)**

      * [ ] Modificar o schema do banco de dados SQLite no terminal (adicionar coluna `Synced`).
      * [ ] Desenvolver o módulo de Descoberta de Serviço (`discovery.py`).
      * [ ] Desenvolver o Serviço de Sincronização (`sync_service.py`) como uma thread.
      * [ ] Integrar os novos módulos à aplicação principal `pobchecker_terminal.py`.

3.  **Fase 3: Testes e Validação**

      * [ ] Testar a sincronização em um ambiente de rede ideal.
      * [ ] Testar o cenário de falha: desligar o servidor ou a rede e verificar se o terminal continua operando e se os dados são sincronizados quando a conexão é restaurada.
      * [ ] Testar o cenário "plug and play" com um novo terminal.

---

### **7. Detalhes Técnicos Específicos**

**7.1. Estrutura das Tabelas Existentes (para referência)**

* **Tabela `POB`:**
  - `CPF` (TEXT, PRIMARY KEY)
  - `Name` (TEXT)
  - `GroupNumber` (INTEGER)
  - `Onshore` (INTEGER, 0=a bordo, 1=em terra)

* **Tabela `EVENTS`:**
  - `ID` (INTEGER, PRIMARY KEY AUTOINCREMENT)
  - `Open` (TEXT, timestamp abertura)
  - `Close` (TEXT, timestamp fechamento)
  - `Closed` (INTEGER, 0=ativo, 1=fechado)

* **Tabela `CHECK_EVENT`:**
  - `ID` (INTEGER, PRIMARY KEY AUTOINCREMENT)
  - `CPF` (TEXT)
  - `Name` (TEXT)
  - `Timestamp` (TEXT)
  - `Event` (INTEGER, FK para EVENTS.ID)
  - `Synced` (INTEGER, nova coluna - 0=não sincronizado, 1=sincronizado)

* **Tabela `CHECK_IN_OUT`:**
  - `ID` (INTEGER, PRIMARY KEY AUTOINCREMENT)
  - `CPF` (TEXT)
  - `Name` (TEXT)
  - `Type` (TEXT, 'IN' ou 'OUT')
  - `Timestamp` (TEXT)
  - `Synced` (INTEGER, nova coluna - 0=não sincronizado, 1=sincronizado)

**7.2. Comandos SQL para Alteração das Tabelas**

```sql
-- Adicionar coluna Synced na tabela CHECK_EVENT
ALTER TABLE CHECK_EVENT ADD COLUMN Synced INTEGER DEFAULT 0;

-- Adicionar coluna Synced na tabela CHECK_IN_OUT
ALTER TABLE CHECK_IN_OUT ADD COLUMN Synced INTEGER DEFAULT 0;
```

**7.3. Configuração do Terminal**

Criar arquivo `terminal_config.json`:
```json
{
  "terminal_id": "terminal-plataforma-01",
  "location": "Sala de Controle",
  "sync_interval": 20,
  "api_key": "sua-chave-api-aqui"
}
```

### **8. Especificações da Interface do Consolidador**

**8.1. Visão Geral da Interface**

- **Público-alvo:** Supervisores, gerentes de plataforma, operadores de sala de controle e pessoal de segurança
- **Tipo:** Aplicação web responsiva com suporte a dashboard em tela grande
- **Atualização:** Tempo real (20s) via WebSocket/Server-Sent Events
- **Framework:** FastAPI + Frontend responsivo

**8.2. Estrutura de Navegação**

```
┌─────────────────────────────────────────────────────────────┐
│ POBChecker - Consolidador Central                    [⟲ 20s] │
├─────────────────────────────────────────────────────────────┤
│ [📊 Dashboard] [🎯 Eventos] [📋 Relatórios] [🖥️ Terminais] [🔌 API] │
└─────────────────────────────────────────────────────────────┘
```

**8.3. Páginas da Interface**

- **Dashboard Principal:**
  - POB Total Consolidado (soma de todos os terminais)
  - Eventos Ativos (contador de eventos correlacionados)
  - Status dos Terminais (grid com conectividade)
  - POB por Terminal (lista detalhada)

- **Página de Eventos:**
  - Eventos Ativos (cards expansíveis)
  - Histórico de Eventos (tabela paginada - 50 itens/página)
  - Correlação Automática (eventos na tolerância temporal)
  - Estatísticas de Presença

- **Página de Relatórios:**
  - Filtros: Data (dd/mm/yyyy), Terminal, Evento
  - Exportação: PDF e Excel
  - Estatísticas gerais, primeiro/último check por terminal
  - Lista de presentes/faltantes com horários

- **Página de Terminais:**
  - Status de conectividade
  - Última sincronização
  - Dados recebidos
  - Detalhes expandíveis

- **Página de API:**
  - Documentação Swagger UI
  - Endpoints para integração futura
  - Exemplos de requests/responses

**8.4. Responsividade**

- **Desktop (>1200px):** Layout full com todas as seções
- **Tablet (768px-1199px):** Layout adaptado com abas
- **Mobile (320px-767px):** Interface simplificada com menu hambúrguer

---

### **9. Lógica de Correlação de Eventos**

**9.1. Problema da Correlação**

Como os terminais geram IDs de eventos independentemente, eventos simultâneos na mesma plataforma podem ter IDs diferentes. O consolidador deve correlacionar esses eventos baseado em janela temporal.

**9.2. Algoritmo de Correlação**

```python
class EventCorrelator:
    def __init__(self, tolerance_minutes=30):
        self.tolerance_minutes = tolerance_minutes
    
    def correlate_events(self, terminal_events):
        """
        Correlaciona eventos de terminais diferentes baseado em janela temporal
        """
        correlated_groups = []
        processed_events = set()
        
        for event in terminal_events:
            if event.id in processed_events:
                continue
                
            # Busca eventos relacionados na janela temporal
            related_events = self.find_related_events(
                event, 
                terminal_events, 
                processed_events
            )
            
            if related_events:
                consolidated = self.create_consolidated_event(related_events)
                correlated_groups.append(consolidated)
                processed_events.update(e.id for e in related_events)
        
        return correlated_groups
    
    def find_related_events(self, base_event, all_events, processed):
        """
        Encontra eventos relacionados dentro da tolerância temporal
        """
        tolerance_delta = timedelta(minutes=self.tolerance_minutes)
        related = [base_event]
        
        for event in all_events:
            if (event.id not in processed and 
                event.terminal_id != base_event.terminal_id and
                abs(event.start_time - base_event.start_time) <= tolerance_delta):
                related.append(event)
        
        return related
```

**9.3. Estrutura do Evento Consolidado**

```python
@dataclass
class ConsolidatedEvent:
    consolidated_id: int
    start_time: datetime
    end_time: Optional[datetime]
    participating_terminals: List[str]
    original_events: List[Dict]
    total_expected: int
    total_present: int
    completion_percentage: float
    is_active: bool
    created_at: datetime
    
    def get_terminal_stats(self):
        """Retorna estatísticas por terminal"""
        stats = {}
        for terminal_id in self.participating_terminals:
            terminal_data = self.get_terminal_data(terminal_id)
            stats[terminal_id] = {
                'expected': terminal_data['expected'],
                'present': terminal_data['present'],
                'percentage': terminal_data['percentage'],
                'first_check': terminal_data['first_check'],
                'last_check': terminal_data['last_check']
            }
        return stats
```

**9.4. Tabela de Eventos Consolidados**

```sql
CREATE TABLE consolidated_events (
    id SERIAL PRIMARY KEY,
    consolidated_id INTEGER UNIQUE NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    participating_terminals TEXT[] NOT NULL,
    original_events JSONB NOT NULL,
    total_expected INTEGER NOT NULL,
    total_present INTEGER NOT NULL,
    completion_percentage FLOAT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### **10. Configurações Detalhadas**

**10.1. Arquivo de Configuração do Consolidador**

```json
{
  "consolidator_config": {
    "server": {
      "host": "0.0.0.0",
      "port": 8000,
      "debug": false
    },
    "correlation": {
      "tolerance_minutes": 30,
      "auto_correlate": true
    },
    "interface": {
      "theme": "light",
      "auto_refresh_seconds": 20,
      "pagination_size": 50,
      "date_format": "dd/mm/yyyy",
      "timezone": "America/Sao_Paulo"
    },
    "database": {
      "host": "localhost",
      "port": 5432,
      "name": "pobchecker_consolidated",
      "user": "pobchecker",
      "password": "senha_segura"
    },
    "network": {
      "mdns_service_name": "_pobchecker._tcp.local.",
      "api_key": "consolidador-api-key-2025"
    },
    "time_sync": {
      "enabled": true,
      "primary_ntp_server": "pool.ntp.org",
      "backup_ntp_servers": [
        "time.google.com",
        "time.cloudflare.com",
        "time.nist.gov",
        "pool.ntp.br"
      ],
      "sync_interval_seconds": 3600,
      "timeout_seconds": 5,
      "max_offset_tolerance": 300,
      "fallback_to_local": true,
      "retry_failed_servers": true,
      "max_retry_attempts": 3
    }
  }
}
```

**10.2. Arquivo de Configuração do Terminal (atualizado)**

```json
{
  "terminal_config": {
    "terminal_id": "terminal-plataforma-01",
    "location": "Sala de Controle",
    "sync_interval_seconds": 20,
    "timezone": "America/Sao_Paulo",
    "api_key": "terminal-api-key-2025",
    "time_sync": {
      "enabled": true,
      "primary_ntp_server": "pool.ntp.org",
      "backup_ntp_servers": [
        "time.google.com",
        "time.cloudflare.com",
        "time.nist.gov",
        "pool.ntp.br"
      ],
      "sync_interval_seconds": 3600,
      "timeout_seconds": 5,
      "max_offset_tolerance": 300,
      "fallback_to_local": true,
      "retry_failed_servers": true,
      "max_retry_attempts": 3
    }
  }
}
```

**10.3. Exemplos de Configuração para Diferentes Ambientes**

#### **Ambiente Corporativo (Servidor NTP Interno)**
```json
{
  "time_sync": {
    "enabled": true,
    "primary_ntp_server": "ntp.empresa.com.br",
    "backup_ntp_servers": [
      "ntp2.empresa.com.br",
      "10.0.1.100",
      "pool.ntp.br"
    ],
    "sync_interval_seconds": 1800,
    "timeout_seconds": 10
  }
}
```

#### **Ambiente Offshore (Rede Restrita)**
```json
{
  "time_sync": {
    "enabled": true,
    "primary_ntp_server": "192.168.1.100",
    "backup_ntp_servers": [
      "192.168.1.101",
      "192.168.1.102"
    ],
    "sync_interval_seconds": 7200,
    "timeout_seconds": 15,
    "fallback_to_local": true
  }
}
```

#### **Ambiente Sem Internet (Somente Local)**
```json
{
  "time_sync": {
    "enabled": false,
    "fallback_to_local": true
  }
}
```

---

### **11. Sincronização Temporal**

**11.1. Problema da Sincronização**

Para correlação eficaz de eventos, os relógios dos terminais e do consolidador devem estar sincronizados. Diferenças de tempo podem afetar a correlação.

**11.2. Estratégia de Sincronização**

- **NTP (Network Time Protocol):** Terminais e consolidador devem **tentar** sincronizar com servidor NTP
- **Sincronização Periódica:** Rotina executada a cada 1 hora
- **Tolerância de Deriva:** Aceitar diferenças de até 5 minutos entre terminais
- **⚠️ Funcionamento Não-Bloqueante:** Falhas na sincronização NTP **NÃO** devem impedir o funcionamento do sistema
- **Fallback para Tempo Local:** Em caso de falha, usar tempo local do sistema
- **Retry Automático:** Tentativas periódicas de reconexão NTP
- **Múltiplos Servidores:** Suporte a servidor principal e servidores de backup
- **Configuração Flexível:** Todos os parâmetros NTP são configuráveis

**11.3. Implementação da Sincronização**

```python
import ntplib
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, List
import json

class TimeSync:
    def __init__(self, config_file=None):
        # Carrega configuração do arquivo
        self.config = self._load_config(config_file)
        
        # Configurações NTP
        self.primary_ntp_server = self.config.get('primary_ntp_server', 'pool.ntp.org')
        self.backup_ntp_servers = self.config.get('backup_ntp_servers', [
            'time.google.com',
            'time.cloudflare.com',
            'time.nist.gov',
            'pool.ntp.br'
        ])
        
        # Configurações de sincronização
        self.retry_interval = self.config.get('sync_interval_seconds', 3600)
        self.timeout = self.config.get('timeout_seconds', 5)
        self.max_retry_attempts = self.config.get('max_retry_attempts', 3)
        self.retry_failed_servers = self.config.get('retry_failed_servers', True)
        
        # Estado da sincronização
        self.last_sync = None
        self.time_offset = 0
        self.sync_enabled = self.config.get('enabled', True)
        self.sync_thread = None
        self.is_ntp_available = False
        self.current_server = None
        self.failed_servers = set()
        
    def _load_config(self, config_file):
        """Carrega configuração do arquivo JSON"""
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    full_config = json.load(f)
                    # Extrai configuração time_sync baseado no tipo de arquivo
                    if 'consolidator_config' in full_config:
                        return full_config['consolidator_config'].get('time_sync', {})
                    elif 'terminal_config' in full_config:
                        return full_config['terminal_config'].get('time_sync', {})
                    else:
                        return full_config.get('time_sync', {})
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"⚠️ Erro ao carregar configuração NTP: {e}. Usando valores padrão.")
                return {}
        return {}
    
    def _get_server_list(self) -> List[str]:
        """Retorna lista de servidores NTP ordenada por prioridade"""
        servers = [self.primary_ntp_server] + self.backup_ntp_servers
        
        # Remove servidores que falharam recentemente se retry estiver desabilitado
        if not self.retry_failed_servers:
            servers = [s for s in servers if s not in self.failed_servers]
            
        return servers
    
    def start_sync_service(self):
        """Inicia o serviço de sincronização em background"""
        if not self.sync_enabled:
            print("🕐 Sincronização NTP desabilitada na configuração")
            return
            
        if self.sync_thread is None or not self.sync_thread.is_alive():
            self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
            self.sync_thread.start()
            print(f"🕐 Serviço de sincronização NTP iniciado")
            print(f"    Servidor principal: {self.primary_ntp_server}")
            print(f"    Servidores backup: {', '.join(self.backup_servers)}")
    
    def _sync_loop(self):
        """Loop de sincronização periódica (não-bloqueante)"""
        while self.sync_enabled:
            try:
                success = self.sync_time_with_fallback()
                if success:
                    self.is_ntp_available = True
                    print(f"✅ Sincronização NTP realizada com sucesso.")
                    print(f"    Servidor: {self.current_server}")
                    print(f"    Offset: {self.time_offset:.2f}s")
                else:
                    self.is_ntp_available = False
                    print("⚠️ Falha na sincronização NTP. Usando tempo local.")
                    
            except Exception as e:
                self.is_ntp_available = False
                print(f"❌ Erro na sincronização NTP: {e}. Sistema continuará com tempo local.")
            
            # Aguarda próxima tentativa (não-bloqueante)
            time.sleep(self.retry_interval)
    
    def sync_time_with_fallback(self) -> bool:
        """
        Tenta sincronizar com servidores NTP usando fallback
        Retorna True se bem-sucedido, False caso contrário
        """
        servers = self._get_server_list()
        
        for server in servers:
            for attempt in range(self.max_retry_attempts):
                try:
                    success = self._sync_with_server(server)
                    if success:
                        self.current_server = server
                        # Remove servidor da lista de falhas se sync foi bem-sucedido
                        self.failed_servers.discard(server)
                        return True
                        
                except Exception as e:
                    print(f"Tentativa {attempt + 1}/{self.max_retry_attempts} falhou para {server}: {e}")
                    if attempt == self.max_retry_attempts - 1:
                        # Adiciona servidor à lista de falhas
                        self.failed_servers.add(server)
                        print(f"❌ Servidor {server} marcado como falhando")
        
        return False
    
    def _sync_with_server(self, server: str) -> bool:
        """Sincroniza com um servidor NTP específico"""
        try:
            ntp_client = ntplib.NTPClient()
            response = ntp_client.request(server, timeout=self.timeout)
            
            ntp_time = datetime.fromtimestamp(response.tx_time)
            local_time = datetime.now()
            
            self.time_offset = (ntp_time - local_time).total_seconds()
            self.last_sync = local_time
            
            return True
            
        except (ntplib.NTPException, OSError, Exception) as e:
            raise e
    
    def get_synced_time(self) -> datetime:
        """
        Retorna tempo sincronizado se disponível, caso contrário tempo local
        NUNCA falha - sempre retorna um datetime válido
        """
        try:
            if self.last_sync and self.is_ntp_available:
                # Calcula se a sincronização ainda é válida (máximo 2 horas)
                sync_age = datetime.now() - self.last_sync
                if sync_age.total_seconds() < 7200:  # 2 horas
                    return datetime.now() + timedelta(seconds=self.time_offset)
            
            # Fallback para tempo local se NTP não disponível ou muito antigo
            return datetime.now()
            
        except Exception:
            # Em caso de qualquer erro, retorna tempo local
            return datetime.now()
    
    def get_time_status(self) -> dict:
        """Retorna status detalhado da sincronização temporal"""
        return {
            'ntp_available': self.is_ntp_available,
            'enabled': self.sync_enabled,
            'current_server': self.current_server,
            'primary_server': self.primary_ntp_server,
            'backup_servers': self.backup_ntp_servers,
            'failed_servers': list(self.failed_servers),
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'time_offset': self.time_offset,
            'current_time': self.get_synced_time().isoformat(),
            'sync_source': 'NTP' if self.is_ntp_available else 'LOCAL',
            'sync_interval': self.retry_interval,
            'timeout': self.timeout
        }
    
    def reload_config(self, config_file=None):
        """Recarrega configuração sem reiniciar o serviço"""
        old_enabled = self.sync_enabled
        self.config = self._load_config(config_file)
        
        # Atualiza configurações
        self.primary_ntp_server = self.config.get('primary_ntp_server', 'pool.ntp.org')
        self.backup_ntp_servers = self.config.get('backup_ntp_servers', [])
        self.retry_interval = self.config.get('sync_interval_seconds', 3600)
        self.timeout = self.config.get('timeout_seconds', 5)
        self.sync_enabled = self.config.get('enabled', True)
        
        # Limpa lista de servidores falhando
        self.failed_servers.clear()
        
        print(f"🔄 Configuração NTP recarregada")
        print(f"    Servidor principal: {self.primary_ntp_server}")
        print(f"    Servidores backup: {', '.join(self.backup_ntp_servers)}")
        
        # Reinicia serviço se necessário
        if not old_enabled and self.sync_enabled:
            self.start_sync_service()
        elif old_enabled and not self.sync_enabled:
            print("🛑 Sincronização NTP desabilitada")
    
    def stop_sync_service(self):
        """Para o serviço de sincronização"""
        self.sync_enabled = False
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=1)
        print("🛑 Serviço de sincronização NTP parado")
```

**11.4. Integração no Sistema**

#### **No Terminal (pobchecker_terminal.py):**
```python
# Inicialização não-bloqueante
time_sync = TimeSync('terminal_config.json')
time_sync.start_sync_service()  # Inicia em background

# Uso no sistema
def record_event():
    # Sempre funciona, mesmo sem NTP
    timestamp = time_sync.get_synced_time()
    # ... resto da lógica
```

#### **No Consolidador (pobchecker_server.py):**
```python
# Inicialização não-bloqueante
time_sync = TimeSync('consolidator_config.json')
time_sync.start_sync_service()

# Endpoint para verificar status temporal
@app.get("/api/v1/system/time-status")
async def get_time_status():
    return time_sync.get_time_status()

# Recarga dinâmica de configuração
@app.post("/api/v1/system/reload-ntp-config")
async def reload_ntp_config():
    time_sync.reload_config('consolidator_config.json')
    return {"status": "success", "message": "Configuração NTP recarregada"}
```

**11.5. Tratamento de Cenários de Falha**

#### **Cenário 1: Servidor NTP indisponível**
```python
# ✅ Sistema continua funcionando com tempo local
# ⚠️ Log de aviso é gerado
# 🔄 Tentativa automática de reconexão a cada hora
# 📊 Status é exposto via API para monitoramento
```

#### **Cenário 2: Timeout na conexão NTP**
```python
# ✅ Timeout de 5 segundos impede travamento
# ✅ Sistema volta ao tempo local imediatamente
# 📝 Erro logado para monitoramento
# 🔄 Tenta próximo servidor da lista
```

#### **Cenário 3: Rede temporariamente indisponível**
```python
# ✅ Sistema offline-first continua funcionando
# ✅ Sincronização é retomada quando rede voltar
# 📊 Status detalhado disponível via API
# 🔄 Retry automático com todos os servidores
```

#### **Cenário 4: Todos os servidores NTP falhando**
```python
# ✅ Sistema continua com tempo local
# ⚠️ Logs de tentativas com todos os servidores
# 🔄 Reset da lista de servidores falhando
# 📈 Métricas de falha expostas via API
```

---

### **12. Endpoints da API Consolidada**

**12.1. Endpoints para Interface Web**

```python
# Dashboard
GET /api/v1/dashboard/summary
GET /api/v1/dashboard/terminals
GET /api/v1/dashboard/events/active

# Eventos
GET /api/v1/events/active
GET /api/v1/events/history?page=1&size=50
GET /api/v1/events/{consolidated_id}/details
GET /api/v1/events/{consolidated_id}/report

# Relatórios
POST /api/v1/reports/generate
GET /api/v1/reports/export/{report_id}?format=pdf|excel

# Terminais
GET /api/v1/terminals/status
GET /api/v1/terminals/{terminal_id}/details

# Sistema
GET /api/v1/system/time-status
GET /api/v1/system/health
POST /api/v1/system/reload-ntp-config
```

**12.2. Endpoints para Integração Externa**

```python
# POB Consolidado
GET /api/v1/pob/current
GET /api/v1/pob/by-terminal
GET /api/v1/pob/history

# Dados para Sistemas Superiores
GET /api/v1/export/pob/current
GET /api/v1/export/events/active
GET /api/v1/export/reports/latest
```

**12.3. Estrutura de Resposta da API**

```json
{
  "dashboard_summary": {
    "pob_total": 142,
    "events_active": 2,
    "terminals_online": 4,
    "terminals_offline": 0,
    "last_update": "14/07/2025 14:45:30"
  },
  "terminals": [
    {
      "terminal_id": "terminal-plataforma-01",
      "location": "Sala de Controle",
      "status": "online",
      "last_sync": "14/07/2025 14:45:15",
      "pob_count": 42,
      "current_mode": "CEV",
      "active_event_id": 1,
      "time_sync_status": "NTP"
    }
  ],
  "time_status": {
    "ntp_available": true,
    "enabled": true,
    "current_server": "pool.ntp.org",
    "primary_server": "pool.ntp.org",
    "backup_servers": ["time.google.com", "time.cloudflare.com"],
    "failed_servers": [],
    "last_sync": "2025-07-14T14:45:00",
    "time_offset": 0.123,
    "current_time": "2025-07-14T14:45:30",
    "sync_source": "NTP",
    "sync_interval": 3600,
    "timeout": 5
  }
}
```

---

### **13. Plano de Implementação Atualizado**

**Fase 1: Backend do Consolidador (4-5 dias)**
- [ ] Servidor FastAPI com estrutura básica
- [ ] Banco PostgreSQL com schema completo
- [ ] Endpoints de sincronização (/sync)
- [ ] Lógica de correlação de eventos
- [ ] Serviço mDNS
- [ ] Sistema de sincronização temporal não-bloqueante configurável

**Fase 2: Interface Web (6-7 dias)**
- [ ] Dashboard responsivo com métricas principais
- [ ] Páginas de eventos e relatórios
- [ ] Monitoramento de terminais
- [ ] Sistema de exportação (PDF/Excel)
- [ ] WebSocket para atualização em tempo real
- [ ] Indicadores de status temporal e configuração NTP

**Fase 3: Modificações no Terminal (3-4 dias)**
- [ ] Adição da coluna Synced nas tabelas
- [ ] Módulo de descoberta de serviço (discovery.py)
- [ ] Serviço de sincronização (sync_service.py)
- [ ] Sistema de sincronização temporal não-bloqueante configurável
- [ ] Integração com aplicação principal

**Fase 4: Testes e Validação (5-6 dias)**
- [ ] Testes de correlação de eventos
- [ ] Testes de sincronização temporal com múltiplos servidores
- [ ] Testes de falha de NTP e fallback
- [ ] Testes de configuração dinâmica NTP
- [ ] Testes de responsividade da interface
- [ ] Testes de carga com múltiplos terminais
- [ ] Testes de falha de rede e recuperação

**Fase 5: Documentação e Deploy (2-3 dias)**
- [ ] Documentação de instalação
- [ ] Guia de configuração NTP para diferentes ambientes
- [ ] Manual do usuário
- [ ] Scripts de deploy

---

### **14. Considerações de Segurança**

**14.1. Autenticação e Autorização**
- **API Key para terminais:** Validação obrigatória em todos os endpoints
- **Tokens de sessão:** Para interface web (opcional, baseado em necessidade)
- **Validação de origem:** Verificar se os dados vêm de terminais autorizados

**14.2. Comunicação Segura**
- **HTTPS:** Obrigatório para interface web
- **Validação de certificados:** Para comunicação mDNS
- **Sanitização de dados:** Validação rigorosa de entrada nos endpoints
- **NTP Security:** Uso de servidores NTP confiáveis

**14.3. Auditoria e Monitoramento**
- **Logs detalhados:** Todas as operações de sincronização
- **Rastreamento de alterações:** Histórico de modificações
- **Monitoramento de acesso:** Tentativas de acesso não autorizadas
- **Alertas:** Notificações para falhas críticas
- **Monitoramento NTP:** Alertas para falhas prolongadas de sincronização

**14.4. Backup e Recuperação**
- **Backup automático:** Dados do PostgreSQL
- **Recuperação de falhas:** Procedimentos documentados
- **Teste de recuperação:** Validação periódica

---

### **15. Dependências e Bibliotecas**

**15.1. Consolidador (pobchecker_server.py)**
```python
# Framework web
fastapi==0.104.1
uvicorn==0.24.0
websockets==12.0

# Banco de dados
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.12.1

# Descoberta de serviço
zeroconf==0.131.0

# Sincronização temporal
ntplib==0.4.0

# Relatórios
reportlab==4.0.7
openpyxl==3.1.2

# Utilidades
python-multipart==0.0.6
python-dotenv==1.0.0
```

**15.2. Terminal (modificações)**
```python
# Já existentes no projeto
requests==2.31.0
sqlite3  # Biblioteca padrão

# Novas dependências
zeroconf==0.131.0
ntplib==0.4.0
```

---

### **16. Estrutura de Arquivos Final**

```
POBChecker/
├── pobchecker_terminal.py          # Terminal existente (modificado)
├── database.py                     # Banco SQLite existente (modificado)
├── sync_service.py                 # Novo - Serviço de sincronização
├── discovery.py                    # Novo - Descoberta de serviço
├── time_sync.py                    # Novo - Sincronização temporal configurável
├── terminal_config.json            # Novo - Configuração do terminal
├── pobchecker_server.py            # Novo - Servidor consolidador
├── consolidator_config.json        # Novo - Configuração do consolidador
├── models/                         # Novo - Modelos de dados
│   ├── __init__.py
│   ├── terminal_models.py
│   └── consolidator_models.py
├── api/                            # Novo - Endpoints da API
│   ├── __init__.py
│   ├── sync_endpoints.py
│   ├── dashboard_endpoints.py
│   └── report_endpoints.py
├── web/                            # Novo - Interface web
│   ├── static/
│   ├── templates/
│   └── assets/
├── utils/                          # Novo - Utilitários
│   ├── __init__.py
│   ├── event_correlator.py
│   └── report_generator.py
└── requirements_network.txt        # Novo - Dependências da rede
```

---

### **17. Métricas de Monitoramento**

**17.1. Métricas do Sistema**
- **Uptime do consolidador:** Tempo online
- **Terminais conectados:** Quantidade e status
- **Latência de sincronização:** Tempo médio de sync
- **Taxa de sucesso:** Percentual de syncs bem-sucedidos
- **Status NTP:** Disponibilidade da sincronização temporal por servidor
- **Deriva temporal:** Diferença de tempo entre terminais

**17.2. Métricas de Negócio**
- **POB total:** Pessoas a bordo consolidado
- **Eventos ativos:** Quantidade de eventos em andamento
- **Taxa de presença:** Percentual médio de presença em eventos
- **Tempo médio de evento:** Duração média dos eventos

**17.3. Alertas Configuráveis**
- **Terminal offline:** Mais de 2 minutos sem sync
- **Falha de correlação:** Eventos não correlacionados
- **Deriva temporal:** Diferença de tempo > 5 minutos
- **Erro de banco:** Falhas no PostgreSQL
- **Falha NTP:** Indisponibilidade prolongada do NTP
- **Servidor NTP falhando:** Falhas em servidor específico

---

### **18. Glossário de Termos**

- **Consolidador:** Servidor central que agrega dados de múltiplos terminais
- **Terminal:** Instância local do POBChecker em um dispositivo
- **Correlação:** Processo de associar eventos de terminais diferentes
- **Sincronização:** Envio de dados do terminal para o consolidador
- **mDNS:** Protocolo de descoberta de serviços na rede local
- **POB:** People On Board - Pessoas a bordo da plataforma
- **CEV:** Check Event - Modo de verificação de presença em eventos
- **CIO:** Check In/Out - Modo de controle de embarque/desembarque
- **NTP:** Network Time Protocol - Protocolo de sincronização de tempo
- **Não-bloqueante:** Operação que não impede o funcionamento do sistema em caso de falha
- **Fallback:** Mecanismo de backup que entra em ação quando o principal falha
- **Servidor NTP Primário:** Servidor principal para sincronização temporal
- **Servidores NTP Backup:** Servidores alternativos caso o primário falhe

---

**Documento atualizado em:** 14 de julho de 2025  
**Versão:** 1.2  
**Autor:** Sistema POBChecker  
**Status:** Especificação completa para implementação  
**Última atualização:** Configuração NTP flexível e não-bloqueante