# 📋 Documentação Completa do Config GUI - Pisk&Click

## 🎯 Visão Geral

O arquivo `config_gui.py` é a interface gráfica principal para configuração do sistema Pisk&Click. Ele permite aos usuários ajustar todos os parâmetros do sistema de controle por movimento facial de forma visual e intuitiva, além de gerenciar perfis personalizados.

---

## 📦 Imports e Dependências

### Bibliotecas Principais
- **tkinter**: Interface gráfica nativa do Python
- **json**: Manipulação de arquivos de configuração
- **os**: Operações do sistema operacional
- **logging**: Sistema de logs para debug e monitoramento
- **typing**: Tipagem estática para melhor código
- **dataclasses**: Criação de classes de dados estruturadas
- **user_profile_manager**: Gerenciamento de perfis de usuário

### Sistema de Logging
```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```
**Função**: Registra eventos importantes da aplicação para debug e monitoramento.

---

## 🏗️ Estruturas de Dados Fundamentais

### ConfigField (Classe de Metadados)
```python
@dataclass
class ConfigField:
    name: str              # Nome interno do campo
    label: str             # Texto exibido na interface
    field_type: str        # Tipo: 'boolean', 'int', 'float', 'string'
    default_value: Any     # Valor padrão
    min_value: Optional[float]  # Valor mínimo (para números)
    max_value: Optional[float]  # Valor máximo (para números)
    tooltip: Optional[str]      # Texto de ajuda
    validation_func: Optional[callable]  # Função de validação
```

**Função**: Define a estrutura e comportamento de cada campo de configuração na interface.

---

## ⚙️ Sistema de Valores Padrão

### ConfigDefaults
Centraliza todos os valores padrão do sistema:

```python
DEFAULTS = {
    "NOSE_TIP_INDEX": 1,
    "LEFT_EYE_LANDMARKS_IDXS": [33, 160, 158, 133, 153, 144],
    "RIGHT_EYE_LANDMARKS_IDXS": [362, 385, 387, 263, 380, 373],
    "REFINE_LANDMARKS": True,
    "EAR_THRESHOLD": 0.2,
    "BLINK_CONSECUTIVE_FRAMES": 2,
    "SMOOTHING_FACTOR": 0.3,
    "CONTROL_AREA_X_MIN": 0.3,
    "CONTROL_AREA_X_MAX": 0.7,
    "CONTROL_AREA_Y_MIN": 0.3,
    "CONTROL_AREA_Y_MAX": 0.7,
    "INVERT_X_AXIS": False,
    "INVERT_Y_AXIS": False,
    "CLICK_DEBOUNCE_TIME": 0.5,
    "PROCESS_EVERY_N_FRAMES": 1,
}
```

**Função**: Garante que o sistema sempre tenha valores válidos, mesmo se o arquivo `config.py` estiver ausente ou corrompido.

---

## ✅ Sistema de Validação

### ConfigValidator
Contém funções para validar entradas do usuário:

#### `validate_float_range(value, min_val, max_val)`
- **Função**: Verifica se um número decimal está dentro do intervalo permitido
- **Uso**: Campos como EAR_THRESHOLD, SMOOTHING_FACTOR
- **Efeito**: Previne valores que podem quebrar o sistema

#### `validate_positive_int(value)`
- **Função**: Verifica se um número inteiro é positivo
- **Uso**: Campos como BLINK_CONSECUTIVE_FRAMES, PROCESS_EVERY_N_FRAMES
- **Efeito**: Evita valores que causariam erros de processamento

---

## 📂 Seções de Configuração

### 1. Detecção Facial

#### REFINE_LANDMARKS
- **Tipo**: Checkbox (Verdadeiro/Falso)
- **Função**: Ativa refinamento de landmarks faciais
- **Efeito quando ATIVADO**: 
  - ✅ Maior precisão na detecção
  - ❌ Maior uso de CPU
- **Efeito quando DESATIVADO**:
  - ✅ Menor uso de CPU
  - ❌ Menor precisão

#### EAR_THRESHOLD (0.15 - 0.30)
- **Tipo**: Campo numérico com incremento
- **Função**: Define sensibilidade para detecção de piscadas
- **Efeito quando MENOR (0.15)**:
  - ✅ Detecta piscadas mais sutis
  - ❌ Pode gerar cliques falsos
- **Efeito quando MAIOR (0.30)**:
  - ✅ Menos cliques acidentais
  - ❌ Precisa piscar mais forte

#### BLINK_CONSECUTIVE_FRAMES (1-10)
- **Tipo**: Campo numérico
- **Função**: Quantos frames consecutivos confirmam uma piscada
- **Efeito quando MENOR**:
  - ✅ Resposta mais rápida
  - ❌ Mais sensível a ruído
- **Efeito quando MAIOR**:
  - ✅ Mais estável
  - ❌ Resposta mais lenta

### 2. Controle do Mouse

#### SMOOTHING_FACTOR (0.0 - 1.0)
- **Tipo**: Campo numérico decimal
- **Função**: Controla suavização do movimento
- **Efeito quando 0.0**:
  - ✅ Movimento instantâneo
  - ❌ Pode ser instável
- **Efeito quando 1.0**:
  - ✅ Movimento muito suave
  - ❌ Resposta muito lenta

#### Área de Controle (X_MIN, X_MAX, Y_MIN, Y_MAX)
- **Tipo**: 4 campos numéricos (0.0 - 1.0)
- **Função**: Define região da tela controlada pelo rosto
- **Efeito quando ÁREA MENOR**:
  - ✅ Controle mais preciso
  - ❌ Alcance limitado
- **Efeito quando ÁREA MAIOR**:
  - ✅ Alcance total da tela
  - ❌ Menos precisão

#### INVERT_X_AXIS / INVERT_Y_AXIS
- **Tipo**: Checkboxes
- **Função**: Inverte direção do movimento
- **Efeito quando ATIVADO**:
  - Movimento do rosto para direita = cursor para esquerda
  - Movimento do rosto para cima = cursor para baixo

### 3. Temporização

#### CLICK_DEBOUNCE_TIME (0.1 - 5.0 segundos)
- **Tipo**: Campo numérico decimal
- **Função**: Tempo mínimo entre cliques
- **Efeito quando MENOR**:
  - ✅ Cliques mais rápidos
  - ❌ Pode gerar cliques duplos
- **Efeito quando MAIOR**:
  - ✅ Evita cliques acidentais
  - ❌ Cliques mais lentos

### 4. Performance

#### PROCESS_EVERY_N_FRAMES (1-10)
- **Tipo**: Campo numérico
- **Função**: Processa apenas 1 a cada N frames
- **Efeito quando 1**:
  - ✅ Máxima responsividade
  - ❌ Maior uso de CPU
- **Efeito quando 10**:
  - ✅ Menor uso de CPU
  - ❌ Resposta mais lenta

---

## 🎨 Sistema de Interface

### ToolTip (Ajuda Visual)
- **Função**: Exibe dicas quando o mouse passa sobre os campos
- **Comportamento**: 
  - Aparece após 1 segundo
  - Fundo amarelo claro
  - Texto explicativo
- **Efeito**: Ajuda usuários a entender cada configuração

### Layout Responsivo
- **Scrollable Frame**: Permite rolar quando há muitos campos
- **Seções Organizadas**: Agrupa configurações relacionadas
- **Botões de Ação**: Salvar, Carregar, Excluir perfis

---

## 👤 Sistema de Gerenciamento de Perfis

### Funcionalidades Principais

#### Dropdown de Perfis
- **Função**: Lista todos os perfis disponíveis
- **Comportamento**: Carrega automaticamente ao selecionar
- **Efeito**: Permite trocar rapidamente entre configurações

#### Botão "Novo Perfil"
- **Função**: Cria um novo perfil com nome personalizado
- **Processo**:
  1. Solicita nome do usuário
  2. Copia configurações atuais
  3. Salva como novo perfil
- **Efeito**: Permite personalização individual

#### Botão "Salvar Perfil"
- **Função**: Salva configurações atuais no perfil selecionado
- **Processo**:
  1. Coleta todos os valores da interface
  2. Valida os dados
  3. Salva no arquivo JSON
  4. Atualiza config.py
- **Efeito**: Persiste as configurações

#### Botão "Carregar Perfil"
- **Função**: Carrega configurações do perfil selecionado
- **Processo**:
  1. Lê arquivo JSON do perfil
  2. Aplica valores na interface
  3. Atualiza todas as variáveis
- **Efeito**: Restaura configurações salvas

#### Botão "Excluir Perfil"
- **Função**: Remove um perfil permanentemente
- **Processo**:
  1. Confirma com o usuário
  2. Remove arquivo JSON
  3. Volta para perfil default
- **Efeito**: Limpa perfis não utilizados

---

## 🔄 Integração com o Sistema

### Salvamento em config.py
A interface gera automaticamente o arquivo `config.py` com o formato:

```python
# --- Constantes e Configurações ---

# Índices dos landmarks faciais (Mediapipe Face Mesh)
NOSE_TIP_INDEX = 1
LEFT_EYE_LANDMARKS_IDXS = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_LANDMARKS_IDXS = [362, 385, 387, 263, 380, 373]

# Qualidade vs Desempenho Mediapipe
REFINE_LANDMARKS = True

# Limiares e Contadores para Detecção de Piscada
EAR_THRESHOLD = 0.25
BLINK_CONSECUTIVE_FRAMES = 2

# ... demais configurações
```

### Compatibilidade com Calibração
- **Integração Automática**: Valores calibrados são carregados automaticamente
- **Sincronização**: Mudanças na interface atualizam o sistema em tempo real
- **Preservação**: Configurações não relacionadas à calibração são mantidas

---

## 🎯 Fluxo de Uso Recomendado

### Para Novos Usuários
1. **Abrir Interface**: `python config_gui.py`
2. **Executar Calibração**: Use o sistema principal para calibrar
3. **Ajustar Configurações**: Modifique campos conforme necessário
4. **Salvar Perfil**: Crie um perfil personalizado
5. **Testar Sistema**: Verifique se o comportamento está adequado

### Para Usuários Experientes
1. **Carregar Perfil Existente**: Selecione perfil no dropdown
2. **Ajustes Finos**: Modifique apenas campos específicos
3. **Salvar Alterações**: Use "Salvar Perfil" para persistir
4. **Criar Variações**: Duplique perfis para diferentes situações

---

## ⚠️ Considerações Importantes

### Valores Críticos
- **EAR_THRESHOLD**: Valor mais importante, afeta diretamente a detecção
- **SMOOTHING_FACTOR**: Impacta significativamente a experiência de uso
- **Área de Controle**: Determina a usabilidade do sistema

### Troubleshooting
- **Sistema Muito Sensível**: Aumente EAR_THRESHOLD e CLICK_DEBOUNCE_TIME
- **Sistema Pouco Responsivo**: Diminua SMOOTHING_FACTOR e PROCESS_EVERY_N_FRAMES
- **Movimento Instável**: Aumente SMOOTHING_FACTOR e BLINK_CONSECUTIVE_FRAMES
- **Alto Uso de CPU**: Desative REFINE_LANDMARKS e aumente PROCESS_EVERY_N_FRAMES

### Backup e Segurança
- **Perfis Salvos**: Localizados na pasta `profiles/`
- **Backup Automático**: Sistema mantém perfil default sempre disponível
- **Recuperação**: Valores padrão sempre disponíveis em caso de erro

---

## 🚀 Extensibilidade

O sistema foi projetado para ser facilmente extensível:

### Adicionar Novos Campos
1. Definir em `ConfigSections.SECTIONS`
2. Adicionar valor padrão em `ConfigDefaults.DEFAULTS`
3. Criar validação se necessário
4. Campo aparece automaticamente na interface

### Personalizar Interface
- **Temas**: Modificar `ttk.Style().theme_use()`
- **Layout**: Ajustar seções e organização
- **Tooltips**: Adicionar mais dicas de ajuda

Esta documentação cobre todos os aspectos do `config_gui.py`, desde a estrutura técnica até o uso prático, fornecendo uma base completa para entender e utilizar o sistema de configuração do Pisk&Click.