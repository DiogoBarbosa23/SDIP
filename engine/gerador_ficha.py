from PIL import Image, ImageDraw, ImageFont

import cv2
import json
import os
import numpy as np


class GeradorFicha:

    LARGURA = 1191
    ALTURA = 1684
    MARGEM = 70
    FIM_CABECALHO = 240
    INICIO_PERGUNTAS = 275
    LIMITE_INFERIOR = 1500

    COLUNA_ESQUERDA_X = 70
    COLUNA_DIREITA_X = 615
    COLUNA_LARGURA = 505

    ESPACO_ENTRE_PERGUNTAS = 18
    ESPACO_APOS_SECAO = 18

    # Espaçamento vertical entre linhas de opções OMR.
    ALTURA_LINHA_OPCAO = 40

    ALTURA_LINHA_ABERTA = 30
    QUANTIDADE_LINHAS_ABERTA = 1

    # ==========================================================
    # CABEÇALHO
    # ==========================================================

    IDENTIFICACAO_INICIO_Y = 170
    IDENTIFICACAO_ALTURA_LINHA = 38
    IDENTIFICACAO_ESPACO_FINAL = 15

    # ==========================================================
    # ÁREA DA LOGO / TÍTULO
    # ==========================================================

    LOGO_X1 = 145
    LOGO_X2 = 320
    LOGO_Y1 = 55
    LOGO_Y2 = 155

    ESPACO_LOGO_TEXTO = 25

    TITULO_X = (
        LOGO_X2
        + ESPACO_LOGO_TEXTO
    )

    TITULO_Y = 65
    NOME_Y = 135

    # ==========================================================
    # ARUCOS
    # ==========================================================

    ARUCO_TAMANHO = 90
    ARUCO_MARGEM = 30
    ARUCO_DICIONARIO = cv2.aruco.DICT_4X4_50
    ARUCO_IDS_POR_PAGINA = 4

    # ==========================================================
    # TAMANHO DE FONTE
    # ==========================================================

    TAMANHO_FONTE_PADRAO = 14
    TAMANHO_FONTE_MINIMO = 10
    TAMANHO_FONTE_MAXIMO = 20

    # ==========================================================
    # CAIXA OMR
    # ==========================================================

    # Tamanho visual da caixa apresentada ao usuário.
    CAIXA_OMR_TAMANHO = 30

    # Margem usada pelo OMRReader.
    #
    # A área efetivamente analisada será:
    #
    # 30 - 7 - 7 = 16 pixels
    #
    # A margem NÃO é desenhada na ficha.
    CAIXA_OMR_MARGEM = 7

    # ==========================================================
    # CONSTRUTOR
    # ==========================================================

    def __init__(
        self,
        nome_pesquisa,
        titulo,
        logo_path=None,
        campos_identificacao=None,
        tamanho_fonte=None
    ):

        self.nome_pesquisa = nome_pesquisa
        self.titulo = titulo
        self.logo_path = logo_path

        self.campos_identificacao = (
            list(campos_identificacao)
            if campos_identificacao
            else []
        )

        # ------------------------------------------------------
        # Normalização do tamanho da fonte
        # ------------------------------------------------------

        if tamanho_fonte is None:
            tamanho_fonte = self.TAMANHO_FONTE_PADRAO

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
            self.TAMANHO_FONTE_MINIMO,
            min(
                self.TAMANHO_FONTE_MAXIMO,
                tamanho_fonte
            )
        )

        self.tamanho_fonte = (
            tamanho_fonte
        )

        # ======================================================
        # ESTADO
        # ======================================================

        self.elementos = []
        self.secoes = []
        self.perguntas = []

        self.coordenadas_omr = []
        self.perguntas_abertas = []

        self.paginas_geradas = []
        self.aruco_paginas = []

    # ==========================================================
    # SEÇÃO
    # ==========================================================

    def adicionar_secao(
        self,
        texto,
        numero=None
    ):

        if numero is None:
            numero = (
                len(self.secoes)
                + 1
            )

        secao = {
            "tipo": "secao",
            "numero": numero,
            "texto": texto
        }

        self.elementos.append(
            secao
        )

        self.secoes.append(
            secao
        )

    # ==========================================================
    # PERGUNTA
    # ==========================================================

    def adicionar_pergunta(
        self,
        texto,
        tipo_resposta,
        opcoes,
        numero=None
    ):

        if numero is None:
            numero = str(
                len(self.perguntas)
                + 1
            )

        pergunta = {
            "tipo": "pergunta",
            "numero": str(numero),
            "texto": texto,
            "tipo_resposta": tipo_resposta,
            "opcoes": list(opcoes)
        }

        self.elementos.append(
            pergunta
        )

        self.perguntas.append(
            pergunta
        )

    # ==========================================================
    # OBTER FICHA
    # ==========================================================

    def obter_ficha(
        self
    ):

        return {
            "nome_pesquisa": (
                self.nome_pesquisa
            ),
            "titulo": self.titulo,
            "logo_path": self.logo_path,
            "tamanho_fonte": (
                self.tamanho_fonte
            ),
            "campos_identificacao": (
                self.campos_identificacao
            ),
            "elementos": self.elementos,
            "secoes": self.secoes,
            "perguntas": self.perguntas,
            "perguntas_abertas": (
                self.perguntas_abertas
            )
        }

    # ==========================================================
    # ALTURA DO CABEÇALHO
    # ==========================================================

    def _calcular_altura_cabecalho(
        self
    ):

        quantidade = len(
            self.campos_identificacao
        )

        if quantidade == 0:
            return self.FIM_CABECALHO

        quantidade_linhas = (
            (quantidade + 1) // 2
        )

        altura_identificacao = (
            quantidade_linhas
            * self.IDENTIFICACAO_ALTURA_LINHA
        )

        fim = (
            self.IDENTIFICACAO_INICIO_Y
            + altura_identificacao
            + self.IDENTIFICACAO_ESPACO_FINAL
        )

        return max(
            self.FIM_CABECALHO,
            fim
        )

    # ==========================================================
    # INÍCIO DAS PERGUNTAS
    # ==========================================================

    def _obter_inicio_perguntas(
        self
    ):

        return (
            self._calcular_altura_cabecalho()
            + 35
        )

    # ==========================================================
    # ÁREA DA LOGO
    # ==========================================================

    def _calcular_area_logo(
        self
    ):

        return (
            self.LOGO_X1,
            self.LOGO_Y1,
            self.LOGO_X2,
            self.LOGO_Y2
        )

    # ==========================================================
    # ÁREA DO TEXTO
    # ==========================================================

    def _calcular_area_texto_cabecalho(
        self
    ):

        x1 = self.TITULO_X

        x2 = (
            self.LARGURA
            - self.MARGEM
        )

        return (
            x1,
            x2
        )

    # ==========================================================
    # FONTES DA FICHA
    # ==========================================================

    def _obter_fontes(
        self
    ):

        base = self.tamanho_fonte

        return {

            "titulo": self._fonte(
                max(
                    16,
                    round(base * 1.75)
                )
            ),

            "subtitulo": self._fonte(
                max(
                    12,
                    round(base * 1.15)
                )
            ),

            "secao": self._fonte(
                max(
                    11,
                    round(base * 1.10)
                )
            ),

            "pergunta": self._fonte(
                base
            ),

            "opcao": self._fonte(
                max(
                    9,
                    round(base * 0.84)
                )
            ),

            "aberta": self._fonte(
                max(
                    9,
                    round(base * 0.84)
                )
            ),

            "identificacao": self._fonte(
                max(
                    8,
                    round(base * 0.67)
                )
            ),

            "logo": self._fonte(
                max(
                    8,
                    round(base * 0.60)
                )
            ),

            "rodape": self._fonte(
                max(
                    8,
                    round(base * 0.67)
                )
            )
        }

    # ==========================================================
    # ALTURA DAS LINHAS DE OPÇÃO
    # ==========================================================

    def _calcular_altura_linha_opcao(
        self,
        desenho,
        fonte_opcao
    ):

        altura = self._altura_fonte(
            desenho,
            fonte_opcao
        )

        return max(
            self.ALTURA_LINHA_OPCAO,
            altura + 10
        )

    # ==========================================================
    # GERAR IMAGEM
    # ==========================================================

    def gerar_imagem(
        self,
        caminho_saida
    ):

        self.coordenadas_omr = []
        self.perguntas_abertas = []
        self.paginas_geradas = []
        self.aruco_paginas = []

        fontes = self._obter_fontes()

        fonte_titulo = fontes["titulo"]
        fonte_subtitulo = fontes["subtitulo"]
        fonte_secao = fontes["secao"]
        fonte_pergunta = fontes["pergunta"]
        fonte_opcao = fontes["opcao"]
        fonte_aberta = fontes["aberta"]
        fonte_identificacao = fontes["identificacao"]
        fonte_logo = fontes["logo"]

        pagina_atual = 1

        imagem, desenho = (
            self._criar_pagina(
                fonte_titulo,
                fonte_subtitulo,
                fonte_logo,
                fonte_identificacao,
                pagina_atual
            )
        )

        inicio_perguntas = (
            self._obter_inicio_perguntas()
        )

        y_esquerda = (
            inicio_perguntas
        )

        y_direita = (
            inicio_perguntas
        )

        coluna_atual = "esquerda"

        altura_linha_opcao = (
            self._calcular_altura_linha_opcao(
                desenho,
                fonte_opcao
            )
        )

        # ======================================================
        # ELEMENTOS
        # ======================================================

        for elemento in self.elementos:

            # ==================================================
            # SEÇÃO
            # ==================================================

            if elemento["tipo"] == "secao":

                altura = (
                    self._calcular_altura_secao(
                        desenho,
                        elemento,
                        fonte_secao
                    )
                )

                if coluna_atual == "esquerda":

                    if (
                        y_esquerda + altura
                        <= self.LIMITE_INFERIOR
                    ):

                        y_esquerda = (
                            self._desenhar_secao(
                                desenho,
                                y_esquerda,
                                self.COLUNA_ESQUERDA_X,
                                elemento,
                                fonte_secao
                            )
                        )

                        continue

                    coluna_atual = "direita"

                if coluna_atual == "direita":

                    if (
                        y_direita + altura
                        <= self.LIMITE_INFERIOR
                    ):

                        y_direita = (
                            self._desenhar_secao(
                                desenho,
                                y_direita,
                                self.COLUNA_DIREITA_X,
                                elemento,
                                fonte_secao
                            )
                        )

                        continue

                    (
                        pagina_atual,
                        imagem,
                        desenho,
                        y_esquerda,
                        y_direita,
                        coluna_atual
                    ) = self._nova_pagina(
                        caminho_saida,
                        pagina_atual,
                        imagem,
                        desenho,
                        fonte_titulo,
                        fonte_subtitulo,
                        fonte_logo,
                        fonte_identificacao
                    )

                    y_esquerda = (
                        self._desenhar_secao(
                            desenho,
                            y_esquerda,
                            self.COLUNA_ESQUERDA_X,
                            elemento,
                            fonte_secao
                        )
                    )

                    continue

            # ==================================================
            # PERGUNTA
            # ==================================================

            altura_pergunta = (
                self._calcular_altura_pergunta(
                    desenho,
                    elemento,
                    fonte_pergunta,
                    fonte_opcao,
                    fonte_aberta,
                    altura_linha_opcao
                )
            )

            if coluna_atual == "esquerda":

                if (
                    y_esquerda + altura_pergunta
                    <= self.LIMITE_INFERIOR
                ):

                    y_esquerda = (
                        self._desenhar_pergunta(
                            imagem,
                            desenho,
                            y_esquerda,
                            self.COLUNA_ESQUERDA_X,
                            elemento["numero"],
                            elemento,
                            pagina_atual,
                            fonte_pergunta,
                            fonte_opcao,
                            fonte_aberta,
                            altura_linha_opcao
                        )
                    )

                    continue

                coluna_atual = "direita"

            if coluna_atual == "direita":

                if (
                    y_direita + altura_pergunta
                    <= self.LIMITE_INFERIOR
                ):

                    y_direita = (
                        self._desenhar_pergunta(
                            imagem,
                            desenho,
                            y_direita,
                            self.COLUNA_DIREITA_X,
                            elemento["numero"],
                            elemento,
                            pagina_atual,
                            fonte_pergunta,
                            fonte_opcao,
                            fonte_aberta,
                            altura_linha_opcao
                        )
                    )

                    continue

                (
                    pagina_atual,
                    imagem,
                    desenho,
                    y_esquerda,
                    y_direita,
                    coluna_atual
                ) = self._nova_pagina(
                    caminho_saida,
                    pagina_atual,
                    imagem,
                    desenho,
                    fonte_titulo,
                    fonte_subtitulo,
                    fonte_logo,
                    fonte_identificacao
                )

                y_esquerda = (
                    self._desenhar_pergunta(
                        imagem,
                        desenho,
                        y_esquerda,
                        self.COLUNA_ESQUERDA_X,
                        elemento["numero"],
                        elemento,
                        pagina_atual,
                        fonte_pergunta,
                        fonte_opcao,
                        fonte_aberta,
                        altura_linha_opcao
                    )
                )

        # ======================================================
        # FINAL DA ÚLTIMA PÁGINA
        # ======================================================

        caminho_pagina = (
            self._gerar_caminho_pagina(
                caminho_saida,
                pagina_atual
            )
        )

        self._finalizar_pagina(
            imagem,
            desenho,
            caminho_pagina
        )

        self.paginas_geradas.append(
            caminho_pagina
        )

        return self.paginas_geradas

    # ==========================================================
    # NOVA PÁGINA
    # ==========================================================

    def _nova_pagina(
        self,
        caminho_saida,
        pagina_atual,
        imagem,
        desenho,
        fonte_titulo,
        fonte_subtitulo,
        fonte_logo,
        fonte_identificacao
    ):

        caminho_pagina = (
            self._gerar_caminho_pagina(
                caminho_saida,
                pagina_atual
            )
        )

        self._finalizar_pagina(
            imagem,
            desenho,
            caminho_pagina
        )

        self.paginas_geradas.append(
            caminho_pagina
        )

        pagina_atual += 1

        imagem, desenho = (
            self._criar_pagina(
                fonte_titulo,
                fonte_subtitulo,
                fonte_logo,
                fonte_identificacao,
                pagina_atual
            )
        )

        inicio_perguntas = (
            self._obter_inicio_perguntas()
        )

        return (
            pagina_atual,
            imagem,
            desenho,
            inicio_perguntas,
            inicio_perguntas,
            "esquerda"
        )

    # ==========================================================
    # CRIAR PÁGINA
    # ==========================================================

    def _criar_pagina(
        self,
        fonte_titulo,
        fonte_subtitulo,
        fonte_logo,
        fonte_identificacao,
        pagina
    ):

        imagem = Image.new(
            "RGB",
            (
                self.LARGURA,
                self.ALTURA
            ),
            "white"
        )

        desenho = ImageDraw.Draw(
            imagem
        )

        # ======================================================
        # ARUCOS
        # ======================================================

        self._desenhar_arucos(
            imagem,
            pagina
        )

        # ======================================================
        # ÁREA DA LOGO
        # ======================================================

        (
            logo_x1,
            logo_y1,
            logo_x2,
            logo_y2
        ) = self._calcular_area_logo()

        desenho.rectangle(
            (
                logo_x1,
                logo_y1,
                logo_x2,
                logo_y2
            ),
            outline="black",
            width=2
        )

        # ======================================================
        # LOGO
        # ======================================================

        if self.logo_path:

            try:

                logo = Image.open(
                    self.logo_path
                ).convert(
                    "RGBA"
                )

                largura_disponivel = max(
                    1,
                    logo_x2
                    - logo_x1
                    - 20
                )

                altura_disponivel = max(
                    1,
                    logo_y2
                    - logo_y1
                    - 20
                )

                logo.thumbnail(
                    (
                        largura_disponivel,
                        altura_disponivel
                    ),
                    Image.Resampling.LANCZOS
                )

                pos_x = (
                    logo_x1
                    + (
                        logo_x2
                        - logo_x1
                        - logo.width
                    ) // 2
                )

                pos_y = (
                    logo_y1
                    + (
                        logo_y2
                        - logo_y1
                        - logo.height
                    ) // 2
                )

                imagem.paste(
                    logo,
                    (
                        pos_x,
                        pos_y
                    ),
                    logo
                )

            except Exception:

                self._desenhar_placeholder_logo(
                    desenho,
                    logo_x1,
                    logo_y1,
                    logo_x2,
                    logo_y2,
                    fonte_logo
                )

        else:

            self._desenhar_placeholder_logo(
                desenho,
                logo_x1,
                logo_y1,
                logo_x2,
                logo_y2,
                fonte_logo
            )

        # ======================================================
        # TEXTO DO CABEÇALHO
        # ======================================================

        (
            texto_x1,
            texto_x2
        ) = (
            self._calcular_area_texto_cabecalho()
        )

        largura_texto = (
            texto_x2
            - texto_x1
        )

        # ======================================================
        # TÍTULO
        # ======================================================

        if self.titulo:

            linhas_titulo = (
                self._quebrar_texto(
                    desenho,
                    self.titulo,
                    fonte_titulo,
                    largura_texto
                )
            )

            y_titulo = (
                self.TITULO_Y
            )

            for linha in linhas_titulo:

                desenho.text(
                    (
                        texto_x1,
                        y_titulo
                    ),
                    linha,
                    fill="black",
                    font=fonte_titulo
                )

                y_titulo += (
                    self._altura_fonte(
                        desenho,
                        fonte_titulo
                    )
                    + 4
                )

        # ======================================================
        # NOME DA PESQUISA
        # ======================================================

        linhas_nome = (
            self._quebrar_texto(
                desenho,
                self.nome_pesquisa,
                fonte_subtitulo,
                largura_texto
            )
        )

        y_nome = (
            self.NOME_Y
        )

        for linha in linhas_nome:

            desenho.text(
                (
                    texto_x1,
                    y_nome
                ),
                linha,
                fill="black",
                font=fonte_subtitulo
            )

            y_nome += (
                self._altura_fonte(
                    desenho,
                    fonte_subtitulo
                )
                + 2
            )

        # ======================================================
        # CAMPOS DE IDENTIFICAÇÃO
        # ======================================================

        self._desenhar_campos_identificacao(
            desenho,
            fonte_identificacao
        )

        # ======================================================
        # LINHA FINAL DO CABEÇALHO
        # ======================================================

        fim_cabecalho = (
            self._calcular_altura_cabecalho()
        )

        desenho.line(
            (
                self.MARGEM,
                fim_cabecalho,
                self.LARGURA - self.MARGEM,
                fim_cabecalho
            ),
            fill="black",
            width=3
        )

        return (
            imagem,
            desenho
        )

    # ==========================================================
    # CAMPOS DE IDENTIFICAÇÃO
    # ==========================================================

    def _desenhar_campos_identificacao(
        self,
        desenho,
        fonte
    ):

        if not self.campos_identificacao:
            return

        largura_util = (
            self.LARGURA
            - (
                self.MARGEM * 2
            )
        )

        largura_coluna = (
            (
                largura_util
                - self.IDENTIFICACAO_ESPACO_FINAL
            )
            / 2
        )

        for indice, campo in enumerate(
            self.campos_identificacao
        ):

            linha = (
                indice // 2
            )

            coluna = (
                indice % 2
            )

            x = (
                self.MARGEM
                + (
                    coluna
                    * (
                        largura_coluna
                        + self.IDENTIFICACAO_ESPACO_FINAL
                    )
                )
            )

            y = (
                self.IDENTIFICACAO_INICIO_Y
                + (
                    linha
                    * self.IDENTIFICACAO_ALTURA_LINHA
                )
            )

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

            texto = (
                f"{nome}: "
            )

            caixa = desenho.textbbox(
                (
                    0,
                    0
                ),
                texto,
                font=fonte
            )

            largura_label = (
                caixa[2]
                - caixa[0]
            )

            desenho.text(
                (
                    x,
                    y
                ),
                texto,
                fill="black",
                font=fonte
            )

            linha_x1 = (
                x
                + largura_label
                + 8
            )

            linha_x2 = (
                x
                + largura_coluna
            )

            desenho.line(
                (
                    linha_x1,
                    y + 19,
                    linha_x2,
                    y + 19
                ),
                fill="black",
                width=1
            )

            if tipo == "Data":

                desenho.text(
                    (
                        linha_x2 - 65,
                        y + 3
                    ),
                    "DD/MM/AAAA",
                    fill="black",
                    font=self._fonte(
                        max(
                            8,
                            round(
                                self.tamanho_fonte
                                * 0.42
                            )
                        )
                    )
                )

    # ==========================================================
    # ARUCOS
    # ==========================================================

    def _desenhar_arucos(
        self,
        imagem,
        pagina
    ):

        try:

            dicionario = (
                cv2.aruco.getPredefinedDictionary(
                    self.ARUCO_DICIONARIO
                )
            )

        except AttributeError:

            dicionario = (
                cv2.aruco.Dictionary_get(
                    self.ARUCO_DICIONARIO
                )
            )

        ids_base = (
            (pagina - 1)
            * self.ARUCO_IDS_POR_PAGINA
        )

        ids = [
            ids_base,
            ids_base + 1,
            ids_base + 2,
            ids_base + 3
        ]

        tamanho = (
            self.ARUCO_TAMANHO
        )

        margem = (
            self.ARUCO_MARGEM
        )

        posicoes = [
            (
                margem,
                margem
            ),
            (
                self.LARGURA
                - margem
                - tamanho,
                margem
            ),
            (
                self.LARGURA
                - margem
                - tamanho,
                self.ALTURA
                - margem
                - tamanho
            ),
            (
                margem,
                self.ALTURA
                - margem
                - tamanho
            )
        ]

        for id_aruco, posicao in zip(
            ids,
            posicoes
        ):

            try:

                marcador = (
                    cv2.aruco.generateImageMarker(
                        dicionario,
                        id_aruco,
                        tamanho
                    )
                )

            except AttributeError:

                marcador = (
                    cv2.aruco.drawMarker(
                        dicionario,
                        id_aruco,
                        tamanho
                    )
                )

            marcador_rgb = cv2.cvtColor(
                marcador,
                cv2.COLOR_GRAY2RGB
            )

            marcador_pil = Image.fromarray(
                marcador_rgb
            )

            imagem.paste(
                marcador_pil,
                posicao
            )

        self.aruco_paginas.append(
            {
                "pagina": pagina,
                "ids": ids,
                "posicoes": [
                    {
                        "id": id_aruco,
                        "x": posicao[0],
                        "y": posicao[1],
                        "largura": tamanho,
                        "altura": tamanho
                    }
                    for id_aruco, posicao
                    in zip(
                        ids,
                        posicoes
                    )
                ]
            }
        )

    # ==========================================================
    # ALTURA DA SEÇÃO
    # ==========================================================

    def _calcular_altura_secao(
        self,
        desenho,
        secao,
        fonte_secao
    ):

        linhas = (
            self._quebrar_texto(
                desenho,
                secao["texto"],
                fonte_secao,
                self.COLUNA_LARGURA
            )
        )

        return (
            len(linhas)
            * self._altura_fonte(
                desenho,
                fonte_secao
            )
            + self.ESPACO_APOS_SECAO
        )

    # ==========================================================
    # DESENHAR SEÇÃO
    # ==========================================================

    def _desenhar_secao(
        self,
        desenho,
        y,
        x_coluna,
        secao,
        fonte_secao
    ):

        linhas = (
            self._quebrar_texto(
                desenho,
                secao["texto"],
                fonte_secao,
                self.COLUNA_LARGURA
            )
        )

        altura_fonte = (
            self._altura_fonte(
                desenho,
                fonte_secao
            )
        )

        for indice_linha, linha in enumerate(
            linhas
        ):

            prefixo = (
                f"{secao['numero']}. "
                if indice_linha == 0
                else "   "
            )

            desenho.text(
                (
                    x_coluna,
                    y
                ),
                prefixo + linha,
                fill="black",
                font=fonte_secao
            )

            y += (
                altura_fonte
            )

        return (
            y
            + self.ESPACO_APOS_SECAO
        )

    # ==========================================================
    # ALTURA DA PERGUNTA
    # ==========================================================

    def _calcular_altura_pergunta(
        self,
        desenho,
        pergunta,
        fonte_pergunta,
        fonte_opcao,
        fonte_aberta,
        altura_linha_opcao
    ):

        linhas_pergunta = (
            self._quebrar_texto(
                desenho,
                pergunta["texto"],
                fonte_pergunta,
                self.COLUNA_LARGURA
            )
        )

        altura_texto = (
            len(linhas_pergunta)
            * self._altura_fonte(
                desenho,
                fonte_pergunta
            )
        )

        if (
            pergunta["tipo_resposta"]
            == "aberta"
        ):

            return (
                altura_texto
                + 18
                + (
                    self.QUANTIDADE_LINHAS_ABERTA
                    * self.ALTURA_LINHA_ABERTA
                )
                + self.ESPACO_ENTRE_PERGUNTAS
            )

        linhas_opcoes = (
            self._calcular_linhas_opcoes(
                desenho,
                pergunta["opcoes"],
                fonte_opcao
            )
        )

        return (
            altura_texto
            + 18
            + (
                linhas_opcoes
                * altura_linha_opcao
            )
            + self.ESPACO_ENTRE_PERGUNTAS
        )

    # ==========================================================
    # LINHAS DE OPÇÕES
    # ==========================================================

    def _calcular_linhas_opcoes(
        self,
        desenho,
        opcoes,
        fonte_opcao
    ):

        x = (
            self.COLUNA_ESQUERDA_X
        )

        linhas = 1

        for opcao in opcoes:

            texto_opcao = str(
                opcao
            )

            largura_opcao = (
                self._largura_opcao(
                    desenho,
                    texto_opcao,
                    fonte_opcao
                )
            )

            if (
                x != self.COLUNA_ESQUERDA_X
                and (
                    x
                    - self.COLUNA_ESQUERDA_X
                    + largura_opcao
                ) > self.COLUNA_LARGURA
            ):

                linhas += 1

                x = (
                    self.COLUNA_ESQUERDA_X
                )

            if (
                largura_opcao
                > self.COLUNA_LARGURA
            ):

                if (
                    x
                    != self.COLUNA_ESQUERDA_X
                ):

                    linhas += 1

                    x = (
                        self.COLUNA_ESQUERDA_X
                    )

                x += (
                    self.COLUNA_LARGURA
                )

            else:

                x += (
                    largura_opcao
                )

        return linhas

    # ==========================================================
    # DESENHAR PERGUNTA
    # ==========================================================

    def _desenhar_pergunta(
        self,
        imagem,
        desenho,
        y,
        x_coluna,
        numero,
        pergunta,
        pagina,
        fonte_pergunta,
        fonte_opcao,
        fonte_aberta,
        altura_linha_opcao
    ):

        linhas_pergunta = (
            self._quebrar_texto(
                desenho,
                pergunta["texto"],
                fonte_pergunta,
                self.COLUNA_LARGURA
            )
        )

        altura_fonte = (
            self._altura_fonte(
                desenho,
                fonte_pergunta
            )
        )

        for indice_linha, linha in enumerate(
            linhas_pergunta
        ):

            prefixo = (
                f"{numero} "
                if indice_linha == 0
                else "   "
            )

            desenho.text(
                (
                    x_coluna,
                    y
                ),
                prefixo + linha,
                fill="black",
                font=fonte_pergunta
            )

            y += (
                altura_fonte
            )

        y += 18

        # ======================================================
        # ABERTA
        # ======================================================

        if (
            pergunta["tipo_resposta"]
            == "aberta"
        ):

            self.perguntas_abertas.append(
                {
                    "numero": str(numero),
                    "texto": pergunta["texto"],
                    "pagina": pagina
                }
            )

            linha_x1 = (
                x_coluna
            )

            linha_x2 = (
                x_coluna
                + self.COLUNA_LARGURA
            )

            for _ in range(
                self.QUANTIDADE_LINHAS_ABERTA
            ):

                desenho.line(
                    (
                        linha_x1,
                        y + 25,
                        linha_x2,
                        y + 25
                    ),
                    fill="black",
                    width=1
                )

                y += (
                    self.ALTURA_LINHA_ABERTA
                )

            return (
                y
                + self.ESPACO_ENTRE_PERGUNTAS
            )

        # ======================================================
        # OMR
        # ======================================================

        x = (
            x_coluna
        )

        for indice_opcao, opcao in enumerate(
            pergunta["opcoes"],
            start=1
        ):

            texto_opcao = str(
                opcao
            )

            largura_opcao = (
                self._largura_opcao(
                    desenho,
                    texto_opcao,
                    fonte_opcao
                )
            )

            if (
                x != x_coluna
                and (
                    x
                    - x_coluna
                    + largura_opcao
                ) > self.COLUNA_LARGURA
            ):

                x = (
                    x_coluna
                )

                y += (
                    altura_linha_opcao
                )

            # ==================================================
            # CAIXA OMR
            # ==================================================

            caixa_x1 = int(
                x
            )

            caixa_y1 = int(
                y
            )

            caixa_x2 = (
                caixa_x1
                + self.CAIXA_OMR_TAMANHO
            )

            caixa_y2 = (
                caixa_y1
                + self.CAIXA_OMR_TAMANHO
            )

            # Apenas a caixa externa.
            # A margem de 7 px é utilizada somente
            # pelo OMRReader durante a leitura.
            desenho.rectangle(
                (
                    caixa_x1,
                    caixa_y1,
                    caixa_x2,
                    caixa_y2
                ),
                outline="black",
                width=2
            )

            # ==================================================
            # MAPA OMR
            # ==================================================

            nome_opcao = (
                self._gerar_nome_opcao(
                    numero,
                    opcao,
                    indice_opcao
                )
            )

            self.coordenadas_omr.append(
                {
                    "nome": nome_opcao,
                    "pagina": pagina,
                    "x1": caixa_x1,
                    "y1": caixa_y1,
                    "x2": caixa_x2,
                    "y2": caixa_y2
                }
            )

            # ==================================================
            # TEXTO DA OPÇÃO
            # ==================================================

            desenho.text(
                (
                    caixa_x2 + 10,
                    caixa_y1 + 2
                ),
                texto_opcao,
                fill="black",
                font=fonte_opcao
            )

            x += (
                largura_opcao
            )

        return (
            y
            + altura_linha_opcao
            + self.ESPACO_ENTRE_PERGUNTAS
        )

    # ==========================================================
    # LARGURA DE OPÇÃO
    # ==========================================================

    def _largura_opcao(
        self,
        desenho,
        texto,
        fonte
    ):

        caixa = desenho.textbbox(
            (
                0,
                0
            ),
            texto,
            font=fonte
        )

        largura_texto = (
            caixa[2]
            - caixa[0]
        )

        return (
            self.CAIXA_OMR_TAMANHO
            + 10
            + largura_texto
            + 15
        )

    # ==========================================================
    # QUEBRAR TEXTO
    # ==========================================================

    def _quebrar_texto(
        self,
        desenho,
        texto,
        fonte,
        largura_maxima
    ):

        palavras = str(
            texto
        ).split()

        if not palavras:
            return [""]

        linhas = []
        linha_atual = ""

        for palavra in palavras:

            teste = (
                palavra
                if not linha_atual
                else (
                    linha_atual
                    + " "
                    + palavra
                )
            )

            caixa = desenho.textbbox(
                (
                    0,
                    0
                ),
                teste,
                font=fonte
            )

            largura = (
                caixa[2]
                - caixa[0]
            )

            if (
                linha_atual
                and largura > largura_maxima
            ):

                linhas.append(
                    linha_atual
                )

                linha_atual = (
                    palavra
                )

            else:

                linha_atual = (
                    teste
                )

        if linha_atual:

            linhas.append(
                linha_atual
            )

        return linhas

    # ==========================================================
    # ALTURA DA FONTE
    # ==========================================================

    @staticmethod
    def _altura_fonte(
        desenho,
        fonte
    ):

        caixa = desenho.textbbox(
            (
                0,
                0
            ),
            "Ag",
            font=fonte
        )

        return (
            caixa[3]
            - caixa[1]
        )

    # ==========================================================
    # FINALIZAR PÁGINA
    # ==========================================================

    def _finalizar_pagina(
        self,
        imagem,
        desenho,
        caminho_saida
    ):

        fontes = (
            self._obter_fontes()
        )

        fonte_rodape = (
            fontes["rodape"]
        )

        texto = (
            "SDIP - Sistema de Digitalização "
            "Inteligente de Pesquisas"
        )

        caixa = desenho.textbbox(
            (
                0,
                0
            ),
            texto,
            font=fonte_rodape
        )

        largura_texto = (
            caixa[2]
            - caixa[0]
        )

        pos_x = (
            self.LARGURA
            - largura_texto
        ) // 2

        desenho.text(
            (
                pos_x,
                self.ALTURA - 60
            ),
            texto,
            fill="black",
            font=fonte_rodape
        )

        imagem.save(
            caminho_saida,
            "PNG"
        )

    # ==========================================================
    # CAMINHO
    # ==========================================================

    @staticmethod
    def _gerar_caminho_pagina(
        caminho_base,
        numero_pagina
    ):

        pasta = os.path.dirname(
            caminho_base
        )

        nome = os.path.basename(
            caminho_base
        )

        nome_base, extensao = (
            os.path.splitext(
                nome
            )
        )

        return os.path.join(
            pasta,
            (
                f"{nome_base}_"
                f"{numero_pagina}"
                f"{extensao}"
            )
        )

    # ==========================================================
    # MATRIZ DE PERSPECTIVA
    # ==========================================================

    def _calcular_matriz_mapa(
        self
    ):

        tamanho = (
            self.ARUCO_TAMANHO
        )

        margem = (
            self.ARUCO_MARGEM
        )

        metade = (
            tamanho
            / 2.0
        )

        origem = np.array(
            [
                [
                    margem + metade,
                    margem + metade
                ],
                [
                    self.LARGURA
                    - margem
                    - tamanho
                    + metade,
                    margem + metade
                ],
                [
                    self.LARGURA
                    - margem
                    - tamanho
                    + metade,
                    self.ALTURA
                    - margem
                    - tamanho
                    + metade
                ],
                [
                    margem + metade,
                    self.ALTURA
                    - margem
                    - tamanho
                    + metade
                ]
            ],
            dtype=np.float32
        )

        destino = np.array(
            [
                [
                    167.21,
                    167.18
                ],
                [
                    1023.55,
                    167.18
                ],
                [
                    1023.55,
                    1516.58
                ],
                [
                    167.21,
                    1516.58
                ]
            ],
            dtype=np.float32
        )

        return cv2.getPerspectiveTransform(
            origem,
            destino
        )

    # ==========================================================
    # TRANSFORMAR CAIXA
    # ==========================================================

    def _transformar_caixa(
        self,
        coordenada,
        matriz
    ):

        pontos = np.array(
            [
                [
                    [
                        coordenada["x1"],
                        coordenada["y1"]
                    ],
                    [
                        coordenada["x2"],
                        coordenada["y1"]
                    ],
                    [
                        coordenada["x2"],
                        coordenada["y2"]
                    ],
                    [
                        coordenada["x1"],
                        coordenada["y2"]
                    ]
                ]
            ],
            dtype=np.float32
        )

        transformados = (
            cv2.perspectiveTransform(
                pontos,
                matriz
            )[0]
        )

        xs = (
            transformados[:, 0]
        )

        ys = (
            transformados[:, 1]
        )

        return {
            "nome": coordenada["nome"],
            "pagina": coordenada["pagina"],
            "x1": int(
                round(
                    float(
                        xs.min()
                    )
                )
            ),
            "y1": int(
                round(
                    float(
                        ys.min()
                    )
                )
            ),
            "x2": int(
                round(
                    float(
                        xs.max()
                    )
                )
            ),
            "y2": int(
                round(
                    float(
                        ys.max()
                    )
                )
            )
        }

    # ==========================================================
    # MAPA OMR
    # ==========================================================

    def gerar_mapa_omr(
        self,
        caminho_saida
    ):

        matriz = (
            self._calcular_matriz_mapa()
        )

        coordenadas_normalizadas = []

        for coordenada in (
            self.coordenadas_omr
        ):

            coordenadas_normalizadas.append(
                self._transformar_caixa(
                    coordenada,
                    matriz
                )
            )

        mapa = {
            "imagem_largura": (
                self.LARGURA
            ),
            "imagem_altura": (
                self.ALTURA
            ),
            "quantidade_paginas": (
                len(
                    self.paginas_geradas
                )
            ),
            "tamanho_fonte": (
                self.tamanho_fonte
            ),
            "caixa_omr_tamanho": (
                self.CAIXA_OMR_TAMANHO
            ),
            "caixa_omr_margem": (
                self.CAIXA_OMR_MARGEM
            ),
            "aruco": (
                self.aruco_paginas
            ),
            "coordenadas": (
                coordenadas_normalizadas
            ),
            "perguntas_abertas": (
                self.perguntas_abertas
            ),
            "campos_identificacao": (
                self.campos_identificacao
            )
        }

        with open(
            caminho_saida,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                mapa,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

    # ==========================================================
    # NOME DA OPÇÃO
    # ==========================================================

    @staticmethod
    def _gerar_nome_opcao(
        numero_pergunta,
        opcao,
        indice_opcao
    ):

        texto = str(
            opcao
        ).strip().lower()

        substituicoes = {
            "á": "a",
            "à": "a",
            "ã": "a",
            "â": "a",
            "ä": "a",
            "é": "e",
            "è": "e",
            "ê": "e",
            "ë": "e",
            "í": "i",
            "ì": "i",
            "î": "i",
            "ï": "i",
            "ó": "o",
            "ò": "o",
            "õ": "o",
            "ô": "o",
            "ö": "o",
            "ú": "u",
            "ù": "u",
            "û": "u",
            "ü": "u",
            "ç": "c"
        }

        for antigo, novo in (
            substituicoes.items()
        ):

            texto = (
                texto.replace(
                    antigo,
                    novo
                )
            )

        caracteres_validos = []

        for caractere in texto:

            if (
                caractere.isalnum()
                or caractere == "_"
            ):

                caracteres_validos.append(
                    caractere
                )

            elif caractere.isspace():

                caracteres_validos.append(
                    "_"
                )

        texto = "".join(
            caracteres_validos
        )

        while "__" in texto:

            texto = (
                texto.replace(
                    "__",
                    "_"
                )
            )

        texto = (
            texto.strip("_")
        )

        if "." in str(
            numero_pergunta
        ):

            return (
                f"{numero_pergunta}_"
                f"{texto}"
            )

        return (
            f"{numero_pergunta}."
            f"{indice_opcao}_"
            f"{texto}"
        )

    # ==========================================================
    # PLACEHOLDER DA LOGO
    # ==========================================================

    @staticmethod
    def _desenhar_placeholder_logo(
        desenho,
        x1,
        y1,
        x2,
        y2,
        fonte
    ):

        texto = (
            "ADICIONE SUA LOGO"
        )

        caixa = desenho.textbbox(
            (
                0,
                0
            ),
            texto,
            font=fonte
        )

        largura_texto = (
            caixa[2]
            - caixa[0]
        )

        altura_texto = (
            caixa[3]
            - caixa[1]
        )

        pos_x = (
            x1
            + (
                x2
                - x1
                - largura_texto
            ) // 2
        )

        pos_y = (
            y1
            + (
                y2
                - y1
                - altura_texto
            ) // 2
        )

        desenho.text(
            (
                pos_x,
                pos_y
            ),
            texto,
            fill="black",
            font=fonte
        )

    # ==========================================================
    # FONTE
    # ==========================================================

    @staticmethod
    def _fonte(
        tamanho
    ):

        fontes = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf"
        ]

        for caminho in fontes:

            try:

                return ImageFont.truetype(
                    caminho,
                    tamanho
                )

            except OSError:

                continue

        return ImageFont.load_default()