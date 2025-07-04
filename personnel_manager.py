# Arquivo: personnel_manager.py - Tela de gerenciamento de pessoal

import customtkinter as ctk
from database import Database

# Define um tema de cores para a aplicação
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class PersonnelManager(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Gerenciamento de Pessoal")
        self.geometry("900x700")
        # Removido self.grab_set() para não ser modal
        self.db = Database()
        self.current_editing_cpf = None  # Para controlar se estamos editando uma pessoa existente

        # --- FRAME PRINCIPAL HORIZONTAL ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        # --- LISTA DE PESSOAS À ESQUERDA ---
        self.list_frame = ctk.CTkFrame(self.main_frame, width=600)
        self.list_frame.pack(side="left", fill="y", padx=10, pady=20)
        self.list_frame.pack_propagate(False)
        self.list_label = ctk.CTkLabel(self.list_frame, text="Pessoas Cadastradas", font=ctk.CTkFont(size=16, weight="bold"))
        self.list_label.pack(pady=10)
        self.filter_frame = ctk.CTkFrame(self.list_frame)
        self.filter_frame.pack(fill="x", padx=10, pady=5)
        self.filter_label = ctk.CTkLabel(self.filter_frame, text="Filtrar por grupo:")
        self.filter_label.pack(side="left", padx=10)
        self.filter_selector = ctk.CTkSegmentedButton(
            self.filter_frame, 
            values=["Todos", "Grupo 1", "Grupo 2"], 
            command=self.filter_list
        )
        self.filter_selector.set("Todos")
        self.filter_selector.pack(side="left", padx=10)
        self.search_filter_entry = ctk.CTkEntry(self.filter_frame, placeholder_text="Buscar por nome...")
        self.search_filter_entry.pack(side="right", padx=10, fill="x", expand=True)
        self.search_filter_entry.bind("<KeyRelease>", self.on_search_filter_change)
        self.scrollable_list = ctk.CTkScrollableFrame(self.list_frame)
        self.scrollable_list.pack(fill="both", expand=True, padx=10, pady=10)

        # --- FORMULÁRIO À DIREITA ---
        self.form_frame = ctk.CTkFrame(self.main_frame)
        self.form_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        self.title_label = ctk.CTkLabel(self.form_frame, text="Gerenciamento de Pessoal", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=20)
        self.cpf_entry = ctk.CTkEntry(self.form_frame, placeholder_text="CPF (apenas números)")
        self.cpf_entry.pack(pady=10, padx=20, fill="x")
        self.nome_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Nome Completo")
        self.nome_entry.pack(pady=10, padx=20, fill="x")
        self.grupo_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Grupo (1 ou 2)")
        self.grupo_entry.pack(pady=10, padx=20, fill="x")
        self.button_frame = ctk.CTkFrame(self.form_frame)
        self.button_frame.pack(pady=20, padx=20, fill="x")
        self.save_button = ctk.CTkButton(self.button_frame, text="Salvar", command=self.save_person)
        self.save_button.pack(side="left", expand=True, padx=5)
        self.search_button = ctk.CTkButton(self.button_frame, text="Buscar por CPF", command=self.search_person)
        self.search_button.pack(side="left", expand=True, padx=5)
        self.clear_button = ctk.CTkButton(self.button_frame, text="Limpar", command=self.clear_fields)
        self.clear_button.pack(side="left", expand=True, padx=5)
        self.delete_button = ctk.CTkButton(self.button_frame, text="Excluir", fg_color="red", hover_color="darkred", command=self.delete_person)
        self.delete_button.pack(side="left", expand=True, padx=5)
        self.status_label = ctk.CTkLabel(self.form_frame, text="Preencha os campos para gerenciar pessoal", text_color="gray")
        self.status_label.pack(pady=10)

        # Carrega a lista de pessoas
        self.refresh_person_list()

    def update_save_button_text(self):
        """Atualiza o texto do botão salvar baseado no modo atual."""
        if self.current_editing_cpf:
            self.save_button.configure(text="Atualizar")
        else:
            self.save_button.configure(text="Salvar")

    def validate_cpf(self, cpf):
        """Valida se o CPF está no formato correto (apenas números e com 11 dígitos)."""
        # Remove qualquer formatação (pontos, traços, espaços)
        cpf_clean = cpf.replace(".", "").replace("-", "").replace(" ", "").strip()
        
        # Verifica se contém apenas números e tem exatamente 11 dígitos
        return cpf_clean.isdigit() and len(cpf_clean) == 11

    def clean_cpf(self, cpf):
        """Remove qualquer formatação do CPF e retorna apenas os números."""
        return cpf.replace(".", "").replace("-", "").replace(" ", "").strip()

    def validate_grupo(self, grupo):
        """Valida se o grupo é 1 ou 2."""
        return grupo in ["1", "2"]

    def clear_fields(self):
        """Limpa todos os campos do formulário."""
        self.cpf_entry.delete(0, "end")
        self.nome_entry.delete(0, "end")
        self.grupo_entry.delete(0, "end")
        self.current_editing_cpf = None
        self.update_save_button_text()
        self.update_status("Campos limpos", "blue")

    def update_status(self, message, color="gray"):
        """Atualiza a mensagem de status."""
        self.status_label.configure(text=message, text_color=color)

    def save_person(self):
        """Salva uma nova pessoa ou atualiza uma existente."""
        cpf = self.cpf_entry.get().strip()
        nome = self.nome_entry.get().strip()
        grupo = self.grupo_entry.get().strip()

        # Validações
        if not cpf or not nome or not grupo:
            self.update_status("Erro: CPF, Nome e Grupo são obrigatórios!", "red")
            return

        if not self.validate_cpf(cpf):
            self.update_status("Erro: CPF deve conter 11 dígitos!", "red")
            return

        if not self.validate_grupo(grupo):
            self.update_status("Erro: Grupo deve ser 1 ou 2!", "red")
            return

        # Remove formatação do CPF
        cpf_clean = self.clean_cpf(cpf)

        # Prepara dados da pessoa
        person_data = {
            'cpf': cpf_clean,
            'nome': nome,
            'grupo': int(grupo),
            'Onshore': 1
        }

        # Verifica se estamos editando uma pessoa existente
        if self.current_editing_cpf and self.current_editing_cpf == cpf_clean:
            # Estamos editando uma pessoa existente
            if self.db.update_person(cpf_clean, person_data):
                self.update_status(f"Pessoa {nome} atualizada com sucesso!", "green")
                self.clear_fields()
                self.refresh_person_list()
                # Atualiza a lista principal se a janela pai existir
                if hasattr(self.master, 'update_person_list'):
                    self.master.update_person_list()
            else:
                self.update_status("Erro ao atualizar pessoa!", "red")
        elif self.db.check_person_exists(cpf_clean):
            # Pessoa já existe, mas não estava sendo editada - perguntar se quer atualizar
            if self.db.update_person(cpf_clean, person_data):
                self.update_status(f"Pessoa {nome} já existia e foi atualizada!", "orange")
                self.current_editing_cpf = cpf_clean
                self.refresh_person_list()
                # Atualiza a lista principal se a janela pai existir
                if hasattr(self.master, 'update_person_list'):
                    self.master.update_person_list()
            else:
                self.update_status("Erro ao atualizar pessoa!", "red")
        else:
            # Insere nova pessoa
            if self.db.insert_person(person_data):
                self.update_status(f"Pessoa {nome} salva com sucesso!", "green")
                self.clear_fields()
                self.refresh_person_list()
                # Atualiza a lista principal se a janela pai existir
                if hasattr(self.master, 'update_person_list'):
                    self.master.update_person_list()
            else:
                self.update_status("Erro ao salvar pessoa! CPF pode já existir.", "red")

    def search_person(self):
        """Busca uma pessoa pelo CPF e preenche os campos do formulário."""
        cpf = self.cpf_entry.get().strip()
        
        if not cpf:
            self.update_status("Digite um CPF para buscar!", "orange")
            return

        if not self.validate_cpf(cpf):
            self.update_status("CPF deve conter 11 dígitos!", "red")
            return

        # Remove formatação do CPF
        cpf_clean = self.clean_cpf(cpf)

        # Busca a pessoa no banco
        person_data = self.db.get_person_details(cpf_clean)
        
        if person_data:
            cpf_db, nome, grupo = person_data
            
            # Preenche os campos
            self.cpf_entry.delete(0, "end")
            self.cpf_entry.insert(0, cpf_db)
            
            self.nome_entry.delete(0, "end")
            self.nome_entry.insert(0, nome)
            
            self.grupo_entry.delete(0, "end")
            self.grupo_entry.insert(0, str(grupo))
            
            self.current_editing_cpf = cpf_clean  # Define que estamos editando esta pessoa
            self.update_save_button_text()
            self.update_status(f"Pessoa encontrada: {nome}", "green")
        else:
            self.update_status("Pessoa não encontrada!", "red")

    def delete_person(self):
        """Exclui uma pessoa do banco de dados."""
        cpf = self.cpf_entry.get().strip()
        nome = self.nome_entry.get().strip()
        
        if not cpf:
            self.update_status("Digite um CPF para excluir!", "orange")
            return

        if not self.validate_cpf(cpf):
            self.update_status("CPF deve conter 11 dígitos!", "red")
            return

        # Remove formatação do CPF
        cpf_clean = self.clean_cpf(cpf)

        # Confirma a exclusão
        if not self.db.check_person_exists(cpf_clean):
            self.update_status("Pessoa não encontrada!", "red")
            return

        # Verificação simples para confirmar exclusão
        if nome:
            # Cria uma janela de confirmação
            confirm_window = ctk.CTkToplevel(self)
            confirm_window.title("Confirmar Exclusão")
            confirm_window.geometry("400x200")
            confirm_window.grab_set()
            
            # Centraliza a janela
            confirm_window.transient(self)
            
            confirm_label = ctk.CTkLabel(confirm_window, text=f"Tem certeza que deseja excluir:\n{nome} (CPF: {cpf})?", 
                                       font=ctk.CTkFont(size=14))
            confirm_label.pack(pady=30)
            
            button_frame = ctk.CTkFrame(confirm_window)
            button_frame.pack(pady=20)
            
            def confirm_delete():
                if self.db.delete_person(cpf_clean):
                    self.update_status(f"Pessoa {nome} excluída com sucesso!", "green")
                    self.clear_fields()
                    self.refresh_person_list()
                    # Atualiza a lista principal se a janela pai existir
                    if hasattr(self.master, 'update_person_list'):
                        self.master.update_person_list()
                else:
                    self.update_status("Erro ao excluir pessoa!", "red")
                confirm_window.destroy()
            
            def cancel_delete():
                confirm_window.destroy()
            
            confirm_btn = ctk.CTkButton(button_frame, text="Confirmar", fg_color="red", 
                                      hover_color="darkred", command=confirm_delete)
            confirm_btn.pack(side="left", padx=10)
            
            cancel_btn = ctk.CTkButton(button_frame, text="Cancelar", command=cancel_delete)
            cancel_btn.pack(side="left", padx=10)
            
        else:
            self.update_status("Preencha o nome para confirmar a exclusão!", "orange")

    def filter_list(self, value):
        """Filtra a lista por grupo."""
        self.refresh_person_list()

    def on_search_filter_change(self, event):
        """Chamado quando o campo de busca é alterado."""
        self.refresh_person_list()

    def refresh_person_list(self):
        """Atualiza a lista de pessoas cadastradas."""
        # Limpa a lista atual
        for widget in self.scrollable_list.winfo_children():
            widget.destroy()

        # Busca pessoas baseado no filtro
        filter_value = self.filter_selector.get()
        search_term = self.search_filter_entry.get().strip().lower()
        
        if filter_value == "Todos":
            people_g1 = self.db.get_people_by_group(1)
            people_g2 = self.db.get_people_by_group(2)
            all_people = people_g1 + people_g2
        elif filter_value == "Grupo 1":
            all_people = self.db.get_people_by_group(1)
        else:  # Grupo 2
            all_people = self.db.get_people_by_group(2)

        # Aplica filtro de busca por nome
        if search_term:
            all_people = [person for person in all_people if search_term in person[1].lower()]

        if not all_people:
            no_data_label = ctk.CTkLabel(self.scrollable_list, text="Nenhuma pessoa encontrada")
            no_data_label.pack(pady=20)
            return

        # Ordena por nome
        all_people.sort(key=lambda x: x[1])

        for person in all_people:
            cpf, nome, grupo = person
            
            # Frame para cada pessoa
            person_frame = ctk.CTkFrame(self.scrollable_list)
            person_frame.pack(fill="x", pady=2, padx=5)
            
            # Label com informações da pessoa
            info_text = f"{nome} | CPF: {cpf} | Grupo: {grupo}"
            person_label = ctk.CTkLabel(person_frame, text=info_text, anchor="w")
            person_label.pack(side="left", padx=10, pady=5, expand=True, fill="x")
            
            # Botão para carregar nos campos
            load_button = ctk.CTkButton(
                person_frame, 
                text="Carregar", 
                width=80,
                command=lambda c=cpf: self.load_person_to_form(c)
            )
            load_button.pack(side="right", padx=10, pady=5)

    def load_person_to_form(self, cpf):
        """Carrega os dados de uma pessoa nos campos do formulário."""
        person_data = self.db.get_person_details(cpf)
        
        if person_data:
            cpf_db, nome, grupo = person_data
            
            # Limpa e preenche os campos
            self.clear_fields()
            
            self.cpf_entry.insert(0, cpf_db)
            self.nome_entry.insert(0, nome)
            self.grupo_entry.insert(0, str(grupo))
            
            self.current_editing_cpf = cpf  # Define que estamos editando esta pessoa
            self.update_save_button_text()
            self.update_status(f"Dados de {nome} carregados", "blue")
            self.update_save_button_text()  # Atualiza o texto do botão salvar

# Classe para uso independente
class PersonnelManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("POBChecker - Gerenciamento de Pessoal")
        self.geometry("700x800")
        
        # Cria o gerenciador como janela separada
        self.manager_window = PersonnelManager(master=self)

if __name__ == "__main__":
    app = PersonnelManagerApp()
    app.mainloop()
