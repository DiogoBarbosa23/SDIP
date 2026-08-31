import os
import json
import shutil
import customtkinter as ctk

from tkinter import (
    filedialog,
    messagebox,
    ttk
)

from PIL import Image

from engine.pdf_reader import PDFReader
from engine.gerador_ficha import GeradorFicha
from engine.fichas_manager import FichasManager
from engine.leitor import LeitorFicha
from engine.sheets import PlanilhaResultados

from ui.viewer import PDFViewer
from ui.form_panel import FormPanel
from ui.formulario_ficha import FormularioFicha

from area_omr import abrir_area_omr


class MainWindow(ctk.CTk):

    def __init__(self):

        super().__init__()

        # ======================================================
        # CONFIGURAÇÕES
        # ======================================================

        self.title(
            "SDIP - Sistema de Digitalização Inteligente de Pesquisas"
        )

        self.geometry(
            "1200x750"
        )

        self.minsize(
            1000,
            600
        )

        ctk.set_appearance_mode(
            "Light"
        )

        ctk.set_default_color_theme(
            "blue"
        )

        # ======================================================
        # GERENCIADOR DE FICHAS
        # ======================================================

        self.fichas_manager = FichasManager()

        # ======================================================
        # ESTADO
        # ======================================================

        self.pdf_path = None
        self.pdf_reader = None
        self.pagina_atual = 0
        self.total_paginas = 0

        # Ficha ativa
        self.ficha_ativa_id = None
        self.pdf_gerado_path = None
        self.mapa_gerado_path = None
        self.mapa_atual = None
        self.dados_ficha_atual = None
        self.resultado_omr = None

        # Ficha recém-gerada nesta sessão
        self.ficha_recente_id = None
        self.pdf_ficha_recente = None
        self.mapa_ficha_recente = None

        # Contexto da ficha mostrada em Visualizar ficha.
        # Pode ser a ficha ativa ou uma ficha recém-gerada que ainda
        # não foi tornada ativa.
        self.ficha_visualizada_id = None
        self.pdf_ficha_visualizada = None
        self.mapa_ficha_visualizada = None
        self.dados_ficha_visualizada = None
        self.modo_visualizacao = False

        # ID da ficha de produção que originou uma nova versão em edição.
        self.ficha_origem_nova_versao_id = None

        self.formulario_ficha = None
        self.popup_ficha = None

        # ======================================================
        # CARREGAR FICHA ATIVA
        # ======================================================

        self.carregar_ficha_ativa()

        # ======================================================
        # MENU
        # ======================================================

        self.criar_menu_principal()

    # ==========================================================
    # CARREGAR FICHA ATIVA
    # ==========================================================

    def carregar_ficha_ativa(self):

        ficha = (
            self.fichas_manager.carregar_ativa()
        )

        if not ficha:

            self.ficha_ativa_id = None
            self.pdf_gerado_path = None
            self.mapa_gerado_path = None
            self.dados_ficha_atual = None

            return

        self.ficha_ativa_id = (
            ficha["ficha_id"]
        )

        self.pdf_gerado_path = (
            ficha["pdf"]
        )

        self.mapa_gerado_path = (
            ficha["mapa"]
        )

        self.dados_ficha_atual = (
            self._copiar_dados_ficha(
                ficha["dados"]
            )
        )

    # ==========================================================
    # LIMPAR TELA
    # ==========================================================

    def limpar_tela(self):

        for widget in self.winfo_children():

            try:
                widget.pack_forget()
            except Exception:
                pass

            try:
                widget.grid_forget()
            except Exception:
                pass

            try:
                widget.place_forget()
            except Exception:
                pass

    # ==========================================================
    # MENU PRINCIPAL
    # ==========================================================

    def criar_menu_principal(self):

        if self.popup_ficha is not None:

            try:
                self.popup_ficha.destroy()
            except Exception:
                pass

            self.popup_ficha = None

        self.limpar_tela()

        self.menu_frame = ctk.CTkFrame(
            self
        )

        self.menu_frame.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=40
        )

        ctk.CTkLabel(
            self.menu_frame,
            text="SDIP",
            font=(
                "Segoe UI",
                42,
                "bold"
            )
        ).pack(
            pady=(90, 5)
        )

        ctk.CTkLabel(
            self.menu_frame,
            text=(
                "Sistema de Digitalização "
                "Inteligente de Pesquisas"
            ),
            font=(
                "Segoe UI",
                18
            )
        ).pack(
            pady=(0, 50)
        )

        # ======================================================
        # DIGITALIZAR
        # ======================================================

        ctk.CTkButton(
            self.menu_frame,
            text="Digitalizar ficha",
            width=320,
            height=55,
            font=(
                "Segoe UI",
                17,
                "bold"
            ),
            command=self.abrir_tela_digitalizacao
        ).pack(
            pady=10
        )

        # ======================================================
        # VISUALIZAR FICHA ATIVA
        # ======================================================

        self.visualizar_ficha_ativa_button = ctk.CTkButton(
            self.menu_frame,
            text="Visualizar ficha ativa",
            width=320,
            height=55,
            font=(
                "Segoe UI",
                17,
                "bold"
            ),
            command=self.visualizar_ficha_ativa
        )

        self.visualizar_ficha_ativa_button.pack(
            pady=10
        )

        if not self.pdf_gerado_path:

            self.visualizar_ficha_ativa_button.configure(
                state="disabled"
            )

        # ======================================================
        # CRIAR / EDITAR
        # ======================================================

        ctk.CTkButton(
            self.menu_frame,
            text="Criar / editar ficha",
            width=320,
            height=55,
            font=(
                "Segoe UI",
                17,
                "bold"
            ),
            command=self.abrir_tela_criacao
        ).pack(
            pady=10
        )

        # ======================================================
        # FICHA ATIVA
        # ======================================================

        if self.dados_ficha_atual:

            nome = self.dados_ficha_atual.get(
                "nome_pesquisa",
                "Sem nome"
            )

            texto = (
                "Ficha ativa: "
                f"{nome}"
            )

        else:

            texto = (
                "Nenhuma ficha ativa."
            )

        ctk.CTkLabel(
            self.menu_frame,
            text=texto,
            font=(
                "Segoe UI",
                11
            ),
            wraplength=500
        ).pack(
            pady=(40, 10)
        )

    # ==========================================================
    # VISUALIZAR FICHA ATIVA
    # ==========================================================

    def visualizar_ficha_ativa(self):

        if not self.pdf_gerado_path:

            messagebox.showwarning(
                "Ficha",
                "Nenhuma ficha ativa foi definida."
            )

            return

        if not os.path.isfile(
            self.pdf_gerado_path
        ):

            messagebox.showwarning(
                "Ficha",
                "O arquivo da ficha ativa não foi encontrado."
            )

            return

        ficha = self.fichas_manager.carregar_ficha(
            self.ficha_ativa_id
        )

        if not ficha:
            messagebox.showwarning(
                "Ficha",
                "Não foi possível carregar os dados da ficha ativa."
            )
            return

        self.ficha_visualizada_id = ficha["ficha_id"]
        self.pdf_ficha_visualizada = ficha["pdf"]
        self.mapa_ficha_visualizada = ficha["mapa"]
        self.dados_ficha_visualizada = self._copiar_dados_ficha(
            ficha["dados"]
        )

        # Abre a tela em modo SOMENTE VISUALIZAÇÃO.
        self.abrir_tela_digitalizacao(
            modo_visualizacao=True,
            dados_ficha=self.dados_ficha_visualizada,
            pdf_path=self.pdf_ficha_visualizada,
            mapa_path=self.mapa_ficha_visualizada,
            ficha_id=self.ficha_visualizada_id
        )

        self.carregar_pdf(
            self.pdf_ficha_visualizada
        )

        self.status.configure(
            text="Status: ficha ativa carregada."
        )

    # ==========================================================
    # VISUALIZAR ÁREA OMR
    # ==========================================================

    def visualizar_area_omr(self):

        try:

            if self.modo_visualizacao:
                abrir_area_omr(
                    self,
                    caminho_pdf=self.pdf_ficha_visualizada,
                    caminho_mapa=self.mapa_ficha_visualizada
                )
            else:
                abrir_area_omr(
                    self
                )

        except Exception as erro:

            messagebox.showerror(
                "Área OMR",
                (
                    "Não foi possível abrir a visualização "
                    "da área de marcação.\n\n"
                    f"{erro}"
                )
            )

    # ==========================================================
    # TELA DE DIGITALIZAÇÃO
    #
    # modo_visualizacao=False
    #     Tela completa de digitalização.
    #
    # modo_visualizacao=True
    #     Tela simplificada para visualizar a ficha ativa.
    # ==========================================================

    def abrir_tela_digitalizacao(
        self,
        modo_visualizacao=False,
        dados_ficha=None,
        pdf_path=None,
        mapa_path=None,
        ficha_id=None
    ):

        self.modo_visualizacao = modo_visualizacao

        if modo_visualizacao:
            self.ficha_visualizada_id = ficha_id or self.ficha_ativa_id
            self.pdf_ficha_visualizada = (
                pdf_path or self.pdf_gerado_path
            )
            self.mapa_ficha_visualizada = (
                mapa_path or self.mapa_gerado_path
            )
            self.dados_ficha_visualizada = (
                self._copiar_dados_ficha(
                    dados_ficha
                    or self.dados_ficha_atual
                    or {}
                )
            )
        else:
            self.ficha_visualizada_id = None
            self.pdf_ficha_visualizada = None
            self.mapa_ficha_visualizada = None
            self.dados_ficha_visualizada = None

        self.limpar_tela()

        self.digitalizacao_frame = ctk.CTkFrame(
            self
        )

        self.digitalizacao_frame.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        # ======================================================
        # CABEÇALHO
        # ======================================================

        top = ctk.CTkFrame(
            self.digitalizacao_frame
        )

        top.pack(
            fill="x",
            padx=8,
            pady=(8, 4)
        )

        ctk.CTkButton(
            top,
            text="← Menu",
            width=90,
            command=self.criar_menu_principal
        ).pack(
            side="left",
            padx=8,
            pady=6
        )

        titulo = (
            "Visualizar ficha ativa"
            if modo_visualizacao
            else
            "Digitalizar ficha"
        )

        ctk.CTkLabel(
            top,
            text=titulo,
            font=(
                "Segoe UI",
                20,
                "bold"
            )
        ).pack(
            side="left",
            padx=12
        )

        # ======================================================
        # CORPO
        # ======================================================

        corpo = ctk.CTkFrame(
            self.digitalizacao_frame
        )

        corpo.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=4
        )

        # ======================================================
        # PAINÉIS REDIMENSIONÁVEIS
        #
        # PDF e formulário ficam lado a lado.
        # O usuário pode arrastar o divisor.
        # Posição inicial aproximada: 40% / 60%.
        # ======================================================

        paned = ttk.Panedwindow(
            corpo,
            orient="horizontal"
        )

        paned.pack(
            fill="both",
            expand=True,
            padx=6,
            pady=6
        )

        # ======================================================
        # VISUALIZADOR PDF
        # ======================================================

        pdf_frame = ctk.CTkFrame(
            paned
        )

        self.viewer = PDFViewer(
            pdf_frame
        )

        self.viewer.pack(
            expand=True,
            fill="both",
            padx=8,
            pady=8
        )

        # ======================================================
        # PAINEL DIREITO
        # ======================================================

        side_panel = ctk.CTkFrame(
            paned
        )

        paned.add(
            pdf_frame,
            weight=2
        )

        paned.add(
            side_panel,
            weight=3
        )

        # Posição inicial do divisor em aproximadamente 40%.
        def posicionar_divisor_inicial():

            largura = paned.winfo_width()

            if largura > 1:

                paned.sashpos(
                    0,
                    int(largura * 0.40)
                )

        self.after_idle(
            posicionar_divisor_inicial
        )

        # ======================================================
        # AÇÕES
        #
        # Os botões ficam em duas colunas para economizar altura
        # e liberar mais espaço para o formulário em notebooks.
        # ======================================================

        ctk.CTkLabel(
            side_panel,
            text="Ações",
            font=(
                "Segoe UI",
                17,
                "bold"
            )
        ).pack(
            pady=(8, 4)
        )

        actions_frame = ctk.CTkFrame(
            side_panel,
            fg_color="transparent"
        )

        actions_frame.pack(
            fill="x",
            padx=10,
            pady=(0, 4)
        )

        actions_frame.grid_columnconfigure(
            0,
            weight=1
        )

        actions_frame.grid_columnconfigure(
            1,
            weight=1
        )

        # ======================================================
        # MODO VISUALIZAÇÃO
        # ======================================================

        if modo_visualizacao:

            ctk.CTkButton(
                actions_frame,
                text="Onde devo marcar?",
                command=self.visualizar_area_omr
            ).grid(
                row=0,
                column=0,
                sticky="ew",
                padx=4,
                pady=4
            )

            self.planilha_button = ctk.CTkButton(
                actions_frame,
                text="Gerar planilha e colocar em produção",
                command=self.gerar_planilha_da_ficha
            )

            self.planilha_button.grid(
                row=0,
                column=1,
                sticky="ew",
                padx=4,
                pady=4
            )

            dados_visualizados = (
                self.dados_ficha_visualizada
                or self.dados_ficha_atual
                or {}
            )

            caminho_planilha = dados_visualizados.get(
                "planilha_resultados_path"
            )

            if caminho_planilha and os.path.isfile(caminho_planilha):
                self.planilha_button.configure(
                    text="Planilha da pesquisa já configurada",
                    state="disabled"
                )

            ctk.CTkButton(
                actions_frame,
                text="Salvar PDF localmente",
                command=self.exportar_pdf_visualizacao
            ).grid(
                row=1,
                column=0,
                columnspan=2,
                sticky="ew",
                padx=4,
                pady=4
            )

        else:

            # ==================================================
            # MODO DIGITALIZAÇÃO NORMAL
            # ==================================================

            ctk.CTkButton(
                actions_frame,
                text="Selecionar ficha PDF",
                command=self.selecionar_pdf
            ).grid(
                row=0,
                column=0,
                sticky="ew",
                padx=4,
                pady=4
            )

            self.open_generated_button = ctk.CTkButton(
                actions_frame,
                text="Abrir ficha ativa",
                command=self.abrir_pdf_gerado
            )

            self.open_generated_button.grid(
                row=0,
                column=1,
                sticky="ew",
                padx=4,
                pady=4
            )

            if not self.pdf_gerado_path:

                self.open_generated_button.configure(
                    state="disabled"
                )

            self.area_omr_button = ctk.CTkButton(
                actions_frame,
                text="Onde devo marcar?",
                command=self.visualizar_area_omr
            )

            self.area_omr_button.grid(
                row=1,
                column=0,
                sticky="ew",
                padx=4,
                pady=4
            )

            if not self.pdf_gerado_path:

                self.area_omr_button.configure(
                    state="disabled"
                )

            self.process_omr_button = ctk.CTkButton(
                actions_frame,
                text="Ler ficha (OMR)",
                command=self.processar_omr
            )

            self.process_omr_button.grid(
                row=1,
                column=1,
                sticky="ew",
                padx=4,
                pady=4
            )

            self.process_omr_button.configure(
                state="disabled"
            )

            self.export_pdf_button = ctk.CTkButton(
                actions_frame,
                text="Salvar PDF localmente",
                command=self.exportar_pdf_ativo
            )

            self.export_pdf_button.grid(
                row=2,
                column=0,
                columnspan=2,
                sticky="ew",
                padx=4,
                pady=4
            )

            if not self.pdf_gerado_path:

                self.export_pdf_button.configure(
                    state="disabled"
                )

        # ======================================================
        # AÇÃO PRINCIPAL — SALVAR RESULTADO
        #
        # Fica fora do FormPanel e acima das informações do PDF
        # para permanecer sempre acessível em telas menores.
        # ======================================================

        if not modo_visualizacao:

            self.save_result_button = ctk.CTkButton(
                side_panel,
                text="Salvar resultado",
                height=42,
                font=(
                    "Segoe UI",
                    15,
                    "bold"
                ),
                command=self.salvar_resultado_atual
            )

            self.save_result_button.pack(
                fill="x",
                padx=14,
                pady=(4, 6)
            )

        # ======================================================
        # INFORMAÇÕES DO PDF
        # ======================================================

        info_frame = ctk.CTkFrame(
            side_panel,
            fg_color="transparent"
        )

        info_frame.pack(
            fill="x",
            padx=10,
            pady=(2, 2)
        )

        self.file_name = ctk.CTkLabel(
            info_frame,
            text="Nenhum PDF selecionado",
            wraplength=500
        )

        self.file_name.pack(
            fill="x",
            pady=(2, 0)
        )

        self.page_label = ctk.CTkLabel(
            info_frame,
            text="Página 0 de 0"
        )

        self.page_label.pack(
            fill="x",
            pady=(0, 2)
        )

        # ======================================================
        # NAVEGAÇÃO DE PÁGINAS
        # ======================================================

        nav_frame = ctk.CTkFrame(
            side_panel,
            fg_color="transparent"
        )

        nav_frame.pack(
            fill="x",
            padx=10,
            pady=(2, 4)
        )

        nav_frame.grid_columnconfigure(
            0,
            weight=1
        )

        nav_frame.grid_columnconfigure(
            1,
            weight=1
        )

        ctk.CTkButton(
            nav_frame,
            text="← Página anterior",
            command=self.pagina_anterior
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(4, 2),
            pady=2
        )

        ctk.CTkButton(
            nav_frame,
            text="Próxima página →",
            command=self.proxima_pagina
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(2, 4),
            pady=2
        )

        # ======================================================
        # FORMULÁRIO
        #
        # O FormPanel contém apenas os campos e seu scroll.
        # A ação principal "Salvar resultado" fica acima, fora do
        # formulário, para permanecer acessível em telas menores.
        # ======================================================

        if not modo_visualizacao:

            self.form_panel = FormPanel(
                side_panel,
                salvar_callback=self.salvar_pesquisa
            )

            self.form_panel.pack(
                fill="both",
                expand=True,
                padx=10,
                pady=(4, 6)
            )

        # ======================================================
        # STATUS
        # ======================================================

        status_inicial = (
            "Status: visualizando ficha ativa."
            if modo_visualizacao
            else
            "Status: aguardando seleção."
        )

        self.status = ctk.CTkLabel(
            self.digitalizacao_frame,
            text=status_inicial
        )

        self.status.pack(
            fill="x",
            padx=10,
            pady=(0, 4)
        )

        # ======================================================
        # MAPA
        # ======================================================

        if not modo_visualizacao:

            self.carregar_mapa_atual()

    # ==========================================================
    # TELA CRIAR / EDITAR
    # ==========================================================

    def abrir_tela_criacao(self):

        self.limpar_tela()

        self.criacao_frame = ctk.CTkFrame(
            self
        )

        self.criacao_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        top = ctk.CTkFrame(
            self.criacao_frame
        )

        top.pack(
            fill="x",
            padx=5,
            pady=5
        )

        ctk.CTkButton(
            top,
            text="← Menu",
            width=100,
            command=self.criar_menu_principal
        ).pack(
            side="left",
            padx=10,
            pady=10
        )

        ctk.CTkLabel(
            top,
            text="Criar / editar ficha",
            font=(
                "Segoe UI",
                22,
                "bold"
            )
        ).pack(
            side="left",
            padx=20
        )

        if self.dados_ficha_atual:

            ctk.CTkButton(
                top,
                text="Editar ficha ativa",
                command=self.editar_ficha
            ).pack(
                side="right",
                padx=10,
                pady=10
            )

        ctk.CTkButton(
            top,
            text="Nova ficha",
            command=self.abrir_nova_ficha
        ).pack(
            side="right",
            padx=10,
            pady=10
        )

        # ======================================================
        # CONTEÚDO
        # ======================================================

        conteudo = ctk.CTkFrame(
            self.criacao_frame
        )

        conteudo.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        if self.dados_ficha_atual:

            nome = self.dados_ficha_atual.get(
                "nome_pesquisa",
                "Sem nome"
            )

            status = self.dados_ficha_atual.get(
                "status_producao",
                FichasManager.STATUS_RASCUNHO
            )
            versao = self.dados_ficha_atual.get("versao", 1)

            planilha = self.dados_ficha_atual.get(
                "planilha_resultados_path"
            )

            if planilha:
                detalhe_planilha = f"\n\nPlanilha: {planilha}"
            else:
                detalhe_planilha = ""

            mensagem = (
                "Ficha ativa:\n\n"
                f"{nome}\n\n"
                f"Status: {status}\n"
                f"Versão: {versao}"
                f"{detalhe_planilha}\n\n"
                "Esta é a ficha ativa no momento."
            )

        else:

            mensagem = (
                "Nenhuma ficha ativa.\n\n"
                "Crie uma nova ficha para começar."
            )

        ctk.CTkLabel(
            conteudo,
            text=mensagem,
            font=(
                "Segoe UI",
                16
            ),
            justify="center",
            wraplength=600
        ).pack(
            pady=(100, 20)
        )

        if self.dados_ficha_atual:

            ctk.CTkButton(
                conteudo,
                text="Editar ficha ativa",
                width=300,
                height=45,
                command=self.editar_ficha
            ).pack(
                pady=10
            )

        ctk.CTkButton(
            conteudo,
            text="Criar nova ficha",
            width=300,
            height=45,
            command=self.abrir_nova_ficha
        ).pack(
            pady=10
        )

    # ==========================================================
    # NOVA FICHA
    # ==========================================================

    def abrir_nova_ficha(self):

        self.limpar_tela()

        self.formulario_ficha = FormularioFicha(
            self,
            voltar_callback=self.voltar_da_ficha,
            gerar_callback=self.receber_dados_ficha
        )

        self.formulario_ficha.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # ==========================================================
    # EDITAR
    # ==========================================================

    def editar_ficha(self):

        if not self.dados_ficha_atual:

            messagebox.showwarning(
                "Editar ficha",
                "Nenhuma ficha ativa disponível para edição."
            )

            return

        status = self.dados_ficha_atual.get(
            "status_producao",
            FichasManager.STATUS_RASCUNHO
        )

        self.ficha_origem_nova_versao_id = None

        if status == FichasManager.STATUS_PRODUCAO:
            resposta = messagebox.askyesno(
                "Ficha em produção",
                (
                    "Esta ficha já está em produção e está vinculada a uma planilha.\n\n"
                    "Alterações estruturais não devem modificar a pesquisa já em andamento.\n\n"
                    "Deseja criar uma nova versão desta ficha?"
                )
            )

            if not resposta:
                return

            self.ficha_origem_nova_versao_id = self.ficha_ativa_id

        self.limpar_tela()

        self.formulario_ficha = FormularioFicha(
            self,
            voltar_callback=self.voltar_da_ficha,
            gerar_callback=self.receber_dados_ficha,
            dados_iniciais=self.dados_ficha_atual
        )

        self.formulario_ficha.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # ==========================================================
    # VOLTAR DO EDITOR
    # ==========================================================

    def voltar_da_ficha(self):

        if self.formulario_ficha is not None:

            self.formulario_ficha.destroy()
            self.formulario_ficha = None

        self.abrir_tela_criacao()

    # ==========================================================
    # GERAR FICHA
    # ==========================================================

    def receber_dados_ficha(
        self,
        dados
    ):

        try:

            # --------------------------------------------------
            # DIRETÓRIO TEMPORÁRIO EXCLUSIVO
            # --------------------------------------------------

            import tempfile

            caminho_trabalho = tempfile.mkdtemp(
                prefix="sdip_geracao_"
            )

            caminho_imagem = os.path.join(
                caminho_trabalho,
                "ficha.png"
            )

            caminho_pdf = os.path.join(
                caminho_trabalho,
                "ficha.pdf"
            )

            caminho_mapa = os.path.join(
                caminho_trabalho,
                "mapa_omr.json"
            )

            # --------------------------------------------------
            # GERADOR
            # --------------------------------------------------

            ficha = GeradorFicha(
                nome_pesquisa=(
                    dados["nome_pesquisa"]
                ),
                titulo=dados.get(
                    "titulo",
                    ""
                ),
                logo_path=dados.get(
                    "logo_path"
                ),
                campos_identificacao=(
                    dados.get(
                        "campos_identificacao",
                        []
                    )
                ),
                tamanho_fonte=dados.get(
                    "tamanho_fonte",
                    GeradorFicha.TAMANHO_FONTE_PADRAO
                )
            )

            elementos = dados.get(
                "elementos"
            )

            # --------------------------------------------------
            # FORMATO ANTIGO
            # --------------------------------------------------

            if elementos is None:

                for pergunta in dados.get(
                    "perguntas",
                    []
                ):

                    ficha.adicionar_pergunta(
                        texto=(
                            pergunta["texto"]
                        ),
                        tipo_resposta=(
                            pergunta[
                                "tipo_resposta"
                            ]
                        ),
                        opcoes=(
                            pergunta.get(
                                "opcoes",
                                []
                            )
                        ),
                        numero=(
                            pergunta.get(
                                "numero"
                            )
                        )
                    )

            # --------------------------------------------------
            # FORMATO ATUAL
            # --------------------------------------------------

            else:

                for elemento in elementos:

                    if elemento["tipo"] == "secao":

                        ficha.adicionar_secao(
                            texto=(
                                elemento["texto"]
                            ),
                            numero=(
                                elemento["numero"]
                            )
                        )

                    elif elemento["tipo"] == "pergunta":

                        ficha.adicionar_pergunta(
                            texto=(
                                elemento["texto"]
                            ),
                            tipo_resposta=(
                                elemento[
                                    "tipo_resposta"
                                ]
                            ),
                            opcoes=(
                                elemento.get(
                                    "opcoes",
                                    []
                                )
                            ),
                            numero=(
                                elemento["numero"]
                            )
                        )

            # --------------------------------------------------
            # GERAÇÃO
            # --------------------------------------------------

            paginas = ficha.gerar_imagem(
                caminho_imagem
            )

            if not paginas:

                raise RuntimeError(
                    "O gerador não produziu nenhuma página."
                )

            ficha.gerar_mapa_omr(
                caminho_mapa
            )

            self.gerar_pdf(
                paginas,
                caminho_pdf
            )

            # --------------------------------------------------
            # METADADOS DE PRODUÇÃO / VERSÃO
            # --------------------------------------------------

            if self.ficha_origem_nova_versao_id:
                origem = self.fichas_manager.carregar_ficha(
                    self.ficha_origem_nova_versao_id
                )

                if not origem:
                    raise FileNotFoundError(
                        "A ficha de produção que originou esta versão não foi encontrada."
                    )

                dados["pesquisa_id"] = origem["dados"].get(
                    "pesquisa_id",
                    self.ficha_origem_nova_versao_id
                )
                dados["versao"] = int(
                    origem["dados"].get("versao", 1)
                    or 1
                ) + 1
                dados["versao_anterior_id"] = (
                    self.ficha_origem_nova_versao_id
                )
                dados["status_producao"] = (
                    FichasManager.STATUS_RASCUNHO
                )
                dados["planilha_resultados_path"] = None
                dados["planilha_cabecalhos"] = []
            else:
                dados["status_producao"] = (
                    FichasManager.STATUS_RASCUNHO
                )
                dados["versao"] = 1
                dados["planilha_resultados_path"] = None
                dados["planilha_cabecalhos"] = []

            # --------------------------------------------------
            # SALVAR PERMANENTEMENTE
            # --------------------------------------------------

            ficha_salva = (
                self.fichas_manager.salvar_ficha(
                    dados,
                    caminho_pdf,
                    caminho_mapa
                )
            )

            self.ficha_origem_nova_versao_id = None

            self.ficha_recente_id = (
                ficha_salva["ficha_id"]
            )

            self.pdf_ficha_recente = (
                ficha_salva["pdf"]
            )

            self.mapa_ficha_recente = (
                ficha_salva["mapa"]
            )

            # --------------------------------------------------
            # SE NÃO HÁ FICHA ATIVA
            # --------------------------------------------------

            tornar_ativa = True

            if self.ficha_ativa_id:

                tornar_ativa = messagebox.askyesno(
                    "Nova ficha",
                    (
                        "A ficha foi salva permanentemente.\n\n"
                        "Já existe uma ficha ativa no sistema.\n\n"
                        "Deseja tornar esta nova ficha a "
                        "ficha ativa?"
                    )
                )

            if tornar_ativa:

                self.fichas_manager.definir_ativa(
                    ficha_salva["ficha_id"]
                )

                self.carregar_ficha_ativa()

            # --------------------------------------------------
            # SAIR DO EDITOR
            # --------------------------------------------------

            if self.formulario_ficha is not None:

                self.formulario_ficha.destroy()
                self.formulario_ficha = None

            self.abrir_tela_criacao()

            # --------------------------------------------------
            # CONTADORES
            # --------------------------------------------------

            quantidade_perguntas = sum(
                1
                for elemento in dados.get(
                    "elementos",
                    dados.get(
                        "perguntas",
                        []
                    )
                )
                if elemento.get(
                    "tipo",
                    "pergunta"
                ) == "pergunta"
            )

            quantidade_abertas = len(
                ficha.perguntas_abertas
            )

            # --------------------------------------------------
            # POPUP
            # --------------------------------------------------

            self.mostrar_popup_ficha_gerada(
                quantidade_perguntas,
                len(paginas),
                len(ficha.coordenadas_omr),
                quantidade_abertas,
                tornar_ativa
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro ao gerar ficha",
                (
                    "Não foi possível gerar a ficha.\n\n"
                    f"{erro}"
                )
            )

            print(
                "=" * 70
            )

            print(
                "ERRO AO GERAR FICHA"
            )

            print(
                "=" * 70
            )

            print(
                repr(erro)
            )

            self.ficha_origem_nova_versao_id = None

            print(
                "=" * 70
            )

    # ==========================================================
    # POPUP
    # ==========================================================

    def mostrar_popup_ficha_gerada(
        self,
        quantidade_perguntas,
        quantidade_paginas,
        quantidade_caixas,
        quantidade_abertas,
        ficha_ativa
    ):

        if self.popup_ficha is not None:

            try:
                self.popup_ficha.destroy()
            except Exception:
                pass

        self.popup_ficha = ctk.CTkToplevel(
            self
        )

        self.popup_ficha.title(
            "Ficha gerada"
        )

        self.popup_ficha.geometry(
            "460x480"
        )

        self.popup_ficha.resizable(
            False,
            False
        )

        self.popup_ficha.transient(
            self
        )

        self.popup_ficha.grab_set()

        ctk.CTkLabel(
            self.popup_ficha,
            text="Ficha gerada com sucesso!",
            font=(
                "Segoe UI",
                22,
                "bold"
            )
        ).pack(
            pady=(30, 15)
        )

        status_ativa = (
            "Esta ficha agora é a ficha ativa."
            if ficha_ativa
            else
            "A ficha foi salva, mas a ficha ativa anterior foi mantida."
        )

        ctk.CTkLabel(
            self.popup_ficha,
            text=(
                f"Perguntas: {quantidade_perguntas}\n"
                f"Páginas: {quantidade_paginas}\n"
                f"Caixas OMR: {quantidade_caixas}\n"
                f"Perguntas abertas: {quantidade_abertas}\n\n"
                f"{status_ativa}"
            ),
            font=(
                "Segoe UI",
                13
            ),
            justify="center",
            wraplength=380
        ).pack(
            pady=(0, 20)
        )

        ctk.CTkButton(
            self.popup_ficha,
            text="Visualizar ficha gerada",
            width=300,
            height=42,
            command=self.popup_visualizar_ficha
        ).pack(
            pady=5
        )

        ctk.CTkButton(
            self.popup_ficha,
            text="Salvar PDF localmente",
            width=300,
            height=42,
            command=self.exportar_pdf_recente
        ).pack(
            pady=5
        )

        ctk.CTkButton(
            self.popup_ficha,
            text="Editar ficha gerada",
            width=300,
            height=42,
            command=self.popup_editar_ficha_recente
        ).pack(
            pady=5
        )

        ctk.CTkButton(
            self.popup_ficha,
            text="Voltar ao menu",
            width=300,
            height=42,
            command=self.popup_voltar_menu
        ).pack(
            pady=5
        )

        self.popup_ficha.update_idletasks()

        largura = 460
        altura = 480

        x = (
            self.winfo_rootx()
            + (
                self.winfo_width()
                - largura
            ) // 2
        )

        y = (
            self.winfo_rooty()
            + (
                self.winfo_height()
                - altura
            ) // 2
        )

        self.popup_ficha.geometry(
            f"{largura}x{altura}+{x}+{y}"
        )

    # ==========================================================
    # POPUP -> VISUALIZAR FICHA RECENTE
    # ==========================================================

    def popup_visualizar_ficha(self):

        if self.popup_ficha is not None:

            self.popup_ficha.destroy()
            self.popup_ficha = None

        ficha = self.fichas_manager.carregar_ficha(
            self.ficha_recente_id
        )

        if not ficha:
            messagebox.showwarning(
                "Ficha",
                "A ficha recém-gerada não foi encontrada."
            )
            return

        self.ficha_visualizada_id = ficha["ficha_id"]
        self.pdf_ficha_visualizada = ficha["pdf"]
        self.mapa_ficha_visualizada = ficha["mapa"]
        self.dados_ficha_visualizada = self._copiar_dados_ficha(
            ficha["dados"]
        )

        self.abrir_tela_digitalizacao(
            modo_visualizacao=True,
            dados_ficha=self.dados_ficha_visualizada,
            pdf_path=self.pdf_ficha_visualizada,
            mapa_path=self.mapa_ficha_visualizada,
            ficha_id=self.ficha_visualizada_id
        )

        self.carregar_pdf(
            self.pdf_ficha_visualizada
        )

        self.status.configure(
            text="Status: ficha recém-gerada carregada para revisão."
        )

    # ==========================================================
    # EXPORTAR PDF
    # ==========================================================

    def exportar_pdf(
        self,
        caminho_pdf
    ):

        if not caminho_pdf:

            messagebox.showwarning(
                "Exportar PDF",
                "Nenhum PDF disponível para exportação."
            )

            return

        if not os.path.isfile(
            caminho_pdf
        ):

            messagebox.showwarning(
                "Exportar PDF",
                "O arquivo PDF não foi encontrado."
            )

            return

        nome_sugerido = os.path.basename(
            caminho_pdf
        )

        destino = filedialog.asksaveasfilename(
            title="Salvar PDF",
            defaultextension=".pdf",
            initialfile=nome_sugerido,
            filetypes=[
                (
                    "Arquivo PDF",
                    "*.pdf"
                ),
                (
                    "Todos os arquivos",
                    "*.*"
                )
            ]
        )

        if not destino:
            return

        try:

            caminho_origem = os.path.abspath(
                caminho_pdf
            )

            caminho_destino = os.path.abspath(
                destino
            )

            if caminho_origem == caminho_destino:

                messagebox.showinfo(
                    "Exportar PDF",
                    "O PDF já está salvo neste local."
                )

                return

            shutil.copy2(
                caminho_pdf,
                destino
            )

            messagebox.showinfo(
                "Exportar PDF",
                (
                    "PDF salvo com sucesso!\n\n"
                    f"{destino}"
                )
            )

        except Exception as erro:

            messagebox.showerror(
                "Exportar PDF",
                (
                    "Não foi possível salvar o PDF.\n\n"
                    f"{erro}"
                )
            )

    # ==========================================================
    # GERAR PLANILHA DA FICHA
    # ==========================================================

    def gerar_planilha_da_ficha(self):

        # Em modo de visualização, a planilha pertence à ficha exibida.
        # No restante da aplicação, usamos a ficha ativa.
        ficha_id = (
            self.ficha_visualizada_id
            if self.modo_visualizacao and self.ficha_visualizada_id
            else self.ficha_ativa_id
        )

        if not ficha_id:
            messagebox.showwarning(
                "Planilha",
                "Nenhuma ficha disponível para gerar a planilha."
            )
            return

        ficha = self.fichas_manager.carregar_ficha(ficha_id)
        if not ficha:
            messagebox.showwarning(
                "Planilha",
                "Não foi possível carregar a ficha selecionada."
            )
            return

        dados_ficha = self._copiar_dados_ficha(
            ficha["dados"]
        )

        caminho_existente = dados_ficha.get(
            "planilha_resultados_path"
        )

        if caminho_existente:
            if os.path.isfile(caminho_existente):
                messagebox.showinfo(
                    "Planilha",
                    "A planilha desta ficha já está configurada.\n\n"
                    f"{caminho_existente}"
                )
                return

            resposta = messagebox.askyesno(
                "Planilha",
                "A planilha configurada anteriormente não foi encontrada.\n\n"
                "Deseja escolher um novo local?"
            )
            if not resposta:
                return

        nome_pesquisa = str(
            dados_ficha.get(
                "nome_pesquisa",
                "resultados"
            )
        ).strip() or "resultados"

        destino = filedialog.asksaveasfilename(
            title="Salvar planilha da pesquisa",
            defaultextension=".xlsx",
            initialfile=(
                f"{PlanilhaResultados._nome_seguro(nome_pesquisa)} - resultados.xlsx"
            ),
            filetypes=[
                (
                    "Planilha Excel",
                    "*.xlsx"
                )
            ]
        )

        if not destino:
            return

        try:
            cabecalhos = PlanilhaResultados.cabecalhos_da_ficha(
                dados_ficha
            )

            caminho_salvo = PlanilhaResultados.criar_planilha(
                destino,
                dados_ficha
            )

            self.fichas_manager.salvar_caminho_planilha(
                ficha_id,
                caminho_salvo,
                cabecalhos=cabecalhos
            )

            if self.ficha_ativa_id == ficha_id:
                self.dados_ficha_atual = self._copiar_dados_ficha(
                    self.fichas_manager.carregar_ficha(ficha_id)["dados"]
                )

            if self.ficha_visualizada_id == ficha_id:
                self.dados_ficha_visualizada = self._copiar_dados_ficha(
                    self.fichas_manager.carregar_ficha(ficha_id)["dados"]
                )

            if hasattr(self, "planilha_button"):
                self.planilha_button.configure(
                    text="Planilha da pesquisa já configurada",
                    state="disabled"
                )

            if hasattr(self, "status"):
                self.status.configure(
                    text="Status: ficha colocada em produção."
                )

            versao = dados_ficha.get("versao", 1)

            messagebox.showinfo(
                "Pesquisa em produção",
                "A ficha foi colocada em produção e a planilha foi criada.\n\n"
                "A linha 1 da planilha representa a estrutura da ficha.\n"
                "Cada nova ficha lida será adicionada como uma nova linha.\n\n"
                f"Versão: {versao}\n"
                f"Colunas: {len(cabecalhos)}\n"
                f"Local: {caminho_salvo}"
            )

        except Exception as erro:
            messagebox.showerror(
                "Erro ao criar planilha",
                "Não foi possível criar a planilha.\n\n"
                f"{erro}"
            )

            print(
                "Erro ao criar planilha:",
                repr(erro)
            )

    # ==========================================================
    # EXPORTAR PDF ATIVO
    # ==========================================================

    def exportar_pdf_ativo(self):

        self.exportar_pdf(
            self.pdf_gerado_path
        )

    # ==========================================================
    # EXPORTAR PDF RECENTE
    # ==========================================================

    def exportar_pdf_recente(self):

        self.exportar_pdf(
            self.pdf_ficha_recente
        )

    # ==========================================================
    # EXPORTAR PDF DA FICHA VISUALIZADA
    # ==========================================================

    def exportar_pdf_visualizacao(self):

        caminho = (
            self.pdf_ficha_visualizada
            or self.pdf_gerado_path
        )

        self.exportar_pdf(
            caminho
        )

    # ==========================================================
    # POPUP -> EDITAR FICHA RECENTE
    # ==========================================================

    def popup_editar_ficha_recente(self):

        if self.popup_ficha is not None:

            self.popup_ficha.destroy()
            self.popup_ficha = None

        fichas = (
            self.fichas_manager.listar_fichas()
        )

        ficha = None

        for item in fichas:

            if (
                item["ficha_id"]
                == self.ficha_recente_id
            ):

                ficha = item
                break

        if not ficha:

            messagebox.showwarning(
                "Ficha",
                "A ficha recém-gerada não foi encontrada."
            )

            return

        self.ficha_origem_nova_versao_id = None

        status = ficha["dados"].get(
            "status_producao",
            FichasManager.STATUS_RASCUNHO
        )

        if status == FichasManager.STATUS_PRODUCAO:
            resposta = messagebox.askyesno(
                "Ficha em produção",
                (
                    "Esta ficha já está em produção.\n\n"
                    "Deseja criar uma nova versão para editá-la?"
                )
            )

            if not resposta:
                return

            self.ficha_origem_nova_versao_id = (
                ficha["ficha_id"]
            )

        self.limpar_tela()

        self.formulario_ficha = FormularioFicha(
            self,
            voltar_callback=self.voltar_da_ficha,
            gerar_callback=self.receber_dados_ficha,
            dados_iniciais=(
                ficha["dados"]
            )
        )

        self.formulario_ficha.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # ==========================================================
    # POPUP -> MENU
    # ==========================================================

    def popup_voltar_menu(self):

        if self.popup_ficha is not None:

            self.popup_ficha.destroy()
            self.popup_ficha = None

        self.criar_menu_principal()

    # ==========================================================
    # COPIAR DADOS DA FICHA
    # ==========================================================

    @staticmethod
    def _copiar_dados_ficha(
        dados
    ):

        elementos_originais = dados.get(
            "elementos",
            dados.get(
                "perguntas",
                []
            )
        )

        elementos = []

        for elemento in elementos_originais:

            copia = dict(
                elemento
            )

            if "opcoes" in elemento:

                copia["opcoes"] = list(
                    elemento.get(
                        "opcoes",
                        []
                    )
                )

            elementos.append(
                copia
            )

        campos_identificacao = []

        for campo in dados.get(
            "campos_identificacao",
            []
        ):

            campos_identificacao.append(
                dict(campo)
            )

        return {
            "nome_pesquisa": dados.get(
                "nome_pesquisa",
                ""
            ),
            "titulo": dados.get(
                "titulo",
                ""
            ),
            "logo_path": dados.get(
                "logo_path"
            ),
            "planilha_resultados_path": dados.get(
                "planilha_resultados_path"
            ),
            "planilha_cabecalhos": list(
                dados.get("planilha_cabecalhos", [])
            ),
            "status_producao": dados.get(
                "status_producao",
                FichasManager.STATUS_RASCUNHO
            ),
            "pesquisa_id": dados.get(
                "pesquisa_id"
            ),
            "versao": dados.get(
                "versao",
                1
            ),
            "versao_anterior_id": dados.get(
                "versao_anterior_id"
            ),
            "tamanho_fonte": dados.get(
                "tamanho_fonte",
                GeradorFicha.TAMANHO_FONTE_PADRAO
            ),
            "campos_identificacao": (
                campos_identificacao
            ),
            "elementos": elementos
        }

    # ==========================================================
    # CARREGAR MAPA
    # ==========================================================

    def carregar_mapa_atual(
        self
    ):

        if not hasattr(
            self,
            "form_panel"
        ):

            return

        caminho = self.mapa_gerado_path

        if not caminho:

            self.mapa_atual = None

            self.form_panel.configurar_campos_identificacao(
                []
            )

            self.form_panel.configurar_perguntas_abertas(
                []
            )

            return

        if not os.path.exists(
            caminho
        ):

            self.mapa_atual = None

            self.form_panel.configurar_campos_identificacao(
                []
            )

            self.form_panel.configurar_perguntas_abertas(
                []
            )

            return

        try:

            with open(
                caminho,
                "r",
                encoding="utf-8"
            ) as arquivo:

                mapa = json.load(
                    arquivo
                )

            self.mapa_atual = mapa

            campos_identificacao = mapa.get(
                "campos_identificacao",
                []
            )

            perguntas_abertas = mapa.get(
                "perguntas_abertas",
                []
            )

            self.form_panel.configurar_campos_identificacao(
                campos_identificacao
            )

            self.form_panel.configurar_perguntas_abertas(
                perguntas_abertas
            )

        except Exception as erro:

            print(
                "Erro ao carregar mapa:"
            )

            print(
                repr(erro)
            )

            self.mapa_atual = None

            self.form_panel.configurar_campos_identificacao(
                []
            )

            self.form_panel.configurar_perguntas_abertas(
                []
            )

    # ==========================================================
    # GERAR PDF
    # ==========================================================

    @staticmethod
    def gerar_pdf(
        paginas,
        caminho_pdf
    ):

        imagens = []

        for caminho in paginas:

            imagem = Image.open(
                caminho
            ).convert(
                "RGB"
            )

            imagens.append(
                imagem
            )

        if not imagens:

            raise RuntimeError(
                "Nenhuma imagem disponível para gerar o PDF."
            )

        primeira = imagens[0]
        restantes = imagens[1:]

        primeira.save(
            caminho_pdf,
            "PDF",
            resolution=144.0,
            save_all=True,
            append_images=restantes
        )

        for imagem in imagens:

            imagem.close()

    # ==========================================================
    # CARREGAR PDF
    # ==========================================================

    def carregar_pdf(
        self,
        caminho
    ):

        self.pdf_path = caminho
        self.resultado_omr = None

        if hasattr(self, "process_omr_button"):

            self.process_omr_button.configure(
                state="normal"
            )

        self.file_name.configure(
            text=os.path.basename(
                caminho
            )
        )

        if self.pdf_reader:

            self.pdf_reader.fechar()

        self.pdf_reader = PDFReader(
            caminho
        )

        self.total_paginas = (
            self.pdf_reader.total_paginas()
        )

        self.pagina_atual = 1

        self.page_label.configure(
            text=(
                f"Página "
                f"{self.pagina_atual} "
                f"de "
                f"{self.total_paginas}"
            )
        )

        imagem = self.pdf_reader.obter_pagina(
            0
        )

        self.viewer.mostrar(
            imagem
        )

    # ==========================================================
    # ABRIR FICHA ATIVA
    # ==========================================================

    def abrir_pdf_gerado(
        self
    ):

        if not self.pdf_gerado_path:

            messagebox.showwarning(
                "Ficha",
                "Nenhuma ficha ativa foi definida."
            )

            return

        if not os.path.exists(
            self.pdf_gerado_path
        ):

            messagebox.showwarning(
                "Ficha",
                "O arquivo da ficha ativa não foi encontrado."
            )

            return

        self.carregar_pdf(
            self.pdf_gerado_path
        )

        self.carregar_mapa_atual()

        self.status.configure(
            text="Status: ficha ativa carregada."
        )

    # ==========================================================
    # SELECIONAR PDF
    # ==========================================================

    def selecionar_pdf(
        self
    ):

        caminho = filedialog.askopenfilename(
            title="Selecionar ficha PDF",
            filetypes=[
                (
                    "Arquivos PDF",
                    "*.pdf"
                )
            ]
        )

        if not caminho:
            return

        self.carregar_pdf(
            caminho
        )

        self.carregar_mapa_atual()

        self.status.configure(
            text="Status: PDF carregado com sucesso."
        )

    # ==========================================================
    # PRÓXIMA PÁGINA
    # ==========================================================

    def proxima_pagina(
        self
    ):

        if not self.pdf_reader:
            return

        if (
            self.pagina_atual
            >= self.total_paginas
        ):

            return

        self.pagina_atual += 1

        imagem = self.pdf_reader.obter_pagina(
            self.pagina_atual - 1
        )

        self.viewer.mostrar(
            imagem
        )

        self.page_label.configure(
            text=(
                f"Página "
                f"{self.pagina_atual} "
                f"de "
                f"{self.total_paginas}"
            )
        )

    # ==========================================================
    # PÁGINA ANTERIOR
    # ==========================================================

    def pagina_anterior(
        self
    ):

        if not self.pdf_reader:
            return

        if self.pagina_atual <= 1:
            return

        self.pagina_atual -= 1

        imagem = self.pdf_reader.obter_pagina(
            self.pagina_atual - 1
        )

        self.viewer.mostrar(
            imagem
        )

        self.page_label.configure(
            text=(
                f"Página "
                f"{self.pagina_atual} "
                f"de "
                f"{self.total_paginas}"
            )
        )

    # ==========================================================
    # PROCESSAR OMR
    # ==========================================================

    def processar_omr(
        self
    ):

        if not self.pdf_path:

            messagebox.showwarning(
                "Leitura OMR",
                "Selecione o PDF escaneado da ficha primeiro."
            )

            return

        if not self.mapa_gerado_path:

            messagebox.showwarning(
                "Leitura OMR",
                "Nenhum mapa OMR está associado à ficha ativa."
            )

            return

        if not self.dados_ficha_atual:

            messagebox.showwarning(
                "Leitura OMR",
                "Os dados da ficha ativa não estão disponíveis."
            )

            return

        try:

            self.process_omr_button.configure(
                state="disabled"
            )

            self.status.configure(
                text="Status: processando ficha com OMR..."
            )

            self.update_idletasks()

            pasta_ficha = os.path.dirname(
                os.path.abspath(
                    self.mapa_gerado_path
                )
            )

            leitor = LeitorFicha(
                mapa_path=self.mapa_gerado_path,
                dados_ficha=self.dados_ficha_atual,
                ficha_id=self.ficha_ativa_id
            )

            resultado = leitor.ler_pdf(
                self.pdf_path
            )

            self.resultado_omr = resultado

            erros = resultado.get(
                "erros_validacao",
                []
            )

            if erros:

                self.status.configure(
                    text=(
                        "Status: OMR concluído, mas foram encontradas "
                        "marcações inválidas."
                    )
                )

                detalhes = "\n".join(
                    f"Pergunta {erro['numero']}: {erro['mensagem']}"
                    for erro in erros
                )

                messagebox.showwarning(
                    "Validação OMR",
                    (
                        "A leitura foi concluída, mas o resultado não "
                        "pode ser salvo enquanto houver marcações inválidas.\n\n"
                        f"{detalhes}"
                    )
                )

                return

            self.status.configure(
                text=(
                    "Status: OMR concluído. "
                    f"{resultado['total_marcadas']} marcações "
                    f"de {resultado['total_caixas']} caixas."
                )
            )

            messagebox.showinfo(
                "Leitura concluída",
                (
                    "Ficha lida com sucesso.\n\n"
                    f"Caixas analisadas: {resultado['total_caixas']}\n"
                    f"Caixas marcadas: {resultado['total_marcadas']}\n"
                    f"Caixas vazias: {resultado['total_vazias']}\n\n"
                    "Revise os campos digitados e clique em "
                    "'Salvar resultado'."
                )
            )

        except Exception as erro:

            self.resultado_omr = None

            self.status.configure(
                text="Status: erro durante a leitura OMR."
            )

            messagebox.showerror(
                "Erro na leitura OMR",
                (
                    "Não foi possível ler a ficha.\n\n"
                    f"{erro}"
                )
            )

            print(
                "Erro na leitura OMR:",
                repr(erro)
            )

        finally:

            if hasattr(self, "process_omr_button"):

                self.process_omr_button.configure(
                    state="normal" if self.pdf_path else "disabled"
                )

    # ==========================================================
    # MONTAR REGISTRO DA PESQUISA
    # ==========================================================

    def _montar_registro_pesquisa(
        self,
        dados
    ):

        if not self.resultado_omr:
            raise ValueError(
                "A ficha ainda não foi processada pelo OMR."
            )

        erros = self.resultado_omr.get(
            "erros_validacao",
            []
        )

        if erros:
            raise ValueError(
                "Existem marcações inválidas no resultado OMR. "
                "Faça uma nova leitura após corrigir a ficha."
            )

        registro = {}

        identificacao = dados.get(
            "identificacao",
            {}
        )

        respostas_omr = self.resultado_omr.get(
            "respostas_omr",
            {}
        )

        respostas_abertas = dados.get(
            "respostas_abertas",
            {}
        )

        # Primeiro, somente os campos de cabeçalho que o usuário criou.
        for campo in self.dados_ficha_atual.get(
            "campos_identificacao",
            []
        ):
            nome = str(
                campo.get("nome", "")
            ).strip()

            if nome:
                registro[nome] = identificacao.get(
                    nome,
                    ""
                )

        # Depois, todas as perguntas da ficha, na ordem original.
        for elemento in self.dados_ficha_atual.get(
            "elementos",
            []
        ):
            if elemento.get("tipo", "pergunta") != "pergunta":
                continue

            numero = str(
                elemento.get("numero", "")
            ).strip()

            if not numero:
                continue

            texto = str(
                elemento.get("texto", "")
            ).strip()

            cabecalho = (
                f"{numero} {texto}".strip()
                if numero and texto
                else (numero or texto)
            )

            if elemento.get("tipo_resposta") == "aberta":
                valor = respostas_abertas.get(
                    numero,
                    ""
                )
            else:
                valor = respostas_omr.get(
                    numero,
                    ""
                )

            registro[cabecalho] = valor

        return registro

    # ==========================================================
    # SALVAR PESQUISA
    # ==========================================================

    def salvar_resultado_atual(
        self
    ):

        if not hasattr(
            self,
            "form_panel"
        ):

            messagebox.showwarning(
                "Salvar resultado",
                "O formulário de preenchimento não está disponível."
            )

            return

        self.form_panel.salvar()

    # ==========================================================
    # SALVAR PESQUISA
    # ==========================================================

    def salvar_pesquisa(
        self,
        dados
    ):

        try:

            registro = self._montar_registro_pesquisa(
                dados
            )

            caminho_planilha = self.dados_ficha_atual.get(
                "planilha_resultados_path"
            )

            if not caminho_planilha:
                raise ValueError(
                    "A planilha desta pesquisa ainda não foi criada. "
                    "Abra 'Visualizar ficha ativa' e clique em "
                    "'Gerar planilha da pesquisa' antes de salvar resultados."
                )

            if not os.path.isfile(caminho_planilha):
                raise FileNotFoundError(
                    "A planilha configurada desta pesquisa não foi encontrada. "
                    "Reconfigure a planilha antes de salvar novos resultados."
                )

            cabecalhos_esperados = PlanilhaResultados.cabecalhos_da_ficha(
                self.dados_ficha_atual
            )

            PlanilhaResultados.adicionar_registro(
                caminho_planilha,
                registro,
                cabecalhos_esperados=cabecalhos_esperados,
                dados_ficha=self.dados_ficha_atual
            )

            self.resultado_omr = None

            self.status.configure(
                text="Status: resultado salvo na planilha. Faça uma nova leitura para o próximo formulário."
            )

            messagebox.showinfo(
                "Resultado salvo",
                (
                    "O resultado da ficha foi salvo com sucesso.\n\n"
                    f"Planilha: {caminho_planilha}"
                )
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro ao salvar resultado",
                (
                    "Não foi possível salvar o resultado.\n\n"
                    f"{erro}"
                )
            )

            print(
                "Erro ao salvar resultado:",
                repr(erro)
            )


# ==========================================================
# EXECUÇÃO
# ==========================================================

if __name__ == "__main__":

    app = MainWindow()

    app.mainloop()
