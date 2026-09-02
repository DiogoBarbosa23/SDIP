import hashlib
import json
import os
import re
import shutil
import uuid
import zipfile

from copy import deepcopy
from datetime import datetime, timezone


class ErroPacotePesquisa(Exception):
    """Erro de validação, exportação ou importação de um pacote .sdip."""


class PacotePesquisa:

    FORMATO = "SDIP-PESQUISA"
    VERSAO_FORMATO = 1

    ARQUIVO_MANIFESTO = "manifest.json"
    ARQUIVO_DADOS = "pesquisa/dados.json"
    ARQUIVO_PDF = "pesquisa/ficha.pdf"
    ARQUIVO_MAPA = "pesquisa/mapa_omr.json"
    ARQUIVO_LOGO = "pesquisa/logo.png"

    ARQUIVOS_OBRIGATORIOS = {
        ARQUIVO_MANIFESTO,
        ARQUIVO_DADOS,
        ARQUIVO_PDF,
        ARQUIVO_MAPA,
    }

    ARQUIVOS_PERMITIDOS = ARQUIVOS_OBRIGATORIOS | {
        ARQUIVO_LOGO,
    }

    TAMANHO_MAXIMO_ARQUIVO = 100 * 1024 * 1024
    TAMANHO_MAXIMO_PACOTE_DESCOMPACTADO = 200 * 1024 * 1024

    PADRAO_FICHA_ID = re.compile(r"^[A-Za-z0-9._-]+$")

    # ==========================================================
    # UTILITÁRIOS
    # ==========================================================

    @staticmethod
    def _sha256_bytes(conteudo):
        return hashlib.sha256(conteudo).hexdigest()

    @staticmethod
    def _ler_bytes(caminho):
        with open(caminho, "rb") as arquivo:
            return arquivo.read()

    @staticmethod
    def _json_bytes(dados):
        return json.dumps(
            dados,
            ensure_ascii=False,
            indent=4,
        ).encode("utf-8")

    @staticmethod
    def _nome_seguro(valor):
        nome = str(valor or "pesquisa").strip()
        nome = re.sub(r'[<>:"/\\|?*]+', "-", nome)
        nome = re.sub(r"\s+", " ", nome).strip(" .")
        return nome or "pesquisa"

    @classmethod
    def nome_arquivo_sugerido(cls, ficha):
        dados = ficha.get("dados", {})
        nome = cls._nome_seguro(
            dados.get("nome_pesquisa", "pesquisa")
        )
        versao = int(dados.get("versao", 1) or 1)
        return f"{nome} - v{versao}.sdip"

    @classmethod
    def _validar_ficha_id(cls, ficha_id):
        ficha_id = str(ficha_id or "").strip()

        if not ficha_id:
            raise ErroPacotePesquisa(
                "O pacote não possui um ficha_id válido."
            )

        if not cls.PADRAO_FICHA_ID.fullmatch(ficha_id):
            raise ErroPacotePesquisa(
                "O ficha_id do pacote possui caracteres inválidos."
            )

        return ficha_id

    @classmethod
    def _dados_para_exportacao(cls, ficha):
        dados = deepcopy(ficha.get("dados") or {})
        ficha_id = cls._validar_ficha_id(
            ficha.get("ficha_id") or dados.get("ficha_id")
        )

        dados["ficha_id"] = ficha_id
        dados["pesquisa_id"] = (
            dados.get("pesquisa_id") or ficha_id
        )
        dados["versao"] = int(
            dados.get("versao", 1) or 1
        )

        # Caminhos de arquivos locais não são portáveis entre PCs.
        # O vínculo Google, quando existir nos metadados, não é removido.
        planilha_local_removida = bool(
            dados.get("planilha_resultados_path")
        )
        dados["planilha_resultados_path"] = None

        logo_path = dados.get("logo_path")
        possui_logo = bool(
            logo_path and os.path.isfile(logo_path)
        )
        dados["logo_path"] = (
            "logo.png" if possui_logo else None
        )

        return dados, possui_logo, planilha_local_removida

    # ==========================================================
    # EXPORTAR
    # ==========================================================

    @classmethod
    def exportar(cls, ficha, caminho_destino):
        if not ficha:
            raise ErroPacotePesquisa(
                "Nenhuma ficha foi informada para exportação."
            )

        caminho_pdf = ficha.get("pdf")
        caminho_mapa = ficha.get("mapa")

        if not caminho_pdf or not os.path.isfile(caminho_pdf):
            raise ErroPacotePesquisa(
                "O PDF da ficha não foi encontrado."
            )

        if not caminho_mapa or not os.path.isfile(caminho_mapa):
            raise ErroPacotePesquisa(
                "O mapa OMR da ficha não foi encontrado."
            )

        dados, possui_logo, planilha_local_removida = (
            cls._dados_para_exportacao(ficha)
        )

        ficha_id = dados["ficha_id"]
        pesquisa_id = str(
            dados.get("pesquisa_id") or ficha_id
        )
        versao = int(dados.get("versao", 1) or 1)

        conteudos = {
            cls.ARQUIVO_DADOS: cls._json_bytes(dados),
            cls.ARQUIVO_PDF: cls._ler_bytes(caminho_pdf),
            cls.ARQUIVO_MAPA: cls._ler_bytes(caminho_mapa),
        }

        if possui_logo:
            conteudos[cls.ARQUIVO_LOGO] = cls._ler_bytes(
                ficha["dados"]["logo_path"]
            )

        arquivos_manifesto = {}

        for nome, conteudo in conteudos.items():
            arquivos_manifesto[nome] = {
                "sha256": cls._sha256_bytes(conteudo),
                "tamanho": len(conteudo),
            }

        manifesto = {
            "formato": cls.FORMATO,
            "versao_formato": cls.VERSAO_FORMATO,
            "exportado_em_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "ficha_id": ficha_id,
            "pesquisa_id": pesquisa_id,
            "versao_pesquisa": versao,
            "nome_pesquisa": str(
                dados.get("nome_pesquisa", "")
            ),
            "status_producao": dados.get(
                "status_producao"
            ),
            "planilha_local_removida": (
                planilha_local_removida
            ),
            "arquivos": arquivos_manifesto,
        }

        caminho_destino = os.path.abspath(
            caminho_destino
        )

        if not caminho_destino.lower().endswith(".sdip"):
            caminho_destino += ".sdip"

        pasta_destino = os.path.dirname(caminho_destino)
        if pasta_destino:
            os.makedirs(pasta_destino, exist_ok=True)

        caminho_temporario = (
            caminho_destino
            + f".tmp_{uuid.uuid4().hex}"
        )

        try:
            with zipfile.ZipFile(
                caminho_temporario,
                "w",
                compression=zipfile.ZIP_DEFLATED,
            ) as pacote:
                pacote.writestr(
                    cls.ARQUIVO_MANIFESTO,
                    cls._json_bytes(manifesto),
                )

                for nome, conteudo in conteudos.items():
                    pacote.writestr(nome, conteudo)

            os.replace(
                caminho_temporario,
                caminho_destino,
            )

        except Exception:
            if os.path.isfile(caminho_temporario):
                try:
                    os.remove(caminho_temporario)
                except OSError:
                    pass
            raise

        return {
            "caminho": caminho_destino,
            "ficha_id": ficha_id,
            "pesquisa_id": pesquisa_id,
            "versao": versao,
            "nome_pesquisa": manifesto["nome_pesquisa"],
            "planilha_local_removida": planilha_local_removida,
        }

    # ==========================================================
    # VALIDAR PACOTE
    # ==========================================================

    @classmethod
    def _ler_e_validar_pacote(cls, caminho_pacote):
        if not caminho_pacote or not os.path.isfile(caminho_pacote):
            raise ErroPacotePesquisa(
                "O arquivo .sdip informado não foi encontrado."
            )

        try:
            with zipfile.ZipFile(caminho_pacote, "r") as pacote:
                infos = pacote.infolist()
                nomes = {info.filename for info in infos}

                ausentes = cls.ARQUIVOS_OBRIGATORIOS - nomes
                if ausentes:
                    raise ErroPacotePesquisa(
                        "Pacote incompleto. Arquivos ausentes: "
                        + ", ".join(sorted(ausentes))
                    )

                desconhecidos = nomes - cls.ARQUIVOS_PERMITIDOS
                if desconhecidos:
                    raise ErroPacotePesquisa(
                        "O pacote contém arquivos não permitidos: "
                        + ", ".join(sorted(desconhecidos))
                    )

                tamanho_total = 0
                for info in infos:
                    if info.is_dir():
                        raise ErroPacotePesquisa(
                            "O pacote contém uma estrutura inválida."
                        )

                    if info.file_size > cls.TAMANHO_MAXIMO_ARQUIVO:
                        raise ErroPacotePesquisa(
                            f'O arquivo "{info.filename}" excede o '
                            "tamanho permitido."
                        )

                    tamanho_total += info.file_size

                if (
                    tamanho_total
                    > cls.TAMANHO_MAXIMO_PACOTE_DESCOMPACTADO
                ):
                    raise ErroPacotePesquisa(
                        "O pacote excede o tamanho máximo permitido."
                    )

                conteudos = {
                    nome: pacote.read(nome)
                    for nome in nomes
                }

        except zipfile.BadZipFile as erro:
            raise ErroPacotePesquisa(
                "O arquivo selecionado não é um pacote SDIP válido."
            ) from erro

        try:
            manifesto = json.loads(
                conteudos[cls.ARQUIVO_MANIFESTO].decode("utf-8")
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as erro:
            raise ErroPacotePesquisa(
                "O manifest.json do pacote é inválido."
            ) from erro

        if manifesto.get("formato") != cls.FORMATO:
            raise ErroPacotePesquisa(
                "O arquivo não pertence ao formato de pesquisa do SDIP."
            )

        if manifesto.get("versao_formato") != cls.VERSAO_FORMATO:
            raise ErroPacotePesquisa(
                "A versão deste pacote .sdip não é suportada."
            )

        ficha_id = cls._validar_ficha_id(
            manifesto.get("ficha_id")
        )

        arquivos_manifesto = manifesto.get("arquivos")
        if not isinstance(arquivos_manifesto, dict):
            raise ErroPacotePesquisa(
                "A lista de integridade do pacote é inválida."
            )

        for nome in nomes:
            if nome == cls.ARQUIVO_MANIFESTO:
                continue

            esperado = arquivos_manifesto.get(nome)
            if not isinstance(esperado, dict):
                raise ErroPacotePesquisa(
                    f'Falta a assinatura de integridade de "{nome}".'
                )

            hash_real = cls._sha256_bytes(conteudos[nome])
            if hash_real != esperado.get("sha256"):
                raise ErroPacotePesquisa(
                    f'O arquivo "{nome}" foi alterado ou corrompido.'
                )

        try:
            dados = json.loads(
                conteudos[cls.ARQUIVO_DADOS].decode("utf-8")
            )
            mapa = json.loads(
                conteudos[cls.ARQUIVO_MAPA].decode("utf-8")
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as erro:
            raise ErroPacotePesquisa(
                "Os metadados JSON do pacote são inválidos."
            ) from erro

        if not isinstance(dados, dict):
            raise ErroPacotePesquisa(
                "O dados.json do pacote possui formato inválido."
            )

        if not isinstance(mapa, (dict, list)):
            raise ErroPacotePesquisa(
                "O mapa OMR do pacote possui formato inválido."
            )

        if str(dados.get("ficha_id") or "") != ficha_id:
            raise ErroPacotePesquisa(
                "O ficha_id do manifest não corresponde ao dados.json."
            )

        pesquisa_id_manifesto = str(
            manifesto.get("pesquisa_id") or ficha_id
        )
        pesquisa_id_dados = str(
            dados.get("pesquisa_id") or ficha_id
        )

        if pesquisa_id_manifesto != pesquisa_id_dados:
            raise ErroPacotePesquisa(
                "O pesquisa_id do manifest não corresponde ao dados.json."
            )

        try:
            versao_manifesto = int(
                manifesto.get("versao_pesquisa", 1) or 1
            )
            versao_dados = int(
                dados.get("versao", 1) or 1
            )
        except (TypeError, ValueError) as erro:
            raise ErroPacotePesquisa(
                "A versão da pesquisa é inválida."
            ) from erro

        if versao_manifesto < 1 or versao_manifesto != versao_dados:
            raise ErroPacotePesquisa(
                "A versão do manifest não corresponde ao dados.json."
            )

        if not conteudos[cls.ARQUIVO_PDF].startswith(b"%PDF"):
            raise ErroPacotePesquisa(
                "O ficha.pdf do pacote não é um PDF válido."
            )

        possui_logo = cls.ARQUIVO_LOGO in conteudos

        if possui_logo:
            dados["logo_path"] = "logo.png"
        else:
            dados["logo_path"] = None

        # Reforço: caminho de XLSX de outra máquina nunca é importado.
        dados["planilha_resultados_path"] = None

        conteudos[cls.ARQUIVO_DADOS] = cls._json_bytes(dados)

        return {
            "manifesto": manifesto,
            "dados": dados,
            "conteudos": conteudos,
            "ficha_id": ficha_id,
            "pesquisa_id": pesquisa_id_dados,
            "versao": versao_dados,
            "possui_logo": possui_logo,
        }

    # ==========================================================
    # IMPORTAR
    # ==========================================================

    @classmethod
    def importar(cls, caminho_pacote, fichas_manager):
        pacote = cls._ler_e_validar_pacote(caminho_pacote)

        ficha_id = pacote["ficha_id"]
        pesquisa_id = pacote["pesquisa_id"]
        versao = pacote["versao"]

        pasta_destino = os.path.join(
            fichas_manager.fichas_dir,
            ficha_id,
        )

        if os.path.exists(pasta_destino):
            raise ErroPacotePesquisa(
                "Esta ficha já está instalada neste SDIP."
            )

        for ficha_existente in fichas_manager.listar_fichas():
            dados_existentes = ficha_existente.get("dados", {})
            pesquisa_existente = str(
                dados_existentes.get("pesquisa_id")
                or ficha_existente.get("ficha_id")
            )
            versao_existente = int(
                dados_existentes.get("versao", 1) or 1
            )

            if (
                pesquisa_existente == pesquisa_id
                and versao_existente == versao
            ):
                raise ErroPacotePesquisa(
                    "Já existe neste SDIP uma ficha da mesma pesquisa "
                    f"na versão {versao}."
                )

        pasta_temporaria = os.path.join(
            fichas_manager.fichas_dir,
            f".importando_{uuid.uuid4().hex}",
        )

        os.makedirs(pasta_temporaria, exist_ok=False)

        try:
            arquivos_destino = {
                cls.ARQUIVO_DADOS: "dados.json",
                cls.ARQUIVO_PDF: "ficha.pdf",
                cls.ARQUIVO_MAPA: "mapa_omr.json",
            }

            if pacote["possui_logo"]:
                arquivos_destino[cls.ARQUIVO_LOGO] = "logo.png"

            for origem, nome_destino in arquivos_destino.items():
                caminho = os.path.join(
                    pasta_temporaria,
                    nome_destino,
                )

                with open(caminho, "wb") as arquivo:
                    arquivo.write(
                        pacote["conteudos"][origem]
                    )

            os.replace(
                pasta_temporaria,
                pasta_destino,
            )

            ficha_importada = fichas_manager.carregar_ficha(
                ficha_id
            )

            if not ficha_importada:
                raise ErroPacotePesquisa(
                    "A pesquisa foi copiada, mas não pôde ser carregada "
                    "pelo SDIP. A importação foi revertida."
                )

        except Exception:
            if os.path.isdir(pasta_temporaria):
                shutil.rmtree(
                    pasta_temporaria,
                    ignore_errors=True,
                )

            if os.path.isdir(pasta_destino):
                shutil.rmtree(
                    pasta_destino,
                    ignore_errors=True,
                )

            raise

        return {
            "ficha": ficha_importada,
            "ficha_id": ficha_id,
            "pesquisa_id": pesquisa_id,
            "versao": versao,
            "nome_pesquisa": pacote["dados"].get(
                "nome_pesquisa",
                "",
            ),
            "planilha_local_removida": bool(
                pacote["manifesto"].get(
                    "planilha_local_removida"
                )
            ),
        }
