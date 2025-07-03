# -*- coding: utf-8 -*-
# Arquivo: main_launcher.py - Launcher principal do POBChecker

import customtkinter as ctk
from attendance_checker import AttendanceChecker
from personnel_manager import PersonnelManager

# Define um tema de cores para a aplicação
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class POBCheckerLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- CONFIGURAÇÃO DA JANELA ---
        self.title("POBChecker - Sistema de Controle de Presença")
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Centraliza a janela na tela
        self.center_window()
        
        # --- TÍTULO PRINCIPAL ---
        self.title_label = ctk.CTkLabel(
            self, 
            text="POBChecker", 
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.title_label.pack(pady=30)
        
        self.subtitle_label = ctk.CTkLabel(
            self, 
            text="Sistema de Controle de Presença", 
            font=ctk.CTkFont(size=16)
        )
        self.subtitle_label.pack(pady=(0, 40))
        
        # --- FRAME DOS MÓDULOS ---
        self.modules_frame = ctk.CTkFrame(self)
        self.modules_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Configure grid para dois módulos lado a lado
        self.modules_frame.columnconfigure(0, weight=1)
        self.modules_frame.columnconfigure(1, weight=1)

        # --- BOTÃO CONTROLE DE PRESENÇA (ESQUERDA) ---
        self.attendance_frame = ctk.CTkFrame(self.modules_frame)
        self.attendance_frame.grid(row=0, column=0, padx=(0, 10), pady=20, sticky="nsew")
        
        self.attendance_icon = ctk.CTkLabel(
            self.attendance_frame, 
            text="📹", 
            font=ctk.CTkFont(size=24)
        )
        self.attendance_icon.pack(pady=10)
        
        self.attendance_title = ctk.CTkLabel(
            self.attendance_frame, 
            text="Controle de Presença", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.attendance_title.pack()
        
        self.attendance_desc = ctk.CTkLabel(
            self.attendance_frame, 
            text="Marcar presença usando QR Code\nou pesquisa manual", 
            font=ctk.CTkFont(size=12)
        )
        self.attendance_desc.pack(pady=5)
        
        self.attendance_button = ctk.CTkButton(
            self.attendance_frame, 
            text="Abrir Controle de Presença",
            command=self.open_attendance_checker,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.attendance_button.pack(pady=15, padx=20, fill="x")
        
        # --- BOTÃO GERENCIAMENTO DE PESSOAL (DIREITA) ---
        self.personnel_frame = ctk.CTkFrame(self.modules_frame)
        self.personnel_frame.grid(row=0, column=1, padx=(10, 0), pady=20, sticky="nsew")
        
        self.personnel_icon = ctk.CTkLabel(
            self.personnel_frame, 
            text="👥", 
            font=ctk.CTkFont(size=24)
        )
        self.personnel_icon.pack(pady=10)
        
        self.personnel_title = ctk.CTkLabel(
            self.personnel_frame, 
            text="Gerenciamento de Pessoal", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.personnel_title.pack()
        
        self.personnel_desc = ctk.CTkLabel(
            self.personnel_frame, 
            text="Cadastrar, editar e excluir\npessoas do sistema", 
            font=ctk.CTkFont(size=12)
        )
        self.personnel_desc.pack(pady=5)
        
        self.personnel_button = ctk.CTkButton(
            self.personnel_frame, 
            text="Abrir Gerenciamento",
            command=self.open_personnel_manager,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.personnel_button.pack(pady=15, padx=20, fill="x")
        
        # --- FOOTER ---
        self.footer_label = ctk.CTkLabel(
            self, 
            text="Selecione o módulo desejado para começar", 
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.footer_label.pack(pady=(20, 10))
        
    def center_window(self):
        """Centraliza a janela na tela."""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        window_width = 600
        window_height = 500
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
    def open_attendance_checker(self):
        """Abre o módulo de controle de presença."""
        try:
            print("Abrindo controle de presença...")
            
            # Minimiza o launcher
            self.withdraw()
            
            # Aguarda um pouco para garantir que a interface seja limpa
            self.after(100, self._create_attendance_checker)
            
        except Exception as e:
            print(f"Erro ao abrir controle de presença: {e}")
            self.deiconify()  # Mostra o launcher em caso de erro
    
    def _create_attendance_checker(self):
        """Cria a janela de controle de presença após um delay."""
        try:
            # Cria o controle de presença como Toplevel
            attendance_app = AttendanceChecker(master=self)
            
            # Configura para mostrar o launcher quando fechar
            def on_attendance_close():
                print("Fechando controle de presença...")
                try:
                    # Para o gerenciador de câmera
                    if hasattr(attendance_app, 'camera_manager') and attendance_app.camera_manager:
                        attendance_app.camera_manager.stop_camera()
                    attendance_app.root.destroy()
                except Exception as e:
                    print(f"Erro ao fechar controle de presença: {e}")
                finally:
                    self.deiconify()  # Mostra o launcher novamente
                    print("Launcher reexibido")
            
            attendance_app.protocol("WM_DELETE_WINDOW", on_attendance_close)
            
            # Força o foco na nova janela
            attendance_app.focus_force()
            attendance_app.lift()
            
        except Exception as e:
            print(f"Erro ao criar controle de presença: {e}")
            import traceback
            traceback.print_exc()
            self.deiconify()  # Mostra o launcher em caso de erro
    
    def open_personnel_manager(self):
        """Abre o módulo de gerenciamento de pessoal."""
        try:
            # Cria a janela de gerenciamento
            personnel_window = PersonnelManager(master=self)
            
            # Configura para não bloquear o launcher
            personnel_window.grab_set()
            
        except Exception as e:
            print(f"Erro ao abrir gerenciamento de pessoal: {e}")

if __name__ == "__main__":
    app = POBCheckerLauncher()
    app.mainloop()
