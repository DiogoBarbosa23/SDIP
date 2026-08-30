# CONTINUIDADE — SDIP 2.0

Este arquivo é a fonte principal de continuidade do projeto.

Antes de continuar o desenvolvimento:

1. Ler este arquivo.
2. Verificar o estado real do código no repositório.
3. Verificar `git status`.
4. Verificar o último commit.
5. Não assumir que arquivos antigos representam o estado atual.
6. Preservar funcionalidades já validadas.
7. Alterar uma parte por vez quando estivermos calibrando.
8. Testar depois de cada alteração importante.
9. Não recalibrar componentes já validados sem evidência técnica.

---

# 1. PROJETO

## Nome

**SDIP 2.0 — Sistema de Digitalização Inteligente de Pesquisas**

## Tipo

Projeto pessoal de código aberto.

O projeto não é vinculado a uma instituição específica.

A ideia é desenvolver uma ferramenta simples e reutilizável para criação, impressão, digitalização e leitura automática de pesquisas em papel.

## Objetivo

Permitir que uma pessoa não técnica consiga:

1. criar uma ficha de pesquisa;
2. definir quantas perguntas quiser;
3. definir seções opcionais;
4. definir as opções de resposta;
5. definir perguntas abertas;
6. definir os campos do cabeçalho;
7. gerar automaticamente a ficha;
8. imprimir a ficha;
9. preenchê-la manualmente;
10. escanear as fichas;
11. processar o PDF;
12. revisar as respostas;
13. preencher os dados de identificação e data;
14. preencher respostas abertas;
15. salvar o resultado;
16. posteriormente enviar os resultados para um destino configurável, inicialmente Google Forms.

---

# 2. DIFERENÇA ENTRE SDIP 1.0 E SDIP 2.0

O SDIP 1.0 utilizava uma ficha previamente definida e um mapa de caixas OMR associado manualmente ao formulário.

O SDIP 2.0 está sendo construído para que:

```text
Perguntas fornecidas pelo usuário

        ↓

Seções opcionais

        ↓

Tipo de resposta

        ↓

Perguntas abertas

        ↓

Campos de identificação

        ↓

Geração automática da ficha

        ↓

Caixas OMR automáticas

        ↓

ArUcos automáticos

        ↓

Mapa OMR automático

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

Validação das respostas

        ↓

Identificação + data + respostas abertas

        ↓

Revisão

        ↓

Salvamento

        ↓

Destino configurável
```

O usuário não deve precisar conhecer coordenadas, homografia, ArUco, mapa OMR ou parâmetros internos do leitor.

---

# 3. TECNOLOGIAS

## Sistema operacional

Windows 11

## Linguagem

Python 3.13.x

## Ambiente

`.venv`

A pasta `.venv` nunca deve ser enviada ao GitHub.

## Bibliotecas principais

* OpenCV
* OpenCV ArUco
* NumPy
* Pillow
* PyMuPDF
* CustomTkinter
* Tkinter
* gspread
* google-auth

O projeto possui `requirements.txt`.

---

# 4. ESTRUTURA ATUAL

Estrutura principal:

```text
PesquisaReader/

├── app.py
├── README.md
├── CONTINUIDADE.md
├── requirements.txt
│
├── config/
│
├── engine/
│   ├── __init__.py
│   ├── geometria.py
│   ├── gerador_ficha.py
│   ├── omr.py
│   ├── pdf_reader.py
│   ├── fichas_manager.py
│   ├── leitor.py
│   └── sheets.py
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── viewer.py
│   ├── form_panel.py
│   └── formulario_ficha.py
│
├── assets/
├── fichas/
├── temp/
├── uploads/
└── area_omr.py
```

Existem também diversos scripts de teste e diagnóstico na raiz.

Eles ainda não foram totalmente limpos.

`area_omr.py` foi criado inicialmente como diagnóstico da área OMR e posteriormente integrado ao aplicativo como funcionalidade permanente.

---

# 5. ESTADO DO GIT E REPOSITÓRIO

O SDIP 2.0 está atualmente sendo mantido no repositório Git configurado no projeto.

O histórico anterior do SDIP 1.0 deve permanecer preservado e não deve ser misturado conceitualmente com a versão 2.0.

Antes de alterações importantes:

```powershell
git status
git log --oneline -5
git remote -v
```

Não executar comandos destrutivos sem explicar primeiro.

Não inventar o nome ou conteúdo do último commit. Verificar o estado real do repositório.

---

# 6. GERADOR DE FICHA — ESTADO ATUAL

O arquivo responsável é:

```text
engine/gerador_ficha.py
```

O gerador atualmente consegue:

* receber perguntas;
* receber tipo de resposta;
* receber opções;
* receber seções;
* receber perguntas abertas;
* receber campos de identificação;
* receber tamanho de fonte;
* gerar uma ou várias páginas;
* distribuir perguntas automaticamente em duas colunas;
* gerar caixas OMR;
* registrar coordenadas;
* gerar ArUcos;
* registrar os ArUcos;
* gerar mapa OMR;
* registrar perguntas abertas;
* registrar campos de identificação;
* criar cabeçalho configurável;
* incluir logo;
* gerar imagens das páginas;
* gerar PDF a partir das páginas produzidas.

O usuário não deve configurar coordenadas manualmente.

---

# 7. LAYOUT DA FICHA

A ficha utiliza duas colunas independentes.

```text
┌──────────────────────┬──────────────────────┐
│ Coluna esquerda      │ Coluna direita       │
│                      │                      │
│ perguntas de cima    │ perguntas de cima    │
│ para baixo           │ para baixo           │
│                      │                      │
└──────────────────────┴──────────────────────┘
```

Existe uma linha central imaginária.

Nenhuma pergunta da coluna esquerda pode ultrapassar essa linha.

Nenhuma pergunta da coluna direita pode invadir a coluna esquerda.

A ordem é:

```text
1. preencher coluna esquerda

2. quando não couber a próxima pergunta:
   continuar no topo da coluna direita

3. quando as duas colunas acabarem:
   criar nova página
```

Uma pergunta não deve ser dividida entre colunas.

Uma pergunta não deve ser dividida entre páginas.

O sistema deve continuar funcionando independentemente da quantidade de perguntas.

---

# 8. QUANTIDADE DE PERGUNTAS E PAGINAÇÃO

A quantidade de perguntas não é fixa.

O `GeradorFicha` deve aceitar poucas ou muitas perguntas e decidir automaticamente quantas páginas são necessárias.

O sistema foi validado com fichas de uma e duas páginas.

Também foi validada a mudança do tamanho da fonte:

```text
Fonte maior

    ↓

ficha passa para 2 páginas

    ↓

mapeamento continua correto
```

Depois:

```text
Fonte reduzida

    ↓

ficha volta para 1 página

    ↓

mapeamento continua correto
```

Conclusão atual:

**A paginação e o mapeamento das caixas OMR permanecem corretos quando a ficha ocupa uma ou duas páginas e quando a alteração da fonte muda essa quantidade.**

O aproveitamento de espaço ainda pode ser melhorado futuramente, mas não é prioridade neste momento.

---

# 9. TESTE TÉCNICO ATUAL DO GERADOR

Existem scripts históricos e de diagnóstico relacionados à geração da ficha.

O arquivo `teste_gerador_ficha.py` é um teste técnico e não representa a interface final do usuário.

O fluxo atual da aplicação utiliza o `GeradorFicha` por meio do `FormularioFicha` e do `MainWindow`.

---

# 10. FLUXO ATUAL DE CRIAÇÃO DE FICHA

A interface de criação já foi implementada.

Fluxo atual:

```text
Abrir SDIP

        ↓

Criar nova ficha

        ↓

Informar nome da pesquisa

        ↓

Informar título opcional

        ↓

Adicionar seções, se necessário

        ↓

Adicionar perguntas

        ↓

Definir tipo de resposta

        ↓

Marcar pergunta aberta, se necessário

        ↓

Adicionar opções

        ↓

Gerar ficha

        ↓

Gerador calcula automaticamente:

    - layout
    - páginas
    - caixas OMR
    - ArUcos
    - mapa
    - perguntas abertas
    - cabeçalho

        ↓

Ficha pronta
```

O usuário não deve configurar coordenadas manualmente.

---

# 11. SEÇÕES

Seções são opcionais.

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

As seções são utilizadas para organização visual e numeração.

**As seções não recebem caixas OMR próprias e não geram colunas na planilha.**

---

# 12. PERGUNTAS ABERTAS

Perguntas podem ser marcadas no editor como:

```text
[X] Resposta aberta
```

Quando uma pergunta é aberta:

* as opções OMR são ocultadas no editor;
* nenhuma caixa OMR é criada para ela;
* uma área de resposta manuscrita é reservada na ficha;
* a pergunta é registrada em `perguntas_abertas`;
* o mapa informa o número da pergunta e a página;
* o painel do leitor possui campo específico para essa resposta.

Exemplo:

```text
2.3 Qual serviço público precisa de atenção?

__________________________________________
```

O teste inicial da funcionalidade já foi realizado.

O fluxo completo ainda precisa ser validado fisicamente junto com:

```text
OMR
+
identificação
+
data
+
resposta aberta
+
validação
+
salvamento
```

---

# 13. CABEÇALHO CONFIGURÁVEL

O cabeçalho da versão 2.0 não deve depender do padrão fixo do SDIP 1.0.

O usuário que cria a ficha pode definir quais campos deseja utilizar.

Exemplos:

```text
Nome do morador
Data
Código
Comunidade
Entrevistador
Bairro
Número do imóvel
Identificador
```

Os campos definidos devem aparecer:

```text
na ficha impressa

        +

no painel do leitor

        +

no resultado final

        +

na estrutura da planilha
```

Os campos antigos da versão 1.0:

```text
Data
Número do Selo
Comunidade
Nome do Morador
Entrevistador
```

não devem mais ser tratados como campos obrigatórios do sistema 2.0.

Eles são apenas exemplos de campos que podem ser cadastrados.

---

# 14. CABEÇALHO E MAPEAMENTO OMR

O cabeçalho é visual e não participa diretamente das coordenadas das caixas OMR.

A lógica geométrica continua baseada nos ArUcos e na transformação da página para 1191 × 1684.

Portanto:

```text
Cabeçalho

    ↓

não define as coordenadas OMR

ArUcos

    ↓

definem a transformação geométrica

Mapa

    ↓

define as caixas na imagem normalizada

OMR

    ↓

lê as caixas
```

Alterações no cabeçalho não devem exigir recalibração do OMR desde que não alterem:

* posição dos ArUcos;
* dimensões da página;
* transformação geométrica;
* posição real das caixas.

---

# 15. LOGO

A logo passou a fazer parte do cabeçalho.

A lógica atual coloca a logo em uma área reservada ao lado do bloco de título/nome, sem ocupar o espaço do ArUco superior esquerdo.

O tamanho da logo é adaptado proporcionalmente à área reservada.

A posição atual foi considerada satisfatória por enquanto.

Melhorias visuais futuras:

* deixar a área mais quadrada;
* testar PNG real;
* melhorar adaptação automática;
* refinamento visual.

Essas melhorias não são prioridade atual.

---

# 16. EDIÇÃO DA FICHA

A aplicação possui suporte para editar a ficha.

O `FormularioFicha` consegue receber `dados_iniciais` e reconstruir a estrutura da ficha.

O usuário pode:

* alterar o nome;
* alterar o título;
* alterar seções;
* alterar perguntas;
* alterar opções;
* transformar uma pergunta em aberta;
* remover elementos;
* adicionar novos elementos;
* gerar novamente.

Fluxo em rascunho:

```text
Criar ficha
    ↓
Gerar
    ↓
Visualizar
    ↓
Editar ficha
    ↓
Gerar novamente
```

A estrutura de gerenciamento de fichas já fornece um identificador para cada ficha.

---

# 17. ARUCO — ESTADO VALIDADO

A ficha utiliza quatro ArUcos por página.

Dicionário:

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

O `gerador_ficha.py` gera esses quatro ArUcos automaticamente.

---

# 18. DETECÇÃO GEOMÉTRICA

O arquivo atual:

```text
engine/geometria.py
```

usa a detecção real de ArUco do OpenCV.

Versão validada do OpenCV:

```text
4.12.0
```

API utilizada:

```python
cv2.aruco.ArucoDetector
```

A geometria trabalha com os IDs reais dos marcadores.

Isso substituiu a estratégia anterior baseada apenas em contornos quadrados.

Essa alteração foi necessária porque os ArUcos possuem diversos contornos internos e o detector antigo podia escolher um quadrado errado, produzindo uma homografia incorreta.

---

# 19. GEOMETRIA POR PÁGINA

A geometria foi adaptada para receber a página atual.

Cada página utiliza o conjunto correspondente de IDs ArUco.

O fluxo é:

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

Cada página é corrigida individualmente.

Uma página torta não deve afetar geometricamente outra.

Essa arquitetura foi testada com uma ficha de duas páginas.

---

# 20. NORMALIZAÇÃO GEOMÉTRICA

A imagem escaneada é normalizada para:

```text
1191 × 1684
```

Fluxo:

```text
PDF

↓

renderização da página

↓

detecção dos ArUcos

↓

identificação dos IDs da página

↓

centros dos ArUcos

↓

homografia

↓

normalização

↓

1191 × 1684

↓

OMR
```

A normalização individual por página está funcionando.

---

# 21. MAPA OMR AUTOMÁTICO

O mapa OMR deixou de ser exclusivamente manual.

O arquivo:

```text
engine/gerador_ficha.py
```

gera automaticamente as coordenadas das caixas.

Cada coordenada possui:

```text
nome
pagina
x1
y1
x2
y2
```

O mapa também registra:

```text
imagem_largura
imagem_altura
quantidade_paginas
aruco
coordenadas
perguntas_abertas
campos_identificacao
```

Cada ficha possui seu mapa correspondente.

O usuário não precisa mapear manualmente cada caixa.

---

# 22. IMPORTANTE — RELAÇÃO ENTRE MAPA E GEOMETRIA

O mapa representa as coordenadas da ficha normalizada.

A geometria corrige a imagem escaneada para:

```text
1191 × 1684
```

Depois dessa correção, o mapa pode ser utilizado pelo OMR.

Não aplicar uma segunda transformação arbitrária ao mapa.

A separação correta é:

```text
Geometria
→ corrige a imagem

Mapa
→ descreve onde estão as caixas na imagem normalizada

OMR
→ lê as caixas
```

Essa relação foi validada visualmente.

---

# 23. OMR — ESTADO ATUAL

O arquivo principal é:

```text
engine/omr.py
```

O sistema:

* carrega o mapa;
* converte a imagem para tons de cinza;
* recorta cada caixa;
* remove a margem interna;
* conta pixels escuros;
* calcula percentual;
* classifica como `MARCADA` ou `VAZIA`.

---

# 24. CALIBRAÇÃO DO OMR

## Threshold de marcação

O threshold atualmente validado é:

```text
5.0%
```

Código equivalente:

```python
marcada = percentual >= 5.0
```

Esse valor não deve ser alterado sem nova calibração.

---

# 25. CALIBRAÇÃO DA MARGEM INTERNA

Foi identificado um problema de falso positivo causado pela borda preta da própria caixa OMR.

Foram realizados testes com ficha em branco:

```text
Margem 4 → 22 marcadas

Margem 5 → 2 marcadas

Margem 6 → 1 marcada

Margem 7 → 0 marcadas

Margem 8 → 0 marcadas

Margem 10 → 0 marcadas
```

Foi escolhido:

```text
MARGEM = 7
```

porque é o menor valor que eliminou todos os falsos positivos na ficha branca.

O valor atualmente aplicado no `engine/omr.py` é:

```python
margem=7
```

Parâmetros atuais:

```text
Margem interna: 7 pixels
Threshold de pixel escuro: 150
Limiar de marcação: 5%
```

Caso ocorram futuros falsos positivos, o primeiro parâmetro a investigar deve ser a margem interna da caixa, utilizando novamente uma ficha branca e uma ficha preenchida para recalibração.

---

# 26. CAIXA OMR — ESTADO VISUAL

A caixa OMR passou por ajustes visuais.

O estado atual deve ser:

```text
[ ]
```

Não deve existir um segundo quadrado visível dentro da caixa.

A área efetivamente analisada pelo OMR continua sendo definida logicamente pela margem interna.

Também foi aumentado o espaçamento vertical das opções para evitar caixas visualmente próximas demais.

Essas alterações não modificaram a lógica do mapa.

---

# 27. VISUALIZAÇÃO "ONDE DEVO MARCAR?"

A aplicação possui uma funcionalidade permanente chamada:

```text
Onde devo marcar?
```

Ela fica dentro do fluxo de **Visualizar ficha ativa**.

A funcionalidade mostra a ficha atual com a área analisada pelo OMR destacada em vermelho.

Objetivos:

* mostrar ao usuário onde deve marcar;
* validar visualmente o mapa;
* confirmar o alinhamento das caixas;
* facilitar diagnóstico;
* validar alterações de layout.

Importante:

```text
Vermelho aparece SOMENTE na visualização.

PDF original permanece normal.

Ficha impressa permanece normal.
```

O diagnóstico não altera o PDF da ficha.

`area_omr.py` permanece como funcionalidade do aplicativo.

O recurso deve sempre utilizar a ficha ativa atual, e não um exemplo genérico.

---

# 28. VALIDAÇÃO VISUAL DO MAPEAMENTO

A visualização `Onde devo marcar?` foi utilizada para validar o mapa atual.

Foram testados:

```text
Ficha de 1 página
→ áreas vermelhas alinhadas corretamente
```

```text
Ficha de 2 páginas
→ áreas vermelhas alinhadas corretamente
```

```text
Fonte maior
→ ficha passa para 2 páginas
→ áreas vermelhas continuam corretas
```

```text
Fonte reduzida
→ ficha volta para 1 página
→ áreas vermelhas continuam corretas
```

Conclusão atual:

**O mapeamento está visualmente correto e calibrado para a arquitetura atual do gerador, geometria e OMR.**

Isso não substitui o teste físico final com scanner.

---

# 29. VALIDAÇÃO FÍSICA ATUAL — FICHA VAZIA

Foi realizado um teste recente com uma ficha vazia de duas páginas.

Resultado:

```text
PÁGINA 1

Total: 70
Marcadas: 0
Vazias: 70
```

```text
PÁGINA 2

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

Esse teste confirmou o funcionamento do OMR em uma ficha vazia de duas páginas.

---

# 30. VALIDAÇÃO FÍSICA HISTÓRICA

Também foram realizados testes físicos anteriores com ficha preenchida.

Resultado:

```text
Total de caixas: 50
Marcadas: 12
Vazias: 38
```

As 12 marcações realizadas foram identificadas corretamente.

Resultado validado:

```text
12/12
100% das marcações reais detectadas
```

Esse continua sendo um dos principais resultados físicos do núcleo OMR.

Esse teste é histórico e não substitui o novo teste físico com a ficha atual.

---

# 31. TESTE REDUZIDO DO OMR

Também foi realizado um teste específico com uma ficha contendo 3 caixas OMR.

Ficha branca:

```text
Total: 3
Marcadas: 0
Vazias: 3
```

Ficha marcada:

```text
Total: 3
Marcadas: 1
Vazias: 2
```

A única marcação realizada foi reconhecida corretamente.

Esse teste serviu para validar o fluxo atual do gerador, mapa, geometria e OMR.

---

# 32. CONFIGURAÇÃO DE IMPRESSÃO

Para preservar as coordenadas:

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

Qualquer alteração de escala pode alterar a relação entre a ficha física e as coordenadas do mapa.

---

# 33. SCANNER — ESTADO ATUAL

Os testes físicos anteriores compararam:

```text
200 DPI
400 DPI
600 DPI
```

A configuração atual utilizada nos testes principais é:

```text
600 DPI
PDF
```

O próximo teste prioritário é realizar novamente o fluxo com o scanner real usando a ficha atual.

Fluxo:

```text
Ficha atual

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

Geometria

    ↓

Normalização

    ↓

OMR
```

Objetivo:

**confirmar definitivamente no fluxo físico completo que o mapeamento atual continua correto após o escaneamento.**

Não alterar `geometria.py` ou `omr.py` antes desse teste, salvo se o teste revelar um problema real.

---

# 34. INTERFACE ATUAL

A interface utiliza:

```text
CustomTkinter
```

Arquivos principais:

```text
ui/main_window.py
ui/viewer.py
ui/form_panel.py
ui/formulario_ficha.py
```

O `MainWindow` atualmente consegue:

* criar ficha;
* editar a ficha;
* gerar PDF;
* gerar mapa;
* definir ficha ativa;
* visualizar ficha ativa;
* navegar entre páginas;
* carregar um PDF;
* carregar o mapa da ficha;
* mostrar campos de identificação;
* mostrar perguntas abertas;
* exportar o PDF;
* abrir a visualização `Onde devo marcar?`;
* integrar a leitura OMR;
* gerar/vincular a planilha da pesquisa;
* salvar os resultados lidos na planilha;
* trabalhar com ficha em rascunho e produção;
* iniciar nova versão de ficha quando necessário.

---

# 35. VISUALIZAÇÃO DA FICHA ATIVA

O fluxo `Visualizar ficha ativa` deve continuar utilizando:

```text
ficha ativa

+

PDF da ficha ativa

+

mapa da ficha ativa
```

O botão `Onde devo marcar?` fica dentro desse fluxo.

O recurso não deve usar uma ficha de exemplo genérica.

Além da utilidade para o usuário, essa função serve como diagnóstico visual para verificar se o mapa da ficha atual está correto.

---

# 36. PROCESSAMENTO MULTIPÁGINA

O núcleo de testes possui suporte para processar páginas individualmente.

Regra:

```text
Página 1
→ geometria independente
→ OMR

Página 2
→ geometria independente
→ OMR

Página 3
→ geometria independente
→ OMR
```

Uma página torta não deve afetar outra.

O gerador também cria páginas adicionais automaticamente quando necessário.

A existência de duas páginas não é um bug do produto.

O teste de ficha vazia de duas páginas funcionou corretamente.

A integração completa desse fluxo no leitor final ainda precisa ser confirmada no novo teste físico prioritário com scanner.

---

# 37. LEITOR E DADOS DE IDENTIFICAÇÃO

O `FormPanel` possui elementos herdados da versão 1.0, mas o objetivo do 2.0 é que os campos exibidos no leitor sejam determinados pela ficha ativa.

Já existe estrutura para:

```text
campos_identificacao
perguntas_abertas
```

O resultado final deve receber dinamicamente os campos da ficha ativa.

Não utilizar como padrão obrigatório os campos fixos antigos:

```text
Data
Número do Selo
Comunidade
Nome do Morador
Entrevistador
```

Esses campos são apenas exemplos possíveis de configuração da ficha.

---

# 38. FLUXO FINAL DA LEITURA

O objetivo é produzir um registro único contendo:

```text
Identificação da ficha

+

Campos do cabeçalho

+

Respostas fechadas

+

Respostas abertas
```

Exemplo conceitual:

```text
Campo: Nome

Valor: João da Silva

Campo: Comunidade

Valor: Comunidade X

1.1_sim

MARCADA

1.2_nao

VAZIA

2.3

Resposta aberta:

"muita coisa"
```

Esse registro deve ser validado antes de ser salvo ou enviado para um destino externo.

---

# 39. SAÍDA TABULAR E PLANILHA

A primeira versão funcional da saída local dos resultados foi concluída.

A planilha passou a ser derivada diretamente da estrutura criada pelo usuário no editor de fichas.

O formato principal passou a ser:

```text
.xlsx
```

A estrutura da planilha não é um modelo fixo.

A ficha é a fonte de verdade.

---

# 40. ESTRUTURA DA PLANILHA

A ordem das colunas deve ser exatamente a ordem dos elementos de dados da ficha:

```text
Campos do cabeçalho
        ↓
Perguntas
```

As seções são exclusivamente visuais e não geram colunas.

Exemplo de ficha:

```text
Cabeçalho:

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

A planilha correspondente deve ter:

```text
A1 = Data
B1 = Número do Selo
C1 = Comunidade
D1 = Nome do Morador
E1 = Entrevistador
F1 = 1.1 A obra foi concluída?
G1 = 1.2 A obra ficou boa?
H1 = 1.3 Houve algum problema?
I1 = 2.1 Como avalia a qualidade?
J1 = 2.2 O serviço atendeu à expectativa?
```

As seções:

```text
Seção 1 - Obras
Seção 2 - Qualidade
```

não aparecem como colunas.

Não criar colunas artificiais como `Ficha ID` ou `Pesquisa`, salvo quando esses campos existirem realmente na ficha.

---

# 41. LINHA 1 E REGISTROS

A primeira linha da planilha representa a estrutura fixa da pesquisa.

```text
Linha 1 = nomes das colunas
Linha 2 = primeira ficha lida
Linha 3 = segunda ficha lida
Linha 4 = terceira ficha lida
...
```

Exemplo:

```text
A1 = Data
B1 = Número do Selo
C1 = Comunidade
D1 = Nome do Morador
E1 = Entrevistador
F1 = 1.1 A obra foi concluída?
```

Primeiro registro:

```text
A2 = 23/08/2026
B2 = 12345
C2 = Comunidade X
D2 = João
E2 = Maria
F2 = Sim
```

Segundo registro:

```text
A3 = 24/08/2026
B3 = 12346
C3 = Comunidade Y
D3 = Pedro
E3 = Ana
F3 = Não
```

Cada ficha processada deve acrescentar uma nova linha.

O sistema não deve recriar ou duplicar o cabeçalho durante a leitura.

---

# 42. FORMATO E COMPATIBILIDADE DA PLANILHA

A planilha `.xlsx` deve possuir:

```text
✅ primeira linha como cabeçalho
✅ primeira linha congelada
✅ filtro automático
✅ uma coluna por campo/pergunta
✅ uma linha por ficha processada
✅ largura das colunas ajustada
✅ datas tratadas como datas Excel quando aplicável
```

Foi identificado um problema de compatibilidade XML que fazia o Excel remover partes de `styles.xml` e substituir conteúdo de `sheet1.xml`.

O problema estava relacionado à ordem de elementos no XML OOXML.

A correção foi aplicada em:

```text
engine/sheets.py
```

Depois da correção, o arquivo `.xlsx` foi validado e reaberto corretamente.

---

# 43. PRODUÇÃO DA FICHA E PLANILHA

O fluxo desejado é:

```text
Criar ficha
    ↓
Gerar ficha
    ↓
Visualizar ficha
    ↓
Confirmar ficha para produção
    ↓
Gerar planilha
    ↓
Usuário escolhe onde salvar o .xlsx
    ↓
Ficha fica vinculada à planilha
```

O SDIP deve guardar o caminho da planilha vinculada àquela ficha/versão.

Depois:

```text
Ficha escaneada
    ↓
Leitura OMR
    ↓
Campos digitados
    ↓
Registro final
    ↓
Adicionar nova linha à planilha vinculada
```

O sistema não deve pedir novamente o destino em cada leitura.

---

# 44. RASCUNHO E PRODUÇÃO

A ficha deve possuir os estados conceituais:

```text
RASCUNHO
PRODUÇÃO
```

## RASCUNHO

Enquanto está em rascunho, o usuário pode alterar livremente:

* nome;
* título;
* cabeçalho;
* seções;
* perguntas;
* opções;
* perguntas abertas;
* ordem dos elementos.

Pode regenerar a ficha quantas vezes forem necessárias.

## PRODUÇÃO

Depois de:

```text
Gerar ficha
    ↓
Visualizar
    ↓
Confirmar
    ↓
Gerar planilha
```

a ficha entra em produção.

Sua estrutura passa a ser o schema da pesquisa.

---

# 45. VERSIONAMENTO

Uma ficha que já está em produção não deve ter sua estrutura alterada silenciosamente.

Alterações estruturais incluem:

```text
Adicionar pergunta
Excluir pergunta
Renomear pergunta
Alterar ordem das perguntas
Adicionar campo de cabeçalho
Excluir campo de cabeçalho
Renomear campo de cabeçalho
Alterar ordem do cabeçalho
Transformar pergunta fechada em aberta
Transformar pergunta aberta em fechada
Alterar estrutura de opções
```

Essas alterações podem mudar a estrutura das colunas e comprometer a compatibilidade com dados já coletados.

Quando o usuário precisar modificar uma ficha em produção, o comportamento esperado é:

```text
Ficha em produção
        ↓
Editar
        ↓
Criar nova versão
```

A nova versão deve:

```text
manter o mesmo pesquisa_id
incrementar a versão
registrar a versão anterior
começar novamente como RASCUNHO
não herdar a planilha da versão anterior
```

Exemplo:

```text
Pesquisa
├── Ficha v1
│   └── Planilha v1
│
├── Ficha v2
│   └── Planilha v2
│
└── Ficha v3
    └── Planilha v3
```

Cada versão possui sua própria estrutura, PDF, mapa OMR e planilha.

---

# 46. FONTE ÚNICA DE VERDADE

A estrutura da planilha deve ser derivada da estrutura da ficha.

Não criar uma segunda estrutura manual específica para a planilha.

Conceitualmente:

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
Cabeçalho da planilha
```

Portanto:

```text
Ficha
    ↓
Fonte de verdade
```

A planilha é uma representação tabular dessa ficha.

---

# 47. LEITURA E CONSTRUÇÃO DA LINHA

Depois da leitura OMR e da entrada manual dos campos, o SDIP deve montar um único registro.

Exemplo:

```text
Campos do cabeçalho:

Data = 23/08/2026
Número do Selo = 12345
Comunidade = X
Nome = João
Entrevistador = Maria

OMR:

1.1 = Sim
1.2 = Sim
1.3 = Não

Pergunta aberta:

2.3 = Precisa melhorar
```

O sistema transforma isso em uma única linha:

```text
23/08/2026
12345
X
João
Maria
Sim
Sim
Não
Precisa melhorar
```

Essa linha é adicionada à planilha existente.

---

# 48. "OUTROS" E "QUAL?"

Existe um caso de processo ainda não definido:

```text
☐ Outros
   Qual? __________________
```

A dúvida é se a anotação manuscrita do campo `Qual?` realmente deve ser transcrita para a planilha.

Esse comportamento será confirmado com os usuários em reunião.

Até essa confirmação:

```text
não alterar a arquitetura;
não criar coluna adicional automaticamente;
não assumir que "Qual?" precisa ser armazenado.
```

A implementação deve seguir o processo real utilizado pelos usuários.

Perguntas abertas independentes continuam gerando coluna normalmente.

---

# 49. ARQUIVOS ENVOLVIDOS NA SAÍDA

Os arquivos atualmente envolvidos são:

```text
engine/sheets.py
engine/fichas_manager.py
engine/leitor.py
ui/main_window.py
```

## engine/sheets.py

Responsável por:

```text
criar .xlsx
validar cabeçalho
adicionar novas linhas
preservar estrutura da planilha
formatar a planilha
```

## engine/fichas_manager.py

Responsável por informações como:

```text
ficha ativa
status
versão
pesquisa_id
vínculo com planilha
```

## engine/leitor.py

Responsável pela integração:

```text
PDF
ArUco
geometria
normalização
OMR
resultado da leitura
```

## ui/main_window.py

Responsável pela integração com a interface:

```text
ler ficha
revisar
gerar planilha
vincular planilha
salvar resultado
criar nova versão
```

---

# 50. COMPONENTES PROTEGIDOS

Os seguintes componentes já foram amplamente validados e não devem ser alterados sem evidência técnica:

```text
engine/omr.py
engine/geometria.py
engine/gerador_ficha.py
```

Também não alterar desnecessariamente:

```text
ui/form_panel.py
ui/viewer.py
ui/formulario_ficha.py
area_omr.py
```

Qualquer mudança nesses componentes deve ser baseada em teste que demonstre um problema real.

---

# 51. VALIDAÇÕES DA SAÍDA TABULAR

Foram realizados testes técnicos com a nova camada de planilha.

Resultados:

```text
✅ estrutura da planilha derivada da ficha
✅ campos do cabeçalho transformados em colunas
✅ perguntas transformadas em colunas
✅ seções não transformadas em colunas
✅ ordem preservada
✅ uma nova linha por registro
✅ primeira linha congelada
✅ filtro automático
✅ largura ajustada
✅ datas tratadas como datas Excel
✅ arquivo .xlsx válido
✅ planilha reaberta sem erro
✅ compatibilidade Excel corrigida
✅ vínculo ficha → planilha
✅ estrutura inicial de RASCUNHO / PRODUÇÃO / versão
```

Foi também realizado teste técnico do leitor com ficha branca:

```text
50 caixas
0 marcadas
0 erros
```

Esse teste técnico não substitui o teste físico real.

---

# 52. TESTE FÍSICO FINAL — PRÓXIMA ETAPA

O próximo teste obrigatório é:

```text
Ficha atual
    ↓
Impressão
    ↓
Preenchimento manual
    ↓
Scanner real
    ↓
600 DPI
    ↓
PDF
    ↓
Digitalizar
    ↓
Ler ficha (OMR)
```

O objetivo é comparar:

```text
Marcações feitas manualmente
        VS.
Marcações identificadas pelo SDIP
```

Critério esperado:

```text
100% das marcações reais detectadas
0 falsos positivos
```

Também devem ser testadas:

```text
marcações na parte superior
marcações no meio
marcações na parte inferior
coluna esquerda
coluna direita
página 1
página 2
resposta única
resposta múltipla
```

Não recalibrar `omr.py` ou `geometria.py` antes de observar o resultado desse teste.

---

# 53. TESTE DA PLANILHA NO FLUXO REAL

Depois de o OMR passar no scanner real:

```text
PDF escaneado
    ↓
Ler ficha
    ↓
respostas OMR
    +
campos digitados
    +
respostas abertas
    ↓
Salvar resultado
    ↓
XLSX vinculado
```

Conferir:

```text
✅ campos do cabeçalho nas colunas corretas
✅ respostas OMR nas colunas corretas
✅ abertas nas colunas corretas
✅ uma única nova linha
✅ nenhuma alteração na linha 1
✅ Excel abre sem reparação
```

---

# 54. TESTES DE BUG E ROBUSTEZ

Depois da validação física principal, iniciar testes negativos.

Casos a testar:

```text
PDF sem ArUco
PDF incorreto
página faltando
página duplicada
página invertida
página fora de ordem
imagem de baixa qualidade
marca fraca
marca forte
marca parcial
marca fora da caixa
pergunta sem resposta
múltiplas marcações em resposta única
múltiplas respostas em questão múltipla
campo de identificação vazio
resposta aberta vazia
planilha inexistente
planilha movida
planilha alterada manualmente
ficha sem vínculo com planilha
ficha em produção tentando ser alterada
```

O objetivo é que o sistema apresente erros compreensíveis e não grave silenciosamente dados incorretos.

---

# 55. UX/UI — PRÓXIMA FASE APÓS OS TESTES

Depois de validar o núcleo técnico, iniciar melhoria da experiência do usuário.

Sequência recomendada:

```text
Criar/Editar ficha
        ↓
Visualizar ficha
        ↓
Confirmar produção
        ↓
Gerar planilha
        ↓
Digitalizar
        ↓
Ler OMR
        ↓
Revisar
        ↓
Salvar
```

Prioridades de UX/UI:

```text
clareza dos botões
hierarquia visual
mensagens de sucesso
mensagens de erro
indicação da ficha ativa
indicação da planilha vinculada
feedback durante processamento
feedback após salvar
clareza entre RASCUNHO e PRODUÇÃO
clareza durante criação de nova versão
```

As melhorias visuais devem ser feitas depois da validação física do fluxo principal.

---

# 56. GOOGLE FORMS

A integração com Google Forms ainda não deve ser implementada.

A ordem correta continua sendo:

```text
OMR funcionando
    ↓
resultado estruturado
    ↓
validação
    ↓
identificação/data/abertas
    ↓
revisão
    ↓
salvamento local em XLSX
    ↓
Google Forms
```

Não acoplar Google Forms diretamente ao OMR.

---

# 57. MÚLTIPLAS FICHAS

Depois do teste físico completo e da estabilização do fluxo de uma ficha, avaliar processamento em lote:

```text
PDF 1
PDF 2
PDF 3
PDF 4
...
```

Cada resultado deve ser vinculado à ficha correta e acrescentado à planilha correspondente.

Nunca utilizar o mapa de uma ficha para outra ficha.

---

# 58. LIMPEZA DO PROJETO

A limpeza de scripts históricos continua posterior à estabilização.

Avaliar:

```text
teste_geometria.py
teste_aruco_scan.py
testes históricos
scripts duplicados
arquivos temporários
diagnósticos
```

Não remover arquivos apenas porque parecem antigos.

Antes de apagar qualquer teste:

```text
avaliar utilidade
identificar duplicação
verificar se é histórico
verificar se pode servir como regressão
```

`area_omr.py` deve permanecer enquanto continuar sendo utilizado pela funcionalidade:

```text
Onde devo marcar?
```

---

# 59. SEGURANÇA

Antes da distribuição:

```text
não incluir .venv
não incluir credenciais
não incluir tokens
não incluir PDFs pessoais
não incluir imagens de teste pessoais
não incluir resultados temporários
não incluir configurações com dados sensíveis
```

A planilha de uma pesquisa deve ser tratada como dado produzido pelo usuário.

O vínculo entre ficha e planilha deve permanecer específico daquela pesquisa/versão.

---

# 60. EMPACOTAMENTO

Quando o fluxo estiver concluído:

```text
Criar ficha
    ↓
Digitalizar
    ↓
Ler
    ↓
Validar
    ↓
Revisar
    ↓
Salvar
    ↓
Enviar para destino
```

o projeto poderá ser empacotado como aplicativo Windows:

```text
SDIP.exe
```

Objetivo:

```text
duplo clique
↓
abrir aplicação
```

O usuário final não deverá precisar executar Python, PowerShell ou `.venv`.

Provavelmente será utilizado PyInstaller, mas somente próximo da versão estável.

---

# 61. DOCUMENTAÇÃO

## README

Deve explicar:

* objetivo;
* arquitetura;
* geração da ficha;
* layout;
* paginação;
* seções;
* perguntas abertas;
* cabeçalho configurável;
* ficha ativa;
* ArUco;
* geometria;
* OMR;
* calibração;
* visualização `Onde devo marcar?`;
* geração da planilha;
* estrutura das colunas;
* fluxo RASCUNHO → PRODUÇÃO;
* versionamento;
* instalação;
* testes;
* estado do projeto;
* fluxo de saída.

## Manual do usuário

Deve explicar:

* criar ficha;
* definir campos do cabeçalho;
* gerar;
* visualizar;
* consultar `Onde devo marcar?`;
* colocar ficha em produção;
* gerar planilha;
* imprimir;
* preencher;
* escanear;
* processar;
* revisar;
* salvar;
* trabalhar com novas versões;
* configurar destino;
* enviar para o destino configurado.

## Documento técnico

Deve registrar:

* parâmetros;
* calibrações;
* diagnósticos;
* decisões técnicas;
* problemas encontrados;
* soluções adotadas;
* resultados dos testes físicos;
* estrutura da saída tabular;
* versionamento de fichas.

---

# 62. ENCERRAMENTO DE SESSÃO

Quando o trabalho do dia terminar:

1. registrar o que foi feito;
2. atualizar este arquivo;
3. registrar arquivos alterados;
4. registrar testes executados;
5. registrar resultados;
6. registrar o próximo passo;
7. verificar `git status`;
8. fazer commit quando apropriado.

Se o usuário esquecer o encerramento, lembrar de atualizar este arquivo antes de finalizar a sessão.

---

# 63. REGRA MAIS IMPORTANTE

O SDIP 2.0 possui trabalho real, testes físicos e parâmetros calibrados.

Não tratar o projeto como tutorial ou exemplo genérico.

Continuar exatamente do estado existente.

Antes de alterar algo importante:

```text
O que está errado?

        ↓

Por que está errado?

        ↓

Qual arquivo é responsável?

        ↓

O componente já foi validado?

        ↓

O que será alterado?

        ↓

Como será testado?

        ↓

Qual resultado esperamos?
```

Não alterar componentes validados sem evidência.

---

# 64. ESTADO ATUAL — 27/08/2026

## Validado

```text
✅ Gerador automático
✅ Layout em duas colunas
✅ Uma ou várias páginas
✅ Ficha de 1 página
✅ Ficha de 2 páginas
✅ Paginação dinâmica
✅ ArUco real
✅ ArUcoDetector
✅ IDs ArUco por página
✅ Geometria
✅ Homografia
✅ Normalização 1191 × 1684
✅ Mapa automático
✅ Mapa associado à ficha
✅ OMR
✅ Margem 7
✅ Threshold 5%
✅ Pixel escuro 150
✅ Caixa OMR visual limpa
✅ Espaçamento vertical ajustado
✅ Ficha branca de 2 páginas: 140 caixas / 0 falsos positivos
✅ Teste físico histórico: 12/12 marcações detectadas
✅ Mapeamento visual de 1 página
✅ Mapeamento visual de 2 páginas
✅ Mapeamento após alteração de fonte
✅ Seções
✅ Resposta única
✅ Resposta múltipla
✅ Perguntas abertas — estrutura inicial
✅ Cabeçalho configurável
✅ Cabeçalho impresso
✅ Edição de ficha em rascunho
✅ Logo
✅ Ficha ativa
✅ Visualização da ficha ativa
✅ Onde devo marcar?
✅ Área OMR vermelha apenas na visualização
✅ PDF original sem marcações vermelhas
✅ Exportação do PDF
✅ Leitor integrado ao fluxo
✅ Estrutura de planilha derivada da ficha
✅ Campos do cabeçalho como colunas
✅ Perguntas como colunas
✅ Seções fora da estrutura tabular
✅ Uma ficha por linha
✅ XLSX
✅ Linha 1 congelada
✅ Filtro automático
✅ Largura de colunas ajustada
✅ Data tratada como data Excel
✅ Compatibilidade com Excel corrigida
✅ Vínculo ficha → planilha
✅ Conceito RASCUNHO → PRODUÇÃO
✅ Estrutura inicial de versionamento
✅ Nova versão sem herdar a planilha anterior
```

## Não validado ainda no fluxo físico atual

```text
[ ] Ficha atual impressa e preenchida
[ ] Scanner real
[ ] 600 DPI no fluxo completo
[ ] 100% das marcações reais reconhecidas
[ ] 0 falsos positivos no fluxo final
[ ] respostas OMR convertidas corretamente por pergunta
[ ] campos digitados chegando nas colunas corretas
[ ] respostas abertas chegando nas colunas corretas
[ ] uma única nova linha criada no XLSX
[ ] Excel abrindo a planilha final sem reparo
```

## Ainda pendente

```text
[ ] Confirmar comportamento de "Outros + Qual?"
[ ] Bateria de testes negativos
[ ] Testes de robustez
[ ] Teste de múltiplas fichas
[ ] Refinamento UX/UI
[ ] Revisão final do fluxo de produção
[ ] Integração com Google Forms
[ ] Avaliar Google Sheets / outros destinos
[ ] Limpeza dos scripts históricos
[ ] Revisão de arquivos temporários
[ ] Documentação final
[ ] Empacotamento em EXE
```

---

# 65. PONTO EXATO DE RETOMADA

O núcleo do SDIP 2.0 continua funcional e calibrado.

A camada de saída para planilha foi implementada e passou a utilizar `.xlsx`, com estrutura derivada diretamente da ficha:

```text
campos do cabeçalho
        +
perguntas da ficha
        ↓
linha 1 da planilha
```

As seções são exclusivamente visuais.

Cada ficha lida acrescenta uma nova linha na planilha vinculada àquela versão da pesquisa.

A planilha é criada uma vez quando a ficha é colocada em produção e o caminho é armazenado para uso posterior.

O Excel apresentou anteriormente erro de XML no arquivo `.xlsx`; a causa foi identificada e corrigida na geração de `styles.xml` e `sheet1.xml`. A nova estrutura foi validada.

O conceito de:

```text
RASCUNHO
    ↓
PRODUÇÃO
    ↓
NOVA VERSÃO
```

faz parte da arquitetura atual.

O comportamento específico de `Outros + Qual?` ainda aguarda decisão dos usuários.

O próximo passo é **teste físico completo**, não alteração do núcleo.

Fluxo imediato:

```text
1. imprimir a ficha atual
2. preencher manualmente
3. escanear no scanner real
4. utilizar 600 DPI
5. processar no SDIP
6. conferir todas as marcações
7. conferir as respostas por pergunta
8. conferir os campos digitados
9. salvar o resultado
10. abrir o XLSX no Excel
11. confirmar que uma única nova linha foi criada
```

Depois dessa validação:

```text
teste de erros
        ↓
teste de robustez
        ↓
UX/UI
        ↓
Google Forms
        ↓
múltiplas fichas
        ↓
EXE
        ↓
limpeza e documentação final
```

Não recalibrar `engine/omr.py` ou `engine/geometria.py` sem evidência técnica obtida no teste físico.

Não modificar componentes já validados apenas para antecipar melhorias.

**Estado de retomada:** o projeto está na fase de **validação física final do OMR e da integração OMR → dados digitados → XLSX**.
