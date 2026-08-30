# SDIP 2.0

## Sistema de Digitalização Inteligente de Pesquisas

Aplicação desktop desenvolvida em Python para automatizar a **criação, impressão, digitalização e leitura de fichas de pesquisas preenchidas manualmente em papel**.

O SDIP utiliza **processamento de imagens, ArUco, correção geométrica e OMR (Optical Mark Recognition)** para transformar respostas marcadas em papel em dados estruturados.

A versão **2.0** evolui o projeto para permitir que a própria aplicação gere dinamicamente a ficha de pesquisa, independentemente da quantidade de perguntas, criando automaticamente as caixas OMR, os marcadores geométricos e o mapa utilizado posteriormente na leitura.

Além das respostas fechadas, a versão 2.0 possui suporte a:

* perguntas abertas;
* cabeçalho configurável;
* seções opcionais;
* paginação automática;
* edição de fichas;
* ficha ativa;
* visualização da área efetivamente analisada pelo OMR;
* leitura integrada ao fluxo de digitalização;
* geração de planilha Excel derivada da estrutura da ficha;
* vínculo entre ficha e planilha;
* controle de rascunho, produção e versões.

---

## 🎯 Objetivo

Reduzir a necessidade de transcrição manual das pesquisas realizadas em campo, permitindo que fichas impressas sejam preenchidas manualmente e posteriormente processadas automaticamente.

Fluxo do sistema:

```text
Criação da pesquisa
        ↓
Definição do cabeçalho, seções, perguntas e opções
        ↓
Geração automática da ficha
        ↓
ArUcos + caixas OMR + mapa automático
        ↓
Visualização
        ↓
Confirmação para produção
        ↓
Geração da planilha da pesquisa
        ↓
Impressão
        ↓
Preenchimento manual
        ↓
Scanner
        ↓
PDF
        ↓
Detecção dos ArUcos
        ↓
Correção geométrica
        ↓
Normalização
        ↓
Leitura OMR
        ↓
Respostas estruturadas
        ↓
Preenchimento/revisão dos dados
        ↓
Salvamento
        ↓
Nova linha na planilha da pesquisa
        ↓
Destino externo
```

O usuário não precisa conhecer:

```text
coordenadas
homografia
ArUco
mapa OMR
thresholds internos
```

A integração com destinos externos, como Google Forms, ainda não foi concluída.

---

# 🚀 Principais recursos

## Geração automática de fichas

O usuário pode definir:

* nome da pesquisa;
* título opcional;
* seções opcionais;
* perguntas;
* numeração das perguntas;
* tipo de resposta;
* opções disponíveis;
* perguntas abertas;
* campos de identificação do cabeçalho;
* tamanho da fonte.

O sistema calcula automaticamente:

* distribuição das perguntas;
* quebra de texto;
* organização das opções;
* caixas OMR;
* páginas necessárias;
* ArUcos;
* mapa OMR;
* áreas destinadas às perguntas abertas;
* layout do cabeçalho.

O usuário não precisa informar coordenadas manualmente.

---

## Seções opcionais

A ficha pode ser criada sem seções ou organizada em seções.

Sem seção:

```text
1 Pergunta

2 Pergunta

3 Pergunta
```

Com seção:

```text
1. Situação da obra

1.1 Pergunta

1.2 Pergunta

1.3 Pergunta

2. Qualidade da reforma

2.1 Pergunta

2.2 Pergunta

2.3 Pergunta
```

As seções são elementos visuais e organizacionais da ficha.

**Seções não recebem caixas OMR e não geram colunas na planilha.**

---

## Perguntas de resposta fechada

Perguntas fechadas podem utilizar:

* resposta única;
* resposta múltipla.

Cada opção recebe automaticamente uma caixa OMR.

Exemplos de identificadores internos:

```text
1.1_sim
1.2_nao
2.3_barra_de_apoio
2.3_corrimao
```

Os identificadores internos são utilizados pelo sistema para relacionar o mapa OMR às perguntas.

Na planilha, o cabeçalho é baseado na estrutura da ficha e utiliza uma representação legível da pergunta.

---

## Perguntas abertas

Uma pergunta pode ser configurada como resposta aberta.

Nesse caso:

* as opções OMR são removidas;
* não são criadas caixas para aquela pergunta;
* é reservada uma área para resposta manuscrita;
* a pergunta é registrada no mapa como pergunta aberta;
* o painel de leitura pode apresentar um campo para o operador informar a resposta.

Exemplo:

```text
2.3 Qual serviço público precisa de atenção?

________________________________________
```

Perguntas abertas independentes também podem gerar colunas na planilha.

O comportamento específico de campos do tipo `Outros` seguido de `Qual?` ainda aguarda confirmação do processo real utilizado pelos usuários.

---

## Cabeçalho configurável

O cabeçalho não é mais fixo como na versão 1.0.

O criador da ficha pode definir os campos conforme a necessidade da pesquisa.

Exemplos:

```text
Nome do morador
Data
Número do selo
Comunidade
Entrevistador
Bairro
Código
Número do imóvel
Identificador
```

Os campos configurados são utilizados em:

```text
Ficha impressa
        +
Painel do leitor
        +
Resultado final
        +
Planilha
```

Dessa forma, campos antigos do SDIP 1.0 não são tratados como obrigatórios.

---

# ✏️ Edição e versionamento de fichas

A aplicação permite editar fichas.

Enquanto uma ficha ainda estiver em **RASCUNHO**, o usuário pode alterar:

* nome;
* título;
* cabeçalho;
* seções;
* perguntas;
* opções;
* perguntas abertas;
* ordem dos elementos;
* configurações de geração.

Fluxo:

```text
Criar ficha
    ↓
Gerar
    ↓
Visualizar
    ↓
Editar
    ↓
Gerar novamente
```

## Ficha em produção

Depois que o usuário confirma a ficha e gera sua planilha, ela passa para o estado:

```text
PRODUÇÃO
```

A partir desse momento, a estrutura da ficha passa a representar o schema da coleta e não deve ser alterada silenciosamente.

Alterações estruturais incluem:

* adicionar pergunta;
* excluir pergunta;
* renomear pergunta;
* mudar ordem das perguntas;
* adicionar campo de cabeçalho;
* excluir campo de cabeçalho;
* renomear campo de cabeçalho;
* mudar ordem do cabeçalho;
* transformar pergunta fechada em aberta;
* transformar pergunta aberta em fechada;
* alterar a estrutura das opções.

Para alterações desse tipo, o sistema deve utilizar **nova versão**.

Exemplo:

```text
Pesquisa
├── Ficha v1
│   └── Planilha v1
│
└── Ficha v2
    └── Planilha v2
```

A nova versão mantém a identidade da pesquisa, mas possui sua própria estrutura, mapa, PDF e planilha.

---

# 📋 Ficha ativa

As fichas são armazenadas com identificadores próprios.

A aplicação possui uma **ficha ativa**, utilizada como referência para:

* visualização;
* PDF;
* mapa OMR;
* leitura;
* campos de identificação;
* perguntas abertas;
* planilha associada.

O mapa de uma ficha não deve ser usado para processar outra ficha.

---

# 📐 Layout automático

A ficha utiliza duas colunas independentes.

```text
┌──────────────────────┬──────────────────────┐
│ Coluna esquerda      │ Coluna direita       │
│                      │                      │
│ Perguntas de cima    │ Perguntas de cima    │
│ para baixo           │ para baixo           │
│                      │                      │
└──────────────────────┴──────────────────────┘
```

A linha central da página funciona como limite real de layout.

Uma pergunta nunca ultrapassa a metade destinada à sua coluna.

A coluna esquerda é preenchida primeiro.

Quando uma nova pergunta não cabe nela, o sistema continua automaticamente na coluna direita.

Quando as duas colunas ficam sem espaço, uma nova página é criada.

Uma pergunta não deve ser dividida entre:

* colunas;
* páginas.

O gerador foi validado com fichas de **uma e duas páginas**.

Alterações do tamanho da fonte também foram testadas, inclusive situações em que uma ficha passa de uma para duas páginas e depois retorna para uma página.

---

# 🖼️ Cabeçalho e logo

O cabeçalho possui:

* título;
* nome da pesquisa;
* campos de identificação;
* área reservada para logo.

A logo é redimensionada proporcionalmente para permanecer dentro da área destinada a ela, sem sobrepor os ArUcos ou o restante do cabeçalho.

---

# 🧠 Como funciona o OMR

Cada opção da ficha possui uma caixa OMR.

Exemplos:

```text
1.1_sim

1.2_nao

2.3_barra_de_apoio

2.3_corrimao
```

Cada caixa possui coordenadas próprias:

```text
x1
y1
x2
y2
```

O leitor analisa apenas o interior da caixa, ignorando uma margem interna das bordas.

O processo é:

```text
Caixa OMR
    ↓
Remoção da margem interna
    ↓
Análise da imagem
    ↓
Contagem de pixels escuros
    ↓
Percentual de pixels escuros
    ↓
MARCADA / VAZIA
```

O limiar atualmente utilizado é:

```python
percentual >= 5.0
```

---

# 📐 Calibração da margem OMR

Durante a validação física, foi identificado que a borda preta das próprias caixas OMR podia ser interpretada como marcação.

Foram realizados testes com uma ficha branca:

| Margem | Falsos positivos |
| -----: | ---------------: |
|      4 |               22 |
|      5 |                2 |
|      6 |                1 |
|  **7** |            **0** |
|      8 |                0 |
|     10 |                0 |

A margem atualmente validada é:

```text
7 pixels
```

A configuração atual do OMR é:

```text
Margem interna: 7 pixels
Threshold de pixel escuro: 150
Limiar de marcação: 5%
```

Esses parâmetros não devem ser alterados sem nova validação.

Caso seja necessário recalibrar, devem ser utilizados:

1. ficha branca;
2. ficha com marcações conhecidas;
3. comparação dos resultados;
4. teste no scanner real.

---

# 🔲 ArUco e correção geométrica

A ficha utiliza quatro marcadores ArUco por página:

```text
DICT_4X4_50
```

Disposição:

```text
0 ---------------- 1

|                  |

|                  |

|                  |

3 ---------------- 2
```

A geometria utiliza:

```python
cv2.aruco.ArucoDetector
```

Versão validada do OpenCV:

```text
4.12.0
```

A detecção trabalha com os IDs reais dos marcadores.

Isso substituiu a estratégia anterior baseada na seleção de contornos quadrados.

---

# 📄 Geometria por página

Cada página é processada individualmente.

Fluxo:

```text
Página 1
    ↓
IDs correspondentes à página 1
    ↓
Homografia
    ↓
Normalização

Página 2
    ↓
IDs correspondentes à página 2
    ↓
Homografia
    ↓
Normalização
```

Uma página torta não deve afetar geometricamente outra.

---

# 📐 Normalização

A imagem escaneada é normalizada para:

```text
1191 × 1684 pixels
```

Fluxo:

```text
PDF escaneado
    ↓
Renderização da página
    ↓
Detecção dos ArUcos
    ↓
Identificação dos IDs
    ↓
Centros dos marcadores
    ↓
Homografia
    ↓
Normalização
    ↓
1191 × 1684
    ↓
OMR
```

O mapa OMR representa coordenadas da imagem normalizada.

Não deve ser aplicada uma segunda transformação arbitrária às coordenadas do mapa.

---

# 🗺️ Mapa OMR automático

Na versão 2.0, o mapa OMR é gerado automaticamente pelo `GeradorFicha`.

Cada caixa desenhada na ficha é registrada com:

```text
nome
pagina
x1
y1
x2
y2
```

O mapa também registra:

* largura da imagem;
* altura da imagem;
* quantidade de páginas;
* ArUcos;
* coordenadas;
* perguntas abertas;
* campos de identificação.

Cada ficha possui seu próprio mapa.

O usuário não precisa mapear manualmente cada caixa.

---

# 👁️ Visualização "Onde devo marcar?"

A aplicação possui um recurso integrado à tela **Visualizar ficha ativa**:

```text
Onde devo marcar?
```

O recurso mostra a ficha atual e destaca em vermelho a área efetivamente analisada pelo OMR.

Serve para:

* mostrar ao usuário onde marcar;
* validar o alinhamento do mapa;
* confirmar a posição das caixas;
* auxiliar no diagnóstico;
* validar alterações no layout.

Importante:

**A marcação vermelha existe somente na visualização.**

Ela não é gravada no PDF e não aparece na ficha impressa.

Arquivo:

```text
area_omr.py
```

---

# ✅ Validação visual do mapeamento

O mapeamento OMR foi validado visualmente utilizando `Onde devo marcar?`.

Foram testados:

* ficha de uma página;
* ficha de duas páginas;
* alteração do tamanho da fonte;
* passagem de uma para duas páginas;
* retorno para uma página.

As áreas destacadas permaneceram alinhadas com as caixas OMR.

O mapeamento é considerado validado para a arquitetura atual.

---

# ✅ Validação física do OMR

## Ficha branca de duas páginas

Resultado:

```text
Página 1
Total: 70
Marcadas: 0
Vazias: 70

Página 2
Total: 70
Marcadas: 0
Vazias: 70
```

Consolidado:

```text
Total: 140
Marcadas: 0
Vazias: 140
```

Resultado:

**0 falsos positivos.**

## Teste físico anterior com marcações

Também foi realizado teste físico anterior com:

```text
Total: 50 caixas
Marcadas: 12
Vazias: 38
```

As 12 marcações reais foram reconhecidas:

```text
12/12
100%
```

Esse resultado é histórico e não substitui o novo teste físico da versão atual.

---

# 🖨️ Configuração de impressão

Para preservar a geometria:

```text
Papel: A4
Orientação: Retrato
Escala: 100%
Tamanho real
```

Não utilizar:

```text
Ajustar à página
Fit to page
Reduzir para caber
Preencher página
Escala automática
```

Alterações de escala podem modificar a relação entre o formulário físico e as coordenadas do mapa OMR.

---

# 📠 Configuração do scanner

Configuração utilizada nos testes:

```text
600 DPI
PDF
```

As páginas são processadas individualmente e os ArUcos são utilizados para corrigir a perspectiva.

O próximo teste físico deve utilizar a ficha atual em produção e o scanner real que será utilizado no processo.

---

# 📊 Saída para planilha

A versão atual possui saída local em formato:

```text
.xlsx
```

A estrutura da planilha é derivada diretamente da ficha criada pelo usuário.

A ficha é a **fonte de verdade**.

A ordem das colunas é:

```text
Campos do cabeçalho
        ↓
Perguntas
```

As seções não geram colunas.

---

# 📋 Estrutura da planilha

Exemplo de ficha:

```text
Cabeçalho

Data
Número do Selo
Comunidade
Nome do Morador
Entrevistador

Seção 1 - Obras

1.1 A obra foi concluída?
1.2 A obra ficou boa?
1.3 Houve algum problema?

Seção 2 - Qualidade

2.1 Como avalia a qualidade?
2.2 O serviço atendeu à expectativa?
```

A primeira linha da planilha será:

| A    | B              | C          | D               | E             | F                         | G                     | H                         | I                            | J                                    |
| ---- | -------------- | ---------- | --------------- | ------------- | ------------------------- | --------------------- | ------------------------- | ---------------------------- | ------------------------------------ |
| Data | Número do Selo | Comunidade | Nome do Morador | Entrevistador | 1.1 A obra foi concluída? | 1.2 A obra ficou boa? | 1.3 Houve algum problema? | 2.1 Como avalia a qualidade? | 2.2 O serviço atendeu à expectativa? |

As seções não aparecem.

A primeira resposta gera a linha 2:

```text
23/08/2026
12345
Comunidade X
João
Maria
Sim
Sim
Não
Boa
Sim
```

A segunda resposta gera a linha 3.

Cada ficha processada gera uma nova linha.

O SDIP não recria o cabeçalho para cada leitura.

---

# ❄️ Cabeçalho fixo da planilha

A planilha possui:

* primeira linha como cabeçalho;
* primeira linha congelada;
* filtro automático;
* largura das colunas ajustada;
* formatação de datas quando aplicável.

O objetivo é que a linha 1 represente permanentemente a estrutura da pesquisa enquanto aquela versão estiver em produção.

---

# 🔗 Vínculo entre ficha e planilha

O fluxo de produção é:

```text
Criar ficha
    ↓
Gerar
    ↓
Visualizar
    ↓
Confirmar ficha para produção
    ↓
Gerar planilha
    ↓
Usuário escolhe onde salvar
    ↓
Ficha vinculada à planilha
```

O caminho da planilha é armazenado junto aos dados da ficha.

Depois:

```text
Ficha escaneada
    ↓
OMR
    ↓
Campos digitados
    ↓
Resultado estruturado
    ↓
Nova linha
    ↓
Planilha vinculada
```

O usuário não deve precisar escolher novamente o arquivo da planilha a cada leitura.

---

# 🧩 Ficha como fonte da estrutura da planilha

O SDIP não deve manter um segundo modelo manual de planilha.

A estrutura deve ser derivada da ficha:

```text
Estrutura da ficha
        ↓
Gerador da ficha
        ↓
PDF + mapa OMR
```

e:

```text
Estrutura da ficha
        ↓
Gerador da planilha
        ↓
Linha 1
```

Assim:

```text
Ficha
  ↓
Fonte única de verdade
```

Isso garante correspondência entre:

```text
pergunta da ficha
      ↕
coluna da planilha
      ↕
resposta lida
```

---

# 🔄 RASCUNHO → PRODUÇÃO → NOVA VERSÃO

O ciclo de vida da ficha é:

```text
RASCUNHO
   ↓
Gerar
   ↓
Visualizar
   ↓
Confirmar
   ↓
PRODUÇÃO
```

Em produção:

```text
Ficha
+
Mapa
+
PDF
+
Planilha
```

representam uma mesma versão.

Se a estrutura precisar mudar:

```text
Produção
   ↓
Nova versão
   ↓
RASCUNHO
   ↓
Editar
   ↓
Gerar
   ↓
Nova planilha
   ↓
PRODUÇÃO
```

Isso evita misturar estruturas diferentes na mesma coleta.

---

# 💾 Fluxo de leitura e salvamento

O objetivo da camada de saída é separar o OMR da persistência.

Arquitetura:

```text
PDF
 ↓
ArUco
 ↓
Geometria
 ↓
Normalização
 ↓
OMR
 ↓
Respostas estruturadas
 ↓
Campos digitados
 ↓
Validação
 ↓
Revisão
 ↓
Registro final
 ↓
Planilha
```

O `engine/omr.py` não deve ser acoplado diretamente à camada de planilhas ou ao Google Forms.

---

# 📝 Respostas e validação

Depois do OMR, as marcações devem ser convertidas em respostas por pergunta.

Exemplos:

```text
1.1 → Sim
1.2 → Não
2.3 → Barra de apoio + Corrimão
3.3 → Muito bom
```

O sistema deve identificar situações inválidas, como:

```text
Pergunta sem resposta

Pergunta de resposta única com múltiplas opções

Marcações ambíguas

Combinação inválida
```

Essas situações devem ser tratadas antes do salvamento definitivo.

---

# 🧾 Dados de identificação

Os campos do cabeçalho da ficha devem determinar os campos apresentados no painel de leitura.

Não utilizar como padrão fixo:

```text
Data
Número do Selo
Comunidade
Nome do Morador
Entrevistador
```

Esses são apenas exemplos de campos configuráveis.

O resultado final deve reunir:

```text
Campos do cabeçalho
+
Respostas OMR
+
Respostas abertas
```

---

# 📤 Google Forms

A integração com Google Forms ainda não foi implementada.

A prioridade é:

```text
OMR
 ↓
resultado estruturado
 ↓
validação
 ↓
entrada manual
 ↓
revisão
 ↓
salvamento em XLSX
 ↓
Google Forms
```

O Google Forms será tratado como um destino posterior, e não como parte do núcleo OMR.

---

# 📦 Possíveis destinos futuros

Depois da estabilização do fluxo local, poderão ser avaliados:

```text
Google Forms
Google Sheets
CSV
XLSX
Outros destinos
```

A camada de destino deve permanecer separada do processamento OMR.

---

# 🧪 Testes

Existem scripts históricos e de diagnóstico.

Exemplos:

```text
teste_ambiente.py
teste_gerador_ficha.py
teste_diagnostico_ficha_gerada.py
teste_overlay_mapa.py
teste_calibracao_margem.py
teste_omr_2.py
```

Esses arquivos não representam necessariamente o fluxo final da aplicação.

Antes de remover qualquer teste:

1. verificar se ainda é utilizado;
2. identificar se existe duplicação;
3. determinar se é histórico;
4. determinar se pode servir como regressão.

---

# 🛡️ Regras de segurança

Antes de distribuir ou publicar o projeto:

Não incluir:

```text
.venv/
credenciais
tokens
PDFs pessoais
imagens pessoais de teste
resultados temporários
configurações com dados sensíveis
```

A planilha gerada pertence à pesquisa do usuário e deve ser tratada como dado produzido pelo usuário.

---

# ⚙️ Instalação

## 1. Clonar o projeto

```bash
git clone <URL_DO_REPOSITORIO>
cd PesquisaReader
```

## 2. Criar ambiente virtual

```bash
python -m venv .venv
```

## 3. Ativar ambiente

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Se necessário:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Depois:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 4. Instalar dependências

```bash
pip install -r requirements.txt
```

## 5. Executar

```bash
python app.py
```

---

# 🔍 Estrutura técnica

Principais componentes:

## `engine/gerador_ficha.py`

Responsável por:

* geração da ficha;
* layout;
* paginação;
* perguntas;
* seções;
* campos;
* caixas OMR;
* ArUcos;
* mapa;
* PDF.

## `engine/geometria.py`

Responsável por:

* detecção de ArUco;
* identificação dos marcadores;
* cálculo da homografia;
* correção geométrica;
* normalização por página.

## `engine/omr.py`

Responsável por:

* leitura das caixas;
* cálculo de percentual;
* classificação `MARCADA` / `VAZIA`.

## `engine/leitor.py`

Responsável pela integração entre:

```text
PDF
+
ArUco
+
geometria
+
normalização
+
OMR
```

e pelo resultado estruturado da leitura.

## `engine/fichas_manager.py`

Responsável por:

* ficha ativa;
* identificação da ficha;
* status;
* versão;
* pesquisa;
* associação com planilha.

## `engine/sheets.py`

Responsável por:

* criação do `.xlsx`;
* estrutura das colunas;
* validação do cabeçalho;
* inserção de novas linhas;
* formatação;
* congelamento do cabeçalho;
* filtro automático;
* preservação da estrutura da pesquisa.

## `ui/main_window.py`

Responsável pela integração dessas funções com a interface principal.

## `ui/formulario_ficha.py`

Responsável pela criação e edição das fichas.

## `ui/form_panel.py`

Responsável pelos dados inseridos manualmente durante a digitalização.

## `ui/viewer.py`

Responsável pela visualização da ficha.

## `area_omr.py`

Responsável pela visualização da área efetivamente analisada pelo OMR.

---

# 📊 Estado atual do desenvolvimento

## Núcleo validado

* [x] Geração automática de ficha
* [x] Layout em duas colunas
* [x] Paginação automática
* [x] Ficha de uma página
* [x] Ficha de duas páginas
* [x] Alteração de paginação por conteúdo/fonte
* [x] Caixas OMR automáticas
* [x] ArUco automático
* [x] ArUcoDetector
* [x] IDs ArUco por página
* [x] Geometria por página
* [x] Homografia
* [x] Normalização 1191 × 1684
* [x] Mapa OMR automático
* [x] OMR
* [x] Margem 7
* [x] Threshold 5%
* [x] Threshold de pixel escuro 150
* [x] Caixa OMR visualmente limpa
* [x] Espaçamento vertical ajustado
* [x] Ficha branca de duas páginas sem falsos positivos
* [x] Teste físico anterior com 12/12 marcações detectadas
* [x] Visualização `Onde devo marcar?`
* [x] Validação visual do mapa
* [x] Seções opcionais
* [x] Resposta única
* [x] Resposta múltipla
* [x] Perguntas abertas — estrutura inicial
* [x] Cabeçalho configurável
* [x] Cabeçalho impresso
* [x] Edição da ficha em rascunho
* [x] Ficha ativa
* [x] Logo
* [x] Leitura integrada ao fluxo
* [x] Estrutura de planilha derivada da ficha
* [x] Campos do cabeçalho como colunas
* [x] Perguntas como colunas
* [x] Seções fora da estrutura tabular
* [x] Uma ficha por linha
* [x] XLSX
* [x] Cabeçalho congelado
* [x] Filtro automático
* [x] Largura das colunas ajustada
* [x] Datas tratadas como datas Excel
* [x] Compatibilidade com Excel corrigida
* [x] Vínculo ficha → planilha
* [x] Conceito RASCUNHO / PRODUÇÃO
* [x] Estrutura inicial de versionamento

## Próxima prioridade

* [ ] Repetir teste completo utilizando o scanner real
* [ ] Confirmar 100% das marcações reais
* [ ] Confirmar 0 falsos positivos no fluxo final
* [ ] Validar respostas por pergunta
* [ ] Validar campos digitados
* [ ] Validar respostas abertas no fluxo completo
* [ ] Validar criação de nova linha no XLSX
* [ ] Validar abertura final no Excel sem reparo
* [ ] Confirmar comportamento de `Outros + Qual?`
* [ ] Testes negativos e de robustez
* [ ] Processamento de múltiplas fichas
* [ ] Melhorias de UX/UI
* [ ] Integração com Google Forms
* [ ] Avaliação de outros destinos
* [ ] Limpeza de scripts históricos
* [ ] Revisão final do armazenamento
* [ ] Empacotamento em `.exe`

---

# 🗺️ Roadmap

```text
Geração automática
        ↓
ArUco + geometria
        ↓
Normalização
        ↓
OMR
        ↓
Calibração
        ↓
Validação visual
        ↓
Leitura integrada
        ↓
Saída XLSX
        ↓
Teste físico final
        ↓
Testes de erros
        ↓
Melhoria UX/UI
        ↓
Google Forms
        ↓
Múltiplas fichas
        ↓
Empacotamento EXE
        ↓
Limpeza final
        ↓
Versão estável SDIP 2.0
```

---

# 📌 Regras importantes do projeto

## Não alterar o núcleo validado sem evidência

Os componentes:

```text
engine/omr.py
engine/geometria.py
engine/gerador_ficha.py
```

não devem ser alterados sem um problema demonstrado por teste.

## Preservar a separação de responsabilidades

```text
Gerador
    ↓
Ficha

Geometria
    ↓
Imagem normalizada

Mapa
    ↓
Localização das caixas

OMR
    ↓
Marcação

Leitor
    ↓
Resultado estruturado

Planilha
    ↓
Persistência

Destino externo
    ↓
Integração
```

## Ficha e mapa devem permanecer associados

Nunca utilizar:

```text
PDF de uma ficha
+
mapa de outra ficha
```

## Ficha em produção deve manter sua estrutura

Mudanças estruturais devem criar nova versão.

## Planilha deve refletir a ficha

A estrutura da planilha deve vir diretamente da ficha.

Seções não são dados e não geram colunas.

Cada campo do cabeçalho e cada pergunta de dados gera uma coluna.

Cada ficha processada gera uma nova linha.

---

# 🧹 Limpeza futura

Depois da estabilização do MVP:

* revisar scripts duplicados;
* remover ou arquivar testes históricos;
* revisar arquivos temporários;
* remover código não utilizado;
* eliminar lógica duplicada;
* consolidar documentação;
* revisar o repositório para distribuição.

Em especial, revisar:

```text
teste_geometria.py
teste_aruco_scan.py
```

e outros scripts de diagnóstico.

A limpeza deve ocorrer depois de concluída a fase de validação.

---

# 👨‍💻 Autor

**Diogo Barbosa**

SDIP — Sistema de Digitalização Inteligente de Pesquisas

Projeto pessoal de código aberto voltado à automação da criação, digitalização e leitura de pesquisas em papel.
