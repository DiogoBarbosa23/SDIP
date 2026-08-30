# ==========================================================
# engine/geometria.py
# ==========================================================
#
# Correção geométrica das fichas SDIP.
#
# Fluxo:
#
#   imagem do scanner
#       ↓
#   detectar ArUcos da página
#       ↓
#   localizar os 4 ArUcos da página
#       ↓
#   calcular homografia
#       ↓
#   normalizar para 1191 x 1684
#       ↓
#   devolver imagem pronta para OMR
#
# IDs dos ArUcos por página:
#
#   Página 1 → 0, 1, 2, 3
#   Página 2 → 4, 5, 6, 7
#   Página 3 → 8, 9, 10, 11
#   ...
#
# ==========================================================

import cv2
import numpy as np


# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

LARGURA_MAPA = 1191
ALTURA_MAPA = 1684

ARUCO_DICIONARIO = cv2.aruco.DICT_4X4_50
ARUCOS_POR_PAGINA = 4


# ==========================================================
# POSIÇÕES DE DESTINO
# ==========================================================
#
# A geometria relativa é sempre:
#
#   base + 0 = superior esquerdo
#   base + 1 = superior direito
#   base + 2 = inferior direito
#   base + 3 = inferior esquerdo
#
# ==========================================================

PONTOS_DESTINO = {
    0: (
        167.21,
        167.18
    ),
    1: (
        1023.55,
        167.18
    ),
    2: (
        1023.55,
        1516.58
    ),
    3: (
        167.21,
        1516.58
    )
}


# ==========================================================
# OBTER IDS DA PÁGINA
# ==========================================================

def obter_ids_referencia(
    pagina=1
):
    """
    Retorna os quatro IDs ArUco esperados para a página.

    Página 1 → {0, 1, 2, 3}
    Página 2 → {4, 5, 6, 7}
    Página 3 → {8, 9, 10, 11}
    """

    try:
        pagina = int(pagina)
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

    ids_base = (
        (pagina - 1)
        * ARUCOS_POR_PAGINA
    )

    return {
        ids_base,
        ids_base + 1,
        ids_base + 2,
        ids_base + 3
    }


# ==========================================================
# DETECTOR ARUCO
# ==========================================================

def _criar_detector_aruco():
    """
    Cria o detector ArUco compatível com OpenCV 4.12.
    """

    dicionario = (
        cv2.aruco.getPredefinedDictionary(
            ARUCO_DICIONARIO
        )
    )

    parametros = cv2.aruco.DetectorParameters()

    detector = cv2.aruco.ArucoDetector(
        dicionario,
        parametros
    )

    return detector


# ==========================================================
# DETECTAR ARUCOS
# ==========================================================

def detectar_pontos_referencia(
    imagem,
    pagina=1
):
    """
    Detecta os quatro ArUcos da página informada.

    Retorna um dicionário normalizado pelas posições
    relativas 0, 1, 2 e 3.

    Exemplo para página 2:

        {
            0: dados do ID 4,
            1: dados do ID 5,
            2: dados do ID 6,
            3: dados do ID 7
        }

    Isso permite que a homografia continue usando
    sempre as posições 0, 1, 2 e 3 internamente.
    """

    if imagem is None:
        raise ValueError(
            "A imagem recebida é inválida."
        )

    if imagem.ndim != 3:
        raise ValueError(
            "A imagem precisa estar em BGR."
        )

    ids_esperados = obter_ids_referencia(
        pagina
    )

    detector = _criar_detector_aruco()

    # ------------------------------------------------------
    # Converter para tons de cinza.
    # ------------------------------------------------------

    cinza = cv2.cvtColor(
        imagem,
        cv2.COLOR_BGR2GRAY
    )

    # ------------------------------------------------------
    # Detectar ArUcos.
    # ------------------------------------------------------

    (
        cantos,
        ids,
        _rejeitados
    ) = detector.detectMarkers(
        cinza
    )

    encontrados = {}

    if ids is None:
        return encontrados

    ids = ids.flatten()

    # Mapeia ID real para posição relativa da página.
    ids_por_posicao = {
        id_aruco: indice
        for indice, id_aruco
        in enumerate(
            sorted(ids_esperados)
        )
    }

    for indice, id_aruco in enumerate(ids):

        id_aruco = int(
            id_aruco
        )

        if id_aruco not in ids_esperados:
            continue

        cantos_marcador = (
            cantos[indice][0]
        )

        # --------------------------------------------------
        # Centro geométrico dos quatro cantos.
        # --------------------------------------------------

        centro = np.mean(
            cantos_marcador,
            axis=0
        )

        centro_x = float(
            centro[0]
        )

        centro_y = float(
            centro[1]
        )

        # --------------------------------------------------
        # Contorno inteiro do marcador.
        # --------------------------------------------------

        contorno = (
            np.round(
                cantos_marcador
            )
            .astype(
                np.int32
            )
            .reshape(
                -1,
                1,
                2
            )
        )

        posicao = ids_por_posicao[
            id_aruco
        ]

        encontrados[posicao] = {
            "id": id_aruco,
            "centro": (
                centro_x,
                centro_y
            ),
            "cantos": cantos_marcador,
            "contorno": contorno
        }

    return encontrados


# ==========================================================
# VALIDAR REFERÊNCIAS
# ==========================================================

def validar_pontos_referencia(
    pontos,
    pagina=1
):
    """
    Verifica se os quatro ArUcos esperados para a página
    foram encontrados.
    """

    ids_esperados = {
        0,
        1,
        2,
        3
    }

    faltantes = (
        ids_esperados
        -
        set(
            pontos.keys()
        )
    )

    if faltantes:
        ids_reais_esperados = sorted(
            obter_ids_referencia(
                pagina
            )
        )

        raise ValueError(
            "Não foi possível localizar "
            "os quatro ArUcos de referência.\n\n"
            f"Página: {pagina}\n"
            f"IDs esperados: {ids_reais_esperados}\n"
            f"Posições faltantes: {sorted(faltantes)}"
        )


# ==========================================================
# CALCULAR HOMOGRAFIA
# ==========================================================

def calcular_homografia(
    pontos
):
    """
    Calcula a homografia usando as quatro posições
    relativas da página:
        0 = superior esquerdo
        1 = superior direito
        2 = inferior direito
        3 = inferior esquerdo
    """

    origem = np.array(
        [
            pontos[0]["centro"],
            pontos[1]["centro"],
            pontos[2]["centro"],
            pontos[3]["centro"]
        ],
        dtype=np.float32
    )

    destino = np.array(
        [
            PONTOS_DESTINO[0],
            PONTOS_DESTINO[1],
            PONTOS_DESTINO[2],
            PONTOS_DESTINO[3]
        ],
        dtype=np.float32
    )

    matriz = cv2.getPerspectiveTransform(
        origem,
        destino
    )

    return matriz


# ==========================================================
# NORMALIZAR
# ==========================================================

def normalizar(
    imagem,
    pagina=1
):
    """
    Detecta os quatro ArUcos da página informada,
    calcula a homografia e normaliza a imagem
    para 1191 x 1684.
    """

    if imagem is None:
        raise ValueError(
            "A imagem recebida é inválida."
        )

    if imagem.ndim != 3:
        raise ValueError(
            "A imagem precisa estar em BGR."
        )

    pontos = detectar_pontos_referencia(
        imagem,
        pagina=pagina
    )

    validar_pontos_referencia(
        pontos,
        pagina=pagina
    )

    matriz = calcular_homografia(
        pontos
    )

    normalizada = cv2.warpPerspective(
        imagem,
        matriz,
        (
            LARGURA_MAPA,
            ALTURA_MAPA
        ),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(
            255,
            255,
            255
        )
    )

    return normalizada


# ==========================================================
# NORMALIZAR COM DIAGNÓSTICO
# ==========================================================

def normalizar_com_diagnostico(
    imagem,
    pagina=1
):
    """
    Igual a normalizar(), mas também devolve:

    - imagem normalizada;
    - imagem de diagnóstico;
    - pontos encontrados;
    - matriz de homografia.
    """

    if imagem is None:
        raise ValueError(
            "A imagem recebida é inválida."
        )

    if imagem.ndim != 3:
        raise ValueError(
            "A imagem precisa estar em BGR."
        )

    pontos = detectar_pontos_referencia(
        imagem,
        pagina=pagina
    )

    validar_pontos_referencia(
        pontos,
        pagina=pagina
    )

    matriz = calcular_homografia(
        pontos
    )

    normalizada = cv2.warpPerspective(
        imagem,
        matriz,
        (
            LARGURA_MAPA,
            ALTURA_MAPA
        ),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(
            255,
            255,
            255
        )
    )

    # ======================================================
    # DIAGNÓSTICO
    # ======================================================

    diagnostico = imagem.copy()

    cores = {
        0: (0, 255, 0),
        1: (255, 0, 0),
        2: (0, 255, 255),
        3: (0, 0, 255)
    }

    for posicao in range(4):

        dados = pontos[
            posicao
        ]

        cantos = np.array(
            dados["contorno"],
            dtype=np.int32
        )

        cx, cy = (
            dados["centro"]
        )

        cor = cores[
            posicao
        ]

        # --------------------------------------------------
        # Desenhar contorno real do ArUco.
        # --------------------------------------------------

        cv2.polylines(
            diagnostico,
            [
                cantos
            ],
            True,
            cor,
            8
        )

        # --------------------------------------------------
        # Centro.
        # --------------------------------------------------

        cv2.circle(
            diagnostico,
            (
                int(cx),
                int(cy)
            ),
            20,
            cor,
            -1
        )

        # --------------------------------------------------
        # ID real.
        # --------------------------------------------------

        cv2.putText(
            diagnostico,
            f"ARUCO {dados['id']}",
            (
                int(cx) + 30,
                int(cy)
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.8,
            cor,
            5,
            cv2.LINE_AA
        )

    return (
        normalizada,
        diagnostico,
        pontos,
        matriz
    )