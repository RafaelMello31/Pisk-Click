#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico para problemas de exibição de janelas OpenCV no Windows.
"""

import cv2
import numpy as np
import time
import sys

def test_opencv_backends():
    """Testa diferentes backends do OpenCV."""
    print("=== Teste de Backends OpenCV ===")
    print(f"Versão OpenCV: {cv2.__version__}")
    print(f"Backends disponíveis: {cv2.getBuildInformation()}")
    
    # Listar backends de vídeo disponíveis
    backends = [
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Microsoft Media Foundation"),
        (cv2.CAP_V4L2, "Video4Linux2"),
        (cv2.CAP_ANY, "Qualquer")
    ]
    
    for backend_id, backend_name in backends:
        try:
            cap = cv2.VideoCapture(0, backend_id)
            if cap.isOpened():
                print(f"✓ {backend_name} (ID: {backend_id}) - Funciona")
                cap.release()
            else:
                print(f"✗ {backend_name} (ID: {backend_id}) - Não funciona")
        except Exception as e:
            print(f"✗ {backend_name} (ID: {backend_id}) - Erro: {e}")

def test_window_creation():
    """Testa criação de janelas com diferentes configurações."""
    print("\n=== Teste de Criação de Janelas ===")
    
    # Teste 1: Janela simples
    print("Teste 1: Janela simples com imagem estática")
    img = np.zeros((300, 400, 3), dtype=np.uint8)
    cv2.putText(img, "Teste de Janela", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    try:
        cv2.namedWindow("Teste Simples", cv2.WINDOW_AUTOSIZE)
        cv2.imshow("Teste Simples", img)
        print("Janela criada. Aguardando 3 segundos...")
        
        # Aguardar e verificar se a janela responde
        for i in range(30):  # 3 segundos
            key = cv2.waitKey(100)
            if key != -1:
                print(f"Tecla detectada: {key}")
                break
        
        cv2.destroyWindow("Teste Simples")
        print("✓ Janela simples funcionou")
        return True
        
    except Exception as e:
        print(f"✗ Erro na janela simples: {e}")
        return False

def test_camera_window():
    """Testa janela com câmera usando diferentes configurações."""
    print("\n=== Teste de Janela com Câmera ===")
    
    # Tentar diferentes backends
    backends_to_try = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    
    for backend in backends_to_try:
        print(f"Tentando backend: {backend}")
        
        try:
            cap = cv2.VideoCapture(0, backend)
            
            if not cap.isOpened():
                print(f"✗ Não foi possível abrir câmera com backend {backend}")
                continue
                
            # Configurar resolução
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            print(f"Câmera aberta com backend {backend}")
            print("Tentando exibir frames...")
            
            # Criar janela com configurações específicas
            window_name = f"Camera Test - Backend {backend}"
            cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
            
            # Tentar mover a janela para uma posição específica
            cv2.moveWindow(window_name, 100, 100)
            
            frame_count = 0
            start_time = time.time()
            
            while time.time() - start_time < 5:  # 5 segundos
                ret, frame = cap.read()
                
                if not ret:
                    print("Falha ao capturar frame")
                    continue
                    
                frame_count += 1
                
                # Adicionar informações no frame
                cv2.putText(frame, f"Frame: {frame_count}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Backend: {backend}", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                cv2.putText(frame, "Pressione ESC para sair", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Mostrar frame
                cv2.imshow(window_name, frame)
                
                # Verificar teclas
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    print("ESC pressionado")
                    break
                elif key != 255:
                    print(f"Tecla pressionada: {key}")
            
            cap.release()
            cv2.destroyWindow(window_name)
            
            print(f"✓ Teste com backend {backend} concluído - {frame_count} frames")
            return True
            
        except Exception as e:
            print(f"✗ Erro com backend {backend}: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                cap.release()
                cv2.destroyAllWindows()
            except:
                pass
    
    return False

def test_window_properties():
    """Testa propriedades específicas das janelas."""
    print("\n=== Teste de Propriedades das Janelas ===")
    
    # Verificar se o sistema suporta GUI
    try:
        # Tentar criar uma janela invisível primeiro
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Diferentes tipos de janela
        window_flags = [
            (cv2.WINDOW_AUTOSIZE, "AUTOSIZE"),
            (cv2.WINDOW_NORMAL, "NORMAL"),
            (cv2.WINDOW_OPENGL, "OPENGL"),
        ]
        
        for flag, name in window_flags:
            try:
                window_name = f"Test_{name}"
                cv2.namedWindow(window_name, flag)
                cv2.imshow(window_name, test_img)
                cv2.waitKey(100)
                cv2.destroyWindow(window_name)
                print(f"✓ Janela {name} funcionou")
            except Exception as e:
                print(f"✗ Janela {name} falhou: {e}")
                
    except Exception as e:
        print(f"✗ Erro geral nas propriedades: {e}")

def main():
    """Função principal de diagnóstico."""
    print("=== Diagnóstico Completo de Exibição OpenCV ===")
    print(f"Sistema: {sys.platform}")
    print(f"Python: {sys.version}")
    
    # Executar todos os testes
    test_opencv_backends()
    
    window_simple_ok = test_window_creation()
    test_window_properties()
    camera_window_ok = test_camera_window()
    
    print("\n=== Resumo dos Resultados ===")
    print(f"Janela simples: {'✓ OK' if window_simple_ok else '✗ FALHOU'}")
    print(f"Janela com câmera: {'✓ OK' if camera_window_ok else '✗ FALHOU'}")
    
    if not window_simple_ok:
        print("\n❌ PROBLEMA CRÍTICO: Janelas OpenCV não estão funcionando!")
        print("Possíveis causas:")
        print("- OpenCV compilado sem suporte GUI")
        print("- Problema com drivers de vídeo")
        print("- Execução em ambiente sem display (SSH, etc.)")
        print("- Conflito com outros softwares")
    elif not camera_window_ok:
        print("\n⚠️ PROBLEMA PARCIAL: Janelas funcionam, mas câmera não")
        print("Possíveis causas:")
        print("- Câmera em uso por outro programa")
        print("- Drivers de câmera desatualizados")
        print("- Permissões de acesso à câmera")
    else:
        print("\n✅ TUDO FUNCIONANDO: OpenCV e câmera OK!")
        print("O problema deve estar na lógica específica do seu código.")
    
    # Limpeza final
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()