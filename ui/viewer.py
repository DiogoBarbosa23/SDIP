import customtkinter as ctk
from PIL import Image


class PDFViewer(ctk.CTkLabel):

    def __init__(self, master):

        super().__init__(
            master,
            text="Nenhum PDF carregado"
        )


        # Guarda a imagem original do PDF
        self.imagem_original = None

        # Guarda a imagem exibida
        self.image = None


        # Atualiza automaticamente quando a área mudar de tamanho
        self.bind(
            "<Configure>",
            self.redimensionar
        )



    # ======================================================
    # Receber nova página do PDF
    # ======================================================

    def mostrar(self, imagem):

        self.imagem_original = imagem.copy()

        self.atualizar_imagem()



    # ======================================================
    # Ajustar imagem para caber na tela
    # ======================================================

    def atualizar_imagem(self):

        if self.imagem_original is None:
            return


        imagem = self.imagem_original.copy()


        # Tamanho disponível do visualizador

        largura = self.winfo_width()
        altura = self.winfo_height()


        # Evita erro na inicialização
        if largura <= 1:
            largura = 800


        if altura <= 1:
            altura = 600



        # Mantém proporção e faz caber na área

        imagem.thumbnail(
            (
                largura - 40,
                altura - 40
            ),
            Image.Resampling.LANCZOS
        )



        self.image = ctk.CTkImage(
            light_image=imagem,
            dark_image=imagem,
            size=imagem.size
        )


        self.configure(
            image=self.image,
            text=""
        )



    # ======================================================
    # Evento de redimensionamento
    # ======================================================

    def redimensionar(self, evento=None):

        self.atualizar_imagem()