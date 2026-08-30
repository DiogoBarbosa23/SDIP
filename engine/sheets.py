import os
import re
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime


class PlanilhaResultados:
    """Cria e atualiza a planilha XLSX vinculada a uma ficha."""

    XL_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
    PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

    @staticmethod
    def _nome_seguro(texto):
        texto = str(texto or "resultados").strip()
        texto = re.sub(r'[<>:"/\\|?*]', "_", texto)
        texto = re.sub(r"\s+", " ", texto).strip(" .")
        return texto or "resultados"

    @staticmethod
    def _coluna_excel(indice):
        """Converte índice 1-based em letras Excel."""
        if indice < 1:
            raise ValueError("Índice de coluna inválido.")

        resultado = []
        numero = indice

        while numero:
            numero, resto = divmod(numero - 1, 26)
            resultado.append(chr(65 + resto))

        return "".join(reversed(resultado))

    @staticmethod
    def _valor_celula(elemento, shared_strings=None):
        valor = elemento.find(f"{{{PlanilhaResultados.XL_NS}}}v")

        if valor is None or valor.text is None:
            indice_compartilhado = None
        elif elemento.get("t") == "s" and shared_strings is not None:
            try:
                indice_compartilhado = int(valor.text)
            except (TypeError, ValueError):
                indice_compartilhado = None

            if (
                indice_compartilhado is not None
                and 0 <= indice_compartilhado < len(shared_strings)
            ):
                return shared_strings[indice_compartilhado]

            return ""
        else:
            return valor.text

        inline = elemento.find(f"{{{PlanilhaResultados.XL_NS}}}is")
        if inline is None:
            return ""

        textos = []
        for no in inline.iter(f"{{{PlanilhaResultados.XL_NS}}}t"):
            textos.append(no.text or "")
        return "".join(textos)

    @classmethod
    def estrutura_da_ficha(cls, dados_ficha):
        """Retorna a estrutura tabular da ficha, sem incluir seções."""
        colunas = []
        nomes_usados = set()

        def adicionar(nome, tipo="Texto", origem="cabecalho", numero=""):
            nome = str(nome or "").strip()
            if not nome:
                return

            chave = nome.casefold()
            if chave in nomes_usados:
                raise ValueError(
                    f'Existe mais de um campo com o cabeçalho "{nome}". '
                    "Renomeie os campos para gerar a planilha."
                )

            nomes_usados.add(chave)
            colunas.append(
                {
                    "cabecalho": nome,
                    "tipo": tipo or "Texto",
                    "origem": origem,
                    "numero": numero,
                }
            )

        for campo in dados_ficha.get("campos_identificacao", []):
            adicionar(
                campo.get("nome", ""),
                campo.get("tipo", "Texto"),
                "cabecalho",
                "",
            )

        elementos = dados_ficha.get("elementos")
        if elementos is None:
            elementos = dados_ficha.get("perguntas", [])

        for elemento in elementos:
            if elemento.get("tipo", "pergunta") != "pergunta":
                continue

            numero = str(elemento.get("numero", "")).strip()
            texto = str(elemento.get("texto", "")).strip()

            if not numero and not texto:
                continue

            # O cabeçalho segue a mesma identificação visível na ficha:
            # número da pergunta + texto, sem inventar campos técnicos.
            nome = f"{numero} {texto}".strip()
            adicionar(
                nome,
                "Texto",
                "pergunta",
                numero,
            )

        if not colunas:
            raise ValueError(
                "A ficha não possui campos de cabeçalho nem perguntas "
                "para formar a planilha."
            )

        return colunas

    @classmethod
    def cabecalhos_da_ficha(cls, dados_ficha):
        return [
            coluna["cabecalho"]
            for coluna in cls.estrutura_da_ficha(dados_ficha)
        ]

    @classmethod
    def tipos_da_ficha(cls, dados_ficha):
        return [
            coluna["tipo"]
            for coluna in cls.estrutura_da_ficha(dados_ficha)
        ]

    @classmethod
    def obter_caminho_padrao(cls, pasta_base, nome_pesquisa):
        return os.path.join(
            pasta_base,
            f"{cls._nome_seguro(nome_pesquisa)} - resultados.xlsx",
        )

    @staticmethod
    def _xml_texto(texto):
        return (
            str(texto)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    @classmethod
    def _celula_xml(cls, referencia, valor, estilo=0, numerica=False):
        if valor is None or str(valor) == "":
            return ""

        if numerica:
            return (
                f'<c r="{referencia}" s="{estilo}" t="n">'
                f"<v>{cls._xml_texto(valor)}</v></c>"
            )

        return (
            f'<c r="{referencia}" s="{estilo}" t="inlineStr">'
            f"<is><t xml:space=\"preserve\">"
            f"{cls._xml_texto(valor)}"
            f"</t></is></c>"
        )

    @staticmethod
    def _parse_data(texto):
        texto = str(texto or "").strip()
        if not texto:
            return None

        formatos = (
            "%d/%m/%Y",
            "%d/%m/%y",
        )

        for formato in formatos:
            try:
                return datetime.strptime(texto, formato).date()
            except ValueError:
                continue

        return None

    @classmethod
    def _numero_excel(cls, data):
        # Sistema de datas padrão do Excel, compatível com o calendário de 1900.
        origem = datetime(1899, 12, 30).date()
        return (data - origem).days

    @classmethod
    def _preparar_valor(cls, valor, tipo):
        if valor is None:
            return "", 0, False

        texto = str(valor).strip()
        if texto == "":
            return "", 0, False

        tipo = str(tipo or "Texto")

        if tipo == "Data":
            data = cls._parse_data(texto)
            if data:
                return cls._numero_excel(data), 2, True

        if tipo == "Número":
            try:
                if re.fullmatch(r"[-+]?\d+", texto):
                    return int(texto), 0, True

                if "," in texto and "." in texto:
                    candidato = texto.replace(".", "").replace(",", ".")
                elif "," in texto:
                    candidato = texto.replace(",", ".")
                else:
                    candidato = texto

                numero = float(candidato)
                return numero, 0, True
            except ValueError:
                # Se o usuário digitou algo que não é número, preservamos o texto.
                pass

        return texto, 0, False

    @classmethod
    def _conteudo_sheet(cls, colunas, registros=None):
        registros = registros or []
        quantidade_colunas = len(colunas)
        ultima_coluna = cls._coluna_excel(quantidade_colunas)
        ultima_linha = max(1, 1 + len(registros))

        partes = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            f'<worksheet xmlns="{cls.XL_NS}">',
            f'<dimension ref="A1:{ultima_coluna}{ultima_linha}"/>',
            "<sheetViews>",
            '<sheetView workbookViewId="0">',
            '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>',
            '<selection pane="bottomLeft" activeCell="A2" sqref="A2"/>',
            "</sheetView>",
            "</sheetViews>",
            "<sheetFormatPr defaultRowHeight=\"15\"/>",
            "<cols>",
        ]

        for indice, coluna in enumerate(colunas, start=1):
            cabecalho = coluna["cabecalho"]
            largura = max(14, min(42, len(cabecalho) * 1.15 + 2))
            letra = cls._coluna_excel(indice)
            partes.append(
                f'<col min="{indice}" max="{indice}" width="{largura:.1f}" '
                f'bestFit="1" customWidth="1"/>'
            )

        partes.extend([
            "</cols>",
            "<sheetData>",
            '<row r="1" ht="36" customHeight="1">',
        ])

        for indice, coluna in enumerate(colunas, start=1):
            referencia = f"{cls._coluna_excel(indice)}1"
            partes.append(
                cls._celula_xml(
                    referencia,
                    coluna["cabecalho"],
                    estilo=1,
                    numerica=False,
                )
            )

        partes.append("</row>")

        for numero_linha, registro in enumerate(registros, start=2):
            partes.append(f'<row r="{numero_linha}">')

            for indice, coluna in enumerate(colunas, start=1):
                nome = coluna["cabecalho"]
                valor, estilo, numerica = cls._preparar_valor(
                    registro.get(nome, ""),
                    coluna.get("tipo", "Texto"),
                )

                if valor == "":
                    continue

                referencia = (
                    f"{cls._coluna_excel(indice)}{numero_linha}"
                )
                partes.append(
                    cls._celula_xml(
                        referencia,
                        valor,
                        estilo=estilo,
                        numerica=numerica,
                    )
                )

            partes.append("</row>")

        partes.extend([
            "</sheetData>",
            f'<autoFilter ref="A1:{ultima_coluna}{ultima_linha}"/>',
            '<pageMargins left="0.25" right="0.25" top="0.5" bottom="0.5" header="0.3" footer="0.3"/>',
            "</worksheet>",
        ])

        return "".join(partes)

    @classmethod
    def _conteudo_styles(cls):
        return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="{cls.XL_NS}">
<numFmts count="1"><numFmt numFmtId="164" formatCode="dd/mm/yyyy"/></numFmts>
<fonts count="2">
<font><sz val="11"/><name val="Calibri"/><family val="2"/></font>
<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/><family val="2"/></font>
</fonts>
<fills count="3">
<fill><patternFill patternType="none"/></fill>
<fill><patternFill patternType="gray125"/></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FF1F4E78"/><bgColor indexed="64"/></patternFill></fill>
</fills>
<borders count="2">
<border><left/><right/><top/><bottom/><diagonal/></border>
<border><left style="thin"><color rgb="FFD9E2F3"/></left><right style="thin"><color rgb="FFD9E2F3"/></right><top style="thin"><color rgb="FFD9E2F3"/></top><bottom style="thin"><color rgb="FFD9E2F3"/></bottom><diagonal/></border>
</borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="3">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>
<xf numFmtId="0" fontId="1" fillId="2" borderId="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
<xf numFmtId="164" fontId="0" fillId="0" borderId="1" applyNumberFormat="1"/>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0"/></cellStyles>
<dxfs count="0"/>
<tableStyles count="0" defaultTableStyle="TableStyleMedium2" defaultPivotStyle="PivotStyleMedium9"/>
</styleSheet>
'''
    @classmethod
    def _conteudo_workbook(cls, nome_planilha="Respostas"):
        nome = cls._xml_texto(nome_planilha)[:31] or "Respostas"
        return (
            f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<workbook xmlns="{cls.XL_NS}" xmlns:r="{cls.REL_NS}">'
            f"<sheets><sheet name=\"{nome}\" sheetId=\"1\" r:id=\"rId1\"/></sheets>"
            f"</workbook>"
        )

    @classmethod
    def _escrever_xlsx_novo(cls, caminho, colunas):
        caminho = os.path.abspath(caminho)
        pasta = os.path.dirname(caminho)
        os.makedirs(pasta, exist_ok=True)

        conteudo_sheet = cls._conteudo_sheet(colunas)

        arquivos = {
            "[Content_Types].xml": (
                f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<Types xmlns="{cls.CT_NS}">'
                f'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                f'<Default Extension="xml" ContentType="application/xml"/>'
                f'<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                f'<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
                f'<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                f"</Types>"
            ),
            "_rels/.rels": (
                f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<Relationships xmlns="{cls.PKG_REL_NS}">'
                f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                f"</Relationships>"
            ),
            "xl/workbook.xml": cls._conteudo_workbook(),
            "xl/_rels/workbook.xml.rels": (
                f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<Relationships xmlns="{cls.PKG_REL_NS}">'
                f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
                f'<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                f"</Relationships>"
            ),
            "xl/styles.xml": cls._conteudo_styles(),
            "xl/worksheets/sheet1.xml": conteudo_sheet,
        }

        fd, temporario = tempfile.mkstemp(
            prefix="sdip_planilha_",
            suffix=".xlsx",
            dir=pasta,
        )
        os.close(fd)

        try:
            with zipfile.ZipFile(
                temporario,
                "w",
                compression=zipfile.ZIP_DEFLATED,
            ) as pacote:
                for nome, conteudo in arquivos.items():
                    pacote.writestr(nome, conteudo.encode("utf-8"))

            os.replace(temporario, caminho)
        finally:
            if os.path.exists(temporario):
                os.remove(temporario)

        return caminho

    @classmethod
    def criar_planilha(cls, caminho, dados_ficha):
        caminho = os.path.abspath(caminho)

        if not caminho.lower().endswith(".xlsx"):
            caminho += ".xlsx"

        if os.path.exists(caminho) and os.path.getsize(caminho) > 0:
            raise FileExistsError(
                f"A planilha já existe: {caminho}"
            )

        colunas = cls.estrutura_da_ficha(dados_ficha)
        return cls._escrever_xlsx_novo(caminho, colunas)

    @classmethod
    def _carregar_shared_strings(cls, pacote):
        try:
            xml = pacote.read("xl/sharedStrings.xml")
        except KeyError:
            return []

        raiz = ET.fromstring(xml)
        strings = []
        for item in raiz.findall(f"{{{cls.XL_NS}}}si"):
            textos = [
                no.text or ""
                for no in item.iter(f"{{{cls.XL_NS}}}t")
            ]
            strings.append("".join(textos))
        return strings

    @classmethod
    def _ler_sheet_xml(cls, caminho):
        with zipfile.ZipFile(caminho, "r") as pacote:
            xml = pacote.read("xl/worksheets/sheet1.xml")
            shared_strings = cls._carregar_shared_strings(pacote)
        return ET.fromstring(xml), shared_strings

    @classmethod
    def _cabecalhos_existentes(cls, caminho):
        raiz, shared_strings = cls._ler_sheet_xml(caminho)
        sheet_data = raiz.find(f"{{{cls.XL_NS}}}sheetData")
        if sheet_data is None:
            return []

        primeira_linha = None
        for linha in sheet_data.findall(f"{{{cls.XL_NS}}}row"):
            if linha.get("r") == "1":
                primeira_linha = linha
                break

        if primeira_linha is None:
            return []

        celulas = []
        for celula in primeira_linha.findall(f"{{{cls.XL_NS}}}c"):
            referencia = celula.get("r", "")
            numero = cls._numero_coluna_da_referencia(referencia)
            celulas.append((
                numero,
                cls._valor_celula(
                    celula,
                    shared_strings=shared_strings
                )
            ))

        if not celulas:
            return []

        max_coluna = max(item[0] for item in celulas)
        resultado = [""] * max_coluna
        for numero, valor in celulas:
            resultado[numero - 1] = valor
        return resultado

    @staticmethod
    def _numero_coluna_da_referencia(referencia):
        letras = "".join(ch for ch in str(referencia) if ch.isalpha())
        numero = 0
        for letra in letras.upper():
            numero = numero * 26 + ord(letra) - 64
        return numero

    @classmethod
    def validar_estrutura(cls, caminho, dados_ficha):
        esperados = cls.cabecalhos_da_ficha(dados_ficha)
        existentes = cls._cabecalhos_existentes(caminho)
        if existentes != esperados:
            raise ValueError(
                "A estrutura da planilha não corresponde à ficha de produção. "
                "A planilha não será alterada."
            )
        return True

    @classmethod
    def _localizar_sheet_data(cls, raiz):
        return raiz.find(f"{{{cls.XL_NS}}}sheetData")

    @classmethod
    def _ultima_linha(cls, sheet_data):
        linhas = sheet_data.findall(f"{{{cls.XL_NS}}}row")
        if not linhas:
            return 1
        return max(int(linha.get("r", "1")) for linha in linhas)

    @classmethod
    def _atualizar_referencias_sheet(cls, raiz, ultima_coluna, ultima_linha):
        dimensao = raiz.find(f"{{{cls.XL_NS}}}dimension")
        if dimensao is None:
            dimensao = ET.Element(f"{{{cls.XL_NS}}}dimension")
            raiz.insert(0, dimensao)
        dimensao.set("ref", f"A1:{ultima_coluna}{ultima_linha}")

        auto_filter = raiz.find(f"{{{cls.XL_NS}}}autoFilter")
        if auto_filter is None:
            auto_filter = ET.Element(f"{{{cls.XL_NS}}}autoFilter")
            sheet_data = cls._localizar_sheet_data(raiz)
            indice = list(raiz).index(sheet_data) + 1 if sheet_data is not None else len(raiz)
            raiz.insert(indice, auto_filter)
        auto_filter.set("ref", f"A1:{ultima_coluna}{ultima_linha}")

    @classmethod
    def _escrever_xml_zip(cls, caminho, xml_sheet):
        pasta = os.path.dirname(os.path.abspath(caminho))
        fd, temporario = tempfile.mkstemp(
            prefix="sdip_planilha_append_",
            suffix=".xlsx",
            dir=pasta,
        )
        os.close(fd)

        try:
            with zipfile.ZipFile(caminho, "r") as origem:
                with zipfile.ZipFile(
                    temporario,
                    "w",
                    compression=zipfile.ZIP_DEFLATED,
                ) as destino:
                    for item in origem.infolist():
                        if item.filename == "xl/worksheets/sheet1.xml":
                            destino.writestr(
                                item,
                                xml_sheet,
                            )
                        else:
                            destino.writestr(
                                item,
                                origem.read(item.filename),
                            )

            os.replace(temporario, caminho)
        finally:
            if os.path.exists(temporario):
                os.remove(temporario)

    @classmethod
    def adicionar_registro(cls, caminho, registro, cabecalhos_esperados=None, dados_ficha=None):
        caminho = os.path.abspath(caminho)

        if not os.path.isfile(caminho):
            raise FileNotFoundError(
                f"A planilha vinculada não foi encontrada: {caminho}"
            )

        if not caminho.lower().endswith(".xlsx"):
            raise ValueError("A planilha vinculada precisa ser um arquivo .xlsx.")

        if dados_ficha is not None:
            cabecalhos_esperados = cls.cabecalhos_da_ficha(dados_ficha)
            tipos = cls.tipos_da_ficha(dados_ficha)
        else:
            cabecalhos_esperados = list(cabecalhos_esperados or registro.keys())
            tipos = ["Texto"] * len(cabecalhos_esperados)

        try:
            raiz, _shared_strings = cls._ler_sheet_xml(caminho)
            sheet_data = cls._localizar_sheet_data(raiz)
            if sheet_data is None:
                raise ValueError("A planilha não possui dados tabulares válidos.")

            existentes = cls._cabecalhos_existentes(caminho)
            if existentes != list(cabecalhos_esperados):
                raise ValueError(
                    "A estrutura da planilha não corresponde à ficha de produção. "
                    "A resposta não foi gravada."
                )

            numero_linha = cls._ultima_linha(sheet_data) + 1
            linha = ET.Element(f"{{{cls.XL_NS}}}row", {"r": str(numero_linha)})

            for indice, (nome, tipo) in enumerate(
                zip(cabecalhos_esperados, tipos),
                start=1,
            ):
                valor, estilo, numerica = cls._preparar_valor(
                    registro.get(nome, ""),
                    tipo,
                )
                if valor == "":
                    continue

                referencia = f"{cls._coluna_excel(indice)}{numero_linha}"
                celula_xml = cls._celula_xml(
                    referencia,
                    valor,
                    estilo=estilo,
                    numerica=numerica,
                )
                elemento = ET.fromstring(celula_xml)
                linha.append(elemento)

            sheet_data.append(linha)

            ultima_coluna = cls._coluna_excel(len(cabecalhos_esperados))
            cls._atualizar_referencias_sheet(
                raiz,
                ultima_coluna,
                numero_linha,
            )

            ET.register_namespace("", cls.XL_NS)
            ET.register_namespace("r", cls.REL_NS)
            xml_sheet = ET.tostring(
                raiz,
                encoding="utf-8",
                xml_declaration=True,
            )

            cls._escrever_xml_zip(
                caminho,
                xml_sheet,
            )

            return caminho

        except PermissionError as erro:
            raise PermissionError(
                "Não foi possível alterar a planilha. "
                "Feche o arquivo no Excel e tente novamente."
            ) from erro
