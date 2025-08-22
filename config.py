# --- Constantes e Configurações ---

# Índices dos landmarks faciais (Mediapipe Face Mesh)
NOSE_TIP_INDEX = 1
LEFT_EYE_LANDMARKS_IDXS = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_LANDMARKS_IDXS = [362, 385, 387, 263, 380, 373]

# Qualidade vs Desempenho Mediapipe
REFINE_LANDMARKS = True

# Limiares e Contadores para Detecção de Piscada
EAR_THRESHOLD = 0.2
BLINK_CONSECUTIVE_FRAMES = 2

# Suavização do Movimento do Mouse
SMOOTHING_FACTOR = 0.3

# Área de Controle do Rosto (Mapeamento Câmera -> Tela)
CONTROL_AREA_X_MIN = 0.3
CONTROL_AREA_X_MAX = 0.7
CONTROL_AREA_Y_MIN = 0.3
CONTROL_AREA_Y_MAX = 0.7

# Inversão de Eixos (Opcional)
INVERT_X_AXIS = False
INVERT_Y_AXIS = False

# Debounce para Cliques
CLICK_DEBOUNCE_TIME = 0.5

# Otimização de Desempenho (Opcional)
PROCESS_EVERY_N_FRAMES = 1

# --- Configurações para a funcionalidade Alt+Tab ---
ALT_TAB_TRIGGER_BOTH_EYES_BLINK = True
ALT_TAB_DEBOUNCE_TIME = 1.0

# --- Configurações para a funcionalidade de Inclinação da Cabeça ---
HEAD_TILT_THRESHOLD = 20.0
HEAD_TILT_DEBOUNCE_TIME = 0.5
HEAD_TILT_LEFT_TRIGGER_KEY = 'left'
HEAD_TILT_RIGHT_TRIGGER_KEY = 'right'
