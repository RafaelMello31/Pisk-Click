# Pisk & Click — Manual de Uso e Configuração

## Visão Geral
- Controle de mouse e cliques por movimentos faciais e piscadas.
- Requer webcam, Python 3.11+, e dependências listadas em `requirements.txt`.

## Início Rápido
- Execute `pisk_and_click.py` para abrir a interface principal.
- Use “Calibração Moderna” para ajustar detecção de piscadas.
- Use “Configurações Avançadas” para personalizar sensibilidade, debounce e proteções.
- Use “Gerenciador de Perfis” para salvar e carregar perfis de usuário.

## Calibração
- Abra `Calibração Moderna` (`modern_calibration.py`).
- Clique em `▶ INICIAR CALIBRAÇÃO`.
- Olhe para a câmera em iluminação uniforme; evite reflexos.
- Realize algumas piscadas normais; o sistema ajusta o EAR automaticamente.
- Use o painel esquerdo para parar ou fechar.

## Configuração
- Abra `Configurações Avançadas` (`modern_config_gui.py`).
- Principais parâmetros:
  - Limiar EAR: sensibilidade da piscada (menor = mais sensível).
  - Frames Consecutivos: quantos frames confirmam uma piscada.
  - Debounce de Clique: tempo mínimo entre cliques.
  - Proteção Piscada Dupla: evita cliques quando ambos os olhos piscam.

## Uso do Controle Facial
- Mova o nariz para controlar o cursor (pelo `main.py`).
- Pisque o olho esquerdo para clique esquerdo; direito para clique direito.
- Atalhos: `q` sai, `+`/`-` ajusta sensibilidade.

## Perfis
- Salve perfis no gerenciador para diferentes usuários.
- Perfis são armazenados em `profiles/`.

## Diagnóstico e Correções
- `fix_mediapipe.py`: corrige dependências do MediaPipe automaticamente.
- `mediapipe_installer.py`: instala MediaPipe com fallback e gera relatório.

## Problemas Comuns
- Sem detecção de rosto: verifique iluminação, posição da câmera e atualize drivers.
- Cliques excessivos: aumente `Debounce` e `Frames Consecutivos`.
- Baixa sensibilidade: reduza o `EAR` ou recalcibre.

## Estrutura do Projeto (organizada)
```
├─ assets/                # Logos e ícones
│  ├─ logo.png
│  ├─ pisk_and_click.ico
│  └─ pisk_and_click_icon.ico
├─ Docs/                  # Documentação
│  └─ Manual_PiskAndClick.md
├─ profiles/              # Perfis de usuário
├─ modern_calibration.py  # Calibração
├─ modern_config_gui.py   # Configurações
├─ modern_profile_manager.py
├─ pisk_and_click.py      # Interface principal
├─ main.py                # Motor de controle facial
├─ config.py              # Configurações globais
├─ user_profile_manager.py
├─ mediapipe_installer.py
├─ fix_mediapipe.py
├─ requirements.txt
└─ README.md
```

## Licença e Contribuição
- Proponha melhorias via Pull Requests.
- Registre bugs via Issues.