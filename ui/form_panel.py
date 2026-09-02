from datetime import datetime

import customtkinter as ctk


class FormPanel(ctk.CTkFrame):

    def __init__(
        self,
        master,
        salvar_callback=None
    ):

        super().__init__(
            master
        )

        self.salvar_callback = (
            salvar_callback
        )

        self.campos_identificacao = {}
        self.campos_identificacao_tipos = {}
        self.manter_identificacao = {}
        self.campos_abertos = {}

        self.criar_interface()

    # ==========================================================
    # INTERFACE
    # ==========================================================

    def criar_interface(self):

        titulo = ctk.CTkLabel(
            self,
            text="Identificação e respostas",
            font=(
                "Segoe UI",
                18,
                "bold"
            )
        )

        titulo.pack(
            pady=(10, 5)
        )

        self.scroll = ctk.CTkScrollableFrame(
            self
        )

        self.scroll.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        # ======================================================
        # IDENTIFICAÇÃO
        # ======================================================

        self.identificacao_frame = ctk.CTkFrame(
            self.scroll
        )

        self.identificacao_frame.pack(
            fill="x",
            padx=5,
            pady=(5, 10)
        )

        self.identificacao_titulo = ctk.CTkLabel(
            self.identificacao_frame,
            text="Identificação",
            font=(
                "Segoe UI",
                15,
                "bold"
            )
        )

        self.identificacao_titulo.pack(
            anchor="w",
            padx=10,
            pady=(8, 5)
        )

        self.identificacao_vazio = ctk.CTkLabel(
            self.identificacao_frame,
            text="Nenhum campo de identificação."
        )

        self.identificacao_vazio.pack(
            anchor="w",
            padx=10,
            pady=(0, 8)
        )

        # ======================================================
        # RESPOSTAS ABERTAS
        # ======================================================

        self.abertas_frame = ctk.CTkFrame(
            self.scroll
        )

        self.abertas_frame.pack(
            fill="x",
            padx=5,
            pady=(5, 10)
        )

        self.abertas_titulo = ctk.CTkLabel(
            self.abertas_frame,
            text="Respostas abertas",
            font=(
                "Segoe UI",
                15,
                "bold"
            )
        )

        self.abertas_titulo.pack(
            anchor="w",
            padx=10,
            pady=(8, 5)
        )

        self.abertas_vazio = ctk.CTkLabel(
            self.abertas_frame,
            text="Nenhuma pergunta aberta."
        )

        self.abertas_vazio.pack(
            anchor="w",
            padx=10,
            pady=(0, 8)
        )


    # ==========================================================
    # CAMPOS DE IDENTIFICAÇÃO
    # ==========================================================

    def configurar_campos_identificacao(
        self,
        campos
    ):

        valores_anteriores = {
            nome: campo.get()
            for nome, campo in self.campos_identificacao.items()
        }

        manter_anteriores = {
            nome: variavel.get()
            for nome, variavel in self.manter_identificacao.items()
        }

        for widget in self.identificacao_frame.winfo_children():

            if widget not in (
                self.identificacao_titulo,
            ):

                widget.destroy()

        self.campos_identificacao = {}
        self.campos_identificacao_tipos = {}
        self.manter_identificacao = {}

        if not campos:

            self.identificacao_vazio = ctk.CTkLabel(
                self.identificacao_frame,
                text="Nenhum campo de identificação."
            )

            self.identificacao_vazio.pack(
                anchor="w",
                padx=10,
                pady=(0, 8)
            )

            return

        for campo in campos:

            nome = str(
                campo.get(
                    "nome",
                    ""
                )
            ).strip()

            tipo = campo.get(
                "tipo",
                "Texto"
            )

            if not nome:

                continue

            ctk.CTkLabel(
                self.identificacao_frame,
                text=f"{nome}:"
            ).pack(
                anchor="w",
                padx=10,
                pady=(6, 2)
            )

            linha = ctk.CTkFrame(
                self.identificacao_frame,
                fg_color="transparent"
            )

            linha.pack(
                fill="x",
                padx=10,
                pady=(0, 4)
            )

            entrada = ctk.CTkEntry(
                linha,
                placeholder_text=(
                    self._placeholder_para_tipo(
                        tipo
                    )
                )
            )

            entrada.pack(
                side="left",
                fill="x",
                expand=True,
                padx=(0, 8)
            )

            if nome in valores_anteriores:

                valor_inicial = valores_anteriores[nome]

            elif tipo == "Data":

                valor_inicial = datetime.now().strftime(
                    "%d/%m/%Y"
                )

            else:

                valor_inicial = ""

            if valor_inicial:

                entrada.insert(
                    0,
                    valor_inicial
                )

            manter = ctk.BooleanVar(
                value=manter_anteriores.get(
                    nome,
                    False
                )
            )

            ctk.CTkCheckBox(
                linha,
                text="Manter",
                variable=manter,
                width=78
            ).pack(
                side="right"
            )

            self.campos_identificacao[
                nome
            ] = entrada

            self.campos_identificacao_tipos[
                nome
            ] = tipo

            self.manter_identificacao[
                nome
            ] = manter

    # ==========================================================
    # PLACEHOLDER
    # ==========================================================

    @staticmethod
    def _placeholder_para_tipo(
        tipo
    ):

        if tipo == "Número":

            return "Digite um número"

        if tipo == "Data":

            return "DD/MM/AAAA"

        return "Digite a informação"

    # ==========================================================
    # PERGUNTAS ABERTAS
    # ==========================================================

    def configurar_perguntas_abertas(
        self,
        perguntas
    ):

        for widget in self.abertas_frame.winfo_children():

            if widget not in (
                self.abertas_titulo,
            ):

                widget.destroy()

        self.campos_abertos = {}

        if not perguntas:

            self.abertas_vazio = ctk.CTkLabel(
                self.abertas_frame,
                text="Nenhuma pergunta aberta."
            )

            self.abertas_vazio.pack(
                anchor="w",
                padx=10,
                pady=(0, 8)
            )

            return

        for pergunta in perguntas:

            numero = str(
                pergunta.get(
                    "numero",
                    ""
                )
            )

            texto = pergunta.get(
                "texto",
                ""
            )

            ctk.CTkLabel(
                self.abertas_frame,
                text=(
                    f"{numero} - {texto}"
                ),
                wraplength=280,
                justify="left",
                anchor="w"
            ).pack(
                fill="x",
                padx=10,
                pady=(8, 3)
            )

            campo = ctk.CTkTextbox(
                self.abertas_frame,
                height=70
            )

            campo.pack(
                fill="x",
                padx=10,
                pady=(0, 5)
            )

            self.campos_abertos[
                numero
            ] = campo

    # ==========================================================
    # DADOS
    # ==========================================================

    def obter_dados(self):

        identificacao = {}

        for nome, campo in (
            self.campos_identificacao.items()
        ):

            identificacao[
                nome
            ] = campo.get().strip()

        respostas_abertas = {}

        for numero, campo in (
            self.campos_abertos.items()
        ):

            respostas_abertas[
                numero
            ] = campo.get(
                "1.0",
                "end-1c"
            ).strip()

        return {
            "identificacao": identificacao,
            "respostas_abertas": respostas_abertas
        }

    # ==========================================================
    # VALIDAR DATAS
    # ==========================================================

    def validar_datas(self):

        campos_invalidos = []

        for nome, campo in self.campos_identificacao.items():

            if self.campos_identificacao_tipos.get(
                nome
            ) != "Data":

                continue

            valor = campo.get().strip()

            if not valor:

                continue

            try:

                data = datetime.strptime(
                    valor,
                    "%d/%m/%Y"
                )

            except ValueError:

                campos_invalidos.append(
                    nome
                )

                continue

            if data.strftime(
                "%d/%m/%Y"
            ) != valor:

                campos_invalidos.append(
                    nome
                )

        return campos_invalidos

    # ==========================================================
    # SALVAR
    # ==========================================================

    def salvar(self):

        dados = self.obter_dados()

        if self.salvar_callback:

            self.salvar_callback(
                dados
            )

    # ==========================================================
    # LIMPAR APÓS SALVAR
    # ==========================================================

    def limpar_apos_salvar(self):

        for nome, campo in self.campos_identificacao.items():

            manter = self.manter_identificacao.get(
                nome
            )

            if manter is not None and manter.get():

                continue

            campo.delete(
                0,
                "end"
            )

        for campo in self.campos_abertos.values():

            campo.delete(
                "1.0",
                "end"
            )

    # ==========================================================
    # LIMPAR
    # ==========================================================

    def limpar(self):

        for campo in (
            self.campos_identificacao.values()
        ):

            campo.delete(
                0,
                "end"
            )

        for campo in (
            self.campos_abertos.values()
        ):

            campo.delete(
                "1.0",
                "end"
            )