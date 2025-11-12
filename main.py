import cv2
import mediapipe as mp
import pyautogui
import time
import math
import numpy as np
import threading
import logging

from config import (
    NOSE_TIP_INDEX,
    LEFT_EYE_LANDMARKS_IDXS,
    RIGHT_EYE_LANDMARKS_IDXS,
    REFINE_LANDMARKS,
    EAR_THRESHOLD,
    BLINK_CONSECUTIVE_FRAMES,
    SMOOTHING_FACTOR,
    CONTROL_AREA_X_MIN,
    CONTROL_AREA_X_MAX,
    CONTROL_AREA_Y_MIN,
    CONTROL_AREA_Y_MAX,
    INVERT_X_AXIS,
    INVERT_Y_AXIS,
    CLICK_DEBOUNCE_TIME,
    PROCESS_EVERY_N_FRAMES,
    MOUSE_ACCELERATION,
    MIN_MOVEMENT_THRESHOLD,
    DOUBLE_BLINK_PROTECTION,
    DOUBLE_BLINK_THRESHOLD,
    DOUBLE_BLINK_COOLDOWN,
    MOUSE_SENSITIVITY_MULTIPLIER,
    SENSITIVITY_ADJUSTMENT_STEP,
    MIN_SENSITIVITY,
    MAX_SENSITIVITY,
)

# Configuração global de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# --- Otimização: Threading para Captura de Vídeo ---
class ThreadedCamera:
    """Classe para capturar frames da câmera em uma thread separada."""

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src, cv2.CAP_DSHOW)  # Usar DirectShow no Windows
        
        # Configurar propriedades da câmera
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.stream.set(cv2.CAP_PROP_FPS, 30)
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduzir buffer para menor latência
        
        if not self.stream.isOpened():
            logger.error("Erro: Não foi possível abrir a câmera.")
            self.grabbed = False
            self.frame = None
            self.stopped = True
            return

        # Ler primeiro frame
        self.grabbed, self.frame = self.stream.read()
        self.stopped = False
        
        if not self.grabbed or self.frame is None:
            logger.error("Erro: Não foi possível capturar frame inicial.")
            self.stopped = True

    def start(self):
        if not self.stopped:
            threading.Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                self.grabbed, self.frame = self.stream.read()
                time.sleep(0.01)  # Pequeno delay para não sobrecarregar

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        if self.stream is not None:
            self.stream.release()


class FaceController:
    """Gerencia a detecção facial, rastreamento do nariz e detecção de piscadas."""

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=REFINE_LANDMARKS,
            min_detection_confidence=0.7,  # Aumentado para melhor detecção
            min_tracking_confidence=0.7,   # Aumentado para melhor tracking
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
        
        # Sistema de calibração automática
        self.ear_history = []
        self.calibration_frames = 0
        self.baseline_ear = 0.3
        self.is_calibrated = False
        
        # Filtros para suavização
        self.left_ear_history = []
        self.right_ear_history = []
        self.filter_size = 5

    def process_frame(self, image):
        """Processa um frame para detectar landmarks faciais."""
        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image_rgb)
        image.flags.writeable = True
        return results

    def get_nose_coords(self, face_landmarks, image_width, image_height):
        """Extrai as coordenadas normalizadas e em pixel da ponta do nariz."""
        nose_tip = face_landmarks[NOSE_TIP_INDEX]
        nose_coords_norm = (nose_tip.x, nose_tip.y)
        nose_pixel_coords = (
            int(nose_tip.x * image_width),
            int(nose_tip.y * image_height),
        )
        return nose_coords_norm, nose_pixel_coords

    def calculate_ear(self, eye_landmarks, image_shape, eye_side='left'):
        """Calcula o Eye Aspect Ratio (EAR) melhorado com calibração automática."""
        try:
            coords_points = np.array(
                [
                    (int(landmark.x * image_shape[1]), int(landmark.y * image_shape[0]))
                    for landmark in eye_landmarks
                ]
            )
            
            if len(coords_points) != 6:
                return self.baseline_ear
                
            p1, p2, p3, p4, p5, p6 = coords_points
            
            # Calcular distâncias com maior precisão
            vertical_dist1 = self._calculate_distance(p2, p6)
            vertical_dist2 = self._calculate_distance(p3, p5)
            horizontal_dist = self._calculate_distance(p1, p4)
            
            if horizontal_dist < 1.0:
                return self.baseline_ear
                
            # Calcular EAR básico
            ear = (vertical_dist1 + vertical_dist2) / (2.0 * horizontal_dist)
            
            # Validar range
            if ear < 0 or ear > 1.0 or not np.isfinite(ear):
                return self.baseline_ear
            
            # Sistema de filtro por olho
            if eye_side == 'left':
                self.left_ear_history.append(ear)
                if len(self.left_ear_history) > self.filter_size:
                    self.left_ear_history.pop(0)
                filtered_ear = np.median(self.left_ear_history)
            else:
                self.right_ear_history.append(ear)
                if len(self.right_ear_history) > self.filter_size:
                    self.right_ear_history.pop(0)
                filtered_ear = np.median(self.right_ear_history)
            
            # Calibração automática rápida (primeiros 30 frames)
            if self.calibration_frames < 30:
                self.ear_history.append(filtered_ear)
                self.calibration_frames += 1
                
                if self.calibration_frames == 30:
                    # Calcular baseline como média dos valores mais altos (olhos abertos)
                    sorted_ears = sorted(self.ear_history)
                    # Pegar os 70% maiores valores (olhos abertos)
                    top_70_percent = sorted_ears[int(len(sorted_ears) * 0.3):]
                    self.baseline_ear = np.mean(top_70_percent)
                    self.is_calibrated = True
                    logger.info(f"Calibração concluída! EAR baseline: {self.baseline_ear:.3f}")
                
            return filtered_ear
            
        except Exception as e:
            return self.baseline_ear

    def get_dynamic_threshold(self):
        """Retorna um threshold dinâmico baseado na calibração."""
        if self.is_calibrated:
            # Threshold como 70% do valor baseline
            return self.baseline_ear * 0.7
        return EAR_THRESHOLD

    def _calculate_distance(self, point1, point2):
        """Calcula a distância euclidiana entre dois pontos 2D."""
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


class MouseController:
    """Gerencia o movimento e cliques do mouse."""

    def __init__(self):
        # Configurações de performance do PyAutoGUI
        pyautogui.FAILSAFE = True  # Manter failsafe para segurança
        pyautogui.PAUSE = 0.01  # Pausa mínima para estabilidade
        
        self.screen_width, self.screen_height = pyautogui.size()
        logger.info(f"Resolução da tela detectada: {self.screen_width}x{self.screen_height}")
        self.prev_mouse_x, self.prev_mouse_y = pyautogui.position()
        self.last_left_click_time = 0
        self.last_right_click_time = 0

    def move_mouse(self, nose_coords_norm, image_width, image_height, sensitivity_multiplier=MOUSE_SENSITIVITY_MULTIPLIER):
        """Move o cursor do mouse baseado nas coordenadas do nariz - Sensibilidade Otimizada."""
        # Mapeamento direto e otimizado
        target_x = self._map_value(
            nose_coords_norm[0], CONTROL_AREA_X_MIN, CONTROL_AREA_X_MAX, 0, self.screen_width
        )
        target_y = self._map_value(
            nose_coords_norm[1], CONTROL_AREA_Y_MIN, CONTROL_AREA_Y_MAX, 0, self.screen_height
        )

        if INVERT_X_AXIS:
            target_x = self.screen_width - target_x
        if INVERT_Y_AXIS:
            target_y = self.screen_height - target_y

        # Aplicar multiplicador de sensibilidade
        center_x = self.screen_width / 2
        center_y = self.screen_height / 2
        
        # Calcular deslocamento do centro e aplicar multiplicador dinâmico
        offset_x = (target_x - center_x) * sensitivity_multiplier
        offset_y = (target_y - center_y) * sensitivity_multiplier
        
        # Recalcular posição com sensibilidade aumentada
        target_x = center_x + offset_x
        target_y = center_y + offset_y
        
        # Garantir que não saia dos limites da tela
        target_x = max(0, min(self.screen_width - 1, target_x))
        target_y = max(0, min(self.screen_height - 1, target_y))

        # Suavização adaptativa - mais responsiva para movimentos grandes
        diff_x = abs(target_x - self.prev_mouse_x)
        diff_y = abs(target_y - self.prev_mouse_y)
        
        # Se o movimento é grande, usar menos suavização para ser mais responsivo
        adaptive_smoothing = SMOOTHING_FACTOR
        if diff_x > 50 or diff_y > 50:  # Movimento grande
            adaptive_smoothing = min(0.8, SMOOTHING_FACTOR * 2)  # Mais responsivo
        elif diff_x < 10 and diff_y < 10:  # Movimento pequeno
            adaptive_smoothing = max(0.1, SMOOTHING_FACTOR * 0.5)  # Mais suave
        
        current_mouse_x = self.prev_mouse_x + (target_x - self.prev_mouse_x) * adaptive_smoothing
        current_mouse_y = self.prev_mouse_y + (target_y - self.prev_mouse_y) * adaptive_smoothing

        # Aplicar threshold de movimento mínimo para reduzir jitter
        movement_x = abs(current_mouse_x - self.prev_mouse_x)
        movement_y = abs(current_mouse_y - self.prev_mouse_y)
        
        if movement_x >= MIN_MOVEMENT_THRESHOLD or movement_y >= MIN_MOVEMENT_THRESHOLD:
            try:
                # Verificar se as coordenadas são válidas
                if (0 <= current_mouse_x < self.screen_width and 
                    0 <= current_mouse_y < self.screen_height):
                    # Usar moveTo para movimentos precisos
                    pyautogui.moveTo(int(current_mouse_x), int(current_mouse_y), duration=0.01)
                    self.prev_mouse_x, self.prev_mouse_y = current_mouse_x, current_mouse_y
            except pyautogui.FailSafeException:
                logger.warning("FailSafe ativado (mouse no canto superior esquerdo). Continue movendo para sair do canto.")
                return True  # Não encerrar, apenas avisar
            except Exception as e:
                logger.warning(f"Erro no movimento do mouse: {e}")
                return True  # Continuar executando
        return True

    def click(self, button_type, current_time):
        """Realiza um clique do mouse (esquerdo ou direito) com debounce."""
        if button_type == "left":
            if current_time - self.last_left_click_time > CLICK_DEBOUNCE_TIME:
                try:
                    pyautogui.click(button="left")
                    logger.info("Clique Esquerdo!")
                    self.last_left_click_time = current_time
                    return True
                except Exception as e:
                    logger.error(f"Erro ao clicar (esquerdo): {e}")
        elif button_type == "right":
            if current_time - self.last_right_click_time > CLICK_DEBOUNCE_TIME:
                try:
                    pyautogui.click(button="right")
                    logger.info("Clique Direito!")
                    self.last_right_click_time = current_time
                    return True
                except Exception as e:
                    logger.error(f"Erro ao clicar (direito): {e}")
        return False

    def _map_value(self, value, from_min, from_max, to_min, to_max):
        """Mapeia um valor de um intervalo para outro, com clamping."""
        try:
            value = max(min(value, from_max), from_min)
            from_span = from_max - from_min
            to_span = to_max - to_min
            
            # Verificar divisão por zero
            if from_span == 0:
                logger.warning(f"Divisão por zero evitada em _map_value: from_min={from_min}, from_max={from_max}")
                return to_min
                
            value_scaled = float(value - from_min) / float(from_span)
            return to_min + (value_scaled * to_span)
        except Exception as e:
            logger.error(f"Erro em _map_value: {e}")
            return to_min


class Application:
    """Classe principal da aplicação Pisk&Click."""

    def __init__(self):
        self.face_controller = FaceController()
        self.mouse_controller = MouseController()
        self.cap = None
        self.image_height, self.image_width = 480, 640
        self.use_dummy_image = False
        self.frame_counter = 0
        self.prev_frame_time = 0
        self.left_blink_counter = 0
        self.right_blink_counter = 0
        self.left_blink_detected_visual = False
        self.right_blink_detected_visual = False
        self.left_blink_timer = 0
        self.right_blink_timer = 0
        self.face_detected = False
        
        # Proteção contra piscada dupla
        self.double_blink_detected_time = 0
        self.last_double_blink_warning = 0
        
        # Sensibilidade dinâmica do mouse
        self.current_sensitivity = MOUSE_SENSITIVITY_MULTIPLIER

    def initialize_camera(self):
        """Inicializa a câmera e verifica sua disponibilidade."""
        try:
            logger.info("Abrindo a webcam...")
            self.cap = ThreadedCamera(0).start()
            time.sleep(2.0)  # Aguarda câmera inicializar completamente
            
            # Tentar ler frame várias vezes
            frame = None
            for attempt in range(5):
                frame = self.cap.read()
                if frame is not None and frame.size > 0:
                    break
                logger.info(f"Tentativa {attempt + 1}/5 de capturar frame...")
                time.sleep(0.5)
            
            if frame is None or frame.size == 0:
                logger.error("Erro: Não foi possível obter frame da webcam após 5 tentativas.")
                logger.error("Verifique se:")
                logger.error("  1. A webcam está conectada")
                logger.error("  2. Nenhum outro programa está usando a webcam")
                logger.error("  3. Os drivers da webcam estão instalados")
                self.use_dummy_image = True
            else:
                self.image_height, self.image_width, _ = frame.shape
                logger.info(f"Resolução da câmera detectada: {self.image_width}x{self.image_height}")
                logger.info("Webcam inicializada com sucesso!")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar câmera: {e}")
            self.use_dummy_image = True
        
        # Configurar janela OpenCV para receber eventos de teclado
        try:
            cv2.namedWindow("Pisk&Click - Controle Facial", cv2.WINDOW_AUTOSIZE)
            cv2.setWindowProperty("Pisk&Click - Controle Facial", cv2.WND_PROP_TOPMOST, 1)
            logger.info("Janela OpenCV configurada para receber eventos de teclado.")
        except Exception as e:
            logger.warning(f"Não foi possível configurar a janela OpenCV: {e}")

    def run(self):
        """Loop principal da aplicação."""
        logger.info("--- Pisk&Click Iniciado ---")
        logger.info("Pressione 'q' para sair.")
        logger.info("Pressione '+' para aumentar sensibilidade, '-' para diminuir.")
        logger.info("Movimente o nariz para controlar o cursor.")
        logger.info("Pisque o olho esquerdo para clique esquerdo, olho direito para clique direito.")
        logger.info(
            f"Ajustes Atuais: EAR Thresh={EAR_THRESHOLD}, Smooth={SMOOTHING_FACTOR}, Refine={REFINE_LANDMARKS}"
        )

        self.initialize_camera()

        try:
            while True:
                try:
                    current_time = time.time()
                    self.frame_counter += 1

                    if self.use_dummy_image:
                        image = np.zeros((self.image_height, self.image_width, 3), dtype=np.uint8)
                        results = None
                        time.sleep(0.1)
                    else:
                        image = self.cap.read()
                        if image is None:
                            logger.warning("Ignorando frame vazio da câmera.")
                            continue
                        image = cv2.flip(image, 1)
                except Exception as e:
                    logger.error(f"Erro no processamento de frame: {e}")
                    continue

                process_this_frame = self.frame_counter % PROCESS_EVERY_N_FRAMES == 0

                nose_coords_norm = None
                left_ear = 0.0
                right_ear = 0.0
                left_blink_detected_this_frame = False
                right_blink_detected_this_frame = False

                if process_this_frame:
                    results = self.face_controller.process_frame(image)

                    if results and results.multi_face_landmarks:
                        self.face_detected = True
                        face_landmarks = results.multi_face_landmarks[0].landmark

                        nose_coords_norm, nose_pixel_coords = self.face_controller.get_nose_coords(
                            face_landmarks, self.image_width, self.image_height
                        )
                        cv2.circle(image, nose_pixel_coords, 5, (0, 0, 255), -1)

                        left_eye_landmarks = [face_landmarks[i] for i in LEFT_EYE_LANDMARKS_IDXS]
                        right_eye_landmarks = [face_landmarks[i] for i in RIGHT_EYE_LANDMARKS_IDXS]
                        
                        left_ear = self.face_controller.calculate_ear(
                            left_eye_landmarks, (self.image_height, self.image_width), 'left'
                        )
                        right_ear = self.face_controller.calculate_ear(
                            right_eye_landmarks, (self.image_height, self.image_width), 'right'
                        )
                        
                        # Usar threshold dinâmico
                        dynamic_threshold = self.face_controller.get_dynamic_threshold()
                        
                        # Detectar se ambos os olhos estão piscando simultaneamente
                        both_eyes_closed = left_ear < dynamic_threshold and right_ear < dynamic_threshold
                        
                        # Verificar proteção contra piscada dupla
                        double_blink_cooldown_active = (current_time - self.double_blink_detected_time) < DOUBLE_BLINK_COOLDOWN
                        
                        if DOUBLE_BLINK_PROTECTION and both_eyes_closed:
                            # Detectar piscada dupla - ambos os olhos fechados simultaneamente
                            ear_difference = abs(left_ear - right_ear)
                            if ear_difference <= DOUBLE_BLINK_THRESHOLD:
                                self.double_blink_detected_time = current_time
                                # Reset contadores para evitar cliques
                                self.left_blink_counter = 0
                                self.right_blink_counter = 0
                                logger.info("Piscada dupla detectada - cliques bloqueados temporariamente")
                        
                        # Processar cliques apenas se não estiver em cooldown de piscada dupla
                        if not double_blink_cooldown_active:
                            # Olho esquerdo = clique esquerdo
                            if left_ear < dynamic_threshold and not (both_eyes_closed and DOUBLE_BLINK_PROTECTION):
                                self.left_blink_counter += 1
                            else:
                                if self.left_blink_counter >= BLINK_CONSECUTIVE_FRAMES:
                                    left_blink_detected_this_frame = self.mouse_controller.click("left", current_time)
                                self.left_blink_counter = 0

                            # Olho direito = clique direito
                            if right_ear < dynamic_threshold and not (both_eyes_closed and DOUBLE_BLINK_PROTECTION):
                                self.right_blink_counter += 1
                            else:
                                if self.right_blink_counter >= BLINK_CONSECUTIVE_FRAMES:
                                    right_blink_detected_this_frame = self.mouse_controller.click("right", current_time)
                                self.right_blink_counter = 0
                        else:
                            # Durante cooldown, resetar contadores
                            self.left_blink_counter = 0
                            self.right_blink_counter = 0

                        # Recursos de Alt+Tab e inclinação da cabeça removidos
                    else:
                        self.face_detected = False
                        self.left_blink_counter = 0
                        self.right_blink_counter = 0
                        logger.warning("Aviso: Rosto não detectado. O controle do mouse está pausado.")

                if self.face_detected and nose_coords_norm and not self.use_dummy_image:
                    if not self.mouse_controller.move_mouse(nose_coords_norm, self.image_width, self.image_height, self.current_sensitivity):
                        break
                elif not self.face_detected and not self.use_dummy_image:
                    cv2.putText(
                        image,
                        "Rosto nao detectado!",
                        (self.image_width // 2 - 150, self.image_height // 2),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2,
                        cv2.LINE_AA,
                    )

                # Usar valores padrão se não houver detecção
                if not process_this_frame or not self.face_detected:
                    left_ear = self.face_controller.baseline_ear
                    right_ear = self.face_controller.baseline_ear
                
                try:
                    self.update_display(
                        image,
                        left_ear,
                        right_ear,
                        left_blink_detected_this_frame,
                        right_blink_detected_this_frame,
                    )
                except Exception as e:
                    logger.error(f"Erro na atualização da interface: {e}")
                    # Continuar sem a interface visual se necessário

                # Controle de teclas
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == ord("Q"):
                    logger.info("Tecla 'Q' pressionada. Encerrando...")
                    break
                elif key == 27:  # ESC key
                    logger.info("Tecla 'ESC' pressionada. Encerrando...")
                    break
                elif key == ord("+") or key == ord("="):
                    # Aumentar sensibilidade
                    old_sensitivity = self.current_sensitivity
                    self.current_sensitivity = min(MAX_SENSITIVITY, self.current_sensitivity + SENSITIVITY_ADJUSTMENT_STEP)
                    if self.current_sensitivity != old_sensitivity:
                        logger.info(f"Sensibilidade aumentada para {self.current_sensitivity:.1f}")
                elif key == ord("-"):
                    # Diminuir sensibilidade
                    old_sensitivity = self.current_sensitivity
                    self.current_sensitivity = max(MIN_SENSITIVITY, self.current_sensitivity - SENSITIVITY_ADJUSTMENT_STEP)
                    if self.current_sensitivity != old_sensitivity:
                        logger.info(f"Sensibilidade diminuída para {self.current_sensitivity:.1f}")
                
                # Verificar se a janela foi fechada pelo usuário
                try:
                    if cv2.getWindowProperty("Pisk&Click - Controle Facial", cv2.WND_PROP_VISIBLE) < 1:
                        logger.info("Janela fechada pelo usuário. Encerrando...")
                        break
                except cv2.error:
                    # Janela foi fechada
                    logger.info("Janela OpenCV foi fechada. Encerrando...")
                    break

        except KeyboardInterrupt:
            logger.info("\nInterrupção pelo usuário (Ctrl+C).")
        except pyautogui.FailSafeException:
            logger.info("\nFailSafe ativado - mouse movido para o canto superior esquerdo da tela.")
            logger.info("Para evitar isso, mantenha o mouse longe do canto superior esquerdo.")
        except AttributeError as e:
            logger.error(f"\nErro de atributo: {e}")
            logger.info("Verifique se todas as configurações estão corretas.")
        except Exception as e:
            logger.error(f"\nErro inesperado: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            logger.info("Aplicação será encerrada devido ao erro.")
        finally:
            self.cleanup()

    def update_display(
        self,
        image,
        left_ear,
        right_ear,
        left_blink_detected_this_frame,
        right_blink_detected_this_frame,
    ):
        """Atualiza a exibição de informações na tela com interface reorganizada."""
        height, width = image.shape[:2]
        
        # Criar overlay com painéis mais escuros para melhor contraste
        overlay = image.copy()
        
        # Painel superior (título e FPS) - mais escuro
        cv2.rectangle(overlay, (0, 0), (width, 70), (0, 0, 0), -1)
        
        # Painel esquerdo (detecção dos olhos) - mais escuro
        cv2.rectangle(overlay, (0, 70), (300, height-80), (0, 0, 0), -1)
        
        # Painel direito (status de cliques) - mais escuro
        cv2.rectangle(overlay, (width-300, 70), (width, height-80), (0, 0, 0), -1)
        
        # Painel inferior (instruções) - mais escuro
        cv2.rectangle(overlay, (0, height-80), (width, height), (0, 0, 0), -1)
        
        # Aplicar overlay com mais opacidade para melhor contraste
        image = cv2.addWeighted(image, 0.4, overlay, 0.6, 0)
        
        # === SEÇÃO SUPERIOR: TÍTULO E FPS ===
        title_text = "PISK & CLICK"
        
        # Título centralizado com sombra para melhor visibilidade
        cv2.putText(image, title_text, (width//2 - 119, 36), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 0), 3)  # Sombra preta
        cv2.putText(image, title_text, (width//2 - 120, 35), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 255), 2)  # Texto principal
        
        # Subtítulo com sombra
        cv2.putText(image, "Controle Facial Ativo", (width//2 - 89, 56), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)  # Sombra
        cv2.putText(image, "Controle Facial Ativo", (width//2 - 90, 55), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)  # Texto branco
        
        # FPS no canto superior esquerdo com sombra
        new_frame_time = time.time()
        if self.prev_frame_time > 0:
            time_diff = new_frame_time - self.prev_frame_time
            if time_diff > 0:
                fps = 1 / time_diff
                fps_color = (0, 255, 0) if fps > 25 else (0, 255, 255) if fps > 15 else (0, 100, 255)
                cv2.putText(image, f"FPS: {int(fps)}", (11, 26),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)  # Sombra
                cv2.putText(image, f"FPS: {int(fps)}", (10, 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, fps_color, 2)  # Texto principal
        self.prev_frame_time = new_frame_time
        
        # === PAINEL ESQUERDO: DETECÇÃO DOS OLHOS ===
        left_panel_x = 10
        
        # Cabeçalho com sombra
        cv2.putText(image, "DETECCAO DOS OLHOS", (left_panel_x + 1, 96), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)  # Sombra
        cv2.putText(image, "DETECCAO DOS OLHOS", (left_panel_x, 95), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)  # Texto principal
        cv2.line(image, (left_panel_x, 100), (290, 100), (255, 255, 255), 2)  # Linha mais visível
        
        # Obter threshold dinâmico
        try:
            dynamic_threshold = self.face_controller.get_dynamic_threshold()
        except:
            dynamic_threshold = EAR_THRESHOLD
        
        # Status dos olhos com barras visuais
        left_ear_normalized = max(0, min(1, left_ear / 0.4))
        right_ear_normalized = max(0, min(1, right_ear / 0.4))
        
        # Olho esquerdo com sombra
        left_status = "ABERTO" if left_ear > dynamic_threshold else "FECHADO"
        left_color = (0, 255, 0) if left_ear > dynamic_threshold else (0, 150, 255)  # Azul mais claro
        
        # Texto com sombra
        cv2.putText(image, f"Olho Esq: {left_status}", (left_panel_x + 1, 126),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)  # Sombra
        cv2.putText(image, f"Olho Esq: {left_status}", (left_panel_x, 125),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, left_color, 2)  # Texto mais grosso
        
        cv2.putText(image, f"EAR: {left_ear:.3f}", (left_panel_x + 1, 146),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)  # Sombra
        cv2.putText(image, f"EAR: {left_ear:.3f}", (left_panel_x, 145),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)  # Texto branco
        
        # Barra de progresso do olho esquerdo
        bar_width = int(200 * left_ear_normalized)
        cv2.rectangle(image, (left_panel_x, 150), (left_panel_x + 200, 160), (50, 50, 50), -1)
        cv2.rectangle(image, (left_panel_x, 150), (left_panel_x + bar_width, 160), left_color, -1)
        
        # Olho direito com sombra
        right_status = "ABERTO" if right_ear > dynamic_threshold else "FECHADO"
        right_color = (0, 255, 0) if right_ear > dynamic_threshold else (0, 150, 255)  # Azul mais claro
        
        # Texto com sombra
        cv2.putText(image, f"Olho Dir: {right_status}", (left_panel_x + 1, 186),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)  # Sombra
        cv2.putText(image, f"Olho Dir: {right_status}", (left_panel_x, 185),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, right_color, 2)  # Texto mais grosso
        
        cv2.putText(image, f"EAR: {right_ear:.3f}", (left_panel_x + 1, 206),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)  # Sombra
        cv2.putText(image, f"EAR: {right_ear:.3f}", (left_panel_x, 205),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)  # Texto branco
        
        # Barra de progresso do olho direito
        bar_width = int(200 * right_ear_normalized)
        cv2.rectangle(image, (left_panel_x, 210), (left_panel_x + 200, 220), (50, 50, 50), -1)
        cv2.rectangle(image, (left_panel_x, 210), (left_panel_x + bar_width, 220), right_color, -1)
        
        # Status de calibração e limiar com sombra
        if self.face_controller.is_calibrated:
            cv2.putText(image, f"Limiar: {dynamic_threshold:.3f}", (left_panel_x + 1, 246),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)  # Sombra
            cv2.putText(image, f"Limiar: {dynamic_threshold:.3f}", (left_panel_x, 245),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 2)  # Verde mais grosso
            
            cv2.putText(image, "(Calibrado)", (left_panel_x + 121, 246),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)  # Sombra
            cv2.putText(image, "(Calibrado)", (left_panel_x + 120, 245),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        else:
            progress = (self.face_controller.calibration_frames / 30) * 100
            cv2.putText(image, f"Calibrando... {progress:.0f}%", (left_panel_x + 1, 246),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)  # Sombra
            cv2.putText(image, f"Calibrando... {progress:.0f}%", (left_panel_x, 245),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 2)  # Amarelo mais grosso
            # Barra de progresso da calibração
            bar_width = int(200 * (progress / 100))
            cv2.rectangle(image, (left_panel_x, 250), (left_panel_x + 200, 260), (50, 50, 50), -1)
            cv2.rectangle(image, (left_panel_x, 250), (left_panel_x + bar_width, 260), (255, 255, 0), -1)
        
        # === PAINEL DIREITO: STATUS DE CLIQUES ===
        right_panel_x = width - 290
        
        # Cabeçalho do painel com sombra
        cv2.putText(image, "STATUS DE CLIQUES", (right_panel_x + 1, 96), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)  # Sombra
        cv2.putText(image, "STATUS DE CLIQUES", (right_panel_x, 95), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)  # Texto principal
        cv2.line(image, (right_panel_x, 100), (width-10, 100), (255, 255, 255), 2)  # Linha mais visível
        
        # Clique esquerdo com sombra
        cv2.putText(image, "CLIQUE ESQUERDO", (right_panel_x + 1, 126),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)  # Sombra
        cv2.putText(image, "CLIQUE ESQUERDO", (right_panel_x, 125),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 220, 255), 2)  # Azul mais claro e grosso
        
        cv2.putText(image, f"Contador: {self.left_blink_counter}/{BLINK_CONSECUTIVE_FRAMES}", 
                    (right_panel_x + 1, 146), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)  # Sombra
        cv2.putText(image, f"Contador: {self.left_blink_counter}/{BLINK_CONSECUTIVE_FRAMES}", 
                    (right_panel_x, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)  # Branco
        
        # Barra de progresso do contador esquerdo
        progress = min(1.0, self.left_blink_counter / BLINK_CONSECUTIVE_FRAMES)
        bar_width = int(200 * progress)
        cv2.rectangle(image, (right_panel_x, 150), (right_panel_x + 200, 160), (50, 50, 50), -1)
        if bar_width > 0:
            cv2.rectangle(image, (right_panel_x, 150), (right_panel_x + bar_width, 160), (100, 200, 255), -1)
        
        # Clique direito com sombra
        cv2.putText(image, "CLIQUE DIREITO", (right_panel_x + 1, 186),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)  # Sombra
        cv2.putText(image, "CLIQUE DIREITO", (right_panel_x, 185),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 255, 150), 2)  # Verde mais claro e grosso
        
        cv2.putText(image, f"Contador: {self.right_blink_counter}/{BLINK_CONSECUTIVE_FRAMES}", 
                    (right_panel_x + 1, 206), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)  # Sombra
        cv2.putText(image, f"Contador: {self.right_blink_counter}/{BLINK_CONSECUTIVE_FRAMES}", 
                    (right_panel_x, 205), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)  # Branco
        
        # Barra de progresso do contador direito
        progress = min(1.0, self.right_blink_counter / BLINK_CONSECUTIVE_FRAMES)
        bar_width = int(200 * progress)
        cv2.rectangle(image, (right_panel_x, 210), (right_panel_x + 200, 220), (50, 50, 50), -1)
        if bar_width > 0:
            cv2.rectangle(image, (right_panel_x, 210), (right_panel_x + bar_width, 220), (100, 255, 100), -1)
        
        # Status da proteção contra piscada dupla
        current_time = time.time()
        double_blink_cooldown_active = (current_time - self.double_blink_detected_time) < DOUBLE_BLINK_COOLDOWN
        
        if DOUBLE_BLINK_PROTECTION:
            if double_blink_cooldown_active:
                remaining_time = DOUBLE_BLINK_COOLDOWN - (current_time - self.double_blink_detected_time)
                cv2.putText(image, "PROTECAO ATIVA", (right_panel_x, 245),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 100, 100), 1)
                cv2.putText(image, f"Cooldown: {remaining_time:.1f}s", (right_panel_x, 265),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 150, 150), 1)
                # Barra de cooldown
                cooldown_progress = 1.0 - (remaining_time / DOUBLE_BLINK_COOLDOWN)
                cooldown_bar_width = int(200 * cooldown_progress)
                cv2.rectangle(image, (right_panel_x, 270), (right_panel_x + 200, 280), (50, 50, 50), -1)
                cv2.rectangle(image, (right_panel_x, 270), (right_panel_x + cooldown_bar_width, 280), (255, 100, 100), -1)
            else:
                cv2.putText(image, "PROTECAO ATIVA", (right_panel_x, 245),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 255, 100), 1)
                cv2.putText(image, "Piscada dupla = bloqueio", (right_panel_x, 265),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 255, 150), 1)
        
        # Status de detecção com animação
        if left_blink_detected_this_frame:
            self.left_blink_detected_visual = True
            self.left_blink_timer = time.time()
        if right_blink_detected_this_frame:
            self.right_blink_detected_visual = True
            self.right_blink_timer = time.time()

        # Indicadores visuais de clique com fade out (no centro da tela)
        center_x = width // 2
        center_y = height // 2
        
        if hasattr(self, 'left_blink_timer') and current_time - self.left_blink_timer < 1.0:
            alpha = 1.0 - (current_time - self.left_blink_timer)
            intensity = int(255 * alpha)
            cv2.putText(image, "CLIQUE ESQUERDO!", (center_x - 100, center_y - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, intensity, 0), 2)
            cv2.circle(image, (center_x - 150, center_y - 25), int(20 * alpha), (0, intensity, 0), -1)
        
        if hasattr(self, 'right_blink_timer') and current_time - self.right_blink_timer < 1.0:
            alpha = 1.0 - (current_time - self.right_blink_timer)
            intensity = int(255 * alpha)
            cv2.putText(image, "CLIQUE DIREITO!", (center_x - 100, center_y + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, intensity), 2)
            cv2.circle(image, (center_x + 150, center_y + 15), int(20 * alpha), (0, 0, intensity), -1)

        # === PAINEL INFERIOR: INSTRUÇÕES ===
        instructions_y = height - 60
        
        # Linha 1: Controles com sombra
        cv2.putText(image, "CONTROLES:", (11, instructions_y + 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)  # Sombra
        cv2.putText(image, "CONTROLES:", (10, instructions_y + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)  # Texto mais grosso
        
        cv2.putText(image, "Q: Sair", (101, instructions_y + 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)  # Sombra
        cv2.putText(image, "Q: Sair", (100, instructions_y + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)  # Branco
        
        cv2.putText(image, "+/-: Sensibilidade", (171, instructions_y + 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)  # Sombra
        cv2.putText(image, "+/-: Sensibilidade", (170, instructions_y + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)  # Branco
        
        # Linha 2: Instruções de uso com sombra
        cv2.putText(image, "USO:", (11, instructions_y + 36),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)  # Sombra
        cv2.putText(image, "USO:", (10, instructions_y + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)  # Texto mais grosso
        
        cv2.putText(image, "Mova o nariz para controlar o cursor", (61, instructions_y + 36),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 2)  # Sombra
        cv2.putText(image, "Mova o nariz para controlar o cursor", (60, instructions_y + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)  # Branco
        
        # Linha 3: Sensibilidade atual com sombra
        cv2.putText(image, f"Sensibilidade: {self.current_sensitivity:.1f}x", (width - 199, instructions_y + 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)  # Sombra
        cv2.putText(image, f"Sensibilidade: {self.current_sensitivity:.1f}x", (width - 200, instructions_y + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 255), 2)  # Ciano mais grosso

        try:
            cv2.imshow("Pisk&Click - Controle Facial", image)
        except cv2.error as e:
            if "display" in str(e).lower():
                if not self.use_dummy_image and self.frame_counter % 60 == 0:
                    logger.warning(
                        "Aviso: Não foi possível exibir a janela (ambiente sem GUI?). Controle do mouse/clique ainda ativo."
                    )
            else:
                logger.error(f"Erro no cv2.imshow: {e}")

    def cleanup(self):
        """Libera os recursos utilizados pela aplicação."""
        logger.info("Encerrando aplicação...")
        if not self.use_dummy_image and self.cap:
            self.cap.stop()
            logger.info("Webcam liberada.")
        if "cv2" in locals() and hasattr(cv2, "destroyAllWindows"):
            try:
                cv2.destroyAllWindows()
            except cv2.error:
                pass
        if self.face_controller.face_mesh:
            self.face_controller.face_mesh.close()
            logger.info("Recursos do Mediapipe liberados.")
            logger.info("Aplicação Pisk&Click encerrada.")


if __name__ == "__main__":
    app = Application()
    app.run()
