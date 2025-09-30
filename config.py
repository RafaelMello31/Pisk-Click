# --- Constantes e Configurações ---

# Índices dos landmarks faciais (Mediapipe Face Mesh)
NOSE_TIP_INDEX = 1
LEFT_EYE_LANDMARKS_IDXS = [362, 380, 374, 263, 386, 385]
RIGHT_EYE_LANDMARKS_IDXS = [33, 159, 158, 133, 153, 145]

# Qualidade vs Desempenho Mediapipe
REFINE_LANDMARKS = True

# Limiares e Contadores para Detecção de Piscada
EAR_THRESHOLD = 0.22
BLINK_CONSECUTIVE_FRAMES = 5

# Suavização do Movimento do Mouse
SMOOTHING_FACTOR = 1.0

# Área de Controle do Rosto (Mapeamento Câmera -> Tela)
CONTROL_AREA_X_MIN = 0.2
CONTROL_AREA_X_MAX = 0.8
CONTROL_AREA_Y_MIN = 0.2
CONTROL_AREA_Y_MAX = 0.8

# Inversão de Eixos (Opcional)
INVERT_X_AXIS = False
INVERT_Y_AXIS = False

# Debounce para Cliques
CLICK_DEBOUNCE_TIME = 0.8

# Otimização de Desempenho (Opcional)
PROCESS_EVERY_N_FRAMES = 5
