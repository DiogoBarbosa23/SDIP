# SDIP

## Sistema de Digitalização Inteligente de Pesquisas

O **SDIP** é uma aplicação desktop desenvolvida em **Python** para automatizar a criação, impressão, digitalização e leitura de pesquisas preenchidas manualmente em papel.

O sistema transforma fichas físicas em dados estruturados utilizando **processamento de imagens, marcadores ArUco, correção geométrica por homografia e OMR (Optical Mark Recognition)**.

O projeto surgiu a partir de uma necessidade real de trabalho: reduzir o processo manual de criação, preenchimento, conferência e digitalização de pesquisas realizadas em formulários impressos.

---

## Fluxo principal

```text
Criar pesquisa
      ↓
Configurar cabeçalho, perguntas e seções
      ↓
Gerar ficha automaticamente
      ↓
Visualizar e validar
      ↓
Colocar pesquisa em produção
      ↓
Imprimir
      ↓
Preenchimento manual
      ↓
Digitalizar em PDF
      ↓
Detectar ArUcos
      ↓
Corrigir geometria
      ↓
Executar leitura OMR
      ↓
Conferir e preencher campos manuais
      ↓
Salvar resultado
      ↓
Registrar na planilha vinculada
```

---

## Principais funcionalidades

### Criação de fichas

O SDIP permite configurar:

* nome da pesquisa;
* título;
* logo;
* campos personalizados de identificação;
* seções;
* perguntas;
* respostas únicas;
* respostas múltiplas;
* perguntas abertas;
* opções de resposta;
* tamanho da fonte.

O sistema gera automaticamente:

* layout da ficha;
* distribuição em duas colunas;
* paginação;
* caixas OMR;
* marcadores ArUco;
* áreas de respostas abertas;
* mapa de coordenadas OMR;
* PDF final da pesquisa.

O usuário não precisa definir coordenadas manualmente.

---

## Interface adaptada para notebooks

A interface foi reorganizada para aproveitar melhor telas menores.

### Criar / Editar ficha

A tela utiliza duas áreas lado a lado:

```text
┌────────────────────────┬──────────────────────────────┐
│ Configuração           │ Estrutura da ficha          │
│                        │                              │
│ Nome                   │ Perguntas                    │
│ Título                 │ Seções                       │
│ Logo                   │ Opções                       │
│ Fonte                  │                              │
│ Identificação          │                              │
│                        │                              │
└────────────────────────┴──────────────────────────────┘
```

As áreas podem ser redimensionadas pelo usuário.

### Digitalizar / Preencher

A ficha e os campos de preenchimento são exibidos simultaneamente:

```text
┌────────────────────────┬──────────────────────────────┐
│                        │ Ações                        │
│                        │                              │
│          PDF           │ Identificação               │
│                        │                              │
│                        │ Respostas abertas            │
│                        │                              │
│                        │ Salvar resultado             │
└────────────────────────┴──────────────────────────────┘
```

O divisor entre as áreas também pode ser movimentado com o mouse.

---

## Visualizador de PDF

O visualizador permite acompanhar a ficha durante a conferência e digitalização.

Recursos atuais:

* ajuste automático da página à área disponível;
* preservação da proporção da ficha;
* visualização da página completa;
* zoom;
* redução de zoom;
* retorno ao modo ajustado;
* scroll quando a página está ampliada;
* redimensionamento junto com a interface.

---

## OMR

Cada alternativa de uma pergunta fechada recebe automaticamente uma caixa OMR.

O fluxo de leitura é:

```text
Caixa OMR
    ↓
Recorte interno
    ↓
Análise dos pixels
    ↓
Percentual de pixels escuros
    ↓
MARCADA ou VAZIA
```

Parâmetros atualmente validados:

```text
Margem interna: 7 pixels
Threshold de pixel escuro: 150
Limiar de marcação: 5%
```

Esses parâmetros fazem parte do núcleo validado do projeto e não devem ser alterados sem novos testes físicos.

---

## ArUco e correção geométrica

Cada página utiliza quatro marcadores ArUco.

Configuração atual:

```text
Dicionário: DICT_4X4_50
OpenCV validado: 4.12.0
```

O processamento utiliza os IDs dos marcadores para identificar e corrigir cada página individualmente.

```text
PDF digitalizado
      ↓
Detecção ArUco
      ↓
Identificação dos marcadores
      ↓
Homografia
      ↓
Correção de perspectiva
      ↓
Normalização
      ↓
OMR
```

A resolução normalizada utilizada pelo sistema é:

```text
1191 × 1684 pixels
```

---

## Mapa OMR

O mapa OMR é criado automaticamente junto com a ficha.

Cada caixa contém informações como:

```text
nome
página
x1
y1
x2
y2
```

O mapa também mantém dados relacionados a:

* campos de identificação;
* perguntas abertas;
* páginas;
* marcadores;
* dimensões;
* coordenadas.

Cada ficha possui seu próprio mapa.

O PDF e o mapa correspondente devem permanecer associados.

---

## Perguntas abertas e identificação

Campos de identificação e perguntas abertas são preenchidos pelo operador durante a digitalização.

Exemplos:

```text
Data
Comunidade
Entrevistador
Número do imóvel
Código
Observação
```

O resultado final combina:

```text
Campos de identificação
        +
Respostas OMR
        +
Respostas abertas
```

---

## Planilha XLSX

Atualmente o SDIP gera e utiliza uma planilha `.xlsx` vinculada à pesquisa.

Sua estrutura é derivada diretamente da ficha:

```text
Campos do cabeçalho
        ↓
Perguntas
```

As seções são apenas organizacionais e não geram colunas.

Cada ficha processada adiciona uma nova linha à planilha.

A planilha possui:

* cabeçalho;
* primeira linha congelada;
* filtro automático;
* organização das colunas;
* tratamento de dados;
* compatibilidade com Excel.

---

## Ficha como fonte de verdade

A estrutura da ficha é utilizada como referência para todo o fluxo:

```text
Estrutura da pesquisa
       ├── PDF
       ├── Mapa OMR
       ├── Campos de preenchimento
       └── Estrutura da planilha
```

Isso reduz o risco de divergência entre a ficha física e os dados armazenados.

---

## Ciclo de vida das fichas

O fluxo previsto é:

```text
RASCUNHO
    ↓
GERAÇÃO
    ↓
VALIDAÇÃO
    ↓
PRODUÇÃO
```

Uma pesquisa em produção deve preservar sua estrutura.

Alterações estruturais posteriores devem gerar uma nova versão da pesquisa.

---

## Impressão

Para preservar a geometria da ficha:

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
Escala automática
```

---

## Digitalização

Configuração utilizada nos testes físicos:

```text
Scanner: 600 DPI
Formato: PDF
```

As páginas são corrigidas geometricamente antes da leitura OMR.

---

## Validação

O núcleo do OMR já passou por testes físicos.

### Ficha branca

Teste de duas páginas:

```text
Total: 140 caixas
Marcadas: 0
Vazias: 140
```

Resultado:

```text
0 falsos positivos
```

### Teste físico com marcações

Em teste anterior:

```text
Marcações reais: 12
Marcações reconhecidas: 12
```

Resultado:

```text
12/12
100%
```

Novas baterias de testes continuarão sendo realizadas conforme o sistema evoluir.

---

## Tecnologias

* Python
* CustomTkinter
* Tkinter
* OpenCV
* ArUco
* OMR
* NumPy
* Pillow
* PyMuPDF
* processamento de imagens
* homografia
* XLSX

---

## Estrutura principal

```text
SDIP/
│
├── engine/
│   ├── gerador_ficha.py
│   ├── geometria.py
│   ├── omr.py
│   ├── leitor.py
│   ├── fichas_manager.py
│   └── sheets.py
│
├── ui/
│   ├── main_window.py
│   ├── formulario_ficha.py
│   ├── form_panel.py
│   └── viewer.py
│
├── config/
├── area_omr.py
├── app.py
├── requirements.txt
└── README.md
```

---

## Componentes críticos

Os seguintes componentes fazem parte do núcleo já validado:

```text
engine/gerador_ficha.py
engine/geometria.py
engine/omr.py
```

Alterações nesses arquivos devem ser realizadas somente quando houver um problema demonstrado por testes.

---

## Instalação

### 1. Criar ambiente virtual

```powershell
python -m venv .venv
```

### 2. Ativar no PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

Caso a execução esteja bloqueada:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Depois:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependências

```powershell
pip install -r requirements.txt
```

### 4. Executar

```powershell
python app.py
```

A pasta `.venv/` é local e não deve ser enviada ao repositório.

---

# Estado atual

## Implementado

* [x] Geração automática de fichas
* [x] Layout automático em duas colunas
* [x] Paginação automática
* [x] Campos personalizados de identificação
* [x] Perguntas únicas
* [x] Perguntas múltiplas
* [x] Perguntas abertas
* [x] Seções
* [x] Logo
* [x] Configuração de fonte
* [x] Ficha ativa
* [x] Estrutura de versionamento
* [x] ArUco
* [x] Homografia
* [x] Normalização
* [x] Mapa OMR automático
* [x] Leitura OMR
* [x] Visualização das áreas OMR
* [x] Geração e atualização de XLSX
* [x] Vínculo entre ficha e planilha
* [x] Interface adaptada para notebooks
* [x] Painéis redimensionáveis
* [x] Visualizador de PDF com zoom
* [x] Scroll nas principais áreas da interface

---

## Próximas etapas

### Prioridade

* [ ] Integração com Google Sheets online
* [ ] Permitir múltiplos usuários/máquinas na mesma pesquisa
* [ ] Seleção e processamento de múltiplos PDFs
* [ ] Fila de fichas para processamento
* [ ] Salvar e renomear o PDF junto ao resultado
* [ ] Associar PDF salvo ao respectivo registro
* [ ] Padronizar datas para `DD/MM/AAAA`
* [ ] Adicionar opção `Manter padrão`
* [ ] Permitir `Manter padrão` em qualquer campo do cabeçalho
* [ ] Alertar antes de salvar campos manuais em branco
* [ ] Melhorar o fluxo operacional de digitalização

### Posteriormente

* [ ] Normalização de identificadores
* [ ] Detecção e alerta de registros duplicados
* [ ] Testes negativos e de robustez
* [ ] Processamento em lote
* [ ] Revisão da edição de rascunhos
* [ ] Limpeza e refatoração técnica
* [ ] Simplificação do visualizador, se necessário
* [ ] Empacotamento em `.exe`
* [ ] Versão estável para distribuição

---

# Próxima evolução estrutural

A próxima integração prevista é o **Google Sheets** como destino compartilhado dos resultados.

Objetivo:

```text
Máquina A ─┐
           │
Máquina B ─┼──→ Google Sheets compartilhado
           │
Máquina C ─┘
```

Uma pesquisa em produção deverá poder receber registros enviados por diferentes operadores e computadores para uma mesma base online.

A integração ainda **não está implementada**.

---

# Segurança

Não devem ser incluídos no repositório:

```text
.venv/
credenciais
tokens
arquivos .env
dados pessoais
PDFs de pesquisas reais
resultados com informações sensíveis
arquivos temporários
```

---

# Propriedade e uso

O **SDIP é um projeto de propriedade de seu autor**.

O código-fonte, arquitetura, lógica, documentação e demais componentes do projeto não estão autorizados para cópia, redistribuição, modificação, exploração comercial ou utilização por terceiros sem autorização expressa do autor.

O projeto poderá ser comercializado futuramente.

**Todos os direitos reservados.**

---

# Autor

**Diogo Barbosa**

SDIP — Sistema de Digitalização Inteligente de Pesquisas
