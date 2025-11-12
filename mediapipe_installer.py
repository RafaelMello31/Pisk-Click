#!/usr/bin/env python3
"""
Sistema inteligente de instalação do MediaPipe
Tenta múltiplas versões e estratégias até encontrar uma que funcione
"""

import subprocess
import sys
import os
import platform
from typing import List, Tuple, Optional

class MediaPipeInstaller:
    """Instalador inteligente do MediaPipe com fallback automático"""
    
    # Lista de versões do MediaPipe em ordem de prioridade (mais estável primeiro)
    MEDIAPIPE_VERSIONS = [
        "0.10.21",  # Versão que funciona no seu sistema
        "0.10.20",
        "0.10.19", 
        "0.10.18",
        "0.10.17",
        "0.10.16",
        "0.10.15",
        "0.10.14",
        "0.10.13",
        "0.10.11",
        "0.10.9",
        "0.10.7",
        "0.10.5",
        "0.10.3",
        "0.10.1",
        "0.10.0"
    ]
    
    def __init__(self):
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.system_info = self._get_system_info()
        
    def _get_system_info(self) -> dict:
        """Coleta informações do sistema para debug"""
        return {
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "python_version": self.python_version,
            "python_executable": sys.executable
        }
    
    def _run_pip_command(self, command: List[str]) -> Tuple[bool, str]:
        """Executa comando pip e retorna sucesso/falha com output"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos timeout
                check=False
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            return success, output
            
        except subprocess.TimeoutExpired:
            return False, "Timeout: Instalação demorou mais de 5 minutos"
        except Exception as e:
            return False, f"Erro na execução: {str(e)}"
    
    def _test_mediapipe_import(self) -> Tuple[bool, str]:
        """Testa se o MediaPipe pode ser importado"""
        try:
            result = subprocess.run([
                sys.executable, "-c", 
                "import mediapipe as mp; print(f'MediaPipe {mp.__version__} OK')"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()
                
        except Exception as e:
            return False, f"Erro no teste: {str(e)}"
    
    def _uninstall_mediapipe(self) -> bool:
        """Remove versão atual do MediaPipe"""
        print("🗑️  Removendo versão atual do MediaPipe...")
        success, output = self._run_pip_command([
            sys.executable, "-m", "pip", "uninstall", "mediapipe", "-y"
        ])
        return success
    
    def install_version(self, version: str) -> Tuple[bool, str]:
        """Tenta instalar uma versão específica do MediaPipe"""
        print(f"📦 Tentando instalar MediaPipe {version}...")
        
        # Comando de instalação
        install_cmd = [
            sys.executable, "-m", "pip", "install", 
            f"mediapipe=={version}",
            "--no-cache-dir",  # Evita cache corrompido
            "--force-reinstall"  # Força reinstalação
        ]
        
        success, output = self._run_pip_command(install_cmd)
        
        if success:
            # Testa se realmente funciona
            import_success, import_output = self._test_mediapipe_import()
            if import_success:
                print(f"✅ MediaPipe {version} instalado e funcionando!")
                return True, import_output
            else:
                print(f"❌ MediaPipe {version} instalado mas não funciona: {import_output}")
                return False, f"Instalação OK mas import falhou: {import_output}"
        else:
            print(f"❌ Falha na instalação do MediaPipe {version}")
            return False, output
    
    def install_with_fallback(self) -> Tuple[bool, str, Optional[str]]:
        """
        Tenta instalar MediaPipe com sistema de fallback
        Retorna: (sucesso, mensagem, versão_instalada)
        """
        print("🚀 Iniciando instalação inteligente do MediaPipe...")
        print(f"🖥️  Sistema: {self.system_info}")
        
        # Primeiro, testa se já está instalado e funcionando
        import_success, import_output = self._test_mediapipe_import()
        if import_success:
            print("✅ MediaPipe já está instalado e funcionando!")
            return True, import_output, "já_instalado"
        
        print("🔄 MediaPipe não está funcionando, iniciando processo de instalação...")
        
        # Remove versão atual se existir
        self._uninstall_mediapipe()
        
        # Tenta cada versão na lista
        for version in self.MEDIAPIPE_VERSIONS:
            print(f"\n🎯 Tentativa {self.MEDIAPIPE_VERSIONS.index(version) + 1}/{len(self.MEDIAPIPE_VERSIONS)}")
            
            success, message = self.install_version(version)
            if success:
                return True, f"MediaPipe {version} instalado com sucesso!", version
            
            print(f"⚠️  Versão {version} falhou, tentando próxima...")
        
        # Se chegou aqui, todas as versões falharam
        error_msg = "❌ ERRO CRÍTICO: Nenhuma versão do MediaPipe funcionou!"
        print(error_msg)
        return False, error_msg, None
    
    def generate_report(self, success: bool, message: str, version: Optional[str]) -> str:
        """Gera relatório detalhado da instalação"""
        report = f"""
=== RELATÓRIO DE INSTALAÇÃO DO MEDIAPIPE ===
Data: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SISTEMA:
- Plataforma: {self.system_info['platform']}
- Arquitetura: {self.system_info['architecture']}
- Python: {self.system_info['python_version']}
- Executável: {self.system_info['python_executable']}

RESULTADO:
- Status: {'✅ SUCESSO' if success else '❌ FALHA'}
- Versão instalada: {version or 'Nenhuma'}
- Mensagem: {message}

VERSÕES TENTADAS: {', '.join(self.MEDIAPIPE_VERSIONS)}
===============================================
"""
        return report

def main():
    """Função principal"""
    installer = MediaPipeInstaller()
    
    print("🎯 INSTALADOR INTELIGENTE DO MEDIAPIPE")
    print("=" * 50)
    
    success, message, version = installer.install_with_fallback()
    
    # Gera relatório
    report = installer.generate_report(success, message, version)
    print(report)
    
    # Salva relatório em arquivo
    try:
        with open("mediapipe_install_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        print("📄 Relatório salvo em: mediapipe_install_report.txt")
    except Exception as e:
        print(f"⚠️  Não foi possível salvar relatório: {e}")
    
    # Retorna código de saída apropriado
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()