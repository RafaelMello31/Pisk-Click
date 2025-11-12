#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador Moderno de Perfis - Pisk & Click
Interface moderna para criar, editar, excluir e selecionar perfis de usuário.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import shutil
from datetime import datetime
from user_profile_manager import UserProfileManager
from PIL import Image, ImageTk

class ModernProfileTheme:
    """Tema moderno para gerenciador de perfis."""
    
    # Cores principais
    PRIMARY = "#2563eb"
    SUCCESS = "#16a34a"
    WARNING = "#ea580c"
    ERROR = "#dc2626"
    INFO = "#0891b2"
    SECONDARY = "#6b7280"
    
    # Backgrounds
    BG_DARK = "#1f2937"
    BG_CARD = "#374151"
    BG_LIGHT = "#4b5563"
    BG_HOVER = "#6b7280"
    
    # Textos
    TEXT_WHITE = "#ffffff"
    TEXT_GRAY = "#d1d5db"
    TEXT_MUTED = "#9ca3af"

class ModernProfileManager:
    """Interface moderna para gerenciamento de perfis."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.profile_manager = UserProfileManager()
        self.current_profile = self.load_current_profile()
        self.setup_window()
        self.create_interface()
        self.refresh_profiles()
        
    def setup_window(self):
        """Configura a janela principal."""
        self.root.title("Gerenciador de Perfis - Pisk & Click")
        self.root.geometry("900x600")
        self.root.configure(bg=ModernProfileTheme.BG_DARK)
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
        
        # Centralizar janela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"900x600+{x}+{y}")
        
    def create_interface(self):
        """Cria a interface completa."""
        # Header
        self.create_header()
        
        # Área principal
        main_frame = tk.Frame(self.root, bg=ModernProfileTheme.BG_DARK)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Painel esquerdo - Lista de perfis
        left_panel = tk.Frame(main_frame, bg=ModernProfileTheme.BG_CARD, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        self.create_profile_list(left_panel)
        
        # Painel direito - Detalhes e ações
        right_panel = tk.Frame(main_frame, bg=ModernProfileTheme.BG_CARD, width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        self.create_profile_details(right_panel)
        
        # Footer
        self.create_footer()
        
    def create_header(self):
        """Cria o cabeçalho com logo."""
        header_frame = tk.Frame(self.root, bg=ModernProfileTheme.PRIMARY, height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Container para logo e texto
        header_content = tk.Frame(header_frame, bg=ModernProfileTheme.PRIMARY)
        header_content.pack(expand=True, fill=tk.BOTH)
        
        # Tentar carregar e exibir o logo otimizado
        try:
            # Preferir logo em assets/
            assets_logo = os.path.join(os.getcwd(), "assets", "logo.png")
            logo_path = assets_logo if os.path.exists(assets_logo) else "logo.png"
            
            if logo_path:
                try:
                    # Abrir logo
                    logo_image = Image.open(logo_path)
                    
                    # Redimensionar o logo
                    logo_height = 50
                    aspect_ratio = logo_image.width / logo_image.height
                    logo_width = int(logo_height * aspect_ratio)
                    logo_image = logo_image.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                    
                    # Converter para PhotoImage
                    self.logo_photo = ImageTk.PhotoImage(logo_image)
                except Exception:
                    # Fallback para PhotoImage
                    try:
                        self.logo_photo = tk.PhotoImage(file=logo_path)
                    except Exception:
                        self.logo_photo = None
                
                # Frame para logo e título lado a lado
                logo_title_frame = tk.Frame(header_content, bg=ModernProfileTheme.PRIMARY)
                logo_title_frame.pack(expand=True)
                
                # Logo
                logo_label = tk.Label(logo_title_frame, image=self.logo_photo, 
                                     bg=ModernProfileTheme.PRIMARY)
                logo_label.pack(side=tk.LEFT, padx=(0, 15), pady=10)
                
                # Textos ao lado do logo
                text_frame = tk.Frame(logo_title_frame, bg=ModernProfileTheme.PRIMARY)
                text_frame.pack(side=tk.LEFT, expand=True, fill=tk.Y)
                
                title_label = tk.Label(text_frame, text="👤 GERENCIADOR DE PERFIS", 
                                      font=("Arial", 20, "bold"), 
                                      bg=ModernProfileTheme.PRIMARY, fg=ModernProfileTheme.TEXT_WHITE)
                title_label.pack(anchor=tk.W, pady=(10, 5))
                
                subtitle_label = tk.Label(text_frame, text="Crie e gerencie perfis personalizados para diferentes usuários", 
                                         font=("Arial", 11), 
                                         bg=ModernProfileTheme.PRIMARY, fg=ModernProfileTheme.TEXT_GRAY)
                subtitle_label.pack(anchor=tk.W)
                
            else:
                # Fallback sem logo
                title_label = tk.Label(header_content, text="👤 GERENCIADOR DE PERFIS", 
                                      font=("Arial", 20, "bold"), 
                                      bg=ModernProfileTheme.PRIMARY, fg=ModernProfileTheme.TEXT_WHITE)
                title_label.pack(expand=True, pady=(15, 5))
                
                subtitle_label = tk.Label(header_content, text="Crie e gerencie perfis personalizados para diferentes usuários", 
                                         font=("Arial", 11), 
                                         bg=ModernProfileTheme.PRIMARY, fg=ModernProfileTheme.TEXT_GRAY)
                subtitle_label.pack(pady=(0, 15))
                
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
            # Fallback sem logo
            title_label = tk.Label(header_content, text="👤 GERENCIADOR DE PERFIS", 
                                  font=("Arial", 20, "bold"), 
                                  bg=ModernProfileTheme.PRIMARY, fg=ModernProfileTheme.TEXT_WHITE)
            title_label.pack(expand=True, pady=(15, 5))
            
            subtitle_label = tk.Label(header_content, text="Crie e gerencie perfis personalizados para diferentes usuários", 
                                     font=("Arial", 11), 
                                     bg=ModernProfileTheme.PRIMARY, fg=ModernProfileTheme.TEXT_GRAY)
            subtitle_label.pack(pady=(0, 15))
        
    def create_profile_list(self, parent):
        """Cria lista de perfis."""
        # Título da seção
        title_frame = tk.Frame(parent, bg=ModernProfileTheme.BG_CARD)
        title_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(title_frame, text="📋 Perfis Disponíveis", 
                font=("Arial", 14, "bold"), 
                bg=ModernProfileTheme.BG_CARD, fg=ModernProfileTheme.TEXT_WHITE).pack(side=tk.LEFT)
        
        # Botão novo perfil
        new_btn = tk.Button(title_frame, text="+ Novo", command=self.create_new_profile,
                           font=("Arial", 9, "bold"), bg=ModernProfileTheme.SUCCESS, 
                           fg=ModernProfileTheme.TEXT_WHITE, relief=tk.FLAT, cursor="hand2",
                           padx=15, pady=5)
        new_btn.pack(side=tk.RIGHT)
        
        # Frame da lista com scroll
        list_frame = tk.Frame(parent, bg=ModernProfileTheme.BG_CARD)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Canvas e scrollbar para lista
        canvas = tk.Canvas(list_frame, bg=ModernProfileTheme.BG_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=ModernProfileTheme.BG_CARD)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.profile_canvas = canvas
        
    def create_profile_details(self, parent):
        """Cria painel de detalhes do perfil."""
        # Título da seção
        title_frame = tk.Frame(parent, bg=ModernProfileTheme.BG_CARD)
        title_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        tk.Label(title_frame, text="🔧 Detalhes do Perfil", 
                font=("Arial", 14, "bold"), 
                bg=ModernProfileTheme.BG_CARD, fg=ModernProfileTheme.TEXT_WHITE).pack()
        
        # Área de detalhes
        details_frame = tk.Frame(parent, bg=ModernProfileTheme.BG_CARD)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Nome do perfil selecionado
        self.selected_name_label = tk.Label(details_frame, text="Nenhum perfil selecionado", 
                                           font=("Arial", 16, "bold"), 
                                           bg=ModernProfileTheme.BG_CARD, fg=ModernProfileTheme.TEXT_GRAY)
        self.selected_name_label.pack(pady=(0, 20))
        
        # Informações do perfil
        info_frame = tk.Frame(details_frame, bg=ModernProfileTheme.BG_LIGHT, relief=tk.RAISED, bd=1)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.info_text = tk.Text(info_frame, height=8, font=("Consolas", 10), 
                                bg=ModernProfileTheme.BG_LIGHT, fg=ModernProfileTheme.TEXT_WHITE,
                                relief=tk.FLAT, wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botões de ação
        actions_frame = tk.Frame(details_frame, bg=ModernProfileTheme.BG_CARD)
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Linha 1 de botões
        btn_frame1 = tk.Frame(actions_frame, bg=ModernProfileTheme.BG_CARD)
        btn_frame1.pack(fill=tk.X, pady=(0, 10))
        
        self.select_btn = tk.Button(btn_frame1, text="✓ Selecionar e Aplicar", command=self.select_profile,
                                   font=("Arial", 10, "bold"), bg=ModernProfileTheme.SUCCESS, 
                                   fg=ModernProfileTheme.TEXT_WHITE, relief=tk.FLAT, cursor="hand2",
                                   height=2, state=tk.DISABLED)
        self.select_btn.pack(fill=tk.X, pady=2)
        
        self.edit_btn = tk.Button(btn_frame1, text="✏️ Editar Perfil", command=self.edit_profile,
                                 font=("Arial", 10, "bold"), bg=ModernProfileTheme.INFO, 
                                 fg=ModernProfileTheme.TEXT_WHITE, relief=tk.FLAT, cursor="hand2",
                                 height=2, state=tk.DISABLED)
        self.edit_btn.pack(fill=tk.X, pady=2)
        
        # Linha 2 de botões
        btn_frame2 = tk.Frame(actions_frame, bg=ModernProfileTheme.BG_CARD)
        btn_frame2.pack(fill=tk.X)
        
        self.duplicate_btn = tk.Button(btn_frame2, text="📋 Duplicar Perfil", command=self.duplicate_profile,
                                      font=("Arial", 10, "bold"), bg=ModernProfileTheme.WARNING, 
                                      fg=ModernProfileTheme.TEXT_WHITE, relief=tk.FLAT, cursor="hand2",
                                      height=2, state=tk.DISABLED)
        self.duplicate_btn.pack(fill=tk.X, pady=2)
        
        self.delete_btn = tk.Button(btn_frame2, text="🗑️ Excluir Perfil", command=self.delete_profile,
                                   font=("Arial", 10, "bold"), bg=ModernProfileTheme.ERROR, 
                                   fg=ModernProfileTheme.TEXT_WHITE, relief=tk.FLAT, cursor="hand2",
                                   height=2, state=tk.DISABLED)
        self.delete_btn.pack(fill=tk.X, pady=2)
        
    def create_footer(self):
        """Cria footer."""
        footer_frame = tk.Frame(self.root, bg=ModernProfileTheme.BG_LIGHT, height=50)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        # Status
        self.status_label = tk.Label(footer_frame, text="✅ Pronto", 
                                    font=("Arial", 10), bg=ModernProfileTheme.BG_LIGHT, 
                                    fg=ModernProfileTheme.TEXT_WHITE)
        self.status_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Perfil atual
        self.current_profile_label = tk.Label(footer_frame, text=f"Perfil atual: {self.current_profile or 'Nenhum'}", 
                                             font=("Arial", 10, "bold"), bg=ModernProfileTheme.BG_LIGHT, 
                                             fg=ModernProfileTheme.SUCCESS)
        self.current_profile_label.pack(side=tk.RIGHT, padx=20, pady=15)
        
    def refresh_profiles(self):
        """Atualiza lista de perfis."""
        # Limpar lista atual
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        profiles = self.profile_manager.list_profiles()
        
        if not profiles:
            # Mensagem quando não há perfis
            no_profiles_frame = tk.Frame(self.scrollable_frame, bg=ModernProfileTheme.BG_CARD)
            no_profiles_frame.pack(fill=tk.X, pady=20)
            
            tk.Label(no_profiles_frame, text="📭 Nenhum perfil encontrado", 
                    font=("Arial", 12), bg=ModernProfileTheme.BG_CARD, 
                    fg=ModernProfileTheme.TEXT_MUTED).pack()
            
            tk.Label(no_profiles_frame, text="Clique em '+ Novo' para criar seu primeiro perfil", 
                    font=("Arial", 10), bg=ModernProfileTheme.BG_CARD, 
                    fg=ModernProfileTheme.TEXT_MUTED).pack()
        else:
            # Criar cards para cada perfil
            for profile_name in profiles:
                self.create_profile_card(profile_name)
                
    def create_profile_card(self, profile_name):
        """Cria card para um perfil."""
        # Frame principal do card
        card_frame = tk.Frame(self.scrollable_frame, bg=ModernProfileTheme.BG_LIGHT, 
                             relief=tk.RAISED, bd=1, cursor="hand2")
        card_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Conteúdo do card
        content_frame = tk.Frame(card_frame, bg=ModernProfileTheme.BG_LIGHT)
        content_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Nome do perfil
        name_label = tk.Label(content_frame, text=f"👤 {profile_name}", 
                             font=("Arial", 12, "bold"), 
                             bg=ModernProfileTheme.BG_LIGHT, fg=ModernProfileTheme.TEXT_WHITE,
                             anchor=tk.W)
        name_label.pack(fill=tk.X)
        
        # Informações adicionais
        config = self.profile_manager.load_profile_config(profile_name)
        if config:
            info_text = f"Configurações: {len(config)} itens"
            if 'created_date' in config:
                info_text += f" • Criado: {config['created_date']}"
        else:
            info_text = "Perfil vazio"
            
        info_label = tk.Label(content_frame, text=info_text, 
                             font=("Arial", 9), 
                             bg=ModernProfileTheme.BG_LIGHT, fg=ModernProfileTheme.TEXT_GRAY,
                             anchor=tk.W)
        info_label.pack(fill=tk.X)
        
        # Indicador se é o perfil atual
        if profile_name == self.current_profile:
            current_label = tk.Label(content_frame, text="✓ PERFIL ATIVO", 
                                    font=("Arial", 8, "bold"), 
                                    bg=ModernProfileTheme.BG_LIGHT, fg=ModernProfileTheme.SUCCESS,
                                    anchor=tk.W)
            current_label.pack(fill=tk.X)
            card_frame.configure(highlightbackground=ModernProfileTheme.SUCCESS, highlightthickness=2)
        
        # Bind click events
        def on_click(event, name=profile_name):
            self.select_profile_for_details(name)
            
        def on_enter(event):
            card_frame.configure(bg=ModernProfileTheme.BG_HOVER)
            content_frame.configure(bg=ModernProfileTheme.BG_HOVER)
            name_label.configure(bg=ModernProfileTheme.BG_HOVER)
            info_label.configure(bg=ModernProfileTheme.BG_HOVER)
            if profile_name == self.current_profile:
                current_label.configure(bg=ModernProfileTheme.BG_HOVER)
                
        def on_leave(event):
            card_frame.configure(bg=ModernProfileTheme.BG_LIGHT)
            content_frame.configure(bg=ModernProfileTheme.BG_LIGHT)
            name_label.configure(bg=ModernProfileTheme.BG_LIGHT)
            info_label.configure(bg=ModernProfileTheme.BG_LIGHT)
            if profile_name == self.current_profile:
                current_label.configure(bg=ModernProfileTheme.BG_LIGHT)
        
        card_frame.bind("<Button-1>", on_click)
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        
        # Bind para todos os widgets filhos
        for widget in [content_frame, name_label, info_label]:
            widget.bind("<Button-1>", on_click)
            
    def select_profile_for_details(self, profile_name):
        """Seleciona perfil para mostrar detalhes."""
        self.selected_profile = profile_name
        self.selected_name_label.config(text=f"👤 {profile_name}", fg=ModernProfileTheme.TEXT_WHITE)
        
        # Carregar e mostrar configurações
        config = self.profile_manager.load_profile_config(profile_name)
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        if config:
            # Formatar configurações para exibição
            display_text = f"📊 CONFIGURAÇÕES DO PERFIL '{profile_name.upper()}'\n"
            display_text += "=" * 50 + "\n\n"
            
            for key, value in config.items():
                if key == 'created_date':
                    display_text += f"📅 Data de Criação: {value}\n"
                elif key == 'last_modified':
                    display_text += f"🔄 Última Modificação: {value}\n"
                else:
                    display_text += f"⚙️ {key}: {value}\n"
                    
            if not config:
                display_text += "📭 Nenhuma configuração salva ainda.\n"
        else:
            display_text = f"❌ Erro ao carregar configurações do perfil '{profile_name}'"
            
        self.info_text.insert(1.0, display_text)
        self.info_text.config(state=tk.DISABLED)
        
        # Habilitar botões
        self.select_btn.config(state=tk.NORMAL)
        self.edit_btn.config(state=tk.NORMAL)
        self.duplicate_btn.config(state=tk.NORMAL)
        self.delete_btn.config(state=tk.NORMAL)
        
    def create_new_profile(self):
        """Cria novo perfil."""
        name = simpledialog.askstring("Novo Perfil", "Digite o nome do novo perfil:")
        if name:
            name = name.strip()
            if not name:
                messagebox.showerror("Erro", "Nome do perfil não pode estar vazio!")
                return
                
            # Verificar se já existe
            if name in self.profile_manager.list_profiles():
                if not messagebox.askyesno("Perfil Existe", f"O perfil '{name}' já existe. Deseja sobrescrever?"):
                    return
                    
            # Criar perfil com configurações padrão
            default_config = {
                'created_date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'last_modified': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'EAR_THRESHOLD': 0.25,
                'BLINK_CONSECUTIVE_FRAMES': 4,
                'SMOOTHING_FACTOR': 0.3,
                'MOUSE_SENSITIVITY_MULTIPLIER': 1.3,
                'CLICK_DEBOUNCE_TIME': 0.4
            }
            
            if self.profile_manager.create_profile(name, default_config):
                self.update_status(f"✅ Perfil '{name}' criado com sucesso!")
                self.refresh_profiles()
            else:
                messagebox.showerror("Erro", f"Erro ao criar perfil '{name}'!")
                
    def select_profile(self):
        """Seleciona perfil como ativo."""
        if hasattr(self, 'selected_profile'):
            self.current_profile = self.selected_profile
            self.save_current_profile()
            self.update_status(f"✅ Perfil '{self.selected_profile}' selecionado como ativo!")
            self.current_profile_label.config(text=f"Perfil atual: {self.current_profile}")
            self.refresh_profiles()
            
    def edit_profile(self):
        """Edita perfil selecionado."""
        if hasattr(self, 'selected_profile'):
            # Abrir janela de edição
            self.open_edit_window(self.selected_profile)
            
    def open_edit_window(self, profile_name):
        """Abre janela de edição de perfil."""
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Editar Perfil - {profile_name}")
        edit_window.geometry("500x400")
        edit_window.configure(bg=ModernProfileTheme.BG_DARK)
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Centralizar janela
        edit_window.update_idletasks()
        x = (edit_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (edit_window.winfo_screenheight() // 2) - (400 // 2)
        edit_window.geometry(f"500x400+{x}+{y}")
        
        # Título
        title_label = tk.Label(edit_window, text=f"✏️ Editando: {profile_name}", 
                              font=("Arial", 14, "bold"), 
                              bg=ModernProfileTheme.BG_DARK, fg=ModernProfileTheme.TEXT_WHITE)
        title_label.pack(pady=20)
        
        # Área de edição
        edit_frame = tk.Frame(edit_window, bg=ModernProfileTheme.BG_CARD)
        edit_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Text widget para edição JSON
        text_widget = tk.Text(edit_frame, font=("Consolas", 10), 
                             bg=ModernProfileTheme.BG_LIGHT, fg=ModernProfileTheme.TEXT_WHITE,
                             wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Carregar configurações atuais
        config = self.profile_manager.load_profile_config(profile_name)
        if config:
            text_widget.insert(1.0, json.dumps(config, indent=2, ensure_ascii=False))
            
        # Botões
        btn_frame = tk.Frame(edit_window, bg=ModernProfileTheme.BG_DARK)
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        def save_changes():
            try:
                new_config = json.loads(text_widget.get(1.0, tk.END))
                new_config['last_modified'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                
                if self.profile_manager.save_profile_config(profile_name, new_config):
                    self.update_status(f"✅ Perfil '{profile_name}' atualizado!")
                    self.refresh_profiles()
                    if hasattr(self, 'selected_profile') and self.selected_profile == profile_name:
                        self.select_profile_for_details(profile_name)
                    edit_window.destroy()
                else:
                    messagebox.showerror("Erro", "Erro ao salvar alterações!")
            except json.JSONDecodeError as e:
                messagebox.showerror("Erro JSON", f"Formato JSON inválido:\n{e}")
                
        save_btn = tk.Button(btn_frame, text="💾 Salvar", command=save_changes,
                            font=("Arial", 10, "bold"), bg=ModernProfileTheme.SUCCESS, 
                            fg=ModernProfileTheme.TEXT_WHITE, relief=tk.FLAT, cursor="hand2")
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = tk.Button(btn_frame, text="❌ Cancelar", command=edit_window.destroy,
                              font=("Arial", 10, "bold"), bg=ModernProfileTheme.ERROR, 
                              fg=ModernProfileTheme.TEXT_WHITE, relief=tk.FLAT, cursor="hand2")
        cancel_btn.pack(side=tk.LEFT)
        
    def duplicate_profile(self):
        """Duplica perfil selecionado."""
        if hasattr(self, 'selected_profile'):
            new_name = simpledialog.askstring("Duplicar Perfil", 
                                             f"Digite o nome para a cópia de '{self.selected_profile}':",
                                             initialvalue=f"{self.selected_profile}_copia")
            if new_name:
                new_name = new_name.strip()
                if not new_name:
                    messagebox.showerror("Erro", "Nome não pode estar vazio!")
                    return
                    
                if new_name in self.profile_manager.list_profiles():
                    messagebox.showerror("Erro", f"Perfil '{new_name}' já existe!")
                    return
                    
                # Carregar configurações do perfil original
                config = self.profile_manager.load_profile_config(self.selected_profile)
                if config:
                    config['created_date'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    config['last_modified'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    
                    if self.profile_manager.create_profile(new_name, config):
                        self.update_status(f"✅ Perfil duplicado como '{new_name}'!")
                        self.refresh_profiles()
                    else:
                        messagebox.showerror("Erro", "Erro ao duplicar perfil!")
                        
    def delete_profile(self):
        """Exclui perfil selecionado."""
        if hasattr(self, 'selected_profile'):
            if messagebox.askyesno("Confirmar Exclusão", 
                                  f"Tem certeza que deseja excluir o perfil '{self.selected_profile}'?\n\nEsta ação não pode ser desfeita!"):
                if self.profile_manager.delete_profile(self.selected_profile):
                    self.update_status(f"✅ Perfil '{self.selected_profile}' excluído!")
                    
                    # Se era o perfil atual, limpar
                    if self.current_profile == self.selected_profile:
                        self.current_profile = None
                        self.save_current_profile()
                        self.current_profile_label.config(text="Perfil atual: Nenhum")
                        
                    # Limpar seleção
                    delattr(self, 'selected_profile')
                    self.selected_name_label.config(text="Nenhum perfil selecionado", fg=ModernProfileTheme.TEXT_GRAY)
                    self.info_text.config(state=tk.NORMAL)
                    self.info_text.delete(1.0, tk.END)
                    self.info_text.config(state=tk.DISABLED)
                    
                    # Desabilitar botões
                    self.select_btn.config(state=tk.DISABLED)
                    self.edit_btn.config(state=tk.DISABLED)
                    self.duplicate_btn.config(state=tk.DISABLED)
                    self.delete_btn.config(state=tk.DISABLED)
                    
                    self.refresh_profiles()
                else:
                    messagebox.showerror("Erro", "Erro ao excluir perfil!")
                    
    def load_current_profile(self):
        """Carrega perfil atual salvo."""
        try:
            if os.path.exists('current_profile.txt'):
                with open('current_profile.txt', 'r') as f:
                    return f.read().strip()
        except:
            pass
        return None
        
    def save_current_profile(self):
        """Salva perfil atual."""
        try:
            with open('current_profile.txt', 'w') as f:
                f.write(self.current_profile or '')
            # Aplicar configurações do perfil ao config.py
            self.apply_profile_to_config()
        except:
            pass
            
    def apply_profile_to_config(self):
        """Aplica configurações do perfil atual ao config.py."""
        if not self.current_profile:
            return
            
        try:
            # Carregar configurações do perfil
            profile_config = self.profile_manager.load_profile_config(self.current_profile)
            if not profile_config:
                return
                
            # Ler config.py atual
            config_path = 'config.py'
            if not os.path.exists(config_path):
                return
                
            with open(config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Atualizar linhas com configurações do perfil
            updated_lines = []
            for line in lines:
                line_updated = False
                for key, value in profile_config.items():
                    if key in ['created_date', 'last_modified']:
                        continue
                        
                    if line.strip().startswith(f'{key} ='):
                        if isinstance(value, str):
                            updated_lines.append(f'{key} = "{value}"\n')
                        else:
                            updated_lines.append(f'{key} = {value}\n')
                        line_updated = True
                        break
                        
                if not line_updated:
                    updated_lines.append(line)
                    
            # Salvar config.py atualizado
            with open(config_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
                
            self.update_status(f"✅ Configurações do perfil '{self.current_profile}' aplicadas!")
            
        except Exception as e:
            print(f"Erro ao aplicar perfil: {e}")
            
    def update_status(self, message):
        """Atualiza status."""
        self.status_label.config(text=message)
        self.root.update()
        
    def run(self):
        """Executa a aplicação."""
        self.root.mainloop()

def main():
    """Função principal."""
    try:
        app = ModernProfileManager()
        app.run()
    except Exception as e:
        print(f"Erro fatal: {e}")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()