#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples para verificar se o OpenCV consegue abrir janelas no sistema.
"""

import cv2
import numpy as np
import time

def test_opencv_window():
    """Testa se o OpenCV consegue abrir uma janela."""
    print("Testando abertura de janela OpenCV...")
    
    try:
        # Criar uma imagem simples
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Adicionar texto
        cv2.putText(img, "Teste OpenCV - Janela Funcionando!", (50, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img, "Pressione qualquer tecla para fechar", (100, 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        
        # Tentar mostrar a janela
        cv2.imshow("Teste OpenCV", img)
        print("Janela criada. Se você não vê a janela, há um problema com OpenCV.")
        
        # Aguardar tecla por 10 segundos
        key = cv2.waitKey(10000)  # 10 segundos
        
        if key == -1:
            print("Timeout - nenhuma tecla pressionada em 10 segundos")
        else:
            print(f"Tecla pressionada: {key}")
            
        cv2.destroyAllWindows()
        print("Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao testar OpenCV: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_camera_access():
    """Testa se consegue acessar a câmera."""
    print("\nTestando acesso à câmera...")
    
    try:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("ERRO: Não foi possível abrir a câmera!")
            return False
            
        print("Câmera aberta com sucesso!")
        
        # Tentar capturar um frame
        ret, frame = cap.read()
        
        if ret:
            print(f"Frame capturado: {frame.shape}")
            
            # Tentar mostrar o frame
            cv2.imshow("Teste Câmera", frame)
            print("Frame da câmera exibido. Pressione qualquer tecla...")
            cv2.waitKey(3000)  # 3 segundos
            cv2.destroyAllWindows()
        else:
            print("ERRO: Não foi possível capturar frame da câmera!")
            
        cap.release()
        print("Câmera liberada.")
        return ret
        
    except Exception as e:
        print(f"Erro ao testar câmera: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal de teste."""
    print("=== Diagnóstico OpenCV e Câmera ===")
    print(f"Versão OpenCV: {cv2.__version__}")
    
    # Teste 1: Janela simples
    window_ok = test_opencv_window()
    
    # Teste 2: Acesso à câmera
    camera_ok = test_camera_access()
    
    print("\n=== Resultados ===")
    print(f"Janela OpenCV: {'✓ OK' if window_ok else '✗ FALHOU'}")
    print(f"Acesso à câmera: {'✓ OK' if camera_ok else '✗ FALHOU'}")
    
    if not window_ok:
        print("\n⚠️  PROBLEMA: OpenCV não consegue abrir janelas!")
        print("Possíveis causas:")
        print("- Sistema sem interface gráfica (headless)")
        print("- Problemas com drivers de vídeo")
        print("- OpenCV compilado sem suporte GUI")
        
    if not camera_ok:
        print("\n⚠️  PROBLEMA: Não consegue acessar a câmera!")
        print("Possíveis causas:")
        print("- Câmera em uso por outro programa")
        print("- Permissões de câmera negadas")
        print("- Driver da câmera com problema")

if __name__ == "__main__":
    main()