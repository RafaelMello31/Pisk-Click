#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo prático de como usar a calibração integrada com o perfil default.
Este script demonstra como executar uma calibração e como os resultados
são automaticamente salvos no perfil default do config_gui.py.
"""

import logging
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def exemplo_calibracao_completa():
    """Exemplo de calibração completa com integração ao perfil default."""
    try:
        logger.info("=== EXEMPLO DE CALIBRAÇÃO COM INTEGRAÇÃO DE PERFIL ===")
        
        # 1. Importar módulos necessários
        from main import FaceController
        from calibration_module import CalibrationModule
        from user_profile_manager import UserProfileManager
        
        # 2. Verificar estado inicial do perfil
        profile_manager = UserProfileManager()
        initial_config = profile_manager.load_profile_config("default")
        
        if initial_config:
            logger.info(f"📋 Configuração inicial do perfil default:")
            logger.info(f"   EAR_THRESHOLD: {initial_config.get('EAR_THRESHOLD', 'N/A')}")
            logger.info(f"   SMOOTHING_FACTOR: {initial_config.get('SMOOTHING_FACTOR', 'N/A')}")
        else:
            logger.info("📋 Perfil default não existe - será criado durante a calibração")
        
        # 3. Inicializar controlador facial
        logger.info("🎥 Inicializando controlador facial...")
        face_controller = FaceController()
        
        # 4. Inicializar módulo de calibração
        logger.info("⚙️ Inicializando módulo de calibração...")
        calibration_module = CalibrationModule(
            face_controller=face_controller,
            profile_manager=profile_manager  # Passa o profile_manager explicitamente
        )
        
        # 5. Executar calibração
        logger.info("🎯 Iniciando processo de calibração...")
        logger.info("   ⚠️ ATENÇÃO: A calibração abrirá janelas visuais")
        logger.info("   ⚠️ Siga as instruções na tela e pressione 'q' para parar se necessário")
        
        # Executar calibração (isso abrirá janelas visuais)
        results = calibration_module.run_calibration(calibrate_ear=True)
        
        # 6. Verificar resultados
        if results.success:
            logger.info("✅ Calibração concluída com sucesso!")
            logger.info(f"   📊 Novo EAR_THRESHOLD: {results.ear_threshold}")
            logger.info(f"   💬 Mensagem: {results.message}")
            
            # 7. Verificar se o perfil foi atualizado
            updated_config = profile_manager.load_profile_config("default")
            if updated_config:
                logger.info("\n📋 Configuração atualizada do perfil default:")
                for key, value in updated_config.items():
                    if key == "EAR_THRESHOLD":
                        logger.info(f"   ✨ {key}: {value} (ATUALIZADO PELA CALIBRAÇÃO)")
                    else:
                        logger.info(f"   📌 {key}: {value}")
            
            logger.info("\n🎉 INTEGRAÇÃO CONCLUÍDA COM SUCESSO!")
            logger.info("   ℹ️ O perfil default agora contém os resultados da calibração")
            logger.info("   ℹ️ Você pode usar o config_gui.py para ajustar outras configurações")
            
        else:
            logger.error("❌ Calibração falhou!")
            logger.error(f"   💬 Mensagem: {results.message}")
            return False
            
        return True
        
    except KeyboardInterrupt:
        logger.info("\n⏹️ Calibração interrompida pelo usuário")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro durante calibração: {e}")
        import traceback
        traceback.print_exc()
        return False

def exemplo_carregamento_perfil():
    """Exemplo de como carregar e usar o perfil default após calibração."""
    try:
        logger.info("\n=== EXEMPLO DE CARREGAMENTO DO PERFIL CALIBRADO ===")
        
        from user_profile_manager import UserProfileManager
        from config_gui import ConfigGUI
        
        # 1. Carregar perfil default
        profile_manager = UserProfileManager()
        profile_config = profile_manager.load_profile_config("default")
        
        if not profile_config:
            logger.error("❌ Perfil default não encontrado")
            logger.info("   💡 Execute primeiro uma calibração para criar o perfil")
            return False
        
        logger.info("📋 Perfil default carregado com sucesso:")
        for key, value in profile_config.items():
            logger.info(f"   📌 {key}: {value}")
        
        # 2. Demonstrar como usar com config_gui
        logger.info("\n🖥️ Para usar com a interface gráfica:")
        logger.info("   1. Execute: python config_gui.py")
        logger.info("   2. Selecione o perfil 'default' no dropdown")
        logger.info("   3. As configurações calibradas estarão carregadas")
        logger.info("   4. Ajuste outras configurações conforme necessário")
        logger.info("   5. Salve o perfil para manter as alterações")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar perfil: {e}")
        return False

def main():
    """Função principal do exemplo."""
    logger.info("🚀 EXEMPLO DE INTEGRAÇÃO CALIBRAÇÃO-PERFIL")
    logger.info("   Este exemplo demonstra como a calibração se integra com o perfil default")
    
    # Perguntar ao usuário o que fazer
    print("\n🤔 O que você gostaria de fazer?")
    print("   1. Executar calibração completa (com câmera)")
    print("   2. Apenas verificar perfil atual")
    print("   3. Sair")
    
    try:
        choice = input("\nDigite sua escolha (1-3): ").strip()
        
        if choice == "1":
            logger.info("\n🎯 Executando calibração completa...")
            success = exemplo_calibracao_completa()
            if success:
                exemplo_carregamento_perfil()
                
        elif choice == "2":
            logger.info("\n📋 Verificando perfil atual...")
            exemplo_carregamento_perfil()
            
        elif choice == "3":
            logger.info("\n👋 Saindo...")
            
        else:
            logger.error("❌ Opção inválida")
            
    except KeyboardInterrupt:
        logger.info("\n👋 Saindo...")

if __name__ == "__main__":
    main()