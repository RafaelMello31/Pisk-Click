# Pisk&Click

Pisk&Click é um sistema de acessibilidade que transforma movimentos faciais em comandos do mouse. A aplicação captura o rosto do usuário com a webcam, rastreia a ponta do nariz para mover o cursor e interpreta piscadas independentes para executar cliques esquerdo e direito. Dessa forma, pessoas com mobilidade reduzida podem interagir com o computador utilizando apenas gestos faciais.

## Objetivos do projeto

- Permitir o controle básico do mouse (movimento, clique esquerdo e clique direito) a partir de expressões faciais.
- Fornecer parâmetros configuráveis para adaptar a sensibilidade do rastreamento a diferentes usuários e ambientes de iluminação.
- Disponibilizar um processo de calibração automática do limiar de piscada (EAR) para melhorar a confiabilidade da detecção.
- Centralizar perfis de configuração para que diferentes usuários possam alternar rapidamente entre ajustes personalizados.

## Requisitos

- Python 3.10 ou superior.
- Webcam funcional conectada ao computador.
- Ambiente gráfico disponível (necessário para `cv2.imshow`, `tkinter` e o controle do sistema operacional via `pyautogui`).
- Dependências listadas em [`requirements.txt`](requirements.txt):
  - `mediapipe==0.10.21`
  - `opencv-python==4.11.0.86`
  - `numpy==1.26.4`
  - `pyautogui==0.9.54`

### Instalação das dependências

1. (Opcional) Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```

2. Instale os requisitos do projeto:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Como executar

### 1. Controle facial do mouse (`main.py`)

1. Conecte a webcam e garanta que nenhum outro programa a esteja utilizando.
2. No diretório do projeto, execute:

   ```bash
   python main.py
   ```

3. Permaneça posicionado(a) em frente à câmera. Movimente o nariz para deslocar o cursor. Pisque apenas o olho esquerdo para clique esquerdo e apenas o direito para clique direito.
4. Pressione `q` na janela de visualização ou `Ctrl+C` no terminal para encerrar.

O script grava logs informativos no terminal e apresenta uma janela com o vídeo da câmera, indicadores de FPS, valores EAR e avisos quando o rosto não é detectado.

### 2. Ajustes avançados pela interface gráfica (`config_gui.py`)

1. Certifique-se de que o `tkinter` está disponível no seu Python (no Linux, instale o pacote `python3-tk` caso necessário).
2. Execute a interface:

   ```bash
   python config_gui.py
   ```

3. Utilize a interface para:
   - Ajustar parâmetros como suavização do cursor, limites da área de controle e limiar de piscada.
   - Inverter os eixos X/Y, definir intervalo mínimo entre cliques e controlar o processamento por frame.
   - Criar, carregar, salvar e excluir perfis de usuário armazenados na pasta `profiles/`.

Ao salvar, a GUI atualiza `config.py`, garantindo que os novos valores sejam aplicados nas próximas execuções do `main.py`.

## Processo de calibração

O módulo [`calibration_module.py`](calibration_module.py) calcula automaticamente um novo limiar de piscada (`EAR_THRESHOLD`) com base em dados coletados pela webcam.

1. Instale as dependências e conecte a webcam.
2. Execute o script abaixo para iniciar a calibração (um ambiente com janela gráfica é necessário):

   ```bash
   python - <<'PY'
   from main import FaceController
   from calibration_module import CalibrationModule

   module = CalibrationModule(FaceController())
   result = module.run_calibration()
   print(result)
   PY
   ```

3. Siga as instruções exibidas no terminal e na janela de vídeo:
   - Mantenha os olhos bem abertos quando solicitado (coleta inicial de referência).
   - Pisque normalmente durante a segunda fase para capturar o comportamento de piscadas.

4. Ao finalizar, o valor calculado é salvo automaticamente em `config.py` (e, se o gerenciamento de perfis estiver configurado, também no perfil atual). Execute novamente `main.py` para utilizar o novo limiar.

> Caso deseje integrar a calibração a outro fluxo, instancie `CalibrationModule` com o `FaceController` usado pela aplicação e chame `run_calibration()` conforme o exemplo acima.

## Resolução de problemas

| Situação | Possível causa | Solução sugerida |
|----------|----------------|------------------|
| `ImportError: No module named 'mediapipe'` ou dependências faltando | Pacotes não instalados | Reinstale os requisitos: `pip install -r requirements.txt`. Atualize o `pip` antes da instalação. |
| A janela da câmera não abre ou é encerrada com aviso de display | Execução em ambiente sem servidor gráfico (ex.: WSL sem X11) | Execute o projeto em um ambiente com suporte a GUI ou utilize um servidor X/Wayland compatível. |
| `tkinter` não encontrado ao abrir `config_gui.py` | Distribuições Linux podem não trazer `tkinter` por padrão | Instale o pacote do sistema (`sudo apt-get install python3-tk` no Debian/Ubuntu) ou utilize uma distribuição que já inclua o módulo. |
| Erro `pyautogui.FailSafeException` e a aplicação encerra | O cursor alcançou o canto superior esquerdo da tela e o mecanismo de segurança foi ativado | Volte o cursor ao centro antes de iniciar o controle. Evite mover rapidamente para os cantos. Só desative o FailSafe se souber o impacto (`pyautogui.FAILSAFE = False`). |
| Mensagem "Rosto não detectado" na janela do `main.py` | Iluminação inadequada, câmera fora de foco ou rosto fora da área delimitada | Ajuste a iluminação, centralize-se na câmera e considere ampliar a área de controle pelos parâmetros `CONTROL_AREA_*` via GUI. |
| Calibração encerra com "dados insuficientes" | Poucas amostras capturadas (piscar pouco ou interrupções) | Repita o processo, mantendo os olhos abertos e piscando normalmente quando solicitado. Certifique-se de não interromper antes do tempo indicado. |
| Cursor não se move apesar do vídeo funcionar | `SMOOTHING_FACTOR` muito baixo ou área de controle estreita | Ajuste os parâmetros correspondentes em `config_gui.py` e salve novamente as configurações. |

## Estrutura do repositório

- `main.py`: aplicação principal de controle do mouse por gestos faciais.
- `config.py`: arquivo de configurações utilizado pela aplicação.
- `config_gui.py`: interface gráfica para edição dos parâmetros e perfis.
- `calibration_module.py`: utilitário para calibração automática do limiar de piscada.
- `profiles/`: diretório onde são salvos os perfis de usuário.
- `requirements.txt`: lista de dependências Python do projeto.

---

Com o ambiente configurado e as calibrações realizadas, o Pisk&Click oferece um fluxo de controle do cursor responsivo que pode ser ajustado às necessidades de cada usuário.