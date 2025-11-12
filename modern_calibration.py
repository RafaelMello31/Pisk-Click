#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Moderna de Calibração - Pisk & Click
Design moderno e intuitivo para calibração de piscadas.
"""

import tkinter as tk
from tkinter import ttk, messagebox, Canvas
import cv2
import mediapipe as mp
import numpy as np
import threading
import time
from PIL import Image, ImageTk, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import json
import os

class ModernCalibrationTheme:
    """Tema moderno para calibração."""
    
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
    
    # Textos
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#8b949e"
    TEXT_MUTED = "#6e7681"
    
    # Gradientes
    GRADIENT_START = "#667eea"
    GRADIENT_END = "#764ba2"


class ModernProgressBar(tk.Canvas):
    """Barra de progresso moderna com animação."""
    
    def __init__(self, parent, width=400, height=20, bg_color=ModernCalibrationTheme.BG_CARD):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=bg_color)
        self.width = width
        self.height = height
        self.progress = 0
        self.draw_progress()
        
    def set_progress(self, value):
        """Define o progresso (0-100)."""
        self.progress = max(0, min(100, value))
        self.draw_progress()
        
    def draw_progress(self):
        """Desenha a barra de progresso."""
        self.delete("all")
        
        # Fundo da barra
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, 
                                radius=10, fill=ModernCalibrationTheme.BG_HOVER, 
                                outline=ModernCalibrationTheme.TEXT_MUTED)
        
        # Progresso
        if self.progress > 0:
            progress_width = (self.width - 4) * (self.progress / 100)
            color = ModernCalibrationTheme.SUCCESS if self.progress == 100 else ModernCalibrationTheme.INFO
            self.create_rounded_rect(2, 2, 2 + progress_width, self.height-2, 
                                    radius=10, fill=color)
        
        # Texto do progresso
        self.create_text(self.width//2, self.height//2, 
                        text=f"{self.progress:.0f}%", 
                        fill=ModernCalibrationTheme.TEXT_PRIMARY, 
                        font=("Segoe UI", 10, "bold"))
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Cria retângulo com bordas arredondadas."""
        points = []
        for x, y in [(x1, y1 + radius), (x1, y1), (x1 + radius, y1),
                     (x2 - radius, y1), (x2, y1), (x2, y1 + radius),
                     (x2, y2 - radius), (x2, y2), (x2 - radius, y2),
                     (x1 + radius, y2), (x1, y2), (x1, y2 - radius)]:
            points.extend([x, y])
        return self.create_polygon(points, smooth=True, **kwargs)


class ModernCalibrationApp:
    """Interface moderna de calibração."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_variables()
        self.create_widgets()
        self.setup_mediapipe()
        
    def setup_window(self):
        """Configura a janela principal."""
        self.root.title("Pisk & Click - Calibração Moderna")
        self.root.geometry("1200x800")
        self.root.configure(bg=ModernCalibrationTheme.BG_DARK)
        self.root.resizable(True, True)
        
        # Definir ícone da janela
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
            # Tenta .ico primeiro
            for icon_path in icon_candidates:
                if icon_path.endswith(".ico") and os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
                    break
            else:
                # Fallback para PNG
                for icon_path in icon_candidates:
                    if icon_path.endswith(".png") and os.path.exists(icon_path):
                        icon_img = tk.PhotoImage(file=icon_path)
                        self.root.iconphoto(True, icon_img)
                        break
        except Exception as e:
            print(f"Aviso: Não foi possível definir ícone da janela: {e}")
        
        # Centralizar
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
        
    def setup_variables(self):
        """Inicializa variáveis."""
        self.cap = None
        self.is_calibrating = False
        self.calibration_data = []
        self.current_step = 0
        self.video_running = False
        self.face_mesh = None
        self.steps = [
            "Preparação",
            "Detecção Facial", 
            "Coleta de Dados",
            "Análise",
            "Finalização"
        ]
        
    def create_widgets(self):
        """Cria interface moderna e responsiva."""
        # Header
        self.create_header()
        
        # Área principal responsiva
        main_frame = tk.Frame(self.root, bg=ModernCalibrationTheme.BG_DARK)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Container principal com PanedWindow para redimensionamento
        paned_window = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, 
                                     bg=ModernCalibrationTheme.BG_DARK,
                                     sashrelief=tk.RAISED, sashwidth=5)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Painel esquerdo (controle) - largura mínima
        left_frame = tk.Frame(paned_window, bg=ModernCalibrationTheme.BG_CARD)
        paned_window.add(left_frame, minsize=350, width=400)
        
        # Painel direito (vídeo) - expansível
        right_frame = tk.Frame(paned_window, bg=ModernCalibrationTheme.BG_CARD)
        paned_window.add(right_frame, minsize=400)
        
        # Painel de controle (esquerda)
        self.create_control_panel(left_frame)
        
        # Área de vídeo (direita)
        self.create_video_area(right_frame)
        
        # Footer
        self.create_footer()
        
    def create_header(self):
        """Cria cabeçalho moderno e responsivo com logo."""
        header_frame = tk.Frame(self.root, bg=ModernCalibrationTheme.PRIMARY, height=120)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Canvas para gradiente responsivo
        header_canvas = tk.Canvas(header_frame, height=120, highlightthickness=0)
        header_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Botão de início no cabeçalho (sempre visível)
        self.header_start_button = tk.Button(
            header_canvas,
            text="▶ Iniciar Calibração",
            command=self.start_calibration,
            font=("Arial", 12, "bold"),
            bg=ModernCalibrationTheme.SUCCESS,
            fg="white",
            relief=tk.RAISED,
            bd=2,
            padx=16,
            pady=6,
            cursor="hand2",
            activebackground=ModernCalibrationTheme.SUCCESS,
            activeforeground="white"
        )
        
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
                    logo_height = 60
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
                self.create_gradient(header_canvas, ModernCalibrationTheme.GRADIENT_START, 
                                   ModernCalibrationTheme.GRADIENT_END, width, height)
                
                # Layout com margem fixa à esquerda para logo e textos ancorados
                margin = 20
                if self.logo_image:
                    logo_w = self.logo_image.width()
                    logo_x = margin + (logo_w // 2)
                    logo_y = int(height * 0.5)
                    header_canvas.create_image(logo_x, logo_y, image=self.logo_image, anchor="center")
                    text_x = margin + logo_w + 20
                else:
                    text_x = margin
                
                # Botão de iniciar sempre à direita
                btn_x = width - 20
                btn_y = height * 0.5
                
                # Títulos responsivos, alinhados à esquerda e sem sobreposição com o botão
                title_size = min(24, max(16, width // 45))
                subtitle_size = min(12, max(9, width // 90))
                max_text_width = max(200, int(btn_x - text_x - 40))
                
                header_canvas.create_text(text_x, int(height * 0.4), text="CALIBRAÇÃO INTELIGENTE", 
                                         fill=ModernCalibrationTheme.TEXT_PRIMARY, 
                                         font=("Segoe UI", title_size, "bold"),
                                         anchor="w", width=max_text_width)
                
                header_canvas.create_text(text_x, int(height * 0.7), text="Configure a detecção de piscadas automaticamente", 
                                         fill=ModernCalibrationTheme.TEXT_SECONDARY, 
                                         font=("Segoe UI", subtitle_size),
                                         anchor="w", width=max_text_width)
                
                header_canvas.create_window(btn_x, btn_y, anchor="e", window=self.header_start_button)
        
        header_canvas.bind("<Configure>", redraw_header)
        header_canvas.after(1, redraw_header)


    def create_control_panel(self, parent):
        """Cria painel de controle."""
        # Título do painel
        title_label = tk.Label(parent, text="Painel de Controle", 
                              font=("Segoe UI", 16, "bold"), 
                              bg=ModernCalibrationTheme.BG_CARD, 
                              fg=ModernCalibrationTheme.TEXT_PRIMARY)
        title_label.pack(pady=20)
        
        # Botões no topo para máxima visibilidade
        buttons_frame = tk.Frame(parent, bg=ModernCalibrationTheme.BG_CARD)
        buttons_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Botão INICIAR - GIGANTE E SUPER VISÍVEL
        self.start_btn = tk.Button(buttons_frame,
                                   text="▶ INICIAR CALIBRAÇÃO",
                                   command=self.start_calibration,
                                   font=("Arial", 20, "bold"),
                                   bg="#00FF00",
                                   fg="#000000",
                                   relief=tk.RAISED,
                                   bd=8,
                                   cursor="hand2",
                                   padx=50,
                                   pady=25,
                                   activebackground="#00CC00",
                                   activeforeground="#000000",
                                   highlightbackground="#FFFF00",
                                   highlightcolor="#FFFF00",
                                   highlightthickness=3)
        self.start_btn.pack(fill=tk.X, pady=10, ipady=18)

        # Botão PARAR
        self.stop_btn = tk.Button(buttons_frame,
                                  text="⏹ PARAR",
                                  command=self.stop_calibration,
                                  font=("Arial", 16, "bold"),
                                  bg="#FF4444",
                                  fg="#FFFFFF",
                                  relief=tk.RAISED,
                                  bd=5,
                                  cursor="hand2",
                                  padx=35,
                                  pady=18,
                                  activebackground="#CC0000",
                                  activeforeground="#FFFFFF")
        self.stop_btn.pack(fill=tk.X, pady=8, ipady=12)

        # Botão FECHAR
        self.close_btn = tk.Button(buttons_frame,
                                   text="✖ FECHAR",
                                   command=self.close_app,
                                   font=("Arial", 14, "bold"),
                                   bg="#888888",
                                   fg="#FFFFFF",
                                   relief=tk.RAISED,
                                   bd=4,
                                   cursor="hand2",
                                   padx=25,
                                   pady=12,
                                   activebackground="#666666",
                                   activeforeground="#FFFFFF")
        self.close_btn.pack(fill=tk.X, pady=8, ipady=10)

        # Progresso geral
        progress_frame = tk.Frame(parent, bg=ModernCalibrationTheme.BG_CARD)
        progress_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(progress_frame, text="Progresso Geral:",
                 font=("Segoe UI", 10), bg=ModernCalibrationTheme.BG_CARD,
                 fg=ModernCalibrationTheme.TEXT_SECONDARY).pack(anchor=tk.W)

        self.progress_bar = ModernProgressBar(progress_frame, width=350, height=25)
        self.progress_bar.pack(pady=5)

        # Steps
        steps_frame = tk.Frame(parent, bg=ModernCalibrationTheme.BG_CARD)
        steps_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(steps_frame, text="Etapas:",
                 font=("Segoe UI", 12, "bold"), bg=ModernCalibrationTheme.BG_CARD,
                 fg=ModernCalibrationTheme.TEXT_PRIMARY).pack(anchor=tk.W, pady=(0, 10))

        self.step_labels = []
        for i, step in enumerate(self.steps):
            step_frame = tk.Frame(steps_frame, bg=ModernCalibrationTheme.BG_CARD)
            step_frame.pack(fill=tk.X, pady=2)

            # Indicador
            indicator = tk.Label(step_frame, text="○", font=("Segoe UI", 12),
                                 bg=ModernCalibrationTheme.BG_CARD,
                                 fg=ModernCalibrationTheme.TEXT_MUTED, width=3)
            indicator.pack(side=tk.LEFT)

            # Texto
            label = tk.Label(step_frame, text=step, font=("Segoe UI", 10),
                             bg=ModernCalibrationTheme.BG_CARD,
                             fg=ModernCalibrationTheme.TEXT_SECONDARY, anchor=tk.W)
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            self.step_labels.append((indicator, label))

        # Instruções (após os botões)
        instructions_frame = tk.Frame(parent, bg=ModernCalibrationTheme.BG_HOVER)
        instructions_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(instructions_frame, text="📋 Instruções",
                 font=("Segoe UI", 12, "bold"), bg=ModernCalibrationTheme.BG_HOVER,
                 fg=ModernCalibrationTheme.TEXT_PRIMARY).pack(pady=10)

        self.instruction_text = tk.Text(instructions_frame, height=8, width=40,
                                        bg=ModernCalibrationTheme.BG_HOVER,
                                        fg=ModernCalibrationTheme.TEXT_SECONDARY,
                                        font=("Segoe UI", 9), wrap=tk.WORD,
                                        relief=tk.FLAT, state=tk.DISABLED)
        self.instruction_text.pack(padx=10, pady=(0, 10))
        
    def create_video_area(self, parent):
        """Cria área de vídeo."""
        # Título
        title_label = tk.Label(parent, text="Visualização da Câmera", 
                              font=("Segoe UI", 16, "bold"), 
                              bg=ModernCalibrationTheme.BG_CARD, 
                              fg=ModernCalibrationTheme.TEXT_PRIMARY)
        title_label.pack(pady=20)
        
        # Canvas para vídeo
        self.video_canvas = tk.Canvas(parent, bg=ModernCalibrationTheme.BG_DARK, 
                                     highlightthickness=2, 
                                     highlightbackground=ModernCalibrationTheme.ACCENT)
        self.video_canvas.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Status da detecção
        status_frame = tk.Frame(parent, bg=ModernCalibrationTheme.BG_CARD)
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.detection_status = tk.Label(status_frame, text="Aguardando câmera...", 
                                        font=("Segoe UI", 12), 
                                        bg=ModernCalibrationTheme.BG_CARD, 
                                        fg=ModernCalibrationTheme.TEXT_SECONDARY)
        self.detection_status.pack()
        
    def create_footer(self):
        """Cria footer."""
        footer_frame = tk.Frame(self.root, bg=ModernCalibrationTheme.BG_CARD, height=40)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        self.status_label = tk.Label(footer_frame, text="Pronto para calibração", 
                                    font=("Segoe UI", 10), 
                                    bg=ModernCalibrationTheme.BG_CARD, 
                                    fg=ModernCalibrationTheme.TEXT_SECONDARY)
        self.status_label.pack(side=tk.LEFT, padx=20, pady=10)
        
    def create_modern_button(self, parent, text, command, color):
        """Cria botão moderno."""
        btn = tk.Button(parent, text=text, command=command, 
                       font=("Segoe UI", 14, "bold"), 
                       bg=color, fg=ModernCalibrationTheme.TEXT_PRIMARY, 
                       relief=tk.FLAT, cursor="hand2", 
                       activebackground=self.lighten_color(color), 
                       activeforeground=ModernCalibrationTheme.TEXT_PRIMARY,
                       width=30, height=3, padx=20, pady=10)
        return btn
        
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
        if color == ModernCalibrationTheme.SUCCESS:
            return "#33e6c4"
        elif color == ModernCalibrationTheme.ERROR:
            return "#f77370"
        else:
            return color
            
    def setup_mediapipe(self):
        """Configura MediaPipe."""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
    def update_step(self, step_index):
        """Atualiza indicador de etapa."""
        for i, (indicator, label) in enumerate(self.step_labels):
            if i < step_index:
                indicator.config(text="✓", fg=ModernCalibrationTheme.SUCCESS)
                label.config(fg=ModernCalibrationTheme.SUCCESS)
            elif i == step_index:
                indicator.config(text="●", fg=ModernCalibrationTheme.INFO)
                label.config(fg=ModernCalibrationTheme.TEXT_PRIMARY)
            else:
                indicator.config(text="○", fg=ModernCalibrationTheme.TEXT_MUTED)
                label.config(fg=ModernCalibrationTheme.TEXT_SECONDARY)
                
    def update_instructions(self, text):
        """Atualiza instruções."""
        self.instruction_text.config(state=tk.NORMAL)
        self.instruction_text.delete(1.0, tk.END)
        self.instruction_text.insert(1.0, text)
        self.instruction_text.config(state=tk.DISABLED)
        
    def start_calibration(self):
        """Inicia calibração."""
        self.is_calibrating = True
        self.current_step = 0
        self.update_step(0)
        self.update_instructions("Iniciando calibração...\n\nPosicione-se em frente à câmera com boa iluminação.")
        
        # Iniciar thread de calibração
        threading.Thread(target=self.calibration_thread, daemon=True).start()
        
    def calibration_thread(self):
        """Thread principal de calibração."""
        try:
            # Etapa 1: Preparação
            self.root.after(0, lambda: self.update_step(0))
            self.root.after(0, lambda: self.update_status("Inicializando câmera..."))
            
            # Inicializar câmera
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Não foi possível abrir a câmera")
                
            # Configurar câmera
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                
            # Inicializar MediaPipe
            mp_face_mesh = mp.solutions.face_mesh
            face_mesh = mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            # Etapa 2: Detecção Facial
            self.root.after(0, lambda: self.update_step(1))
            self.root.after(0, lambda: self.update_status("Câmera inicializada. Detectando rosto..."))
            self.root.after(0, lambda: self.update_instructions("POSICIONE SEU ROSTO\n\nCertifique-se de que seu rosto está bem visível na câmera."))
            
            # Iniciar visualização da câmera
            self.start_video_feed(face_mesh)
            
            # Aguardar detecção do rosto
            face_detected = False
            detection_start = time.time()
            while not face_detected and self.is_calibrating and (time.time() - detection_start < 10):
                ret, frame = self.cap.read()
                if ret:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = face_mesh.process(rgb_frame)
                    if results.multi_face_landmarks:
                        face_detected = True
                time.sleep(0.1)
            
            if not face_detected:
                raise Exception("Não foi possível detectar o rosto. Verifique a iluminação e posição.")
            
            # Etapa 3: Coleta de Dados
            self.root.after(0, lambda: self.update_step(2))
            self.root.after(0, lambda: self.update_status("Rosto detectado! Coletando dados..."))
            
            # Coletar dados de olhos abertos
            self.root.after(0, lambda: self.update_instructions("MANTENHA OS OLHOS ABERTOS\n\nOlhe para a câmera e mantenha os olhos bem abertos por 3 segundos."))
            open_ear_values = self.collect_ear_data(face_mesh, 3, "olhos abertos")
            
            if not self.is_calibrating:
                return
                
            # Coletar dados de piscadas
            self.root.after(0, lambda: self.update_instructions("PISQUE VÁRIAS VEZES\n\nPisque naturalmente várias vezes seguidas por 5 segundos."))
            blink_ear_values = self.collect_ear_data(face_mesh, 5, "piscadas")
            
            if not self.is_calibrating:
                return
                
            # Etapa 4: Análise
            self.root.after(0, lambda: self.update_step(3))
            self.root.after(0, lambda: self.update_status("Analisando dados coletados..."))
            
            # Calcular threshold
            if open_ear_values and blink_ear_values:
                avg_open = np.mean(open_ear_values)
                avg_blink = np.mean(blink_ear_values)
                threshold = (avg_open + avg_blink) / 2
                
                # Etapa 5: Finalização
                self.root.after(0, lambda: self.update_step(4))
                self.root.after(0, lambda: self.update_status("Salvando configurações..."))
                
                # Salvar configuração
                self.save_calibration(threshold)
                
                self.root.after(0, lambda: self.update_status("Calibração concluída com sucesso!"))
                self.root.after(0, lambda: self.update_instructions(f"CALIBRAÇÃO CONCLUÍDA!\n\nThreshold calculado: {threshold:.3f}\n\nOlhos abertos: {avg_open:.3f}\nPiscadas: {avg_blink:.3f}\n\nVocê pode fechar esta janela."))
                self.root.after(0, lambda: messagebox.showinfo("Sucesso", f"Calibração concluída!\nThreshold: {threshold:.3f}"))
            else:
                raise Exception("Não foi possível coletar dados suficientes")
                
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Erro na calibração: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro durante calibração: {e}"))
        finally:
            self.stop_video_feed()
            if hasattr(self, 'cap') and self.cap:
                self.cap.release()
                
    def start_video_feed(self, face_mesh):
        """Inicia feed de vídeo."""
        self.video_running = True
        self.face_mesh = face_mesh
        self.update_video_frame()
        
    def stop_video_feed(self):
        """Para feed de vídeo."""
        self.video_running = False
        
    def update_video_frame(self):
        """Atualiza frame do vídeo."""
        if not self.video_running or not hasattr(self, 'cap'):
            return
            
        ret, frame = self.cap.read()
        if ret:
            # Espelhar horizontalmente
            frame = cv2.flip(frame, 1)
            
            # Processar com MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            # Desenhar landmarks se detectados
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                
                # Desenhar pontos dos olhos
                h, w, _ = frame.shape
                for idx in [33, 160, 158, 133, 153, 144]:  # Olho direito
                    x = int(landmarks.landmark[idx].x * w)
                    y = int(landmarks.landmark[idx].y * h)
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
                    
                for idx in [362, 385, 387, 263, 373, 380]:  # Olho esquerdo
                    x = int(landmarks.landmark[idx].x * w)
                    y = int(landmarks.landmark[idx].y * h)
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
                
                self.root.after(0, lambda: self.detection_status.config(text="✓ Rosto detectado", fg=ModernCalibrationTheme.SUCCESS))
            else:
                self.root.after(0, lambda: self.detection_status.config(text="⚠ Posicione seu rosto na câmera", fg=ModernCalibrationTheme.WARNING))
            
            # Converter para formato Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            # Redimensionar para caber no canvas
            canvas_width = self.video_canvas.winfo_width()
            canvas_height = self.video_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                img = img.resize((canvas_width-4, canvas_height-4), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Atualizar canvas
                self.video_canvas.delete("all")
                self.video_canvas.create_image(canvas_width//2, canvas_height//2, image=photo)
                self.video_canvas.image = photo  # Manter referência
        
        # Agendar próximo frame
        if self.video_running:
            self.root.after(33, self.update_video_frame)  # ~30 FPS
                
    def collect_ear_data(self, face_mesh, duration, phase):
        """Coleta dados EAR durante um período."""
        ear_values = []
        start_time = time.time()
        
        while time.time() - start_time < duration and self.is_calibrating:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            # Converter para RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                
                # Calcular EAR para ambos os olhos
                left_ear = self.calculate_ear(landmarks, [362, 385, 387, 263, 373, 380])
                right_ear = self.calculate_ear(landmarks, [33, 160, 158, 133, 153, 144])
                
                if left_ear > 0 and right_ear > 0:
                    avg_ear = (left_ear + right_ear) / 2
                    ear_values.append(avg_ear)
            
            # Atualizar progresso
            elapsed = time.time() - start_time
            progress = (elapsed / duration) * 100
            remaining = duration - elapsed
            
            # Atualizar interface na thread principal
            self.root.after(0, lambda p=min(progress, 100): self.progress_bar.set_progress(p))
            self.root.after(0, lambda r=max(0, remaining): self.detection_status.config(
                text=f"Coletando dados... {r:.1f}s restantes"
            ))
            
            time.sleep(0.03)  # ~30 FPS
            
        return ear_values
        
    def calculate_ear(self, landmarks, eye_indices):
        """Calcula Eye Aspect Ratio."""
        try:
            # Obter coordenadas dos pontos do olho
            eye_points = []
            for idx in eye_indices:
                x = landmarks.landmark[idx].x
                y = landmarks.landmark[idx].y
                eye_points.append([x, y])
            
            eye_points = np.array(eye_points)
            
            # Calcular distâncias verticais
            A = np.linalg.norm(eye_points[1] - eye_points[5])
            B = np.linalg.norm(eye_points[2] - eye_points[4])
            
            # Calcular distância horizontal
            C = np.linalg.norm(eye_points[0] - eye_points[3])
            
            # Calcular EAR
            if C > 0:
                ear = (A + B) / (2.0 * C)
                return ear
            return 0
        except:
            return 0
            
    def save_calibration(self, threshold):
        """Salva resultado da calibração."""
        try:
            # Ler configuração atual
            config_data = {}
            if os.path.exists('config.py'):
                with open('config.py', 'r', encoding='utf-8') as f:
                    content = f.read()
                    
            # Atualizar threshold
            new_content = []
            found_threshold = False
            
            for line in content.split('\n'):
                if line.startswith('EAR_THRESHOLD'):
                    new_content.append(f'EAR_THRESHOLD = {threshold:.3f}')
                    found_threshold = True
                else:
                    new_content.append(line)
                    
            if not found_threshold:
                new_content.append(f'EAR_THRESHOLD = {threshold:.3f}')
                
            # Salvar arquivo
            with open('config.py', 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_content))
                
        except Exception as e:
            print(f"Erro ao salvar calibração: {e}")
            
    def stop_calibration(self):
        """Para calibração."""
        self.is_calibrating = False
        self.stop_video_feed()
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
        self.update_status("Calibração interrompida")
        self.detection_status.config(text="Calibração interrompida")
        
    def update_status(self, message):
        """Atualiza status."""
        self.status_label.config(text=message)
        
    def close_app(self):
        """Fecha aplicação."""
        self.is_calibrating = False
        if self.cap:
            self.cap.release()
        self.root.destroy()
        
    def run(self):
        """Executa aplicação."""
        self.root.mainloop()


def main():
    """Função principal."""
    app = ModernCalibrationApp()
    app.run()


if __name__ == "__main__":
    main()