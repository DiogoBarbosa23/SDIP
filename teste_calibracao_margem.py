import os
import cv2
import fitz
import numpy as np

from engine.geometria import normalizar
from engine.omr import OMRReader


PDF_PATH = "uploads/gtibranco.pdf"
MAPA_PATH = "temp/mapa_caixas_gerado.json"

MARGENS = [4, 5, 6, 7, 8, 10]


def main():
    print("=" * 70)
    print("SDIP - CALIBRAÇÃO DA MARGEM OMR")
    print("=" * 70)

    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(PDF_PATH)

    if not os.path.exists(MAPA_PATH):
        raise FileNotFoundError(MAPA_PATH)

    documento = fitz.open(PDF_PATH)

    try:
        if documento.page_count != 1:
            raise ValueError(
                "O teste espera exatamente 1 página."
            )

        pagina = documento[0]

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
                f"Canais não suportados: {pix.n}"
            )

        print()
        print("Normalizando imagem...")

        normalizada = normalizar(
            imagem
        )

        print(
            f"Imagem normalizada: "
            f"{normalizada.shape[1]} x "
            f"{normalizada.shape[0]}"
        )

        print()
        print("-" * 70)
        print(
            f"{'Margem':<12}"
            f"{'Caixas':<12}"
            f"{'Marcadas':<12}"
            f"{'Vazias':<12}"
        )
        print("-" * 70)

        for margem in MARGENS:

            omr = OMRReader(
                mapa_path=MAPA_PATH,
                margem=margem
            )

            resultados = omr.analisar_imagem(
                normalizada
            )

            total = len(resultados)

            marcadas = sum(
                1
                for resultado in resultados
                if resultado["marcada"]
            )

            vazias = total - marcadas

            print(
                f"{margem:<12}"
                f"{total:<12}"
                f"{marcadas:<12}"
                f"{vazias:<12}"
            )

        print("-" * 70)

    finally:
        documento.close()


if __name__ == "__main__":
    main()