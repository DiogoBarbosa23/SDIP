# SDIP 2.0

## Sistema de Digitalização Inteligente de Pesquisas

O **SDIP 2.0** é uma aplicação desktop desenvolvida em **Python** para automatizar a criação, impressão, digitalização e leitura de fichas de pesquisas preenchidas manualmente em papel.

O sistema utiliza **processamento de imagens, ArUco, correção geométrica e OMR (Optical Mark Recognition)** para transformar respostas marcadas em papel em dados estruturados.

A versão 2.0 permite gerar dinamicamente fichas de pesquisa, independentemente da quantidade de perguntas, criando automaticamente o layout, caixas OMR, marcadores ArUco e o mapa utilizado durante a leitura.

---

## Principais recursos

* Geração automática de fichas de pesquisa
* Layout em duas colunas
* Paginação automática
* Perguntas de resposta única e múltipla
* Perguntas abertas
* Seções opcionais
* Cabeçalho configurável
* Campos de identificação personalizados
* Inserção de logo
* Edição de fichas em modo rascunho
* Ficha ativa
* Versionamento de fichas em produção
* Geração automática do mapa OMR
* Detecção de ArUco
* Correção geométrica por homografia
* Normalização das páginas
* Leitura OMR
* Visualização da área analisada pelo OMR
* Geração de planilhas `.xlsx`
* Vínculo entre ficha e planilha
* Registro de cada ficha processada como uma nova linha
* Fluxo integrado de digitalização e leitura

---

## Fluxo do sistema

```text
Criação da pesquisa
        ↓
Definição das perguntas e campos
        ↓
Geração automática da ficha
        ↓
ArUcos + caixas OMR + mapa
        ↓
Visualização e validação
        ↓
Confirmação para produção
        ↓
Geração da planilha
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
Resultado estruturado
        ↓
Revisão
        ↓
Nova linha na planilha
```

A integração com destinos externos, como **Google Forms**, ainda não foi implementada.

---

## Arquitetura

O SDIP mantém separação entre geração, geometria, OMR, leitura e persistência.

```text
Gerador de ficha
       ↓
PDF + mapa OMR
       ↓
Geometria / ArUco
       ↓
Imagem normalizada
       ↓
OMR
       ↓
Resultado estruturado
       ↓
Validação / revisão
       ↓
Planilha
       ↓
Destinos externos
```

A **ficha é a fonte de verdade** para a estrutura dos dados.

A estrutura da planilha é derivada diretamente da ficha, mantendo correspondência entre:

```text
Pergunta da ficha
       ↕
Coluna da planilha
       ↕
Resposta lida
```

---

# Recursos principais

## Geração automática de fichas

O usuário pode definir:

* Nome da pesquisa
* Título
* Cabeçalho
* Campos de identificação
* Seções
* Perguntas
* Numeração
* Tipo de resposta
* Opções
* Perguntas abertas
* Tamanho da fonte
* Logo

O sistema calcula automaticamente:

* Distribuição das perguntas
* Quebra de texto
* Organização das opções
* Caixas OMR
* Quantidade de páginas
* ArUcos
* Mapa OMR
* Áreas para perguntas abertas
* Layout do cabeçalho

O usuário não precisa informar coordenadas manualmente.

---

## Perguntas fechadas

As perguntas fechadas podem utilizar:

* Resposta única
* Resposta múltipla

Cada opção recebe automaticamente uma caixa OMR.

Exemplo:

```text
1.1_sim
1.2_nao
2.3_barra_de_apoio
2.3_corrimao
```

Os identificadores internos são utilizados para relacionar as caixas ao mapa OMR.

---

## Perguntas abertas

Perguntas abertas não possuem caixas OMR.

O sistema reserva uma área para resposta manuscrita e registra a pergunta como campo aberto.

Exemplo:

```text
2.3 Qual serviço público precisa de atenção?

________________________________________
________________________________________
```

O painel de leitura pode apresentar um campo para que o operador informe a resposta.

---

## Seções

As fichas podem ser criadas sem seções ou organizadas em seções.

Exemplo:

```text
1. Situação da obra

1.1 Pergunta
1.2 Pergunta
1.3 Pergunta

2. Qualidade da reforma

2.1 Pergunta
2.2 Pergunta
```

As seções são elementos organizacionais.

**Seções não recebem caixas OMR e não geram colunas na planilha.**

---

## Cabeçalho configurável

O cabeçalho pode ser definido de acordo com a necessidade da pesquisa.

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

Os campos configurados são utilizados na:

```text
Ficha impressa
      +
Interface de leitura
      +
Planilha
```

Os campos não são fixos e podem variar de acordo com cada pesquisa.

---

# Edição e versionamento

As fichas possuem ciclo de vida:

```text
RASCUNHO
   ↓
GERAÇÃO
   ↓
VISUALIZAÇÃO
   ↓
CONFIRMAÇÃO
   ↓
PRODUÇÃO
```

Enquanto estiver em **RASCUNHO**, a ficha pode ser editada.

Alterações estruturais depois da entrada em produção devem resultar em uma nova versão.

Exemplo:

```text
Pesquisa
├── Ficha v1
│   └── Planilha v1
│
└── Ficha v2
    └── Planilha v2
```

Cada versão mantém sua própria estrutura, PDF, mapa OMR e planilha associada.

---

## Ficha ativa

A aplicação mantém uma **ficha ativa**, utilizada como referência para:

* Visualização
* PDF
* Mapa OMR
* Leitura
* Campos de identificação
* Perguntas abertas
* Planilha associada

O mapa de uma ficha não deve ser utilizado para processar outra ficha.

---

# Processamento OMR

Cada opção da ficha possui uma caixa OMR registrada automaticamente no mapa.

O processo de leitura é:

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

Parâmetros atualmente validados:

```text
Margem interna: 7 pixels
Threshold de pixel escuro: 150
Limiar de marcação: 5%
```

O limiar de marcação utilizado é:

```python
percentual >= 5.0
```

Esses parâmetros não devem ser alterados sem nova validação física.

---

# ArUco e correção geométrica

A ficha utiliza quatro marcadores ArUco por página.

Dicionário utilizado:

```text
DICT_4X4_50
```

A detecção utiliza:

```python
cv2.aruco.ArucoDetector
```

A versão do OpenCV validada durante o desenvolvimento foi:

```text
4.12.0
```

Os IDs reais dos marcadores são utilizados para identificar a página correspondente.

---

## Geometria por página

Cada página é processada individualmente.

```text
Página 1
    ↓
IDs correspondentes
    ↓
Homografia
    ↓
Normalização

Página 2
    ↓
IDs correspondentes
    ↓
Homografia
    ↓
Normalização
```

Uma página com problema de alinhamento não deve afetar geometricamente as demais.

---

## Normalização

As páginas são normalizadas para:

```text
1191 × 1684 pixels
```

Fluxo:

```text
PDF escaneado
    ↓
Renderização
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

O mapa OMR utiliza coordenadas da imagem normalizada.

---

# Mapa OMR

O mapa OMR é gerado automaticamente pelo gerador de fichas.

Cada caixa é registrada com:

```text
nome
página
x1
y1
x2
y2
```

O mapa também registra informações relacionadas à ficha, como:

* Dimensões da imagem
* Quantidade de páginas
* ArUcos
* Coordenadas
* Perguntas abertas
* Campos de identificação

Cada ficha possui seu próprio mapa.

O usuário não precisa mapear manualmente cada caixa OMR.

---

# Visualização da área OMR

A aplicação possui o recurso:

```text
Onde devo marcar?
```

Esse recurso mostra a ficha ativa e destaca a área efetivamente analisada pelo OMR.

É utilizado para:

* Mostrar onde o usuário deve marcar
* Validar o alinhamento do mapa
* Confirmar a posição das caixas
* Auxiliar no diagnóstico
* Validar alterações no layout

A marcação vermelha existe somente na visualização.

**Ela não é gravada no PDF e não aparece na ficha impressa.**

Arquivo relacionado:

```text
area_omr.py
```

---

# Layout automático

O gerador utiliza duas colunas independentes.

```text
┌──────────────────────┬──────────────────────┐
│ Coluna esquerda      │ Coluna direita       │
│                      │                      │
│ Perguntas de cima    │ Perguntas de cima    │
│ para baixo           │ para baixo           │
│                      │                      │
└──────────────────────┴──────────────────────┘
```

A linha central da página funciona como limite de layout.

Uma pergunta não deve ultrapassar a área destinada à sua coluna.

Quando uma pergunta não cabe na coluna atual, o sistema continua na próxima coluna.

Quando as duas colunas ficam sem espaço, uma nova página é criada.

Uma pergunta não deve ser dividida entre:

* Colunas
* Páginas

O gerador foi validado com fichas de uma e duas páginas.

---

# Cabeçalho e logo

O cabeçalho pode conter:

* Título
* Nome da pesquisa
* Campos de identificação
* Área reservada para logo

A logo é redimensionada proporcionalmente para permanecer dentro da área destinada a ela sem sobrepor os ArUcos ou demais elementos do cabeçalho.

---

# Planilha XLSX

A estrutura da planilha é derivada diretamente da ficha.

A ordem das colunas é:

```text
Campos do cabeçalho
        ↓
Perguntas
```

As seções não geram colunas.

Cada ficha processada gera uma nova linha.

Exemplo:

```text
Data
Número do Selo
Comunidade
Nome do Morador
Entrevistador
1.1 A obra foi concluída?
1.2 A obra ficou boa?
1.3 Houve algum problema?
2.1 Como avalia a qualidade?
2.2 O serviço atendeu à expectativa?
```

A planilha possui:

* Primeira linha como cabeçalho
* Primeira linha congelada
* Filtro automático
* Largura das colunas ajustada
* Tratamento de datas
* Compatibilidade com Excel

---

## Vínculo ficha → planilha

O fluxo de produção é:

```text
Criar ficha
    ↓
Gerar
    ↓
Visualizar
    ↓
Confirmar para produção
    ↓
Gerar planilha
    ↓
Escolher local para salvar
    ↓
Ficha vinculada à planilha
```

Durante a leitura:

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

O usuário não precisa selecionar novamente a planilha a cada leitura.

---

# Ficha como fonte de verdade

O SDIP não deve manter um segundo modelo manual de planilha.

A estrutura da ficha é utilizada para gerar tanto o PDF quanto a estrutura da planilha:

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
Cabeçalho
```

Dessa forma:

```text
Ficha
  ↓
Fonte única de verdade
```

Isso mantém a correspondência entre pergunta, coluna e resposta.

---

# Configuração de impressão

Para preservar a geometria do formulário:

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

Alterações de escala podem modificar a relação entre a ficha física e as coordenadas do mapa OMR.

---

# Configuração do scanner

Configuração utilizada nos testes:

```text
600 DPI
PDF
```

As páginas são processadas individualmente e os ArUcos são utilizados para corrigir a perspectiva.

O teste físico final deverá utilizar a ficha atual em produção e o scanner que será utilizado no processo real.

---

# Validação

Durante o desenvolvimento foram realizados testes visuais e físicos.

## Teste com ficha branca

Uma ficha branca de duas páginas apresentou:

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

Resultado consolidado:

```text
Total: 140
Marcadas: 0
Vazias: 140
```

Resultado:

**0 falsos positivos.**

Também foi realizado um teste físico anterior com:

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

Esse resultado é histórico e deverá ser novamente validado utilizando a versão atual em produção.

---

# Respostas e validação

Após o OMR, as marcações devem ser convertidas em respostas por pergunta.

Exemplos:

```text
1.1 → Sim

1.2 → Não

2.3 → Barra de apoio + Corrimão
```

O sistema deve identificar situações inválidas, como:

* Pergunta sem resposta
* Múltiplas respostas em pergunta de resposta única
* Marcações ambíguas
* Combinações inválidas

Essas situações devem ser tratadas antes do salvamento definitivo.

---

# Dados de identificação

Os campos do cabeçalho determinam os campos apresentados durante a leitura.

Não existem campos obrigatórios fixos.

Exemplos como:

```text
Data
Número do Selo
Comunidade
Nome do Morador
Entrevistador
```

são apenas configurações possíveis.

O resultado final reúne:

```text
Campos do cabeçalho
        +
Respostas OMR
        +
Respostas abertas
```

---

# Google Forms

A integração com Google Forms ainda não foi implementada.

A arquitetura prevista é:

```text
OMR
 ↓
Resultado estruturado
 ↓
Validação
 ↓
Revisão
 ↓
XLSX
 ↓
Destino externo
```

O Google Forms será tratado como um destino posterior e não como parte do núcleo OMR.

Outros destinos poderão ser avaliados futuramente, como:

```text
Google Forms
Google Sheets
CSV
XLSX
Outros destinos
```

---

# Estrutura técnica

Principais componentes:

```text
engine/
├── gerador_ficha.py
├── geometria.py
├── omr.py
├── leitor.py
├── fichas_manager.py
└── sheets.py

ui/
├── main_window.py
├── formulario_ficha.py
├── form_panel.py
└── viewer.py

area_omr.py
app.py
requirements.txt
```

### `engine/gerador_ficha.py`

Responsável pela geração da ficha, layout, paginação, perguntas, seções, campos, caixas OMR, ArUcos, mapa e PDF.

### `engine/geometria.py`

Responsável pela detecção dos ArUcos, identificação dos marcadores, homografia, correção geométrica e normalização.

### `engine/omr.py`

Responsável pela leitura das caixas e classificação entre `MARCADA` e `VAZIA`.

### `engine/leitor.py`

Integra PDF, ArUco, geometria, normalização e OMR para produzir o resultado estruturado.

### `engine/fichas_manager.py`

Responsável pela ficha ativa, identificação, status, versão, pesquisa e associação com planilha.

### `engine/sheets.py`

Responsável pela criação e atualização dos arquivos `.xlsx`.

### `ui/`

Responsável pela interface gráfica e interação com as funcionalidades do sistema.

### `area_omr.py`

Responsável pela visualização das áreas efetivamente analisadas pelo OMR.

---

# Testes

Existem scripts históricos e de diagnóstico utilizados durante o desenvolvimento.

Exemplos:

```text
teste_ambiente.py
teste_gerador_ficha.py
teste_diagnostico_ficha_gerada.py
teste_overlay_mapa.py
teste_calibracao_margem.py
teste_omr_2.py
teste_geometria.py
teste_aruco_scan.py
```

Esses arquivos não representam necessariamente o fluxo final da aplicação.

Antes de remover qualquer teste:

1. Verificar se ainda é utilizado
2. Identificar possíveis duplicações
3. Determinar se é histórico
4. Verificar se pode ser utilizado como teste de regressão

---

# Instalação

## Requisitos

* Python
* Git
* Windows recomendado para o ambiente atual

## 1. Clonar o projeto

```bash
git clone <URL_DO_REPOSITORIO>
cd SDIP-2.0
```

## 2. Criar o ambiente virtual

```bash
python -m venv .venv
```

## 3. Ativar o ambiente virtual

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Caso o PowerShell bloqueie a execução:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Depois:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 4. Instalar as dependências

Com a `.venv` ativada:

```powershell
pip install -r requirements.txt
```

## 5. Executar

```powershell
python app.py
```

### Fluxo rápido

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

A pasta `.venv/` é local e **não deve ser enviada para o GitHub**.

---

# Segurança

Antes de distribuir ou publicar o projeto, não incluir:

```text
.venv/
credenciais
tokens
dados pessoais
PDFs pessoais
imagens pessoais de teste
resultados temporários
configurações com dados sensíveis
```

---

# Estado atual

## Concluído

* [x] Geração automática de fichas
* [x] Layout em duas colunas
* [x] Paginação automática
* [x] Fichas de uma e duas páginas
* [x] Perguntas de resposta única
* [x] Perguntas de resposta múltipla
* [x] Perguntas abertas
* [x] Seções opcionais
* [x] Cabeçalho configurável
* [x] Logo
* [x] Edição em rascunho
* [x] Ficha ativa
* [x] Estrutura inicial de versionamento
* [x] ArUco automático
* [x] ArUcoDetector
* [x] IDs ArUco por página
* [x] Correção geométrica
* [x] Homografia
* [x] Normalização 1191 × 1684
* [x] Mapa OMR automático
* [x] OMR
* [x] Margem OMR validada
* [x] Threshold de marcação
* [x] Visualização da área OMR
* [x] Leitura integrada
* [x] Geração de XLSX
* [x] Estrutura da planilha derivada da ficha
* [x] Cabeçalho congelado
* [x] Filtro automático
* [x] Tratamento de datas
* [x] Vínculo ficha → planilha

## Próximas etapas

* [ ] Repetir teste completo utilizando o scanner real
* [ ] Confirmar todas as marcações reais
* [ ] Confirmar ausência de falsos positivos no fluxo final
* [ ] Validar respostas por pergunta
* [ ] Validar campos digitados
* [ ] Validar respostas abertas no fluxo completo
* [ ] Validar criação de novas linhas no XLSX
* [ ] Validar abertura final no Excel sem reparos
* [ ] Confirmar comportamento de `Outros + Qual?`
* [ ] Testes negativos e de robustez
* [ ] Processamento de múltiplas fichas
* [ ] Melhorias de UX/UI
* [ ] Limpeza de scripts históricos
* [ ] Revisão final do armazenamento
* [ ] Integração com Google Forms
* [ ] Avaliação de outros destinos
* [ ] Empacotamento em `.exe`
* [ ] Versão estável do SDIP 2.0

---

# Regras importantes do projeto

## Preservar o núcleo validado

Os componentes principais:

```text
engine/omr.py
engine/geometria.py
engine/gerador_ficha.py
```

não devem ser alterados sem um problema demonstrado por testes.

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
Marcações

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
Mapa de outra ficha
```

## Ficha em produção deve manter sua estrutura

Alterações estruturais devem criar uma nova versão.

## Planilha deve refletir a ficha

A estrutura da planilha deve ser derivada diretamente da ficha.

Seções não são dados e não geram colunas.

Cada campo do cabeçalho e cada pergunta de dados gera uma coluna.

Cada ficha processada gera uma nova linha.

---

# Roadmap

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
Testes de robustez
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
SDIP 2.0 estável
```

---

# Propriedade e uso

O **SDIP 2.0 é um projeto de propriedade de seu autor**.

O código-fonte, arquitetura, lógica, documentação e demais componentes do projeto **não estão autorizados para cópia, redistribuição, modificação, exploração comercial ou utilização por terceiros sem autorização expressa do autor**.

Este repositório é privado e o projeto poderá ser **comercializado futuramente**.

**Todos os direitos reservados.**

---

# Autor

**Diogo Barbosa**

SDIP — Sistema de Digitalização Inteligente de Pesquisas
