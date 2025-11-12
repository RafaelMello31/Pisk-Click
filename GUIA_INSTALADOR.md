# 📦 Guia do Instalador - Pisk & Click

## ✅ Instalador Criado com Sucesso!

**Arquivo**: `PiskAndClick_Setup.exe`  
**Tamanho**: ~26 MB  
**Status**: Pronto para distribuir

---

## 🚀 Como Usar o Instalador

### Para Você (Desenvolvedor)

1. **Distribuir o instalador**:
   - Compartilhe o arquivo `PiskAndClick_Setup.exe`
   - Pode ser via Google Drive, Dropbox, pen drive, etc.

2. **Recompilar** (se fizer alterações):
   ```batch
   compilar_instalador.bat
   ```

### Para Usuários Finais

1. **Execute** `PiskAndClick_Setup.exe`
2. **Clique** em "Avançar" no assistente
3. **Aguarde** a instalação (5-10 minutos)
4. **Pronto!** Use o atalho na área de trabalho

---

## 🎯 O Que o Instalador Faz

### Instalação Automática:

1. ✅ **Detecta Python** no sistema
2. ✅ **Instala Python 3.11** (se necessário)
3. ✅ **Cria ambiente virtual** isolado
4. ✅ **Instala dependências**:
   - NumPy 1.24.0
   - Protobuf 3.20.0
   - OpenCV 4.8.1.78
   - Pillow 10.0.0
   - PyAutoGUI 0.9.54
   - MediaPipe (instalação inteligente)
5. ✅ **Cria atalhos** na área de trabalho e menu iniciar
6. ✅ **Configura scripts** de execução

### Tempo de Instalação:
- **Com Python**: 3-5 minutos
- **Sem Python**: 5-10 minutos

---

## 📋 Requisitos para Usuários

- **Sistema**: Windows 7/8/10/11 (64-bit)
- **Espaço**: 1 GB livre
- **Webcam**: Qualquer modelo
- **Permissões**: Administrador

---

## 🔧 Estrutura Instalada

```
C:\Program Files\PiskAndClick\
├── venv\                          # Ambiente virtual Python
├── profiles\                      # Perfis de usuário
├── pisk_and_click.py             # Interface principal
├── main.py                        # Motor de controle
├── config.py                      # Configurações
├── modern_*.py                    # Módulos modernos
├── mediapipe_installer.py        # Instalador inteligente
├── assets\logo.png               # Logo
├── assets\pisk_and_click.ico     # Ícone
├── Iniciar_PiskAndClick.bat      # Script de execução
└── Iniciar_PiskAndClick.vbs      # Execução silenciosa
```

---

## 🎮 Como Usar Após Instalação

1. **Duplo clique** no atalho "Pisk & Click" na área de trabalho
2. **Escolha** uma opção:
   - 🎯 Controle Facial
   - ⚙️ Calibração
   - 🔧 Configurações
   - 👤 Perfis

---

## 🐛 Solução de Problemas

### Instalação Falha

**Problema**: Erro durante instalação  
**Solução**:
- Execute como Administrador
- Desative antivírus temporariamente
- Verifique espaço em disco

### Python Não Detectado

**Problema**: Instalador não encontra Python  
**Solução**:
- O instalador instala automaticamente
- Aguarde a instalação completa

### MediaPipe Não Funciona

**Problema**: Erro ao iniciar programa  
**Solução**:
- O programa reinstala automaticamente
- Aguarde alguns segundos

---

## 📦 Para Distribuir

### Checklist:

- [x] Instalador compilado
- [x] Testado em máquina limpa
- [x] Python incluído
- [x] Todas dependências incluídas
- [x] Atalhos funcionando

### Informações para Usuários:

```
Nome: Pisk & Click v1.0
Descrição: Controle Facial para Acessibilidade
Tamanho: 26 MB
Requisitos: Windows 7+ (64-bit)
Instalação: Automática
Tempo: 5-10 minutos
Licença: Gratuito
```

---

## ✨ Melhorias Implementadas

1. ✅ **Instalação 100% automática**
2. ✅ **Python embutido**
3. ✅ **Ambiente virtual isolado**
4. ✅ **Instalador inteligente do MediaPipe**
5. ✅ **Scripts de execução otimizados**
6. ✅ **Desinstalação limpa**
7. ✅ **Sem arquivos desnecessários**

---

## 🎓 Para Apresentação do TCC

### Demonstração:

1. **Mostre o instalador** sendo executado
2. **Explique** o processo automático
3. **Demonstre** o programa funcionando
4. **Destaque** a facilidade de uso

### Pontos Fortes:

- ✅ Instalação sem conhecimento técnico
- ✅ Python incluído (não precisa instalar)
- ✅ Ambiente isolado (não interfere no sistema)
- ✅ Desinstalação limpa

---

**Desenvolvido para TCC - Controle Facial para Acessibilidade**
