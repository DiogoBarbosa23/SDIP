import json

import os

import cv2

import numpy as np


class OMRReader:

    def __init__(
        self,
        mapa_path,
        margem=7
    ):
        self.mapa_path = mapa_path
        self.margem = margem
        self.mapa = None
        self.perguntas_abertas = []

        self.carregar_mapa()

    # ======================================================
    # CARREGAR MAPA
    # ======================================================

    def carregar_mapa(
        self
    ):

        if not os.path.exists(
            self.mapa_path
        ):
            raise FileNotFoundError(
                f"Mapa não encontrado: {self.mapa_path}"
            )

        with open(
            self.mapa_path,
            "r",
            encoding="utf-8"
        ) as arquivo:

            self.mapa = json.load(
                arquivo
            )

        if "coordenadas" not in self.mapa:
            raise ValueError(
                "O mapa não possui coordenadas."
            )

        self.perguntas_abertas = (
            self.mapa.get(
                "perguntas_abertas",
                []
            )
        )

    # ======================================================
    # PERGUNTAS ABERTAS
    # ======================================================

    def obter_perguntas_abertas(
        self
    ):

        return list(
            self.perguntas_abertas
        )

    # ======================================================
    # ANALISAR IMAGEM
    # ======================================================

    def analisar_imagem(
        self,
        imagem,
        pagina=1
    ):
        """
        Analisa somente as caixas OMR pertencentes
        à página informada.

        Página 1 -> coordenadas com pagina=1
        Página 2 -> coordenadas com pagina=2
        etc.

        Para mapas antigos que não possuam o campo
        "pagina", assume página 1.
        """

        if imagem is None:
            raise ValueError(
                "A imagem recebida é inválida."
            )

        try:
            pagina = int(
                pagina
            )
        except (
            TypeError,
            ValueError
        ):
            raise ValueError(
                "O número da página deve ser inteiro."
            )

        if pagina < 1:
            raise ValueError(
                "O número da página deve ser maior ou igual a 1."
            )

        imagem_cv = np.array(
            imagem
        )

        if len(
            imagem_cv.shape
        ) == 3:

            imagem_cinza = cv2.cvtColor(
                imagem_cv,
                cv2.COLOR_RGB2GRAY
            )

        else:

            imagem_cinza = imagem_cv

        # ==================================================
        # FILTRAR COORDENADAS DA PÁGINA
        # ==================================================

        coordenadas = []

        for item in self.mapa[
            "coordenadas"
        ]:

            pagina_item = item.get(
                "pagina",
                1
            )

            try:
                pagina_item = int(
                    pagina_item
                )
            except (
                TypeError,
                ValueError
            ):
                pagina_item = 1

            if pagina_item == pagina:
                coordenadas.append(
                    item
                )

        resultados = []

        for item in coordenadas:

            resultado = self.analisar_caixa(
                imagem_cinza,
                item
            )

            resultados.append(
                resultado
            )

        return resultados

    # ======================================================
    # ANALISAR CAIXA
    # ======================================================

    def analisar_caixa(
        self,
        imagem_cinza,
        coordenada
    ):

        x1 = int(
            coordenada["x1"]
        )

        y1 = int(
            coordenada["y1"]
        )

        x2 = int(
            coordenada["x2"]
        )

        y2 = int(
            coordenada["y2"]
        )

        x_inicio = min(
            x1,
            x2
        )

        x_fim = max(
            x1,
            x2
        )

        y_inicio = min(
            y1,
            y2
        )

        y_fim = max(
            y1,
            y2
        )

        # ==================================================
        # APLICAR MARGEM
        # ==================================================

        x_inicio += self.margem
        y_inicio += self.margem

        x_fim -= self.margem
        y_fim -= self.margem

        # ==================================================
        # VALIDAR REGIÃO
        # ==================================================

        if (
            x_fim <= x_inicio
            or
            y_fim <= y_inicio
        ):

            return {
                "nome": coordenada["nome"],
                "pagina": coordenada.get(
                    "pagina",
                    1
                ),
                "pixels_escuros": 0,
                "total_pixels": 0,
                "percentual_escuro": 0.0,
                "marcada": False
            }

        regiao = imagem_cinza[
            y_inicio:y_fim,
            x_inicio:x_fim
        ]

        if regiao.size == 0:

            return {
                "nome": coordenada["nome"],
                "pagina": coordenada.get(
                    "pagina",
                    1
                ),
                "pixels_escuros": 0,
                "total_pixels": 0,
                "percentual_escuro": 0.0,
                "marcada": False
            }

        # ==================================================
        # OMR
        # ==================================================

        limite_escuro = 150

        pixels_escuros = np.sum(
            regiao < limite_escuro
        )

        total_pixels = regiao.size

        percentual = (
            pixels_escuros
            /
            total_pixels
        ) * 100

        marcada = (
            percentual >= 5.0
        )

        return {
            "nome": coordenada["nome"],
            "pagina": coordenada.get(
                "pagina",
                1
            ),
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "pixels_escuros": int(
                pixels_escuros
            ),
            "total_pixels": int(
                total_pixels
            ),
            "percentual_escuro": round(
                percentual,
                2
            ),
            "marcada": marcada
        }