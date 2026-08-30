import json
import cv2


IMAGEM_PATH = "temp/ficha_teste_layout_1.png"
MAPA_PATH = "temp/mapa_caixas_gerado.json"


def main():

    imagem = cv2.imread(
        IMAGEM_PATH
    )

    if imagem is None:
        raise FileNotFoundError(
            f"Imagem não encontrada: {IMAGEM_PATH}"
        )

    with open(
        MAPA_PATH,
        "r",
        encoding="utf-8"
    ) as arquivo:
        mapa = json.load(arquivo)

    cinza = cv2.cvtColor(
        imagem,
        cv2.COLOR_BGR2GRAY
    )

    marcadas = 0

    print("=" * 70)
    print("TESTE OMR DIRETO NA PNG GERADA")
    print("=" * 70)

    for item in mapa["coordenadas"]:

        x1 = int(item["x1"])
        y1 = int(item["y1"])
        x2 = int(item["x2"])
        y2 = int(item["y2"])

        margem = 4

        regiao = cinza[
            y1 + margem:y2 - margem,
            x1 + margem:x2 - margem
        ]

        pixels_escuros = (
            (regiao < 150).sum()
        )

        total_pixels = regiao.size

        percentual = (
            pixels_escuros
            / total_pixels
            * 100
        )

        marcada = percentual >= 5.0

        if marcada:
            marcadas += 1

        print(
            f"{item['nome']:<35} "
            f"{percentual:>7.2f}% "
            f"{'MARCADA' if marcada else 'VAZIA'}"
        )

    print("=" * 70)
    print(
        f"Total: {len(mapa['coordenadas'])}"
    )
    print(
        f"Marcadas: {marcadas}"
    )
    print(
        f"Vazias: "
        f"{len(mapa['coordenadas']) - marcadas}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
    