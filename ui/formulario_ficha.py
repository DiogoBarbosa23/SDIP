import os

import customtkinter as ctk

from tkinter import filedialog, messagebox, ttk


class SecaoEditor(ctk.CTkFrame):

    def __init__(
        self,
        master,
        numero,
        remover_callback
    ):
        super().__init__(
            master,
            border_width=1
        )

        self.numero = numero
        self.remover_callback = remover_callback

        self.criar_interface()

    def criar_interface(self):

        self.grid_columnconfigure(
            0,
            weight=1
        )

        titulo = ctk.CTkLabel(
            self,
            text=f"Seção {self.numero}",
            font=(
                "Segoe UI",
                14,
                "bold"
            )
        )

        titulo.grid(
            row=0,
            column=0,
            sticky="w",
            padx=15,
            pady=(12, 5)
        )

        ctk.CTkButton(
            self,
            text="Remover",
            width=90,
            command=self.remover
        ).grid(
            row=0,
            column=1,
            padx=15,
            pady=(12, 5)
        )

        ctk.CTkLabel(
            self,
            text="Título da seção:"
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            padx=15,
            pady=(5, 2)
        )

        self.texto = ctk.CTkEntry(
            self,
            placeholder_text="Ex.: Situação da obra"
        )

        self.texto.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=15,
            pady=(0, 15)
        )

    def remover(self):
        self.remover_callback(self)

    def obter_dados(self):

        return {
            "tipo": "secao",
            "numero": self.numero,
            "texto": self.texto.get().strip()
        }


class CampoIdentificacaoEditor(ctk.CTkFrame):

    def __init__(
        self,
        master,
        numero,
        remover_callback
    ):
        super().__init__(
            master,
            border_width=1
        )

        self.numero = numero
        self.remover_callback = remover_callback

        self.criar_interface()

    def criar_interface(self):

        self.grid_columnconfigure(
            0,
            weight=1
        )

        ctk.CTkLabel(
            self,
            text=f"Campo {self.numero}",
            font=(
                "Segoe UI",
                13,
                "bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=12,
            pady=(10, 5)
        )

        ctk.CTkButton(
            self,
            text="×",
            width=35,
            command=self.remover
        ).grid(
            row=0,
            column=1,
            padx=12,
            pady=(10, 5)
        )

        ctk.CTkLabel(
            self,
            text="Nome do campo:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=12,
            pady=(3, 2)
        )

        self.nome = ctk.CTkEntry(
            self,
            placeholder_text="Ex.: Nome do morador"
        )

        self.nome.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 8)
        )

        ctk.CTkLabel(
            self,
            text="Tipo:"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=12,
            pady=(2, 2)
        )

        self.tipo = ctk.CTkComboBox(
            self,
            values=[
                "Texto",
                "Número",
                "Data"
            ]
        )

        self.tipo.set(
            "Texto"
        )

        self.tipo.grid(
            row=4,
            column=0,
            sticky="w",
            padx=12,
            pady=(0, 10)
        )

    def remover(self):
        self.remover_callback(self)

    def obter_dados(self):

        return {
            "nome": self.nome.get().strip(),
            "tipo": self.tipo.get()
        }

    def carregar_dados(
        self,
        dados
    ):

        self.nome.delete(
            0,
            "end"
        )

        self.nome.insert(
            0,
            dados.get(
                "nome",
                ""
            )
        )

        tipo = dados.get(
            "tipo",
            "Texto"
        )

        if tipo not in (
            "Texto",
            "Número",
            "Data"
        ):
            tipo = "Texto"

        self.tipo.set(
            tipo
        )

    def atualizar_numero(
        self,
        numero
    ):

        self.numero = numero

        for filho in self.winfo_children():

            if isinstance(
                filho,
                ctk.CTkLabel
            ):

                texto = filho.cget(
                    "text"
                )

                if texto.startswith(
                    "Campo "
                ):

                    filho.configure(
                        text=f"Campo {numero}"
                    )

                    break


class PerguntaEditor(ctk.CTkFrame):

    def __init__(
        self,
        master,
        numero,
        remover_callback
    ):

        super().__init__(
            master,
            border_width=1
        )

        self.numero = numero
        self.remover_callback = remover_callback
        self.opcoes = []

        self.criar_interface()

    def criar_interface(self):

        self.grid_columnconfigure(
            0,
            weight=1
        )

        ctk.CTkLabel(
            self,
            text=self._titulo_pergunta(),
            font=(
                "Segoe UI",
                14,
                "bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=15,
            pady=(12, 5)
        )

        ctk.CTkButton(
            self,
            text="Remover",
            width=90,
            command=self.remover
        ).grid(
            row=0,
            column=1,
            padx=15,
            pady=(12, 5)
        )

        ctk.CTkLabel(
            self,
            text="Pergunta:"
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            padx=15,
            pady=(5, 2)
        )

        self.texto = ctk.CTkEntry(
            self,
            placeholder_text="Digite a pergunta"
        )

        self.texto.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=15,
            pady=(0, 10)
        )

        ctk.CTkLabel(
            self,
            text="Tipo de resposta:"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=15,
            pady=(0, 2)
        )

        self.tipo = ctk.CTkComboBox(
            self,
            values=[
                "Única",
                "Múltipla"
            ]
        )

        self.tipo.set(
            "Única"
        )

        self.tipo.grid(
            row=4,
            column=0,
            sticky="w",
            padx=15,
            pady=(0, 5)
        )

        self.aberta = ctk.CTkCheckBox(
            self,
            text="Resposta aberta",
            command=self.atualizar_modo_aberta
        )

        self.aberta.grid(
            row=4,
            column=1,
            sticky="w",
            padx=15,
            pady=(0, 5)
        )

        self.opcoes_label = ctk.CTkLabel(
            self,
            text="Opções:"
        )

        self.opcoes_label.grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="w",
            padx=15,
            pady=(0, 2)
        )

        self.opcoes_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.opcoes_frame.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=15
        )

        self.opcoes_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.adicionar_opcao_button = ctk.CTkButton(
            self,
            text="+ Adicionar opção",
            width=150,
            command=self.adicionar_opcao
        )

        self.adicionar_opcao_button.grid(
            row=7,
            column=0,
            sticky="w",
            padx=15,
            pady=(8, 15)
        )

        self.adicionar_opcao()
        self.adicionar_opcao()

    def _titulo_pergunta(self):

        numero = str(
            self.numero
        ).strip()

        if numero:
            return f"Pergunta {numero}"

        return "Pergunta"

    def atualizar_titulo(
        self,
        numero
    ):

        self.numero = numero

        for filho in self.winfo_children():

            if isinstance(
                filho,
                ctk.CTkLabel
            ):

                texto = filho.cget(
                    "text"
                )

                if texto.startswith(
                    "Pergunta"
                ):

                    filho.configure(
                        text=self._titulo_pergunta()
                    )

                    break

    def atualizar_modo_aberta(self):

        aberta = (
            self.aberta.get() == 1
        )

        if aberta:

            self.opcoes_label.grid_remove()
            self.opcoes_frame.grid_remove()
            self.adicionar_opcao_button.grid_remove()

            self.tipo.configure(
                state="disabled"
            )

        else:

            self.opcoes_label.grid()
            self.opcoes_frame.grid()
            self.adicionar_opcao_button.grid()

            self.tipo.configure(
                state="normal"
            )

    def adicionar_opcao(
        self,
        valor_inicial=""
    ):

        numero = (
            len(self.opcoes)
            + 1
        )

        frame = ctk.CTkFrame(
            self.opcoes_frame,
            fg_color="transparent"
        )

        frame.grid(
            row=numero - 1,
            column=0,
            sticky="ew",
            pady=2
        )

        frame.grid_columnconfigure(
            0,
            weight=1
        )

        entrada = ctk.CTkEntry(
            frame,
            placeholder_text=f"Opção {numero}"
        )

        entrada.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 8)
        )

        if valor_inicial:

            entrada.insert(
                0,
                valor_inicial
            )

        ctk.CTkButton(
            frame,
            text="×",
            width=35,
            command=lambda: self.remover_opcao(
                frame,
                entrada
            )
        ).grid(
            row=0,
            column=1
        )

        self.opcoes.append(
            {
                "frame": frame,
                "entrada": entrada
            }
        )

    def remover_opcao(
        self,
        frame,
        entrada
    ):

        if len(self.opcoes) <= 1:

            messagebox.showwarning(
                "Opção",
                (
                    "Uma pergunta precisa "
                    "ter pelo menos uma opção."
                )
            )

            return

        frame.destroy()

        self.opcoes = [
            opcao
            for opcao in self.opcoes
            if opcao["entrada"] is not entrada
        ]

        self.renumerar_opcoes()

    def renumerar_opcoes(self):

        for indice, opcao in enumerate(
            self.opcoes,
            start=1
        ):

            opcao["frame"].grid_configure(
                row=indice - 1
            )

            opcao["entrada"].configure(
                placeholder_text=f"Opção {indice}"
            )

    def remover(self):

        self.remover_callback(
            self
        )

    def obter_dados(self):

        texto = (
            self.texto.get().strip()
        )

        if self.aberta.get() == 1:

            return {
                "tipo": "pergunta",
                "numero": str(
                    self.numero
                ),
                "texto": texto,
                "tipo_resposta": "aberta",
                "opcoes": []
            }

        tipo = self.tipo.get()

        opcoes = []

        for opcao in self.opcoes:

            valor = (
                opcao["entrada"]
                .get()
                .strip()
            )

            if valor:
                opcoes.append(
                    valor
                )

        return {
            "tipo": "pergunta",
            "numero": str(
                self.numero
            ),
            "texto": texto,
            "tipo_resposta": (
                "unica"
                if tipo == "Única"
                else "multipla"
            ),
            "opcoes": opcoes
        }

    def carregar_dados(
        self,
        dados
    ):

        self.texto.delete(
            0,
            "end"
        )

        self.texto.insert(
            0,
            dados.get(
                "texto",
                ""
            )
        )

        tipo_resposta = dados.get(
            "tipo_resposta",
            "unica"
        )

        if tipo_resposta == "aberta":

            self.aberta.select()
            self.atualizar_modo_aberta()

            return

        self.aberta.deselect()

        self.tipo.configure(
            state="normal"
        )

        self.tipo.set(
            "Múltipla"
            if tipo_resposta == "multipla"
            else "Única"
        )

        for opcao in self.opcoes:
            opcao["frame"].destroy()

        self.opcoes = []

        opcoes = dados.get(
            "opcoes",
            []
        )

        if not opcoes:

            self.adicionar_opcao()
            self.adicionar_opcao()

        else:

            for valor in opcoes:

                self.adicionar_opcao(
                    valor
                )


class FormularioFicha(ctk.CTkFrame):

    TAMANHO_FONTE_PADRAO = 14
    TAMANHOS_FONTE = [
        "10 pt",
        "11 pt",
        "12 pt",
        "13 pt",
        "14 pt",
        "15 pt",
        "16 pt",
        "17 pt",
        "18 pt",
        "19 pt",
        "20 pt"
    ]

    def __init__(
        self,
        master,
        voltar_callback=None,
        gerar_callback=None,
        dados_iniciais=None
    ):

        super().__init__(
            master
        )

        self.voltar_callback = (
            voltar_callback
        )

        self.gerar_callback = (
            gerar_callback
        )

        self.dados_iniciais = (
            dados_iniciais
        )

        self.elementos = []
        self.campos_identificacao = []
        self.logo_path = None

        self.tamanho_fonte = (
            self.TAMANHO_FONTE_PADRAO
        )

        self.criar_interface()

        if dados_iniciais:

            self.carregar_dados(
                dados_iniciais
            )

        else:

            self.adicionar_pergunta()

    # ==========================================================
    # INTERFACE
    # ==========================================================

    def criar_interface(self):

        self.grid_rowconfigure(
            1,
            weight=1
        )

        self.grid_columnconfigure(
            0,
            weight=1
        )

        # ------------------------------------------------------
        # CABEÇALHO
        # ------------------------------------------------------

        header = ctk.CTkFrame(
            self
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=(10, 5)
        )

        header.grid_columnconfigure(
            1,
            weight=1
        )

        ctk.CTkLabel(
            header,
            text="Criar nova ficha",
            font=(
                "Segoe UI",
                22,
                "bold"
            )
        ).grid(
            row=0,
            column=0,
            padx=15,
            pady=10
        )

        ctk.CTkButton(
            header,
            text="Voltar",
            width=100,
            command=self.voltar
        ).grid(
            row=0,
            column=1,
            sticky="e",
            padx=15,
            pady=10
        )

        # ------------------------------------------------------
        # ÁREA PRINCIPAL REDIMENSIONÁVEL
        # ------------------------------------------------------

        paned = ttk.Panedwindow(
            self,
            orient="horizontal"
        )

        paned.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=5
        )

        painel_configuracao = ctk.CTkFrame(
            paned
        )

        painel_estrutura = ctk.CTkFrame(
            paned
        )

        paned.add(
            painel_configuracao,
            weight=2
        )

        paned.add(
            painel_estrutura,
            weight=3
        )

        def posicionar_divisor_inicial():

            largura = paned.winfo_width()

            if largura > 1:

                paned.sashpos(
                    0,
                    int(largura * 0.42)
                )

        self.after_idle(
            posicionar_divisor_inicial
        )

        # ======================================================
        # COLUNA ESQUERDA - CONFIGURAÇÃO
        # ======================================================

        painel_configuracao.grid_columnconfigure(
            0,
            weight=1
        )

        painel_configuracao.grid_rowconfigure(
            2,
            weight=1
        )

        ctk.CTkLabel(
            painel_configuracao,
            text="Configuração",
            font=(
                "Segoe UI",
                18,
                "bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=15,
            pady=(12, 6)
        )

        # ------------------------------------------------------
        # DADOS DA FICHA
        # ------------------------------------------------------

        dados_frame = ctk.CTkFrame(
            painel_configuracao
        )

        dados_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=10,
            pady=(0, 8)
        )

        dados_frame.grid_columnconfigure(
            1,
            weight=1
        )

        ctk.CTkLabel(
            dados_frame,
            text="Nome da pesquisa:"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(10, 6),
            pady=(10, 4)
        )

        self.nome_pesquisa = ctk.CTkEntry(
            dados_frame,
            placeholder_text="Ex.: Pesquisa de Satisfação"
        )

        self.nome_pesquisa.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 10),
            pady=(10, 4)
        )

        ctk.CTkLabel(
            dados_frame,
            text="Título:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=(10, 6),
            pady=4
        )

        self.titulo = ctk.CTkEntry(
            dados_frame,
            placeholder_text="Opcional"
        )

        self.titulo.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(6, 10),
            pady=4
        )

        # ------------------------------------------------------
        # LOGO
        # ------------------------------------------------------

        ctk.CTkLabel(
            dados_frame,
            text="Logo:"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=(10, 6),
            pady=4
        )

        logo_frame = ctk.CTkFrame(
            dados_frame,
            fg_color="transparent"
        )

        logo_frame.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=(6, 10),
            pady=4
        )

        logo_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.logo_nome = ctk.CTkLabel(
            logo_frame,
            text="Nenhuma logo selecionada.",
            anchor="w"
        )

        self.logo_nome.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 4)
        )

        self.logo_button = ctk.CTkButton(
            logo_frame,
            text="Escolher PNG",
            width=110,
            command=self.selecionar_logo
        )

        self.logo_button.grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 5)
        )

        self.remover_logo_button = ctk.CTkButton(
            logo_frame,
            text="Remover",
            width=80,
            command=self.remover_logo,
            state="disabled"
        )

        self.remover_logo_button.grid(
            row=1,
            column=1,
            sticky="e"
        )

        # ------------------------------------------------------
        # TAMANHO DA FONTE
        # ------------------------------------------------------

        ctk.CTkLabel(
            dados_frame,
            text="Fonte:"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=(10, 6),
            pady=(4, 10)
        )

        fonte_frame = ctk.CTkFrame(
            dados_frame,
            fg_color="transparent"
        )

        fonte_frame.grid(
            row=3,
            column=1,
            sticky="ew",
            padx=(6, 10),
            pady=(4, 10)
        )

        fonte_frame.grid_columnconfigure(
            1,
            weight=1
        )

        self.tamanho_fonte_combo = ctk.CTkComboBox(
            fonte_frame,
            values=self.TAMANHOS_FONTE,
            width=100,
            state="readonly",
            command=self.alterar_tamanho_fonte
        )

        self.tamanho_fonte_combo.set(
            f"{self.TAMANHO_FONTE_PADRAO} pt"
        )

        self.tamanho_fonte_combo.grid(
            row=0,
            column=0,
            sticky="w"
        )

        ctk.CTkLabel(
            fonte_frame,
            text="Menor = mais perguntas.",
            anchor="w"
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=(8, 0)
        )

        # ------------------------------------------------------
        # CAMPOS DE IDENTIFICAÇÃO
        # ------------------------------------------------------

        identificacao = ctk.CTkFrame(
            painel_configuracao
        )

        identificacao.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10)
        )

        identificacao.grid_columnconfigure(
            0,
            weight=1
        )

        identificacao.grid_rowconfigure(
            2,
            weight=1
        )

        ctk.CTkLabel(
            identificacao,
            text="Campos de identificação",
            font=(
                "Segoe UI",
                16,
                "bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=12,
            pady=(10, 2)
        )

        ctk.CTkLabel(
            identificacao,
            text="Preenchidos durante a digitalização.",
            justify="left"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=12,
            pady=(0, 6)
        )

        self.identificacao_scroll = ctk.CTkScrollableFrame(
            identificacao
        )

        self.identificacao_scroll.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=12,
            pady=4
        )

        self.adicionar_campo_button = ctk.CTkButton(
            identificacao,
            text="+ Adicionar campo",
            width=160,
            command=self.adicionar_campo_identificacao
        )

        self.adicionar_campo_button.grid(
            row=3,
            column=0,
            sticky="w",
            padx=12,
            pady=(5, 10)
        )

        # ======================================================
        # COLUNA DIREITA - ESTRUTURA DA FICHA
        # ======================================================

        painel_estrutura.grid_columnconfigure(
            0,
            weight=1
        )

        painel_estrutura.grid_rowconfigure(
            2,
            weight=1
        )

        ctk.CTkLabel(
            painel_estrutura,
            text="Estrutura da ficha",
            font=(
                "Segoe UI",
                18,
                "bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=15,
            pady=(12, 6)
        )

        controles = ctk.CTkFrame(
            painel_estrutura,
            fg_color="transparent"
        )

        controles.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=10,
            pady=(0, 5)
        )

        ctk.CTkButton(
            controles,
            text="+ Adicionar seção",
            command=self.adicionar_secao
        ).pack(
            side="left",
            padx=(0, 8)
        )

        ctk.CTkButton(
            controles,
            text="+ Adicionar pergunta",
            command=self.adicionar_pergunta
        ).pack(
            side="left"
        )

        self.scroll = ctk.CTkScrollableFrame(
            painel_estrutura
        )

        self.scroll.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10)
        )

        # ------------------------------------------------------
        # RODAPÉ FIXO
        # ------------------------------------------------------

        rodape = ctk.CTkFrame(
            self
        )

        rodape.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=10,
            pady=(5, 10)
        )

        self.status = ctk.CTkLabel(
            rodape,
            text="0 campos / 0 seções / 0 perguntas"
        )

        self.status.pack(
            side="left",
            padx=15,
            pady=8
        )

        self.gerar_button = ctk.CTkButton(
            rodape,
            text="Gerar ficha",
            command=self.gerar
        )

        self.gerar_button.pack(
            side="right",
            padx=15,
            pady=8
        )

        self.modo_edicao_label = ctk.CTkLabel(
            rodape,
            text="",
            font=(
                "Segoe UI",
                11
            )
        )

        self.modo_edicao_label.pack(
            side="right",
            padx=10
        )

    # ==========================================================
    # LOGO
    # ==========================================================

    def selecionar_logo(self):

        caminho = filedialog.askopenfilename(
            title="Selecionar logo",
            filetypes=[
                (
                    "Imagem PNG",
                    "*.png"
                )
            ]
        )

        if not caminho:
            return

        self.logo_path = caminho

        self.logo_nome.configure(
            text=os.path.basename(
                caminho
            )
        )

        self.remover_logo_button.configure(
            state="normal"
        )

    def remover_logo(self):

        self.logo_path = None

        self.logo_nome.configure(
            text="Nenhuma logo selecionada."
        )

        self.remover_logo_button.configure(
            state="disabled"
        )

    def atualizar_logo_interface(
        self,
        caminho
    ):

        if caminho and os.path.isfile(
            caminho
        ):

            self.logo_path = caminho

            self.logo_nome.configure(
                text=os.path.basename(
                    caminho
                )
            )

            self.remover_logo_button.configure(
                state="normal"
            )

        else:

            self.remover_logo()

    # ==========================================================
    # TAMANHO DA FONTE
    # ==========================================================

    def alterar_tamanho_fonte(
        self,
        valor
    ):

        try:

            tamanho = int(
                str(valor)
                .replace(
                    " pt",
                    ""
                )
                .strip()
            )

        except (
            TypeError,
            ValueError
        ):

            tamanho = (
                self.TAMANHO_FONTE_PADRAO
            )

        tamanho = max(
            10,
            min(
                20,
                tamanho
            )
        )

        self.tamanho_fonte = tamanho

    # ==========================================================
    # CAMPOS DE IDENTIFICAÇÃO
    # ==========================================================

    def adicionar_campo_identificacao(
        self,
        dados_iniciais=None
    ):

        numero = (
            len(
                self.campos_identificacao
            )
            + 1
        )

        campo = CampoIdentificacaoEditor(
            self.identificacao_scroll,
            numero,
            self.remover_campo_identificacao
        )

        campo.pack(
            fill="x",
            pady=4
        )

        if dados_iniciais:

            campo.carregar_dados(
                dados_iniciais
            )

        self.campos_identificacao.append(
            campo
        )

        self.atualizar_status()

    def remover_campo_identificacao(
        self,
        campo
    ):

        campo.destroy()

        self.campos_identificacao = [
            item
            for item in self.campos_identificacao
            if item is not campo
        ]

        self.renumerar_campos_identificacao()
        self.atualizar_status()

    def renumerar_campos_identificacao(self):

        for numero, campo in enumerate(
            self.campos_identificacao,
            start=1
        ):

            campo.atualizar_numero(
                numero
            )

            campo.grid_configure()

    def obter_campos_identificacao(self):

        campos = []

        for campo in self.campos_identificacao:

            dados = campo.obter_dados()

            if not dados["nome"]:

                messagebox.showwarning(
                    "Campo de identificação",
                    (
                        f"Informe o nome do campo "
                        f"{campo.numero}."
                    )
                )

                return None

            campos.append(
                dados
            )

        return campos

    # ==========================================================
    # CARREGAR DADOS
    # ==========================================================

    def carregar_dados(
        self,
        dados
    ):

        self.nome_pesquisa.delete(
            0,
            "end"
        )

        self.nome_pesquisa.insert(
            0,
            dados.get(
                "nome_pesquisa",
                ""
            )
        )

        self.titulo.delete(
            0,
            "end"
        )

        self.titulo.insert(
            0,
            dados.get(
                "titulo",
                ""
            )
        )

        self.atualizar_logo_interface(
            dados.get(
                "logo_path"
            )
        )

        # ------------------------------------------------------
        # TAMANHO DA FONTE
        # ------------------------------------------------------

        tamanho_fonte = dados.get(
            "tamanho_fonte",
            self.TAMANHO_FONTE_PADRAO
        )

        try:

            tamanho_fonte = int(
                tamanho_fonte
            )

        except (
            TypeError,
            ValueError
        ):

            tamanho_fonte = (
                self.TAMANHO_FONTE_PADRAO
            )

        tamanho_fonte = max(
            10,
            min(
                20,
                tamanho_fonte
            )
        )

        self.tamanho_fonte = (
            tamanho_fonte
        )

        self.tamanho_fonte_combo.set(
            f"{tamanho_fonte} pt"
        )

        # ------------------------------------------------------
        # CAMPOS DE IDENTIFICAÇÃO
        # ------------------------------------------------------

        for campo in self.campos_identificacao:
            campo.destroy()

        self.campos_identificacao = []

        for campo in dados.get(
            "campos_identificacao",
            []
        ):

            self.adicionar_campo_identificacao(
                campo
            )

        # ------------------------------------------------------
        # ELEMENTOS
        # ------------------------------------------------------

        self.elementos = []

        for filho in self.scroll.winfo_children():
            filho.destroy()

        elementos = dados.get(
            "elementos"
        )

        if elementos is None:

            elementos = []

            for pergunta in dados.get(
                "perguntas",
                []
            ):

                elementos.append(
                    pergunta
                )

        for elemento in elementos:

            tipo = elemento.get(
                "tipo",
                "pergunta"
            )

            if tipo == "secao":

                secao = SecaoEditor(
                    self.scroll,
                    elemento.get(
                        "numero",
                        self.contar_secoes() + 1
                    ),
                    self.remover_secao
                )

                secao.pack(
                    fill="x",
                    pady=7
                )

                secao.texto.insert(
                    0,
                    elemento.get(
                        "texto",
                        ""
                    )
                )

                self.elementos.append(
                    {
                        "tipo": "secao",
                        "widget": secao
                    }
                )

            else:

                pergunta = PerguntaEditor(
                    self.scroll,
                    elemento.get(
                        "numero",
                        ""
                    ),
                    self.remover_pergunta
                )

                pergunta.pack(
                    fill="x",
                    pady=7
                )

                pergunta.carregar_dados(
                    elemento
                )

                self.elementos.append(
                    {
                        "tipo": "pergunta",
                        "widget": pergunta
                    }
                )

        if not self.elementos:
            self.adicionar_pergunta()

        self.renumerar_elementos()

        self.modo_edicao_label.configure(
            text="Editando ficha existente"
        )

    # ==========================================================
    # SEÇÕES
    # ==========================================================

    def adicionar_secao(self):

        numero = (
            self.contar_secoes()
            + 1
        )

        secao = SecaoEditor(
            self.scroll,
            numero,
            self.remover_secao
        )

        if self.contar_secoes() == 0:

            primeira_pergunta = None

            for elemento in self.elementos:

                if elemento["tipo"] == "pergunta":

                    primeira_pergunta = (
                        elemento["widget"]
                    )

                    break

            if primeira_pergunta:

                secao.pack(
                    fill="x",
                    pady=7,
                    before=primeira_pergunta
                )

            else:

                secao.pack(
                    fill="x",
                    pady=7
                )

            indice_insercao = 0

            for indice, elemento in enumerate(
                self.elementos
            ):

                if elemento["tipo"] == "pergunta":

                    indice_insercao = indice

                    break

            self.elementos.insert(
                indice_insercao,
                {
                    "tipo": "secao",
                    "widget": secao
                }
            )

        else:

            secao.pack(
                fill="x",
                pady=7
            )

            self.elementos.append(
                {
                    "tipo": "secao",
                    "widget": secao
                }
            )

        self.renumerar_elementos()

    def remover_secao(
        self,
        secao
    ):

        secao.destroy()

        self.elementos = [
            elemento
            for elemento in self.elementos
            if elemento["widget"] is not secao
        ]

        self.renumerar_elementos()

    # ==========================================================
    # PERGUNTAS
    # ==========================================================

    def adicionar_pergunta(self):

        pergunta = PerguntaEditor(
            self.scroll,
            "",
            self.remover_pergunta
        )

        pergunta.pack(
            fill="x",
            pady=7
        )

        self.elementos.append(
            {
                "tipo": "pergunta",
                "widget": pergunta
            }
        )

        self.renumerar_elementos()

    def remover_pergunta(
        self,
        pergunta
    ):

        if self.contar_perguntas() <= 1:

            messagebox.showwarning(
                "Pergunta",
                (
                    "A ficha precisa ter "
                    "pelo menos uma pergunta."
                )
            )

            return

        pergunta.destroy()

        self.elementos = [
            elemento
            for elemento in self.elementos
            if elemento["widget"] is not pergunta
        ]

        self.renumerar_elementos()

    # ==========================================================
    # NUMERAÇÃO
    # ==========================================================

    def renumerar_elementos(self):

        numero_secao = 0
        pergunta_global = 0
        pergunta_na_secao = 0

        possui_secao = (
            self.contar_secoes() > 0
        )

        for elemento in self.elementos:

            widget = elemento["widget"]

            if elemento["tipo"] == "secao":

                numero_secao += 1
                pergunta_na_secao = 0

                widget.numero = (
                    numero_secao
                )

                self.atualizar_titulo_widget(
                    widget,
                    f"Seção {numero_secao}"
                )

            else:

                pergunta_global += 1

                if possui_secao:

                    pergunta_na_secao += 1

                    numero = (
                        f"{numero_secao}."
                        f"{pergunta_na_secao}"
                    )

                else:

                    numero = str(
                        pergunta_global
                    )

                widget.atualizar_titulo(
                    numero
                )

        self.atualizar_status()

    @staticmethod
    def atualizar_titulo_widget(
        widget,
        texto
    ):

        for filho in widget.winfo_children():

            if isinstance(
                filho,
                ctk.CTkLabel
            ):

                atual = filho.cget(
                    "text"
                )

                if (
                    atual.startswith(
                        "Seção "
                    )
                    or atual.startswith(
                        "Pergunta"
                    )
                ):

                    filho.configure(
                        text=texto
                    )

                    break

    # ==========================================================
    # CONTADORES
    # ==========================================================

    def contar_secoes(self):

        return sum(
            1
            for elemento in self.elementos
            if elemento["tipo"] == "secao"
        )

    def contar_perguntas(self):

        return sum(
            1
            for elemento in self.elementos
            if elemento["tipo"] == "pergunta"
        )

    def atualizar_status(self):

        campos = len(
            self.campos_identificacao
        )

        secoes = self.contar_secoes()

        perguntas = self.contar_perguntas()

        self.status.configure(
            text=(
                f"{campos} "
                + (
                    "campo"
                    if campos == 1
                    else "campos"
                )
                + " / "
                + f"{secoes} "
                + (
                    "seção"
                    if secoes == 1
                    else "seções"
                )
                + " / "
                + f"{perguntas} "
                + (
                    "pergunta"
                    if perguntas == 1
                    else "perguntas"
                )
            )
        )

    # ==========================================================
    # GERAR
    # ==========================================================

    def gerar(self):

        nome = (
            self.nome_pesquisa
            .get()
            .strip()
        )

        titulo = (
            self.titulo
            .get()
            .strip()
        )

        if not nome:

            messagebox.showwarning(
                "Dados da ficha",
                "Informe o nome da pesquisa."
            )

            return

        campos_identificacao = (
            self.obter_campos_identificacao()
        )

        if campos_identificacao is None:
            return

        elementos = []

        for elemento in self.elementos:

            dados = (
                elemento["widget"]
                .obter_dados()
            )

            if dados["tipo"] == "secao":

                if not dados["texto"]:

                    messagebox.showwarning(
                        "Seção",
                        (
                            f"Informe o título "
                            f"da seção {dados['numero']}."
                        )
                    )

                    return

                elementos.append(
                    dados
                )

                continue

            if not dados["texto"]:

                messagebox.showwarning(
                    "Pergunta",
                    (
                        "Informe o texto da "
                        f"pergunta {dados['numero']}."
                    )
                )

                return

            if (
                dados["tipo_resposta"] != "aberta"
                and len(
                    dados["opcoes"]
                ) < 2
            ):

                messagebox.showwarning(
                    "Opções",
                    (
                        f"A pergunta "
                        f"{dados['numero']} precisa "
                        "ter pelo menos duas opções."
                    )
                )

                return

            elementos.append(
                dados
            )

        if self.contar_perguntas() == 0:

            messagebox.showwarning(
                "Perguntas",
                "Adicione pelo menos uma pergunta."
            )

            return

        dados_ficha = {
            "nome_pesquisa": nome,
            "titulo": titulo,
            "logo_path": self.logo_path,
            "tamanho_fonte": self.tamanho_fonte,
            "campos_identificacao": (
                campos_identificacao
            ),
            "elementos": elementos
        }

        if self.gerar_callback:

            self.gerar_callback(
                dados_ficha
            )

    # ==========================================================
    # VOLTAR
    # ==========================================================

    def voltar(self):

        if self.voltar_callback:

            self.voltar_callback()