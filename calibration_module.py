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

# Logger do módulo
logger = logging.getLogger(__name__)

# Importa as configurações padrão do config.py original para ter valores de fallback
try:
    from config import (
        NOSE_TIP_INDEX,
        LEFT_EYE_LANDMARKS_IDXS,
        RIGHT_EYE_LANDMARKS_IDXS,
        REFINE_LANDMARKS,
        EAR_THRESHOLD,
    )
except ImportError:
    logger.warning("config.py não encontrado. Usando valores padrão.")
    NOSE_TIP_INDEX = 1
    LEFT_EYE_LANDMARKS_IDXS = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE_LANDMARKS_IDXS = [362, 385, 387, 263, 380, 373]
    REFINE_LANDMARKS = False
    EAR_THRESHOLD = 0.25


@dataclass
class CalibrationResults:
    """Estrutura para armazenar resultados da calibração."""
    ear_threshold: Optional[float] = None
    success: bool = False
    message: str = ""


@dataclass
class CalibrationConfig:
    """Configurações para o processo de calibração."""
    ear_collection_duration: int = 10
    min_data_points: int = 50
    ear_percentile_threshold: float = 5.0  # Percentil usado para detectar piscadas
    ear_min_threshold: float = 0.10
    ear_max_threshold: float = 0.30


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
    """Coletor de dados para calibração com interface visual melhorada."""

    def __init__(self, face_controller, camera_manager: CameraManager):
        self.face_controller = face_controller
        self.camera_manager = camera_manager
        self.window_name = "Calibração EAR - Pisck & Click"

    def collect_ear_data(self, duration: int, instruction: str) -> Tuple[List[float], List[float]]:
        """Coleta dados EAR com interface visual garantidamente visível."""
        logger.info(f"Coletando dados EAR: {instruction}")
        
        left_ears = []
        right_ears = []
        start_time = time.time()
        frame_count = 0

        try:
            with self.camera_manager.get_camera() as cap:
                # Configurar janela com posicionamento forçado
                self._setup_window()
                
                logger.info(f"Iniciando coleta por {duration} segundos...")
                logger.info(f"Instrução: {instruction}")
                
                while time.time() - start_time < duration:
                    success, image = cap.read()
                    if not success:
                        continue

                    frame_count += 1
                    image = cv2.flip(image, 1)
                    
                    # Processar com MediaPipe
                    results = self.face_controller.process_frame(image)

                    # Calcular EAR se face detectada
                    if results and results.multi_face_landmarks:
                        face_landmarks = results.multi_face_landmarks[0].landmark

                        left_ear = self._calculate_ear(face_landmarks, LEFT_EYE_LANDMARKS_IDXS)
                        right_ear = self._calculate_ear(face_landmarks, RIGHT_EYE_LANDMARKS_IDXS)

                        if left_ear > 0:
                            left_ears.append(left_ear)
                        if right_ear > 0:
                            right_ears.append(right_ear)

                    # Interface visual melhorada
                    remaining_time = int(duration - (time.time() - start_time))
                    # Fazer cópia da imagem para permitir modificações
                    display_image = np.array(image, copy=True)
                    if not display_image.flags.writeable:
                        display_image = display_image.copy()
                    self._draw_enhanced_interface(display_image, remaining_time, instruction, 
                                                len(left_ears), len(right_ears), frame_count)
                    
                    # Mostrar janela com posicionamento forçado
                    cv2.imshow(self.window_name, display_image)

                    # Verificar teclas
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        logger.info("Usuário pressionou 'q' - parando coleta")
                        break
                    elif key == 27:  # ESC
                        logger.info("Usuário pressionou ESC - parando coleta")
                        break

                logger.info(f"Coleta finalizada: {frame_count} frames, {len(left_ears)} + {len(right_ears)} dados EAR")
                
        except Exception as e:
            logger.error(f"Erro durante coleta: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self._cleanup_window()

        return left_ears, right_ears
    
    def _setup_window(self):
        """Configura janela OpenCV ampla e bem visível."""
        # Criar nova janela redimensionável
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        
        # Posicionar centralmente na tela
        cv2.moveWindow(self.window_name, 200, 100)
        
        # Definir tamanho amplo para melhor visibilidade
        cv2.resizeWindow(self.window_name, 1000, 750)
        
        logger.info(f"Janela '{self.window_name}' configurada na posição (200, 100) com tamanho 1000x750")
    
    def _cleanup_window(self):
        """Limpa recursos da janela com verificação de existência."""
        try:
            # Verificar se a janela existe antes de tentar destruí-la
            if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) >= 0:
                cv2.destroyWindow(self.window_name)
                cv2.waitKey(1)  # Permite que o OpenCV processe a destruição
                logger.info(f"Janela '{self.window_name}' fechada")
            else:
                logger.info(f"Janela '{self.window_name}' já estava fechada")
        except Exception as e:
            logger.warning(f"Erro ao fechar janela: {e}")
    
    def _draw_enhanced_interface(self, image, remaining_time: int, instruction: str, 
                               left_count: int, right_count: int, frame_count: int):
        """Desenha interface visual ampla com instruções claras e informações de calibração em tempo real."""
        height, width = image.shape[:2]
        
        # Calcular EAR em tempo real se há face detectada
        current_left_ear = 0.0
        current_right_ear = 0.0
        face_detected = False
        
        # Processar frame para obter EAR em tempo real
        results = self.face_controller.process_frame(image)
        if results and results.multi_face_landmarks:
            face_detected = True
            face_landmarks = results.multi_face_landmarks[0].landmark
            
            current_left_ear = self._calculate_ear(face_landmarks, LEFT_EYE_LANDMARKS_IDXS)
            current_right_ear = self._calculate_ear(face_landmarks, RIGHT_EYE_LANDMARKS_IDXS)
        
        # Painel de instruções superior amplo
        overlay = image.copy()
        cv2.rectangle(overlay, (0, 0), (width, 320), (0, 0, 0), -1)
        image = cv2.addWeighted(image, 0.5, overlay, 0.5, 0)
        
        # Título principal grande e destacado
        title_text = "CALIBRAÇÃO PISCK & CLICK"
        title_size = cv2.getTextSize(title_text, cv2.FONT_HERSHEY_DUPLEX, 1.5, 3)[0]
        title_x = (width - title_size[0]) // 2
        cv2.putText(image, title_text, (title_x, 50),
                    cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 255), 3)
        
        # Linha decorativa
        cv2.line(image, (50, 70), (width - 50, 70), (0, 255, 255), 2)
        
        # Informações EAR em tempo real
        if face_detected:
            ear_left_color = (0, 255, 0) if current_left_ear > EAR_THRESHOLD else (0, 0, 255)
            ear_right_color = (0, 255, 0) if current_right_ear > EAR_THRESHOLD else (0, 0, 255)
            
            cv2.putText(image, f"EAR Esquerdo: {current_left_ear:.3f}", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, ear_left_color, 2)
            cv2.putText(image, f"EAR Direito: {current_right_ear:.3f}", (width - 300, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, ear_right_color, 2)
            
            # Indicador de piscada
            if current_left_ear < EAR_THRESHOLD:
                cv2.putText(image, "PISCADA ESQ!", (50, 130),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            if current_right_ear < EAR_THRESHOLD:
                cv2.putText(image, "PISCADA DIR!", (width - 200, 130),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            cv2.putText(image, "ROSTO NÃO DETECTADO", (width//2 - 150, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        
        # Tempo restante muito destacado
        time_color = (0, 255, 0) if remaining_time > 3 else (0, 100, 255)
        time_text = f"TEMPO RESTANTE: {remaining_time}s"
        time_size = cv2.getTextSize(time_text, cv2.FONT_HERSHEY_DUPLEX, 1.8, 4)[0]
        time_x = (width - time_size[0]) // 2
        cv2.putText(image, time_text, (time_x, 170),
                    cv2.FONT_HERSHEY_DUPLEX, 1.8, time_color, 4)
        
        # Instrução principal muito grande e clara com destaque para fases
        instruction_lines = self._split_instruction(instruction.upper(), width)
        y_offset = 220
        
        # Se a primeira linha contém "FASE", destacar em cor diferente
        for i, line in enumerate(instruction_lines):
            if i == 0 and "FASE" in line:
                # Primeira linha (FASE) em destaque
                line_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_DUPLEX, 1.4, 4)[0]
                line_x = (width - line_size[0]) // 2
                cv2.putText(image, line, (line_x, y_offset),
                            cv2.FONT_HERSHEY_DUPLEX, 1.4, (0, 255, 255), 4)
                y_offset += 50
            else:
                # Demais linhas em branco
                line_size = cv2.getTextSize(line, cv2.FONT_HERSHEY_DUPLEX, 1.1, 3)[0]
                line_x = (width - line_size[0]) // 2
                cv2.putText(image, line, (line_x, y_offset),
                            cv2.FONT_HERSHEY_DUPLEX, 1.1, (255, 255, 255), 3)
                y_offset += 40
        
        # Painel inferior com informações
        cv2.rectangle(overlay, (0, height - 140), (width, height), (0, 0, 0), -1)
        image = cv2.addWeighted(image, 0.7, overlay, 0.3, 0)
        
        # Limiar EAR atual
        threshold_text = f"LIMIAR EAR ATUAL: {EAR_THRESHOLD:.3f}"
        threshold_size = cv2.getTextSize(threshold_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        threshold_x = (width - threshold_size[0]) // 2
        cv2.putText(image, threshold_text, (threshold_x, height - 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Estatísticas centralizadas
        stats_text = f"DADOS COLETADOS: {left_count + right_count} | FRAMES: {frame_count}"
        stats_size = cv2.getTextSize(stats_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        stats_x = (width - stats_size[0]) // 2
        cv2.putText(image, stats_text, (stats_x, height - 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        # Controles centralizados
        controls_text = "PRESSIONE 'Q' OU ESC PARA PARAR A CALIBRAÇÃO"
        controls_size = cv2.getTextSize(controls_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        controls_x = (width - controls_size[0]) // 2
        cv2.putText(image, controls_text, (controls_x, height - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        # Indicador de atividade pulsante
        activity_color = (0, 255, 0) if frame_count % 20 < 10 else (0, 200, 0)
        cv2.circle(image, (width - 50, 50), 15, activity_color, -1)
        cv2.putText(image, "REC", (width - 65, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Barra de progresso visual ampla
        progress_width = int((width - 100) * (1 - remaining_time / 10))  # Assumindo duração máxima de 10s
        if progress_width > 0:
            # Fundo da barra
            cv2.rectangle(image, (50, height - 20), (width - 50, height - 10), (50, 50, 50), -1)
            # Progresso
            cv2.rectangle(image, (50, height - 20), (50 + progress_width, height - 10), 
                         (0, 255, 0), -1)
        
        return image
    
    def _split_instruction(self, instruction: str, width: int) -> List[str]:
        """Divide instruções longas em múltiplas linhas para melhor legibilidade."""
        max_chars = width // 20  # Aproximadamente baseado no tamanho da fonte
        words = instruction.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_chars:
                current_line += (" " if current_line else "") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [instruction]

    def _calculate_ear(self, face_landmarks, eye_indices: List[int]) -> float:
        """Calcula o Eye Aspect Ratio para um olho."""
        try:
            eye_landmarks = [face_landmarks[i] for i in eye_indices]
            return self.face_controller.calculate_ear(
                eye_landmarks,
                (self.camera_manager.image_height, self.camera_manager.image_width),
            )
        except Exception as e:
            logger.debug(f"Erro ao calcular EAR: {e}")
            return 0.0

    @staticmethod
    def _draw_countdown(image: np.ndarray, main_text: str, instruction: str):
        """Desenha interface visual ampla durante a preparação."""
        height, width = image.shape[:2]

        # Fundo semi-transparente amplo
        overlay = image.copy()
        cv2.rectangle(overlay, (0, 0), (width, 200), (0, 0, 0), -1)
        image = cv2.addWeighted(image, 0.5, overlay, 0.5, 0)

        # Texto principal centralizado e grande
        main_size = cv2.getTextSize(main_text, cv2.FONT_HERSHEY_DUPLEX, 1.5, 3)[0]
        main_x = (width - main_size[0]) // 2
        cv2.putText(image, main_text, (main_x, 60),
                    cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 0), 3)
        
        # Instrução centralizada
        inst_size = cv2.getTextSize(instruction, cv2.FONT_HERSHEY_DUPLEX, 1.0, 2)[0]
        inst_x = (width - inst_size[0]) // 2
        cv2.putText(image, instruction, (inst_x, 120),
                    cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)
        
        # Controles centralizados
        control_text = "PRESSIONE 'Q' PARA PARAR"
        control_size = cv2.getTextSize(control_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        control_x = (width - control_size[0]) // 2
        cv2.putText(image, control_text, (control_x, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)


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
        # Importa o UserProfileManager se não foi fornecido
        if self.profile_manager is None:
            from user_profile_manager import UserProfileManager
            self.profile_manager = UserProfileManager()

    def save_calibration_results(self, results: CalibrationResults, profile_name: str = "default"):
        """Salva os resultados da calibração no perfil e no config.py."""
        if not results.success:
            logger.error(f"Tentativa de salvar calibração sem sucesso: {results.message}")
            return False

        try:
            # Sempre salva no perfil default para integração com config_gui.py
            self._save_to_profile(results, profile_name)
            
            # Também salva no config.py para compatibilidade
            self._save_to_config_file(results)
            
            logger.info(f"Configurações de calibração salvas no perfil '{profile_name}' e config.py")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            return False

    def _save_to_profile(self, results: CalibrationResults, profile_name: str):
        """Salva no sistema de perfis, criando o perfil se não existir."""
        current_config = self.profile_manager.load_profile_config(profile_name)
        
        # Se o perfil não existe, cria com configurações padrão
        if not current_config:
            current_config = self._get_default_config()
            logger.info(f"Criando perfil '{profile_name}' com configurações padrão")
            self.profile_manager.create_profile(profile_name, current_config)
        
        # Atualiza apenas o EAR_THRESHOLD com o resultado da calibração
        if results.ear_threshold is not None:
            old_threshold = current_config.get("EAR_THRESHOLD", "N/A")
            current_config["EAR_THRESHOLD"] = results.ear_threshold
            logger.info(f"Atualizando EAR_THRESHOLD no perfil '{profile_name}': {old_threshold} -> {results.ear_threshold}")
        
        # Salva as configurações atualizadas
        success = self.profile_manager.save_profile_config(profile_name, current_config)
        if success:
            logger.info(f"Perfil '{profile_name}' atualizado com sucesso")
        else:
            logger.error(f"Falha ao salvar perfil '{profile_name}'")

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
            import config
            return {
                "REFINE_LANDMARKS": config.REFINE_LANDMARKS,
                "EAR_THRESHOLD": config.EAR_THRESHOLD,
                "BLINK_CONSECUTIVE_FRAMES": config.BLINK_CONSECUTIVE_FRAMES,
                "SMOOTHING_FACTOR": config.SMOOTHING_FACTOR,
                "CONTROL_AREA_X_MIN": config.CONTROL_AREA_X_MIN,
                "CONTROL_AREA_X_MAX": config.CONTROL_AREA_X_MAX,
                "CONTROL_AREA_Y_MIN": config.CONTROL_AREA_Y_MIN,
                "CONTROL_AREA_Y_MAX": config.CONTROL_AREA_Y_MAX,
                "INVERT_X_AXIS": config.INVERT_X_AXIS,
                "INVERT_Y_AXIS": config.INVERT_Y_AXIS,
                "CLICK_DEBOUNCE_TIME": config.CLICK_DEBOUNCE_TIME,
                "PROCESS_EVERY_N_FRAMES": config.PROCESS_EVERY_N_FRAMES,
            }
        except ImportError:
            # Configuração mínima se não conseguir importar
            return {
                "EAR_THRESHOLD": 0.25,
                "REFINE_LANDMARKS": False
            }

    def _generate_config_content(self, results: CalibrationResults) -> str:
        """Gera o conteúdo do arquivo config.py."""
        # Importa valores atuais
        import config

        # Atualiza com resultados da calibração
        ear_threshold = results.ear_threshold if results.ear_threshold is not None else config.EAR_THRESHOLD

        return f'''# --- Constantes e Configurações ---
# Arquivo gerado automaticamente pela calibração

# Índices dos landmarks faciais (Mediapipe Face Mesh)
NOSE_TIP_INDEX = {config.NOSE_TIP_INDEX}
LEFT_EYE_LANDMARKS_IDXS = {config.LEFT_EYE_LANDMARKS_IDXS}
RIGHT_EYE_LANDMARKS_IDXS = {config.RIGHT_EYE_LANDMARKS_IDXS}

# Qualidade vs Desempenho Mediapipe
REFINE_LANDMARKS = {config.REFINE_LANDMARKS}

# Limiares e Contadores para Detecção de Piscada
EAR_THRESHOLD = {ear_threshold}
BLINK_CONSECUTIVE_FRAMES = {config.BLINK_CONSECUTIVE_FRAMES}

# Suavização do Movimento do Mouse
SMOOTHING_FACTOR = {config.SMOOTHING_FACTOR}

# Área de Controle do Rosto (Mapeamento Câmera -> Tela)
CONTROL_AREA_X_MIN = {config.CONTROL_AREA_X_MIN}
CONTROL_AREA_X_MAX = {config.CONTROL_AREA_X_MAX}
CONTROL_AREA_Y_MIN = {config.CONTROL_AREA_Y_MIN}
CONTROL_AREA_Y_MAX = {config.CONTROL_AREA_Y_MAX}

# Inversão de Eixos (Opcional)
INVERT_X_AXIS = {config.INVERT_X_AXIS}
INVERT_Y_AXIS = {config.INVERT_Y_AXIS}

# Debounce para Cliques
CLICK_DEBOUNCE_TIME = {config.CLICK_DEBOUNCE_TIME}

# Otimização de Desempenho (Opcional)
PROCESS_EVERY_N_FRAMES = {config.PROCESS_EVERY_N_FRAMES}
'''


class CalibrationModule:
    """Módulo principal de calibração refatorado."""

    def __init__(self, face_controller, profile_manager=None, config: CalibrationConfig = None):
        self.face_controller = face_controller
        self.config = config or CalibrationConfig()
        self.camera_manager = CameraManager()
        self.data_collector = DataCollector(face_controller, self.camera_manager)
        
        # Garante que sempre temos um profile_manager disponível
        if profile_manager is None:
            from user_profile_manager import UserProfileManager
            profile_manager = UserProfileManager()
            
        self.config_manager = ConfigManager(profile_manager)

    def run_calibration(self, calibrate_ear: bool = True) -> CalibrationResults:
        """Executa o processo completo de calibração com interface visual."""
        logger.info("=== INICIANDO CALIBRAÇÃO COM INTERFACE VISUAL ===")
        
        # Mostrar janela de boas-vindas
        self._show_welcome_screen()
        
        results = CalibrationResults()
        
        try:
            if calibrate_ear:
                results.ear_threshold = self._calibrate_ear()
            
            results.success = results.ear_threshold is not None
            
            if results.success:
                results.message = "Calibração concluída com sucesso"
                self.config_manager.save_calibration_results(results)
                logger.info("=== CALIBRAÇÃO FINALIZADA COM SUCESSO ===")
                self._show_success_screen(results)
            else:
                results.message = "Falha na calibração - dados insuficientes"
                logger.warning("=== CALIBRAÇÃO FALHOU ===")
                self._show_error_screen()
        
        except Exception as e:
            logger.error(f"Erro durante calibração: {e}")
            results.success = False
            results.message = f"Erro: {str(e)}"
            self._show_error_screen()
        
        return results
    
    def _show_welcome_screen(self):
        """Mostra tela de boas-vindas com explicação completa do processo."""
        img = np.zeros((600, 800, 3), dtype=np.uint8)
        img[:] = (50, 50, 50)
        
        # Título principal
        cv2.putText(img, "BEM-VINDO A CALIBRACAO DO PISCK & CLICK", (80, 60),
                    cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 255), 2)
        
        # Linha decorativa
        cv2.line(img, (50, 80), (750, 80), (0, 255, 255), 2)
        
        # Explicação do processo
        instructions = [
            "Este processo ira calibrar o sistema para seus olhos.",
            "Havera 2 fases principais:",
            "",
            "FASE 1: Mantenha os olhos ABERTOS olhando para a camera",
            "        (5 segundos - para medir olhos abertos)",
            "",
            "FASE 2: Pisque NORMALMENTE como no dia a dia",
            "        (8-10 segundos - para medir piscadas naturais)",
            "",
            "IMPORTANTE:",
            "• Mantenha boa iluminacao no rosto",
            "• Posicione-se centralizado na camera",
            "• Siga as instrucoes que aparecerao na tela",
            "• Pressione 'Q' ou ESC para cancelar a qualquer momento",
            "",
            "Pressione ESPACO para iniciar ou ESC para sair"
        ]
        
        y_start = 120
        for instruction in instructions:
            if instruction == "":
                y_start += 15
                continue
                
            color = (255, 255, 255)
            font_size = 0.6
            thickness = 1
            
            if "FASE" in instruction:
                color = (0, 255, 0)
                font_size = 0.7
                thickness = 2
            elif "IMPORTANTE:" in instruction:
                color = (0, 255, 255)
                font_size = 0.7
                thickness = 2
            elif instruction.startswith("•"):
                color = (255, 255, 0)
            elif "Pressione" in instruction:
                color = (255, 255, 0)
                font_size = 0.7
                thickness = 2
                
            cv2.putText(img, instruction, (70, y_start),
                       cv2.FONT_HERSHEY_SIMPLEX, font_size, color, thickness)
            y_start += 30
        
        cv2.namedWindow("Calibração - Bem-vindo", cv2.WINDOW_NORMAL)
        cv2.moveWindow("Calibração - Bem-vindo", 200, 50)
        cv2.resizeWindow("Calibração - Bem-vindo", 800, 600)
        cv2.imshow("Calibração - Bem-vindo", img)
        
        # Aguarda input do usuário
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):  # Espaço para continuar
                break
            elif key == 27:  # ESC para sair
                cv2.destroyWindow("Calibração - Bem-vindo")
                raise KeyboardInterrupt("Calibração cancelada pelo usuário")
        
        cv2.destroyWindow("Calibração - Bem-vindo")
    
    def _show_success_screen(self, results: CalibrationResults):
        """Mostra tela de sucesso."""
        img = np.zeros((400, 600, 3), dtype=np.uint8)
        img[:] = (0, 50, 0)  # Verde escuro
        
        cv2.putText(img, "CALIBRACAO CONCLUIDA!", (100, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        cv2.putText(img, f"Limiar EAR: {results.ear_threshold:.3f}", (150, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(img, "Configuracoes salvas!", (150, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 1)
        cv2.putText(img, "Pressione qualquer tecla para fechar", (80, 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        cv2.namedWindow("Calibração - Sucesso", cv2.WINDOW_NORMAL)
        cv2.moveWindow("Calibração - Sucesso", 300, 150)
        cv2.imshow("Calibração - Sucesso", img)
        
        cv2.waitKey(3000)  # Aguardar 3 segundos ou tecla
        cv2.destroyWindow("Calibração - Sucesso")
    
    def _show_error_screen(self):
        """Mostra tela de erro."""
        img = np.zeros((400, 600, 3), dtype=np.uint8)
        img[:] = (0, 0, 50)  # Azul escuro
        
        cv2.putText(img, "ERRO NA CALIBRACAO", (120, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        cv2.putText(img, "Tente novamente", (180, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(img, "Verifique iluminacao e posicao", (80, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
        cv2.putText(img, "Pressione qualquer tecla para fechar", (80, 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        cv2.namedWindow("Calibração - Erro", cv2.WINDOW_NORMAL)
        cv2.moveWindow("Calibração - Erro", 300, 150)
        cv2.imshow("Calibração - Erro", img)
        
        cv2.waitKey(3000)  # Aguardar 3 segundos ou tecla
        cv2.destroyWindow("Calibração - Erro")

    def _calibrate_ear(self) -> Optional[float]:
        """Calibra o limiar EAR."""
        logger.info("--- Calibração de Piscada ---")

        # Coleta dados com olhos abertos
        logger.info("FASE 1: Mantenha os olhos bem abertos e olhe para a câmera.")
        time.sleep(3)
        open_left, open_right = self.data_collector.collect_ear_data(
            5, "FASE 1: Mantenha os olhos ABERTOS e olhe para a camera"
        )

        # Coleta dados piscando normalmente
        logger.info("\nFASE 2: Agora pisque normalmente como faria no dia a dia.")
        time.sleep(2)
        blink_left, blink_right = self.data_collector.collect_ear_data(
            self.config.ear_collection_duration, "FASE 2: Pisque NORMALMENTE como no dia a dia"
        )

        # Combina todos os dados
        all_open = open_left + open_right
        all_blink = blink_left + blink_right

        return CalibrationAlgorithm.calibrate_ear_threshold(
            all_open, all_blink, self.config
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
            image.flags.writeable = False
            return self.face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        def calculate_ear(self, eye_landmarks, image_shape):
            """Calcula EAR usando a mesma lógica da aplicação principal."""
            coords_points = np.array(
                [(int(landmark.x * image_shape[1]), int(landmark.y * image_shape[0])) for landmark in eye_landmarks]
            )
            p1, p2, p3, p4, p5, p6 = coords_points
            vertical_dist1 = math.dist(p2, p6)
            vertical_dist2 = math.dist(p3, p5)
            horizontal_dist = math.dist(p1, p4)
            if horizontal_dist == 0:
                return 0.0
            return (vertical_dist1 + vertical_dist2) / (2.0 * horizontal_dist)

        def close(self):
            """Libera recursos do FaceMesh."""
            self.face_mesh.close()

    print("="*60)
    print("🎨 MÓDULO DE CALIBRAÇÃO - EXECUÇÃO DIRETA")
    print("="*60)
    print("📹 Iniciando calibração com interface visual melhorada...")
    print("   • Janela ampla (1000x750)")
    print("   • Instruções claras e destacadas")
    print("   • Interface visual aprimorada")
    print()
    
    controller = MockFaceController()
    try:
        # Configuração de calibração
        config = CalibrationConfig(
            ear_collection_duration=8,
            min_data_points=30,
            ear_percentile_threshold=25.0
        )
        
        # Criar e executar módulo de calibração
        calibration_module = CalibrationModule(controller, config=config)
        results = calibration_module.run_calibration()
        
        # Mostrar resultados
        print()
        print("="*60)
        print("📊 RESULTADOS DA CALIBRAÇÃO DIRETA")
        print("="*60)
        print(f"✅ Sucesso: {results.success}")
        print(f"📝 Mensagem: {results.message}")
        if results.ear_threshold:
            print(f"👁️  Limiar EAR: {results.ear_threshold:.3f}")
        print()
        
        if results.success:
            print("🎉 CALIBRAÇÃO EXECUTADA DIRETAMENTE COM SUCESSO!")
        else:
            print("❌ Falha na calibração direta")
            
    except Exception as e:
        print(f"❌ Erro durante execução direta: {e}")
        import traceback
        traceback.print_exc()
    finally:
        controller.close()
        print("\n🏁 Execução direta finalizada")
