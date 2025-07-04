# -*- coding: utf-8 -*-
# Arquivo: attendance_checker.py - Tela de controle de presença

import customtkinter as ctk
import time
from database import Database
from audio_manager import play_beep_sound, play_success_sound, play_error_sound
from camera_manager import CameraManager
from config import QR_EVENT_CODE, DEFAULT_MODE

# Define um tema de cores para a aplicação
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AttendanceChecker:
    def __init__(self, master=None):
        # Se não há master, cria como CTk (janela principal)
        if master is None:
            self.root = ctk.CTk()
        else:
            # Se há master, cria como Toplevel
            self.root = ctk.CTkToplevel(master)
            
        # Redireciona métodos do root para self
        self.title = self.root.title
        self.geometry = self.root.geometry
        self.grid_columnconfigure = self.root.grid_columnconfigure
        self.grid_rowconfigure = self.root.grid_rowconfigure
        self.protocol = self.root.protocol
        self.withdraw = self.root.withdraw
        self.deiconify = self.root.deiconify
        self.after = self.root.after
        self.mainloop = self.root.mainloop
        self.destroy = self.root.destroy
        self.focus_force = self.root.focus_force
        self.lift = self.root.lift

        # --- CONFIGURAÇÃO DA JANELA PRINCIPAL ---
        self.title("POBChecker - Controle de Presença")
        self.geometry("1000x700")

        # --- INICIALIZAÇÃO DE VARIÁVEIS E BANCO DE DADOS ---
        self.db = Database()
        self.current_group = 1
        self.person_widgets = {} 
        
        # Modos de operação
        self.current_mode = DEFAULT_MODE  # "CIO" ou "CEV"
        self.active_event_id = None
        
        # Executa limpeza automática
        self.db.clean_old_records()
        
        if self.current_mode == "CEV":
            self.active_event_id = self.db.get_active_event()
        
        # --- GERENCIADOR DE CÂMERA ---
        self.camera_manager = None

        # --- LAYOUT DA INTERFACE ---
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # Frame Esquerdo - Câmera e Controles
        self.left_frame = ctk.CTkFrame(self.root, width=180, corner_radius=0)
        self.left_frame.grid(row=0, column=0, rowspan=2, sticky="nswe")
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_propagate(False)  # Mantém o tamanho fixo
        
        self.camera_label = ctk.CTkLabel(self.left_frame, text="Câmera", font=ctk.CTkFont(size=12, weight="bold"))
        self.camera_label.grid(row=0, column=0, padx=3, pady=3)
        
        self.video_canvas = ctk.CTkLabel(self.left_frame, text="", width=160, height=120)
        self.video_canvas.grid(row=1, column=0, padx=3, pady=3)
        
        # Frame de controles
        self.controls_frame = ctk.CTkFrame(self.left_frame)
        self.controls_frame.grid(row=2, column=0, padx=3, pady=3, sticky="ew")
        
        # Indicador de modo atual
        self.mode_indicator_label = ctk.CTkLabel(
            self.controls_frame, 
            text=f"MODO: {self.current_mode}", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self._get_mode_color()
        )
        self.mode_indicator_label.pack(padx=3, pady=3)
        
        # Status do evento (apenas para CEV)
        self.event_status_label = ctk.CTkLabel(
            self.controls_frame, 
            text="", 
            font=ctk.CTkFont(size=9)
        )
        self.event_status_label.pack(padx=3, pady=1)
        
        # Frame de pesquisa manual
        self.manual_search_frame = ctk.CTkFrame(self.controls_frame)
        self.manual_search_frame.pack(padx=3, pady=3, fill="x")
        
        self.search_label = ctk.CTkLabel(self.manual_search_frame, text="Pesquisa Manual:", font=ctk.CTkFont(size=9))
        self.search_label.pack(padx=3, pady=(3, 0))
        
        self.search_entry = ctk.CTkEntry(self.manual_search_frame, placeholder_text="Nome ou CPF...", height=24)
        self.search_entry.pack(padx=3, pady=2, fill="x")
        
        self.search_button = ctk.CTkButton(
            self.manual_search_frame, 
            text=self._get_search_button_text(), 
            command=self.manual_action,
            height=24,
            font=ctk.CTkFont(size=9)
        )
        self.search_button.pack(padx=3, pady=(0, 3))

        # Frame Direito - Lista e Estatísticas
        self.right_frame = ctk.CTkFrame(self.root)
        self.right_frame.grid(row=0, column=1, rowspan=2, sticky="nswe", padx=10, pady=10)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(2, weight=1)

        # Controles Superiores
        self.top_controls_frame = ctk.CTkFrame(self.right_frame)
        self.top_controls_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        self.top_controls_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.group_selector = ctk.CTkSegmentedButton(
            self.top_controls_frame, 
            values=["Grupo 1", "Grupo 2"], 
            command=self.change_group
        )
        self.group_selector.set("Grupo 1")
        self.group_selector.grid(row=0, column=0, padx=5, pady=5)
        
        # Estatísticas
        self.stats_frame = ctk.CTkFrame(self.top_controls_frame)
        self.stats_frame.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="e")
        
        self.total_label = ctk.CTkLabel(self.stats_frame, text="Total: 0", font=ctk.CTkFont(size=14, weight="bold"))
        self.total_label.pack(side="left", padx=10)
        
        self.checked_label = ctk.CTkLabel(self.stats_frame, text="Checados: 0", font=ctk.CTkFont(size=14, weight="bold"), text_color="#34A853")
        self.checked_label.pack(side="left", padx=10)
        
        self.unchecked_label = ctk.CTkLabel(self.stats_frame, text="Não Checados: 0", font=ctk.CTkFont(size=14, weight="bold"), text_color="#EA4335")
        self.unchecked_label.pack(side="left", padx=10)
        
        # Configuração da interface baseada no modo
        self._setup_mode_interface()

        # Barra de Status
        self.status_bar = ctk.CTkLabel(self.root, text=self._get_initial_status_message(), anchor="w")
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        # Inicialização
        self.update_person_list()
        
        # Inicia o gerenciador de câmera após um pequeno delay
        self.after(500, self.init_camera_manager)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def init_camera_manager(self):
        """Initializa o gerenciador de câmera."""
        print("Inicializando gerenciador de câmera...")
        self.camera_manager = CameraManager(
            video_canvas=self.video_canvas,
            on_qr_detected=self.process_qr_code
        )
        
        if not self.camera_manager.start_camera():
            self.update_status_bar("Erro: Câmera não encontrada ou não pôde ser inicializada.", "red")

    def process_qr_code(self, qr_data):
        """Processa os dados lidos do QR Code."""
        print(f"Processando QR Code: {qr_data}")
        
        # Verifica se é o QR_EVENT especial
        if qr_data.strip() == QR_EVENT_CODE:
            self.handle_qr_event()
            return
        
        # Extrai CPF e nome dos dados do QR Code
        cpf, nome_qr = self.db.parse_qr_data(qr_data)
        
        if not cpf:
            self.update_status_bar("QR Code inválido: formato não reconhecido.", "red")
            play_error_sound()
            return
        
        if self.current_mode == "CIO":
            self.handle_cio_mode(cpf, nome_qr)
        elif self.current_mode == "CEV":
            self.handle_cev_mode(cpf, nome_qr)

    def handle_qr_event(self):
        """Trata o QR_EVENT para alternar entre modos."""
        if self.current_mode == "CIO":
            # Ativa modo CEV
            self.current_mode = "CEV"
            self.active_event_id = self.db.create_event()
            self.update_status_bar(f"Modo CEV ativado. Evento #{self.active_event_id} criado.", "green")
            play_success_sound()
        elif self.current_mode == "CEV" and self.active_event_id:
            # Desativa modo CEV
            self.db.close_event(self.active_event_id)
            self.update_status_bar(f"Modo CEV desativado. Evento #{self.active_event_id} fechado.", "orange")
            self.current_mode = "CIO"
            self.active_event_id = None
            play_beep_sound()
        else:
            # CEV sem evento ativo - cria novo evento
            self.active_event_id = self.db.create_event()
            self.update_status_bar(f"Evento #{self.active_event_id} criado no modo CEV.", "green")
            play_success_sound()
        
        # Atualiza interface
        self.mode_indicator_label.configure(
            text=f"MODO: {self.current_mode}",
            text_color=self._get_mode_color()
        )
        self.search_button.configure(text=self._get_search_button_text())
        self._setup_mode_interface()
        self.update_person_list()

    def handle_cio_mode(self, cpf, nome_qr):
        """Trata QR Code no modo CIO (Check In/Out)."""
        # Verifica se a pessoa está no POB
        person_in_pob = self.db.is_person_in_pob(cpf)
        nome_display = nome_qr if nome_qr else "Pessoa não identificada"
        
        if person_in_pob:
            # Pessoa está no POB, remove (Check Out)
            if self.db.remove_person_from_pob(cpf):
                self.update_status_bar(f"CHECK OUT: {nome_display} saiu da plataforma.", "orange")
                play_beep_sound()
                self.update_person_list()
            else:
                self.update_status_bar("Erro ao fazer check out.", "red")
                play_error_sound()
        else:
            # Pessoa não está no POB, adiciona (Check In)
            if nome_qr and self.db.add_person_to_pob(cpf, nome_qr, self.current_group):
                self.update_status_bar(f"CHECK IN: {nome_display} entrou na plataforma.", "green")
                play_success_sound()
                self.update_person_list()
            else:
                self.update_status_bar("Erro ao fazer check in ou dados incompletos.", "red")
                play_error_sound()

    def handle_cev_mode(self, cpf, nome_qr):
        """Trata QR Code no modo CEV (Check Event)."""
        if not self.active_event_id:
            self.update_status_bar("Nenhum evento ativo. Use QR_EVENT para criar um evento.", "red")
            play_error_sound()
            return
        
        # Verifica se a pessoa está cadastrada
        person_data = self.db.find_person_by_cpf(cpf)
        if not person_data:
            self.update_status_bar("Pessoa não encontrada no cadastro.", "red")
            play_error_sound()
            return
        
        cpf_db, nome_db, grupo = person_data
        nome_display = nome_qr if nome_qr else nome_db
        
        # Verifica se a pessoa já está checada no evento
        if self.db.is_person_checked_in_event(cpf, self.active_event_id):
            # Pessoa já checada - fazer estorno
            if self.db.remove_check_event(cpf, self.active_event_id):
                self.update_status_bar(f"Estorno realizado: {nome_display} removido da lista de presença", "orange")
                play_beep_sound()
                self.update_person_list()
            else:
                self.update_status_bar("Erro ao realizar estorno de presença.", "red")
                play_error_sound()
        else:
            # Pessoa não checada - registrar presença
            if self.db.record_check_event(cpf, nome_display, self.active_event_id):
                self.update_status_bar(f"Presença registrada: {nome_display}", "green")
                play_success_sound()
                self.update_person_list()
            else:
                self.update_status_bar("Erro ao registrar presença.", "red")
                play_error_sound()

    def manual_action(self):
        """Executa ação manual baseada no modo atual."""
        search_term = self.search_entry.get()
        if not search_term:
            self.update_status_bar("Digite um nome ou CPF para pesquisar.", "orange")
            return
        
        if self.current_mode == "CIO":
            self._manual_cio_action(search_term)
        elif self.current_mode == "CEV":
            self._manual_cev_action(search_term)

    def _manual_cio_action(self, search_term):
        """Ação manual para modo CIO."""
        results = self.db.find_people_by_search(search_term)
        
        if len(results) == 1:
            person_data = results[0]
            cpf, nome, grupo = person_data
            # Simula processamento de QR Code
            qr_data = f"{cpf}|{nome}"
            self.handle_cio_mode(cpf, nome)
            self.search_entry.delete(0, 'end')
        elif len(results) > 1:
            names = [person[1] for person in results]
            self.update_status_bar(f"Múltiplos resultados: {', '.join(names[:3])}{'...' if len(names) > 3 else ''}", "orange")
        else:
            self.update_status_bar("Pessoa não encontrada. Use QR Code para adicionar novas pessoas.", "red")

    def _manual_cev_action(self, search_term):
        """Ação manual para modo CEV."""
        if not self.active_event_id:
            self.update_status_bar("Nenhum evento ativo. Use QR_EVENT para criar um evento.", "red")
            return
            
        results = self.db.find_people_by_search(search_term)

        if len(results) == 1:
            person_data = results[0]
            cpf, nome, grupo = person_data
            self.handle_cev_mode(cpf, nome)
            self.search_entry.delete(0, 'end')
        elif len(results) > 1:
            names = [person[1] for person in results]
            self.update_status_bar(f"Múltiplos resultados: {', '.join(names[:3])}{'...' if len(names) > 3 else ''}", "orange")
        else:
            self.update_status_bar("Nenhuma pessoa encontrada com este nome ou CPF.", "red")

    def change_group(self, value):
        """Chamado quando o seletor de grupo é alterado."""
        group_number_str = value.replace("Grupo ", "")
        self.current_group = int(group_number_str)
        self.update_person_list()
        self.update_status_bar(f"Exibindo Grupo {self.current_group}", "white")

    def update_person_list(self):
        """Atualiza a lista de pessoas baseada no modo atual."""
        if self.current_mode == "CIO":
            self._update_cio_list()
        elif self.current_mode == "CEV":
            self._update_cev_list()

    def _update_cio_list(self):
        """Atualiza lista para modo CIO - apenas pessoas no POB."""
        # Limpa lista atual
        if hasattr(self, 'scrollable_frame') and self.scrollable_frame.winfo_exists():
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
        
        # Limpa frames do modo CEV se existirem
        if hasattr(self, 'unchecked_frame') and self.unchecked_frame.winfo_exists():
            for widget in self.unchecked_frame.winfo_children():
                widget.destroy()
        if hasattr(self, 'checked_frame') and self.checked_frame.winfo_exists():
            for widget in self.checked_frame.winfo_children():
                widget.destroy()
        
        self.person_widgets.clear()

        # Busca pessoas no POB do grupo atual
        people = self.db.get_people_by_group(self.current_group)
        # Filtra apenas pessoas que estão realmente no POB (Onshore = 0)
        people_in_pob = [p for p in people if self.db.is_person_in_pob(p[0])]

        if hasattr(self, 'scrollable_frame') and self.scrollable_frame.winfo_exists():
            for person in people_in_pob:
                cpf, nome, _ = person
                
                row_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=2, padx=2)

                label_nome = ctk.CTkLabel(row_frame, text=nome, anchor="w")
                label_nome.pack(side="left", padx=10, pady=5, expand=True, fill="x")
                
                label_cpf = ctk.CTkLabel(row_frame, text=cpf, anchor="e", width=150)
                label_cpf.pack(side="right", padx=10, pady=5)
                
                self.person_widgets[cpf] = row_frame

        self._update_cio_stats(len(people_in_pob))

    def _update_cev_list(self):
        """Atualiza listas para modo CEV - separadas por checados/não checados."""
        # Limpa lista do modo CIO se existir
        if hasattr(self, 'scrollable_frame') and self.scrollable_frame.winfo_exists():
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
        
        # Limpa listas atuais do modo CEV
        if hasattr(self, 'unchecked_frame') and self.unchecked_frame.winfo_exists():
            for widget in self.unchecked_frame.winfo_children():
                widget.destroy()
        if hasattr(self, 'checked_frame') and self.checked_frame.winfo_exists():
            for widget in self.checked_frame.winfo_children():
                widget.destroy()
        
        self.person_widgets.clear()

        if not self.active_event_id:
            self._update_cev_stats(0, 0)
            return

        # Busca pessoas do grupo atual
        people = self.db.get_people_by_group(self.current_group)
        checked_cpfs = self.db.get_checks_in_event(self.active_event_id)

        checked_people = []
        unchecked_people = []

        for person in people:
            cpf, nome, _ = person
            if cpf in checked_cpfs:
                checked_people.append(person)
            else:
                unchecked_people.append(person)

        # Preenche lista de não checados
        if hasattr(self, 'unchecked_frame') and self.unchecked_frame.winfo_exists():
            for person in unchecked_people:
                cpf, nome, _ = person
                
                row_frame = ctk.CTkFrame(self.unchecked_frame, fg_color="#FFF2F2")  # Fundo vermelho claro
                row_frame.pack(fill="x", pady=2, padx=2)

                label_nome = ctk.CTkLabel(row_frame, text=nome, anchor="w", fg_color="transparent")
                label_nome.pack(side="left", padx=10, pady=5, expand=True, fill="x")
                
                label_cpf = ctk.CTkLabel(row_frame, text=cpf, anchor="e", width=120, fg_color="transparent")
                label_cpf.pack(side="right", padx=10, pady=5)
                
                self.person_widgets[f"unchecked_{cpf}"] = row_frame

        # Preenche lista de checados
        if hasattr(self, 'checked_frame') and self.checked_frame.winfo_exists():
            for person in checked_people:
                cpf, nome, _ = person
                
                row_frame = ctk.CTkFrame(self.checked_frame, fg_color="#F0F8F0")  # Fundo verde claro
                row_frame.pack(fill="x", pady=2, padx=2)

                label_nome = ctk.CTkLabel(row_frame, text=nome, anchor="w", fg_color="transparent")
                label_nome.pack(side="left", padx=10, pady=5, expand=True, fill="x")
                
                label_cpf = ctk.CTkLabel(row_frame, text=cpf, anchor="e", width=120, fg_color="transparent")
                label_cpf.pack(side="right", padx=10, pady=5)
                
                self.person_widgets[f"checked_{cpf}"] = row_frame

        self._update_cev_stats(len(checked_people), len(unchecked_people))

    def _update_cio_stats(self, total_in_pob):
        """Atualiza estatísticas para modo CIO."""
        self.total_label.configure(text=f"No POB: {total_in_pob}")
        self.checked_label.configure(text="")
        self.unchecked_label.configure(text="")

    def _update_cev_stats(self, checked_count, unchecked_count):
        """Atualiza estatísticas para modo CEV."""
        total_count = checked_count + unchecked_count
        self.total_label.configure(text=f"Total: {total_count}")
        self.checked_label.configure(text=f"Checados: {checked_count}")
        self.unchecked_label.configure(text=f"Não Checados: {unchecked_count}")
        
    def update_status_bar(self, message, color_name):
        """Atualiza o texto e a cor da barra de status."""
        colors = {
            "green": "#34A853",
            "red": "#EA4335",
            "blue": "#4285F4",
            "orange": "#FBBC05",
            "white": "white"
        }
        self.status_bar.configure(text=message, text_color=colors.get(color_name, "white"))

    def on_closing(self):
        """Função chamada ao fechar a janela para liberar recursos."""
        print("Fechando aplicação...")
        
        # Para o gerenciador de câmera
        if self.camera_manager:
            self.camera_manager.stop_camera()
        
        # Destrói a janela
        self.root.destroy()
        print("Janela destruída")

    def _get_mode_color(self):
        """Retorna a cor para o indicador de modo."""
        if self.current_mode == "CIO":
            return "#4285F4"  # Azul
        else:
            return "#34A853"  # Verde

    def _get_search_button_text(self):
        """Retorna o texto do botão de pesquisa baseado no modo."""
        if self.current_mode == "CIO":
            return "Check In/Out"
        else:
            return "Marcar/Desmarcar"

    def _get_initial_status_message(self):
        """Retorna a mensagem inicial da barra de status."""
        if self.current_mode == "CIO":
            return "Modo CIO: Aponte QR Code para check in/out ou use QR_EVENT para ativar CEV."
        else:
            if self.active_event_id:
                return "Modo CEV ativo: Aponte QR Code para marcar/desmarcar presença ou QR_EVENT para desativar."
            else:
                return "Modo CEV: Use QR_EVENT para iniciar um evento."

    def _setup_mode_interface(self):
        """Configura a interface baseada no modo atual."""
        # Atualiza status do evento
        if self.current_mode == "CEV":
            if self.active_event_id:
                self.event_status_label.configure(text=f"Evento Ativo: #{self.active_event_id}")
            else:
                self.event_status_label.configure(text="Nenhum evento ativo")
        else:
            self.event_status_label.configure(text="")

        # Configura interface baseada no modo
        if self.current_mode == "CEV":
            # Modo CEV - duas listas separadas
            self._setup_cev_interface()
        else:
            # Modo CIO - lista única
            self._setup_cio_interface()

    def _setup_cio_interface(self):
        """Configura interface para modo CIO."""
        # Remove frames antigos se existirem e limpa todas as referências
        for widget in self.right_frame.winfo_children():
            if hasattr(widget, '_is_list_container') or hasattr(widget, '_is_cev_header'):
                widget.destroy()

        # Limpa referências de frames do modo CEV
        if hasattr(self, 'unchecked_frame'):
            delattr(self, 'unchecked_frame')
        if hasattr(self, 'checked_frame'):
            delattr(self, 'checked_frame')
        if hasattr(self, 'unchecked_header'):
            delattr(self, 'unchecked_header')
        if hasattr(self, 'checked_header'):
            delattr(self, 'checked_header')

        # Reseta o grid para uma coluna
        self.right_frame.grid_columnconfigure(0, weight=1)
        # Remove a coluna 1 do grid para garantir que só uma coluna fique visível
        self.right_frame.grid_columnconfigure(1, weight=0, minsize=0)
        # Esconde widgets da coluna 1 se existirem
        for widget in self.right_frame.grid_slaves(column=1):
            widget.grid_remove()
        
        # Reajusta o top_controls_frame para uma coluna
        self.top_controls_frame.grid(row=0, column=0, columnspan=1, sticky="ew", padx=10, pady=10)

        # Lista de Pessoas no POB
        self.list_header = ctk.CTkLabel(
            self.right_frame, 
            text="Pessoas no POB (Plataforma)", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.list_header.grid(row=1, column=0, pady=(0, 5), sticky="w", padx=10)
        self.list_header._is_list_container = True
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self.right_frame, label_text="")
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame._is_list_container = True

    def _setup_cev_interface(self):
        """Configura interface para modo CEV com duas listas."""
        # Remove frames antigos se existirem e limpa todas as referências
        for widget in self.right_frame.winfo_children():
            if hasattr(widget, '_is_list_container') or hasattr(widget, '_is_cev_header'):
                widget.destroy()

        # Limpa referências de frames do modo CIO
        if hasattr(self, 'scrollable_frame'):
            delattr(self, 'scrollable_frame')
        if hasattr(self, 'list_header'):
            delattr(self, 'list_header')

        # Configura grid para duas colunas iguais
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(1, weight=1)
        
        # Reajusta o top_controls_frame para duas colunas
        self.top_controls_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        # Lista de Não Checados (esquerda)
        self.unchecked_header = ctk.CTkLabel(
            self.right_frame, 
            text="Não Checados", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#EA4335"
        )
        self.unchecked_header.grid(row=1, column=0, pady=(0, 5), sticky="w", padx=10)
        self.unchecked_header._is_cev_header = True
        
        self.unchecked_frame = ctk.CTkScrollableFrame(self.right_frame, label_text="")
        self.unchecked_frame.grid(row=2, column=0, sticky="nsew", padx=(10, 5), pady=5)
        self.unchecked_frame.grid_columnconfigure(0, weight=1)
        self.unchecked_frame._is_list_container = True

        # Lista de Checados (direita)
        self.checked_header = ctk.CTkLabel(
            self.right_frame, 
            text="Checados", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#34A853"
        )
        self.checked_header.grid(row=1, column=1, pady=(0, 5), sticky="w", padx=10)
        self.checked_header._is_cev_header = True
        
        self.checked_frame = ctk.CTkScrollableFrame(self.right_frame, label_text="")
        self.checked_frame.grid(row=2, column=1, sticky="nsew", padx=(5, 10), pady=5)
        self.checked_frame.grid_columnconfigure(0, weight=1)
        self.checked_frame._is_list_container = True

if __name__ == "__main__":
    import sys
    
    # Modo de teste - apenas verifica se a câmera inicializa
    if "--test" in sys.argv:
        print("=== MODO TESTE ATTENDANCE_CHECKER ===")
        try:
            app = AttendanceChecker()
            print("✓ AttendanceChecker criado")
            
            # Aguarda um pouco para o camera manager inicializar
            time.sleep(2)
            
            if app.camera_manager and app.camera_manager.is_active():
                print("✓ Câmera inicializada com sucesso")
            else:
                print("✗ Problema com a câmera")
            
            app.on_closing()
            print("✓ Teste concluído")
            
        except Exception as e:
            print(f"✗ Erro no teste: {e}")
            import traceback
            traceback.print_exc()
    else:
        # Execução normal
        app = AttendanceChecker()
        app.mainloop()
