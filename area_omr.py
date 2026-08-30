import os
import json
import tkinter as tk
from tkinter import messagebox

import cv2
import fitz
import numpy as np
from PIL import Image, ImageTk, ImageDraw

from engine.geometria import normalizar_com_diagnostico


# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

DIRETORIO_FICHAS = "fichas"

ARQUIVO_FICHA_ATIVA = os.path.join(
    DIRETORIO_FICHAS,
    "ativa.json"
)

DPI = 600

MARGEM_OMR = 7

LARGURA_MAPA = 1191
ALTURA_MAPA = 1684


# ==========================================================
# OBTTER FICHA ATIVA
# ==========================================================

def obter_ficha_ativa():

    if not os.path.isfile(
        ARQUIVO_FICHA_ATIVA
    ):
        raise FileNotFoundError(
            (
                "Arquivo da ficha ativa não encontrado:\n\n"
                f"{ARQUIVO_FICHA_ATIVA}"
            )
        )

    with open(
        ARQUIVO_FICHA_ATIVA,
        "r",
        encoding="utf-8"
    ) as arquivo:

        ativa = json.load(
            arquivo
        )

    ficha_id = ativa.get(
        "ficha_id"
    )

    if not ficha_id:

        raise ValueError(
            "O ativa.json não possui um ficha_id válido."
        )

    pasta_ficha = os.path.join(
        DIRETORIO_FICHAS,
        ficha_id
    )

    caminho_pdf = os.path.join(
        pasta_ficha,
        "ficha.pdf"
    )

    caminho_mapa = os.path.join(
        pasta_ficha,
        "mapa_omr.json"
    )

    if not os.path.isfile(
        caminho_pdf
    ):
        raise FileNotFoundError(
            (
                "PDF da ficha ativa não encontrado:\n\n"
                f"{caminho_pdf}"
            )
        )

    if not os.path.isfile(
        caminho_mapa
    ):
        raise FileNotFoundError(
            (
                "Mapa OMR da ficha ativa não encontrado:\n\n"
                f"{caminho_mapa}"
            )
        )

    return (
        ficha_id,
        os.path.abspath(caminho_pdf),
        os.path.abspath(caminho_mapa)
    )


# ==========================================================
# RENDERIZAR PÁGINA
# ==========================================================

def renderizar_pagina(
    pagina,
    dpi=DPI
):

    escala = dpi / 72.0

    matriz = fitz.Matrix(
        escala,
        escala
    )

    pix = pagina.get_pixmap(
        matrix=matriz,
        alpha=False
    )

    imagem = np.frombuffer(
        pix.samples,
        dtype=np.uint8
    )

    imagem = imagem.reshape(
        pix.height,
        pix.width,
        pix.n
    )

    if pix.n == 3:

        imagem = cv2.cvtColor(
            imagem,
            cv2.COLOR_RGB2BGR
        )

    elif pix.n == 4:

        imagem = cv2.cvtColor(
            imagem,
            cv2.COLOR_RGBA2BGR
        )

    else:

        raise ValueError(
            (
                "Formato de imagem não suportado: "
                f"{pix.n} canais."
            )
        )

    return imagem


# ==========================================================
# OBTER COORDENADAS DA PÁGINA
# ==========================================================

def obter_coordenadas_pagina(
    mapa,
    numero_pagina
):

    coordenadas = mapa.get(
        "coordenadas",
        []
    )

    resultado = []

    for coordenada in coordenadas:

        pagina = coordenada.get(
            "pagina",
            1
        )

        try:
            pagina = int(
                pagina
            )
        except (
            TypeError,
            ValueError
        ):
            pagina = 1

        if pagina == numero_pagina:

            resultado.append(
                coordenada
            )

    return resultado


# ==========================================================
# DESENHAR ÁREA DE LEITURA
# ==========================================================

def desenhar_area_omr(
    imagem_normalizada,
    mapa,
    numero_pagina
):

    if imagem_normalizada is None:

        raise ValueError(
            "Imagem normalizada inválida."
        )

    imagem = imagem_normalizada.copy()

    coordenadas = obter_coordenadas_pagina(
        mapa,
        numero_pagina
    )

    if not coordenadas:
        return imagem

    largura_mapa = int(
        mapa.get(
            "imagem_largura",
            LARGURA_MAPA
        )
    )

    altura_mapa = int(
        mapa.get(
            "imagem_altura",
            ALTURA_MAPA
        )
    )

    largura_imagem = imagem.shape[1]
    altura_imagem = imagem.shape[0]

    fator_x = (
        largura_imagem
        /
        largura_mapa
    )

    fator_y = (
        altura_imagem
        /
        altura_mapa
    )

    for coordenada in coordenadas:

        x1 = int(
            round(
                coordenada["x1"]
                * fator_x
            )
        )

        y1 = int(
            round(
                coordenada["y1"]
                * fator_y
            )
        )

        x2 = int(
            round(
                coordenada["x2"]
                * fator_x
            )
        )

        y2 = int(
            round(
                coordenada["y2"]
                * fator_y
            )
        )

        margem_x = int(
            round(
                MARGEM_OMR
                * fator_x
            )
        )

        margem_y = int(
            round(
                MARGEM_OMR
                * fator_y
            )
        )

        area_x1 = x1 + margem_x
        area_y1 = y1 + margem_y

        area_x2 = x2 - margem_x
        area_y2 = y2 - margem_y

        cv2.rectangle(
            imagem,
            (
                area_x1,
                area_y1
            ),
            (
                area_x2,
                area_y2
            ),
            (0, 0, 255),
            2
        )

    return imagem


# ==========================================================
# CLASSE DA JANELA
# ==========================================================

class JanelaAreaOMR:

    def __init__(
        self,
        master,
        caminho_pdf=None,
        caminho_mapa=None,
        ficha_id=None
    ):

        self.master = master
        self.caminho_pdf_inicial = caminho_pdf
        self.caminho_mapa_inicial = caminho_mapa
        self.ficha_id_inicial = ficha_id

        self.janela = tk.Toplevel(
            master
        )

        self.janela.title(
            "Onde devo marcar?"
        )

        self.janela.geometry(
            "1200x850"
        )

        self.janela.minsize(
            900,
            650
        )

        self.janela.protocol(
            "WM_DELETE_WINDOW",
            self.fechar
        )

        # ==================================================
        # ESTADO
        # ==================================================

        self.ficha_id = None

        self.caminho_pdf = None

        self.caminho_mapa = None

        self.mapa = None

        self.documento = None

        self.pagina_atual = 1

        self.total_paginas = 0

        self.imagem_tk = None

        self.imagem_exibida = None

        # ==================================================
        # INTERFACE
        # ==================================================

        self.criar_interface()

        # ==================================================
        # CARREGAR
        # ==================================================

        self.carregar()

    # ======================================================
    # INTERFACE
    # ======================================================

    def criar_interface(
        self
    ):

        # --------------------------------------------------
        # TÍTULO
        # --------------------------------------------------

        frame_titulo = tk.Frame(
            self.janela
        )

        frame_titulo.pack(
            fill="x",
            padx=15,
            pady=12
        )

        tk.Label(
            frame_titulo,
            text="Onde devo marcar?",
            font=(
                "Segoe UI",
                20,
                "bold"
            )
        ).pack(
            side="left"
        )

        self.label_ficha = tk.Label(
            frame_titulo,
            text="",
            font=(
                "Segoe UI",
                10
            )
        )

        self.label_ficha.pack(
            side="left",
            padx=15
        )

        # --------------------------------------------------
        # EXPLICAÇÃO
        # --------------------------------------------------

        tk.Label(
            self.janela,
            text=(
                "As áreas em vermelho indicam exatamente "
                "a região utilizada pelo sistema para "
                "identificar cada marcação."
            ),
            font=(
                "Segoe UI",
                10
            ),
            justify="left"
        ).pack(
            anchor="w",
            padx=15,
            pady=(0, 10)
        )

        # --------------------------------------------------
        # CONTROLES
        # --------------------------------------------------

        frame_controles = tk.Frame(
            self.janela
        )

        frame_controles.pack(
            fill="x",
            padx=15,
            pady=(0, 10)
        )

        self.botao_anterior = tk.Button(
            frame_controles,
            text="Página anterior",
            command=self.pagina_anterior,
            padx=12,
            pady=6
        )

        self.botao_anterior.pack(
            side="left"
        )

        self.label_pagina = tk.Label(
            frame_controles,
            text="Página 1 de 1",
            font=(
                "Segoe UI",
                10,
                "bold"
            )
        )

        self.label_pagina.pack(
            side="left",
            padx=15
        )

        self.botao_proxima = tk.Button(
            frame_controles,
            text="Próxima página",
            command=self.proxima_pagina,
            padx=12,
            pady=6
        )

        self.botao_proxima.pack(
            side="left"
        )

        # --------------------------------------------------
        # ÁREA DE IMAGEM
        # --------------------------------------------------

        frame_imagem = tk.Frame(
            self.janela,
            bd=1,
            relief="sunken"
        )

        frame_imagem.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.canvas = tk.Canvas(
            frame_imagem,
            background="#d0d0d0",
            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        self.canvas.bind(
            "<Configure>",
            self.redimensionar
        )

    # ======================================================
    # CARREGAR
    # ======================================================

    def carregar(
        self
    ):

        try:

            if (
                self.caminho_pdf_inicial
                and self.caminho_mapa_inicial
            ):
                self.caminho_pdf = os.path.abspath(
                    self.caminho_pdf_inicial
                )
                self.caminho_mapa = os.path.abspath(
                    self.caminho_mapa_inicial
                )
                self.ficha_id = (
                    self.ficha_id_inicial
                    or "ficha_visualizada"
                )
            else:
                (
                    self.ficha_id,
                    self.caminho_pdf,
                    self.caminho_mapa
                ) = obter_ficha_ativa()

            with open(
                self.caminho_mapa,
                "r",
                encoding="utf-8"
            ) as arquivo:

                self.mapa = json.load(
                    arquivo
                )

            self.documento = fitz.open(
                self.caminho_pdf
            )

            self.total_paginas = (
                self.documento.page_count
            )

            if self.total_paginas <= 0:

                raise ValueError(
                    "A ficha ativa não possui páginas."
                )

            self.label_ficha.configure(
                text=(
                    f"Ficha ativa: {self.ficha_id}"
                )
            )

            self.mostrar_pagina()

        except Exception as erro:

            messagebox.showerror(
                "Erro",
                (
                    "Não foi possível abrir a ficha ativa.\n\n"
                    f"{erro}"
                ),
                parent=self.janela
            )

            self.fechar()

    # ======================================================
    # PROCESSAR PÁGINA
    # ======================================================

    def processar_pagina(
        self,
        numero_pagina
    ):

        pagina_pdf = self.documento[
            numero_pagina - 1
        ]

        imagem = renderizar_pagina(
            pagina_pdf,
            DPI
        )

        (
            imagem_normalizada,
            _diagnostico,
            _pontos,
            _matriz
        ) = normalizar_com_diagnostico(
            imagem,
            pagina=numero_pagina
        )

        imagem_area = desenhar_area_omr(
            imagem_normalizada,
            self.mapa,
            numero_pagina
        )

        return imagem_area

    # ======================================================
    # MOSTRAR PÁGINA
    # ======================================================

    def mostrar_pagina(
        self
    ):

        if self.documento is None:
            return

        try:

            imagem = self.processar_pagina(
                self.pagina_atual
            )

            imagem_rgb = cv2.cvtColor(
                imagem,
                cv2.COLOR_BGR2RGB
            )

            imagem_pil = Image.fromarray(
                imagem_rgb
            )

            self.imagem_exibida = (
                imagem_pil
            )

            self.atualizar_imagem()

            self.atualizar_navegacao()

        except Exception as erro:

            messagebox.showerror(
                "Erro",
                (
                    "Não foi possível visualizar "
                    f"a página {self.pagina_atual}.\n\n"
                    f"{erro}"
                ),
                parent=self.janela
            )

    # ======================================================
    # ATUALIZAR IMAGEM
    # ======================================================

    def atualizar_imagem(
        self
    ):

        if self.imagem_exibida is None:
            return

        largura_canvas = max(
            self.canvas.winfo_width(),
            1
        )

        altura_canvas = max(
            self.canvas.winfo_height(),
            1
        )

        imagem = (
            self.imagem_exibida
        )

        margem = 20

        largura_disponivel = max(
            largura_canvas - margem * 2,
            100
        )

        altura_disponivel = max(
            altura_canvas - margem * 2,
            100
        )

        fator = min(
            largura_disponivel / imagem.width,
            altura_disponivel / imagem.height
        )

        fator = min(
            fator,
            1.0
        )

        largura = max(
            1,
            int(
                imagem.width
                * fator
            )
        )

        altura = max(
            1,
            int(
                imagem.height
                * fator
            )
        )

        imagem_redimensionada = (
            imagem.resize(
                (
                    largura,
                    altura
                ),
                Image.Resampling.LANCZOS
            )
        )

        self.imagem_tk = ImageTk.PhotoImage(
            imagem_redimensionada
        )

        self.canvas.delete(
            "all"
        )

        self.canvas.create_image(
            margem,
            margem,
            anchor="nw",
            image=self.imagem_tk
        )

        self.canvas.configure(
            scrollregion=(
                0,
                0,
                largura + margem * 2,
                altura + margem * 2
            )
        )

    # ======================================================
    # REDIMENSIONAR
    # ======================================================

    def redimensionar(
        self,
        _evento
    ):

        self.atualizar_imagem()

    # ======================================================
    # PÁGINA ANTERIOR
    # ======================================================

    def pagina_anterior(
        self
    ):

        if self.pagina_atual <= 1:
            return

        self.pagina_atual -= 1

        self.mostrar_pagina()

    # ======================================================
    # PRÓXIMA PÁGINA
    # ======================================================

    def proxima_pagina(
        self
    ):

        if (
            self.pagina_atual
            >= self.total_paginas
        ):
            return

        self.pagina_atual += 1

        self.mostrar_pagina()

    # ======================================================
    # NAVEGAÇÃO
    # ======================================================

    def atualizar_navegacao(
        self
    ):

        self.label_pagina.configure(
            text=(
                f"Página "
                f"{self.pagina_atual}"
                f" de "
                f"{self.total_paginas}"
            )
        )

        if self.pagina_atual <= 1:

            self.botao_anterior.configure(
                state="disabled"
            )

        else:

            self.botao_anterior.configure(
                state="normal"
            )

        if (
            self.pagina_atual
            >= self.total_paginas
        ):

            self.botao_proxima.configure(
                state="disabled"
            )

        else:

            self.botao_proxima.configure(
                state="normal"
            )

    # ======================================================
    # FECHAR
    # ======================================================

    def fechar(
        self
    ):

        if self.documento is not None:

            try:
                self.documento.close()
            except Exception:
                pass

            self.documento = None

        self.janela.destroy()


# ==========================================================
# FUNÇÃO PÚBLICA PARA O PROGRAMA PRINCIPAL
# ==========================================================

def abrir_area_omr(
    master,
    caminho_pdf=None,
    caminho_mapa=None,
    ficha_id=None
):

    return JanelaAreaOMR(
        master,
        caminho_pdf=caminho_pdf,
        caminho_mapa=caminho_mapa,
        ficha_id=ficha_id
    )


# ==========================================================
# EXECUÇÃO DIRETA PARA TESTES
# ==========================================================

if __name__ == "__main__":

    root = tk.Tk()

    root.withdraw()

    abrir_area_omr(
        root
    )

    root.mainloop()