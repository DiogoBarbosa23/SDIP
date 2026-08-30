import fitz
from PIL import Image
import io


class PDFReader:

    def __init__(self, pdf_path):

        self.document = fitz.open(pdf_path)


    # ======================================================
    # Total de páginas
    # ======================================================

    def total_paginas(self):

        return len(self.document)


    # ======================================================
    # Obter página como imagem
    # ======================================================

    def obter_pagina(self, indice):

        pagina = self.document.load_page(indice)

        pix = pagina.get_pixmap(
            matrix=fitz.Matrix(2, 2),
            alpha=False
        )

        # Converte a página renderizada para PNG
        imagem_bytes = pix.tobytes("png")

        # ==================================================
        # DEBUG
        # ==================================================

        print("====================================")
        print("PDFReader - obtendo página")
        print("Tipo dos bytes:", type(imagem_bytes))
        print("Tamanho dos bytes:", len(imagem_bytes))

        # Abre a imagem através dos bytes
        imagem = Image.open(
            io.BytesIO(imagem_bytes)
        )

        # Força o carregamento completo da imagem
        imagem.load()

        print("Imagem:", imagem)
        print("Formato:", imagem.format)
        print("Modo:", imagem.mode)
        print("Tamanho:", imagem.size)
        print("====================================")

        # Garante RGB
        if imagem.mode != "RGB":

            imagem = imagem.convert("RGB")

        return imagem


    # ======================================================
    # Fechar PDF
    # ======================================================

    def fechar(self):

        if self.document:

            self.document.close()