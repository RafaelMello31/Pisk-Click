import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

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
       "REFINE_LANDMARKS": False,
       "EAR_THRESHOLD": 0.25,
       "BLINK_CONSECUTIVE_FRAMES": 2,
       "SMOOTHING_FACTOR": 0.7,
       "CONTROL_AREA_X_MIN": 0.3,
       "CONTROL_AREA_X_MAX": 0.7,
       "CONTROL_AREA_Y_MIN": 0.3,
       "CONTROL_AREA_Y_MAX": 0.7,
       "INVERT_X_AXIS": False,
       "INVERT_Y_AXIS": False,
       "CLICK_DEBOUNCE_TIME": 0.5,
       "PROCESS_EVERY_N_FRAMES": 3,
       "ALT_TAB_TRIGGER_BOTH_EYES_BLINK": True,
       "ALT_TAB_DEBOUNCE_TIME": 1.0,
       "HEAD_TILT_THRESHOLD": 15.0,
       "HEAD_TILT_DEBOUNCE_TIME": 0.5,
       "HEAD_TILT_LEFT_TRIGGER_KEY": "left",
       "HEAD_TILT_RIGHT_TRIGGER_KEY": "right",
   }

   @classmethod
   def get_default(cls, key: str) -> Any:
       """Obtém valor padrão com fallback seguro."""
       try:
           from config import *  # noqa
           return globals().get(key, cls.DEFAULTS.get(key))
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

   @staticmethod
   def validate_key_string(value: str) -> bool:
       return isinstance(value, str) and len(value.strip()) > 0


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
           ConfigField(
               "ALT_TAB_DEBOUNCE_TIME",
               "Tempo entre Alt+Tab (segundos)",
               "float",
               ConfigDefaults.get_default("ALT_TAB_DEBOUNCE_TIME"),
               min_value=0.5,
               max_value=10.0,
               tooltip="Tempo mínimo entre comandos Alt+Tab consecutivos",
               validation_func=lambda x: ConfigValidator.validate_float_range(x, 0.5, 10.0),
           ),
           ConfigField(
               "HEAD_TILT_DEBOUNCE_TIME",
               "Tempo entre inclinações da cabeça (segundos)",
               "float",
               ConfigDefaults.get_default("HEAD_TILT_DEBOUNCE_TIME"),
               min_value=0.1,
               max_value=5.0,
               tooltip="Tempo mínimo entre detecções de inclinação da cabeça",
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
       "Funcionalidades": [
           ConfigField(
               "ALT_TAB_TRIGGER_BOTH_EYES_BLINK",
               "Alt+Tab com piscada dupla",
               "boolean",
               ConfigDefaults.get_default("ALT_TAB_TRIGGER_BOTH_EYES_BLINK"),
               tooltip="Ativa Alt+Tab quando ambos os olhos piscam simultaneamente",
           ),
           ConfigField(
               "HEAD_TILT_THRESHOLD",
               "Limiar de inclinação da cabeça (graus)",
               "float",
               ConfigDefaults.get_default("HEAD_TILT_THRESHOLD"),
               min_value=5.0,
               max_value=45.0,
               tooltip="Ângulo mínimo de inclinação da cabeça para trigger",
               validation_func=lambda x: ConfigValidator.validate_float_range(x, 5.0, 45.0),
           ),
           ConfigField(
               "HEAD_TILT_LEFT_TRIGGER_KEY",
               "Tecla para inclinação esquerda",
               "string",
               ConfigDefaults.get_default("HEAD_TILT_LEFT_TRIGGER_KEY"),
               tooltip="Tecla a ser pressionada ao inclinar cabeça para esquerda",
               validation_func=ConfigValidator.validate_key_string,
           ),
           ConfigField(
               "HEAD_TILT_RIGHT_TRIGGER_KEY",
               "Tecla para inclinação direita",
               "string",
               ConfigDefaults.get_default("HEAD_TILT_RIGHT_TRIGGER_KEY"),
               tooltip="Tecla a ser pressionada ao inclinar cabeça para direita",
               validation_func=ConfigValidator.validate_key_string,
           ),
       ],
   }


# --------------------------------------------------------------------------- #
# Profile Manager                                                             #
# --------------------------------------------------------------------------- #
class ProfileManager:
   """Gerenciador simplificado de perfis."""

   def __init__(self, profiles_dir: str = "profiles"):
       self.profiles_dir = profiles_dir
       os.makedirs(profiles_dir, exist_ok=True)

   def list_profiles(self) -> list:
       try:
           return [
               f[:-5] for f in os.listdir(self.profiles_dir) if f.endswith(".json")
           ] or ["default"]
       except Exception as e:
           logger.error(f"Erro ao listar perfis: {e}")
           return ["default"]

   def create_profile(self, name: str, config: Dict[str, Any]) -> bool:
       try:
           with open(self._profile_path(name), "w") as f:
               json.dump(config, f, indent=2)
           return True
       except Exception as e:
           logger.error(f"Erro ao criar perfil {name}: {e}")
           return False

   def save_profile_config(self, name: str, config: Dict[str, Any]) -> bool:
       return self.create_profile(name, config)

   def load_profile_config(self, name: str) -> Optional[Dict[str, Any]]:
       try:
           with open(self._profile_path(name), "r") as f:
               return json.load(f)
       except FileNotFoundError:
           return None
       except Exception as e:
           logger.error(f"Erro ao carregar perfil {name}: {e}")
           return None

   def delete_profile(self, name: str) -> bool:
       try:
           path = self._profile_path(name)
           if os.path.exists(path):
               os.remove(path)
               return True
           return False
       except Exception as e:
           logger.error(f"Erro ao excluir perfil {name}: {e}")
           return False

   def _profile_path(self, name: str) -> str:
       return os.path.join(self.profiles_dir, f"{name}.json")


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

       self.profile_manager = ProfileManager()
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
               from_=field.min_value or 1,
               to=field.max_value or 100,
               textvariable=var,
               width=15,
               validate="key",
               validatecommand=(self.root.register(lambda x: x.isdigit() or x == ""), "%P"),
           )
       elif field.field_type == "float":
           var = tk.DoubleVar(value=field.default_value)
           widget = tt