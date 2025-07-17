# 📋 **DOCUMENTO DE ESPECIFICAÇÕES - SISTEMA POBChecker**

## **Data:** 16 de julho de 2025
## **Versão:** 1.1 - Definição de Requisitos com Preservação de Funcionalidades

---

## 🎯 **OBJETIVO GERAL**

Implementar sistema de sincronização de dados entre terminais e consolidador com controle de versão, eliminando conflitos através de filosofia unidirecional (Terminal → Consolidador) e indexação única por (Terminal, Tabela, ID).

---

## 🔒 **PREMISSAS FUNDAMENTAIS DE PRESERVAÇÃO**

### **1. ANÁLISE PRÉVIA OBRIGATÓRIA**
- **PRIMEIRA ETAPA:** Agent deve SEMPRE analisar e entender completamente o funcionamento atual do sistema antes de fazer qualquer alteração
- **MAPEAMENTO:** Identificar todas as funcionalidades existentes, arquivos, configurações e dependências
- **PRESERVAÇÃO:** Funcionalidades NÃO mencionadas neste documento devem ter suas funcionalidade e para isso devem ser testados após as alterações. Isso inclui e não se limita aos sistemas auxuliares como tests e utilitarys.
- **COMPATIBILIDADE:** Todas as alterações devem manter compatibilidade com o sistema existente

### **2. DESCOBERTA AUTOMÁTICA DE REDE - PRESERVAÇÃO OBRIGATÓRIA**
- **MANTER INTACTO:** Sistema de descoberta automática implementado em [`network_discovery.py`](network_discovery.py)
- **FUNCIONALIDADES PRESERVADAS:**
  - ✅ Descoberta mDNS (Zeroconf)
  - ✅ HTTP direto em IPs conhecidos
  - ✅ Network Scan automático
  - ✅ Fallbacks múltiplos
  - ✅ Configurações de timeout e portas
- **COMPATIBILIDADE:** Consolidador deve responder aos endpoints de descoberta existentes
- **CONFIGURAÇÃO:** Manter estrutura de configuração via JSON existente

### **3. SINCRONIZAÇÃO AUTOMÁTICA - PRESERVAÇÃO OBRIGATÓRIA**
- **MANTER INTACTO:** Sistema de sincronização implementado em [`sync_service.py`](sync_service.py)
- **FUNCIONALIDADES PRESERVADAS:**
  - ✅ Sincronização em background (thread daemon)
  - ✅ Intervalo configurável
  - ✅ Retry automático em falhas
  - ✅ Estatísticas de sincronização
  - ✅ Integração com time_sync
- **ENDPOINT:** Manter endpoint `/sync` com formato de dados compatível
- **CONFIGURAÇÃO:** Preservar [`terminal_config.json`](terminal_config.json) e estrutura

### **4. CONFIGURAÇÕES DE BANCO DE DADOS - PRESERVAÇÃO OBRIGATÓRIA**
- **TERMINAL:** Manter uso de SQLite conforme sistema atual
- **CONSOLIDADOR:** Adaptar para PostgreSQL mantendo compatibilidade
- **CONFIGURAÇÕES:** Preservar arquivos de configuração existentes:
  - [`terminal_config.json`](terminal_config.json)
  - [`consolidator_config.json`](consolidator_config.json)
  - Outros arquivos de configuração encontrados
- **CONEXÕES:** Manter lógica de conexão e reconnexão automática

### **5. ESTRUTURA DE ARQUIVOS - PRESERVAÇÃO OBRIGATÓRIA**
- **MANTER:** Estrutura de pastas e arquivos existentes
- **ARQUIVOS CRÍTICOS:** Não alterar arquivos não relacionados às mudanças especificadas
- **IMPORTS:** Manter imports e dependências existentes
- **PATHS:** Preservar caminhos relativos e absolutos

### **6. INTERFACE E ENDPOINTS - PRESERVAÇÃO OBRIGATÓRIA**
- **ENDPOINTS EXISTENTES:** Manter todos os endpoints da API não relacionados à sincronização
- **INTERFACE WEB:** Pode ser atualizado caso necessário
- **COMPATIBILIDADE:** Novos endpoints devem seguir padrão existente
- **AUTENTICAÇÃO:** Manter sistema de autenticação por API key

### **7. LOGGING E MONITORAMENTO - PRESERVAÇÃO OBRIGATÓRIA**
- **LOGS:** Manter sistema de logging existente
- **MONITORAMENTO:** Preservar funcionalidades de monitoramento
- **SAÚDE:** Manter endpoints de health check

---

## 📝 **ESPECIFICAÇÕES DEFINIDAS**

### **1. FILOSOFIA DE SINCRONIZAÇÃO**

#### **1.1 Princípio Fundamental**
- **Direção:** UNIDIRECIONAL (Terminal → Consolidador APENAS)
- **Independência:** Terminais operam de forma independente
- **Consolidação:** Consolidador replica e consolida dados recebidos
- **Sem Conflitos:** Indexação por (Terminal, Tabela, ID) elimina conflitos

#### **1.2 Controle de Versão**
- **Campo version:** Cada registro possui campo `version` que incrementa a cada modificação
- **Campo last_modified:** Timestamp da última modificação
- **Sincronização:** Baseada em versões (terminal envia apenas registros com versão superior)

### **2. ESTRUTURA DE DADOS**

#### **2.1 Renomeação de Campos**
- Não renomear campos existentes antes desse pacote de alterações.

#### **2.2 Tabelas a Serem Sincronizadas**
1. **EVENTS** - Eventos do sistema
2. **CHECK_EVENT** - Registros de presença em eventos
3. **CHECK_IN_OUT** - Registros de entrada/saída

#### **2.3 Tabela NÃO Sincronizada**
- **POB** - Não será sincronizada (evita conflitos de exclusão)
- **Cálculo:** POB será calculado em tempo real baseado em CHECK_IN_OUT

### **3. ALTERAÇÕES OBRIGATÓRIAS NO TERMINAL**

#### **3.1 Lógica de Estorno**
- **Problema Atual:** Função `remove_check_event()` EXCLUI registros fisicamente
- **Solução:** Substituir exclusão por campo STATUS
- **Status:** 'ACTIVE' (padrão) ou 'CANCELED' (estornado)
- **QR_EVENT_CONTROL:** Altera status para 'CANCELED' ao invés de excluir

#### **3.2 Estrutura das Tabelas do Terminal**
```
POB: CPF, Name, Onshore, version, last_modified (NÃO SINCRONIZADA)
EVENTS: ID, Open, Close, Closed, version, last_modified
CHECK_EVENT: ID, CPF, Name, Timestamp, Event, Status, version, last_modified
CHECK_IN_OUT: ID, CPF, Name, Type, Timestamp, version, last_modified
```

### **4. ESTRUTURA DO CONSOLIDADOR**

#### **4.1 Tabelas Consolidadas**
```
events_consolidated: terminal_id, original_id, Open, Close, Closed, version, sync_timestamp
check_event_consolidated: terminal_id, original_id, CPF, Name, Timestamp, Event, Status, version, sync_timestamp
check_in_out_consolidated: terminal_id, original_id, CPF, Name, Type, Timestamp, version, sync_timestamp
terminal_status: terminal_id, location, last_sync, status, sync_count
```

#### **4.2 Indexação Única**
- **Chave:** (terminal_id, original_id) para cada tabela consolidada
- **Evita Conflitos:** Cada registro é único por terminal de origem

### **5. LÓGICA DE SINCRONIZAÇÃO**

#### **5.1 Processo de Sincronização**
1. **Terminal:** Envia os dados periodicamente das tabelas que devem ser sincronizadas. Frequencia de envio deve ser configurável no arquivo de configuração do terminal. Padrão 20s.
2. **Envio:** Terminal envia dados para consolidador via API REST
3. **Consolidador:** Recebe e armazena dados indexados por (terminal, tabela, id)
4. **Verificação:** Consolidador só aceita registros com versão superior à armazenada

#### **5.2 Controle de Versão**
- **Incremento:** Versão incrementa automaticamente em modificações
- **Comparação:** Sistema compara versões antes de sincronizar
- **Atualização:** Apenas dados com versão superior são sincronizados

### **6. CÁLCULO DE POB**

#### **6.1 Método de Cálculo**
- **Fonte:** Baseado exclusivamente em registros CHECK_IN_OUT
- **Tempo Real:** Calculado dinamicamente quando necessário
- **Histórico:** Mantém histórico completo de movimentações

#### **6.2 Lógica de Cálculo**
- **Status:** Última movimentação de cada pessoa determina status
- **IN:** Pessoa está a bordo
- **OUT:** Pessoa está em terra
- **Consolidado:** Soma de todas as pessoas "IN" de todos os terminais

### **7. CORRELAÇÃO DE EVENTOS**

#### **7.1 Lógica de Correlação**
- **Automática:** Correlaciona eventos de diferentes terminais
- **Janela Temporal:** Eventos próximos no tempo são correlacionados
- **Tolerância:** Configurável (padrão: +-30 minutos)

#### **7.2 Resultado da Correlação**
- **Evento Consolidado:** Agrupa eventos relacionados
- **Estatísticas:** Total de participantes, por terminal, etc.
- **Status:** Considera registros ACTIVE.Registros CANCELED não devem ser contabilizados e nem exibidos.

### **8. ELIMINAÇÃO DE MIGRAÇÃO**

#### **8.1 Estratégia de Implementação**
- **Sem Migração:** Dados atuais podem ser deletados. inclusive a estrutura atual das tabelas.
- **Recriação:** Tabelas serão recriadas com nova estrutura
- **Ambiente:** Sistema está em desenvolvimento, sem dados críticos

#### **8.2 Estrutura Final**
- **Permanente:** Código final deve ter estrutura definitiva
- **Sem Legado:** Eliminar códigos temporários de migração
- **Limpeza:** Manter apenas lógica de produção, eliminando logicas e estruturas temporárias após a confirmação de funcionamento. Mantenha o teste de Sistema que estão na pasta tests.

### **9. TRATAMENTO DE CONFLITOS**

#### **9.1 Estratégia de Resolução**
- **Automática:** Última modificação ganha (timestamp)
- **Versão:** Versão mais alta tem prioridade
- **Indexação:** (Terminal, Tabela, ID) elimina conflitos estruturais

#### **9.2 Situações Sem Conflito**
- **Terminais Independentes:** Cada terminal gera IDs únicos
- **Tabela POB:** Não sincronizada, evita conflitos
- **Limpeza Automática:** Manter estratégia de limpeza automática de dados dos terminais= nas mesmas premissas existentes antes dessa etpa de alterações.

### **10. INTERFACE DO CONSOLIDADOR**

#### **10.1 Alterações Necessárias**
- **Status:** Considerar campo STATUS em eventos (ACTIVE/CANCELED)
- **Versionamento:** Exibir informações de versão e sincronização

#### **10.2 Funcionalidades Adicionais**
- **Dashboard:** Estatísticas de sincronização por terminal
- **Monitoramento:** Status de versões e última sincronização
- **Correlação:** Visualização de eventos correlacionados
- **Interface Visual:** Atualiazar Interface visual WEB para padrão moderno.

---

## 🚨 **PONTOS CRÍTICOS IDENTIFICADOS**

### **1. Mudanças Obrigatórias**
- Alteração de exclusão para STATUS em CHECK_EVENT
- Eliminação de sincronização da tabela POB

### **2. Validações Necessárias**
- Verificar se lógica de estorno por STATUS atende necessidades
- Confirmar se cálculo de POB por CHECK_IN_OUT é suficiente
- Validar estrutura das tabelas consolidadas

### **3. Testes Obrigatórios**
- Sistema de controle de versão
- Lógica de STATUS em eventos
- Cálculo de POB em tempo real
- Correlação de eventos automática

---

## 📊 **RESUMO EXECUTIVO**

**Sistema POBChecker será modificado para:**
- Sincronização unidirecional com controle de versão
- Eliminação de conflitos através de indexação única
- Estorno por STATUS ao invés de exclusão
- Cálculo de POB em tempo real
- Correlação automática de eventos
- Interface atualizada para nova estrutura

**Filosofia:** Terminais independentes → Consolidador replica → Correlação automática

**Resultado:** Sistema robusto, sem conflitos, com histórico completo e sincronização inteligente.

---

## 🔧 **METODOLOGIA DE IMPLEMENTAÇÃO**

### **ETAPA 1: ANÁLISE COMPLETA**
1. **Mapeamento:** Identificar todos os arquivos, configurações e dependências
2. **Funcionalidades:** Documentar todas as funcionalidades existentes
3. **Integrações:** Mapear integrações entre componentes
4. **Preservação:** Definir o que deve ser mantido intacto

### **ETAPA 2: PLANEJAMENTO**
1. **Compatibilidade:** Planejar mudanças mantendo compatibilidade
2. **Testes:** Definir testes para validar funcionalidades preservadas
3. **Rollback:** Preparar estratégia de rollback se necessário
4. **Validação:** Validar cada etapa antes de prosseguir

### **ETAPA 3: IMPLEMENTAÇÃO INCREMENTAL**
1. **Pequenas Mudanças:** Implementar alterações em pequenos incrementos
2. **Testes Constantes:** Testar funcionalidades preservadas após cada mudança
3. **Validação:** Validar que descoberta automática e sincronização continuam funcionando
4. **Documentação:** Documentar mudanças e impactos

---

**Este documento serve como base para reimplementação do sistema seguindo as especificações definidas e garantindo a preservação das funcionalidades críticas existentes.**