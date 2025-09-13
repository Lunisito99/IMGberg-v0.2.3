# hola! Si eres un dev y estas revisando mi codigo mejoralo,espero tu comentario con tu mejora me serviria en mi emprendimiento! :D

import customtkinter as ctk
import tkinter.filedialog as tkfd
import tkinter.colorchooser as tkcolor
import os
import json
from editor import Editor
from PIL import Image, ImageTk
import tkinter as tk

# Esto es para la ventana principal de la app, es donde todo empieza.
# si es un lio es porque no se organizarme xd
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IMGberg")
        self.geometry("1200x800")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Le puse un icono para que se vea mas pro, si no esta, no pasa nada
        if os.path.exists("icon.png"):
            self.iconphoto(False, tk.PhotoImage(file="icon.png"))
            
        self.show_main_menu()

    # Aqui va el menu principal, es lo primero que se ve
    # con los botones de nuevo proyecto y los que ya existen
    def show_main_menu(self):
        self.clear_frame()
        
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(main_frame, text="IMGberg", font=("Arial", 60, "bold")).pack(pady=(50, 20))
        
        # Puse este mensaje para que en el cel se vea mejor
        ctk.CTkLabel(main_frame, text="Para una mejor experiencia, por favor usa la aplicación en modo horizontal.", font=("Arial", 14)).pack(pady=10)
        
        projects_frame = ctk.CTkFrame(main_frame)
        projects_frame.pack(pady=20, fill="x", padx=100)
        
        new_project_button = ctk.CTkButton(
            projects_frame, 
            text="+ Nuevo Proyecto", 
            command=self.open_new_project_dialog,
            width=200, 
            height=200,
            font=("Arial", 24)
        )
        new_project_button.pack(side="left", padx=10)
        
        self.load_and_display_projects(projects_frame)

    # Cargo los proyectos que ya se crearon para mostrarlos en el menu
    def load_and_display_projects(self, parent_frame):
        if not os.path.exists("imgberg"):
            return
        
        for project_name in os.listdir("imgberg"):
            project_path = os.path.join("imgberg", project_name, f"{project_name}.imgb")
            if os.path.exists(project_path):
                ctk.CTkButton(
                    parent_frame,
                    text=project_name,
                    command=lambda name=project_name: self.open_project(name),
                    width=200,
                    height=200,
                    font=("Arial", 18)
                ).pack(side="left", padx=10)

    # Esto es para el pop-up de nuevo proyecto
    # Si no carga es porque soy malo con los hilos
    def open_new_project_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Crear Nuevo Proyecto")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()
        
        self.project_data_to_show = None
        
        ctk.CTkLabel(dialog, text="Nombre:").grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        name_entry = ctk.CTkEntry(dialog, placeholder_text="Mi Proyecto")
        name_entry.grid(row=0, column=1, padx=20, pady=(20, 5), sticky="ew")
        
        ctk.CTkLabel(dialog, text="Ancho (px):").grid(row=1, column=0, padx=20, pady=5, sticky="w")
        width_entry = ctk.CTkEntry(dialog, placeholder_text="1920")
        width_entry.grid(row=1, column=1, padx=20, pady=5, sticky="ew")
        
        ctk.CTkLabel(dialog, text="Alto (px):").grid(row=2, column=0, padx=20, pady=5, sticky="w")
        height_entry = ctk.CTkEntry(dialog, placeholder_text="1080")
        height_entry.grid(row=2, column=1, padx=20, pady=5, sticky="ew")
        
        dialog.selected_color = "#FFFFFF" 
        def choose_color():
            color_code = tkcolor.askcolor(title="Elegir Color de Fondo")
            if color_code:
                dialog.selected_color = color_code[1]
                color_button.configure(text=dialog.selected_color)

        ctk.CTkLabel(dialog, text="Color de Fondo:").grid(row=3, column=0, padx=20, pady=5, sticky="w")
        color_button = ctk.CTkButton(dialog, text="Elegir Color", command=choose_color)
        color_button.grid(row=3, column=1, padx=20, pady=5, sticky="ew")

        def create_project_and_close_dialog():
            try:
                self.project_data_to_show = {
                    "name": name_entry.get() or "Proyecto sin nombre",
                    "width": int(width_entry.get() or "1920"),
                    "height": int(height_entry.get() or "1080"),
                    "color": dialog.selected_color
                }
                dialog.destroy()
            except ValueError:
                print("Por favor, introduce valores numéricos válidos.")
                
        ctk.CTkButton(dialog, text="Crear", command=create_project_and_close_dialog).grid(row=4, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        
        dialog.update_idletasks()
        
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        
        self.wait_window(dialog)
        
        if self.project_data_to_show:
            self.show_editor(self.project_data_to_show, is_new=True)

    # Esto es para cuando abres un proyecto que ya existe
    def open_project(self, project_name):
        project_dir = os.path.join("imgberg", project_name)
        imgb_path = os.path.join(project_dir, f"{project_name}.imgb")
        if os.path.exists(imgb_path):
            with open(imgb_path, 'r') as f:
                project_data = json.load(f)
            layers = []
            layer_files = sorted([f for f in os.listdir(project_dir) if f.startswith("layer_") and f.endswith(".png")])
            for filename in layer_files:
                try:
                    layers.append(Image.open(os.path.join(project_dir, filename)).convert("RGBA"))
                except Exception as e:
                    print(f"Error al cargar la capa {filename}: {e}")
            project_data['layers'] = layers
            self.show_editor(project_data, is_new=False)
        else:
            print("Archivo `.imgb` no encontrado o faltan capas.")

    # Muestro el editor de fotos
    def show_editor(self, project_data, is_new):
        self.clear_frame()
        self.editor = Editor(self, project_data, is_new)
        self.editor.pack(fill="both", expand=True)

    # Esto borra todo lo que hay en la ventana, para que no se superpongan
    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

# Aca se inicia mi app :)
if __name__ == "__main__":
    mi_app = App()
    mi_app.mainloop()