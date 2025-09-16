import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from user_profile_manager import UserProfileManager

# --------------------------------------------------------------------------- #
# Logging                                                                     #
# --------------------------------------------------------------------------- #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Metadados de Campos                                                         #
# --------------------------------------------------------------------------- #
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


# --------------------------------------------------------------------------- #
# Valores Padrão                                                              #
# --------------------------------------------------------------------------- #
class ConfigDefaults:
    """Centraliza todos os valores padrão de configuração."""

    DEFAULTS = {
        "NOSE_TIP_INDEX": 1,
        "LEFT_EYE_LANDMARKS_IDXS": [33, 160, 158, 133, 153, 144],
        "RIGHT_EYE_LANDMARKS_IDXS": [362, 385, 387, 263, 380, 373],
        "REFINE_LANDMARKS": True,
        "EAR_THRESHOLD": 0.2,
        "BLINK_CONSECUTIVE_FRAMES": 2,
        "SMOOTHING_FACTOR": 0.3,
        "CONTROL_AREA_X_MIN": 0.3,
        "CONTROL_AREA_X_MAX": 0.7,
        "CONTROL_AREA_Y_MIN": 0.3,
        "CONTROL_AREA_Y_MAX": 0.7,
        "INVERT_X_AXIS": False,
        "INVERT_Y_AXIS": False,
        "CLICK_DEBOUNCE_TIME": 0.5,
        "PROCESS_EVERY_N_FRAMES": 1,
    }

    @classmethod
    def get_default(cls, key: str) -> Any:
        """Obtém valor padrão com fallback seguro."""
        try:
            import config  # noqa
            return getattr(config, key, cls.DEFAULTS.get(key))
        except ImportError:
            return cls.DEFAULTS.get(key)


# --------------------------------------------------------------------------- #
# Validações                                                                  #
# --------------------------------------------------------------------------- #
class ConfigValidator:
    """Validadores para diferentes tipos de configuração."""

    @staticmethod
    def validate_float_range(value: float, min_val: float, max_val: float) -> bool:
        try:
            float_val = float(value)
            return min_val <= float_val <= max_val
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_positive_int(value: int) -> bool:
        try:
            int_val = int(value)
            return int_val > 0
        except (ValueError, TypeError):
            return False


# --------------------------------------------------------------------------- #
# Seções de Configuração                                                      #
# --------------------------------------------------------------------------- #
class ConfigSections:
    """Define as seções e campos de configuração."""

    SECTIONS = {
        "Detecção Facial": [
            ConfigField(
                "REFINE_LANDMARKS",
                "Refinar landmarks (melhor precisão, mais CPU)",
                "boolean",
                ConfigDefaults.get_default("REFINE_LANDMARKS"),
                tooltip="Ativa refinamento de landmarks para maior precisão, mas consome mais CPU",
            ),
            ConfigField(
                "EAR_THRESHOLD",
                "Limiar de piscada (0.15-0.30)",
                "float",
                ConfigDefaults.get_default("EAR_THRESHOLD"),
                min_value=0.15,
                max_value=0.30,
                tooltip="Valor que determina quando uma piscada é detectada",
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.15, 0.30),
            ),
            ConfigField(
                "BLINK_CONSECUTIVE_FRAMES",
                "Frames consecutivos para piscada",
                "int",
                ConfigDefaults.get_default("BLINK_CONSECUTIVE_FRAMES"),
                min_value=1,
                max_value=10,
                tooltip="Número de frames consecutivos necessários para confirmar uma piscada",
                validation_func=ConfigValidator.validate_positive_int,
            ),
        ],
        "Controle do Mouse": [
            ConfigField(
                "SMOOTHING_FACTOR",
                "Suavização do movimento (0.0-1.0)",
                "float",
                ConfigDefaults.get_default("SMOOTHING_FACTOR"),
                min_value=0.0,
                max_value=1.0,
                tooltip="Controla a suavização do movimento do mouse (0=sem suavização, 1=máxima)",
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.0, 1.0),
            ),
            ConfigField(
                "CONTROL_AREA_X_MIN",
                "Área de controle X mínima (0.0-1.0)",
                "float",
                ConfigDefaults.get_default("CONTROL_AREA_X_MIN"),
                min_value=0.0,
                max_value=1.0,
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.0, 1.0),
            ),
            ConfigField(
                "CONTROL_AREA_X_MAX",
                "Área de controle X máxima (0.0-1.0)",
                "float",
                ConfigDefaults.get_default("CONTROL_AREA_X_MAX"),
                min_value=0.0,
                max_value=1.0,
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.0, 1.0),
            ),
            ConfigField(
                "CONTROL_AREA_Y_MIN",
                "Área de controle Y mínima (0.0-1.0)",
                "float",
                ConfigDefaults.get_default("CONTROL_AREA_Y_MIN"),
                min_value=0.0,
                max_value=1.0,
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.0, 1.0),
            ),
            ConfigField(
                "CONTROL_AREA_Y_MAX",
                "Área de controle Y máxima (0.0-1.0)",
                "float",
                ConfigDefaults.get_default("CONTROL_AREA_Y_MAX"),
                min_value=0.0,
                max_value=1.0,
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.0, 1.0),
            ),
            ConfigField(
                "INVERT_X_AXIS",
                "Inverter eixo X",
                "boolean",
                ConfigDefaults.get_default("INVERT_X_AXIS"),
                tooltip="Inverte o movimento horizontal do mouse",
            ),
            ConfigField(
                "INVERT_Y_AXIS",
                "Inverter eixo Y",
                "boolean",
                ConfigDefaults.get_default("INVERT_Y_AXIS"),
                tooltip="Inverte o movimento vertical do mouse",
            ),
        ],
        "Temporização": [
            ConfigField(
                "CLICK_DEBOUNCE_TIME",
                "Tempo entre cliques (segundos)",
                "float",
                ConfigDefaults.get_default("CLICK_DEBOUNCE_TIME"),
                min_value=0.1,
                max_value=5.0,
                tooltip="Tempo mínimo entre cliques consecutivos",
                validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.1, 5.0),
            ),
        ],
        "Performance": [
            ConfigField(
                "PROCESS_EVERY_N_FRAMES",
                "Processar a cada N frames",
                "int",
                ConfigDefaults.get_default("PROCESS_EVERY_N_FRAMES"),
                min_value=1,
                max_value=10,
                tooltip="Processa apenas 1 a cada N frames para melhor performance",
                validation_func=ConfigValidator.validate_positive_int,
            ),
        ],
    }


# --------------------------------------------------------------------------- #
# ToolTip                                                                     #
# --------------------------------------------------------------------------- #
class ToolTip:
    """Classe para adicionar tooltips aos widgets."""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        x, y, _, _ = (
            self.widget.bbox("insert") if hasattr(self.widget, "bbox") else (0, 0, 0, 0)
        )
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(
            self.tooltip_window,
            text=self.text,
            background="lightyellow",
            relief="solid",
            borderwidth=1,
            font=("Arial", 8),
        )
        label.pack()

    def on_leave(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


# --------------------------------------------------------------------------- #
# Config GUI                                                                  #
# --------------------------------------------------------------------------- #
class ConfigGUI:
    """Interface gráfica para configuração do Pisk&Click."""

    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()

        self.profile_manager = UserProfileManager()
        self.current_profile = "default"
        self.config_vars: Dict[str, tk.Variable] = {}
        self.tooltips = []

        self.create_widgets()
        self.load_current_config_from_defaults()
        self.load_profile("default")
        self.update_profile_dropdown()

    # --- Janela ------------------------------------------------------------- #
    def setup_window(self):
        self.root.title("Pisk&Click - Configurações")
        self.root.geometry("800x900")
        self.root.resizable(True, True)
        ttk.Style().theme_use("clam")
        self.center_window()

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # --- Widgets ----------------------------------------------------------- #
    def create_widgets(self):
        self.setup_scrollable_frame()
        self.create_title()
        self.create_profile_section()
        self.create_config_sections()
        self.create_action_buttons()

    def setup_scrollable_frame(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_title(self):
        title_label = ttk.Label(
            self.scrollable_frame,
            text="Configurações do Pisk&Click",
            font=("Arial", 18, "bold"),
        )
        title_label.pack(pady=(0, 20))

    def create_profile_section(self):
        frame = ttk.LabelFrame(self.scrollable_frame, text="Gerenciamento de Perfis", padding=15)
        frame.pack(fill=tk.X, pady=10)

        ttk.Label(frame, text="Perfil Atual:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )

        self.profile_name_var = tk.StringVar(value=self.current_profile)
        self.profile_dropdown = ttk.Combobox(
            frame, textvariable=self.profile_name_var, state="readonly", width=20
        )
        self.profile_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.profile_dropdown.bind("<<ComboboxSelected>>", self.on_profile_selected)

        ttk.Button(frame, text="Novo Perfil", command=self.create_new_profile).grid(
            row=0, column=2, padx=5, pady=5
        )

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")
        ttk.Button(button_frame, text="Salvar Perfil", command=self.save_current_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Carregar Perfil", command=self.load_selected_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Excluir Perfil", command=self.delete_selected_profile).pack(side=tk.LEFT, padx=5)

        frame.grid_columnconfigure(1, weight=1)

    def create_config_sections(self):
        for section_name, fields in ConfigSections.SECTIONS.items():
            self.create_section(self.scrollable_frame, section_name, fields)

    def create_section(self, parent, title: str, config_fields: list):
        section_frame = ttk.LabelFrame(parent, text=title, padding=15)
        section_frame.pack(fill=tk.X, pady=10)

        for field in config_fields:
            row_frame = ttk.Frame(section_frame)
            row_frame.pack(fill=tk.X, pady=8)

            label = ttk.Label(row_frame, text=field.label, width=45, font=("Arial", 9))
            label.pack(side=tk.LEFT, anchor="w")
            if field.tooltip:
                ToolTip(label, field.tooltip)

            widget = self.create_input_widget(row_frame, field)
            widget.pack(side=tk.RIGHT, anchor="e")
            if field.tooltip:
                ToolTip(widget, field.tooltip)

    def create_input_widget(self, parent, field: ConfigField):
        if field.field_type == "boolean":
            var = tk.BooleanVar(value=field.default_value)
            widget = ttk.Checkbutton(parent, variable=var)
        elif field.field_type == "int":
            var = tk.IntVar(value=field.default_value)
            widget = ttk.Spinbox(
                parent,
                from_=field.min_value if field.min_value is not None else 1,
                to=field.max_value if field.max_value is not None else 100,
                textvariable=var,
                width=15,
                validate="key",
                validatecommand=(self.root.register(lambda P: P.isdigit() or P == ""), "%P"),
            )
        elif field.field_type == "float":
            var = tk.DoubleVar(value=field.default_value)
            widget = ttk.Spinbox(
                parent,
                from_=field.min_value if field.min_value is not None else 0.0,
                to=field.max_value if field.max_value is not None else 1.0,
                increment=0.01,
                textvariable=var,
                width=15,
            )
        elif field.field_type == "string":
            var = tk.StringVar(value=field.default_value)
            widget = ttk.Entry(parent, textvariable=var, width=20)
        else:
            raise ValueError(f"Tipo de campo desconhecido: {field.field_type}")

        self.config_vars[field.name] = var
        return widget

    def create_action_buttons(self):
        frame = ttk.Frame(self.scrollable_frame)
        frame.pack(fill=tk.X, pady=20)
        ttk.Button(frame, text="Salvar Configuração", command=self.save_current_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Fechar", command=self.root.destroy).pack(side=tk.RIGHT, padx=5)

    # --- Perfil e Configuração --------------------------------------------- #
    def load_current_config_from_defaults(self):
        for section in ConfigSections.SECTIONS.values():
            for field in section:
                var = self.config_vars.get(field.name)
                if var is not None:
                    var.set(ConfigDefaults.get_default(field.name))

    def get_config_values(self) -> Dict[str, Any]:
        return {key: var.get() for key, var in self.config_vars.items()}

    def apply_loaded_config(self, config: Dict[str, Any]):
        for key, value in config.items():
            if key in self.config_vars:
                self.config_vars[key].set(value)

    def save_current_profile(self):
        config = self.get_config_values()
        try:
            self.profile_manager.save_profile_config(self.current_profile, config)
            self.save_to_config_file(config)
            messagebox.showinfo("Configuração", "Configurações salvas com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar configurações: {e}")

    def save_to_config_file(self, config: Dict[str, Any]):
        try:
            with open("config.py", "w", encoding="utf-8") as f:
                f.write(self.generate_config_content(config))
        except Exception as e:
            logger.error(f"Erro ao salvar config.py: {e}")
            raise

    def generate_config_content(self, config: Dict[str, Any]) -> str:
        return f'''# --- Constantes e Configurações ---

# Índices dos landmarks faciais (Mediapipe Face Mesh)
NOSE_TIP_INDEX = {config["NOSE_TIP_INDEX"]}
LEFT_EYE_LANDMARKS_IDXS = {config["LEFT_EYE_LANDMARKS_IDXS"]}
RIGHT_EYE_LANDMARKS_IDXS = {config["RIGHT_EYE_LANDMARKS_IDXS"]}

# Qualidade vs Desempenho Mediapipe
REFINE_LANDMARKS = {config["REFINE_LANDMARKS"]}

# Limiares e Contadores para Detecção de Piscada
EAR_THRESHOLD = {config["EAR_THRESHOLD"]}
BLINK_CONSECUTIVE_FRAMES = {config["BLINK_CONSECUTIVE_FRAMES"]}

# Suavização do Movimento do Mouse
SMOOTHING_FACTOR = {config["SMOOTHING_FACTOR"]}

# Área de Controle do Rosto (Mapeamento Câmera -> Tela)
CONTROL_AREA_X_MIN = {config["CONTROL_AREA_X_MIN"]}
CONTROL_AREA_X_MAX = {config["CONTROL_AREA_X_MAX"]}
CONTROL_AREA_Y_MIN = {config["CONTROL_AREA_Y_MIN"]}
CONTROL_AREA_Y_MAX = {config["CONTROL_AREA_Y_MAX"]}

# Inversão de Eixos (Opcional)
INVERT_X_AXIS = {config["INVERT_X_AXIS"]}
INVERT_Y_AXIS = {config["INVERT_Y_AXIS"]}

# Debounce para Cliques
CLICK_DEBOUNCE_TIME = {config["CLICK_DEBOUNCE_TIME"]}

# Otimização de Desempenho (Opcional)
PROCESS_EVERY_N_FRAMES = {config["PROCESS_EVERY_N_FRAMES"]}
'''

    def load_profile(self, profile_name: str):
        config = self.profile_manager.load_profile_config(profile_name)
        if config:
            self.apply_loaded_config(config)
            self.current_profile = profile_name

    def load_selected_profile(self):
        profile_name = self.profile_name_var.get()
        self.load_profile(profile_name)

    def delete_selected_profile(self):
        profile_name = self.profile_name_var.get()
        if messagebox.askyesno("Excluir", f"Deseja excluir o perfil '{profile_name}'?"):
            self.profile_manager.delete_profile(profile_name)
            self.current_profile = "default"
            self.profile_name_var.set(self.current_profile)
            self.update_profile_dropdown()
            self.load_profile(self.current_profile)

    def create_new_profile(self):
        name = simpledialog.askstring("Novo Perfil", "Nome do perfil:")
        if not name:
            return
        if name in self.profile_manager.list_profiles():
            messagebox.showerror("Erro", "Perfil já existe.")
            return
        self.profile_manager.create_profile(name, self.get_config_values())
        self.update_profile_dropdown()
        self.profile_name_var.set(name)
        self.current_profile = name

    def on_profile_selected(self, event=None):
        self.load_profile(self.profile_name_var.get())

    def update_profile_dropdown(self):
        profiles = self.profile_manager.list_profiles()
        if "default" not in profiles:
            profiles.insert(0, "default")
        self.profile_dropdown["values"] = profiles

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    gui = ConfigGUI()
    gui.run()
