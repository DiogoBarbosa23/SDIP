from engine.gerador_ficha import GeradorFicha


ficha = GeradorFicha(
    nome_pesquisa="Pesquisa de Satisfação",
    titulo="Avaliação dos Serviços",
    logo_path=None
)


# ==========================================================
# PERGUNTAS
# ==========================================================

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
        "Pintura",
        "Instalação elétrica",
        "Outros"
    ]
)

ficha.adicionar_pergunta(
    texto="Como você avalia a qualidade da reforma?",
    tipo_resposta="unica",
    opcoes=[
        "Péssimo",
        "Ruim",
        "Regular",
        "Bom",
        "Muito bom"
    ]
)

ficha.adicionar_pergunta(
    texto="O serviço atendeu às suas necessidades?",
    tipo_resposta="unica",
    opcoes=[
        "Sim",
        "Não",
        "Parcialmente"
    ]
)

ficha.adicionar_pergunta(
    texto="Como você avalia o atendimento recebido?",
    tipo_resposta="unica",
    opcoes=[
        "Péssimo",
        "Ruim",
        "Regular",
        "Bom",
        "Muito bom"
    ]
)

ficha.adicionar_pergunta(
    texto="Quais melhorias você considera mais importantes?",
    tipo_resposta="multipla",
    opcoes=[
        "Acessibilidade",
        "Segurança",
        "Iluminação",
        "Pintura",
        "Instalações",
        "Estrutura"
    ]
)

ficha.adicionar_pergunta(
    texto="O prazo para realização do serviço foi adequado?",
    tipo_resposta="unica",
    opcoes=[
        "Sim",
        "Não"
    ]
)

ficha.adicionar_pergunta(
    texto="Como você avalia o resultado final?",
    tipo_resposta="unica",
    opcoes=[
        "Péssimo",
        "Ruim",
        "Regular",
        "Bom",
        "Muito bom"
    ]
)

ficha.adicionar_pergunta(
    texto="Você recomendaria o programa?",
    tipo_resposta="unica",
    opcoes=[
        "Sim",
        "Não"
    ]
)

ficha.adicionar_pergunta(
    texto="Qual área precisa de mais atenção?",
    tipo_resposta="multipla",
    opcoes=[
        "Educação",
        "Saúde",
        "Segurança",
        "Saneamento",
        "Lazer",
        "Transporte"
    ]
)

ficha.adicionar_pergunta(
    texto="Como você avalia a comunicação durante a obra?",
    tipo_resposta="unica",
    opcoes=[
        "Péssimo",
        "Ruim",
        "Regular",
        "Bom",
        "Muito bom"
    ]
)

ficha.adicionar_pergunta(
    texto="Você ficou satisfeito com o serviço realizado?",
    tipo_resposta="unica",
    opcoes=[
        "Sim",
        "Não",
        "Parcialmente"
    ]
)


# ==========================================================
# GERAR
# ==========================================================

print("=" * 60)
print("TESTE DO GERADOR DE FICHA + MAPA OMR")
print("=" * 60)

print()
print(
    "Quantidade de perguntas:",
    len(ficha.perguntas)
)

print()
print("Gerando ficha visual...")

caminho_imagem = (
    "temp/ficha_teste_layout.png"
)

caminho_mapa = (
    "temp/mapa_caixas_gerado.json"
)

paginas = ficha.gerar_imagem(
    caminho_imagem
)

ficha.gerar_mapa_omr(
    caminho_mapa
)


# ==========================================================
# RESULTADO
# ==========================================================

print()
print("Páginas geradas:")

for pagina in paginas:
    print(
        f"- {pagina}"
    )

print()
print("Mapa OMR gerado:")
print(
    f"- {caminho_mapa}"
)

print()
print(
    "Quantidade de páginas:",
    len(paginas)
)

print(
    "Caixas OMR registradas:",
    len(ficha.coordenadas_omr)
)

print()
print("=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)