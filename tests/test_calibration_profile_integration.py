#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de integração entre calibração e perfil default.
Verifica se os resultados da calibração são salvos corretamente no perfil default.
"""

import sys
import os
import json
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_calibration_profile_integration():
    """Testa a integração entre calibração e perfil default."""
    try:
        # Importar módulos necessários
        from main import FaceController
        from calibration_module import CalibrationModule, CalibrationResults
        from user_profile_manager import UserProfileManager
        
        logger.info("=== TESTE DE INTEGRAÇÃO CALIBRAÇÃO-PERFIL ===")
        
        # 1. Verificar estado inicial do perfil default
        profile_manager = UserProfileManager()
        initial_config = profile_manager.load_profile_config("default")
        
        if initial_config:
            initial_ear = initial_config.get("EAR_THRESHOLD", "N/A")
            logger.info(f"EAR_THRESHOLD inicial no perfil default: {initial_ear}")
        else:
            logger.info("Perfil default não existe ainda")
        
        # 2. Simular resultado de calibração
        logger.info("Simulando resultado de calibração...")
        
        # Criar resultado simulado
        calibration_result = CalibrationResults(
            ear_threshold=0.25,  # Valor simulado
            success=True,
            message="Calibração simulada com sucesso"
        )
        
        # 3. Inicializar CalibrationModule (sem face_controller real para teste)
        logger.info("Inicializando CalibrationModule...")
        calibration_module = CalibrationModule(
            face_controller=None,  # Para teste, não precisamos do face_controller
            profile_manager=profile_manager
        )
        
        # 4. Salvar resultado da calibração
        logger.info("Salvando resultado da calibração no perfil default...")
        success = calibration_module.config_manager.save_calibration_results(
            calibration_result, 
            profile_name="default"
        )
        
        if success:
            logger.info("✅ Calibração salva com sucesso!")
        else:
            logger.error("❌ Falha ao salvar calibração")
            return False
        
        # 5. Verificar se o perfil foi atualizado
        updated_config = profile_manager.load_profile_config("default")
        
        if updated_config:
            updated_ear = updated_config.get("EAR_THRESHOLD", "N/A")
            logger.info(f"EAR_THRESHOLD atualizado no perfil default: {updated_ear}")
            
            # Verificar se o valor foi realmente atualizado
            if updated_ear == calibration_result.ear_threshold:
                logger.info("✅ Perfil default atualizado corretamente!")
            else:
                logger.error(f"❌ Valor não foi atualizado corretamente. Esperado: {calibration_result.ear_threshold}, Atual: {updated_ear}")
                return False
        else:
            logger.error("❌ Não foi possível carregar o perfil default atualizado")
            return False
        
        # 6. Verificar se config.py também foi atualizado
        try:
            import importlib
            import config
            importlib.reload(config)
            
            config_ear = getattr(config, 'EAR_THRESHOLD', 'N/A')
            logger.info(f"EAR_THRESHOLD no config.py: {config_ear}")
            
            if config_ear == calibration_result.ear_threshold:
                logger.info("✅ config.py também foi atualizado corretamente!")
            else:
                logger.warning(f"⚠️ config.py não foi atualizado. Esperado: {calibration_result.ear_threshold}, Atual: {config_ear}")
        
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível verificar config.py: {e}")
        
        # 7. Mostrar configuração completa do perfil
        logger.info("\n=== CONFIGURAÇÃO COMPLETA DO PERFIL DEFAULT ===")
        for key, value in updated_config.items():
            logger.info(f"{key}: {value}")
        
        logger.info("\n✅ TESTE DE INTEGRAÇÃO CONCLUÍDO COM SUCESSO!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_gui_compatibility():
    """Testa se o perfil é compatível com config_gui.py."""
    try:
        logger.info("\n=== TESTE DE COMPATIBILIDADE COM CONFIG_GUI ===")
        
        from user_profile_manager import UserProfileManager
        from config_gui import ConfigSections
        
        profile_manager = UserProfileManager()
        profile_config = profile_manager.load_profile_config("default")
        
        if not profile_config:
            logger.error("❌ Perfil default não encontrado")
            return False
        
        # Verificar se todas as configurações esperadas pelo config_gui estão presentes
        expected_fields = set()
        for section_fields in ConfigSections.SECTIONS.values():
            for field in section_fields:
                expected_fields.add(field.name)
        
        profile_fields = set(profile_config.keys())
        
        missing_fields = expected_fields - profile_fields
        extra_fields = profile_fields - expected_fields
        
        if missing_fields:
            logger.warning(f"⚠️ Campos ausentes no perfil: {missing_fields}")
        
        if extra_fields:
            logger.info(f"ℹ️ Campos extras no perfil: {extra_fields}")
        
        common_fields = expected_fields & profile_fields
        logger.info(f"✅ Campos compatíveis: {len(common_fields)}/{len(expected_fields)}")
        
        if len(common_fields) >= len(expected_fields) * 0.8:  # 80% de compatibilidade
            logger.info("✅ Perfil é compatível com config_gui.py!")
            return True
        else:
            logger.error("❌ Perfil não é suficientemente compatível com config_gui.py")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro durante teste de compatibilidade: {e}")
        return False

if __name__ == "__main__":
    logger.info("Iniciando testes de integração...")
    
    # Executar testes
    test1_success = test_calibration_profile_integration()
    test2_success = test_config_gui_compatibility()
    
    # Resultado final
    if test1_success and test2_success:
        logger.info("\n🎉 TODOS OS TESTES PASSARAM! A integração está funcionando corretamente.")
        sys.exit(0)
    else:
        logger.error("\n❌ ALGUNS TESTES FALHARAM. Verifique os logs acima.")
        sys.exit(1)