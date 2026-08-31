import tkinter as tk
from tkinter import ttk

import customtkinter as ctk
from PIL import Image, ImageTk


class PDFViewer(ctk.CTkFrame):

    ZOOM_MINIMO = 0.50
    ZOOM_MAXIMO = 3.00
    PASSO_ZOOM = 0.25
    MARGEM = 16

    def __init__(self, master):

        super().__init__(
            master
        )

        # Guarda a imagem original da página do PDF.
        self.imagem_original = None

        # Referência da imagem exibida no Canvas.
        self.image = None

        # ID da imagem criada dentro do Canvas.
        self.canvas_image_id = None

        # 1.0 representa o tamanho "Ajustar à área".
        self.zoom = 1.0

        # Evita várias renderizações seguidas durante
        # o redimensionamento da janela/divisor.
        self._redimensionamento_pendente = None

        self.grid_rowconfigure(
            1,
            weight=1
        )

        self.grid_columnconfigure(
            0,
            weight=1
        )

        # ======================================================
        # CONTROLES DE ZOOM
        # ======================================================

        controles = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        controles.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=8,
            pady=(6, 2)
        )

        controles.grid_columnconfigure(
            0,
            weight=1
        )

        controles_zoom = ctk.CTkFrame(
            controles,
            fg_color="transparent"
        )

        controles_zoom.pack(
            anchor="center"
        )

        self.zoom_menos_button = ctk.CTkButton(
            controles_zoom,
            text="−",
            width=38,
            command=self.diminuir_zoom
        )

        self.zoom_menos_button.pack(
            side="left",
            padx=3
        )

        self.ajustar_button = ctk.CTkButton(
            controles_zoom,
            text="Ajustar",
            width=80,
            command=self.ajustar
        )

        self.ajustar_button.pack(
            side="left",
            padx=3
        )

        self.zoom_label = ctk.CTkLabel(
            controles_zoom,
            text="Ajustado",
            width=70
        )

        self.zoom_label.pack(
            side="left",
            padx=3
        )

        self.zoom_mais_button = ctk.CTkButton(
            controles_zoom,
            text="+",
            width=38,
            command=self.aumentar_zoom
        )

        self.zoom_mais_button.pack(
            side="left",
            padx=3
        )

        # ======================================================
        # ÁREA DE VISUALIZAÇÃO
        # ======================================================

        area = ctk.CTkFrame(
            self
        )

        area.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=6,
            pady=(2, 6)
        )

        area.grid_rowconfigure(
            0,
            weight=1
        )

        area.grid_columnconfigure(
            0,
            weight=1
        )

        self.canvas = tk.Canvas(
            area,
            highlightthickness=0,
            borderwidth=0,
            background="#d9d9d9"
        )

        self.canvas.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.scroll_vertical = ttk.Scrollbar(
            area,
            orient="vertical",
            command=self.canvas.yview
        )

        self.scroll_vertical.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.scroll_horizontal = ttk.Scrollbar(
            area,
            orient="horizontal",
            command=self.canvas.xview
        )

        self.scroll_horizontal.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        self.canvas.configure(
            yscrollcommand=self.scroll_vertical.set,
            xscrollcommand=self.scroll_horizontal.set
        )

        self.mensagem_canvas = self.canvas.create_text(
            0,
            0,
            text="Nenhum PDF carregado",
            anchor="center"
        )

        # Quando a área disponível muda, recalculamos
        # o tamanho da página para evitar cortes.
        self.canvas.bind(
            "<Configure>",
            self.redimensionar
        )

    # ======================================================
    # RECEBER NOVA PÁGINA DO PDF
    # ======================================================

    def mostrar(self, imagem):

        self.imagem_original = imagem.copy()

        # Cada nova página começa ajustada integralmente
        # à área disponível.
        self.zoom = 1.0

        self.canvas.xview_moveto(
            0
        )

        self.canvas.yview_moveto(
            0
        )

        self.atualizar_imagem()

    # ======================================================
    # CALCULAR ESCALA DE AJUSTE
    # ======================================================

    def _calcular_escala_ajuste(self):

        if self.imagem_original is None:
            return 1.0

        largura_area = max(
            self.canvas.winfo_width() - (self.MARGEM * 2),
            1
        )

        altura_area = max(
            self.canvas.winfo_height() - (self.MARGEM * 2),
            1
        )

        largura_imagem, altura_imagem = (
            self.imagem_original.size
        )

        if largura_imagem <= 0 or altura_imagem <= 0:
            return 1.0

        escala_largura = (
            largura_area / largura_imagem
        )

        escala_altura = (
            altura_area / altura_imagem
        )

        # Sempre usamos o menor fator para que
        # largura E altura caibam integralmente.
        return min(
            escala_largura,
            escala_altura
        )

    # ======================================================
    # ATUALIZAR IMAGEM EXIBIDA
    # ======================================================

    def atualizar_imagem(self):

        if self.imagem_original is None:

            largura = max(
                self.canvas.winfo_width(),
                1
            )

            altura = max(
                self.canvas.winfo_height(),
                1
            )

            self.canvas.coords(
                self.mensagem_canvas,
                largura / 2,
                altura / 2
            )

            return

        escala_ajuste = (
            self._calcular_escala_ajuste()
        )

        escala_final = (
            escala_ajuste * self.zoom
        )

        largura_original, altura_original = (
            self.imagem_original.size
        )

        largura_nova = max(
            int(largura_original * escala_final),
            1
        )

        altura_nova = max(
            int(altura_original * escala_final),
            1
        )

        imagem = self.imagem_original.resize(
            (
                largura_nova,
                altura_nova
            ),
            Image.Resampling.LANCZOS
        )

        # ImageTk.PhotoImage evita uma segunda escala
        # adicional do CustomTkinter sobre a imagem.
        self.image = ImageTk.PhotoImage(
            imagem
        )

        self.canvas.itemconfigure(
            self.mensagem_canvas,
            state="hidden"
        )

        if self.canvas_image_id is None:

            self.canvas_image_id = (
                self.canvas.create_image(
                    0,
                    0,
                    image=self.image,
                    anchor="nw"
                )
            )

        else:

            self.canvas.itemconfigure(
                self.canvas_image_id,
                image=self.image
            )

        largura_canvas = max(
            self.canvas.winfo_width(),
            1
        )

        altura_canvas = max(
            self.canvas.winfo_height(),
            1
        )

        # Quando a página é menor que o Canvas,
        # ela fica centralizada. Quando é maior,
        # começa na margem e pode ser percorrida
        # pelas barras de rolagem.
        if largura_nova < largura_canvas:

            x = (
                largura_canvas - largura_nova
            ) / 2

        else:

            x = self.MARGEM

        if altura_nova < altura_canvas:

            y = (
                altura_canvas - altura_nova
            ) / 2

        else:

            y = self.MARGEM

        self.canvas.coords(
            self.canvas_image_id,
            x,
            y
        )

        largura_scroll = max(
            largura_canvas,
            x + largura_nova + self.MARGEM
        )

        altura_scroll = max(
            altura_canvas,
            y + altura_nova + self.MARGEM
        )

        self.canvas.configure(
            scrollregion=(
                0,
                0,
                largura_scroll,
                altura_scroll
            )
        )

        self._atualizar_texto_zoom()

    # ======================================================
    # ZOOM
    # ======================================================

    def aumentar_zoom(self):

        novo_zoom = min(
            self.zoom + self.PASSO_ZOOM,
            self.ZOOM_MAXIMO
        )

        if novo_zoom == self.zoom:
            return

        self.zoom = novo_zoom

        self.atualizar_imagem()

    def diminuir_zoom(self):

        novo_zoom = max(
            self.zoom - self.PASSO_ZOOM,
            self.ZOOM_MINIMO
        )

        if novo_zoom == self.zoom:
            return

        self.zoom = novo_zoom

        self.atualizar_imagem()

    def ajustar(self):

        self.zoom = 1.0

        self.canvas.xview_moveto(
            0
        )

        self.canvas.yview_moveto(
            0
        )

        self.atualizar_imagem()

    def _atualizar_texto_zoom(self):

        if abs(self.zoom - 1.0) < 0.001:

            texto = "Ajustado"

        else:

            texto = (
                f"{int(round(self.zoom * 100))}%"
            )

        self.zoom_label.configure(
            text=texto
        )

    # ======================================================
    # EVENTO DE REDIMENSIONAMENTO
    # ======================================================

    def redimensionar(self, evento=None):

        if self._redimensionamento_pendente is not None:

            try:

                self.after_cancel(
                    self._redimensionamento_pendente
                )

            except Exception:

                pass

        self._redimensionamento_pendente = (
            self.after(
                80,
                self._aplicar_redimensionamento
            )
        )

    def _aplicar_redimensionamento(self):

        self._redimensionamento_pendente = None

        self.atualizar_imagem()
