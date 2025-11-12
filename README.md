# 🎯 Pisk & Click v2.0 - Controle Facial Moderno

> **Sistema avançado de controle de mouse e clique através de movimentos faciais e piscadas, desenvolvido para acessibilidade e inclusão digital.**

![Pisk & Click Logo](assets/logo.png)

## ✨ Novidades da v2.0

- 🎨 **Interface Moderna**: Design completamente renovado com logo de alta qualidade
- 🧠 **Calibração Inteligente**: Sistema automático de ajuste de sensibilidade
- 👤 **Gerenciador de Perfis**: Configurações personalizadas para múltiplos usuários
- ⚙️ **Configurações Avançadas**: Interface intuitiva para ajuste fino
- 🖼️ **Logos Otimizados**: Ícones de alta qualidade em todas as resoluções
- 🔧 **Instalador Robusto**: Instalação automática com correções inteligentes

## 🚀 Instalação Rápida

### 📦 Instalador Automático (Recomendado)
1. Compile o instalador usando **Inno Setup**:
   - Abra `PiskAndClick_Installer_v2_Fixed.iss`
   - Pressione **F9** para compilar
2. Execute o instalador gerado como **administrador**
3. Siga as instruções na tela
4. **Pronto!** O programa estará no desktop com ícone personalizado

### 🛠️ Instalação Manual para Desenvolvedores
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/pisk-and-click.git
cd pisk-and-click

# Crie ambiente virtual (recomendado)
python -m venv .venv
.venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Execute a interface principal
python pisk_and_click.py
```

## 🎮 Como Usar

### 1️⃣ Primeira Execução
- Execute **Pisk & Click** pelo atalho do desktop
- A interface moderna será aberta com logo de alta qualidade
- Escolha uma das opções: Calibração, Configurações ou Controle Direto

### 2️⃣ Calibração (Recomendado)
- Clique em **"⚙️ Calibração"**
- Posicione-se em frente à câmera com boa iluminação
- Siga as instruções na tela:
  - Mantenha os olhos abertos por 3 segundos
  - Pisque várias vezes por 5 segundos
- O sistema calculará automaticamente o melhor threshold

### 3️⃣ Controle Facial
- Clique em **"🎯 Controle Facial"**
- **Movimento**: Mova a cabeça para controlar o cursor
- **Clique Esquerdo**: Pisque o olho esquerdo
- **Clique Direito**: Pisque o olho direito
- **Sair**: Pressione 'Q' ou mova o mouse para o canto superior esquerdo

## ⚙️ Configurações Avançadas

### 🎛️ Interface de Configurações
- **Sensibilidade do Mouse**: 0.5x a 3.0x (padrão: 1.3x)
- **Limiar de Piscada**: 0.1 a 0.5 (ajustado automaticamente na calibração)
- **Suavização**: 0.1 a 1.0 (padrão: 0.3)
- **Área de Controle**: Defina região ativa da tela
- **Proteção Piscada Dupla**: Evita cliques acidentais

### 👤 Sistema de Perfis
- **Criar Perfis**: Configurações específicas por usuário
- **Alternar Perfis**: Troca rápida entre configurações
- **Exportar/Importar**: Backup e compartilhamento de configurações

## 📋 Requisitos do Sistema

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **SO** | Windows 7 | Windows 10/11 |
| **Python** | 3.8+ | 3.11+ |
| **RAM** | 4GB | 8GB+ |
| **CPU** | Intel i3 | Intel i5+ |
| **Câmera** | 480p | 720p+ |
| **Iluminação** | Ambiente claro | Luz natural/LED |

## 🔧 Solução de Problemas

### ❌ Problemas Comuns

<details>
<summary><strong>Câmera não detectada</strong></summary>

- ✅ Verifique conexão da câmera
- ✅ Feche outros programas usando a câmera (Skype, Teams, etc.)
- ✅ Execute `python test_dependencies.py` para diagnóstico
- ✅ Reinicie o programa
</details>

<details>
<summary><strong>MediaPipe não funciona</strong></summary>

- ✅ Execute `python fix_mediapipe.py` para correção automática
- ✅ Reinstale com: `pip uninstall mediapipe && pip install mediapipe==0.10.7`
- ✅ Verifique se Visual C++ Redistributable está instalado
</details>

<details>
<summary><strong>Movimento irregular do mouse</strong></summary>

- ✅ Melhore a iluminação do ambiente
- ✅ Ajuste sensibilidade nas configurações (teclas +/-)
- ✅ Recalibre o sistema
- ✅ Verifique se há reflexos na tela
</details>

<details>
<summary><strong>Cliques não funcionam</strong></summary>

- ✅ Recalibre a detecção de piscadas
- ✅ Ajuste o limiar EAR nas configurações
- ✅ Pisque apenas um olho por vez
- ✅ Verifique proteção contra piscada dupla
</details>

## 🏗️ Arquitetura do Projeto

```
📁 pisk-and-click/
├── 🎯 pisk_and_click.py          # Interface principal moderna
├── 🧠 main.py                    # Motor de controle facial
├── ⚙️ config.py                  # Configurações do sistema
├── 🎨 modern_config_gui.py       # Interface de configurações
├── 📊 modern_calibration.py      # Sistema de calibração
├── 👤 modern_profile_manager.py  # Gerenciador de perfis
├── 🔧 user_profile_manager.py    # Backend de perfis
├── 🩺 test_dependencies.py       # Diagnóstico do sistema
├── 🔨 fix_mediapipe.py          # Correção automática
├── 📦 requirements.txt           # Dependências Python
├── assets/                      # Recursos visuais
│   ├── 🖼️ logo.png               # Logo principal (512x512)
│   └── 🔷 pisk_and_click.ico     # Ícone Windows
├── 📋 PiskAndClick_Installer_v2_Fixed.iss  # Instalador
└── 📖 README.md                  # Esta documentação
```

## 🔬 Tecnologias Utilizadas

### 🧠 Inteligência Artificial
- **MediaPipe** - Detecção facial e landmarks em tempo real
- **OpenCV** - Processamento de vídeo e visão computacional

### 🖥️ Interface e Sistema
- **Tkinter** - Interface gráfica nativa
- **PyAutoGUI** - Controle de mouse e teclado
- **Pillow (PIL)** - Processamento de imagens e logos

### 📊 Dados e Configuração
- **JSON** - Armazenamento de configurações e perfis
- **NumPy** - Cálculos matemáticos otimizados

## 🤝 Contribuindo

Contribuições são muito bem-vindas! 

### 🚀 Como Contribuir
1. **Fork** o projeto
2. **Clone** seu fork: `git clone https://github.com/seu-usuario/pisk-and-click.git`
3. **Crie** uma branch: `git checkout -b feature/nova-funcionalidade`
4. **Desenvolva** e teste suas mudanças
5. **Commit**: `git commit -m 'Adiciona nova funcionalidade'`
6. **Push**: `git push origin feature/nova-funcionalidade`
7. **Abra** um Pull Request

### 🐛 Reportar Bugs
- Use [GitHub Issues](https://github.com/seu-usuario/pisk-and-click/issues)
- Inclua informações do sistema e logs de erro
- Descreva passos para reproduzir o problema

## 📄 Licença

Este projeto está licenciado sob a **Licença MIT** - veja [LICENSE](LICENSE) para detalhes.

## 🏆 Reconhecimentos

- 🙏 **Google MediaPipe Team** - Biblioteca de detecção facial
- 🙏 **OpenCV Community** - Processamento de imagens
- 🙏 **Python Community** - Ecossistema incrível
- 🙏 **Contribuidores** - Todos que ajudaram a melhorar o projeto
- 🙏 **Testadores** - Feedback valioso da comunidade

## 📞 Suporte e Contato

- 🐛 **Issues**: [GitHub Issues](https://github.com/seu-usuario/pisk-and-click/issues)
- 📚 **Documentação**: [Wiki do Projeto](https://github.com/seu-usuario/pisk-and-click/wiki)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/seu-usuario/pisk-and-click/discussions)

---

<div align="center">

**🎯 Desenvolvido com ❤️ para tornar a tecnologia mais acessível a todos**

![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-green?style=for-the-badge&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-orange?style=for-the-badge)

**⭐ Se este projeto te ajudou, considere dar uma estrela!**

</div>