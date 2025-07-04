# POBChecker - Sistema de Controle POB para Plataformas Petrolíferas

## 📋 Sobre o Projeto

O **POBChecker** é um sistema desenvolvido para controle de presença do POB (People On Board - Pessoas a Bordo) em plataformas de petróleo offshore. O sistema utiliza câmera para leitura de QR Codes contendo informações de CPF e nome dos funcionários, proporcionando um controle eficiente e automatizado da presença.

### 🎯 Objetivo Principal

- **Controle de Presença**: Monitoramento em tempo real de pessoas a bordo
- **Compatibilidade Raspberry Pi**: Otimizado para funcionar em dispositivos embarcados 
- **Sistema Linux**: Totalmente compatível com ambientes Linux para uso em plataformas offshore
- **Interface Intuitiva**: Interface gráfica moderna e de fácil utilização

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

## 🚀 Instalação

### Pré-requisitos

- Python 3.7 ou superior
- Câmera conectada (USB ou integrada)
- Conexão com a internet (para instalação inicial)

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

# Instale dependências Python
pip install -r requirements.txt

# Execute o sistema principal
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

# Execute
python pobchecker_terminal.py
```

### Instalação no Windows (Desenvolvimento)

```powershell
# Instale as dependências Python
pip install -r requirements.txt

# Execute o aplicativo principal
python pobchecker_terminal.py
```

## 📱 Funcionalidades

### Módulos do Sistema

1. **Controle de Presença** (`pobchecker_terminal.py`)
   - Script principal do sistema
   - Leitura de QR Codes via câmera
   - Modo Check Alert - Verificação de presença
   - Modo Check In/Out - Adição/remoção do POB
   - Pesquisa manual por nome ou CPF
   
2. **Helpers** (pasta `helper/`)
   - `helper_generate_qrcodes.py` - Geração de QR Codes personalizados
   - `helper_clear_data.py` - Limpeza de dados
   - `helper_pob_generate.py` - Geração de dados de teste
   
3. **Banco de Dados** (`database.py`)
   - SQLite para persistência local
   - Tabelas: POB, EVENTS, CHECKS
   - Backup automático de dados

### Formato dos QR Codes

Os QR Codes contêm informações no formato: `CPF|NOME`
- Separador: `|` (pipe) - escolhido para evitar ambiguidades
- Exemplo: `12345678901|João Silva Santos`

## 🖥️ Como Usar

### 1. Inicialização
```bash
python pobchecker_terminal.py
```

### 2. Geração de QR Codes
- Execute `python helper/helper_generate_qrcodes.py` para gerar QR Codes
- Os códigos são salvos na pasta `qrcodes_cpf/`
- Formato: CPF|Nome para melhor identificação

### 3. Controle de Presença
- **Modo Check Alert**: Verificação de presença para alarmes
- **Modo Check In/Out**: Controle de embarque/desembarque
- Use a câmera para ler QR Codes ou pesquise manualmente

### 4. Relatórios
- Visualização em tempo real do POB
- Estatísticas de presença por grupo
- Histórico de eventos

## 🔧 Configuração para Raspberry Pi

### Hardware Recomendado
```
Raspberry Pi 4B (4GB RAM)
MicroSD 32GB Classe 10
Câmera Pi ou USB
Display 7" Touch (opcional)
Case protetor para ambiente industrial
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
pobchecker_terminal.py  # Script principal do sistema
database.py            # Operações de banco de dados
camera_manager.py      # Gerenciamento de câmera
audio_manager.py       # Sistema de áudio multiplataforma
demo_system.py         # Sistema de demonstração e menu
helper/                # Pasta de utilitários
  helper_generate_qrcodes.py  # Geração de QR Codes
  helper_clear_data.py        # Limpeza de dados
  helper_pob_generate.py      # Geração de dados de teste
```

### Testes
```bash
# Teste de compatibilidade
python test_compatibility.py

# Teste de validação CPF
python test_cpf_validation.py

# Utilitários auxiliares (movidos para pasta helper/)
python helper/helper_clear_data.py
```

## 📄 Licença

Este projeto foi desenvolvido para uso no controle de POB em plataformas offshore.

## 🆘 Suporte

Para suporte técnico ou questões sobre o sistema:
- Consulte a documentação técnica interna
- Entre em contato com a equipe de TI da plataforma
- Verifique os logs do sistema em caso de erros

---

**POBChecker v2.0** - Sistema de Controle POB  
Desenvolvido por Ygor Pitombeira - Segurança Offshore

### Sistema
- **Linux**: `pulseaudio-utils`, `alsa-utils`, `python3-tk`
- **Windows**: Incluído no Python padrão
- **macOS**: Incluído no sistema

## Como Usar

1. Execute `python main.py`
2. A câmera será ativada automaticamente
3. Aponte QR codes para a câmera para registrar presenças
4. Use a pesquisa manual para buscar por nome ou CPF
5. Alterne entre grupos usando o seletor no topo
6. Use o botão "Gerenciar Pessoal" para adicionar/editar pessoas

## Desenvolvimento

Para contribuir com o projeto:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Teste em pelo menos dois sistemas operacionais diferentes
4. Envie um pull request

## Licença

Este projeto é de uso interno e educacional.

## Suporte

Para problemas específicos do sistema operacional:

- **Windows**: Certifique-se de que o Python foi instalado corretamente
- **Linux**: Verifique permissões de câmera e áudio
- **macOS**: Permita acesso à câmera nas configurações de privacidade
