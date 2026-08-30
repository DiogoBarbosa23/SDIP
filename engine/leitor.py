import json
import os

import cv2
import fitz
import numpy as np
from PIL import Image

from engine.geometria import normalizar
from engine.gerador_ficha import GeradorFicha
from engine.omr import OMRReader


class LeitorFicha:
    """Integra PDF escaneado + geometria + OMR + estrutura da ficha."""

    DPI = 600
    MARGEM_OMR_PADRAO = 7

    def __init__(self, mapa_path, dados_ficha, ficha_id=None):
        self.mapa_path = os.path.abspath(mapa_path)
        self.dados_ficha = dados_ficha or {}
        self.ficha_id = ficha_id

        if not os.path.isfile(self.mapa_path):
            raise FileNotFoundError(
                f"Mapa OMR não encontrado: {self.mapa_path}"
            )

        with open(self.mapa_path, "r", encoding="utf-8") as arquivo:
            self.mapa = json.load(arquivo)

        self.quantidade_paginas_mapa = int(
            self.mapa.get("quantidade_paginas", 0)
        )

        self.margem_omr = int(
            self.mapa.get(
                "caixa_omr_margem",
                self.MARGEM_OMR_PADRAO
            )
        )

    @staticmethod
    def _renderizar_pagina(pagina, dpi=600):
        escala = dpi / 72.0
        pix = pagina.get_pixmap(
            matrix=fitz.Matrix(escala, escala),
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
            return cv2.cvtColor(
                imagem,
                cv2.COLOR_RGB2BGR
            )

        if pix.n == 4:
            return cv2.cvtColor(
                imagem,
                cv2.COLOR_RGBA2BGR
            )

        raise ValueError(
            f"Formato de imagem não suportado: {pix.n} canais."
        )

    def ler_pdf(self, caminho_pdf):
        caminho_pdf = os.path.abspath(caminho_pdf)

        if not os.path.isfile(caminho_pdf):
            raise FileNotFoundError(
                f"PDF não encontrado: {caminho_pdf}"
            )

        documento = fitz.open(caminho_pdf)

        try:
            total_paginas = documento.page_count

            if total_paginas <= 0:
                raise ValueError("O PDF não possui páginas.")

            if (
                self.quantidade_paginas_mapa
                and self.quantidade_paginas_mapa != total_paginas
            ):
                raise ValueError(
                    "A quantidade de páginas do PDF não corresponde "
                    "ao mapa da ficha ativa.\n\n"
                    f"PDF: {total_paginas}\n"
                    f"Mapa: {self.quantidade_paginas_mapa}\n\n"
                    "Confirme que o PDF foi gerado a partir da ficha ativa."
                )

            omr = OMRReader(
                mapa_path=self.mapa_path,
                margem=self.margem_omr
            )

            resultados_paginas = []

            for indice in range(total_paginas):
                numero_pagina = indice + 1
                imagem = self._renderizar_pagina(
                    documento[indice],
                    dpi=self.DPI
                )

                normalizada = normalizar(
                    imagem,
                    pagina=numero_pagina
                )

                imagem_rgb = cv2.cvtColor(
                    normalizada,
                    cv2.COLOR_BGR2RGB
                )

                imagem_pil = Image.fromarray(
                    imagem_rgb
                )

                resultados = omr.analisar_imagem(
                    imagem_pil,
                    pagina=numero_pagina
                )

                resultados_paginas.append({
                    "pagina": numero_pagina,
                    "resultados": resultados
                })

            resultados_caixas = []
            for pagina in resultados_paginas:
                resultados_caixas.extend(
                    pagina["resultados"]
                )

            return self._montar_resultado(
                resultados_paginas,
                resultados_caixas
            )

        finally:
            documento.close()

    def _montar_resultado(
        self,
        resultados_paginas,
        resultados_caixas
    ):
        perguntas = []

        for elemento in self.dados_ficha.get("elementos", []):
            if elemento.get("tipo", "pergunta") != "pergunta":
                continue

            pergunta = dict(elemento)

            if pergunta.get("tipo_resposta") == "aberta":
                continue

            perguntas.append(pergunta)

        marcadas = {
            item["nome"]
            for item in resultados_caixas
            if item.get("marcada")
        }

        respostas = {}
        erros = []

        for pergunta in perguntas:
            numero = str(pergunta.get("numero", "")).strip()
            opcoes = list(pergunta.get("opcoes", []))
            selecionadas = []

            for indice, opcao in enumerate(opcoes, start=1):
                nome = GeradorFicha._gerar_nome_opcao(
                    numero,
                    opcao,
                    indice
                )

                if nome in marcadas:
                    selecionadas.append(opcao)

            tipo_resposta = pergunta.get(
                "tipo_resposta",
                "unica"
            )

            if tipo_resposta == "unica":
                if len(selecionadas) > 1:
                    erros.append({
                        "numero": numero,
                        "tipo": "multipla_marcacao_em_resposta_unica",
                        "mensagem": (
                            "A pergunta de resposta única possui "
                            f"{len(selecionadas)} opções marcadas."
                        ),
                        "opcoes": selecionadas
                    })

                respostas[numero] = (
                    selecionadas[0]
                    if len(selecionadas) == 1
                    else ""
                )

            else:
                respostas[numero] = " | ".join(
                    selecionadas
                )

        total_caixas = len(resultados_caixas)
        total_marcadas = sum(
            1
            for item in resultados_caixas
            if item.get("marcada")
        )

        return {
            "ficha_id": self.ficha_id,
            "quantidade_paginas": len(resultados_paginas),
            "total_caixas": total_caixas,
            "total_marcadas": total_marcadas,
            "total_vazias": total_caixas - total_marcadas,
            "respostas_omr": respostas,
            "erros_validacao": erros,
            "resultados_paginas": resultados_paginas,
        }
