# -*- coding: utf-8 -*-
# Arquivo: attendance_checker.py - Tela de controle de presença

import customtkinter as ctk
import time
from database import Database
from audio_manager import play_beep_sound, play_success_sound, play_error_sound
from camera_manager import CameraManager

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
        self.geometry("1100x700")

        # --- INICIALIZAÇÃO DE VARIÁVEIS E BANCO DE DADOS ---
        self.db = Database()
        self.current_group = 1
        self.person_widgets = {} 
        self.event_alert = self.db.get_event("ALERT")
        self.present_cpfs = self.db.get_checks_in_event(self.event_alert)
        
        # --- GERENCIADOR DE CÂMERA ---
        self.camera_manager = None

        # --- LAYOUT DA INTERFACE ---
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # Frame Esquerdo - Câmera e Controles
        self.left_frame = ctk.CTkFrame(self.root, width=300, corner_radius=0)
        self.left_frame.grid(row=0, column=0, rowspan=2, sticky="nswe")
        self.left_frame.grid_rowconfigure(1, weight=1)
        
        self.camera_label = ctk.CTkLabel(self.left_frame, text="Câmera")
        self.camera_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.video_canvas = ctk.CTkLabel(self.left_frame, text="")
        self.video_canvas.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Frame de pesquisa manual
        self.manual_search_frame = ctk.CTkFrame(self.left_frame)
        self.manual_search_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # Botão de modo de operação
        self.mode_label = ctk.CTkLabel(self.manual_search_frame, text="Modo de Operação:", font=ctk.CTkFont(size=12, weight="bold"))
        self.mode_label.pack(padx=10, pady=(10, 5))
        
        self.mode_selector = ctk.CTkSegmentedButton(
            self.manual_search_frame, 
            values=["Check Alert", "Check In/Out"], 
            command=self.change_mode
        )
        self.mode_selector.set("Check Alert")
        self.mode_selector.pack(padx=10, pady=5)
        
        self.current_mode = "Check Alert"
        
        self.search_label = ctk.CTkLabel(self.manual_search_frame, text="Pesquisa Manual (Nome ou CPF):")
        self.search_label.pack(padx=10, pady=(10, 0))
        
        self.search_entry = ctk.CTkEntry(self.manual_search_frame, placeholder_text="Digite para pesquisar...")
        self.search_entry.pack(padx=10, pady=5, fill="x")
        
        self.search_button = ctk.CTkButton(self.manual_search_frame, text="Marcar Presença", command=self.manual_check_in)
        self.search_button.pack(padx=10, pady=(0, 10))

        # Frame Direito - Lista e Estatísticas
        self.right_frame = ctk.CTkFrame(self.root)
        self.right_frame.grid(row=0, column=1, rowspan=2, sticky="nswe", padx=10, pady=10)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(2, weight=1)

        # Controles Superiores
        self.top_controls_frame = ctk.CTkFrame(self.right_frame)
        self.top_controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.top_controls_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.group_selector = ctk.CTkSegmentedButton(self.top_controls_frame, values=["Grupo 1", "Grupo 2"], command=self.change_group)
        self.group_selector.set("Grupo 1")
        self.group_selector.grid(row=0, column=0, padx=5, pady=5)
        
        # Estatísticas
        self.stats_frame = ctk.CTkFrame(self.top_controls_frame)
        self.stats_frame.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="e")
        
        self.total_label = ctk.CTkLabel(self.stats_frame, text="Total: 0", font=ctk.CTkFont(size=14, weight="bold"))
        self.total_label.pack(side="left", padx=10)
        
        self.present_label = ctk.CTkLabel(self.stats_frame, text="Presentes: 0", font=ctk.CTkFont(size=14, weight="bold"), text_color="#34A853")
        self.present_label.pack(side="left", padx=10)
        
        self.absent_label = ctk.CTkLabel(self.stats_frame, text="Ausentes: 0", font=ctk.CTkFont(size=14, weight="bold"), text_color="#EA4335")
        self.absent_label.pack(side="left", padx=10)
        
        # Lista de Pessoas
        self.list_header = ctk.CTkLabel(self.right_frame, text="Lista de Pessoas", font=ctk.CTkFont(size=16, weight="bold"))
        self.list_header.grid(row=1, column=0, pady=(0, 5), sticky="w", padx=10)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self.right_frame, label_text="")
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Barra de Status
        self.status_bar = ctk.CTkLabel(self.root, text="Aponte o QR Code para a câmera.", anchor="w")
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
        """Processa os dados lidos do QR Code (CPF|Nome ou só CPF)."""
        print(f"Processando QR Code: {qr_data}")
        
        # Extrai CPF e nome dos dados do QR Code
        cpf, nome_qr = self.db.parse_qr_data(qr_data)
        
        if not cpf:
            self.update_status_bar("QR Code inválido: formato não reconhecido.", "red")
            play_error_sound()
            return
            
        if self.current_mode == "Check Alert":
            # Modo Check Alert - verifica se a pessoa está cadastrada
            person_data = self.db.find_person_by_cpf(cpf)
            if person_data:
                cpf_db, nome_db, grupo = person_data
                nome_display = nome_qr if nome_qr else nome_db
                
                if cpf in self.present_cpfs:
                    self.update_status_bar(f"{nome_display} já teve a presença registrada.", "blue")
                else:
                    self.mark_as_present((cpf_db, nome_display, grupo))
            else:
                self.update_status_bar("QR Code inválido: CPF não encontrado na listagem.", "red")
                play_error_sound()
                
        elif self.current_mode == "Check In/Out":
            # Modo Check In/Out - adiciona ou remove da tabela POB
            person_in_pob = self.db.find_person_by_cpf(cpf)
            nome_display = nome_qr if nome_qr else "Pessoa não identificada"
            
            if person_in_pob:
                # Pessoa já está no POB, remove
                if self.db.remove_person_from_pob(cpf):
                    self.update_status_bar(f"{nome_display} removido do POB.", "orange")
                    play_beep_sound()
                    self.present_cpfs.discard(cpf)  # Remove dos presentes também
                    self.update_person_list()
                else:
                    self.update_status_bar("Erro ao remover pessoa do POB.", "red")
                    play_error_sound()
            else:
                # Pessoa não está no POB, adiciona
                if nome_qr and self.db.add_person_to_pob(cpf, nome_qr, self.current_group):
                    self.update_status_bar(f"{nome_display} adicionado ao POB.", "green")
                    play_success_sound()
                    self.update_person_list()
                else:
                    self.update_status_bar("Erro ao adicionar pessoa ao POB ou dados incompletos.", "red")
                    play_error_sound()

    def change_mode(self, mode):
        """Muda o modo de operação entre Check Alert e Check In/Out."""
        self.current_mode = mode
        if mode == "Check Alert":
            self.search_button.configure(text="Marcar Presença")
            self.update_status_bar("Modo: Check Alert - Aponte o QR Code para verificar presença.", "blue")
        else:
            self.search_button.configure(text="Check In/Out")
            self.update_status_bar("Modo: Check In/Out - Aponte o QR Code para adicionar/remover do POB.", "orange")

    def manual_check_in(self):
        """Busca uma pessoa pelo termo na caixa de pesquisa e executa ação baseada no modo."""
        search_term = self.search_entry.get()
        if not search_term:
            self.update_status_bar("Digite um nome ou CPF para pesquisar.", "orange")
            return
        
        if self.current_mode == "Check Alert":
            # Modo Check Alert - marca presença
            results = self.db.find_people_by_search(search_term)

            if len(results) == 1:
                person_data = results[0]
                if person_data[0] in self.present_cpfs:
                    self.update_status_bar(f"{person_data[1]} já teve a presença registrada.", "blue")
                else:
                    self.mark_as_present(person_data)
                    self.search_entry.delete(0, 'end')  # Limpa o campo
            elif len(results) > 1:
                names = [person[1] for person in results]
                self.update_status_bar(f"Múltiplos resultados: {', '.join(names[:3])}{'...' if len(names) > 3 else ''}", "orange")
            else:
                self.update_status_bar("Nenhuma pessoa encontrada com este nome ou CPF.", "red")
                
        elif self.current_mode == "Check In/Out":
            # Modo Check In/Out - adiciona/remove do POB
            results = self.db.find_people_by_search(search_term)
            
            if len(results) == 1:
                person_data = results[0]
                cpf, nome, grupo = person_data
                # Simula processamento de QR Code
                qr_data = f"{cpf}|{nome}"
                self.process_qr_code(qr_data)
                self.search_entry.delete(0, 'end')  # Limpa o campo
            elif len(results) > 1:
                names = [person[1] for person in results]
                self.update_status_bar(f"Múltiplos resultados: {', '.join(names[:3])}{'...' if len(names) > 3 else ''}", "orange")
            else:
                self.update_status_bar("Pessoa não encontrada. Use QR Code para adicionar novas pessoas.", "red")

    def mark_as_present(self, person_data):
        """Função central para marcar uma pessoa como presente."""
        cpf, nome, grupo = person_data
        
        self.db.person_check(cpf, nome, self.event_alert)
        self.present_cpfs.add(cpf)
        
        if grupo == self.current_group:
            if cpf in self.person_widgets:
                widget = self.person_widgets[cpf]
                widget.configure(fg_color="#D1E7DD")  # Verde claro
                for child in widget.winfo_children():
                    child.configure(fg_color="#D1E7DD")
                play_beep_sound()
        
        self.update_stats()
        self.update_status_bar(f"Presença registrada: {nome} (Grupo {grupo})", "green")

    def change_group(self, value):
        """Chamado quando o seletor de grupo é alterado."""
        group_number_str = value.replace("Grupo ", "")
        self.current_group = int(group_number_str)
        self.update_person_list()
        self.update_status_bar(f"Exibindo Grupo {self.current_group}", "white")

    def update_person_list(self):
        """Limpa e recarrega a lista de pessoas na UI com base no grupo selecionado."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.person_widgets.clear()

        people = self.db.get_people_by_group(self.current_group)

        for person in people:
            cpf, nome, _ = person
            
            row_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2, padx=2)

            if cpf in self.present_cpfs:
                row_frame.configure(fg_color="#D1E7DD")

            label_nome = ctk.CTkLabel(row_frame, text=nome, anchor="w")
            label_nome.pack(side="left", padx=10, pady=5, expand=True, fill="x")
            label_cpf = ctk.CTkLabel(row_frame, text=cpf, anchor="e", width=150)
            label_cpf.pack(side="right", padx=10, pady=5)
            
            if cpf in self.present_cpfs:
                for child in row_frame.winfo_children():
                    child.configure(fg_color=row_frame.cget("fg_color"))
            
            self.person_widgets[cpf] = row_frame

        self.update_stats()

    def update_stats(self):
        """Recalcula e atualiza os rótulos de estatísticas."""
        people_in_group = self.db.get_people_by_group(self.current_group)
        total_count = len(people_in_group)
        
        present_count = 0
        for person in people_in_group:
            if person[0] in self.present_cpfs:
                present_count += 1
                
        absent_count = total_count - present_count

        self.total_label.configure(text=f"Total: {total_count}")
        self.present_label.configure(text=f"Presentes: {present_count}")
        self.absent_label.configure(text=f"Ausentes: {absent_count}")
        
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
