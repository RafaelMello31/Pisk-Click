#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Moderna de Configurações - Pisk & Click
Design moderno e intuitivo para configurações do sistema.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from pathlib import Path
from PIL import Image, ImageTk, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

class ModernConfigTheme:
    """Tema moderno para configurações."""
    
    # Cores principais
    PRIMARY = "#1a1a2e"
    SECONDARY = "#16213e"
    ACCENT = "#0f4c75"
    SUCCESS = "#00d4aa"
    WARNING = "#ffa726"
    ERROR = "#ef5350"
    INFO = "#42a5f5"
    
    # Backgrounds
    BG_DARK = "#0d1117"
    BG_CARD = "#21262d"
    BG_HOVER = "#30363d"
    BG_INPUT = "#161b22"
    
    # Textos
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#8b949e"
    TEXT_MUTED = "#6e7681"
    
    # Gradientes
    GRADIENT_START = "#667eea"
    GRADIENT_END = "#764ba2"


class ModernSlider(tk.Canvas):
    """Slider moderno customizado."""
    
    def __init__(self, parent, width=300, height=30, min_val=0, max_val=100, 
                 initial_val=50, callback=None, label=""):
        super().__init__(parent, width=width, height=height, highlightthickness=0, 
                        bg=ModernConfigTheme.BG_CARD)
        
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = initial_val
        self.callback = callback
        self.label = label
        self.dragging = False
        
        self.draw_slider()
        self.bind_events()
        
    def draw_slider(self):
        """Desenha o slider."""
        self.delete("all")
        
        # Track
        track_y = self.height // 2
        track_start = 20
        track_end = self.width - 20
        
        self.create_line(track_start, track_y, track_end, track_y, 
                        fill=ModernConfigTheme.BG_HOVER, width=4)
        
        # Progress
        progress_ratio = (self.current_val - self.min_val) / (self.max_val - self.min_val)
        progress_end = track_start + (track_end - track_start) * progress_ratio
        
        self.create_line(track_start, track_y, progress_end, track_y, 
                        fill=ModernConfigTheme.ACCENT, width=4)
        
        # Handle
        handle_x = progress_end
        self.create_oval(handle_x - 8, track_y - 8, handle_x + 8, track_y + 8, 
                        fill=ModernConfigTheme.TEXT_PRIMARY, outline=ModernConfigTheme.ACCENT, width=2)
        
        # Value text
        self.create_text(self.width // 2, 5, text=f"{self.label}: {self.current_val:.2f}", 
                        fill=ModernConfigTheme.TEXT_PRIMARY, font=("Segoe UI", 9, "bold"))
        
    def bind_events(self):
        """Vincula eventos."""
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        
    def on_click(self, event):
        """Clique no slider."""
        self.dragging = True
        self.update_value(event.x)
        
    def on_drag(self, event):
        """Arrastar slider."""
        if self.dragging:
            self.update_value(event.x)
            
    def on_release(self, event):
        """Soltar slider."""
        self.dragging = False
        
    def update_value(self, x):
        """Atualiza valor baseado na posição."""
        track_start = 20
        track_end = self.width - 20
        
        # Calcular novo valor
        ratio = max(0, min(1, (x - track_start) / (track_end - track_start)))
        self.current_val = self.min_val + ratio * (self.max_val - self.min_val)
        
        self.draw_slider()
        
        if self.callback:
            self.callback(self.current_val)
            
    def set_value(self, value):
        """Define valor programaticamente."""
        self.current_val = max(self.min_val, min(self.max_val, value))
        self.draw_slider()


class ModernToggle(tk.Canvas):
    """Toggle switch moderno."""
    
    def __init__(self, parent, width=60, height=30, initial_state=False, callback=None):
        super().__init__(parent, width=width, height=height, highlightthickness=0, 
                        bg=ModernConfigTheme.BG_CARD)
        
        self.width = width
        self.height = height
        self.state = initial_state
        self.callback = callback
        
        self.draw_toggle()
        self.bind("<Button-1>", self.on_click)
        
    def draw_toggle(self):
        """Desenha o toggle."""
        self.delete("all")
        
        # Background
        bg_color = ModernConfigTheme.SUCCESS if self.state else ModernConfigTheme.BG_HOVER
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, 
                                radius=self.height//2, fill=bg_color)
        
        # Handle
        handle_x = self.width - 15 if self.state else 15
        self.create_oval(handle_x - 10, self.height//2 - 10, 
                        handle_x + 10, self.height//2 + 10, 
                        fill=ModernConfigTheme.TEXT_PRIMARY, outline="")
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Cria retângulo arredondado."""
        points = []
        for x, y in [(x1, y1 + radius), (x1, y1), (x1 + radius, y1),
                     (x2 - radius, y1), (x2, y1), (x2, y1 + radius),
                     (x2, y2 - radius), (x2, y2), (x2 - radius, y2),
                     (x1 + radius, y2), (x1, y2), (x1, y2 - radius)]:
            points.extend([x, y])
        return self.create_polygon(points, smooth=True, **kwargs)
        
    def on_click(self, event):
        """Toggle ao clicar."""
        self.state = not self.state
        self.draw_toggle()
        
        if self.callback:
            self.callback(self.state)


class ModernConfigApp:
    """Interface moderna de configurações."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.load_config()
        self.create_widgets()
        
    def setup_window(self):
        """Configura janela."""
        self.root.title("Pisk & Click - Configurações Avançadas")
        self.root.geometry("1000x700")
        self.root.configure(bg=ModernConfigTheme.BG_DARK)
        self.root.resizable(True, True)
        
        # Definir ícone da janela (preferir assets/ com fallback)
        try:
            assets_dir = os.path.join(os.getcwd(), "assets")
            icon_candidates = [
                os.path.join(assets_dir, "pisk_and_click.ico"),
                os.path.join(assets_dir, "pisk_and_click_icon.ico"),
                os.path.join(assets_dir, "logo.ico"),
                os.path.join(assets_dir, "logo.png"),
                "pisk_and_click.ico",
                "pisk_and_click_icon.ico",
                "logo.ico",
                "logo.png",
            ]
            for icon_path in icon_candidates:
                if icon_path.endswith(".ico") and os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
                    break
            else:
                for icon_path in icon_candidates:
                    if icon_path.endswith(".png") and os.path.exists(icon_path):
                        icon_img = tk.PhotoImage(file=icon_path)
                        self.root.iconphoto(True, icon_img)
                        break
        except Exception as e:
            print(f"Aviso: Não foi possível definir ícone da janela: {e}")
        
        # Centralizar
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"1000x700+{x}+{y}")
        
    def load_config(self):
        """Carrega configurações."""
        self.config = {
            'ear_threshold': 0.25,
            'blink_consecutive_frames': 4,
            'smoothing_factor': 0.3,
            'mouse_sensitivity': 1.3,
            'control_area_x_min': 0.25,
            'control_area_x_max': 0.75,
            'control_area_y_min': 0.25,
            'control_area_y_max': 0.75,
            'click_debounce_time': 0.4,
            'double_blink_protection': True,
            'process_every_n_frames': 1
        }
        
        # Tentar carregar do arquivo
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
        except:
            pass
            
    def create_widgets(self):
        """Cria interface."""
        # Header
        self.create_header()
        
        # Notebook para abas
        self.create_notebook()
        
        # Footer
        self.create_footer()
        
    def create_header(self):
        """Cria cabeçalho responsivo com logo."""
        header_frame = tk.Frame(self.root, bg=ModernConfigTheme.PRIMARY, height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Canvas para gradiente responsivo
        header_canvas = tk.Canvas(header_frame, height=100, highlightthickness=0)
        header_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Carregar logo otimizado
        self.logo_image = None
        try:
            # Preferir logo em assets/
            assets_logo = os.path.join(os.getcwd(), "assets", "logo.png")
            logo_path = assets_logo if os.path.exists(assets_logo) else "logo.png"
            
            if logo_path:
                try:
                    logo_pil = Image.open(logo_path)
                    
                    # Redimensionar o logo
                    logo_height = 50
                    aspect_ratio = logo_pil.width / logo_pil.height
                    logo_width = int(logo_height * aspect_ratio)
                    logo_pil = logo_pil.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                    
                    self.logo_image = ImageTk.PhotoImage(logo_pil)
                except Exception:
                    # Fallback para PhotoImage se PIL falhar
                    try:
                        self.logo_image = tk.PhotoImage(file=logo_path)
                    except Exception:
                        self.logo_image = None
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
        
        # Função para redesenhar header
        def redraw_header(event=None):
            header_canvas.delete("all")
            width = header_canvas.winfo_width()
            height = header_canvas.winfo_height()
            
            if width > 1:
                # Gradiente responsivo
                self.create_gradient(header_canvas, ModernConfigTheme.GRADIENT_START, 
                                   ModernConfigTheme.GRADIENT_END, width, height)
                
                # Posições responsivas
                center_x = width // 2

                # Posicionar logo com margem fixa e textos ancorados à esquerda
                margin = 20
                if self.logo_image:
                    logo_w = self.logo_image.width()
                    logo_h = self.logo_image.height()
                    logo_x = margin + (logo_w // 2)
                    logo_y = int(height * 0.5)
                    header_canvas.create_image(logo_x, logo_y, image=self.logo_image, anchor="center")
                    text_x = margin + logo_w + 20
                else:
                    text_x = margin

                # Título responsivo (ancorado à esquerda, sem sobreposição)
                title_size = min(24, max(16, width // 45))
                header_canvas.create_text(text_x, int(height * 0.4), text="CONFIGURAÇÕES AVANÇADAS",
                                         fill=ModernConfigTheme.TEXT_PRIMARY,
                                         font=("Segoe UI", title_size, "bold"),
                                         anchor="w")

                # Subtítulo responsivo
                subtitle_size = min(12, max(9, width // 90))
                header_canvas.create_text(text_x, int(height * 0.7), text="Personalize o comportamento do sistema",
                                         fill=ModernConfigTheme.TEXT_SECONDARY,
                                         font=("Segoe UI", subtitle_size),
                                         anchor="w")
        
        header_canvas.bind("<Configure>", redraw_header)
        header_canvas.after(1, redraw_header)
        
    def create_notebook(self):
        """Cria notebook com abas."""
        # Container
        notebook_frame = tk.Frame(self.root, bg=ModernConfigTheme.BG_DARK)
        notebook_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Notebook customizado
        self.notebook = ttk.Notebook(notebook_frame)
        
        # Configurar estilo
        style = ttk.Style()
        style.configure('Modern.TNotebook', background=ModernConfigTheme.BG_DARK)
        style.configure('Modern.TNotebook.Tab', 
                       background=ModernConfigTheme.BG_CARD,
                       foreground=ModernConfigTheme.TEXT_SECONDARY,
                       padding=[20, 10])
        
        # Abas
        self.create_detection_tab()
        self.create_mouse_tab()
        self.create_advanced_tab()
        
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
    def create_detection_tab(self):
        """Aba de detecção."""
        tab_frame = tk.Frame(self.notebook, bg=ModernConfigTheme.BG_CARD)
        self.notebook.add(tab_frame, text="🎯 Detecção")
        
        # Scroll
        canvas = tk.Canvas(tab_frame, bg=ModernConfigTheme.BG_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernConfigTheme.BG_CARD)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Conteúdo
        self.create_section(scrollable_frame, "Detecção de Piscadas", [
            {
                'type': 'slider',
                'label': 'Limiar EAR',
                'key': 'ear_threshold',
                'min': 0.1,
                'max': 0.5,
                'description': 'Sensibilidade para detectar piscadas. Menor = mais sensível.'
            },
            {
                'type': 'slider',
                'label': 'Frames Consecutivos',
                'key': 'blink_consecutive_frames',
                'min': 1,
                'max': 10,
                'description': 'Quantos frames consecutivos para confirmar piscada.'
            },
            {
                'type': 'slider',
                'label': 'Debounce de Clique',
                'key': 'click_debounce_time',
                'min': 0.1,
                'max': 2.0,
                'description': 'Tempo mínimo entre cliques (segundos).'
            }
        ])
        
        self.create_section(scrollable_frame, "Proteções", [
            {
                'type': 'toggle',
                'label': 'Proteção Piscada Dupla',
                'key': 'double_blink_protection',
                'description': 'Bloqueia cliques quando ambos os olhos piscam.'
            }
        ])
        
    def create_mouse_tab(self):
        """Aba de mouse."""
        tab_frame = tk.Frame(self.notebook, bg=ModernConfigTheme.BG_CARD)
        self.notebook.add(tab_frame, text="🖱️ Mouse")
        
        # Scroll
        canvas = tk.Canvas(tab_frame, bg=ModernConfigTheme.BG_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernConfigTheme.BG_CARD)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Conteúdo
        self.create_section(scrollable_frame, "Movimento do Cursor", [
            {
                'type': 'slider',
                'label': 'Sensibilidade',
                'key': 'mouse_sensitivity',
                'min': 0.5,
                'max': 3.0,
                'description': 'Multiplicador de sensibilidade do mouse.'
            },
            {
                'type': 'slider',
                'label': 'Suavização',
                'key': 'smoothing_factor',
                'min': 0.1,
                'max': 1.0,
                'description': 'Suavização do movimento. Menor = mais suave.'
            }
        ])
        
        self.create_section(scrollable_frame, "Área de Controle", [
            {
                'type': 'slider',
                'label': 'X Mínimo',
                'key': 'control_area_x_min',
                'min': 0.0,
                'max': 0.5,
                'description': 'Limite esquerdo da área de controle.'
            },
            {
                'type': 'slider',
                'label': 'X Máximo',
                'key': 'control_area_x_max',
                'min': 0.5,
                'max': 1.0,
                'description': 'Limite direito da área de controle.'
            },
            {
                'type': 'slider',
                'label': 'Y Mínimo',
                'key': 'control_area_y_min',
                'min': 0.0,
                'max': 0.5,
                'description': 'Limite superior da área de controle.'
            },
            {
                'type': 'slider',
                'label': 'Y Máximo',
                'key': 'control_area_y_max',
                'min': 0.5,
                'max': 1.0,
                'description': 'Limite inferior da área de controle.'
            }
        ])
        
    def create_advanced_tab(self):
        """Aba avançada."""
        tab_frame = tk.Frame(self.notebook, bg=ModernConfigTheme.BG_CARD)
        self.notebook.add(tab_frame, text="⚙️ Avançado")
        
        # Scroll
        canvas = tk.Canvas(tab_frame, bg=ModernConfigTheme.BG_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernConfigTheme.BG_CARD)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Conteúdo
        self.create_section(scrollable_frame, "Performance", [
            {
                'type': 'slider',
                'label': 'Processar a Cada N Frames',
                'key': 'process_every_n_frames',
                'min': 1,
                'max': 5,
                'description': 'Processar menos frames para melhor performance.'
            }
        ])
        
        # Botões de ação
        actions_frame = tk.Frame(scrollable_frame, bg=ModernConfigTheme.BG_CARD)
        actions_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(actions_frame, text="Ações", font=("Segoe UI", 14, "bold"), 
                bg=ModernConfigTheme.BG_CARD, fg=ModernConfigTheme.TEXT_PRIMARY).pack(anchor=tk.W, pady=(0, 10))
        
        buttons_frame = tk.Frame(actions_frame, bg=ModernConfigTheme.BG_CARD)
        buttons_frame.pack(fill=tk.X)
        
        self.create_action_button(buttons_frame, "Restaurar Padrões", 
                                 self.restore_defaults, ModernConfigTheme.WARNING).pack(side=tk.LEFT, padx=(0, 10))
        
        self.create_action_button(buttons_frame, "Exportar Config", 
                                 self.export_config, ModernConfigTheme.INFO).pack(side=tk.LEFT, padx=(0, 10))
        
        self.create_action_button(buttons_frame, "Importar Config", 
                                 self.import_config, ModernConfigTheme.ACCENT).pack(side=tk.LEFT)
        
    def create_section(self, parent, title, controls):
        """Cria seção de controles."""
        section_frame = tk.Frame(parent, bg=ModernConfigTheme.BG_HOVER)
        section_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Título da seção
        title_frame = tk.Frame(section_frame, bg=ModernConfigTheme.BG_HOVER)
        title_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        tk.Label(title_frame, text=title, font=("Segoe UI", 14, "bold"), 
                bg=ModernConfigTheme.BG_HOVER, fg=ModernConfigTheme.TEXT_PRIMARY).pack(anchor=tk.W)
        
        # Controles
        for control in controls:
            self.create_control(section_frame, control)
            
    def create_control(self, parent, control_config):
        """Cria controle individual."""
        control_frame = tk.Frame(parent, bg=ModernConfigTheme.BG_HOVER)
        control_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Label
        label_frame = tk.Frame(control_frame, bg=ModernConfigTheme.BG_HOVER)
        label_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(label_frame, text=control_config['label'], 
                font=("Segoe UI", 11, "bold"), bg=ModernConfigTheme.BG_HOVER, 
                fg=ModernConfigTheme.TEXT_PRIMARY).pack(side=tk.LEFT)
        
        # Descrição
        if 'description' in control_config:
            tk.Label(label_frame, text=control_config['description'], 
                    font=("Segoe UI", 9), bg=ModernConfigTheme.BG_HOVER, 
                    fg=ModernConfigTheme.TEXT_SECONDARY).pack(side=tk.RIGHT)
        
        # Controle
        if control_config['type'] == 'slider':
            slider = ModernSlider(control_frame, 
                                 min_val=control_config['min'],
                                 max_val=control_config['max'],
                                 initial_val=self.config[control_config['key']],
                                 callback=lambda val, key=control_config['key']: self.update_config(key, val),
                                 label=control_config['label'])
            slider.pack(pady=5)
            
        elif control_config['type'] == 'toggle':
            toggle = ModernToggle(control_frame,
                                 initial_state=self.config[control_config['key']],
                                 callback=lambda val, key=control_config['key']: self.update_config(key, val))
            toggle.pack(pady=5)
            
    def create_action_button(self, parent, text, command, color):
        """Cria botão de ação."""
        btn = tk.Button(parent, text=text, command=command, 
                       font=("Segoe UI", 10, "bold"), 
                       bg=color, fg=ModernConfigTheme.TEXT_PRIMARY, 
                       relief=tk.FLAT, cursor="hand2", 
                       activebackground=self.lighten_color(color), 
                       activeforeground=ModernConfigTheme.TEXT_PRIMARY,
                       padx=20, pady=8)
        return btn
        
    def create_footer(self):
        """Cria footer."""
        footer_frame = tk.Frame(self.root, bg=ModernConfigTheme.BG_CARD, height=60)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        # Botões principais
        buttons_frame = tk.Frame(footer_frame, bg=ModernConfigTheme.BG_CARD)
        buttons_frame.pack(expand=True)
        
        self.create_action_button(buttons_frame, "Salvar", 
                                 self.save_config, ModernConfigTheme.SUCCESS).pack(side=tk.LEFT, padx=10, pady=15)
        
        self.create_action_button(buttons_frame, "Cancelar", 
                                 self.cancel, ModernConfigTheme.ERROR).pack(side=tk.LEFT, padx=10, pady=15)
        
        self.create_action_button(buttons_frame, "Aplicar", 
                                 self.apply_config, ModernConfigTheme.INFO).pack(side=tk.LEFT, padx=10, pady=15)
        
    def create_gradient(self, canvas, color1, color2, width, height):
        """Cria gradiente responsivo."""
        r1, g1, b1 = self.hex_to_rgb(color1)
        r2, g2, b2 = self.hex_to_rgb(color2)
        
        for i in range(height):
            ratio = i / height if height > 0 else 0
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(0, i, width, i, fill=color)
            
    def hex_to_rgb(self, hex_color):
        """Converte hex para RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
    def lighten_color(self, color):
        """Clareia cor."""
        # Implementação simplificada
        return color
        
    def update_config(self, key, value):
        """Atualiza configuração."""
        self.config[key] = value
        
    def save_config(self):
        """Salva configurações."""
        try:
            # Salvar em config.json
            with open('config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
                
            # Atualizar config.py
            self.update_config_py()
            
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
            
    def update_config_py(self):
        """Atualiza arquivo config.py."""
        config_content = f'''# Configurações do Pisk & Click - Gerado automaticamente

# Detecção de piscadas
EAR_THRESHOLD = {self.config['ear_threshold']}
BLINK_CONSECUTIVE_FRAMES = {int(self.config['blink_consecutive_frames'])}

# Mouse
SMOOTHING_FACTOR = {self.config['smoothing_factor']}
MOUSE_SENSITIVITY_MULTIPLIER = {self.config['mouse_sensitivity']}

# Área de controle
CONTROL_AREA_X_MIN = {self.config['control_area_x_min']}
CONTROL_AREA_X_MAX = {self.config['control_area_x_max']}
CONTROL_AREA_Y_MIN = {self.config['control_area_y_min']}
CONTROL_AREA_Y_MAX = {self.config['control_area_y_max']}

# Cliques
CLICK_DEBOUNCE_TIME = {self.config['click_debounce_time']}
DOUBLE_BLINK_PROTECTION = {self.config['double_blink_protection']}

# Performance
PROCESS_EVERY_N_FRAMES = {int(self.config['process_every_n_frames'])}

# Constantes fixas
NOSE_TIP_INDEX = 1
# Landmarks invertidos por causa do flip da imagem (cv2.flip)
LEFT_EYE_LANDMARKS_IDXS = [33, 160, 158, 133, 153, 144]  # Era RIGHT
RIGHT_EYE_LANDMARKS_IDXS = [362, 385, 387, 263, 373, 380]  # Era LEFT
REFINE_LANDMARKS = True
INVERT_X_AXIS = False
INVERT_Y_AXIS = False
MIN_MOVEMENT_THRESHOLD = 2
SENSITIVITY_ADJUSTMENT_STEP = 0.1
MIN_SENSITIVITY = 0.5
MAX_SENSITIVITY = 2.5
DOUBLE_BLINK_THRESHOLD = 0.05
DOUBLE_BLINK_COOLDOWN = 1.0
'''
        
        with open('config.py', 'w') as f:
            f.write(config_content)
            
    def apply_config(self):
        """Aplica configurações sem salvar."""
        self.update_config_py()
        messagebox.showinfo("Aplicado", "Configurações aplicadas temporariamente!")
        
    def cancel(self):
        """Cancela e fecha."""
        self.root.destroy()
        
    def restore_defaults(self):
        """Restaura padrões."""
        if messagebox.askyesno("Confirmar", "Restaurar configurações padrão?"):
            self.config = {
                'ear_threshold': 0.25,
                'blink_consecutive_frames': 4,
                'smoothing_factor': 0.3,
                'mouse_sensitivity': 1.3,
                'control_area_x_min': 0.25,
                'control_area_x_max': 0.75,
                'control_area_y_min': 0.25,
                'control_area_y_max': 0.75,
                'click_debounce_time': 0.4,
                'double_blink_protection': True,
                'process_every_n_frames': 1
            }
            messagebox.showinfo("Restaurado", "Configurações padrão restauradas!")
            
    def export_config(self):
        """Exporta configurações."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.config, f, indent=2)
                messagebox.showinfo("Sucesso", "Configurações exportadas!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar: {e}")
                
    def import_config(self):
        """Importa configurações."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    imported_config = json.load(f)
                    self.config.update(imported_config)
                messagebox.showinfo("Sucesso", "Configurações importadas!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao importar: {e}")
                
    def run(self):
        """Executa aplicação."""
        self.root.mainloop()


def main():
    """Função principal."""
    app = ModernConfigApp()
    app.run()


if __name__ == "__main__":
    main()