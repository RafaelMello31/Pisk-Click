#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug específico do módulo de calibração.
Testa cada etapa individualmente.
"""

import cv2
import mediapipe as mp
import time
import numpy as np
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def test_camera_with_mediapipe():
    """Testa câmera com MediaPipe e interface visual."""
    print("=== Teste: Câmera + MediaPipe + Interface Visual ===")
    
    # Inicializar MediaPipe
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # Abrir câmera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERRO: Não foi possível abrir a câmera!")
        return False
        
    print("Câmera aberta. Iniciando loop de captura...")
    print("Você deve ver uma janela com sua imagem e instruções.")
    print("Pressione 'q' para sair.")
    
    start_time = time.time()
    duration = 10  # 10 segundos de teste
    
    try:
        while time.time() - start_time < duration:
            success, image = cap.read()
            
            if not success:
                print("Falha ao capturar frame")
                continue
                
            # Espelhar imagem
            image = cv2.flip(image, 1)
            
            # Processar com MediaPipe
            image.flags.writeable = False
            results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            image.flags.writeable = True
            
            # Desenhar interface
            remaining_time = int(duration - (time.time() - start_time))
            
            # Fundo semi-transparente
            height, width = image.shape[:2]
            overlay = image.copy()
            cv2.rectangle(overlay, (10, 10), (width - 10, 120), (0, 0, 0), -1)
            image = cv2.addWeighted(image, 0.7, overlay, 0.3, 0)
            
            # Textos
            cv2.putText(image, f"Tempo: {remaining_time}s", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(image, "Teste de Interface Visual", (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(image, "Pressione 'q' para parar", (20, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # Status do MediaPipe
            if results and results.multi_face_landmarks:
                cv2.putText(image, "Face detectada!", (width - 200, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                cv2.putText(image, "Nenhuma face", (width - 200, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Mostrar janela
            cv2.imshow("Debug Calibração", image)
            
            # Verificar tecla
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Saída solicitada pelo usuário")
                break
            elif key != 255:  # Alguma tecla foi pressionada
                print(f"Tecla pressionada: {key}")
                
        print("Teste concluído!")
        return True
        
    except Exception as e:
        print(f"Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        cap.release()
        cv2.destroyAllWindows()
        face_mesh.close()
        print("Recursos liberados.")

def test_context_manager():
    """Testa o context manager do CameraManager."""
    print("\n=== Teste: Context Manager ===")
    
    from calibration_module import CameraManager
    
    camera_manager = CameraManager()
    
    try:
        with camera_manager.get_camera() as cap:
            print("Context manager funcionando")
            print(f"Resolução: {camera_manager.image_width}x{camera_manager.image_height}")
            
            # Capturar alguns frames
            for i in range(5):
                ret, frame = cap.read()
                if ret:
                    print(f"Frame {i+1} capturado: {frame.shape}")
                    
                    # Mostrar frame por 1 segundo
                    cv2.imshow("Context Manager Test", frame)
                    cv2.waitKey(1000)
                else:
                    print(f"Falha ao capturar frame {i+1}")
                    
        print("Context manager finalizado com sucesso")
        return True
        
    except Exception as e:
        print(f"Erro no context manager: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cv2.destroyAllWindows()

def main():
    """Função principal de debug."""
    print("=== Debug do Módulo de Calibração ===")
    print("Este script testa cada componente individualmente.")
    print("\nIniciando testes...\n")
    
    # Teste 1: Câmera + MediaPipe + Interface
    test1_ok = test_camera_with_mediapipe()
    
    # Teste 2: Context Manager
    test2_ok = test_context_manager()
    
    print("\n=== Resultados do Debug ===")
    print(f"Câmera + MediaPipe + Interface: {'✓ OK' if test1_ok else '✗ FALHOU'}")
    print(f"Context Manager: {'✓ OK' if test2_ok else '✗ FALHOU'}")
    
    if test1_ok and test2_ok:
        print("\n✅ Todos os componentes estão funcionando!")
        print("O problema pode estar na lógica específica do módulo de calibração.")
    else:
        print("\n❌ Há problemas nos componentes básicos.")
        print("Verifique os erros acima para mais detalhes.")

if __name__ == "__main__":
    main()