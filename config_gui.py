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
# Tema e Cores Personalizadas                                                #
# --------------------------------------------------------------------------- #
class ModernTheme:
    """Classe para definir o tema moderno da aplicação."""
    
    # Paleta de cores principal
    PRIMARY = "#2E3440"      # Azul escuro elegante
    SECONDARY = "#3B4252"    # Azul médio
    ACCENT = "#5E81AC"       # Azul claro
    SUCCESS = "#A3BE8C"      # Verde suave
    WARNING = "#EBCB8B"      # Amarelo suave
    ERROR = "#BF616A"        # Vermelho suave
    
    # Cores de fundo com gradientes
    BG_PRIMARY = "#ECEFF4"   # Branco gelo
    BG_SECONDARY = "#E5E9F0" # Cinza muito claro
    BG_CARD = "#FFFFFF"      # Branco puro
    BG_GRADIENT_START = "#ECEFF4"  # Início do gradiente de fundo
    BG_GRADIENT_END = "#E5E9F0"    # Fim do gradiente de fundo
    
    # Cores de texto com variações
    TEXT_PRIMARY = "#2E3440" # Texto principal
    TEXT_SECONDARY = "#4C566A" # Texto secundário
    TEXT_MUTED = "#6B7280"   # Texto esmaecido
    TEXT_HIGHLIGHT = "#FFFFFF" # Texto destacado
    
    # Gradientes melhorados
    GRADIENT_START = "#667eea"
    GRADIENT_END = "#764ba2"
    GRADIENT_ACCENT_START = "#5E81AC"
    GRADIENT_ACCENT_END = "#81A1C1"
    
    # Cores de brilho e sombra
    GLOW_COLOR = "#5E81AC33"    # Brilho sutil
    SHADOW_COLOR = "#2E344080"  # Sombra suave
    BORDER_LIGHT = "#D8DEE9"    # Borda clara
    BORDER_DARK = "#4C566A"     # Borda escura
    
    @classmethod
    def configure_style(cls):
        """Configura o estilo ttk com o tema moderno."""
        style = ttk.Style()
        
        # Configurar tema base
        style.theme_use('clam')
        
        # Configurar cores gerais com gradientes sutis
        style.configure('TLabel', 
                       background=cls.BG_PRIMARY,
                       foreground=cls.TEXT_PRIMARY,
                       font=('Arial', 10))
        
        style.configure('TFrame',
                       background=cls.BG_PRIMARY,
                       relief='flat')
        
        # Configurar estilos com gradientes
        style.configure('Gradient.TFrame',
                       background=cls.BG_GRADIENT_START,
                       relief='flat')
        
        style.configure('Card.TFrame',
                       background=cls.BG_CARD,
                       relief='solid',
                       borderwidth=1,
                       bordercolor=cls.BORDER_LIGHT)
        
        # Configurar LabelFrame com estilo moderno e sombras
        style.configure('Modern.TLabelframe',
                       background=cls.BG_CARD,
                       borderwidth=2,
                       relief='solid',
                       bordercolor=cls.ACCENT,
                       lightcolor=cls.GLOW_COLOR,
                       darkcolor=cls.SHADOW_COLOR)
        
        style.configure('Modern.TLabelframe.Label',
                       background=cls.BG_CARD,
                       foreground=cls.ACCENT,
                       font=('Arial', 11, 'bold'))
        
        # Configurar botões modernos com gradientes
        style.configure('Modern.TButton',
                       background=cls.ACCENT,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Arial', 10, 'bold'),
                       padding=(20, 10))
        
        style.map('Modern.TButton',
                 background=[('active', cls.GRADIENT_ACCENT_START),
                           ('pressed', cls.GRADIENT_ACCENT_END),
                           ('!active', cls.ACCENT)],
                 relief=[('pressed', 'sunken'),
                        ('!pressed', 'raised')])
        
        # Configurar Entry (campos de texto) com efeitos visuais
        style.configure('Modern.TEntry',
                       fieldbackground=cls.BG_CARD,
                       background=cls.BG_CARD,
                       foreground=cls.TEXT_PRIMARY,
                       borderwidth=2,
                       relief='solid',
                       insertcolor=cls.ACCENT,
                       font=('Arial', 10),
                       padding=(8, 6))
        
        style.map('Modern.TEntry',
                 focuscolor=[('focus', cls.ACCENT)],
                 bordercolor=[('focus', cls.ACCENT),
                            ('!focus', cls.BG_SECONDARY)],
                 lightcolor=[('focus', cls.GLOW_COLOR),
                           ('!focus', cls.BG_CARD)])
        
        # Configurar Combobox com efeitos visuais
        style.configure('Modern.TCombobox',
                       fieldbackground=cls.BG_CARD,
                       background=cls.ACCENT,
                       foreground=cls.TEXT_PRIMARY,
                       borderwidth=2,
                       relief='solid',
                       bordercolor=cls.ACCENT)
        
        style.map('Modern.TCombobox',
                 bordercolor=[('focus', cls.ACCENT),
                            ('!focus', cls.BORDER_LIGHT)],
                 lightcolor=[('focus', cls.GLOW_COLOR),
                           ('!focus', cls.BG_CARD)])
        
        # Configurar Spinbox com configuração simplificada e efetiva
        style.configure('Modern.TSpinbox',
                       fieldbackground=cls.BG_CARD,
                       background='#ffffff',
                       foreground=cls.TEXT_PRIMARY,
                       borderwidth=1,
                       relief='solid',
                       bordercolor=cls.ACCENT,
                       arrowcolor='#000000',
                       arrowsize=16,
                       padding=(8, 4))
        
        # Mapear cores das setas diretamente no Spinbox principal
        style.map('Modern.TSpinbox',
                 bordercolor=[('focus', cls.ACCENT),
                            ('!focus', cls.BORDER_LIGHT)],
                 arrowcolor=[('active', '#ff0000'),  # Vermelho para teste de visibilidade
                           ('pressed', '#ff0000'),
                           ('!active', '#000000')])
        
        # Remover configurações duplicadas - usando apenas a configuração principal do Spinbox
        
        # Configurar Checkbutton com efeitos hover
        style.configure('Modern.TCheckbutton',
                       background=cls.BG_CARD,
                       foreground=cls.TEXT_PRIMARY,
                       focuscolor='none',
                       font=('Arial', 10))
        
        style.map('Modern.TCheckbutton',
                 background=[('active', cls.BG_SECONDARY),
                           ('!active', cls.BG_CARD)],
                 foreground=[('active', cls.ACCENT),
                           ('!active', cls.TEXT_PRIMARY)])
        
        return style

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
# ToolTip Moderno                                                             #
# --------------------------------------------------------------------------- #
class ModernToolTip:
    """Tooltip moderno com design elegante e animações suaves."""

    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.show_timer = None
        self.fade_job = None
        
        # Bind eventos
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)

    def on_enter(self, event=None):
        """Inicia timer para mostrar tooltip."""
        self.cancel_timer()
        self.show_timer = self.widget.after(self.delay, self.show_tooltip)

    def on_leave(self, event=None):
        """Esconde tooltip e cancela timer."""
        self.cancel_timer()
        self.hide_tooltip()

    def cancel_timer(self):
        """Cancela timer pendente."""
        if self.show_timer:
            self.widget.after_cancel(self.show_timer)
            self.show_timer = None
        if self.fade_job:
            self.widget.after_cancel(self.fade_job)
            self.fade_job = None

    def show_tooltip(self, event=None):
        """Mostra o tooltip com design melhorado."""
        if self.tooltip_window or not self.text:
            return
        
        # Calcular posição otimizada
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() - 40
        
        # Ajustar se sair da tela
        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()
        
        if x + 200 > screen_width:
            x = screen_width - 220
        if y < 0:
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10

        # Criar janela do tooltip
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.attributes('-alpha', 0.0)
        self.tooltip_window.attributes('-topmost', True)
        
        # Frame principal com bordas melhoradas
        main_frame = tk.Frame(
            self.tooltip_window,
            bg=ModernTheme.PRIMARY,
            relief='flat',
            bd=0
        )
        main_frame.pack(padx=3, pady=3)
        
        # Frame interno com gradiente simulado
        content_frame = tk.Frame(
            main_frame,
            bg=ModernTheme.BG_CARD,
            relief='flat',
            bd=1
        )
        content_frame.pack(padx=1, pady=1)
        
        # Ícone informativo
        icon_label = tk.Label(
            content_frame,
            text="💡",
            bg=ModernTheme.BG_CARD,
            font=('Segoe UI', 10),
            padx=5,
            pady=2
        )
        icon_label.pack(side=tk.LEFT, anchor="nw")
        
        # Label com texto estilizado
        text_label = tk.Label(
            content_frame,
            text=self.text,
            bg=ModernTheme.BG_CARD,
            fg=ModernTheme.TEXT_PRIMARY,
            font=('Segoe UI', 9),
            padx=8,
            pady=8,
            justify='left',
            wraplength=280,
            anchor="w"
        )
        text_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Efeito de fade-in suave
        self.fade_in()

    def fade_in(self, alpha=0.0):
        """Efeito de fade-in suave para o tooltip."""
        if self.tooltip_window and alpha < 0.95:
            alpha += 0.08
            try:
                self.tooltip_window.attributes('-alpha', alpha)
                self.fade_job = self.widget.after(15, lambda: self.fade_in(alpha))
            except tk.TclError:
                pass

    def hide_tooltip(self, event=None):
        """Esconde o tooltip."""
        if self.tooltip_window:
            try:
                self.tooltip_window.destroy()
            except tk.TclError:
                pass
            self.tooltip_window = None

    def on_motion(self, event=None):
        """Atualiza posição do tooltip se necessário."""
        pass

# Manter compatibilidade com código existente
ToolTip = ModernToolTip


# --------------------------------------------------------------------------- #
# Config GUI                                                                  #
# --------------------------------------------------------------------------- #
class ConfigGUI:
    """Interface gráfica para configuração do Pisk&Click."""

    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Configurar tema moderno
        self.style = ModernTheme.configure_style()
        
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
        """Configura a janela principal com design moderno."""
        self.root.title("🎯 Pisk&Click - Configurações Avançadas")
        self.root.geometry("1000x800")
        self.root.configure(bg=ModernTheme.BG_PRIMARY)
        
        # Configurar fonte padrão do sistema
        self.root.option_add('*Font', 'Arial 10')
        
        # Configurar comportamento da janela
        self.root.minsize(900, 600)
        self.root.resizable(True, True)
        
        # Configurar grid weights para responsividade
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
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
        """Cria um frame com scroll para o conteúdo."""
        # Container principal com padding responsivo
        main_container = tk.Frame(self.root, bg=ModernTheme.BG_PRIMARY)
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)
        
        # Configurar grid weights para responsividade
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Canvas para scroll com bordas suaves
        self.canvas = tk.Canvas(
            main_container, 
            bg=ModernTheme.BG_PRIMARY,
            highlightthickness=0,
            relief="flat",
            bd=0
        )
        
        # Scrollbar estilizada
        scrollbar = ttk.Scrollbar(
            main_container, 
            orient="vertical", 
            command=self.canvas.yview
        )
        
        # Frame scrollable com padding interno
        self.scrollable_frame = tk.Frame(self.canvas, bg=ModernTheme.BG_PRIMARY)
        
        # Configurar scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Configurar redimensionamento do canvas
        def configure_canvas(event):
            canvas_width = event.width
            self.canvas.itemconfig(canvas_window, width=canvas_width)
        
        self.canvas.bind('<Configure>', configure_canvas)
        
        # Criar janela no canvas
        canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout com grid para melhor controle
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind mouse wheel para scroll suave
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_title(self):
        # Container para o cabeçalho
        header_frame = tk.Frame(self.scrollable_frame, bg=ModernTheme.BG_PRIMARY)
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Título principal com gradiente simulado
        title_frame = tk.Frame(header_frame, bg=ModernTheme.ACCENT, height=80)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🎯 Configurações Avançadas",
            font=("Arial", 24, "bold"),
            bg=ModernTheme.ACCENT,
            fg="white"
        )
        title_label.pack(expand=True)
        
        # Subtítulo
        subtitle_label = tk.Label(
            header_frame,
            text="Personalize sua experiência com o Pisk&Click",
            font=("Arial", 12),
            bg=ModernTheme.BG_PRIMARY,
            fg=ModernTheme.TEXT_SECONDARY
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Linha decorativa
        separator = tk.Frame(header_frame, height=2, bg=ModernTheme.ACCENT)
        separator.pack(fill=tk.X, pady=(0, 10))

    def create_profile_section(self):
        # Frame principal com estilo moderno
        frame = ttk.LabelFrame(
            self.scrollable_frame, 
            text="👤 Gerenciamento de Perfis", 
            style="Modern.TLabelframe",
            padding=20
        )
        frame.pack(fill=tk.X, pady=(0, 20))

        # Seção de seleção de perfil
        profile_select_frame = tk.Frame(frame, bg=ModernTheme.BG_CARD)
        profile_select_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            profile_select_frame, 
            text="Perfil Atual:", 
            font=("Arial", 11, "bold"),
            bg=ModernTheme.BG_CARD,
            fg=ModernTheme.TEXT_PRIMARY
        ).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")

        self.profile_name_var = tk.StringVar(value=self.current_profile)
        self.profile_dropdown = ttk.Combobox(
            profile_select_frame, 
            textvariable=self.profile_name_var, 
            state="readonly", 
            width=25,
            style="Modern.TCombobox",
            font=("Arial", 10)
        )
        self.profile_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.profile_dropdown.bind("<<ComboboxSelected>>", self.on_profile_selected)

        ttk.Button(
            profile_select_frame, 
            text="➕ Novo", 
            command=self.create_new_profile,
            style="Modern.TButton"
        ).grid(row=0, column=2, padx=(10, 0), pady=5)

        # Seção de botões de ação
        button_frame = tk.Frame(frame, bg=ModernTheme.BG_CARD)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botões com ícones e estilos modernos
        buttons_data = [
            ("💾 Salvar", self.save_current_profile, ModernTheme.SUCCESS),
            ("📂 Carregar", self.load_selected_profile, ModernTheme.ACCENT),
            ("🗑️ Excluir", self.delete_selected_profile, ModernTheme.ERROR)
        ]
        
        for i, (text, command, color) in enumerate(buttons_data):
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=("Arial", 10, "bold"),
                relief="flat",
                padx=20,
                pady=8,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=(0, 10) if i < len(buttons_data)-1 else 0)
            
            # Efeito hover
            def on_enter(e, button=btn, original_color=color):
                button.configure(bg=self._darken_color(original_color))
            def on_leave(e, button=btn, original_color=color):
                button.configure(bg=original_color)
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

        profile_select_frame.grid_columnconfigure(1, weight=1)
        
    def _darken_color(self, color):
        """Escurece uma cor hex para efeito hover."""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, c - 30) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def create_config_sections(self):
        for section_name, fields in ConfigSections.SECTIONS.items():
            self.create_section(self.scrollable_frame, section_name, fields)

    def create_section(self, parent, title: str, config_fields: list):
        # Ícones melhorados para cada seção com símbolos mais expressivos
        section_icons = {
            "Detecção Facial": "👁️",
            "Controle do Mouse": "🎯",
            "Temporização": "⏱️",
            "Performance": "⚡",
            "Configurações de Clique": "🎯",
            "Configurações de Teclado": "⌨️",
            "Configurações de Interface": "🎨",
            "Configurações Avançadas": "⚙️",
            "Configurações de Sistema": "💻",
            "Configurações de Performance": "⚡",
            "Configurações de Áudio": "🔊",
            "Configurações de Rede": "🌐",
            "Configurações de Segurança": "🔒",
            "Configurações Gerais": "📋"
        }
        
        icon = section_icons.get(title, "⚙️")
        
        # Frame da seção com estilo moderno e espaçamento melhorado
        section_frame = ttk.LabelFrame(
            parent, 
            text=f"  {icon} {title}  ", 
            style="Modern.TLabelframe",
            padding=(25, 20)
        )
        section_frame.pack(fill=tk.X, padx=15, pady=12)
        
        # Configurar grid weights para responsividade
        section_frame.grid_columnconfigure(0, weight=1)

        for i, field in enumerate(config_fields):
            # Container para cada campo com espaçamento otimizado
            row_frame = tk.Frame(section_frame, bg=ModernTheme.BG_CARD)
            row_frame.pack(fill=tk.X, pady=10, padx=5)
            
            # Configurar grid weights para campos
            row_frame.grid_columnconfigure(0, weight=1)
            
            # Frame para label com melhor alinhamento
            label_frame = tk.Frame(row_frame, bg=ModernTheme.BG_CARD)
            label_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Label estilizado com wraplength para responsividade
            label = tk.Label(
                label_frame, 
                text=field.label, 
                font=("Arial", 10),
                bg=ModernTheme.BG_CARD,
                fg=ModernTheme.TEXT_PRIMARY,
                anchor="w",
                justify="left",
                wraplength=400
            )
            label.pack(side=tk.LEFT, anchor="w", padx=(0, 15))
            
            if field.tooltip:
                ToolTip(label, field.tooltip)

            # Widget de entrada estilizado
            widget_frame = tk.Frame(row_frame, bg=ModernTheme.BG_CARD)
            widget_frame.pack(side=tk.RIGHT, anchor="e")
            
            widget = self.create_input_widget(widget_frame, field)
            widget.pack(side=tk.RIGHT, anchor="e")
            
            if field.tooltip:
                ToolTip(widget, field.tooltip)
                
            # Linha separadora sutil entre campos (exceto o último)
            if i < len(config_fields) - 1:
                separator = tk.Frame(
                    section_frame, 
                    height=1, 
                    bg=ModernTheme.BG_SECONDARY
                )
                separator.pack(fill=tk.X, pady=(8, 0), padx=10)

    def create_input_widget(self, parent, field: ConfigField):
        # Container para o widget com melhor espaçamento
        widget_container = tk.Frame(parent, bg=ModernTheme.BG_CARD)
        
        if field.field_type == "boolean":
            var = tk.BooleanVar(value=field.default_value)
            widget = ttk.Checkbutton(
                widget_container, 
                variable=var,
                style="Modern.TCheckbutton"
            )
            widget.pack(padx=8, pady=4)
            
        elif field.field_type == "int":
            var = tk.IntVar(value=field.default_value)
            widget = ttk.Spinbox(
                widget_container,
                from_=field.min_value if field.min_value is not None else 1,
                to=field.max_value if field.max_value is not None else 100,
                textvariable=var,
                width=18,
                style="Modern.TSpinbox",
                font=("Arial", 10),
                validate="key",
                validatecommand=(self.root.register(lambda P: P.isdigit() or P == ""), "%P"),
            )
            widget.pack(padx=8, pady=4)
            
        elif field.field_type == "float":
            var = tk.DoubleVar(value=field.default_value)
            widget = ttk.Spinbox(
                widget_container,
                from_=field.min_value if field.min_value is not None else 0.0,
                to=field.max_value if field.max_value is not None else 1.0,
                increment=0.01,
                textvariable=var,
                width=18,
                style="Modern.TSpinbox",
                font=("Arial", 10),
            )
            widget.pack(padx=8, pady=4)
            
        elif field.field_type == "string":
            var = tk.StringVar(value=field.default_value)
            widget = ttk.Entry(
                widget_container, 
                textvariable=var, 
                width=25,
                style="Modern.TEntry",
                font=("Segoe UI", 10)
            )
            widget.pack(padx=8, pady=4)
            
        else:
            raise ValueError(f"Tipo de campo desconhecido: {field.field_type}")

        self.config_vars[field.name] = var
        return widget_container

    def create_action_buttons(self):
        """Cria botões de ação com design moderno."""
        # Frame para botões com fundo elegante e espaçamento melhorado
        button_frame = tk.Frame(
            self.scrollable_frame, 
            bg=ModernTheme.BG_PRIMARY,
            pady=25
        )
        button_frame.pack(fill="x", padx=25, pady=(35, 25))
        
        # Configurar grid para responsividade
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        
        # Container interno para centralizar botões
        inner_frame = tk.Frame(button_frame, bg=ModernTheme.BG_PRIMARY)
        inner_frame.grid(row=0, column=1, sticky="ew", padx=20)
        
        # Configurar grid do container interno
        inner_frame.grid_columnconfigure(0, weight=1)
        inner_frame.grid_columnconfigure(1, weight=1)
        inner_frame.grid_columnconfigure(2, weight=1)
        
        # Botão Salvar
        save_btn = ttk.Button(
            inner_frame,
            text="💾 Salvar Configurações",
            command=self.save_current_profile,
            style="Modern.TButton",
            width=22
        )
        save_btn.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        
        # Botão Fechar
        close_btn = ttk.Button(
            inner_frame,
            text="❌ Fechar",
            command=self.root.destroy,
            style="Modern.TButton",
            width=22
        )
        close_btn.grid(row=0, column=2, padx=(10, 0), pady=5, sticky="ew")
        
        # Adicionar tooltips melhorados
        ModernToolTip(save_btn, "Salva as configurações atuais no arquivo de configuração")
        ModernToolTip(close_btn, "Fecha a janela de configurações")

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
        # Usar valores padrão para campos que não estão na interface
        nose_tip_index = config.get("NOSE_TIP_INDEX", ConfigDefaults.get_default("NOSE_TIP_INDEX"))
        left_eye_landmarks = config.get("LEFT_EYE_LANDMARKS_IDXS", ConfigDefaults.get_default("LEFT_EYE_LANDMARKS_IDXS"))
        right_eye_landmarks = config.get("RIGHT_EYE_LANDMARKS_IDXS", ConfigDefaults.get_default("RIGHT_EYE_LANDMARKS_IDXS"))
        
        return f'''# --- Constantes e Configurações ---

# Índices dos landmarks faciais (Mediapipe Face Mesh)
NOSE_TIP_INDEX = {nose_tip_index}
LEFT_EYE_LANDMARKS_IDXS = {left_eye_landmarks}
RIGHT_EYE_LANDMARKS_IDXS = {right_eye_landmarks}

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
