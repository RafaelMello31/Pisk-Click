import json
import os
import logging

logger = logging.getLogger(__name__)

class UserProfileManager:
   """Gerencia a criação, salvamento e carregamento de perfis de usuário."""

   def __init__(self, profiles_dir="profiles"):
       self.profiles_dir = profiles_dir
       if not os.path.exists(self.profiles_dir):
           os.makedirs(self.profiles_dir)

   def _get_profile_path(self, profile_name):
       """Retorna o caminho completo para o arquivo de configuração de um perfil."""
       return os.path.join(self.profiles_dir, f"{profile_name}.json")

   def create_profile(self, profile_name, initial_config=None):
       """Cria um novo perfil de usuário com configurações iniciais."""
       profile_path = self._get_profile_path(profile_name)
       if os.path.exists(profile_path):
           logger.warning(f"Aviso: Perfil '{profile_name}' já existe. Sobrescrevendo...")

       config_to_save = initial_config if initial_config is not None else {}
       try:
           with open(profile_path, "w") as f:
               json.dump(config_to_save, f, indent=4)
           logger.info(f"Perfil '{profile_name}' criado com sucesso em {profile_path}")
           return True
       except Exception as e:
           logger.error(f"Erro ao criar perfil '{profile_name}': {e}")
           return False

   def save_profile_config(self, profile_name, config_data):
       """Salva as configurações para um perfil existente."""
       profile_path = self._get_profile_path(profile_name)
       if not os.path.exists(profile_path):
           logger.error(f"Erro: Perfil '{profile_name}' não encontrado para salvar.")
           return False

       try:
           with open(profile_path, "w") as f:
               json.dump(config_data, f, indent=4)
           logger.info(f"Configurações salvas para o perfil '{profile_name}' em {profile_path}")
           return True
       except Exception as e:
           logger.error(f"Erro ao salvar configurações para o perfil '{profile_name}': {e}")
           return False

   def load_profile_config(self, profile_name):
       """Carrega as configurações de um perfil existente."""
       profile_path = self._get_profile_path(profile_name)
       if not os.path.exists(profile_path):
           logger.error(f"Erro: Perfil '{profile_name}' não encontrado para carregar.")
           return None

       try:
           with open(profile_path, "r") as f:
               config_data = json.load(f)
           logger.info(f"Configurações carregadas do perfil '{profile_name}'")
           return config_data
       except Exception as e:
           logger.error(f"Erro ao carregar configurações do perfil '{profile_name}': {e}")
           return None

   def list_profiles(self):
       """Lista todos os perfis de usuário disponíveis."""
       profiles = []
       if os.path.exists(self.profiles_dir):
           for filename in os.listdir(self.profiles_dir):
               if filename.endswith(".json"):
                   profiles.append(os.path.splitext(filename)[0])
       return sorted(profiles)

   def delete_profile(self, profile_name):
       """Deleta um perfil de usuário."""
       profile_path = self._get_profile_path(profile_name)
       if not os.path.exists(profile_path):
           logger.warning(f"Aviso: Perfil '{profile_name}' não encontrado para deletar.")
           return False
       try:
           os.remove(profile_path)
           logger.info(f"Perfil '{profile_name}' deletado com sucesso.")
           return True
       except Exception as e:
           logger.error(f"Erro ao deletar perfil '{profile_name}': {e}")
           return False

if __name__ == "__main__":
   logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')
   # Exemplo de uso
   manager = UserProfileManager("test_profiles")

   # Criar um novo perfil
   manager.create_profile("usuario_teste", {"EAR_THRESHOLD": 0.22, "SMOOTHING_FACTOR": 0.4})

   # Listar perfis
   logger.info(f"Perfis existentes: {manager.list_profiles()}")

   # Carregar um perfil
   loaded_config = manager.load_profile_config("usuario_teste")
   if loaded_config:
       logger.info(f"Configurações do usuario_teste: {loaded_config}")

   # Salvar configurações atualizadas para um perfil
   updated_config = {"EAR_THRESHOLD": 0.25, "SMOOTHING_FACTOR": 0.5, "NEW_SETTING": True}
   manager.save_profile_config("usuario_teste", updated_config)

   # Carregar novamente para verificar
   loaded_config = manager.load_profile_config("usuario_teste")
   if loaded_config:
       logger.info(f"Configurações atualizadas do usuario_teste: {loaded_config}")

   # Deletar um perfil
   manager.delete_profile("usuario_teste")
   logger.info(f"Perfis existentes após deleção: {manager.list_profiles()}")