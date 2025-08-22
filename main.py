import cv2
import mediapipe as mp
import pyautogui
import time
import math
import numpy as np
import threading
from queue import Queue

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
    ALT_TAB_TRIGGER_BOTH_EYES_BLINK,
    ALT_TAB_DEBOUNCE_TIME,
    HEAD_TILT_THRESHOLD,
    HEAD_TILT_DEBOUNCE_TIME,
    HEAD_TILT_LEFT_TRIGGER_KEY,
    HEAD_TILT_RIGHT_TRIGGER_KEY
)

# --- Otimização: Threading para Captura de Vídeo ---
class ThreadedCamera:
    """Classe para capturar frames da câmera em uma thread separada."""
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        if not self.stream.isOpened():
            print("Erro: Não foi possível abrir a câmera.")
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
            min_tracking_confidence=0.5
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
        nose_pixel_coords = (int(nose_tip.x * image_width), int(nose_tip.y * image_height))
        return nose_coords_norm, nose_pixel_coords

    def calculate_ear(self, eye_landmarks, image_shape):
        """Calcula o Eye Aspect Ratio (EAR) para um olho."""
        try:
            coords_points = np.array([(int(landmark.x * image_shape[1]), int(landmark.y * image_shape[0])) for landmark in eye_landmarks])
            p1, p2, p3, p4, p5, p6 = coords_points
            vertical_dist1 = self._calculate_distance(p2, p6)
            vertical_dist2 = self._calculate_distance(p3, p5)
            horizontal_dist = self._calculate_distance(p1, p4)
            if horizontal_dist == 0: return 0.0
            ear = (vertical_dist1 + vertical_dist2) / (2.0 * horizontal_dist)
            return ear
        except Exception as e:
            print(f"Erro ao calcular EAR: {e}")
            return 0.0

    def _calculate_distance(self, point1, point2):
        """Calcula a distância euclidiana entre dois pontos 2D."""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def get_head_pose(self, face_landmarks, image_shape):
        """Calcula a pose da cabeça (pitch, yaw, roll) a partir dos landmarks faciais."""
        img_h, img_w, img_c = image_shape
        
        face_3d = np.array([
            [0.0, 0.0, 0.0],           # Nariz (ponta)
            [0.0, -330.0, -65.0],      # Queixo
            [-225.0, 170.0, -135.0],   # Olho esquerdo (canto esquerdo)
            [225.0, 170.0, -135.0],    # Olho direito (canto direito)
            [-150.0, -150.0, -125.0],  # Boca (canto esquerdo)
            [150.0, -150.0, -125.0]    # Boca (canto direito)
        ], dtype=np.float64)

        face_2d = np.array([
            [face_landmarks[1].x * img_w, face_landmarks[1].y * img_h],
            [face_landmarks[152].x * img_w, face_landmarks[152].y * img_h],
            [face_landmarks[33].x * img_w, face_landmarks[33].y * img_h],
            [face_landmarks[263].x * img_w, face_landmarks[263].y * img_h],
            [face_landmarks[61].x * img_w, face_landmarks[61].y * img_h],
            [face_landmarks[291].x * img_w, face_landmarks[291].y * img_h]
        ], dtype=np.float64)

        focal_length = 1 * img_w
        cam_center = (img_w / 2, img_h / 2)
        camera_matrix = np.array([
            [focal_length, 0, cam_center[0]],
            [0, focal_length, cam_center[1]],
            [0, 0, 1]
        ], dtype=np.float64)

        dist_coeffs = np.zeros((4, 1))

        success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, camera_matrix, dist_coeffs)

        rmat, jac = cv2.Rodrigues(rot_vec)

        angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

        yaw = angles[1] * 180 / math.pi
        roll = angles[2] * 180 / math.pi

        return yaw, roll

class MouseController:
    """Gerencia o movimento e cliques do mouse."""
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"Resolução da tela detectada: {self.screen_width}x{self.screen_height}")
        self.prev_mouse_x, self.prev_mouse_y = pyautogui.position()
        self.last_left_click_time = 0
        self.last_right_click_time = 0
        self.last_alt_tab_time = 0
        self.last_head_tilt_time = 0

    def move_mouse(self, nose_coords_norm, image_width, image_height):
        """Move o cursor do mouse baseado nas coordenadas do nariz."""
        target_x = self._map_value(nose_coords_norm[0], CONTROL_AREA_X_MIN, CONTROL_AREA_X_MAX, 0, self.screen_width)
        target_y = self._map_value(nose_coords_norm[1], CONTROL_AREA_Y_MIN, CONTROL_AREA_Y_MAX, 0, self.screen_height)

        if INVERT_X_AXIS: target_x = self.screen_width - target_x
        if INVERT_Y_AXIS: target_y = self.screen_height - target_y

        current_mouse_x = self.prev_mouse_x + (target_x - self.prev_mouse_x) * SMOOTHING_FACTOR
        current_mouse_y = self.prev_mouse_y + (target_y - self.prev_mouse_y) * SMOOTHING_FACTOR

        try:
            pyautogui.moveTo(int(current_mouse_x), int(current_mouse_y))
            self.prev_mouse_x, self.prev_mouse_y = current_mouse_x, current_mouse_y
        except pyautogui.FailSafeException:
            print("FailSafe ativado (mouse movido para o canto). Encerrando...")
            return False
        except Exception as e:
            print(f"Erro ao mover o mouse: {e}")
        return True

    def click(self, button_type, current_time):
        """Realiza um clique do mouse (esquerdo ou direito) com debounce."""
        if button_type == 'left':
            if current_time - self.last_left_click_time > CLICK_DEBOUNCE_TIME:
                try:
                    pyautogui.click(button='left')
                    print("Clique Esquerdo!")
                    self.last_left_click_time = current_time
                    return True
                except Exception as e:
                    print(f"Erro ao clicar (esquerdo): {e}")
        elif button_type == 'right':
            if current_time - self.last_right_click_time > CLICK_DEBOUNCE_TIME:
                try:
                    pyautogui.click(button='right')
                    print("Clique Direito!")
                    self.last_right_click_time = current_time
                    return True
                except Exception as e:
                    print(f"Erro ao clicar (direito): {e}")
        return False

    def trigger_alt_tab(self, current_time):
        """Ativa a combinação Alt+Tab com debounce."""
        if current_time - self.last_alt_tab_time > ALT_TAB_DEBOUNCE_TIME:
            try:
                pyautogui.hotkey('alt', 'tab')
                print("Alt+Tab ativado!")
                self.last_alt_tab_time = current_time
                return True
            except Exception as e:
                print(f"Erro ao ativar Alt+Tab: {e}")
        return False

    def trigger_head_tilt(self, direction, current_time):
        """Ativa uma ação do teclado baseada na inclinação da cabeça com debounce."""
        if current_time - self.last_head_tilt_time > HEAD_TILT_DEBOUNCE_TIME:
            try:
                if direction == 'left':
                    pyautogui.press(HEAD_TILT_LEFT_TRIGGER_KEY)
                    print(f"Inclinação da cabeça para a esquerda: {HEAD_TILT_LEFT_TRIGGER_KEY} pressionado!")
                elif direction == 'right':
                    pyautogui.press(HEAD_TILT_RIGHT_TRIGGER_KEY)
                    print(f"Inclinação da cabeça para a direita: {HEAD_TILT_RIGHT_TRIGGER_KEY} pressionado!")
                self.last_head_tilt_time = current_time
                return True
            except Exception as e:
                print(f"Erro ao ativar gatilho de inclinação da cabeça: {e}")
        return False

    def _map_value(self, value, from_min, from_max, to_min, to_max):
        """Mapeia um valor de um intervalo para outro, com clamping."""
        value = max(min(value, from_max), from_min)
        from_span = from_max - from_min
        to_span = to_max - to_min
        if from_span == 0: return to_min
        value_scaled = float(value - from_min) / float(from_span)
        return to_min + (value_scaled * to_span)

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
        print("Abrindo a webcam...")
        self.cap = ThreadedCamera(0).start()
        time.sleep(1.0) # Aguarda a câmera inicializar
        frame = self.cap.read()
        if frame is None:
            print("Erro: Não foi possível abrir a webcam. O controle do mouse não funcionará.")
            self.use_dummy_image = True
        else:
            self.image_height, self.image_width, _ = frame.shape
            print(f"Resolução da câmera detectada: {self.image_width}x{self.image_height}")

    def run(self):
        """Loop principal da aplicação."""
        print("--- Pisk&Click Iniciado ---")
        print("Pressione 'q' para sair.")
        print("Movimente o nariz para controlar o cursor.")
        print("Pisque o olho esquerdo para clique esquerdo, olho direito para clique direito.")
        print("Incline a cabeça para a esquerda/direita para acionar gatilhos.")
        print(f"Ajustes Atuais: EAR Thresh={EAR_THRESHOLD}, Smooth={SMOOTHING_FACTOR}, Refine={REFINE_LANDMARKS}")

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
                        print("Ignorando frame vazio da câmera.")
                        continue
                    image = cv2.flip(image, 1)

                process_this_frame = (self.frame_counter % PROCESS_EVERY_N_FRAMES == 0)

                nose_coords_norm = None
                left_ear = 0.0
                right_ear = 0.0
                left_blink_detected_this_frame = False
                right_blink_detected_this_frame = False
                yaw = 0.0
                roll = 0.0

                if process_this_frame:
                    results = self.face_controller.process_frame(image)

                    if results and results.multi_face_landmarks:
                        self.face_detected = True
                        face_landmarks = results.multi_face_landmarks[0].landmark

                        nose_coords_norm, nose_pixel_coords = self.face_controller.get_nose_coords(face_landmarks, self.image_width, self.image_height)
                        cv2.circle(image, nose_pixel_coords, 5, (0, 0, 255), -1)

                        left_eye_landmarks = [face_landmarks[i] for i in LEFT_EYE_LANDMARKS_IDXS]
                        right_eye_landmarks = [face_landmarks[i] for i in RIGHT_EYE_LANDMARKS_IDXS]
                        left_ear = self.face_controller.calculate_ear(left_eye_landmarks, (self.image_height, self.image_width))
                        right_ear = self.face_controller.calculate_ear(right_eye_landmarks, (self.image_height, self.image_width))

                        if left_ear < EAR_THRESHOLD:
                            self.left_blink_counter += 1
                        else:
                            if self.left_blink_counter >= BLINK_CONSECUTIVE_FRAMES:
                                left_blink_detected_this_frame = self.mouse_controller.click('left', current_time)
                            self.left_blink_counter = 0

                        if right_ear < EAR_THRESHOLD:
                            self.right_blink_counter += 1
                        else:
                            if self.right_blink_counter >= BLINK_CONSECUTIVE_FRAMES:
                                right_blink_detected_this_frame = self.mouse_controller.click('right', current_time)
                            self.right_blink_counter = 0

                        if ALT_TAB_TRIGGER_BOTH_EYES_BLINK and left_blink_detected_this_frame and right_blink_detected_this_frame:
                            self.mouse_controller.trigger_alt_tab(current_time)

                        try:
                            yaw, roll = self.face_controller.get_head_pose(face_landmarks, image.shape)
                            if roll < -HEAD_TILT_THRESHOLD:
                                self.mouse_controller.trigger_head_tilt('left', current_time)
                            elif roll > HEAD_TILT_THRESHOLD:
                                self.mouse_controller.trigger_head_tilt('right', current_time)
                        except Exception as e:
                            print(f"Erro ao calcular pose da cabeça: {e}")

                    else:
                        self.face_detected = False
                        self.left_blink_counter = 0
                        self.right_blink_counter = 0
                        print("Aviso: Rosto não detectado. O controle do mouse está pausado.")

                if self.face_detected and nose_coords_norm and not self.use_dummy_image:
                    if not self.mouse_controller.move_mouse(nose_coords_norm, self.image_width, self.image_height):
                        break
                elif not self.face_detected and not self.use_dummy_image:
                    cv2.putText(image, "Rosto nao detectado!", (self.image_width // 2 - 150, self.image_height // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                self.update_display(image, left_ear, right_ear, left_blink_detected_this_frame, right_blink_detected_this_frame, yaw, roll)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Tecla 'q' pressionada. Encerrando...")
                    break

        except KeyboardInterrupt:
            print("\nInterrupção pelo usuário (Ctrl+C).")
        except Exception as e:
            print(f"Ocorreu um erro inesperado no loop principal: {e}")
        finally:
            self.cleanup()

    def update_display(self, image, left_ear, right_ear, left_blink_detected_this_frame, right_blink_detected_this_frame, yaw, roll):
        """Atualiza a exibição de informações na tela."""
        new_frame_time = time.time()
        if self.prev_frame_time > 0:
            fps = 1 / (new_frame_time - self.prev_frame_time)
            cv2.putText(image, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
        self.prev_frame_time = new_frame_time

        cv2.putText(image, f"EAR Esq: {left_ear:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(image, f"EAR Dir: {right_ear:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(image, f"Yaw: {yaw:.2f}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(image, f"Roll: {roll:.2f}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)

        if left_blink_detected_this_frame:
            self.left_blink_detected_visual = True
        if right_blink_detected_this_frame:
            self.right_blink_detected_visual = True

        if self.left_blink_detected_visual:
            cv2.putText(image, "CLIQUE ESQ", (self.image_width - 200, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
        if self.right_blink_detected_visual:
            cv2.putText(image, "CLIQUE DIR", (self.image_width - 200, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)

        if left_ear >= EAR_THRESHOLD: self.left_blink_detected_visual = False
        if right_ear >= EAR_THRESHOLD: self.right_blink_detected_visual = False

        try:
            cv2.imshow('Pisk&Click - Controle Facial', image)
        except cv2.error as e:
            if "display" in str(e).lower():
                if not self.use_dummy_image and self.frame_counter % 60 == 0:
                    print("Aviso: Não foi possível exibir a janela (ambiente sem GUI?). Controle do mouse/clique ainda ativo.")
            else:
                print(f"Erro no cv2.imshow: {e}")

    def cleanup(self):
        """Libera os recursos utilizados pela aplicação."""
        print("Encerrando aplicação...")
        if not self.use_dummy_image and self.cap:
            self.cap.stop()
            print("Webcam liberada.")
        if 'cv2' in locals() and hasattr(cv2, 'destroyAllWindows'):
            try:
                cv2.destroyAllWindows()
            except cv2.error:
                pass
        if self.face_controller.face_mesh:
            self.face_controller.face_mesh.close()
            print("Recursos do Mediapipe liberados.")
        print("Aplicação Pisk&Click encerrada.")

if __name__ == "__main__":
    app = Application()
    app.run()


