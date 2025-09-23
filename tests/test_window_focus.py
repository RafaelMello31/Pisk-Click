#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico para problemas de foco e visibilidade de janelas OpenCV no Windows.
"""

import cv2
import numpy as np
import time
import sys
import os

def test_window_visibility():
    """Testa visibilidade e foco das janelas OpenCV."""
    print("=== Teste de Visibilidade de Janelas OpenCV ===")
    
    # Criar uma imagem colorida e chamativa
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    
    # Fundo colorido
    img[:] = (50, 50, 50)  # Cinza escuro
    
    # Retângulo vermelho grande
    cv2.rectangle(img, (50, 50), (550, 350), (0, 0, 255), -1)
    
    # Texto grande e visível
    cv2.putText(img, "JANELA DE TESTE", (100, 150), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    cv2.putText(img, "SE VOCE VE ISSO", (120, 200), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    cv2.putText(img, "AS JANELAS FUNCIONAM!", (80, 250), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    cv2.putText(img, "Pressione qualquer tecla", (150, 300), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    
    window_name = "TESTE DE VISIBILIDADE"
    
    try:
        # Criar janela com configurações específicas
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        # Tentar diferentes posições e tamanhos
        positions = [(100, 100), (200, 200), (0, 0), (300, 150)]
        
        for i, (x, y) in enumerate(positions):
            print(f"\nTentativa {i+1}: Posição ({x}, {y})")
            
            # Mover janela
            cv2.moveWindow(window_name, x, y)
            
            # Redimensionar
            cv2.resizeWindow(window_name, 600, 400)
            
            # Mostrar imagem
            cv2.imshow(window_name, img)
            
            print(f"Janela criada na posição ({x}, {y})")
            print("Você deveria ver uma janela vermelha com texto branco.")
            print("Aguardando 3 segundos ou pressione qualquer tecla...")
            
            # Aguardar resposta
            key = cv2.waitKey(3000)
            
            if key != -1:
                print(f"✅ Tecla detectada: {key}")
                print("✅ JANELA ESTÁ VISÍVEL E FUNCIONANDO!")
                cv2.destroyWindow(window_name)
                return True
            else:
                print("⏳ Nenhuma tecla pressionada, tentando próxima posição...")
        
        print("\n❌ Nenhuma janela foi visível em nenhuma posição.")
        cv2.destroyWindow(window_name)
        return False
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        return False

def test_fullscreen_window():
    """Testa janela em tela cheia."""
    print("\n=== Teste de Janela em Tela Cheia ===")
    
    try:
        # Criar imagem para tela cheia
        img = np.zeros((768, 1024, 3), dtype=np.uint8)
        img[:] = (0, 100, 0)  # Verde escuro
        
        # Texto grande
        cv2.putText(img, "TELA CHEIA", (300, 300), 
                    cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 5)
        cv2.putText(img, "Pressione ESC para sair", (250, 400), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        
        window_name = "TESTE TELA CHEIA"
        
        # Criar janela em tela cheia
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        cv2.imshow(window_name, img)
        
        print("Janela em tela cheia criada.")
        print("Você deveria ver uma tela verde com texto branco.")
        print("Pressione ESC para sair ou aguarde 5 segundos...")
        
        key = cv2.waitKey(5000)
        
        cv2.destroyWindow(window_name)
        
        if key == 27:  # ESC
            print("✅ ESC detectado - janela em tela cheia funcionou!")
            return True
        else:
            print("⏳ Timeout - janela pode não estar visível")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de tela cheia: {e}")
        return False

def test_multiple_windows():
    """Testa múltiplas janelas simultâneas."""
    print("\n=== Teste de Múltiplas Janelas ===")
    
    try:
        windows = []
        
        for i in range(3):
            # Criar imagem única para cada janela
            img = np.zeros((200, 300, 3), dtype=np.uint8)
            color = [(255, 0, 0), (0, 255, 0), (0, 0, 255)][i]
            img[:] = color
            
            cv2.putText(img, f"JANELA {i+1}", (80, 100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            window_name = f"Janela_{i+1}"
            windows.append((window_name, img))
            
            # Criar e posicionar janela
            cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
            cv2.moveWindow(window_name, 100 + i*320, 100 + i*50)
            cv2.imshow(window_name, img)
        
        print("3 janelas coloridas criadas (vermelha, verde, azul)")
        print("Pressione qualquer tecla ou aguarde 4 segundos...")
        
        key = cv2.waitKey(4000)
        
        # Fechar todas as janelas
        for window_name, _ in windows:
            cv2.destroyWindow(window_name)
        
        if key != -1:
            print(f"✅ Tecla detectada: {key} - múltiplas janelas funcionaram!")
            return True
        else:
            print("⏳ Timeout - janelas podem não estar visíveis")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de múltiplas janelas: {e}")
        return False

def check_system_info():
    """Verifica informações do sistema que podem afetar OpenCV."""
    print("\n=== Informações do Sistema ===")
    
    print(f"Sistema Operacional: {sys.platform}")
    print(f"Python: {sys.version}")
    print(f"OpenCV: {cv2.__version__}")
    
    # Verificar variáveis de ambiente relevantes
    env_vars = ['DISPLAY', 'WAYLAND_DISPLAY', 'XDG_SESSION_TYPE']
    for var in env_vars:
        value = os.environ.get(var, 'Não definida')
        print(f"{var}: {value}")
    
    # Verificar backends disponíveis
    print("\nBackends de vídeo disponíveis:")
    backends = [
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Microsoft Media Foundation"),
        (cv2.CAP_V4L2, "Video4Linux2"),
    ]
    
    for backend_id, name in backends:
        try:
            cap = cv2.VideoCapture(0, backend_id)
            if cap.isOpened():
                print(f"  ✅ {name}")
                cap.release()
            else:
                print(f"  ❌ {name}")
        except:
            print(f"  ❌ {name} (erro)")

def main():
    """Função principal de diagnóstico."""
    print("=== DIAGNÓSTICO COMPLETO DE VISIBILIDADE DE JANELAS ===")
    print("Este teste verifica se as janelas OpenCV estão aparecendo corretamente.")
    print("\nSe você NÃO vir nenhuma janela durante os testes,")
    print("isso explica por que o módulo de calibração não mostra interface.")
    
    check_system_info()
    
    # Executar testes
    test1 = test_window_visibility()
    test2 = test_fullscreen_window()
    test3 = test_multiple_windows()
    
    print("\n" + "="*60)
    print("RESULTADOS FINAIS")
    print("="*60)
    print(f"Janelas normais: {'✅ FUNCIONAM' if test1 else '❌ NÃO FUNCIONAM'}")
    print(f"Janela tela cheia: {'✅ FUNCIONA' if test2 else '❌ NÃO FUNCIONA'}")
    print(f"Múltiplas janelas: {'✅ FUNCIONAM' if test3 else '❌ NÃO FUNCIONAM'}")
    
    if not any([test1, test2, test3]):
        print("\n🚨 PROBLEMA IDENTIFICADO:")
        print("As janelas OpenCV NÃO estão aparecendo no seu sistema!")
        print("\nPossíveis soluções:")
        print("1. Verifique se há outras janelas abertas cobrindo as janelas OpenCV")
        print("2. Tente Alt+Tab para ver se as janelas estão minimizadas")
        print("3. Verifique configurações de múltiplos monitores")
        print("4. Reinstale OpenCV: pip uninstall opencv-python && pip install opencv-python")
        print("5. Teste em outro ambiente Python")
        print("6. Verifique se não há software de captura de tela interferindo")
    elif test1 or test2 or test3:
        print("\n✅ JANELAS FUNCIONAM PARCIAL OU TOTALMENTE")
        print("O problema do módulo de calibração pode ser:")
        print("1. Janelas sendo criadas fora da área visível")
        print("2. Janelas sendo fechadas muito rapidamente")
        print("3. Problema específico na lógica do módulo")
        print("4. Conflito com MediaPipe ou outras bibliotecas")
    
    # Limpeza final
    cv2.destroyAllWindows()
    
    print("\nTeste concluído. Pressione Enter para finalizar...")
    input()

if __name__ == "__main__":
    main()