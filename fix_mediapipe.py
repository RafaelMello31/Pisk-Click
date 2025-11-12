#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir problemas do MediaPipe no Windows
"""

import sys
import subprocess
import os

def run_command(cmd):
    """Executa comando e retorna resultado."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_mediapipe():
    """Testa se MediaPipe funciona."""
    try:
        import mediapipe as mp
        # Tentar inicializar FaceMesh
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        print("✓ MediaPipe funcionando corretamente!")
        return True
    except Exception as e:
        print(f"✗ MediaPipe com problema: {e}")
        return False

def fix_mediapipe():
    """Tenta corrigir problemas do MediaPipe."""
    print("Tentando corrigir MediaPipe...")
    
    # Configurar variáveis de ambiente
    os.environ['MEDIAPIPE_DISABLE_GPU'] = '1'
    os.environ['GLOG_logtostderr'] = '1'
    os.environ['GLOG_v'] = '0'
    os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
    
    # Versões compatíveis conhecidas
    compatible_versions = [
        ("mediapipe==0.10.3", "opencv-python==4.8.1.78"),
        ("mediapipe==0.10.1", "opencv-python==4.8.0.76"),
        ("mediapipe==0.9.3.0", "opencv-python==4.7.1.72"),
    ]
    
    for mp_version, cv_version in compatible_versions:
        print(f"\nTentando: {mp_version} + {cv_version}")
        
        # Desinstalar versões atuais
        print("Removendo versões atuais...")
        run_command("python -m pip uninstall -y mediapipe opencv-python")
        
        # Instalar versões específicas
        print("Instalando versões compatíveis...")
        success1, _, _ = run_command(f"python -m pip install --no-cache-dir {cv_version}")
        success2, _, _ = run_command(f"python -m pip install --no-cache-dir {mp_version}")
        
        if success1 and success2:
            print("Instalação concluída, testando...")
            if test_mediapipe():
                print(f"✓ Sucesso com {mp_version}!")
                return True
        
        print("✗ Esta combinação não funcionou...")
    
    print("✗ Não foi possível corrigir o MediaPipe automaticamente.")
    return False

def main():
    """Função principal."""
    print("=" * 60)
    print("    CORREÇÃO DO MEDIAPIPE - PISK & CLICK")
    print("=" * 60)
    
    # Testar primeiro
    if test_mediapipe():
        print("MediaPipe já está funcionando!")
        return
    
    # Tentar corrigir
    if fix_mediapipe():
        print("\n✓ MediaPipe corrigido com sucesso!")
    else:
        print("\n✗ Não foi possível corrigir automaticamente.")
        print("\nTente instalar manualmente:")
        print("1. pip uninstall mediapipe opencv-python")
        print("2. pip install opencv-python==4.8.1.78")
        print("3. pip install mediapipe==0.10.3")
    
    input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()