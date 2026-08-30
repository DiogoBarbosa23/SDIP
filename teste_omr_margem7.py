import os
import cv2
import fitz
import numpy as np

from engine.geometria import normalizar
from engine.omr import OMRReader


PDF_PATH = "uploads/gtimarcada.pdf"
MAPA_PATH = "temp/mapa_caixas_gerado.json"


def main():
    print("=" * 70)
    print("SDIP - TESTE OMR COM MARGEM 7")
    print("=" * 70)

    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(PDF_PATH)

    if not os.path.exists(MAPA_PATH):
        raise FileNotFoundError(MAPA_PATH)

    documento = fitz.open(PDF_PATH)

    try:
        if documento.page_count != 1:
            raise ValueError(
                "Este teste espera exatamente 1 página."
            )

        pagina = documento[0]

        escala = 600 / 72.0

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

        omr = OMRReader(
            mapa_path=MAPA_PATH,
            margem=7
        )

        resultados = omr.analisar_imagem(
            normalizada
        )

        print()
        print("=" * 70)
        print("RESULTADOS")
        print("=" * 70)

        marcadas = 0

        for resultado in resultados:

            if resultado["marcada"]:
                marcadas += 1

            estado = (
                "MARCADA"
                if resultado["marcada"]
                else "VAZIA"
            )

            print(
                f"{resultado['nome']:<35} "
                f"{resultado['percentual_escuro']:>7.2f}% "
                f"{estado}"
            )

        print("=" * 70)
        print(
            f"Total de caixas: {len(resultados)}"
        )
        print(
            f"Marcadas: {marcadas}"
        )
        print(
            f"Vazias: {len(resultados) - marcadas}"
        )
        print("=" * 70)

    finally:
        documento.close()


if __name__ == "__main__":
    main()