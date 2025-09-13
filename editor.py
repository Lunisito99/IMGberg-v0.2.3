# hola! Si eres un dev y estas revisando mi codigo mejoralo,espero tu comentario con tu mejora me serviria en mi emprendimiento! :D

import customtkinter as ctk
import tkinter.filedialog as tkfd
import tkinter.colorchooser as tkcolor
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont
import os
import json
import numpy as np
import math

# Esta es mi seccion de IA, no es magia, son trucos jajaja
# Son solo funciones de simulacion, se ven cool pero no son IA real
def remove_background_ai(image):
    print("Simulando eliminación de fondo con IA...")
    image_rgba = image.convert("RGBA")
    
    # Este es el truco para que se vea transparente, con cuadros
    width, height = image_rgba.size
    bg = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(bg)
    tile_size = 20
    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            color = (200, 200, 200) if (x // tile_size + y // tile_size) % 2 == 0 else (255, 255, 255)
            draw.rectangle([x, y, x + tile_size, y + tile_size], fill=color)

    blended_image = Image.alpha_composite(bg, image_rgba)
    return blended_image

# Esto hace que las fotos se vean mas nitidas, como si la IA lo hiciera
def enhance_quality_ai(image):
    print("Simulando mejora de calidad con IA...")
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.5)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2)
    return image

# Y esto para que las fotos parezcan dibujos animados, es solo un filtro
def cartoonify_ai(image):
    print("Simulando efecto de estilizado (Cartoon) con IA...")
    image = image.filter(ImageFilter.SMOOTH)
    image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
    image = image.filter(ImageFilter.SHARPEN)
    image = image.convert("P", palette=Image.ADAPTIVE, colors=64)
    image = image.convert("RGB")
    return image

# Y esta es la clase de mi editor de fotos, es lo mas complicado xd
class Editor(ctk.CTkFrame):
    def __init__(self, master, project_data, is_new):
        super().__init__(master)
        self.master = master
        self.project_data = project_data
        
        self.selected_layer_index = -1
        self.current_zoom = 1.0
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        if is_new:
            self.layers = [Image.new('RGB', (project_data['width'], project_data['height']), project_data['color'])]
            self.layer_positions = [(0, 0)]
            self.layer_metadata = [{"type": "background"}]
        else:
            self.layers = project_data.get('layers', [])
            self.layer_positions = project_data.get('layer_positions', [(0, 0) for _ in range(len(self.layers))])
            self.layer_metadata = project_data.get('layer_metadata', [{"type": "background"}])
            if not self.layers:
                self.layers = [Image.new('RGB', (project_data['width'], project_data['height']), project_data['color'])]
                self.layer_positions = [(0, 0)]
                self.layer_metadata = [{"type": "background"}]
            del self.project_data['layers']
            
        self.configure_gui()
        self.update_canvas()

    # Esto es para el layout, es un lio pero funciona
    def configure_gui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Este es mi panel izquierdo para las herramientas, propiedades y capas
        self.left_panel = ctk.CTkFrame(self)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.left_panel.grid_rowconfigure(0, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)

        # Esta es la zona del lienzo, donde se ven las fotos
        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        self.grid_columnconfigure(1, weight=3)
        
        self.canvas_label = ctk.CTkLabel(self.canvas_frame, text="")
        self.canvas_label.grid(row=0, column=0, sticky="nsew")

        # Esto es para manejar el raton y los eventos
        self.canvas_label.bind("<Button-1>", self.on_click_canvas)
        # Esto es para que no se laguee al arrastrar, solo muevo la posicion
        self.canvas_label.bind("<B1-Motion>", self.on_drag_canvas)
        # y aca actualizo la imagen cuando suelto el click
        self.canvas_label.bind("<ButtonRelease-1>", self.on_release_canvas)
        self.canvas_label.bind("<MouseWheel>", self.on_zoom)
        self.canvas_frame.bind("<Configure>", self.update_canvas)

        self.tools_panel = ctk.CTkScrollableFrame(self.left_panel)
        self.tools_panel.grid(row=0, column=0, sticky="nsew")
        
        self.properties_panel = ctk.CTkScrollableFrame(self.left_panel)
        self.properties_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.properties_panel.grid_columnconfigure(0, weight=1)

        self.layers_panel = ctk.CTkScrollableFrame(self.left_panel)
        self.layers_panel.grid(row=0, column=2, sticky="nsew")
        
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_columnconfigure(1, weight=1)
        self.left_panel.grid_columnconfigure(2, weight=1)
        
        self.create_tools_section()
        self.update_layers_panel()

    # Esta es mi seccion de herramientas y botones
    def create_tools_section(self):
        ctk.CTkLabel(self.tools_panel, text="Herramientas", font=("Arial", 16, "bold")).pack(pady=5)
        
        ctk.CTkButton(self.tools_panel, text="Guardar Proyecto", command=self.save_project).pack(pady=2)
        ctk.CTkButton(self.tools_panel, text="Volver al Menú", command=self.go_back_to_menu).pack(pady=2)
        
        ctk.CTkLabel(self.tools_panel, text="Crear Elementos", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        ctk.CTkButton(self.tools_panel, text="Añadir Imagen", command=self.add_image_layer).pack(pady=2)
        ctk.CTkButton(self.tools_panel, text="Añadir Texto", command=self.open_text_tool_window).pack(pady=2)
        ctk.CTkButton(self.tools_panel, text="Figuras...", command=self.open_shapes_window).pack(pady=2)
        
        ctk.CTkLabel(self.tools_panel, text="Edición de Capas", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        ctk.CTkButton(self.tools_panel, text="Borrar Fondo (IA)", command=self.remove_background).pack(pady=2)
        ctk.CTkButton(self.tools_panel, text="Mejorar Calidad (IA)", command=self.enhance_quality).pack(pady=2)
        ctk.CTkButton(self.tools_panel, text="Estilizar (IA)", command=self.cartoonify).pack(pady=2)
        ctk.CTkButton(self.tools_panel, text="Fusionar Capas", command=self.weld_layers).pack(pady=2)
        ctk.CTkButton(self.tools_panel, text="Curvas RGB", command=self.open_curves_window).pack(pady=2)
        ctk.CTkButton(self.tools_panel, text="Filtros...", command=self.open_filters_window).pack(pady=2)
        ctk.CTkButton(self.tools_panel, text="Ajustes de Color", command=self.open_color_adjustments_window).pack(pady=2)

    # Esto es para la ventana de texto, por si alguien quiere escribir algo
    def open_text_tool_window(self):
        text_window = ctk.CTkToplevel(self)
        text_window.title("Añadir Texto")
        text_window.geometry("300x250")
        
        ctk.CTkLabel(text_window, text="Introduce tu texto:").pack(pady=5)
        text_entry = ctk.CTkEntry(text_window, width=250)
        text_entry.pack(pady=5)
        
        ctk.CTkLabel(text_window, text="Tamaño de la fuente:").pack(pady=5)
        size_slider = ctk.CTkSlider(text_window, from_=10, to=200)
        size_slider.set(50)
        size_slider.pack(pady=5)

        def add_text_layer():
            text_content = text_entry.get()
            font_size = int(size_slider.get())
            if not text_content:
                return

            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
            
            temp_draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
            text_bbox = temp_draw.textbbox((0, 0), text_content, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            text_layer = Image.new('RGBA', (self.project_data['width'], self.project_data['height']), (0, 0, 0, 0))
            draw = ImageDraw.Draw(text_layer)
            
            pos_x = (self.project_data['width'] - text_width) // 2
            pos_y = (self.project_data['height'] - text_height) // 2
            
            draw.text((pos_x, pos_y), text_content, font=font, fill="white")
            
            self.layers.append(text_layer)
            self.layer_positions.append((0, 0))
            self.layer_metadata.append({"type": "text", "content": text_content, "font_size": font_size, "color": "white"})
            self.update_layers_panel()
            self.update_canvas()
            text_window.destroy()

        ctk.CTkButton(text_window, text="Añadir", command=add_text_layer).pack(pady=10)

    # Ventana para ajustar brillo, contraste y saturacion
    def open_color_adjustments_window(self):
        if self.selected_layer_index == -1:
            print("Selecciona una capa para ajustar los colores.")
            return

        color_window = ctk.CTkToplevel(self)
        color_window.title("Ajustes de Color")
        color_window.geometry("300x300")
        
        ctk.CTkLabel(color_window, text="Brillo:").pack(pady=(10, 0))
        brightness_slider = ctk.CTkSlider(color_window, from_=0.1, to=2.0)
        brightness_slider.set(1.0)
        brightness_slider.pack(pady=5)
        
        ctk.CTkLabel(color_window, text="Contraste:").pack(pady=(10, 0))
        contrast_slider = ctk.CTkSlider(color_window, from_=0.1, to=2.0)
        contrast_slider.set(1.0)
        contrast_slider.pack(pady=5)

        ctk.CTkLabel(color_window, text="Saturación:").pack(pady=(10, 0))
        saturation_slider = ctk.CTkSlider(color_window, from_=0.1, to=2.0)
        saturation_slider.set(1.0)
        saturation_slider.pack(pady=5)
        
        original_layer = self.layers[self.selected_layer_index].copy()

        def apply_adjustments(event=None):
            brightness = brightness_slider.get()
            contrast = contrast_slider.get()
            saturation = saturation_slider.get()
            
            temp_layer = original_layer.copy()
            
            enhancer = ImageEnhance.Brightness(temp_layer)
            temp_layer = enhancer.enhance(brightness)
            
            enhancer = ImageEnhance.Contrast(temp_layer)
            temp_layer = enhancer.enhance(contrast)
            
            enhancer = ImageEnhance.Color(temp_layer)
            temp_layer = enhancer.enhance(saturation)
            
            self.layers[self.selected_layer_index] = temp_layer
            self.update_canvas()

        brightness_slider.bind("<ButtonRelease-1>", apply_adjustments)
        contrast_slider.bind("<ButtonRelease-1>", apply_adjustments)
        saturation_slider.bind("<ButtonRelease-1>", apply_adjustments)

    # Ventana para crear figuras geometricas
    def open_shapes_window(self):
        shapes_window = ctk.CTkToplevel(self)
        shapes_window.title("Crear Figuras")
        shapes_window.geometry("200x250")
        ctk.CTkLabel(shapes_window, text="Elige una figura:", font=("Arial", 14, "bold")).pack(pady=10)
        ctk.CTkButton(shapes_window, text="Círculo", command=lambda: self.create_shape("circle", shapes_window)).pack(pady=5)
        ctk.CTkButton(shapes_window, text="Cuadrado", command=lambda: self.create_shape("square", shapes_window)).pack(pady=5)
        ctk.CTkButton(shapes_window, text="Triángulo", command=lambda: self.create_shape("triangle", shapes_window)).pack(pady=5)

    # Ventana para aplicar filtros
    def open_filters_window(self):
        filters_window = ctk.CTkToplevel(self)
        filters_window.title("Filtros")
        filters_window.geometry("200x250")
        ctk.CTkLabel(filters_window, text="Elige un filtro:", font=("Arial", 14, "bold")).pack(pady=10)
        ctk.CTkButton(filters_window, text="Desenfocar", command=lambda: self.apply_filter(ImageFilter.BLUR, filters_window)).pack(pady=5)
        ctk.CTkButton(filters_window, text="Aumentar Nitidez", command=lambda: self.apply_filter(ImageFilter.SHARPEN, filters_window)).pack(pady=5)
        ctk.CTkButton(filters_window, text="Contorno", command=lambda: self.apply_filter(ImageFilter.CONTOUR, filters_window)).pack(pady=5)
        ctk.CTkButton(filters_window, text="Relieve", command=lambda: self.apply_filter(ImageFilter.EMBOSS, filters_window)).pack(pady=5)

    # Esto aplica el filtro a la capa seleccionada
    def apply_filter(self, filter_type, window):
        if self.selected_layer_index != -1:
            try:
                self.layers[self.selected_layer_index] = self.layers[self.selected_layer_index].filter(filter_type)
                self.update_canvas()
                window.destroy()
            except Exception as e:
                print(f"Error al aplicar el filtro: {e}")
        else:
            print("Selecciona una capa para aplicar el filtro.")

    # Esto actualiza el panel de capas, un poco desorganizado pero se entiende
    def update_layers_panel(self):
        for widget in self.layers_panel.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.layers_panel, text="Capas", font=("Arial", 16, "bold")).pack(pady=(10, 5))
        for i, layer in reversed(list(enumerate(self.layers))):
            layer_frame = ctk.CTkFrame(self.layers_panel)
            layer_frame.pack(fill="x", pady=2)
            
            is_selected = i == self.selected_layer_index
            select_button = ctk.CTkButton(
                layer_frame, 
                text=f"Capa {len(self.layers) - 1 - i}",
                command=lambda index=i: self.select_layer(index)
            )
            if is_selected:
                select_button.configure(fg_color="#3a78b5")
            select_button.pack(side="left", fill="x", expand=True)
            
        if self.selected_layer_index != -1 and self.layer_metadata[self.selected_layer_index].get("type") in ["circle", "square", "triangle", "text"]:
            self.show_properties_panel()
        else:
            self.hide_properties_panel()

    # Selecciona una capa para editarla
    def select_layer(self, index):
        if self.selected_layer_index == index:
            self.selected_layer_index = -1
        else:
            self.selected_layer_index = index
        self.update_layers_panel()

    # Muestro las propiedades de la capa seleccionada
    def show_properties_panel(self):
        for widget in self.properties_panel.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.properties_panel, text="Propiedades", font=("Arial", 16, "bold")).pack(pady=5)

        metadata = self.layer_metadata[self.selected_layer_index]
        
        ctk.CTkLabel(self.properties_panel, text="Color:").pack(padx=10, pady=(10, 0))
        color_button = ctk.CTkButton(self.properties_panel, text="Cambiar Color", command=lambda: self.change_shape_property('color'))
        color_button.pack(padx=10, pady=5)

        if metadata.get("type") in ["circle", "square", "triangle"]:
            ctk.CTkLabel(self.properties_panel, text="Tamaño:").pack(padx=10, pady=(10, 0))
            size_slider = ctk.CTkSlider(self.properties_panel, from_=10, to=400, command=lambda val: self.change_shape_property('size', val))
            size_slider.set(metadata.get('size', 200))
            size_slider.pack(padx=10, pady=5)
            
            ctk.CTkLabel(self.properties_panel, text="Rotación (grados):").pack(padx=10, pady=(10, 0))
            rotation_slider = ctk.CTkSlider(self.properties_panel, from_=0, to=360, command=lambda val: self.change_shape_property('rotation', val))
            rotation_slider.set(metadata.get('rotation', 0))
            rotation_slider.pack(padx=10, pady=5)
        
        ctk.CTkLabel(self.properties_panel, text="Posición X:").pack(padx=10, pady=(10, 0))
        pos_x_entry = ctk.CTkEntry(self.properties_panel)
        pos_x_entry.insert(0, str(self.layer_positions[self.selected_layer_index][0]))
        pos_x_entry.bind("<Return>", lambda event: self.change_shape_property('pos_x', pos_x_entry.get()))
        pos_x_entry.pack(padx=10, pady=5)

        ctk.CTkLabel(self.properties_panel, text="Posición Y:").pack(padx=10, pady=(10, 0))
        pos_y_entry = ctk.CTkEntry(self.properties_panel)
        pos_y_entry.insert(0, str(self.layer_positions[self.selected_layer_index][1]))
        pos_y_entry.bind("<Return>", lambda event: self.change_shape_property('pos_y', pos_y_entry.get()))
        pos_y_entry.pack(padx=10, pady=5)
        
    # Esto esconde el panel de propiedades
    def hide_properties_panel(self):
        for widget in self.properties_panel.winfo_children():
            widget.destroy()

    # Esto cambia las propiedades de la capa seleccionada
    def change_shape_property(self, prop_type, value=None):
        if self.selected_layer_index != -1:
            metadata = self.layer_metadata[self.selected_layer_index]
            current_pos_x, current_pos_y = self.layer_positions[self.selected_layer_index]

            if prop_type == 'color':
                color_code = tkcolor.askcolor(title="Elegir Color de Figura")
                if color_code:
                    metadata['color'] = color_code[1]
            elif prop_type == 'size':
                metadata['size'] = value
            elif prop_type == 'rotation':
                metadata['rotation'] = value
            elif prop_type == 'pos_x':
                try:
                    self.layer_positions[self.selected_layer_index] = (int(value), current_pos_y)
                except ValueError:
                    pass
            elif prop_type == 'pos_y':
                try:
                    self.layer_positions[self.selected_layer_index] = (current_pos_x, int(value))
                except ValueError:
                    pass

            self.redraw_shape(self.selected_layer_index)

    # Redibuja la figura con las nuevas propiedades
    def redraw_shape(self, index):
        metadata = self.layer_metadata[index]
        shape_type = metadata["type"]
        color = metadata.get("color", "black")
        size = metadata.get("size", 200)
        rotation = metadata.get("rotation", 0)

        temp_layer = Image.new('RGBA', (self.project_data['width'], self.project_data['height']), (0, 0, 0, 0))
        draw = ImageDraw.Draw(temp_layer)
        
        if shape_type == "text":
            text_content = metadata.get("content", "Texto")
            font_size = metadata.get("font_size", 50)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
            
            draw.text((0, 0), text_content, font=font, fill=color)

        elif shape_type in ["circle", "square", "triangle"]:
            bbox = [100, 100, 100 + size, 100 + size]
            if shape_type == "circle":
                draw.ellipse(bbox, fill=color)
            elif shape_type == "square":
                draw.rectangle(bbox, fill=color)
            elif shape_type == "triangle":
                draw.polygon([(100, 100 + size), (100 + size, 100 + size), (100 + size/2, 100)], fill=color)
        
        if rotation != 0:
            temp_layer = temp_layer.rotate(rotation, expand=True)

        self.layers[index] = temp_layer
        self.update_canvas()

    # Muestra los ajustes de curvas RGB
    def open_curves_window(self):
        if self.selected_layer_index == -1:
            print("Selecciona una capa para ajustar las curvas.")
            return

        curves_window = ctk.CTkToplevel(self)
        curves_window.title("Curvas RGB")
        curves_window.geometry("350x400")
        
        ctk.CTkLabel(curves_window, text="Ajustes de Curvas RGB", font=("Arial", 16, "bold")).pack(pady=10)
        
        ctk.CTkLabel(curves_window, text="Gamma General").pack()
        gamma_slider = ctk.CTkSlider(curves_window, from_=0.1, to=2.0)
        gamma_slider.set(1.0)
        gamma_slider.pack(pady=5)
        gamma_slider.bind("<ButtonRelease-1>", lambda event: self.apply_curves(gamma_slider.get()))

        ctk.CTkLabel(curves_window, text="Gamma Rojo").pack()
        red_slider = ctk.CTkSlider(curves_window, from_=0.1, to=2.0)
        red_slider.set(1.0)
        red_slider.pack(pady=5)
        red_slider.bind("<ButtonRelease-1>", lambda event: self.apply_rgb_curves(red_slider.get(), 'red'))

        ctk.CTkLabel(curves_window, text="Gamma Verde").pack()
        green_slider = ctk.CTkSlider(curves_window, from_=0.1, to=2.0)
        green_slider.set(1.0)
        green_slider.pack(pady=5)
        green_slider.bind("<ButtonRelease-1>", lambda event: self.apply_rgb_curves(green_slider.get(), 'green'))

        ctk.CTkLabel(curves_window, text="Gamma Azul").pack()
        blue_slider = ctk.CTkSlider(curves_window, from_=0.1, to=2.0)
        blue_slider.set(1.0)
        blue_slider.pack(pady=5)
        blue_slider.bind("<ButtonRelease-1>", lambda event: self.apply_rgb_curves(blue_slider.get(), 'blue'))

    def apply_curves(self, gamma):
        if self.selected_layer_index != -1:
            current_layer = self.layers[self.selected_layer_index]
            gamma_map = [int(255 * (i / 255) ** gamma) for i in range(256)]
            if current_layer.mode == 'RGBA':
                r, g, b, a = current_layer.split()
                r = r.point(gamma_map)
                g = g.point(gamma_map)
                b = b.point(gamma_map)
                processed_layer = Image.merge('RGBA', (r, g, b, a))
            else:
                processed_layer = current_layer.point(gamma_map * 3)
            self.layers[self.selected_layer_index] = processed_layer
            self.update_canvas()

    def apply_rgb_curves(self, gamma, channel):
        if self.selected_layer_index != -1:
            current_layer = self.layers[self.selected_layer_index]
            if current_layer.mode != 'RGB':
                current_layer = current_layer.convert('RGB')
                
            r, g, b = current_layer.split()
            gamma_map = [int(255 * (i / 255) ** gamma) for i in range(256)]
            
            if channel == 'red':
                r = r.point(gamma_map)
            elif channel == 'green':
                g = g.point(gamma_map)
            elif channel == 'blue':
                b = b.point(gamma_map)
            
            processed_layer = Image.merge('RGB', (r, g, b))
            self.layers[self.selected_layer_index] = processed_layer
            self.update_canvas()

    def combine_layers(self):
        combined = Image.new('RGB', (self.project_data['width'], self.project_data['height']), "black")
        for i, layer in enumerate(self.layers):
            if layer.mode == 'RGBA':
                pos_x, pos_y = self.layer_positions[i]
                combined.paste(layer, (pos_x, pos_y), layer)
            else:
                combined.paste(layer, (0, 0))
        return combined

    # Actualiza el lienzo para mostrar la imagen combinada
    def update_canvas(self, event=None):
        if not self.winfo_exists() or self.winfo_width() <= 0 or self.winfo_height() <= 0:
            return
            
        self.combined_image = self.combine_layers()
        canvas_width = self.canvas_frame.winfo_width()
        canvas_height = self.canvas_frame.winfo_height()
        
        if canvas_width <= 0 or canvas_height <= 0:
            return
        
        img_width, img_height = self.combined_image.size
        
        scale = min(canvas_width / img_width, canvas_height / img_height) * self.current_zoom
        scaled_width = int(img_width * scale)
        scaled_height = int(img_height * scale)

        resized_image = self.combined_image.resize((scaled_width, scaled_height), Image.LANCZOS)
        
        self.tk_image = ImageTk.PhotoImage(resized_image)
        self.canvas_label.configure(image=self.tk_image)
        self.canvas_label.image = self.tk_image

    # Esto selecciona la capa al hacer click en el lienzo
    def on_click_canvas(self, event):
        self.drag_start_x, self.drag_start_y = event.x, event.y
        self.selected_layer_index = -1
        
        for i in range(len(self.layers) - 1, -1, -1):
            layer = self.layers[i]
            pos_x, pos_y = self.layer_positions[i]
            
            canvas_to_img_x = int(event.x / self.current_zoom)
            canvas_to_img_y = int(event.y / self.current_zoom)

            if pos_x <= canvas_to_img_x < pos_x + layer.width and pos_y <= canvas_to_img_y < pos_y + layer.height:
                pixel = layer.getpixel((canvas_to_img_x - pos_x, canvas_to_img_y - pos_y))
                if layer.mode == 'RGBA' and pixel[3] > 0:
                    self.selected_layer_index = i
                    self.drag_offset_x = canvas_to_img_x - pos_x
                    self.drag_offset_y = canvas_to_img_y - pos_y
                    break
        self.update_layers_panel()

    # Esto mueve la capa, el lag se quito porque no actualizo la imagen hasta que sueltas el click
    def on_drag_canvas(self, event):
        if self.selected_layer_index == -1:
            return
        
        canvas_to_img_x = int(event.x / self.current_zoom)
        canvas_to_img_y = int(event.y / self.current_zoom)

        new_x = canvas_to_img_x - self.drag_offset_x
        new_y = canvas_to_img_y - self.drag_offset_y
        
        self.layer_positions[self.selected_layer_index] = (new_x, new_y)

    # Esto actualiza el lienzo al soltar el click, para que se vea el cambio
    def on_release_canvas(self, event):
        self.update_canvas()

    # Y esto es para el zoom con la rueda del raton
    def on_zoom(self, event):
        if event.delta > 0:
            self.current_zoom *= 1.1
        else:
            self.current_zoom /= 1.1
        self.update_canvas()
        
    def create_shape(self, shape_type, window):
        new_layer = Image.new('RGBA', (self.project_data['width'], self.project_data['height']), (0, 0, 0, 0))
        draw = ImageDraw.Draw(new_layer)
        size = 200
        x, y = 100, 100
        
        if shape_type == "circle":
            draw.ellipse([x, y, x + size, y + size], fill="blue")
            color = "blue"
        elif shape_type == "square":
            draw.rectangle([x, y, x + size, y + size], fill="red")
            color = "red"
        elif shape_type == "triangle":
            draw.polygon([(x, y + size), (x + size, y + size), (x + size/2, y)], fill="green")
            color = "green"
        
        self.layers.append(new_layer)
        self.layer_positions.append((0, 0))
        self.layer_metadata.append({"type": shape_type, "color": color, "size": size, "rotation": 0})
        self.update_layers_panel()
        self.update_canvas()
        window.destroy()

    # Añade una nueva capa de imagen
    def add_image_layer(self):
        file_path = tkfd.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif")])
        if file_path:
            try:
                new_layer = Image.open(file_path).convert("RGBA")
                new_layer.thumbnail((self.project_data['width'], self.project_data['height']), Image.LANCZOS)
                self.layers.append(new_layer)
                self.layer_positions.append((0, 0))
                self.layer_metadata.append({"type": "image"})
                self.update_layers_panel()
                self.update_canvas()
            except Exception as e:
                print(f"Error al cargar la imagen: {e}")
    
    # Llama a mi funcion de IA para quitar el fondo
    def remove_background(self):
        if self.selected_layer_index == -1:
            print("Selecciona una capa para quitar el fondo.")
            return
        original_image = self.layers[self.selected_layer_index]
        processed_image = remove_background_ai(original_image)
        self.layers[self.selected_layer_index] = processed_image
        self.update_canvas()

    # Llama a mi funcion de IA para mejorar la calidad
    def enhance_quality(self):
        if self.selected_layer_index == -1:
            print("Selecciona una capa para mejorar la calidad.")
            return
        original_image = self.layers[self.selected_layer_index]
        processed_image = enhance_quality_ai(original_image)
        self.layers[self.selected_layer_index] = processed_image
        self.update_canvas()

    # Llama a mi funcion de IA para estilizar la foto
    def cartoonify(self):
        if self.selected_layer_index == -1:
            print("Selecciona una capa para estilizar.")
            return
        original_image = self.layers[self.selected_layer_index]
        processed_image = cartoonify_ai(original_image)
        self.layers[self.selected_layer_index] = processed_image
        self.update_canvas()

    # Fusiona todas las capas en una sola
    def weld_layers(self):
        if self.selected_layer_index == -1:
            print("Selecciona al menos dos capas para fusionar.")
            return
        
        if len(self.layers) > 1:
            merged_layer = self.combine_layers()
            self.layers = [merged_layer]
            self.layer_positions = [(0, 0)]
            self.layer_metadata = [{"type": "merged"}]
            self.selected_layer_index = 0
            self.update_layers_panel()
            self.update_canvas()
    
    # Esto guarda todo mi proyecto para poder volver luego
    def save_project(self):
        project_name = self.project_data['name'].replace(" ", "_")
        folder_path = os.path.join("imgberg", project_name)
        
        os.makedirs(folder_path, exist_ok=True)
        
        final_image = self.combine_layers()
        final_image.save(os.path.join(folder_path, f"{project_name}.png"))
        
        project_info = {
            "name": self.project_data['name'],
            "width": self.project_data['width'],
            "height": self.project_data['height'],
            "color": self.project_data['color'],
            "layer_positions": self.layer_positions,
            "layer_metadata": self.layer_metadata
        }
        
        with open(os.path.join(folder_path, f"{project_name}.imgb"), 'w') as f:
            json.dump(project_info, f, indent=4)
        
        for i, layer in enumerate(self.layers):
            layer_path = os.path.join(folder_path, f"layer_{i}.png")
            layer.save(layer_path, "PNG")
        
        print(f"Proyecto guardado en: {folder_path}")

    # Este boton me regresa al menu principal
    def go_back_to_menu(self):
        self.destroy()
        self.master.show_main_menu()