import os
import json
import cv2
import fitz
import numpy as np

from engine.geometria import normalizar_com_diagnostico


PDF_PATH = "uploads/gtibranco.pdf"
MAPA_PATH = "temp/mapa_caixas_gerado.json"

SAIDA_NORMALIZADA = "temp/diagnostico_nova_ficha_normalizada.png"


def main():
    print("=" * 70)
    print("SDIP - DIAGNÓSTICO DA FICHA GERADA")
    print("=" * 70)

    # ----------------------------------------------------------
    # Verificar arquivos
    # ----------------------------------------------------------

    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(
            f"PDF não encontrado: {PDF_PATH}"
        )

    if not os.path.exists(MAPA_PATH):
        raise FileNotFoundError(
            f"Mapa não encontrado: {MAPA_PATH}"
        )

    # ----------------------------------------------------------
    # Carregar mapa
    # ----------------------------------------------------------

    with open(
        MAPA_PATH,
        "r",
        encoding="utf-8"
    ) as arquivo:
        mapa = json.load(arquivo)

    coordenadas = mapa["coordenadas"]

    print()
    print("Mapa carregado")
    print(
        f"Caixas no mapa: {len(coordenadas)}"
    )

    print(
        f"Páginas no mapa: "
        f"{mapa.get('quantidade_paginas')}"
    )

    # ----------------------------------------------------------
    # Abrir PDF
    # ----------------------------------------------------------

    documento = fitz.open(PDF_PATH)

    try:
        print()
        print(
            f"Páginas no PDF: "
            f"{documento.page_count}"
        )

        if documento.page_count != 1:
            raise ValueError(
                "Este diagnóstico espera exatamente 1 página."
            )

        pagina = documento[0]

        # ------------------------------------------------------
        # Renderização em 600 DPI
        # ------------------------------------------------------

        dpi = 600
        escala = dpi / 72.0

        pix = pagina.get_pixmap(
            matrix=fitz.Matrix(
                escala,
                escala
            ),
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
                f"Formato inesperado: {pix.n} canais."
            )

        print()
        print(
            "Imagem escaneada:"
        )

        print(
            f"{imagem.shape[1]} x "
            f"{imagem.shape[0]}"
        )

        # ------------------------------------------------------
        # Geometria
        # ------------------------------------------------------

        print()
        print(
            "Executando normalização..."
        )

        (
            normalizada,
            diagnostico,
            pontos,
            matriz
        ) = normalizar_com_diagnostico(
            imagem
        )

        print()
        print(
            "Pontos detectados:"
        )

        for id_ponto in sorted(
            pontos.keys()
        ):
            centro = pontos[
                id_ponto
            ]["centro"]

            print(
                f"  {id_ponto}: "
                f"({centro[0]:.2f}, "
                f"{centro[1]:.2f})"
            )

        print()
        print(
            "Imagem normalizada:"
        )

        print(
            f"{normalizada.shape[1]} x "
            f"{normalizada.shape[0]}"
        )

        cv2.imwrite(
            SAIDA_NORMALIZADA,
            normalizada
        )

        print()
        print(
            f"Normalizada salva em: "
            f"{SAIDA_NORMALIZADA}"
        )

        # ------------------------------------------------------
        # Converter para cinza
        # ------------------------------------------------------

        cinza = cv2.cvtColor(
            normalizada,
            cv2.COLOR_BGR2GRAY
        )

        # ------------------------------------------------------
        # Analisar caixas diretamente
        # ------------------------------------------------------

        print()
        print("=" * 70)
        print("ANÁLISE DAS CAIXAS")
        print("=" * 70)

        marcadas = 0

        for item in coordenadas:

            x1 = int(item["x1"])
            y1 = int(item["y1"])
            x2 = int(item["x2"])
            y2 = int(item["y2"])

            margem = 4

            x_inicio = min(x1, x2) + margem
            x_fim = max(x1, x2) - margem

            y_inicio = min(y1, y2) + margem
            y_fim = max(y1, y2) - margem

            regiao = cinza[
                y_inicio:y_fim,
                x_inicio:x_fim
            ]

            if regiao.size == 0:
                percentual = 0.0
            else:
                pixels_escuros = np.sum(
                    regiao < 150
                )

                percentual = (
                    pixels_escuros /
                    regiao.size
                ) * 100

            marcada = percentual >= 5.0

            if marcada:
                marcadas += 1

            estado = (
                "MARCADA"
                if marcada
                else "VAZIA"
            )

            print(
                f"{item['nome']:<35} "
                f"{percentual:>7.2f}% "
                f"{estado:<8} "
                f"({x1},{y1})"
            )

        # ------------------------------------------------------
        # Resumo
        # ------------------------------------------------------

        print()
        print("=" * 70)
        print("RESUMO")
        print("=" * 70)

        print(
            f"Total de caixas: {len(coordenadas)}"
        )

        print(
            f"Marcadas: {marcadas}"
        )

        print(
            f"Vazias: "
            f"{len(coordenadas) - marcadas}"
        )

        print("=" * 70)

        # ------------------------------------------------------
        # Mostrar maiores percentuais
        # ------------------------------------------------------

        resultados = []

        for item in coordenadas:

            x1 = int(item["x1"])
            y1 = int(item["y1"])
            x2 = int(item["x2"])
            y2 = int(item["y2"])

            margem = 4

            regiao = cinza[
                y1 + margem:y2 - margem,
                x1 + margem:x2 - margem
            ]

            if regiao.size == 0:
                percentual = 0.0
            else:
                percentual = (
                    np.sum(regiao < 150)
                    / regiao.size
                ) * 100

            resultados.append(
                (
                    percentual,
                    item["nome"]
                )
            )

        resultados.sort(
            reverse=True
        )

        print()
        print(
            "10 maiores percentuais:"
        )

        for percentual, nome in resultados[:10]:
            print(
                f"{nome:<35} "
                f"{percentual:>7.2f}%"
            )

    finally:
        documento.close()


if __name__ == "__main__":
    main()