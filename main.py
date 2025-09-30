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
)

# Configuração global de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# --- Otimização: Threading para Captura de Vídeo ---
class ThreadedCamera:
    """Classe para capturar frames da câmera em uma thread separada."""

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        if not self.stream.isOpened():
            logger.error("Erro: Não foi possível abrir a câmera.")
            self.grabbed = False
            return

        self.grabbed, self.frame = self.stream.read()
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                self.grabbed, self.frame = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True


class FaceController:
    """Gerencia a detecção facial, rastreamento do nariz e detecção de piscadas."""

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=REFINE_LANDMARKS,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

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

    def calculate_ear(self, eye_landmarks, image_shape):
        """Calcula o Eye Aspect Ratio (EAR) para um olho."""
        try:
            coords_points = np.array(
                [
                    (int(landmark.x * image_shape[1]), int(landmark.y * image_shape[0]))
                    for landmark in eye_landmarks
                ]
            )
            
            # Verificar se temos exatamente 6 pontos
            if len(coords_points) != 6:
                logger.warning(f"Número incorreto de landmarks para EAR: {len(coords_points)}")
                return 0.0
                
            p1, p2, p3, p4, p5, p6 = coords_points
            
            # Calcular distâncias verticais e horizontal
            vertical_dist1 = self._calculate_distance(p2, p6)
            vertical_dist2 = self._calculate_distance(p3, p5)
            horizontal_dist = self._calculate_distance(p1, p4)
            
            # Verificar divisão por zero com mais detalhes
            if horizontal_dist == 0 or horizontal_dist < 0.001:
                logger.warning(f"Distância horizontal inválida no cálculo EAR: {horizontal_dist}")
                return 0.0
                
            # Calcular EAR
            ear = (vertical_dist1 + vertical_dist2) / (2.0 * horizontal_dist)
            
            # Verificar se o valor está em um range razoável
            if ear < 0 or ear > 1 or not np.isfinite(ear):
                logger.warning(f"Valor EAR inválido: {ear}")
                return 0.0
                
            return ear
            
        except ZeroDivisionError as e:
            logger.error(f"Divisão por zero no cálculo EAR: {e}")
            return 0.0
        except Exception as e:
            logger.error(f"Erro ao calcular EAR: {e}")
            return 0.0

    def _calculate_distance(self, point1, point2):
        """Calcula a distância euclidiana entre dois pontos 2D."""
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


class MouseController:
    """Gerencia o movimento e cliques do mouse."""

    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        logger.info(f"Resolução da tela detectada: {self.screen_width}x{self.screen_height}")
        self.prev_mouse_x, self.prev_mouse_y = pyautogui.position()
        self.last_left_click_time = 0
        self.last_right_click_time = 0

    def move_mouse(self, nose_coords_norm, image_width, image_height):
        """Move o cursor do mouse baseado nas coordenadas do nariz."""
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

        current_mouse_x = self.prev_mouse_x + (target_x - self.prev_mouse_x) * SMOOTHING_FACTOR
        current_mouse_y = self.prev_mouse_y + (target_y - self.prev_mouse_y) * SMOOTHING_FACTOR

        try:
            pyautogui.moveTo(int(current_mouse_x), int(current_mouse_y))
            self.prev_mouse_x, self.prev_mouse_y = current_mouse_x, current_mouse_y
        except pyautogui.FailSafeException:
            logger.warning("FailSafe ativado (mouse movido para o canto). Encerrando...")
            return False
        except Exception:
            logger.warning("FailSafe ativado (mouse movido para o canto). Encerrando...")
            return False
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
        self.face_detected = False

    def initialize_camera(self):
        """Inicializa a câmera e verifica sua disponibilidade."""
        logger.info("Abrindo a webcam...")
        self.cap = ThreadedCamera(0).start()
        time.sleep(1.0)  # Aguarda a câmera inicializar
        frame = self.cap.read()
        if frame is None:
            logger.error("Erro: Não foi possível abrir a webcam. O controle do mouse não funcionará.")
            self.use_dummy_image = True
        else:
            self.image_height, self.image_width, _ = frame.shape
            logger.info(f"Resolução da câmera detectada: {self.image_width}x{self.image_height}")

    def run(self):
        """Loop principal da aplicação."""
        logger.info("--- Pisk&Click Iniciado ---")
        logger.info("Pressione 'q' para sair.")
        logger.info("Movimente o nariz para controlar o cursor.")
        logger.info("Pisque o olho esquerdo para clique esquerdo, olho direito para clique direito.")
        logger.info(
            f"Ajustes Atuais: EAR Thresh={EAR_THRESHOLD}, Smooth={SMOOTHING_FACTOR}, Refine={REFINE_LANDMARKS}"
        )

        self.initialize_camera()

        try:
            while True:
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
                            left_eye_landmarks, (self.image_height, self.image_width)
                        )
                        right_ear = self.face_controller.calculate_ear(
                            right_eye_landmarks, (self.image_height, self.image_width)
                        )

                        if left_ear < EAR_THRESHOLD:
                            self.left_blink_counter += 1
                        else:
                            if self.left_blink_counter >= BLINK_CONSECUTIVE_FRAMES:
                                left_blink_detected_this_frame = self.mouse_controller.click("left", current_time)
                            self.left_blink_counter = 0

                        if right_ear < EAR_THRESHOLD:
                            self.right_blink_counter += 1
                        else:
                            if self.right_blink_counter >= BLINK_CONSECUTIVE_FRAMES:
                                right_blink_detected_this_frame = self.mouse_controller.click("right", current_time)
                            self.right_blink_counter = 0

                        # Recursos de Alt+Tab e inclinação da cabeça removidos
                    else:
                        self.face_detected = False
                        self.left_blink_counter = 0
                        self.right_blink_counter = 0
                        logger.warning("Aviso: Rosto não detectado. O controle do mouse está pausado.")

                if self.face_detected and nose_coords_norm and not self.use_dummy_image:
                    if not self.mouse_controller.move_mouse(nose_coords_norm, self.image_width, self.image_height):
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

                self.update_display(
                    image,
                    left_ear,
                    right_ear,
                    left_blink_detected_this_frame,
                    right_blink_detected_this_frame,
                )

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logger.info("Tecla 'q' pressionada. Encerrando...")
                    break

        except KeyboardInterrupt:
            logger.info("\nInterrupção pelo usuário (Ctrl+C).")
        except pyautogui.FailSafeException:
            logger.info("\nFailSafe ativado - mouse movido para o canto da tela.")
        except Exception as e:
            logger.error(f"\nErro inesperado: {e}")
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
        """Atualiza a exibição de informações na tela com interface melhorada."""
        height, width = image.shape[:2]
        
        # Painel de informações superior
        overlay = image.copy()
        cv2.rectangle(overlay, (0, 0), (width, 150), (0, 0, 0), -1)
        image = cv2.addWeighted(image, 0.7, overlay, 0.3, 0)
        
        # FPS
        new_frame_time = time.time()
        if self.prev_frame_time > 0:
            time_diff = new_frame_time - self.prev_frame_time
            if time_diff > 0:  # Evitar divisão por zero
                fps = 1 / time_diff
                cv2.putText(image, f"FPS: {int(fps)}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(image, "FPS: --", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        self.prev_frame_time = new_frame_time

        # Título
        cv2.putText(image, "PISCK & CLICK - CONTROLE ATIVO", (width//2 - 200, 30),
                    cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
        
        # Informações EAR com cores dinâmicas
        left_ear_color = (0, 255, 0) if left_ear > EAR_THRESHOLD else (0, 0, 255)
        right_ear_color = (0, 255, 0) if right_ear > EAR_THRESHOLD else (0, 0, 255)
        
        cv2.putText(image, f"EAR Esquerdo: {left_ear:.3f}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, left_ear_color, 2)
        cv2.putText(image, f"EAR Direito: {right_ear:.3f}", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, right_ear_color, 2)
        
        # Limiar EAR atual
        cv2.putText(image, f"Limiar: {EAR_THRESHOLD:.3f}", (10, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Contadores de piscada
        cv2.putText(image, f"Contador Esq: {self.left_blink_counter}/{BLINK_CONSECUTIVE_FRAMES}", 
                    (width//2 - 100, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(image, f"Contador Dir: {self.right_blink_counter}/{BLINK_CONSECUTIVE_FRAMES}", 
                    (width//2 - 100, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Status de detecção
        if left_blink_detected_this_frame:
            self.left_blink_detected_visual = True
        if right_blink_detected_this_frame:
            self.right_blink_detected_visual = True

        # Indicadores visuais de clique
        if self.left_blink_detected_visual:
            cv2.putText(image, "CLIQUE ESQUERDO!", (width - 250, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.circle(image, (width - 50, 70), 20, (0, 255, 0), -1)
            
        if self.right_blink_detected_visual:
            cv2.putText(image, "CLIQUE DIREITO!", (width - 250, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.circle(image, (width - 50, 100), 20, (0, 0, 255), -1)

        if left_ear >= EAR_THRESHOLD:
            self.left_blink_detected_visual = False
        if right_ear >= EAR_THRESHOLD:
            self.right_blink_detected_visual = False

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
