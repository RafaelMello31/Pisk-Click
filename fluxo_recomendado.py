#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fluxo Recomendado para o Pisck & Click

Este script demonstra o fluxo ideal de uso do sistema:
1. Executar calibração
2. Verificar/ajustar configurações via GUI
3. Iniciar programa principal

Este fluxo garante que todas as configurações estejam otimizadas
antes da execução principal do sistema.
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FluxoRecomendado:
    """Gerencia o fluxo recomendado de execução do Pisck & Click."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.calibration_module = self.base_dir / "calibration_module.py"
        self.config_gui = self.base_dir / "config_gui.py"
        self.main_module = self.base_dir / "main.py"
        
    def verificar_arquivos(self):
        """Verifica se todos os arquivos necessários existem."""
        arquivos = {
            "Módulo de Calibração": self.calibration_module,
            "Interface de Configuração": self.config_gui,
            "Programa Principal": self.main_module
        }
        
        arquivos_faltando = []
        for nome, arquivo in arquivos.items():
            if not arquivo.exists():
                arquivos_faltando.append(f"{nome}: {arquivo}")
                
        if arquivos_faltando:
            logger.error("Arquivos não encontrados:")
            for arquivo in arquivos_faltando:
                logger.error(f"  - {arquivo}")
            return False
            
        logger.info("✅ Todos os arquivos necessários foram encontrados")
        return True
    
    def executar_calibracao(self):
        """Executa o módulo de calibração."""
        print("\n" + "="*60)
        print("🎯 ETAPA 1: CALIBRAÇÃO")
        print("="*60)
        print("📹 Iniciando processo de calibração...")
        print("   • A janela de calibração será aberta")
        print("   • Siga as instruções na tela")
        print("   • O limiar EAR será calculado automaticamente")
        print("\n⚠️  IMPORTANTE: Mantenha-se em frente à câmera durante todo o processo")
        
        input("\n🔄 Pressione ENTER para iniciar a calibração...")
        
        try:
            # Executar calibração
            resultado = subprocess.run(
                [sys.executable, str(self.calibration_module)],
                cwd=self.base_dir,
                capture_output=False,  # Permite ver a saída em tempo real
                text=True
            )
            
            if resultado.returncode == 0:
                print("\n✅ Calibração concluída com sucesso!")
                print("📊 Configurações salvas automaticamente")
                return True
            else:
                print(f"\n❌ Erro durante calibração (código: {resultado.returncode})")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao executar calibração: {e}")
            return False
    
    def abrir_config_gui(self):
        """Abre a interface gráfica de configuração."""
        print("\n" + "="*60)
        print("⚙️  ETAPA 2: VERIFICAÇÃO DE CONFIGURAÇÕES")
        print("="*60)
        print("🖥️  Abrindo interface de configuração...")
        print("   • Verifique se os valores estão corretos")
        print("   • Ajuste configurações se necessário")
        print("   • Salve as alterações antes de fechar")
        print("\n💡 DICA: O limiar EAR foi calculado automaticamente na calibração")
        
        input("\n🔄 Pressione ENTER para abrir a interface de configuração...")
        
        try:
            # Executar GUI de configuração
            processo = subprocess.Popen(
                [sys.executable, str(self.config_gui)],
                cwd=self.base_dir
            )
            
            print("\n🖼️  Interface de configuração aberta!")
            print("📝 Aguardando você finalizar as configurações...")
            print("\n⚠️  FECHE a janela de configuração quando terminar")
            
            # Aguardar o processo terminar
            processo.wait()
            
            print("\n✅ Configurações finalizadas!")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao abrir interface de configuração: {e}")
            return False
    
    def executar_programa_principal(self):
        """Executa o programa principal."""
        print("\n" + "="*60)
        print("🚀 ETAPA 3: EXECUÇÃO PRINCIPAL")
        print("="*60)
        print("🎮 Iniciando Pisck & Click...")
        print("   • Sistema calibrado e configurado")
        print("   • Controle por movimento facial ativo")
        print("   • Clique por piscada habilitado")
        print("\n🎯 Sistema pronto para uso!")
        
        input("\n🔄 Pressione ENTER para iniciar o programa principal...")
        
        try:
            # Executar programa principal
            subprocess.run(
                [sys.executable, str(self.main_module)],
                cwd=self.base_dir
            )
            
            print("\n✅ Execução finalizada!")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao executar programa principal: {e}")
            return False
    
    def executar_fluxo_completo(self):
        """Executa o fluxo completo recomendado."""
        print("🎨 PISCK & CLICK - FLUXO RECOMENDADO")
        print("="*60)
        print("📋 Este script irá guiá-lo através do processo completo:")
        print("   1️⃣  Calibração do sistema")
        print("   2️⃣  Verificação de configurações")
        print("   3️⃣  Execução do programa principal")
        print("\n🎯 Isso garante a melhor experiência de uso!")
        
        if not self.verificar_arquivos():
            print("\n❌ Não é possível continuar sem todos os arquivos")
            return False
        
        # Etapa 1: Calibração
        if not self.executar_calibracao():
            print("\n❌ Falha na calibração. Fluxo interrompido.")
            return False
        
        # Pequena pausa entre etapas
        time.sleep(2)
        
        # Etapa 2: Configuração
        if not self.abrir_config_gui():
            print("\n❌ Falha na configuração. Fluxo interrompido.")
            return False
        
        # Pequena pausa entre etapas
        time.sleep(2)
        
        # Etapa 3: Execução principal
        if not self.executar_programa_principal():
            print("\n❌ Falha na execução principal.")
            return False
        
        print("\n" + "="*60)
        print("🎉 FLUXO COMPLETO FINALIZADO COM SUCESSO!")
        print("="*60)
        print("✅ Calibração realizada")
        print("✅ Configurações verificadas")
        print("✅ Sistema executado")
        print("\n🎯 Pisck & Click está pronto para uso otimizado!")
        
        return True

def main():
    """Função principal."""
    try:
        fluxo = FluxoRecomendado()
        sucesso = fluxo.executar_fluxo_completo()
        
        if sucesso:
            print("\n🏁 Processo concluído com sucesso!")
        else:
            print("\n⚠️  Processo interrompido ou com falhas")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        print(f"\n❌ Erro inesperado: {e}")
    
    input("\n🔄 Pressione ENTER para sair...")

if __name__ == "__main__":
    main()