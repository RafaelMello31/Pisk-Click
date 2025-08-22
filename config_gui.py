import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConfigField:
    """Representa um campo de configuração com metadados."""
    name: str
    label: str
    field_type: str
    default_value: Any
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    tooltip: Optional[str] = None
    validation_func: Optional[callable] = None


class ConfigDefaults:
    """Centraliza todos os valores padrão de configuração."""

    # Valores padrão com fallback
    DEFAULTS = {
        'NOSE_TIP_INDEX': 1,
        'LEFT_EYE_LANDMARKS_IDXS': [33, 160, 158, 133, 153, 144],
        'RIGHT_EYE_LANDMARKS_IDXS': [362, 385, 387, 263, 380, 373],
        'REFINE_LANDMARKS': False,
        'EAR_THRESHOLD': 0.25,
        'BLINK_CONSECUTIVE_FRAMES': 2,
        'SMOOTHING_FACTOR': 0.7,
        'CONTROL_AREA_X_MIN': 0.3,
        'CONTROL_AREA_X_MAX': 0.7,
        'CONTROL_AREA_Y_MIN': 0.3,
        'CONTROL_AREA_Y_MAX': 0.7,
        'INVERT_X_AXIS': False,
        'INVERT_Y_AXIS': False,
        'CLICK_DEBOUNCE_TIME': 0.5,
        'PROCESS_EVERY_N_FRAMES': 3,
        'ALT_TAB_TRIGGER_BOTH_EYES_BLINK': True,
        'ALT_TAB_DEBOUNCE_TIME': 1.0,
        'HEAD_TILT_THRESHOLD': 15.0,
        'HEAD_TILT_DEBOUNCE_TIME': 0.5,
        'HEAD_TILT_LEFT_TRIGGER_KEY': 'left',
        'HEAD_TILT_RIGHT_TRIGGER_KEY': 'right'
    }

    @classmethod
    def get_default(cls, key: str) -> Any:
        """Obtém valor padrão com fallback seguro."""
        try:
            from config import *
            return globals().get(key, cls.DEFAULTS.get(key))
        except ImportError:
            return cls.DEFAULTS.get(key)


class ConfigValidator:
    """Validadores para diferentes tipos de configuração."""

    @staticmethod
    def validate_float_range(value: float, min_val: float, max_val: float) -> bool:
        """Valida se um float está dentro do range especificado."""
        try:
            float_val = float(value)
            return min_val <= float_val <= max_val
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_positive_int(value: int) -> bool:
        """Valida se é um inteiro positivo."""
        try:
            int_val = int(value)
            return int_val > 0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_key_string(value: str) -> bool:
        """Valida se é uma string válida para tecla."""
        return isinstance(value, str) and len(value.strip()) > 0


class ConfigSections:
    """Define as seções e campos de configuração."""

    SECTIONS = {
        "Detecção Facial": [
            ConfigField(
                "REFINE_LANDMARKS",
                "Refinar landmarks (melhor precisão, mais CPU)",
                "boolean",
                ConfigDefaults.get_default('REFINE_LANDMARKS'),
                tooltip="Ativa refinamento de landmarks para maior precisão, mas consome mais CPU"
            ),
            ConfigField(
                "EAR_THRESHOLD",
                "Limiar de piscada (0.15-0.30)",
                "float",
                ConfigDefaults.get_default('EAR_THRESHOLD'),
                min_value=0.15,
                max_value=0.30,
                tooltip="Valor que determina quando uma piscada é detectada",
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.15, 0.30)
            ),
            ConfigField(
                "BLINK_CONSECUTIVE_FRAMES",
                "Frames consecutivos para piscada",
                "int",
                ConfigDefaults.get_default('BLINK_CONSECUTIVE_FRAMES'),
                min_value=1,
                max_value=10,
                tooltip="Número de frames consecutivos necessários para confirmar uma piscada",
                validation_func=ConfigValidator.validate_positive_int
            ),
        ],

        "Controle do Mouse": [
            ConfigField(
                "SMOOTHING_FACTOR",
                "Suavização do movimento (0.0-1.0)",
                "float",
                ConfigDefaults.get_default('SMOOTHING_FACTOR'),
                min_value=0.0,
                max_value=1.0,
                tooltip="Controla a suavização do movimento do mouse (0=sem suavização, 1=máxima)",
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.0, 1.0)
            ),
            ConfigField(
                "CONTROL_AREA_X_MIN",
                "Área de controle X mínima (0.0-1.0)",
                "float",
                ConfigDefaults.get_default('CONTROL_AREA_X_MIN'),
                min_value=0.0,
                max_value=1.0,
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.0, 1.0)
            ),
            ConfigField(
                "CONTROL_AREA_X_MAX",
                "Área de controle X máxima (0.0-1.0)",
                "float",
                ConfigDefaults.get_default('CONTROL_AREA_X_MAX'),
                min_value=0.0,
                max_value=1.0,
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.0, 1.0)
            ),
            ConfigField(
                "CONTROL_AREA_Y_MIN",
                "Área de controle Y mínima (0.0-1.0)",
                "float",
                ConfigDefaults.get_default('CONTROL_AREA_Y_MIN'),
                min_value=0.0,
                max_value=1.0,
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.0, 1.0)
            ),
            ConfigField(
                "CONTROL_AREA_Y_MAX",
                "Área de controle Y máxima (0.0-1.0)",
                "float",
                ConfigDefaults.get_default('CONTROL_AREA_Y_MAX'),
                min_value=0.0,
                max_value=1.0,
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.0, 1.0)
            ),
            ConfigField(
                "INVERT_X_AXIS",
                "Inverter eixo X",
                "boolean",
                ConfigDefaults.get_default('INVERT_X_AXIS'),
                tooltip="Inverte o movimento horizontal do mouse"
            ),
            ConfigField(
                "INVERT_Y_AXIS",
                "Inverter eixo Y",
                "boolean",
                ConfigDefaults.get_default('INVERT_Y_AXIS'),
                tooltip="Inverte o movimento vertical do mouse"
            ),
        ],

        "Temporização": [
            ConfigField(
                "CLICK_DEBOUNCE_TIME",
                "Tempo entre cliques (segundos)",
                "float",
                ConfigDefaults.get_default('CLICK_DEBOUNCE_TIME'),
                min_value=0.1,
                max_value=5.0,
                tooltip="Tempo mínimo entre cliques consecutivos",
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.1, 5.0)
            ),
            ConfigField(
                "ALT_TAB_DEBOUNCE_TIME",
                "Tempo entre Alt+Tab (segundos)",
                "float",
                ConfigDefaults.get_default('ALT_TAB_DEBOUNCE_TIME'),
                min_value=0.5,
                max_value=10.0,
                tooltip="Tempo mínimo entre comandos Alt+Tab consecutivos",
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.5, 10.0)
            ),
            ConfigField(
                "HEAD_TILT_DEBOUNCE_TIME",
                "Tempo entre inclinações da cabeça (segundos)",
                "float",
                ConfigDefaults.get_default('HEAD_TILT_DEBOUNCE_TIME'),
                min_value=0.1,
                max_value=5.0,
                tooltip="Tempo mínimo entre detecções de inclinação da cabeça",
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.1, 5.0)
            ),
        ],

        "Performance": [
            ConfigField(
                "PROCESS_EVERY_N_FRAMES",
                "Processar a cada N frames",
                "int",
                ConfigDefaults.get_default('PROCESS_EVERY_N_FRAMES'),
                min_value=1,
                max_value=10,
                tooltip="Processa apenas 1 a cada N frames para melhor performance",
                validation_func=ConfigValidator.validate_positive_int
            ),
        ],

        "Funcionalidades": [
            ConfigField(
                "ALT_TAB_TRIGGER_BOTH_EYES_BLINK",
                "Alt+Tab com piscada dupla",
                "boolean",
                ConfigDefaults.get_default('ALT_TAB_TRIGGER_BOTH_EYES_BLINK'),
                tooltip="Ativa Alt+Tab quando ambos os olhos piscam simultaneamente"
            ),
            ConfigField(
                "HEAD_TILT_THRESHOLD",
                "Limiar de inclinação da cabeça (graus)",
                "float",
                ConfigDefaults.get_default('HEAD_TILT_THRESHOLD'),
                min_value=5.0,
                max_value=45.0,
                tooltip="Ângulo mínimo de inclinação da cabeça para trigger",
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 5.0, 45.0)
            ),
            ConfigField(
                "HEAD_TILT_LEFT_TRIGGER_KEY",
                "Tecla para inclinação esquerda",
                "string",
                ConfigDefaults.get_default('HEAD_TILT_LEFT_TRIGGER_KEY'),
                tooltip="Tecla a ser pressionada ao inclinar cabeça para esquerda",
                validation_func=ConfigValidator.validate_key_string
            ),
            ConfigField(
                "HEAD_TILT_RIGHT_TRIGGER_KEY",
                "Tecla para inclinação direita",
                "string",
                ConfigDefaults.get_default('HEAD_TILT_RIGHT_TRIGGER_KEY'),
                tooltip="Tecla a ser pressionada ao inclinar cabeça para direita",
                validation_func=ConfigValidator.validate_key_string
            ),
        ]
    }


class ProfileManager:
    """Gerenciador simplificado de perfis (substitui a dependência externa)."""

    def __init__(self, profiles_dir: str = "profiles"):
        self.profiles_dir = profiles_dir
        os.makedirs(profiles_dir, exist_ok=True)

    def list_profiles(self) -> list:
        """Lista todos os perfis disponíveis."""
        try:
            profiles = []
            for file in os.listdir(self.profiles_dir):
                if file.endswith('.json'):
                    profiles.append(file[:-5])  # Remove .json
            return profiles if profiles else ['default']
        except Exception as e:
            logger.error(f"Erro ao listar perfis: {e}")
            return ['default']

    def create_profile(self, name: str, config: Dict[str, Any]) -> bool:
        """Cria um novo perfil."""
        try:
            profile_path = os.path.join(self.profiles_dir, f"{name}.json")
            with open(profile_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Erro ao criar perfil {name}: {e}")
            return False

    def save_profile_config(self, name: str, config: Dict[str, Any]) -> bool:
        """Salva configurações em um perfil."""
        return self.create_profile(name, config)

    def load_profile_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Carrega configurações de um perfil."""
        try:
            profile_path = os.path.join(self.profiles_dir, f"{name}.json")
            if os.path.exists(profile_path):
                with open(profile_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Erro ao carregar perfil {name}: {e}")
            return None

    def delete_profile(self, name: str) -> bool:
        """Exclui um perfil."""
        try:
            profile_path = os.path.join(self.profiles_dir, f"{name}.json")
            if os.path.exists(profile_path):
                os.remove(profile_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao excluir perfil {name}: {e}")
            return False


class ToolTip:
    """Classe para adicionar tooltips aos widgets."""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        """Mostra o tooltip."""
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(self.tooltip_window, text=self.text,
                          background="lightyellow", relief="solid", borderwidth=1,
                          font=("Arial", 8))
        label.pack()

    def on_leave(self, event=None):
        """Esconde o tooltip."""
        if self.tooltip_window:
            self.current_profile = profile_name
            self.profile_name_var.set(profile_name)
            logger.info(f"Perfil '{profile_name}' carregado com sucesso!")
        else:
            logger.warning(f"Não foi possível carregar o perfil '{profile_name}'")
            messagebox.showwarning("Aviso",
                                   f"Não foi possível carregar o perfil '{profile_name}'\nCriando perfil padrão.")
            # Se o perfil não existe, volta para o padrão
            self.restore_defaults()
            self.current_profile = "default"
            self.profile_name_var.set("default")
            # Garante que o perfil default exista
            self.profile_manager.create_profile("default", self.get_current_config_values())
            self.update_profile_dropdown()

    def delete_selected_profile(self):
        """Exclui o perfil selecionado no dropdown."""
        profile_to_delete = self.profile_name_var.get()
        if profile_to_delete == "default":
            messagebox.showwarning("Aviso", "O perfil 'default' não pode ser excluído.")
            return

        if messagebox.askyesno("Confirmar Exclusão",
                               f"Tem certeza que deseja excluir o perfil '{profile_to_delete}'?"):
            if self.profile_manager.delete_profile(profile_to_delete):
                messagebox.showinfo("Sucesso", f"Perfil '{profile_to_delete}' excluído.")
                self.update_profile_dropdown()
                self.load_profile("default")
            else:
                messagebox.showerror("Erro", "Não foi possível excluir o perfil.")

    def get_current_config_values(self) -> Dict[str, Any]:
        """Retorna um dicionário com os valores atuais da GUI."""
        config_data = {}
        for name, var in self.config_vars.items():
            try:
                config_data[name] = var.get()
            except tk.TclError as e:
                logger.error(f"Erro ao obter valor de {name}: {e}")
                # Usar valor padrão em caso de erro
                config_data[name] = ConfigDefaults.get_default(name)
        return config_data

    def restore_defaults(self):
        """Restaura as configurações padrão na GUI."""
        self.load_current_config_from_defaults()
        messagebox.showinfo("Sucesso", "Configurações padrão restauradas!")

    def apply_and_close(self):
        """Aplica as configurações e fecha a janela."""
        if not self.validate_all_fields():
            return

        # Salva as configurações no perfil atual
        if self.save_current_profile():
            if self.generate_config_file_from_profile(self.current_profile):
                messagebox.showinfo("Sucesso", "Configurações aplicadas com sucesso!")
                self.root.destroy()
            else:
                messagebox.showerror("Erro", "Não foi possível gerar o arquivo de configuração.")
        else:
            messagebox.showerror("Erro", "Não foi possível aplicar as configurações.")

    def generate_config_file_from_profile(self, profile_name: str) -> bool:
        """Gera um novo arquivo config.py com as configurações do perfil."""
        config_data = self.profile_manager.load_profile_config(profile_name)
        if not config_data:
            messagebox.showerror("Erro", f"Perfil '{profile_name}' não encontrado.")
            return False

        def format_value(value: Any) -> str:
            """Formata valores para o arquivo config.py."""
            if isinstance(value, bool):
                return str(value)
            elif isinstance(value, str):
                return f"'{value}'"
            elif isinstance(value, list):
                return str(value)
            else:
                return str(value)

        # Template do arquivo config.py melhorado
        config_content = f'''# -*- coding: utf-8 -*-
"""
Arquivo de configuração gerado automaticamente pelo ConfigGUI
Perfil: {profile_name}
Data: {self.get_current_timestamp()}
"""

# --- Constantes e Configurações do Pisk&Click ---

# Índices dos landmarks faciais (Mediapipe Face Mesh)
NOSE_TIP_INDEX = {format_value(config_data.get('NOSE_TIP_INDEX', ConfigDefaults.get_default('NOSE_TIP_INDEX')))}
LEFT_EYE_LANDMARKS_IDXS = {format_value(config_data.get('LEFT_EYE_LANDMARKS_IDXS', ConfigDefaults.get_default('LEFT_EYE_LANDMARKS_IDXS')))}
RIGHT_EYE_LANDMARKS_IDXS = {format_value(config_data.get('RIGHT_EYE_LANDMARKS_IDXS', ConfigDefaults.get_default('RIGHT_EYE_LANDMARKS_IDXS')))}

# === DETECÇÃO FACIAL ===
# Qualidade vs Desempenho Mediapipe
REFINE_LANDMARKS = {format_value(config_data.get('REFINE_LANDMARKS', ConfigDefaults.get_default('REFINE_LANDMARKS')))}

# Limiares e Contadores para Detecção de Piscada
EAR_THRESHOLD = {format_value(config_data.get('EAR_THRESHOLD', ConfigDefaults.get_default('EAR_THRESHOLD')))}
BLINK_CONSECUTIVE_FRAMES = {format_value(config_data.get('BLINK_CONSECUTIVE_FRAMES', ConfigDefaults.get_default('BLINK_CONSECUTIVE_FRAMES')))}

# === CONTROLE DO MOUSE ===
# Suavização do Movimento do Mouse
SMOOTHING_FACTOR = {format_value(config_data.get('SMOOTHING_FACTOR', ConfigDefaults.get_default('SMOOTHING_FACTOR')))}

# Área de Controle do Rosto (Mapeamento Câmera -> Tela)
CONTROL_AREA_X_MIN = {format_value(config_data.get('CONTROL_AREA_X_MIN', ConfigDefaults.get_default('CONTROL_AREA_X_MIN')))}
CONTROL_AREA_X_MAX = {format_value(config_data.get('CONTROL_AREA_X_MAX', ConfigDefaults.get_default('CONTROL_AREA_X_MAX')))}
CONTROL_AREA_Y_MIN = {format_value(config_data.get('CONTROL_AREA_Y_MIN', ConfigDefaults.get_default('CONTROL_AREA_Y_MIN')))}
CONTROL_AREA_Y_MAX = {format_value(config_data.get('CONTROL_AREA_Y_MAX', ConfigDefaults.get_default('CONTROL_AREA_Y_MAX')))}

# Inversão de Eixos (Opcional)
INVERT_X_AXIS = {format_value(config_data.get('INVERT_X_AXIS', ConfigDefaults.get_default('INVERT_X_AXIS')))}
INVERT_Y_AXIS = {format_value(config_data.get('INVERT_Y_AXIS', ConfigDefaults.get_default('INVERT_Y_AXIS')))}

# === TEMPORIZAÇÃO ===
# Debounce para Cliques
CLICK_DEBOUNCE_TIME = {format_value(config_data.get('CLICK_DEBOUNCE_TIME', ConfigDefaults.get_default('CLICK_DEBOUNCE_TIME')))}

# Configurações para Alt+Tab
ALT_TAB_DEBOUNCE_TIME = {format_value(config_data.get('ALT_TAB_DEBOUNCE_TIME', ConfigDefaults.get_default('ALT_TAB_DEBOUNCE_TIME')))}

# Configurações para Inclinação da Cabeça
HEAD_TILT_DEBOUNCE_TIME = {format_value(config_data.get('HEAD_TILT_DEBOUNCE_TIME', ConfigDefaults.get_default('HEAD_TILT_DEBOUNCE_TIME')))}

# === PERFORMANCE ===
# Otimização de Desempenho (Processar apenas 1 a cada N frames)
PROCESS_EVERY_N_FRAMES = {format_value(config_data.get('PROCESS_EVERY_N_FRAMES', ConfigDefaults.get_default('PROCESS_EVERY_N_FRAMES')))}

# === FUNCIONALIDADES AVANÇADAS ===
# Funcionalidade Alt+Tab com piscada dupla
ALT_TAB_TRIGGER_BOTH_EYES_BLINK = {format_value(config_data.get('ALT_TAB_TRIGGER_BOTH_EYES_BLINK', ConfigDefaults.get_default('ALT_TAB_TRIGGER_BOTH_EYES_BLINK')))}

# Configurações para Inclinação da Cabeça
HEAD_TILT_THRESHOLD = {format_value(config_data.get('HEAD_TILT_THRESHOLD', ConfigDefaults.get_default('HEAD_TILT_THRESHOLD')))}
HEAD_TILT_LEFT_TRIGGER_KEY = {format_value(config_data.get('HEAD_TILT_LEFT_TRIGGER_KEY', ConfigDefaults.get_default('HEAD_TILT_LEFT_TRIGGER_KEY')))}
HEAD_TILT_RIGHT_TRIGGER_KEY = {format_value(config_data.get('HEAD_TILT_RIGHT_TRIGGER_KEY', ConfigDefaults.get_default('HEAD_TILT_RIGHT_TRIGGER_KEY')))}

# === CONFIGURAÇÕES AVANÇADAS ===
# (Estas configurações normalmente não precisam ser alteradas)

# Validação de configurações (executada na importação)
def validate_config():
    """Valida as configurações carregadas."""
    issues = []

    if not (0.1 <= EAR_THRESHOLD <= 0.4):
        issues.append(f"EAR_THRESHOLD ({EAR_THRESHOLD}) deve estar entre 0.1 e 0.4")

    if not (0.0 <= SMOOTHING_FACTOR <= 1.0):
        issues.append(f"SMOOTHING_FACTOR ({SMOOTHING_FACTOR}) deve estar entre 0.0 e 1.0")

    if CONTROL_AREA_X_MIN >= CONTROL_AREA_X_MAX:
        issues.append("CONTROL_AREA_X_MIN deve ser menor que CONTROL_AREA_X_MAX")

    if CONTROL_AREA_Y_MIN >= CONTROL_AREA_Y_MAX:
        issues.append("CONTROL_AREA_Y_MIN deve ser menor que CONTROL_AREA_Y_MAX")

    if issues:
        import warnings
        for issue in issues:
            warnings.warn(f"Configuração inválida: {issue}")

    return len(issues) == 0

# Executar validação na importação
if __name__ != "__main__":
    validate_config()
'''

        try:
            with open("config.py", "w", encoding="utf-8") as f:
                f.write(config_content)
            logger.info("Arquivo config.py gerado com sucesso!")
            return True
        except Exception as e:
            logger.error(f"Erro ao gerar config.py: {e}")
            messagebox.showerror("Erro", f"Erro ao gerar config.py: {e}")
            return False

    def get_current_timestamp(self) -> str:
        """Retorna timestamp atual formatado."""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def run(self):
        """Executa a interface gráfica."""
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Erro na execução da GUI: {e}")
            messagebox.showerror("Erro Fatal", f"Erro na execução da GUI: {e}")


def main():
    """Função principal com tratamento de erro global."""
    try:
        gui = ConfigGUI()
        gui.run()
    except Exception as e:
        logger.error(f"Erro fatal na inicialização: {e}")
        # Tentar mostrar erro ao usuário mesmo se a GUI não inicializar
        try:
            root = tk.Tk()
            root.withdraw()  # Esconder janela principal
            messagebox.showerror("Erro Fatal",
                                 f"Erro fatal na inicialização da aplicação:\n\n{e}\n\n"
                                 f"Verifique se todas as dependências estão instaladas.")
        except:
            print(f"ERRO FATAL: {e}")


if __name__ == "__main__":
    main().tooltip_window.destroy()
    self.tooltip_window = None


class ConfigGUI:
    """Interface gráfica melhorada para configuração do Pisk&Click."""

    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()

        self.profile_manager = ProfileManager()
        self.current_profile = "default"
        self.config_vars = {}
        self.tooltips = []

        self.create_widgets()
        self.load_current_config_from_defaults()
        self.load_profile("default")
        self.update_profile_dropdown()

    def setup_window(self):
        """Configura a janela principal."""
        self.root.title("Pisk&Click - Configurações")
        self.root.geometry("800x900")
        self.root.resizable(True, True)

        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')

        # Centralizar janela
        self.center_window()

    def center_window(self):
        """Centraliza a janela na tela."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """Cria todos os widgets da interface."""
        # Frame principal com scroll
        self.setup_scrollable_frame()

        # Título
        self.create_title()

        # Seção de perfis
        self.create_profile_section()

        # Seções de configuração
        self.create_config_sections()

        # Botões de ação
        self.create_action_buttons()

    def setup_scrollable_frame(self):
        """Configura o frame principal com scroll."""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind scroll do mouse
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        """Lida com o scroll do mouse."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_title(self):
        """Cria o título da aplicação."""
        title_label = ttk.Label(self.scrollable_frame, text="Configurações do Pisk&Click",
                                font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))

    def create_profile_section(self):
        """Cria a seção de gerenciamento de perfis."""
        profile_frame = ttk.LabelFrame(self.scrollable_frame, text="Gerenciamento de Perfis", padding=15)
        profile_frame.pack(fill=tk.X, pady=10)

        # Linha 1: Seleção de perfil
        ttk.Label(profile_frame, text="Perfil Atual:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )

        self.profile_name_var = tk.StringVar(value=self.current_profile)
        self.profile_dropdown = ttk.Combobox(profile_frame, textvariable=self.profile_name_var,
                                             state="readonly", width=20)
        self.profile_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.profile_dropdown.bind("<<ComboboxSelected>>", self.on_profile_selected)

        ttk.Button(profile_frame, text="Novo Perfil", command=self.create_new_profile).grid(
            row=0, column=2, padx=5, pady=5
        )

        # Linha 2: Ações de perfil
        button_frame = ttk.Frame(profile_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")

        ttk.Button(button_frame, text="Salvar Perfil", command=self.save_current_profile).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Carregar Perfil", command=self.load_selected_profile).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Excluir Perfil", command=self.delete_selected_profile).pack(
            side=tk.LEFT, padx=5
        )

        profile_frame.grid_columnconfigure(1, weight=1)

    def create_config_sections(self):
        """Cria todas as seções de configuração."""
        for section_name, fields in ConfigSections.SECTIONS.items():
            self.create_section(self.scrollable_frame, section_name, fields)

    def create_section(self, parent, title: str, config_fields: list):
        """Cria uma seção de configurações com validação aprimorada."""
        section_frame = ttk.LabelFrame(parent, text=title, padding=15)
        section_frame.pack(fill=tk.X, pady=10)

        for field in config_fields:
            row_frame = ttk.Frame(section_frame)
            row_frame.pack(fill=tk.X, pady=8)

            # Label com tooltip
            label = ttk.Label(row_frame, text=field.label, width=45, font=("Arial", 9))
            label.pack(side=tk.LEFT, anchor="w")

            if field.tooltip:
                ToolTip(label, field.tooltip)

            # Widget de entrada baseado no tipo
            widget = self.create_input_widget(row_frame, field)
            widget.pack(side=tk.RIGHT, anchor="e")

            # Adicionar tooltip no widget também
            if field.tooltip:
                ToolTip(widget, field.tooltip)

    def create_input_widget(self, parent, field: ConfigField):
        """Cria o widget apropriado para cada tipo de campo."""
        if field.field_type == "boolean":
            var = tk.BooleanVar(value=field.default_value)
            widget = ttk.Checkbutton(parent, variable=var)

        elif field.field_type == "int":
            var = tk.IntVar(value=field.default_value)
            widget = ttk.Spinbox(
                parent,
                from_=field.min_value or 1,
                to=field.max_value or 100,
                textvariable=var,
                width=15,
                validate='key',
                validatecommand=(self.root.register(lambda x: x.isdigit() or x == ""), '%P')
            )

        elif field.field_type == "float":
            var = tk.DoubleVar(value=field.default_value)
            widget = ttk.Entry(parent, textvariable=var, width=15)
            # Adicionar validação em tempo real
            widget.bind('<FocusOut>', lambda e, f=field: self.validate_field(f))

        elif field.field_type == "string":
            var = tk.StringVar(value=field.default_value)
            widget = ttk.Entry(parent, textvariable=var, width=15)

        self.config_vars[field.name] = var
        return widget

    def validate_field(self, field: ConfigField):
        """Valida um campo específico."""
        if field.validation_func:
            try:
                value = self.config_vars[field.name].get()
                if not field.validation_func(value):
                    messagebox.showwarning(
                        "Valor Inválido",
                        f"Valor inválido para {field.label}. "
                        f"Valor deve estar entre {field.min_value} e {field.max_value}."
                    )
                    # Restaurar valor padrão
                    self.config_vars[field.name].set(field.default_value)
            except Exception as e:
                logger.error(f"Erro na validação do campo {field.name}: {e}")

    def validate_all_fields(self) -> bool:
        """Valida todos os campos antes de salvar."""
        errors = []

        for section_name, fields in ConfigSections.SECTIONS.items():
            for field in fields:
                if field.validation_func:
                    try:
                        value = self.config_vars[field.name].get()
                        if not field.validation_func(value):
                            errors.append(
                                f"- {field.label}: valor deve estar entre {field.min_value} e {field.max_value}")
                    except Exception as e:
                        errors.append(f"- {field.label}: {str(e)}")

        # Validações específicas
        x_min = self.config_vars.get('CONTROL_AREA_X_MIN', tk.DoubleVar()).get()
        x_max = self.config_vars.get('CONTROL_AREA_X_MAX', tk.DoubleVar()).get()
        if x_min >= x_max:
            errors.append("- Área de controle X mínima deve ser menor que máxima")

        y_min = self.config_vars.get('CONTROL_AREA_Y_MIN', tk.DoubleVar()).get()
        y_max = self.config_vars.get('CONTROL_AREA_Y_MAX', tk.DoubleVar()).get()
        if y_min >= y_max:
            errors.append("- Área de controle Y mínima deve ser menor que máxima")

        if errors:
            messagebox.showerror("Erros de Validação",
                                 "Corrija os seguintes erros:\n\n" + "\n".join(errors))
            return False
        return True

    def create_action_buttons(self):
        """Cria os botões de ação."""
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.pack(fill=tk.X, pady=20)

        ttk.Button(button_frame, text="Restaurar Padrões",
                   command=self.restore_defaults, style="Accent.TButton").pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Validar Configurações",
                   command=self.validate_all_fields).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Aplicar e Fechar",
                   command=self.apply_and_close, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)

    def load_current_config_from_defaults(self):
        """Carrega configurações padrão na GUI."""
        for name, var in self.config_vars.items():
            default_value = ConfigDefaults.get_default(name)
            if default_value is not None:
                var.set(default_value)

    # ... (métodos de gerenciamento de perfil permanecem similares, mas com melhor tratamento de erro)

    def update_profile_dropdown(self):
        """Atualiza as opções do dropdown de perfis."""
        profiles = self.profile_manager.list_profiles()
        self.profile_dropdown["values"] = profiles
        if self.current_profile not in profiles and profiles:
            self.current_profile = profiles[0]
        elif not profiles:
            self.current_profile = "default"
        self.profile_name_var.set(self.current_profile)

    def on_profile_selected(self, event):
        """Lida com a seleção de um perfil no dropdown."""
        selected_profile = self.profile_name_var.get()
        if selected_profile != self.current_profile:
            self.load_profile(selected_profile)

    def create_new_profile(self):
        """Cria um novo perfil com validação."""
        new_profile_name = simpledialog.askstring("Novo Perfil", "Digite o nome do novo perfil:")
        if new_profile_name:
            new_profile_name = new_profile_name.strip()
            if not new_profile_name:
                messagebox.showerror("Erro", "Nome do perfil não pode estar vazio.")
                return

            if new_profile_name in self.profile_manager.list_profiles():
                messagebox.showerror("Erro", f"Perfil '{new_profile_name}' já existe.")
                return

            if self.validate_all_fields():
                if self.profile_manager.create_profile(new_profile_name, self.get_current_config_values()):
                    self.current_profile = new_profile_name
                    self.update_profile_dropdown()
                    messagebox.showinfo("Sucesso", f"Perfil '{new_profile_name}' criado e carregado.")
                else:
                    messagebox.showerror("Erro", "Não foi possível criar o perfil.")

    def save_current_profile(self):
        """Salva as configurações atuais no perfil ativo."""
        if self.validate_all_fields():
            if self.profile_manager.save_profile_config(self.current_profile, self.get_current_config_values()):
                messagebox.showinfo("Sucesso", f"Configurações salvas para o perfil '{self.current_profile}'")
                return True
            else:
                messagebox.showerror("Erro", "Não foi possível salvar as configurações do perfil.")
                return False
        return False

    def load_selected_profile(self):
        """Carrega o perfil selecionado no dropdown."""
        selected_profile = self.profile_name_var.get()
        self.load_profile(selected_profile)

    def load_profile(self, profile_name: str):
        """Carrega as configurações de um perfil."""
        config_data = self.profile_manager.load_profile_config(profile_name)
        if config_data:
            for name, value in config_data.items():
                if name in self.config_vars:
                    self.config_vars[name].set(value)
            self