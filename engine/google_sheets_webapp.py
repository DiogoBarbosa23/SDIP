import json
import secrets
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class GoogleSheetsWebAppErro(Exception):
    """Erro base da integração do SDIP com Google Sheets via Apps Script."""


class GoogleSheetsWebAppConexaoErro(GoogleSheetsWebAppErro):
    """Falha de comunicação com o Web App."""


class GoogleSheetsWebAppRespostaErro(GoogleSheetsWebAppErro):
    """O Web App respondeu, mas a resposta não pôde ser utilizada."""


class GoogleSheetsWebAppEstruturaErro(GoogleSheetsWebAppRespostaErro):
    """A estrutura real da planilha diverge da estrutura esperada."""


class GoogleSheetsWebAppChaveErro(GoogleSheetsWebAppRespostaErro):
    """A chave de integração foi rejeitada pelo Web App."""


class GoogleSheetsWebApp:
    """
    Integração gratuita do SDIP com Google Sheets através de
    um Google Apps Script publicado como Web App.

    Este módulo não depende de Google Cloud, Service Account,
    gspread ou bibliotecas externas.
    """

    TIMEOUT_PADRAO = 20
    TAMANHO_CHAVE = 32

    _MARCADOR_CHAVE = "__CHAVE_SDIP__"
    _MARCADOR_ABA = "__NOME_ABA__"

    _MODELO_APPS_SCRIPT = r'''const CHAVE_SDIP = __CHAVE_SDIP__;
const NOME_ABA = __NOME_ABA__; // Vazio = primeira aba da planilha.


function doGet(e) {
  try {
    validarChave_(e && e.parameter ? e.parameter.chave : "");

    const planilha = SpreadsheetApp.getActiveSpreadsheet();
    const aba = obterAba_(planilha);

    return respostaJson_({
      ok: true,
      mensagem: "Conexão com o SDIP funcionando.",
      planilha: planilha.getName(),
      aba: aba.getName()
    });

  } catch (erro) {
    return respostaErro_(erro);
  }
}


function doPost(e) {
  const lock = LockService.getScriptLock();

  try {
    if (!lock.tryLock(10000)) {
      throw new Error(
        "A planilha está recebendo outro registro. Tente novamente."
      );
    }

    if (!e || !e.postData || !e.postData.contents) {
      throw new Error("Requisição sem dados.");
    }

    const payload = JSON.parse(e.postData.contents);

    validarChave_(payload.chave);

    const acao = String(payload.acao || "").trim();

    const planilha = SpreadsheetApp.getActiveSpreadsheet();
    const aba = obterAba_(planilha);

    if (acao === "configurar") {
      return configurar_(aba, payload);
    }

    if (acao === "salvar") {
      return salvar_(aba, payload);
    }

    if (acao === "validar") {
      return validar_(aba, payload);
    }

    throw new Error("Ação inválida.");

  } catch (erro) {
    return respostaErro_(erro);

  } finally {
    if (lock.hasLock()) {
      lock.releaseLock();
    }
  }
}


function configurar_(aba, payload) {
  const esperados = normalizarCabecalhos_(payload.cabecalhos);

  if (esperados.length === 0) {
    throw new Error("Nenhum cabeçalho foi informado.");
  }

  const encontrados = obterCabecalhos_(aba);

  if (encontrados.length === 0) {
    aba.getRange(1, 1, 1, esperados.length).setValues([esperados]);
    aba.setFrozenRows(1);

    return respostaJson_({
      ok: true,
      configurada: true,
      mensagem: "Cabeçalhos criados com sucesso.",
      cabecalhos: esperados
    });
  }

  validarEstrutura_(esperados, encontrados);

  return respostaJson_({
    ok: true,
    configurada: false,
    mensagem: "A planilha já estava configurada corretamente.",
    cabecalhos: encontrados
  });
}


function validar_(aba, payload) {
  const esperados = normalizarCabecalhos_(payload.cabecalhos);
  const encontrados = obterCabecalhos_(aba);

  validarEstrutura_(esperados, encontrados);

  return respostaJson_({
    ok: true,
    mensagem: "Estrutura compatível.",
    cabecalhos: encontrados
  });
}


function salvar_(aba, payload) {
  const esperados = normalizarCabecalhos_(payload.cabecalhos);
  const encontrados = obterCabecalhos_(aba);

  validarEstrutura_(esperados, encontrados);

  const registro = payload.registro;

  if (!registro || typeof registro !== "object" || Array.isArray(registro)) {
    throw new Error("Registro inválido.");
  }

  const linha = esperados.map(function(cabecalho) {
    const valor = registro[cabecalho];

    if (valor === null || valor === undefined) {
      return "";
    }

    return String(valor);
  });

  aba.appendRow(linha);

  return respostaJson_({
    ok: true,
    mensagem: "Registro salvo com sucesso.",
    linha: aba.getLastRow()
  });
}


function validarChave_(chaveRecebida) {
  if (!CHAVE_SDIP) {
    throw new Error(
      "A chave do SDIP ainda não foi configurada no Apps Script."
    );
  }

  if (String(chaveRecebida || "") !== CHAVE_SDIP) {
    throw new Error("Chave de acesso inválida.");
  }
}


function obterAba_(planilha) {
  if (NOME_ABA) {
    const aba = planilha.getSheetByName(NOME_ABA);

    if (!aba) {
      throw new Error(
        'A aba configurada "' + NOME_ABA + '" não foi encontrada.'
      );
    }

    return aba;
  }

  const abas = planilha.getSheets();

  if (!abas || abas.length === 0) {
    throw new Error("A planilha não possui nenhuma aba.");
  }

  return abas[0];
}


function obterCabecalhos_(aba) {
  const ultimaColuna = aba.getLastColumn();

  if (ultimaColuna === 0) {
    return [];
  }

  const valores = aba
    .getRange(1, 1, 1, ultimaColuna)
    .getValues()[0];

  while (
    valores.length > 0 &&
    String(valores[valores.length - 1] || "").trim() === ""
  ) {
    valores.pop();
  }

  return normalizarCabecalhos_(valores);
}


function normalizarCabecalhos_(cabecalhos) {
  if (!Array.isArray(cabecalhos)) {
    return [];
  }

  return cabecalhos.map(function(valor) {
    return String(valor || "").trim();
  });
}


function validarEstrutura_(esperados, encontrados) {
  if (esperados.length !== encontrados.length) {
    throw new Error(
      "Estrutura incompatível. " +
      "Esperado: [" + esperados.join(" | ") + "]. " +
      "Encontrado: [" + encontrados.join(" | ") + "]."
    );
  }

  for (let i = 0; i < esperados.length; i++) {
    if (esperados[i] !== encontrados[i]) {
      throw new Error(
        "Estrutura incompatível na coluna " + (i + 1) + ". " +
        'Esperado: "' + esperados[i] + '". ' +
        'Encontrado: "' + encontrados[i] + '".'
      );
    }
  }
}


function respostaJson_(dados) {
  return ContentService
    .createTextOutput(JSON.stringify(dados))
    .setMimeType(ContentService.MimeType.JSON);
}


function respostaErro_(erro) {
  return respostaJson_({
    ok: false,
    erro: erro && erro.message
      ? erro.message
      : String(erro)
  });
}
'''

    def __init__(
        self,
        url_webapp: str,
        chave_integracao: str,
        timeout: int = TIMEOUT_PADRAO,
    ):
        self.url_webapp = self.validar_url_webapp(url_webapp)
        self.chave_integracao = self.validar_chave(chave_integracao)

        try:
            self.timeout = int(timeout)
        except (TypeError, ValueError) as erro:
            raise ValueError("Timeout inválido.") from erro

        if self.timeout <= 0:
            raise ValueError("Timeout deve ser maior que zero.")

    @classmethod
    def gerar_chave_integracao(cls) -> str:
        return secrets.token_urlsafe(cls.TAMANHO_CHAVE)

    @classmethod
    def gerar_codigo_apps_script(
        cls,
        chave_integracao: str | None = None,
        nome_aba: str = "",
    ) -> tuple[str, str]:
        chave = (
            cls.gerar_chave_integracao()
            if chave_integracao is None
            else cls.validar_chave(chave_integracao)
        )

        nome_aba_normalizado = str(nome_aba or "").strip()

        codigo = cls._MODELO_APPS_SCRIPT.replace(
            cls._MARCADOR_CHAVE,
            json.dumps(chave, ensure_ascii=False),
        ).replace(
            cls._MARCADOR_ABA,
            json.dumps(nome_aba_normalizado, ensure_ascii=False),
        )

        return codigo, chave

    @staticmethod
    def validar_chave(chave_integracao: str) -> str:
        chave = str(chave_integracao or "").strip()

        if not chave:
            raise ValueError("A chave de integração não pode ficar vazia.")

        return chave

    @staticmethod
    def validar_url_webapp(url_webapp: str) -> str:
        url = str(url_webapp or "").strip()

        if not url:
            raise ValueError("A URL do Web App não pode ficar vazia.")

        parsed = urllib.parse.urlparse(url)

        if parsed.scheme.lower() != "https":
            raise ValueError("A URL do Web App deve usar HTTPS.")

        if parsed.netloc.lower() != "script.google.com":
            raise ValueError(
                "A URL informada não é uma URL válida do Google Apps Script."
            )

        if not parsed.path.startswith("/macros/s/"):
            raise ValueError(
                "A URL informada não corresponde a uma implantação Web App."
            )

        if not parsed.path.endswith("/exec"):
            raise ValueError(
                "Use a URL da implantação que termina em '/exec'."
            )

        if parsed.query or parsed.fragment:
            raise ValueError(
                "Cole somente a URL /exec, sem parâmetros adicionais."
            )

        return url

    def testar_conexao(self) -> dict[str, Any]:
        separador = "&" if "?" in self.url_webapp else "?"
        endereco = (
            self.url_webapp
            + separador
            + urllib.parse.urlencode(
                {"chave": self.chave_integracao}
            )
        )

        resposta = self._requisicao_get(endereco)
        self._exigir_ok(resposta)

        return resposta

    def configurar_cabecalhos(
        self,
        cabecalhos: list[str],
    ) -> dict[str, Any]:
        cabecalhos_normalizados = self._normalizar_cabecalhos(cabecalhos)

        resposta = self._requisicao_post(
            {
                "acao": "configurar",
                "chave": self.chave_integracao,
                "cabecalhos": cabecalhos_normalizados,
            }
        )

        self._exigir_ok(resposta)
        return resposta

    def validar_estrutura(
        self,
        cabecalhos: list[str],
    ) -> dict[str, Any]:
        cabecalhos_normalizados = self._normalizar_cabecalhos(cabecalhos)

        resposta = self._requisicao_post(
            {
                "acao": "validar",
                "chave": self.chave_integracao,
                "cabecalhos": cabecalhos_normalizados,
            }
        )

        self._exigir_ok(resposta)
        return resposta

    def salvar_registro(
        self,
        cabecalhos: list[str],
        registro: dict[str, Any],
    ) -> dict[str, Any]:
        cabecalhos_normalizados = self._normalizar_cabecalhos(cabecalhos)

        if not isinstance(registro, dict):
            raise TypeError("O registro deve ser um dicionário.")

        resposta = self._requisicao_post(
            {
                "acao": "salvar",
                "chave": self.chave_integracao,
                "cabecalhos": cabecalhos_normalizados,
                "registro": registro,
            }
        )

        self._exigir_ok(resposta)
        return resposta

    @staticmethod
    def _normalizar_cabecalhos(cabecalhos: list[str]) -> list[str]:
        if not isinstance(cabecalhos, (list, tuple)):
            raise TypeError("Os cabeçalhos devem ser uma lista.")

        normalizados = [
            str(cabecalho or "").strip()
            for cabecalho in cabecalhos
        ]

        if not normalizados:
            raise ValueError("Nenhum cabeçalho foi informado.")

        if any(not cabecalho for cabecalho in normalizados):
            raise ValueError(
                "Os cabeçalhos não podem conter valores vazios."
            )

        if len(set(normalizados)) != len(normalizados):
            raise ValueError(
                "Os cabeçalhos não podem conter nomes duplicados."
            )

        return normalizados

    def _requisicao_get(
        self,
        endereco: str,
    ) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(
                endereco,
                timeout=self.timeout,
            ) as resposta:
                conteudo = resposta.read().decode(
                    "utf-8",
                    errors="replace",
                )

        except urllib.error.HTTPError as erro:
            raise GoogleSheetsWebAppConexaoErro(
                f"Erro HTTP {erro.code} ao acessar o Web App."
            ) from erro

        except urllib.error.URLError as erro:
            motivo = getattr(erro, "reason", erro)
            raise GoogleSheetsWebAppConexaoErro(
                f"Não foi possível acessar o Web App: {motivo}"
            ) from erro

        except TimeoutError as erro:
            raise GoogleSheetsWebAppConexaoErro(
                "O Web App demorou demais para responder."
            ) from erro

        return self._decodificar_resposta(conteudo)

    def _requisicao_post(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        dados = json.dumps(
            payload,
            ensure_ascii=False,
        ).encode("utf-8")

        requisicao = urllib.request.Request(
            self.url_webapp,
            data=dados,
            headers={
                "Content-Type": "application/json; charset=utf-8",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                requisicao,
                timeout=self.timeout,
            ) as resposta:
                conteudo = resposta.read().decode(
                    "utf-8",
                    errors="replace",
                )

        except urllib.error.HTTPError as erro:
            raise GoogleSheetsWebAppConexaoErro(
                f"Erro HTTP {erro.code} ao acessar o Web App."
            ) from erro

        except urllib.error.URLError as erro:
            motivo = getattr(erro, "reason", erro)
            raise GoogleSheetsWebAppConexaoErro(
                f"Não foi possível acessar o Web App: {motivo}"
            ) from erro

        except TimeoutError as erro:
            raise GoogleSheetsWebAppConexaoErro(
                "O Web App demorou demais para responder."
            ) from erro

        return self._decodificar_resposta(conteudo)

    @staticmethod
    def _decodificar_resposta(conteudo: str) -> dict[str, Any]:
        try:
            resposta = json.loads(conteudo)

        except json.JSONDecodeError as erro:
            raise GoogleSheetsWebAppRespostaErro(
                "O Web App respondeu em formato inválido. "
                "Confira a implantação e a opção 'Who has access'."
            ) from erro

        if not isinstance(resposta, dict):
            raise GoogleSheetsWebAppRespostaErro(
                "O Web App retornou uma resposta inesperada."
            )

        return resposta

    @staticmethod
    def _exigir_ok(resposta: dict[str, Any]) -> None:
        if resposta.get("ok"):
            return

        mensagem = str(
            resposta.get(
                "erro",
                "O Google Sheets rejeitou a operação.",
            )
        ).strip()

        mensagem_lower = mensagem.lower()

        if (
            "estrutura incompatível" in mensagem_lower
            or "estrutura incompativel" in mensagem_lower
        ):
            raise GoogleSheetsWebAppEstruturaErro(mensagem)

        if (
            "chave de acesso inválida" in mensagem_lower
            or "chave de acesso invalida" in mensagem_lower
            or "chave do sdip" in mensagem_lower
        ):
            raise GoogleSheetsWebAppChaveErro(mensagem)

        raise GoogleSheetsWebAppRespostaErro(mensagem)
