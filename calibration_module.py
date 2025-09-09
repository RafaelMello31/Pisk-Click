import cv2
import mediapipe as mp
import time
import numpy as np
import json
import os
import math
import logging
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from contextlib import contextmanager

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importa as configurações padrão do config.py original para ter valores de fallback
try:
    from config import (
        NOSE_TIP_INDEX,
        LEFT_EYE_LANDMARKS_IDXS,
        RIGHT_EYE_LANDMARKS_IDXS,
        REFINE_LANDMARKS,
        EAR_THRESHOLD,
        HEAD_TILT_THRESHOLD
    )
except ImportError:
    logger.warning("config.py não encontrado. Usando valores padrão.")
    # Define valores padrão se config.py não puder ser importado (primeira execução)
    NOSE_TIP_INDEX = 1
    LEFT_EYE_LANDMARKS_IDXS = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE_LANDMARKS_IDXS = [362, 385, 387, 263, 380, 373]
    REFINE_LANDMARKS = False
    EAR_THRESHOLD = 0.25
    HEAD_TILT_THRESHOLD = 15.0


@dataclass
class CalibrationResults:
    """Estrutura para armazenar resultados da calibração."""
    ear_threshold: Optional[float] = None
    head_tilt_threshold: Optional[float] = None
    success: bool = False
    message: str = ""


@dataclass
class CalibrationConfig:
    """Configurações para o processo de calibração."""
    ear_collection_duration: int = 10
    head_tilt_collection_duration: int = 10
    min_data_points: int = 50
    ear_percentile_threshold: float = 5.0  # Percentil usado para detectar piscadas
    head_tilt_percentile_threshold: float = 75.0
    ear_min_threshold: float = 0.10
    ear_max_threshold: float = 0.30
    head_tilt_min_threshold: float = 3.0
    head_tilt_max_threshold: float = 25.0


class CameraManager:
    """Gerenciador da câmera com context manager."""

    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap = None
        self.image_height = 480
        self.image_width = 640

    @contextmanager
    def get_camera(self):
        """Context manager para gerenciar a câmera."""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                raise RuntimeError("Não foi possível abrir a webcam")

            # Detecta resolução da câmera
            ret, frame = self.cap.read()
            if ret:
                self.image_height, self.image_width, _ = frame.shape
                logger.info(f"Resolução da câmera: {self.image_width}x{self.image_height}")

            yield self.cap
        except Exception as e:
            logger.error(f"Erro ao inicializar câmera: {e}")
            raise
        finally:
            if self.cap:
                self.cap.release()
                cv2.destroyAllWindows()
                logger.info("Câmera liberada")


class DataCollector:
    """Coletor de dados para calibração."""

    def __init__(self, face_controller, camera_manager: CameraManager):
        self.face_controller = face_controller
        self.camera_manager = camera_manager

    def collect_ear_data(self, duration: int, instruction: str) -> Tuple[List[float], List[float]]:
        """Coleta dados de Eye Aspect Ratio (EAR)."""
        logger.info(f"Coletando dados EAR: {instruction}")
        left_ears = []
        right_ears = []
        start_time = time.time()

        with self.camera_manager.get_camera() as cap:
            while time.time() - start_time < duration:
                success, image = cap.read()
                if not success:
                    continue

                image = cv2.flip(image, 1)
                results = self.face_controller.process_frame(image)

                if results and results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0].landmark

                    left_ear = self._calculate_ear(face_landmarks, LEFT_EYE_LANDMARKS_IDXS)
                    right_ear = self._calculate_ear(face_landmarks, RIGHT_EYE_LANDMARKS_IDXS)

                    if left_ear > 0:
                        left_ears.append(left_ear)
                    if right_ear > 0:
                        right_ears.append(right_ear)

                # Interface visual
                remaining_time = int(duration - (time.time() - start_time))
                self._draw_countdown(image, f"EAR: {remaining_time}s", instruction)
                cv2.imshow("Calibração EAR", image)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logger.info("Calibração interrompida pelo usuário")
                    break

        logger.info(f"Coletados {len(left_ears)} pontos para olho esquerdo, {len(right_ears)} para direito")
        return left_ears, right_ears

    def collect_head_tilt_data(self, duration: int) -> List[float]:
        """Coleta dados de inclinação da cabeça."""
        logger.info("Coletando dados de inclinação da cabeça")
        rolls = []
        start_time = time.time()

        with self.camera_manager.get_camera() as cap:
            while time.time() - start_time < duration:
                success, image = cap.read()
                if not success:
                    continue

                image = cv2.flip(image, 1)
                results = self.face_controller.process_frame(image)

                if results and results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0].landmark
                    try:
                        yaw, roll = self.face_controller.get_head_pose(face_landmarks, image.shape)
                        rolls.append(roll)
                    except Exception as e:
                        logger.warning(f"Erro ao obter pose da cabeça: {e}")

                # Interface visual
                remaining_time = int(duration - (time.time() - start_time))
                instruction = "Incline a cabeça para os lados"
                self._draw_countdown(image, f"Inclinação: {remaining_time}s", instruction)
                cv2.imshow("Calibração Inclinação", image)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logger.info("Calibração interrompida pelo usuário")
                    break

        logger.info(f"Coletados {len(rolls)} pontos de inclinação")
        return rolls

    def _calculate_ear(self, face_landmarks, eye_indices: List[int]) -> float:
        """Calcula o Eye Aspect Ratio para um olho."""
        try:
            eye_landmarks = [face_landmarks[i] for i in eye_indices]
            return self.face_controller.calculate_ear(
                eye_landmarks,
                (self.camera_manager.image_height, self.camera_manager.image_width)
            )
        except Exception as e:
            logger.debug(f"Erro ao calcular EAR: {e}")
            return 0.0

    @staticmethod
    def _draw_countdown(image: np.ndarray, main_text: str, instruction: str):
        """Desenha interface visual durante a coleta."""
        height, width = image.shape[:2]

        # Fundo semi-transparente
        overlay = image.copy()
        cv2.rectangle(overlay, (10, 10), (width - 10, 120), (0, 0, 0), -1)
        image = cv2.addWeighted(image, 0.7, overlay, 0.3, 0)

        # Textos
        cv2.putText(image, main_text, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(image, instruction, (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(image, "Pressione 'q' para parar", (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)


class CalibrationAlgorithm:
    """Algoritmos de calibração."""

    @staticmethod
    def calibrate_ear_threshold(
            open_eyes_data: List[float],
            blinking_data: List[float],
            config: CalibrationConfig
    ) -> Optional[float]:
        """Calcula o limiar EAR ideal usando análise estatística."""
        all_data = open_eyes_data + blinking_data

        if len(all_data) < config.min_data_points:
            logger.warning(f"Dados insuficientes para calibração EAR: {len(all_data)} < {config.min_data_points}")
            return None

        # Remove outliers usando IQR
        clean_data = CalibrationAlgorithm._remove_outliers(all_data)

        if len(clean_data) < config.min_data_points // 2:
            logger.warning("Muitos outliers removidos, usando dados originais")
            clean_data = all_data

        # Usa percentil baixo como indicativo de piscadas
        sorted_data = sorted(clean_data)
        percentile_index = int(len(sorted_data) * config.ear_percentile_threshold / 100)

        if percentile_index >= len(sorted_data):
            percentile_index = len(sorted_data) - 1

        threshold = sorted_data[percentile_index]

        # Aplica limites de segurança
        threshold = max(config.ear_min_threshold,
                        min(threshold, config.ear_max_threshold))

        logger.info(f"Limiar EAR calculado: {threshold:.3f}")
        return threshold

    @staticmethod
    def calibrate_head_tilt_threshold(
            tilt_data: List[float],
            config: CalibrationConfig
    ) -> Optional[float]:
        """Calcula o limiar de inclinação da cabeça."""
        if len(tilt_data) < config.min_data_points:
            logger.warning(f"Dados insuficientes para calibração de inclinação: {len(tilt_data)}")
            return None

        # Remove valores próximos de zero (cabeça reta)
        significant_tilts = [abs(t) for t in tilt_data if abs(t) > 1.0]

        if not significant_tilts:
            logger.warning("Nenhuma inclinação significativa detectada")
            return None

        # Remove outliers
        clean_data = CalibrationAlgorithm._remove_outliers(significant_tilts)

        if not clean_data:
            clean_data = significant_tilts

        # Usa percentil como limiar
        threshold = np.percentile(clean_data, config.head_tilt_percentile_threshold)

        # Aplica limites de segurança
        threshold = max(config.head_tilt_min_threshold,
                        min(threshold, config.head_tilt_max_threshold))

        logger.info(f"Limiar de inclinação calculado: {threshold:.3f}°")
        return threshold

    @staticmethod
    def _remove_outliers(data: List[float]) -> List[float]:
        """Remove outliers usando método IQR."""
        if len(data) < 4:
            return data

        data_array = np.array(data)
        q1 = np.percentile(data_array, 25)
        q3 = np.percentile(data_array, 75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        filtered_data = [x for x in data if lower_bound <= x <= upper_bound]

        logger.debug(f"Outliers removidos: {len(data) - len(filtered_data)} de {len(data)}")
        return filtered_data


class ConfigManager:
    """Gerenciador de configurações."""

    def __init__(self, profile_manager=None):
        self.profile_manager = profile_manager

    def save_calibration_results(self, results: CalibrationResults, profile_name: str = "default"):
        """Salva os resultados da calibração."""
        if not results.success:
            logger.error(f"Tentativa de salvar calibração sem sucesso: {results.message}")
            return False

        try:
            if self.profile_manager:
                self._save_to_profile(results, profile_name)

            self._save_to_config_file(results)
            logger.info("Configurações de calibração salvas com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            return False

    def _save_to_profile(self, results: CalibrationResults, profile_name: str):
        """Salva no sistema de perfis."""
        current_config = self.profile_manager.load_profile_config(profile_name)
        if not current_config:
            current_config = self._get_default_config()
            self.profile_manager.create_profile(profile_name, current_config)

        if results.ear_threshold is not None:
            current_config["EAR_THRESHOLD"] = results.ear_threshold
        if results.head_tilt_threshold is not None:
            current_config["HEAD_TILT_THRESHOLD"] = results.head_tilt_threshold

        self.profile_manager.save_profile_config(profile_name, current_config)

    def _save_to_config_file(self, results: CalibrationResults):
        """Salva no arquivo config.py."""
        try:
            # Re-importa configurações atuais
            import importlib
            import config
            importlib.reload(config)

            # Gera novo conteúdo do config.py
            config_content = self._generate_config_content(results)

            with open("config.py", "w", encoding='utf-8') as f:
                f.write(config_content)

        except Exception as e:
            logger.error(f"Erro ao atualizar config.py: {e}")
            raise

    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão."""
        try:
            from config import *
            return {
                "REFINE_LANDMARKS": REFINE_LANDMARKS,
                "EAR_THRESHOLD": EAR_THRESHOLD,
                "BLINK_CONSECUTIVE_FRAMES": BLINK_CONSECUTIVE_FRAMES,
                "SMOOTHING_FACTOR": SMOOTHING_FACTOR,
                "CONTROL_AREA_X_MIN": CONTROL_AREA_X_MIN,
                "CONTROL_AREA_X_MAX": CONTROL_AREA_X_MAX,
                "CONTROL_AREA_Y_MIN": CONTROL_AREA_Y_MIN,
                "CONTROL_AREA_Y_MAX": CONTROL_AREA_Y_MAX,
                "INVERT_X_AXIS": INVERT_X_AXIS,
                "INVERT_Y_AXIS": INVERT_Y_AXIS,
                "CLICK_DEBOUNCE_TIME": CLICK_DEBOUNCE_TIME,
                "PROCESS_EVERY_N_FRAMES": PROCESS_EVERY_N_FRAMES,
                "ALT_TAB_TRIGGER_BOTH_EYES_BLINK": ALT_TAB_TRIGGER_BOTH_EYES_BLINK,
                "ALT_TAB_DEBOUNCE_TIME": ALT_TAB_DEBOUNCE_TIME,
                "HEAD_TILT_THRESHOLD": HEAD_TILT_THRESHOLD,
                "HEAD_TILT_DEBOUNCE_TIME": HEAD_TILT_DEBOUNCE_TIME,
                "HEAD_TILT_LEFT_TRIGGER_KEY": HEAD_TILT_LEFT_TRIGGER_KEY,
                "HEAD_TILT_RIGHT_TRIGGER_KEY": HEAD_TILT_RIGHT_TRIGGER_KEY,
            }
        except ImportError:
            # Configuração mínima se não conseguir importar
            return {
                "EAR_THRESHOLD": 0.25,
                "HEAD_TILT_THRESHOLD": 15.0,
                "REFINE_LANDMARKS": False
            }

    def _generate_config_content(self, results: CalibrationResults) -> str:
        """Gera o conteúdo do arquivo config.py."""
        # Importa valores atuais
        from config import *

        # Atualiza com resultados da calibração
        ear_threshold = results.ear_threshold if results.ear_threshold is not None else EAR_THRESHOLD
        head_tilt_threshold = results.head_tilt_threshold if results.head_tilt_threshold is not None else HEAD_TILT_THRESHOLD

        return f'''# --- Constantes e Configurações ---
    # Arquivo gerado automaticamente pela calibração

    # Índices dos landmarks faciais (Mediapipe Face Mesh)
    NOSE_TIP_INDEX = {NOSE_TIP_INDEX}
    LEFT_EYE_LANDMARKS_IDXS = {LEFT_EYE_LANDMARKS_IDXS}
    RIGHT_EYE_LANDMARKS_IDXS = {RIGHT_EYE_LANDMARKS_IDXS}

    # Qualidade vs Desempenho Mediapipe
    REFINE_LANDMARKS = {REFINE_LANDMARKS}

    # Limiares e Contadores para Detecção de Piscada
    EAR_THRESHOLD = {ear_threshold}
    BLINK_CONSECUTIVE_FRAMES = {BLINK_CONSECUTIVE_FRAMES}

    # Suavização do Movimento do Mouse
    SMOOTHING_FACTOR = {SMOOTHING_FACTOR}

    # Área de Controle do Rosto (Mapeamento Câmera -> Tela)
    CONTROL_AREA_X_MIN = {CONTROL_AREA_X_MIN}
    CONTROL_AREA_X_MAX = {CONTROL_AREA_X_MAX}
    CONTROL_AREA_Y_MIN = {CONTROL_AREA_Y_MIN}
    CONTROL_AREA_Y_MAX = {CONTROL_AREA_Y_MAX}

    # Inversão de Eixos (Opcional)
    INVERT_X_AXIS = {INVERT_X_AXIS}
    INVERT_Y_AXIS = {INVERT_Y_AXIS}

    # Debounce para Cliques
    CLICK_DEBOUNCE_TIME = {CLICK_DEBOUNCE_TIME}

    # Otimização de Desempenho (Opcional)
    PROCESS_EVERY_N_FRAMES = {PROCESS_EVERY_N_FRAMES}

    # --- Configurações para a funcionalidade Alt+Tab ---
    ALT_TAB_TRIGGER_BOTH_EYES_BLINK = {ALT_TAB_TRIGGER_BOTH_EYES_BLINK}
    ALT_TAB_DEBOUNCE_TIME = {ALT_TAB_DEBOUNCE_TIME}

    # --- Configurações para a funcionalidade de Inclinação da Cabeça ---
    HEAD_TILT_THRESHOLD = {head_tilt_threshold}
    HEAD_TILT_DEBOUNCE_TIME = {HEAD_TILT_DEBOUNCE_TIME}
    HEAD_TILT_LEFT_TRIGGER_KEY = {repr(HEAD_TILT_LEFT_TRIGGER_KEY)}
    HEAD_TILT_RIGHT_TRIGGER_KEY = {repr(HEAD_TILT_RIGHT_TRIGGER_KEY)}
    '''


class CalibrationModule:
    """Módulo principal de calibração refatorado."""

    def __init__(self, face_controller, profile_manager=None, config: CalibrationConfig = None):
        self.face_controller = face_controller
        self.config = config or CalibrationConfig()
        self.camera_manager = CameraManager()
        self.data_collector = DataCollector(face_controller, self.camera_manager)
        self.config_manager = ConfigManager(profile_manager)

    def run_calibration(self, calibrate_ear: bool = True, calibrate_head_tilt: bool = True) -> CalibrationResults:
        """Executa o processo completo de calibração."""
        logger.info("=== Iniciando Calibração Automática ===")

        results = CalibrationResults()

        try:
            if calibrate_ear:
                results.ear_threshold = self._calibrate_ear()

            if calibrate_head_tilt:
                results.head_tilt_threshold = self._calibrate_head_tilt()

            # Considera bem-sucedida se pelo menos uma calibração funcionou
            results.success = (results.ear_threshold is not None) or (results.head_tilt_threshold is not None)

            if results.success:
                results.message = "Calibração concluída com sucesso"
                self.config_manager.save_calibration_results(results)
                logger.info("=== Calibração Finalizada com Sucesso ===")
            else:
                results.message = "Falha na calibração - dados insuficientes"
                logger.warning("=== Calibração Falhou ===")

        except Exception as e:
            logger.error(f"Erro durante calibração: {e}")
            results.success = False
            results.message = f"Erro: {str(e)}"

        return results

    def _calibrate_ear(self) -> Optional[float]:
        """Calibra o limiar EAR."""
        logger.info("--- Calibração de Piscada ---")

        # Coleta dados com olhos abertos
        print("Mantenha os olhos bem abertos e olhe para a câmera.")
        time.sleep(3)
        open_left, open_right = self.data_collector.collect_ear_data(
            5, "Mantenha os olhos abertos"
        )

        # Coleta dados piscando normalmente
        print("\nAgora pisque normalmente.")
        time.sleep(2)
        blink_left, blink_right = self.data_collector.collect_ear_data(
            self.config.ear_collection_duration, "Pisque normalmente"
        )

        # Combina todos os dados
        all_open = open_left + open_right
        all_blink = blink_left + blink_right

        return CalibrationAlgorithm.calibrate_ear_threshold(
            all_open, all_blink, self.config
        )

    def _calibrate_head_tilt(self) -> Optional[float]:
        """Calibra o limiar de inclinação da cabeça."""
        logger.info("--- Calibração de Inclinação da Cabeça ---")

        print("Incline a cabeça para a esquerda e direita repetidamente.")
        time.sleep(3)

        tilt_data = self.data_collector.collect_head_tilt_data(
            self.config.head_tilt_collection_duration
        )

        return CalibrationAlgorithm.calibrate_head_tilt_threshold(
            tilt_data, self.config
        )


# Exemplo de uso
if __name__ == "__main__":
    # Para testar o módulo independentemente
    class MockFaceController:
        """Mock do FaceController para testes."""

        def __init__(self):
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=REFINE_LANDMARKS,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )

        def process_frame(self, image):
            """Processa frame e retorna landmarks."""
            image.flags.writ