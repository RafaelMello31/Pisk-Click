#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pisk & Click - Interface Simples e Funcional
Versão simplificada que garante que todas as funções funcionem.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from PIL import Image, ImageTk

class SimpleTheme:
    """Tema simples e funcional."""
    PRIMARY = "#2563eb"      # Azul
    SUCCESS = "#16a34a"      # Verde
    WARNING = "#ea580c"      # Laranja
    ERROR = "#dc2626"        # Vermelho
    INFO = "#0891b2"         # Ciano
    SECONDARY = "#6b7280"    # Cinza
    
    BG_DARK = "#1f2937"      # Fundo escuro
    BG_LIGHT = "#374151"     # Fundo claro
    TEXT_WHITE = "#ffffff"   # Texto branco
    TEXT_GRAY = "#d1d5db"    # Texto cinza

class PiskAndClickApp:
    """Interface simples do Pisk & Click."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_interface()
        
    def setup_window(self):
        """Configura a janela principal."""
        self.root.title("Pisk & Click - Controle Facial")
        self.root.geometry("900x700")  # Aumentado para acomodar o logo maior
        self.root.configure(bg=SimpleTheme.BG_DARK)
        
        # Definir ícone da janela
        try:
            assets_dir = os.path.join(os.getcwd(), "assets")
            icon_candidates = [
                os.path.join(assets_dir, "pisk_and_click.ico"),
                os.path.join(assets_dir, "pisk_and_click_icon.ico"),
                os.path.join(assets_dir, "logo.png"),
                "pisk_and_click.ico",
                "pisk_and_click_icon.ico",
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
        
        # Centralizar janela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"900x700+{x}+{y}")
        
    def create_interface(self):
        """Cria a interface completa."""
        # Header com logo otimizado
        header_frame = tk.Frame(self.root, bg=SimpleTheme.PRIMARY, height=140)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Container para logo e texto
        header_content = tk.Frame(header_frame, bg=SimpleTheme.PRIMARY)
        header_content.pack(expand=True, fill=tk.BOTH)
        
        # Tentar carregar e exibir o logo
        try:
            # Tentar carregar logo otimizado primeiro
            logo_path = None
            logo_size = 80  # Tamanho maior para melhor qualidade
            
            # Usar apenas o logo original
            assets_logo = os.path.join(os.getcwd(), "assets", "logo.png")
            logo_path = assets_logo if os.path.exists(assets_logo) else "logo.png"
            logo_size = 80
            
            if logo_path:
                # Abrir e redimensionar logo com alta qualidade
                logo_image = Image.open(logo_path)
                
                # Redimensionar o logo original
                logo_image = logo_image.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                
                # Converter para PhotoImage
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                
                # Frame principal centralizado
                main_content_frame = tk.Frame(header_content, bg=SimpleTheme.PRIMARY)
                main_content_frame.pack(expand=True)
                
                # Frame para logo e título lado a lado
                logo_title_frame = tk.Frame(main_content_frame, bg=SimpleTheme.PRIMARY)
                logo_title_frame.pack(expand=True, pady=20)
                
                # Logo com melhor alinhamento
                logo_label = tk.Label(logo_title_frame, image=self.logo_photo, 
                                     bg=SimpleTheme.PRIMARY, bd=0, highlightthickness=0)
                logo_label.pack(side=tk.LEFT, padx=(0, 20))
                
                # Textos ao lado do logo com melhor alinhamento vertical
                text_frame = tk.Frame(logo_title_frame, bg=SimpleTheme.PRIMARY)
                text_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)
                
                # Espaçador para centralizar verticalmente
                spacer_top = tk.Frame(text_frame, bg=SimpleTheme.PRIMARY, height=10)
                spacer_top.pack()
                
                title_label = tk.Label(text_frame, text="PISK & CLICK", 
                                      font=("Segoe UI", 28, "bold"), 
                                      bg=SimpleTheme.PRIMARY, fg=SimpleTheme.TEXT_WHITE)
                title_label.pack(anchor=tk.W, pady=(0, 8))
                
                subtitle_label = tk.Label(text_frame, text="Controle Facial para Acessibilidade", 
                                         font=("Segoe UI", 14), 
                                         bg=SimpleTheme.PRIMARY, fg=SimpleTheme.TEXT_GRAY)
                subtitle_label.pack(anchor=tk.W)
                
                # Versão do software
                version_label = tk.Label(text_frame, text="v1.0 - Interface Moderna", 
                                        font=("Segoe UI", 10), 
                                        bg=SimpleTheme.PRIMARY, fg=SimpleTheme.TEXT_GRAY)
                version_label.pack(anchor=tk.W, pady=(5, 0))
                
            else:
                # Fallback sem logo
                title_label = tk.Label(header_content, text="PISK & CLICK", 
                                      font=("Segoe UI", 28, "bold"), 
                                      bg=SimpleTheme.PRIMARY, fg=SimpleTheme.TEXT_WHITE)
                title_label.pack(expand=True, pady=(30, 5))
                
                subtitle_label = tk.Label(header_content, text="Controle Facial para Acessibilidade", 
                                         font=("Segoe UI", 14), 
                                         bg=SimpleTheme.PRIMARY, fg=SimpleTheme.TEXT_GRAY)
                subtitle_label.pack(pady=(0, 30))
                
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
            # Fallback sem logo
            title_label = tk.Label(header_content, text="PISK & CLICK", 
                                  font=("Segoe UI", 28, "bold"), 
                                  bg=SimpleTheme.PRIMARY, fg=SimpleTheme.TEXT_WHITE)
            title_label.pack(expand=True, pady=(30, 5))
            
            subtitle_label = tk.Label(header_content, text="Controle Facial para Acessibilidade", 
                                     font=("Segoe UI", 14), 
                                     bg=SimpleTheme.PRIMARY, fg=SimpleTheme.TEXT_GRAY)
            subtitle_label.pack(pady=(0, 30))
        
        # Área principal
        main_frame = tk.Frame(self.root, bg=SimpleTheme.BG_DARK)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Grid de botões 2x3
        buttons = [
            ("🎯 Controle Facial", "Iniciar controle facial", SimpleTheme.SUCCESS, self.start_main_program, "INICIAR"),
            ("⚙️ Calibração", "Calibrar detecção", SimpleTheme.INFO, self.start_calibration, "CALIBRAR"),
            ("🔧 Configurações", "Ajustar parâmetros", SimpleTheme.WARNING, self.open_config, "CONFIGURAR"),
            ("👤 Perfis", "Gerenciar usuários", SimpleTheme.PRIMARY, self.manage_profiles, "GERENCIAR"),
            ("📋 Fluxo Completo", "Calibrar + Configurar + Usar", SimpleTheme.SECONDARY, self.start_complete_flow, "EXECUTAR"),
            ("❌ Sair", "Fechar aplicação", SimpleTheme.ERROR, self.quit_app, "SAIR")
        ]
        
        for i, (title, desc, color, command, btn_text) in enumerate(buttons):
            row = i // 3
            col = i % 3
            
            # Frame do botão
            btn_frame = tk.Frame(main_frame, bg=color, relief=tk.RAISED, bd=3)
            btn_frame.grid(row=row, column=col, padx=15, pady=15, sticky="nsew", ipadx=20, ipady=20)
            
            # Configurar grid
            main_frame.grid_rowconfigure(row, weight=1)
            main_frame.grid_columnconfigure(col, weight=1)
            
            # Conteúdo do botão
            tk.Label(btn_frame, text=title, font=("Arial", 14, "bold"), 
                    bg=color, fg=SimpleTheme.TEXT_WHITE).pack(pady=(10, 5))
            
            tk.Label(btn_frame, text=desc, font=("Arial", 10), 
                    bg=color, fg=SimpleTheme.TEXT_WHITE, wraplength=150).pack(pady=5)
            
            # Botão clicável
            action_btn = tk.Button(btn_frame, text=btn_text, command=command,
                                  font=("Arial", 10, "bold"), bg=SimpleTheme.TEXT_WHITE, 
                                  fg=color, relief=tk.FLAT, cursor="hand2", padx=15, pady=5)
            action_btn.pack(pady=(10, 15))
            
            # Efeito hover
            def on_enter(event, frame=btn_frame):
                frame.configure(bd=5)
                
            def on_leave(event, frame=btn_frame):
                frame.configure(bd=3)
            
            btn_frame.bind("<Enter>", on_enter)
            btn_frame.bind("<Leave>", on_leave)
            btn_frame.bind("<Button-1>", lambda e, cmd=command: cmd())
        
        # Footer
        footer_frame = tk.Frame(self.root, bg=SimpleTheme.BG_LIGHT, height=40)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        self.status_label = tk.Label(footer_frame, text="✅ Pronto para usar", 
                                    font=("Arial", 10), bg=SimpleTheme.BG_LIGHT, 
                                    fg=SimpleTheme.TEXT_WHITE)
        self.status_label.pack(expand=True)
        
    def update_status(self, message, icon="ℹ️"):
        """Atualiza status."""
        self.status_label.config(text=f"{icon} {message}")
        self.root.update()
        
    def start_main_program(self):
        """Inicia programa principal."""
        self.update_status("Iniciando controle facial...", "🚀")
        try:
            if os.path.exists("main.py"):
                subprocess.Popen([sys.executable, "main.py"])
                self.update_status("Controle facial iniciado!", "✅")
            else:
                messagebox.showerror("Erro", "Arquivo main.py não encontrado!")
                self.update_status("Erro: main.py não encontrado", "❌")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar: {e}")
            self.update_status(f"Erro: {e}", "❌")
            
    def start_calibration(self):
        """Inicia calibração."""
        self.update_status("Iniciando calibração...", "⚙️")
        try:
            if os.path.exists("modern_calibration.py"):
                subprocess.Popen([sys.executable, "modern_calibration.py"])
                self.update_status("Calibração iniciada!", "✅")
            elif os.path.exists("calibration_module.py"):
                subprocess.Popen([sys.executable, "calibration_module.py"])
                self.update_status("Calibração iniciada!", "✅")
            else:
                messagebox.showerror("Erro", "Módulo de calibração não encontrado!")
                self.update_status("Erro: calibração não encontrada", "❌")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na calibração: {e}")
            self.update_status(f"Erro: {e}", "❌")
            
    def open_config(self):
        """Abre configurações."""
        self.update_status("Abrindo configurações...", "🔧")
        try:
            if os.path.exists("modern_config_gui.py"):
                subprocess.Popen([sys.executable, "modern_config_gui.py"])
                self.update_status("Configurações abertas!", "✅")
            elif os.path.exists("config_gui.py"):
                subprocess.Popen([sys.executable, "config_gui.py"])
                self.update_status("Configurações abertas!", "✅")
            else:
                messagebox.showerror("Erro", "Interface de configuração não encontrada!")
                self.update_status("Erro: configurações não encontradas", "❌")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro nas configurações: {e}")
            self.update_status(f"Erro: {e}", "❌")
            
    def manage_profiles(self):
        """Gerencia perfis."""
        self.update_status("Abrindo perfis...", "👤")
        try:
            if os.path.exists("modern_profile_manager.py"):
                subprocess.Popen([sys.executable, "modern_profile_manager.py"])
                self.update_status("Gerenciador de perfis aberto!", "✅")
            elif os.path.exists("user_profile_manager.py"):
                subprocess.Popen([sys.executable, "user_profile_manager.py"])
                self.update_status("Perfis abertos!", "✅")
            else:
                messagebox.showinfo("Perfis", "Gerenciador de perfis ainda não implementado.")
                self.update_status("Perfis não implementados", "⚠️")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro nos perfis: {e}")
            self.update_status(f"Erro: {e}", "❌")
            
    def start_complete_flow(self):
        """Executa fluxo completo."""
        response = messagebox.askyesno(
            "Fluxo Completo",
            "Executar fluxo completo?\n\n1. Calibração\n2. Configurações\n3. Controle Facial"
        )
        
        if response:
            self.update_status("Iniciando fluxo completo...", "📋")
            try:
                # Calibração
                if os.path.exists("calibration_module.py"):
                    self.update_status("Passo 1/3: Calibração", "⚙️")
                    subprocess.run([sys.executable, "calibration_module.py"])
                
                # Configurações
                if os.path.exists("config_gui.py"):
                    self.update_status("Passo 2/3: Configurações", "🔧")
                    messagebox.showinfo("Configurações", "Ajuste as configurações e feche para continuar.")
                    subprocess.run([sys.executable, "config_gui.py"])
                
                # Programa principal
                if os.path.exists("main.py"):
                    self.update_status("Passo 3/3: Controle Facial", "🎯")
                    subprocess.Popen([sys.executable, "main.py"])
                
                self.update_status("Fluxo completo executado!", "✅")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro no fluxo: {e}")
                self.update_status(f"Erro no fluxo: {e}", "❌")
                
    def quit_app(self):
        """Sair da aplicação."""
        if messagebox.askyesno("Sair", "Deseja realmente sair?"):
            self.root.quit()
            
    def run(self):
        """Executa a aplicação."""
        self.root.mainloop()

def main():
    """Função principal."""
    try:
        app = PiskAndClickApp()
        app.run()
    except Exception as e:
        print(f"Erro fatal: {e}")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()