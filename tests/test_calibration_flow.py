#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico do fluxo de calibração para identificar onde a interface não aparece.
"""

import cv2
import mediapipe as mp
import time
import logging
import numpy as np
from typing import List, Tuple

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constantes dos landmarks dos olhos
LEFT_EYE_LANDMARKS_IDXS = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
RIGHT_EYE_LANDMARKS_IDXS = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]

class MockCameraManager:
    """Mock do CameraManager para teste."""
    
    def __init__(self):
        self.image_width = 640
        self.image_height = 480
    
    def get_camera(self):
        return MockCameraContext()

class MockCameraContext:
    """Context manager para câmera."""
    
    def __enter__(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Não foi possível abrir a câmera")
        
        # Configurar resolução
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        logger.info("Câmera aberta no context manager")
        return self.cap
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'cap'):
            self.cap.release()
            logger.info("Câmera liberada no context manager")
        cv2.destroyAllWindows()
        logger.info("Janelas OpenCV fechadas")

class MockFaceController:
    """Mock do FaceController."""
    
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        logger.info("FaceController inicializado")
    
    def process_frame(self, image):
        """Processa frame e retorna landmarks."""
        image.flags.writeable = False
        results = self.face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        image.flags.writeable = True
        return results

def calculate_ear(face_landmarks, eye_landmarks_idxs: List[int]) -> float:
    """Calcula o Eye Aspect Ratio (EAR)."""
    try:
        # Pegar coordenadas dos landmarks do olho
        eye_points = []
        for idx in eye_landmarks_idxs:
            landmark = face_landmarks[idx]
            eye_points.append([landmark.x, landmark.y])
        
        eye_points = np.array(eye_points)
        
        # Calcular distâncias verticais
        A = np.linalg.norm(eye_points[1] - eye_points[5])
        B = np.linalg.norm(eye_points[2] - eye_points[4])
        
        # Calcular distância horizontal
        C = np.linalg.norm(eye_points[0] - eye_points[3])
        
        # Calcular EAR
        if C > 0:
            ear = (A + B) / (2.0 * C)
            return ear
        
        return 0.0
        
    except Exception as e:
        logger.warning(f"Erro ao calcular EAR: {e}")
        return 0.0

def draw_countdown(image, countdown_text: str, instruction: str):
    """Desenha interface visual na imagem."""
    height, width = image.shape[:2]
    
    # Criar overlay semi-transparente
    overlay = image.copy()
    cv2.rectangle(overlay, (10, 10), (width - 10, 150), (0, 0, 0), -1)
    image = cv2.addWeighted(image, 0.7, overlay, 0.3, 0)
    
    # Textos
    cv2.putText(image, countdown_text, (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
    cv2.putText(image, instruction, (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(image, "Pressione 'q' para parar", (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
    
    return image

def collect_ear_data_with_debug(duration: int, instruction: str, face_controller, camera_manager) -> Tuple[List[float], List[float]]:
    """Coleta dados EAR com debug detalhado."""
    logger.info(f"=== INICIANDO COLETA: {instruction} ===")
    logger.info(f"Duração: {duration} segundos")
    
    left_ears = []
    right_ears = []
    start_time = time.time()
    frame_count = 0
    
    try:
        with camera_manager.get_camera() as cap:
            logger.info("Context manager da câmera ativo")
            
            # Criar janela explicitamente
            window_name = "Calibração EAR - Debug"
            cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
            cv2.moveWindow(window_name, 100, 100)
            logger.info(f"Janela '{window_name}' criada")
            
            while time.time() - start_time < duration:
                success, image = cap.read()
                
                if not success:
                    logger.warning("Falha ao capturar frame")
                    continue
                
                frame_count += 1
                
                # Espelhar imagem
                image = cv2.flip(image, 1)
                
                # Processar com MediaPipe
                results = face_controller.process_frame(image)
                
                # Calcular EAR se face detectada
                if results and results.multi_face_landmarks:
                    face_landmarks = results.multi_face_landmarks[0].landmark
                    
                    left_ear = calculate_ear(face_landmarks, LEFT_EYE_LANDMARKS_IDXS)
                    right_ear = calculate_ear(face_landmarks, RIGHT_EYE_LANDMARKS_IDXS)
                    
                    if left_ear > 0:
                        left_ears.append(left_ear)
                    if right_ear > 0:
                        right_ears.append(right_ear)
                    
                    # Debug info no frame
                    cv2.putText(image, f"L_EAR: {left_ear:.3f}", (10, 200),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                    cv2.putText(image, f"R_EAR: {right_ear:.3f}", (10, 220),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                    cv2.putText(image, "Face detectada!", (10, 180),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                else:
                    cv2.putText(image, "Nenhuma face detectada", (10, 180),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # Interface visual
                remaining_time = int(duration - (time.time() - start_time))
                countdown_text = f"Tempo: {remaining_time}s"
                
                image = draw_countdown(image, countdown_text, instruction)
                
                # Adicionar info de debug
                cv2.putText(image, f"Frame: {frame_count}", (10, 250),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(image, f"Dados coletados: L={len(left_ears)}, R={len(right_ears)}", (10, 270),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # PONTO CRÍTICO: Mostrar a janela
                logger.debug(f"Mostrando frame {frame_count} na janela '{window_name}'")
                cv2.imshow(window_name, image)
                
                # Verificar teclas
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    logger.info("Usuário pressionou 'q' - parando coleta")
                    break
                elif key != 255:
                    logger.info(f"Tecla pressionada: {key}")
            
            logger.info(f"Coleta finalizada - {frame_count} frames processados")
            
    except Exception as e:
        logger.error(f"Erro durante coleta: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cv2.destroyAllWindows()
        logger.info("Janelas fechadas")
    
    logger.info(f"Dados coletados: {len(left_ears)} left_ears, {len(right_ears)} right_ears")
    return left_ears, right_ears

def test_calibration_flow():
    """Testa o fluxo completo de calibração com debug."""
    logger.info("=== TESTE DO FLUXO DE CALIBRAÇÃO ===")
    
    # Inicializar componentes
    face_controller = MockFaceController()
    camera_manager = MockCameraManager()
    
    try:
        # Simular o fluxo do _calibrate_ear
        logger.info("--- Fase 1: Olhos Abertos ---")
        logger.info("Mantenha os olhos bem abertos e olhe para a câmera.")
        time.sleep(2)  # Reduzido para teste
        
        open_left, open_right = collect_ear_data_with_debug(
            3, "Mantenha os olhos abertos", face_controller, camera_manager
        )
        
        logger.info(f"Dados olhos abertos coletados: L={len(open_left)}, R={len(open_right)}")
        
        # Pausa entre fases
        logger.info("\n--- Fase 2: Piscadas Normais ---")
        logger.info("Agora pisque normalmente.")
        time.sleep(1)
        
        blink_left, blink_right = collect_ear_data_with_debug(
            5, "Pisque normalmente", face_controller, camera_manager
        )
        
        logger.info(f"Dados piscadas coletados: L={len(blink_left)}, R={len(blink_right)}")
        
        # Resultados
        total_open = len(open_left) + len(open_right)
        total_blink = len(blink_left) + len(blink_right)
        
        logger.info("\n=== RESULTADOS DO TESTE ===")
        logger.info(f"Total de dados coletados: {total_open + total_blink}")
        logger.info(f"Olhos abertos: {total_open} amostras")
        logger.info(f"Piscadas: {total_blink} amostras")
        
        if total_open > 0 and total_blink > 0:
            logger.info("✅ Coleta de dados bem-sucedida!")
            
            # Calcular estatísticas básicas
            if open_left and open_right:
                avg_open = np.mean(open_left + open_right)
                logger.info(f"EAR médio (olhos abertos): {avg_open:.3f}")
            
            if blink_left and blink_right:
                avg_blink = np.mean(blink_left + blink_right)
                logger.info(f"EAR médio (piscadas): {avg_blink:.3f}")
                
            return True
        else:
            logger.warning("❌ Falha na coleta de dados")
            return False
            
    except Exception as e:
        logger.error(f"Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Limpeza final
        cv2.destroyAllWindows()
        if hasattr(face_controller, 'face_mesh'):
            face_controller.face_mesh.close()

def main():
    """Função principal."""
    print("=== TESTE DE DEBUG DO FLUXO DE CALIBRAÇÃO ===")
    print("Este teste simula exatamente o que o calibration_module faz.")
    print("Você DEVE ver janelas com sua imagem e instruções.")
    print("\nIniciando em 3 segundos...")
    
    time.sleep(3)
    
    success = test_calibration_flow()
    
    print("\n=== CONCLUSÃO ===")
    if success:
        print("✅ O fluxo de calibração funcionou corretamente!")
        print("Se você VIU as janelas, o problema não está no código básico.")
        print("Se você NÃO VIU as janelas, há um problema específico.")
    else:
        print("❌ Houve problemas no fluxo de calibração.")
        print("Verifique os logs acima para mais detalhes.")

if __name__ == "__main__":
    main()