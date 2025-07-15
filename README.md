# POBChecker - Sistema de Controle POB para Plataformas Petrolíferas

## 📋 Sobre o Projeto

O **POBChecker** é um sistema desenvolvido para controle de presença do POB (People On Board - Pessoas a Bordo) em plataformas de petróleo offshore. O sistema utiliza câmera para leitura de QR Codes contendo informações de CPF e nome dos funcionários, proporcionando um controle eficiente e automatizado da presença.

### 🎯 Objetivos Principais

- **Controle de Embarque/Desembarque**: Monitoramento em tempo real de pessoas a bordo da plataforma
- **Controle de Presença em Eventos**: Sistema de verificação de presença para reuniões, alarmes e procedimentos de segurança
- **Arquitetura Distribuída**: Terminais locais sincronizados com servidor central
- **Sincronização em Rede**: Dados consolidados automaticamente entre múltiplos terminais
- **Compatibilidade Raspberry Pi**: Otimizado para funcionar em dispositivos embarcados 
- **Sistema Linux**: Totalmente compatível com ambientes Linux para uso em plataformas offshore
- **Interface Intuitiva**: Interface gráfica moderna e de fácil utilização
- **Dois Modos de Operação**: CIO (Check In/Out) para embarque/desembarque e CEV (Check Event) para presença em eventos

## 🔧 Características Técnicas

### Compatibilidade de Sistemas
✅ **Linux** (Ubuntu, Debian, Raspberry Pi OS) - **Principal**  
✅ **Windows** (7, 8, 10, 11) - Para desenvolvimento e testes  
✅ **macOS** (10.14+) - Para desenvolvimento

### Hardware Recomendado
- **Raspberry Pi 4** (4GB RAM ou superior) - Para implantação final
- **Câmera USB** ou **Câmera do Raspberry Pi**
- **Tela de 7" ou superior** para interface touch
- **Armazenamento**: MicroSD 32GB (Classe 10)
- **Rede**: Ethernet ou WiFi para sincronização entre terminais

## 🚀 Instalação

### Pré-requisitos

- Python 3.7 ou superior
- Câmera conectada (USB ou integrada)
- Conexão com a internet (para instalação inicial)
- Rede local (para sincronização multi-terminal - opcional)

### Instalação no Raspberry Pi (Recomendado)

```bash
# Atualize o sistema
sudo apt update && sudo apt upgrade -y

# Instale dependências do sistema
sudo apt install python3-pip python3-venv pulseaudio-utils alsa-utils python3-tk -y

# Clone o projeto
git clone <repository-url> POBChecker
cd POBChecker

# Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale dependências Python básicas
pip install -r requirements.txt

# Para funcionalidades de rede (opcional)
pip install -r requirements_network.txt

# Execute o sistema principal (terminal local)
python pobchecker_terminal.py
```

### Instalação no Linux (Ubuntu/Debian)

```bash
# Instale dependências do sistema
sudo apt-get update
sudo apt-get install pulseaudio-utils alsa-utils python3-tk python3-pip python3-venv

# Configure o projeto
cd POBChecker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Para funcionalidades de rede (opcional)
pip install -r requirements_network.txt

# Execute
python pobchecker_terminal.py
```

### Instalação no Windows (Desenvolvimento)

```powershell
# Instale as dependências Python básicas
pip install -r requirements.txt

# Para funcionalidades de rede (opcional)
pip install -r requirements_network.txt

# Execute o aplicativo principal (terminal local)
python pobchecker_terminal.py
```

## 🌐 Arquitetura do Sistema

O POBChecker possui uma arquitetura distribuída que pode operar em dois modos:

### 1. **Modo Terminal Local** (Standalone)
- Operação independente sem necessidade de rede
- Dados armazenados localmente no SQLite
- Interface gráfica completa (`pobchecker_terminal.py`)

### 2. **Modo Servidor Central** (Consolidador)
- Servidor central que consolida dados de múltiplos terminais
- Interface web para monitoramento (`pobchecker_server.py`)
- Suporte a PostgreSQL para alta disponibilidade
- Sincronização automática com terminais

### 3. **Sincronização em Rede**
- Descoberta automática de serviços via mDNS
- Sincronização temporal com servidores NTP
- Dados consolidados automaticamente
- Fallback para operação offline

## 🚀 Modos de Execução

### Terminal Local (Recomendado para início)
```bash
python pobchecker_terminal.py
```

### Servidor Central (Para consolidação)
```bash
python run_server.py
# ou
python pobchecker_server.py
```

### Demo e Testes
```bash
python demo_system.py
```

## 📱 Funcionalidades

### Modos de Operação

O sistema opera em dois modos principais que podem ser alternados durante o uso:

#### 1. **Modo CIO (Check In/Out)** 
- **Finalidade**: Controle de embarque e desembarque da plataforma
- **Operação**: Leitura de QR Code automaticamente registra entrada ou saída
- **Indicador**: Interface azul com texto "MODO: CIO"
- **Lista**: Exibe apenas pessoas atualmente a bordo da plataforma

#### 2. **Modo CEV (Check Event)**
- **Finalidade**: Verificação de presença em eventos (reuniões, alarmes, exercícios)
- **Operação**: Criação de eventos para controle de presença específica
- **Indicador**: Interface verde com texto "MODO: CEV" 
- **Lista**: Duas colunas - "Não Checados" (vermelho) e "Checados" (verde)

### Módulos do Sistema

1. **Sistema Principal** (`pobchecker_terminal.py`)
   - Interface gráfica principal com câmera integrada
   - Leitura automática de QR Codes
   - Alternância entre modos CIO e CEV
   - Pesquisa manual por nome ou CPF
   - Controle por grupos (Grupo 1 e Grupo 2)
   - Sincronização automática com servidor (se disponível)

2. **Servidor Central** (`pobchecker_server.py`)
   - API REST para consolidação de dados
   - Interface web para monitoramento
   - Suporte a PostgreSQL e SQLite
   - Descoberta automática de terminais
   - Relatórios consolidados
   
3. **Serviços de Rede**
   - `sync_service.py` - Sincronização de dados entre terminais
   - `network_discovery.py` - Descoberta automática de serviços
   - `time_sync.py` - Sincronização temporal via NTP
   - `database_postgres.py` - Suporte a PostgreSQL

4. **Utilitários Helper** (pasta `helper/`)
   - `helper_generate_qrcodes.py` - Geração de QR Codes no formato CPF|Nome
   - `helper_clear_data.py` - Limpeza de dados do sistema
   - `helper_pob_generate.py` - Geração de dados de teste
   - `helper_auto_clear_data.py` - Limpeza automática de registros antigos
   
5. **Banco de Dados** (`database.py`)
   - SQLite para persistência local
   - Tabelas: POB, EVENTS, CHECK_EVENT, CHECK_IN_OUT
   - Backup automático e limpeza de dados antigos

### Formato dos QR Codes

Os QR Codes contêm informações no formato: **`CPF|NOME`**
- **Separador**: `|` (pipe) - escolhido para evitar ambiguidades
- **Exemplo**: `12345678901|João Silva Santos`
- **QR Especial**: `QR_EVENT_CONTROL_2024` - usado para alternar entre modos

## 🖥️ Como Usar

### 1. Inicialização
```bash
# Terminal local (modo standalone)
python pobchecker_terminal.py

# Servidor central (modo consolidador)
python run_server.py
```

### 2. Configuração de Rede (Opcional)
```bash
# Arquivo: terminal_config.json
{
  "terminal_id": "terminal-01",
  "location": "Plataforma A",
  "sync_interval_seconds": 30,
  "network": {
    "enabled": true,
    "api_key": "sua-chave-api"
  }
}
```

### 3. Geração de QR Codes
- Execute `python helper/helper_generate_qrcodes.py` para gerar QR Codes
- Os códigos são salvos na pasta `qrcodes_cpf/`
- Formato: CPF|Nome para melhor identificação

### 4. Controle de Presença
- **Modo CIO**: Controle de embarque/desembarque
- **Modo CEV**: Verificação de presença em eventos
- Use a câmera para ler QR Codes ou pesquise manualmente

### 5. Relatórios
- Visualização em tempo real do POB
- Estatísticas de presença por grupo
- Histórico de eventos
- Dashboard web (modo servidor)
- Relatórios consolidados multi-terminal

## 🔧 Manual Operacional

### Operações no Modo CIO (Check In/Out)

#### ✅ **Check In - Chegada na Plataforma**

**Processo Automático via QR Code:**
1. Posicione o QR Code da pessoa em frente à câmera
2. O sistema detecta automaticamente se a pessoa não está a bordo
3. **Som de sucesso** + **Mensagem verde**: "CHECK IN: [Nome] entrou na plataforma"
4. A pessoa aparece na lista "Pessoas no POB (Plataforma)"

**Processo Manual:**
1. Digite o nome ou CPF no campo "Pesquisa Manual"
2. Clique em "Check In/Out"
3. Se encontrada uma pessoa única, o check in é realizado automaticamente

#### ❌ **Check Out - Saída da Plataforma**

**Processo Automático via QR Code:**
1. Posicione o QR Code da pessoa em frente à câmera
2. O sistema detecta automaticamente que a pessoa está a bordo
3. **Som de alerta** + **Mensagem laranja**: "CHECK OUT: [Nome] saiu da plataforma"
4. A pessoa é removida da lista "Pessoas no POB"

**Processo Manual:**
1. Digite o nome ou CPF no campo "Pesquisa Manual" 
2. Clique em "Check In/Out"
3. Se a pessoa estiver a bordo, o check out é realizado automaticamente

### Operações no Modo CEV (Check Event)

#### 🎯 **Ativação do Modo CEV**

1. **Via QR Code Especial**: Aponte o QR Code `QR_EVENT_CONTROL` para a câmera
2. **Resultado**: 
   - Sistema muda para "MODO: CEV" (indicador verde)
   - Novo evento é criado automaticamente
   - Interface mostra duas colunas: "Não Checados" e "Checados"
   - **Mensagem**: "Modo CEV ativado. Evento #[ID] criado."

#### ✅ **Check de Presença em Evento**

**Para marcar presença:**
1. **Via QR Code**: Posicione o QR Code da pessoa em frente à câmera
2. **Via Manual**: Digite nome ou CPF e clique em "Marcar/Desmarcar"
3. **Resultado**:
   - **Som de sucesso** + **Mensagem verde**: "Presença registrada: [Nome]"
   - Pessoa move da coluna "Não Checados" para "Checados"
   - Fundo da pessoa fica verde claro

#### ↩️ **Estorno de Check de Presença**

**Para remover marca de presença:**
1. **Via QR Code**: Aponte novamente o QR Code da pessoa já checada
2. **Via Manual**: Digite nome ou CPF da pessoa checada e clique em "Marcar/Desmarcar"
3. **Resultado**:
   - **Som de alerta** + **Mensagem laranja**: "Estorno realizado: [Nome] removido da lista de presença"
   - Pessoa retorna da coluna "Checados" para "Não Checados"
   - Fundo da pessoa volta para vermelho claro

#### ❌ **Desativação do Modo CEV**

1. **Via QR Code Especial**: Aponte novamente o QR Code `QR_EVENT_CONTROL`
2. **Resultado**:
   - Evento atual é fechado automaticamente
   - Sistema retorna para "MODO: CIO" (indicador azul)
   - **Mensagem**: "Modo CEV desativado. Evento #[ID] fechado."

### Funcionalidades Auxiliares

#### 👥 **Seleção de Grupos**
- **Grupo 1 / Grupo 2**: Use o seletor no topo para alternar entre grupos
- Cada grupo mantém sua lista independente de pessoas
- Útil para separar equipes ou turnos diferentes

#### 🔍 **Pesquisa Manual**
- **Campo de busca**: Aceita nome parcial ou CPF completo
- **Resultado único**: Executa ação automaticamente (check in/out ou presença)
- **Múltiplos resultados**: Mostra lista de opções na barra de status
- **Não encontrado**: Em modo CIO, sugere usar QR Code para adicionar pessoa

#### 📊 **Estatísticas em Tempo Real**
- **Modo CIO**: "Total: X" (pessoas a bordo)
- **Modo CEV**: "Total: X", "Checados: Y", "Não Checados: Z"
- Atualização automática a cada operação

### Códigos de Cores e Sons

#### **Indicadores Visuais:**
- 🔵 **Azul**: Modo CIO ativo
- 🟢 **Verde**: Modo CEV ativo / Operação de sucesso / Pessoas checadas
- 🟠 **Laranja**: Check out / Estorno de presença
- 🔴 **Vermelho**: Erros / Pessoas não checadas

#### **Feedback Sonoro:**
- 🔊 **Som de Sucesso**: Check in realizado / Presença marcada
- 📢 **Som de Alerta**: Check out realizado / Estorno de presença  
- ❌ **Som de Erro**: QR Code inválido / Operação falhada

### Situações Especiais

#### **QR Code Não Reconhecido:**
- Formato inválido ou danificado
- **Ação**: Verificar formato CPF|Nome ou usar pesquisa manual

#### **Pessoa Não Cadastrada (Modo CEV):**
- QR Code válido mas pessoa não está no sistema
- **Ação**: Adicionar pessoa via modo CIO primeiro

#### **Erro de Câmera:**
- **Sintoma**: "Erro: Câmera não encontrada"
- **Ação**: Verificar conexão da câmera e reiniciar sistema

#### **Evento Não Ativo (Modo CEV):**
- Tentativa de marcar presença sem evento ativo
- **Ação**: Usar QR_EVENT_CONTROL_2024 para criar novo evento

## 🔧 Configuração para Raspberry Pi

### Hardware Recomendado
```
Raspberry Pi 4B (4GB RAM)
MicroSD 32GB Classe 10
Câmera Pi ou USB
Display 7" Touch (opcional)
Case protetor para ambiente industrial
Switch de rede (para múltiplos terminais)
```

### Configuração Otimizada
```bash
# Configure para boot automático
sudo systemctl enable ssh
sudo raspi-config
# - Enable Camera
# - Enable SSH
# - Boot Options > Desktop Autologin

# Instale o POBChecker
cd /home/pi
git clone <repo> POBChecker
cd POBChecker
chmod +x setup_pi.sh
./setup_pi.sh
```

## 🛠️ Desenvolvimento

### Estrutura do Código
```
pobchecker_terminal.py  # Script principal - Interface e lógica operacional
database.py            # Operações de banco de dados SQLite
camera_manager.py      # Gerenciamento de câmera e detecção QR
audio_manager.py       # Sistema de áudio multiplataforma
config.py             # Configurações do sistema
demo_system.py         # Sistema de demonstração e menu
helper/                # Pasta de utilitários
  helper_generate_qrcodes.py  # Geração de QR Codes
  helper_clear_data.py        # Limpeza de dados
  helper_pob_generate.py      # Geração de dados de teste
  helper_auto_clear_data.py   # Limpeza automática
tests/                 # Testes do sistema
  run_all_tests.py     # Execução de todos os testes
  simple_test.py       # Testes básicos
```

### Principais Funcionalidades Implementadas

#### **Sistema Principal (pobchecker_terminal.py)**
- Interface gráfica moderna com CustomTkinter
- Alternância automática entre modos CIO e CEV
- Leitura de QR Codes em tempo real
- Pesquisa manual com autocompletar
- Controle de grupos independentes
- Feedback visual e sonoro
- Limpeza automática de registros antigos
- Sincronização automática com servidor (quando disponível)

#### **Servidor Central (pobchecker_server.py)**
- API REST completa para consolidação
- Interface web para monitoramento
- Descoberta automática de terminais via mDNS
- Suporte a PostgreSQL e SQLite
- Relatórios consolidados
- Dashboard em tempo real

#### **Serviços de Rede**
- **Sincronização** (`sync_service.py`): Dados automáticos entre terminais
- **Descoberta** (`network_discovery.py`): Detecção automática de serviços
- **Temporal** (`time_sync.py`): Sincronização NTP não-bloqueante
- **PostgreSQL** (`database_postgres.py`): Suporte a banco enterprise

#### **Banco de Dados (database.py)**
- SQLite com 4 tabelas principais:
  - **POB**: Pessoas cadastradas (CPF, Nome, Grupo, Status)
  - **EVENTS**: Eventos de verificação de presença
  - **CHECK_EVENT**: Registros de presença em eventos
  - **CHECK_IN_OUT**: Histórico de embarque/desembarque
- Migração automática de esquema
- Backup automático de dados
- Limpeza de registros antigos (6+ meses)

#### **Gerenciador de Câmera (camera_manager.py)**
- Detecção automática de QR Codes
- Suporte múltiplas câmeras
- Otimização para Raspberry Pi
- Tratamento de erros de hardware

#### **Sistema de Áudio (audio_manager.py)**
- Sons diferenciados por tipo de operação
- Compatibilidade multiplataforma
- Fallback para sistemas sem áudio

### Testes e Validação
```bash
# Executar todos os testes
python tests/run_all_tests.py

# Teste básico do sistema
python tests/simple_test.py

# Teste do sistema principal
python pobchecker_terminal.py --test

# Menu de demonstração
python demo_system.py
```

### Utilitários de Manutenção
```bash
# Limpar dados antigos (6+ meses)
python helper/helper_auto_clear_data.py

# Limpar todos os dados de teste
python helper/helper_clear_data.py

# Popular com dados de exemplo
python helper/helper_pob_generate.py
```

### Contribuição

Para contribuir com o projeto:

1. **Fork** o repositório
2. **Crie** uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Teste** em pelo menos dois sistemas operacionais diferentes
4. **Documente** as mudanças no código
5. **Envie** um pull request com descrição detalhada

## 📄 Licença

Este projeto foi desenvolvido para uso no controle de POB em plataformas offshore.

## 🆘 Suporte

Para suporte técnico ou questões sobre o sistema:
- Consulte a documentação técnica interna
- Entre em contato com a equipe de TI da plataforma
- Verifique os logs do sistema em caso de erros

---

**POBChecker v2.0** - Sistema de Controle POB  
Desenvolvido por Ygor Pitombeira

## 🛠️ Desenvolvimento

### Estrutura do Código
```
pobchecker_terminal.py  # Script principal - Interface e lógica operacional
database.py            # Operações de banco de dados SQLite
camera_manager.py      # Gerenciamento de câmera e detecção QR
audio_manager.py       # Sistema de áudio multiplataforma
config.py             # Configurações do sistema
demo_system.py         # Sistema de demonstração e menu
helper/                # Pasta de utilitários
  helper_generate_qrcodes.py  # Geração de QR Codes
  helper_clear_data.py        # Limpeza de dados
  helper_pob_generate.py      # Geração de dados de teste
  helper_auto_clear_data.py   # Limpeza automática
tests/                 # Testes do sistema
  run_all_tests.py     # Execução de todos os testes
  simple_test.py       # Testes básicos
```

### Testes e Validação
```bash
# Executar todos os testes
python tests/run_all_tests.py

# Teste básico do sistema
python tests/simple_test.py

# Teste do sistema principal
python pobchecker_terminal.py --test

# Menu de demonstração
python demo_system.py
```

### Utilitários de Manutenção
```bash
# Limpar dados antigos (6+ meses)
python helper/helper_auto_clear_data.py

# Limpar todos os dados de teste
python helper/helper_clear_data.py

# Popular com dados de exemplo
python helper/helper_pob_generate.py
```

## 📄 Licença e Desenvolvimento

Este projeto foi desenvolvido para uso no controle de POB em plataformas offshore da **PETROBRAS**.

**POBChecker v2.0** - Sistema de Controle POB  
Desenvolvido por **Ygor Pitombeira**

### Compatibilidade Testada
- **Linux** (Ubuntu, Debian, Raspberry Pi OS) - **Ambiente Principal**
- **Windows** (7, 8, 10, 11) - Para desenvolvimento e testes  
- **macOS** (10.14+) - Para desenvolvimento

### Dependências de Sistema
- **Linux**: `pulseaudio-utils`, `alsa-utils`, `python3-tk`
- **Windows**: Incluído no Python padrão
- **macOS**: Incluído no sistema

## 🆘 Suporte e Solução de Problemas

### Problemas Comuns

#### **Câmera não funciona:**
- **Linux**: `sudo usermod -a -G video $USER` (relogar após comando)
- **Windows**: Verificar se não há outros programas usando a câmera
- **macOS**: Permitir acesso à câmera em Preferências > Segurança

#### **Erro de permissões (Linux):**
- **Som**: `sudo usermod -a -G audio $USER`
- **Câmera**: `sudo usermod -a -G video $USER`
- Reiniciar sessão após os comandos

#### **QR Codes não são detectados:**
- Verificar iluminação adequada
- Manter QR Code a 15-30cm da câmera
- Certificar-se que está no formato correto (CPF|Nome)

#### **Banco de dados corrompido:**
- Backup automático está em `pobchecker.sqlite3.backup`
- Remover arquivo principal para resetar sistema

### Contato para Suporte Técnico
- **Desenvolvimento**: Questões sobre código e funcionalidades
- **Operacional**: Dúvidas sobre uso em plataformas
- **TI Plataforma**: Problemas de infraestrutura local

---

**Última Atualização**: Julho 2025  
**Versão**: 2.0 - Sistema Reorganizado com Modos CIO/CEV e Funcionalidades de Rede  

## 🌐 Funcionalidades de Rede (Nova Versão)

### Arquitetura Distribuída
O POBChecker agora suporta operação em rede com:
- **Terminais Locais**: Interfaces operacionais distribuídas
- **Servidor Central**: Consolidação de dados de múltiplos terminais
- **Sincronização Automática**: Dados sincronizados em tempo real
- **Operação Offline**: Funciona mesmo sem conectividade

### Componentes de Rede

#### **Servidor Central** (`pobchecker_server.py`)
- API REST completa para consolidação
- Interface web para monitoramento
- Suporte a PostgreSQL para alta disponibilidade
- Descoberta automática de terminais via mDNS
- Dashboard em tempo real

#### **Sincronização** (`sync_service.py`)
- Sincronização automática de dados não enviados
- Retry automático em caso de falha de rede
- Configuração por arquivo JSON
- Operação em background não-bloqueante

#### **Descoberta de Rede** (`network_discovery.py`)
- Detecção automática de serviços via mDNS
- Fallback para IPs conhecidos
- Scan automático de rede local
- Configuração flexível de descoberta

#### **Sincronização Temporal** (`time_sync.py`)
- Sincronização com servidores NTP
- Múltiplos servidores de backup
- Funcionamento offline garantido
- Configuração por arquivo JSON

### Configuração de Rede

#### **Terminal Config** (`terminal_config.json`)
```json
{
  "terminal_id": "terminal-01",
  "location": "Plataforma A - Ponte",
  "sync_interval_seconds": 30,
  "network": {
    "enabled": true,
    "api_key": "sua-chave-segura-aqui",
    "discovery_timeout": 10
  },
  "time_sync": {
    "enabled": true,
    "primary_ntp_server": "pool.ntp.br",
    "sync_interval_seconds": 3600
  }
}
```

#### **Consolidator Config** (`consolidator_config.json`)
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "api_key": "chave-servidor-central"
  },
  "database": {
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "name": "pobchecker",
    "user": "postgres",
    "password": "senha"
  },
  "mdns": {
    "enabled": true,
    "service_name": "pobchecker-server"
  }
}
```

### Instalação com Funcionalidades de Rede

```bash
# Instalar dependências básicas
pip install -r requirements.txt

# Instalar dependências de rede
pip install -r requirements_network.txt

# Configurar PostgreSQL (opcional)
# Editar consolidator_config.json

# Iniciar servidor central
python run_server.py

# Iniciar terminal com sincronização
python pobchecker_terminal.py
```

### Modo de Operação

#### **Funcionamento Híbrido**
- **Sem Rede**: Operação completamente local
- **Com Rede**: Sincronização automática transparente
- **Falha de Rede**: Continua funcionando, ressincroniza quando retorna

#### **Descoberta Automática**
- Terminais detectam servidor automaticamente
- Configuração mínima necessária
- Fallback para IPs conhecidos

#### **Segurança**
- Autenticação via API Key
- Comunicação HTTP com headers de segurança
- Validação de dados em todas as operações

### Relatórios Consolidados

#### **Dashboard Web**
- Acesso via `http://servidor:8000/dashboard`
- Visualização em tempo real de todos os terminais
- Estatísticas consolidadas
- Histórico de eventos

#### **API REST**
- Endpoints para integração externa
- Dados em formato JSON
- Filtros por terminal, data, evento
- Documentação automática via FastAPI

### Benefícios da Versão em Rede

1. **Visibilidade Centralizada**: Todos os dados em um local
2. **Redundância**: Backup automático entre terminais
3. **Relatórios Unificados**: Dados de toda a plataforma
4. **Escalabilidade**: Suporta múltiplos terminais
5. **Confiabilidade**: Funciona mesmo offline
