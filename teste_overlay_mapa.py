import json
import cv2


IMAGEM = "temp/diagnostico_nova_ficha_normalizada.png"
MAPA = "temp/mapa_caixas_gerado.json"
SAIDA = "temp/overlay_mapa.png"


def main():
    imagem = cv2.imread(IMAGEM)

    if imagem is None:
        raise FileNotFoundError(
            f"Imagem não encontrada: {IMAGEM}"
        )

    with open(
        MAPA,
        "r",
        encoding="utf-8"
    ) as arquivo:
        mapa = json.load(arquivo)

    for item in mapa["coordenadas"]:

        x1 = int(item["x1"])
        y1 = int(item["y1"])
        x2 = int(item["x2"])
        y2 = int(item["y2"])

        # Desenha o retângulo da caixa OMR.
        cv2.rectangle(
            imagem,
            (x1, y1),
            (x2, y2),
            (0, 0, 255),
            2
        )

        # Nome da caixa.
        cv2.putText(
            imagem,
            item["nome"],
            (x1, max(15, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (0, 0, 255),
            1,
            cv2.LINE_AA
        )

    cv2.imwrite(
        SAIDA,
        imagem
    )

    print("=" * 60)
    print("OVERLAY DO MAPA OMR")
    print("=" * 60)
    print()
    print(f"Imagem: {IMAGEM}")
    print(f"Mapa:   {MAPA}")
    print(f"Saída:  {SAIDA}")
    print()
    print("Abra a imagem de saída e confira")
    print("se os quadrados vermelhos estão exatamente")
    print("sobre as caixas impressas.")
    print("=" * 60)


if __name__ == "__main__":
    main()