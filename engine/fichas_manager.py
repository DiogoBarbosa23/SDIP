import json
import os
import shutil
import uuid

from datetime import datetime


class FichasManager:

    STATUS_RASCUNHO = "RASCUNHO"
    STATUS_PRODUCAO = "PRODUÇÃO"

    def __init__(self):

        self.base_dir = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        self.fichas_dir = os.path.join(
            self.base_dir,
            "fichas"
        )

        self.arquivo_ativa = os.path.join(
            self.fichas_dir,
            "ativa.json"
        )

        os.makedirs(
            self.fichas_dir,
            exist_ok=True
        )

    # ==========================================================
    # CRIAR ID
    # ==========================================================

    @staticmethod
    def _gerar_id():

        data = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        sufixo = uuid.uuid4().hex[:8]

        return (
            f"ficha_{data}_{sufixo}"
        )

    # ==========================================================
    # CAMINHO DA FICHA
    # ==========================================================

    def _obter_pasta_ficha(
        self,
        ficha_id
    ):

        return os.path.join(
            self.fichas_dir,
            ficha_id
        )

    # ==========================================================
    # CARREGAR QUALQUER FICHA
    # ==========================================================

    def carregar_ficha(
        self,
        ficha_id
    ):

        if not ficha_id:
            return None

        pasta = self._obter_pasta_ficha(ficha_id)

        caminho_dados = os.path.join(
            pasta,
            "dados.json"
        )

        caminho_pdf = os.path.join(
            pasta,
            "ficha.pdf"
        )

        caminho_mapa = os.path.join(
            pasta,
            "mapa_omr.json"
        )

        if not (
            os.path.isfile(caminho_dados)
            and os.path.isfile(caminho_pdf)
            and os.path.isfile(caminho_mapa)
        ):
            return None

        try:
            with open(
                caminho_dados,
                "r",
                encoding="utf-8"
            ) as arquivo:
                dados = json.load(arquivo)

            logo_path = dados.get("logo_path")

            if logo_path:
                caminho_logo = os.path.join(
                    pasta,
                    logo_path
                )

                if os.path.isfile(caminho_logo):
                    dados["logo_path"] = caminho_logo
                else:
                    dados["logo_path"] = None

            # Compatibilidade com fichas antigas.
            if not dados.get("status_producao"):
                dados["status_producao"] = (
                    self.STATUS_PRODUCAO
                    if dados.get("planilha_resultados_path")
                    else self.STATUS_RASCUNHO
                )

            if not dados.get("versao"):
                dados["versao"] = 1

            if not dados.get("pesquisa_id"):
                dados["pesquisa_id"] = ficha_id

            return {
                "ficha_id": ficha_id,
                "pasta": pasta,
                "pdf": caminho_pdf,
                "mapa": caminho_mapa,
                "dados": dados
            }

        except (
            OSError,
            json.JSONDecodeError
        ):
            return None

    # ==========================================================
    # SALVAR FICHA
    # ==========================================================

    def salvar_ficha(
        self,
        dados,
        caminho_pdf,
        caminho_mapa
    ):

        ficha_id = self._gerar_id()

        pasta = self._obter_pasta_ficha(
            ficha_id
        )

        os.makedirs(
            pasta,
            exist_ok=False
        )

        destino_pdf = os.path.join(
            pasta,
            "ficha.pdf"
        )

        destino_mapa = os.path.join(
            pasta,
            "mapa_omr.json"
        )

        destino_dados = os.path.join(
            pasta,
            "dados.json"
        )

        shutil.copy2(
            caminho_pdf,
            destino_pdf
        )

        shutil.copy2(
            caminho_mapa,
            destino_mapa
        )

        dados_salvos = dict(
            dados
        )

        caminho_logo = dados_salvos.pop(
            "logo_path",
            None
        )

        if caminho_logo:

            if not os.path.isfile(
                caminho_logo
            ):

                raise FileNotFoundError(
                    "A logo selecionada não foi encontrada."
                )

            destino_logo = os.path.join(
                pasta,
                "logo.png"
            )

            shutil.copy2(
                caminho_logo,
                destino_logo
            )

            # Guardamos somente o nome do arquivo.
            dados_salvos["logo_path"] = "logo.png"

        else:

            dados_salvos["logo_path"] = None

        # Uma ficha nova começa como rascunho.
        # A planilha só é vinculada quando o usuário confirma produção.
        dados_salvos["ficha_id"] = ficha_id
        dados_salvos["status_producao"] = dados_salvos.get(
            "status_producao",
            self.STATUS_RASCUNHO
        ) or self.STATUS_RASCUNHO
        dados_salvos["versao"] = int(
            dados_salvos.get(
                "versao",
                1
            )
            or 1
        )
        dados_salvos["pesquisa_id"] = (
            dados_salvos.get("pesquisa_id")
            or ficha_id
        )

        # Nova versão nunca deve herdar silenciosamente a planilha da versão anterior.
        if dados_salvos["status_producao"] != self.STATUS_PRODUCAO:
            dados_salvos["planilha_resultados_path"] = None
            dados_salvos["planilha_cabecalhos"] = []

        with open(
            destino_dados,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                dados_salvos,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

        return {
            "ficha_id": ficha_id,
            "pasta": pasta,
            "pdf": destino_pdf,
            "mapa": destino_mapa,
            "dados": destino_dados,
            "logo": (
                os.path.join(
                    pasta,
                    "logo.png"
                )
                if caminho_logo
                else None
            )
        }

    # ==========================================================
    # DEFINIR COMO ATIVA
    # ==========================================================

    def definir_ativa(
        self,
        ficha_id
    ):

        ficha = self.carregar_ficha(ficha_id)

        if not ficha:
            raise FileNotFoundError(
                "A ficha informada não existe ou está incompleta."
            )

        dados_ativa = {
            "ficha_id": ficha_id
        }

        with open(
            self.arquivo_ativa,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                dados_ativa,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

    # ==========================================================
    # OBTER ID DA ATIVA
    # ==========================================================

    def obter_id_ativa(self):

        if not os.path.isfile(
            self.arquivo_ativa
        ):
            return None

        try:
            with open(
                self.arquivo_ativa,
                "r",
                encoding="utf-8"
            ) as arquivo:
                dados = json.load(arquivo)

            return dados.get("ficha_id")

        except (
            OSError,
            json.JSONDecodeError
        ):
            return None

    # ==========================================================
    # CARREGAR FICHA ATIVA
    # ==========================================================

    def carregar_ativa(self):
        return self.carregar_ficha(
            self.obter_id_ativa()
        )

    # ==========================================================
    # ATUALIZAR METADADOS DA FICHA
    # ==========================================================

    def atualizar_dados_ficha(
        self,
        ficha_id,
        alteracoes
    ):

        ficha = self.carregar_ficha(ficha_id)

        if not ficha:
            raise FileNotFoundError(
                "A ficha informada não foi encontrada."
            )

        dados = ficha["dados"]
        dados.update(alteracoes or {})
        dados["ficha_id"] = ficha_id

        caminho_dados = os.path.join(
            ficha["pasta"],
            "dados.json"
        )

        # Ao salvar, reconstruímos o caminho da logo para o formato relativo.
        caminho_logo = dados.get("logo_path")
        if caminho_logo and os.path.abspath(caminho_logo).startswith(
            os.path.abspath(ficha["pasta"]) + os.sep
        ):
            dados["logo_path"] = os.path.relpath(
                caminho_logo,
                ficha["pasta"]
            )

        with open(
            caminho_dados,
            "w",
            encoding="utf-8"
        ) as arquivo:
            json.dump(
                dados,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

        return dados

    # ==========================================================
    # CONFIGURAR PLANILHA DA FICHA
    # ==========================================================

    def salvar_caminho_planilha(
        self,
        ficha_id,
        caminho_planilha,
        cabecalhos=None
    ):

        ficha = self.carregar_ficha(ficha_id)

        if not ficha:
            raise FileNotFoundError(
                "O arquivo da ficha não foi encontrado."
            )

        caminho_planilha = (
            os.path.abspath(caminho_planilha)
            if caminho_planilha
            else None
        )

        alteracoes = {
            "planilha_resultados_path": caminho_planilha,
            "status_producao": self.STATUS_PRODUCAO,
            "planilha_cabecalhos": list(cabecalhos or [])
        }

        return self.atualizar_dados_ficha(
            ficha_id,
            alteracoes
        ).get("planilha_resultados_path")

    # ==========================================================
    # LISTAR FICHAS
    # ==========================================================

    def listar_fichas(self):

        fichas = []

        if not os.path.isdir(
            self.fichas_dir
        ):
            return fichas

        for nome in os.listdir(
            self.fichas_dir
        ):

            if nome == "ativa.json":
                continue

            pasta = os.path.join(
                self.fichas_dir,
                nome
            )

            if not os.path.isdir(
                pasta
            ):
                continue

            ficha = self.carregar_ficha(nome)

            if ficha:
                fichas.append(ficha)

        fichas.sort(
            key=lambda item: item["ficha_id"],
            reverse=True
        )

        return fichas
