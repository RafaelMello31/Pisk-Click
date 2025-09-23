#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para o módulo de calibração.
Testa se a interface visual está funcionando corretamente.
"""

import sys
import logging
from calibration_module import CalibrationModule, CalibrationConfig

# Configurar logging para ver as mensagens
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Mock do FaceController para teste
class MockFaceController:
    """Mock do FaceController para testes."""
    
    def __init__(self):
        import mediapipe as mp
        import cv2
        
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
    def process_frame(self, image):
        """Processa frame e retorna landmarks."""
        import cv2
        image.flags.writeable = False
        return self.face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
    def calculate_ear(self, eye_landmarks, image_shape):
        """Calcula EAR usando a mesma lógica da aplicação principal."""
        import numpy as np
        import math
        
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

def main():
    """Função principal de teste."""
    print("=== Teste do Módulo de Calibração ===")
    print("Este teste irá abrir a interface de calibração.")
    print("Você deve ver uma janela com instruções visuais.")
    print("Pressione 'q' para sair durante a calibração.")
    print("\nIniciando em 3 segundos...")
    
    import time
    time.sleep(3)
    
    # Criar o controlador mock
    face_controller = MockFaceController()
    
    try:
        # Configuração de calibração com tempos reduzidos para teste
        config = CalibrationConfig(
            ear_collection_duration=5,  # 5 segundos em vez de 10
            min_data_points=10,  # Menos pontos para teste
        )
        
        # Criar módulo de calibração
        calibration_module = CalibrationModule(face_controller, config=config)
        
        # Executar calibração
        logger.info("Iniciando calibração...")
        results = calibration_module.run_calibration()
        
        # Mostrar resultados
        print("\n=== Resultados da Calibração ===")
        print(f"Sucesso: {results.success}")
        print(f"Mensagem: {results.message}")
        if results.ear_threshold:
            print(f"Limiar EAR calculado: {results.ear_threshold:.3f}")
            
    except KeyboardInterrupt:
        print("\nCalibração interrompida pelo usuário.")
    except Exception as e:
        print(f"\nErro durante a calibração: {e}")
        import traceback
        traceback.print_exc()
    finally:
        face_controller.close()
        print("\nTeste finalizado.")

if __name__ == "__main__":
    main()