from PIL import Image, ImageDraw, ImageFont

from engine.gerador_ficha import GeradorFicha


# ==========================================================
# CONFIGURAÇÃO DA FICHA
# ==========================================================

LARGURA = 1191
ALTURA = 1684

MARGEM = 80

TAMANHO_TITULO = 42
TAMANHO_PERGUNTA = 28
TAMANHO_OPCAO = 24

TAMANHO_CAIXA = 24
ESPACO_OPCAO = 45
ESPACO_PERGUNTA = 35


# ==========================================================
# FONTE
# ==========================================================

def carregar_fonte(tamanho):
    try:
        return ImageFont.truetype(
            "arial.ttf",
            tamanho
        )
    except OSError:
        return ImageFont.load_default()


# ==========================================================
# CRIAR FICHA DE TESTE
# ==========================================================

ficha = GeradorFicha(
    nome_pesquisa="Reforma no Lar",
    titulo="Pesquisa de Satisfação"
)

ficha.adicionar_pergunta(
    texto="A obra foi concluída?",
    tipo_resposta="unica",
    opcoes=[
        "Sim",
        "Não"
    ]
)

ficha.adicionar_pergunta(
    texto="Qual serviço foi realizado?",
    tipo_resposta="multipla",
    opcoes=[
        "Barra de apoio",
        "Corrimão",
        "Rampa",
        "Outros"
    ]
)


dados = ficha.obter_ficha()


# ==========================================================
# CRIAR IMAGEM A4
# ==========================================================

imagem = Image.new(
    "RGB",
    (LARGURA, ALTURA),
    "white"
)

desenho = ImageDraw.Draw(imagem)


fonte_titulo = carregar_fonte(
    TAMANHO_TITULO
)

fonte_pergunta = carregar_fonte(
    TAMANHO_PERGUNTA
)

fonte_opcao = carregar_fonte(
    TAMANHO_OPCAO
)


# ==========================================================
# TÍTULO
# ==========================================================

y = MARGEM

desenho.text(
    (
        MARGEM,
        y
    ),
    dados["titulo"],
    fill="black",
    font=fonte_titulo
)

y += 90


# ==========================================================
# PERGUNTAS
# ==========================================================

for numero, pergunta in enumerate(
    dados["perguntas"],
    start=1
):

    texto_pergunta = (
        f"{numero}. {pergunta['texto']}"
    )

    desenho.text(
        (
            MARGEM,
            y
        ),
        texto_pergunta,
        fill="black",
        font=fonte_pergunta
    )

    y += 50

    for opcao in pergunta["opcoes"]:

        # Coordenada da caixa
        x_caixa = MARGEM
        y_caixa = y

        # Caixa OMR
        desenho.rectangle(
            (
                x_caixa,
                y_caixa,
                x_caixa + TAMANHO_CAIXA,
                y_caixa + TAMANHO_CAIXA
            ),
            outline="black",
            width=2
        )

        # Texto da opção
        desenho.text(
            (
                x_caixa + TAMANHO_CAIXA + 15,
                y_caixa - 3
            ),
            opcao,
            fill="black",
            font=fonte_opcao
        )

        y += ESPACO_OPCAO

    y += ESPACO_PERGUNTA


# ==========================================================
# SALVAR
# ==========================================================

saida = "temp/ficha_gerada_teste.png"

imagem.save(
    saida
)

print("=" * 60)
print("GERADOR DE FICHA — TESTE VISUAL")
print("=" * 60)
print(f"Arquivo gerado: {saida}")
print(f"Tamanho: {LARGURA} x {ALTURA}")
print("=" * 60)