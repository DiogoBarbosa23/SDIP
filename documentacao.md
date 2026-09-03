# Documentação Técnica — SDIP

## Sistema de Digitalização Inteligente de Pesquisas

Este documento registra a arquitetura, decisões técnicas, parâmetros validados, regras de funcionamento, integrações e resultados de testes do **SDIP — Sistema de Digitalização Inteligente de Pesquisas**.

O objetivo deste arquivo é complementar o `README.md`.

Enquanto o `README.md` apresenta o projeto, suas funcionalidades e seu fluxo geral, este documento concentra informações importantes para manutenção, testes, estabilização e evolução técnica do sistema.

---

# 1. Visão geral

O SDIP é uma aplicação desktop desenvolvida em Python para automatizar o processo de:

```text
criação da pesquisa
        ↓
geração da ficha
        ↓
impressão
        ↓
preenchimento manual
        ↓
digitalização
        ↓
processamento do PDF
        ↓
leitura OMR
        ↓
conferência
        ↓
estruturação dos dados
        ↓
salvamento
        ↓
arquivamento do PDF processado
```

A proposta é permitir que pesquisas originalmente realizadas em papel continuem utilizando formulários físicos, mas tenham sua etapa posterior de digitalização e transcrição amplamente automatizada.

O sistema não depende de um formulário fixo.

Cada pesquisa pode possuir sua própria estrutura, campos, perguntas, seções, mapa OMR e destinos de resultado.

---

# 2. Princípio central

O usuário do SDIP não deve precisar conhecer detalhes internos como:

```text
coordenadas
ArUco
homografia
mapa OMR
thresholds
normalização geométrica
estrutura interna da planilha
```

Esses elementos são controlados automaticamente pela aplicação.

A estrutura criada pelo usuário funciona como a principal fonte de verdade do sistema.

```text
Estrutura da pesquisa
        │
        ├── PDF
        ├── mapa OMR
        ├── formulário de preenchimento
        ├── planilha XLSX
        ├── Google Sheets
        └── regra de nomeação dos PDFs
```

A arquitetura atual não utiliza mapas OMR globais definidos manualmente.

Cada ficha possui seu próprio mapa.

---

# 3. Tecnologias

Principais tecnologias utilizadas:

* Python;
* CustomTkinter;
* Tkinter;
* OpenCV;
* OpenCV ArUco;
* NumPy;
* Pillow;
* PyMuPDF;
* processamento de imagens;
* homografia;
* OMR;
* XLSX;
* Google Sheets;
* Google Apps Script;
* Web Apps;
* JSON;
* Git;
* GitHub.

Ambiente principal de desenvolvimento:

```text
Windows
Python 3.13.x
.venv
```

A integração atual com Google Sheets utiliza apenas recursos gratuitos do Google Apps Script e bibliotecas padrão do Python.

Não são necessários:

```text
gspread
google-auth
Service Account
credentials.json
Google Cloud com faturamento
```

---

# 4. Estrutura principal do projeto

```text
SDIP/
│
├── engine/
│   ├── gerador_ficha.py
│   ├── geometria.py
│   ├── omr.py
│   ├── leitor.py
│   ├── pdf_reader.py
│   ├── fichas_manager.py
│   ├── sheets.py
│   ├── google_sheets_webapp.py
│   └── pacote_pesquisa.py
│
├── ui/
│   ├── main_window.py
│   ├── formulario_ficha.py
│   ├── form_panel.py
│   └── viewer.py
│
├── docs/
│   ├── MANUAL_USUARIO_SDIP.pdf
│   └── manual_rapido_sdip.png
│
├── area_omr.py
├── app.py
├── MANUAL_USUARIO.md
├── requirements.txt
├── README.md
├── documentacao.md
└── CONTINUIDADE.md
```

A antiga pasta:

```text
config/
```

não faz mais parte da arquitetura atual.

Ela existia em versões anteriores para armazenar mapas OMR globais ou artefatos de testes antigos.

Depois da validação da arquitetura atual, esses arquivos foram removidos.

---

# 5. Separação de responsabilidades

A arquitetura segue aproximadamente este fluxo:

```text
Gerador
    ↓
Ficha física
    ↓
Scanner
    ↓
PDF
    ↓
Leitor
    ↓
Geometria
    ↓
Imagem normalizada
    ↓
Mapa OMR da ficha
    ↓
OMR
    ↓
Resultado estruturado
    ↓
Validação
    ↓
Persistência
```

Cada camada deve continuar separada sempre que possível.

O leitor não deve assumir responsabilidades relacionadas à persistência em XLSX ou Google Sheets.

O OMR não deve conhecer regras de interface.

A geração da ficha não deve depender de configurações locais de uma máquina específica.

---

# 6. Gerador de ficha

Arquivo principal:

```text
engine/gerador_ficha.py
```

Responsabilidades:

* receber a estrutura definida pelo usuário;
* criar cabeçalho;
* aplicar logo;
* criar campos de identificação;
* criar seções;
* criar perguntas;
* criar opções;
* criar perguntas abertas;
* distribuir conteúdo;
* criar páginas;
* criar caixas OMR;
* inserir marcadores ArUco;
* registrar coordenadas;
* gerar mapa OMR;
* gerar imagens;
* permitir criação posterior do PDF.

O usuário não informa coordenadas manualmente.

Essa característica é fundamental para a arquitetura atual.

---

# 7. Layout automático

A ficha utiliza duas colunas independentes.

```text
┌──────────────────────┬──────────────────────┐
│ Coluna esquerda      │ Coluna direita       │
│                      │                      │
│ Perguntas            │ Perguntas            │
│                      │                      │
│                      │                      │
└──────────────────────┴──────────────────────┘
```

Regra:

```text
preencher coluna esquerda
        ↓
não existe espaço suficiente
        ↓
continuar no topo da coluna direita
        ↓
não existe espaço nas duas colunas
        ↓
criar nova página
```

Uma pergunta não deve ser dividida entre:

* colunas;
* páginas.

O sistema já foi validado com fichas de uma e duas páginas.

Alterações no tamanho da fonte podem modificar automaticamente a quantidade de páginas.

---

# 8. Seções

As seções são elementos estruturais e visuais.

Exemplo:

```text
1. Infraestrutura

1.1 A obra foi concluída?
1.2 A qualidade foi satisfatória?

2. Atendimento

2.1 O atendimento foi adequado?
2.2 Houve algum problema?
```

Seções:

* organizam perguntas;
* participam da numeração;
* não recebem caixas OMR;
* não produzem colunas próprias na planilha.

---

# 9. Perguntas fechadas

Perguntas fechadas podem possuir:

```text
resposta única
```

ou:

```text
resposta múltipla
```

Cada opção recebe automaticamente uma caixa OMR.

Exemplos de identificadores internos:

```text
1.1_sim
1.1_nao
2.3_bom
2.3_regular
2.3_ruim
```

Esses identificadores relacionam a estrutura da pergunta às coordenadas armazenadas no mapa OMR correspondente à ficha.

---

# 10. Perguntas abertas

Uma pergunta pode ser configurada como aberta.

Nesse caso:

* opções fechadas não são exibidas;
* nenhuma caixa OMR é criada;
* uma área para escrita manual é criada na ficha;
* a pergunta fica registrada na estrutura;
* o operador recebe um campo correspondente durante a digitalização;
* sua resposta passa a integrar o registro final.

Exemplo:

```text
2.3 Qual serviço precisa de maior atenção?

________________________________________
```

Perguntas abertas geram colunas normalmente na planilha.

---

# 11. Cabeçalho configurável

O SDIP não utiliza um cabeçalho rígido.

Cada pesquisa pode definir seus próprios campos.

Exemplos:

```text
Data
Código
Nome
CPF
Matrícula
Comunidade
Entrevistador
Bairro
Setor
Protocolo
Número do imóvel
```

Os campos configurados participam de:

```text
Ficha impressa
        +
Painel de preenchimento
        +
Registro
        +
Planilha
```

Também podem participar da geração automática do nome do PDF processado.

---

# 12. Tipos de campos

Campos de identificação podem possuir tipos específicos.

Um dos tipos atualmente implementados é:

```text
Data
```

Campos desse tipo possuem regras específicas de preenchimento e validação.

---

# 13. Validação de data

Formato utilizado:

```text
DD/MM/AAAA
```

Exemplo:

```text
02/09/2026
```

A validação verifica:

* dia;
* mês;
* ano;
* quatro dígitos no ano;
* separadores;
* existência real da data.

Exemplos inválidos:

```text
2/9/26
02/09/26
2026-09-02
31/02/2026
32/01/2026
15/13/2026
```

Uma data preenchida incorretamente bloqueia o salvamento.

Um campo de data vazio continua permitido, sujeito à confirmação dos campos manuais vazios.

---

# 14. Logo

A ficha pode possuir logo personalizada.

A imagem é redimensionada proporcionalmente para ocupar a área reservada.

A logo não deve:

* invadir os ArUcos;
* alterar a geometria da página;
* modificar as coordenadas OMR.

---

# 15. ArUco

Cada página utiliza quatro marcadores ArUco.

Dicionário:

```text
DICT_4X4_50
```

OpenCV validado:

```text
4.12.0
```

API utilizada:

```python
cv2.aruco.ArucoDetector
```

A detecção utiliza os IDs reais dos marcadores.

---

# 16. Função dos ArUcos

Os marcadores permitem localizar geometricamente a página digitalizada.

Fluxo:

```text
Página escaneada
        ↓
Detecção dos ArUcos
        ↓
Localização dos marcadores
        ↓
Determinação da geometria
        ↓
Homografia
        ↓
Imagem normalizada
```

Isso reduz problemas provocados por:

* deslocamento;
* inclinação;
* perspectiva;
* pequenas diferenças de posicionamento durante o scanner.

---

# 17. Geometria por página

Arquivo:

```text
engine/geometria.py
```

Cada página é processada individualmente.

```text
Página 1
    ↓
ArUcos da página
    ↓
Homografia
    ↓
Normalização

Página 2
    ↓
ArUcos da página
    ↓
Homografia
    ↓
Normalização
```

Uma página torta não deve alterar o processamento geométrico de outra.

---

# 18. Normalização geométrica

Depois da homografia, a página é normalizada para:

```text
1191 × 1684 pixels
```

Fluxo:

```text
PDF
 ↓
renderização
 ↓
ArUcos
 ↓
homografia
 ↓
normalização
 ↓
1191 × 1684
 ↓
OMR
```

O mapa OMR utiliza coordenadas da imagem normalizada.

---

# 19. Arquitetura atual do mapa OMR

O mapa é gerado automaticamente junto com cada ficha.

Cada ficha possui seu próprio arquivo:

```text
fichas/
└── <ficha_id>/
    └── mapa_omr.json
```

Cada caixa possui informações como:

```text
nome
pagina
x1
y1
x2
y2
```

O mapa também mantém informações relacionadas a:

* largura da imagem;
* altura da imagem;
* quantidade de páginas;
* ArUcos;
* coordenadas;
* perguntas abertas;
* campos de identificação.

A arquitetura atual segue:

```text
Pesquisa
    ↓
Ficha
    ↓
mapa_omr.json da própria ficha
    ↓
LeitorFicha
    ↓
OMRReader(mapa_path=...)
```

Não existe mais fallback para um mapa global.

---

# 20. Remoção da arquitetura antiga de mapas

Nas primeiras versões existiam:

```text
config/mapa_caixas.json
config/mapa_caixas_gerado.json
```

Esses arquivos não pertencem mais ao fluxo atual.

## `config/mapa_caixas.json`

Era um mapa global/manual de uma arquitetura anterior.

O construtor de `OMRReader` possuía:

```python
def __init__(
    self,
    mapa_path="config/mapa_caixas.json",
    margem=7
):
```

Esse fallback foi removido.

A assinatura atual é:

```python
def __init__(
    self,
    mapa_path,
    margem=7
):
```

Assim, o código que utiliza `OMRReader` precisa informar explicitamente qual mapa pertence à ficha sendo processada.

Foram verificadas as chamadas existentes em:

```text
engine/leitor.py
teste_omr_2.py
teste_omr_margem7.py
```

Todas fornecem `mapa_path`.

## `config/mapa_caixas_gerado.json`

Era utilizado como saída por um teste antigo.

O teste:

```text
teste_gerador_ficha.py
```

foi ajustado para utilizar:

```text
temp/mapa_caixas_gerado.json
```

O arquivo passou a ser tratado corretamente como artefato temporário de teste.

---

# 21. Validação da remoção do mapa legado

A remoção não foi realizada apenas por inspeção visual.

Foram executadas verificações antes e depois.

## Verificação de chamadas

Todas as chamadas de:

```python
OMRReader(...)
```

foram verificadas.

Resultado:

```text
todas passam mapa_path explicitamente
```

## Busca por referências

Foram procuradas referências a:

```text
config/mapa_caixas.json
config/mapa_caixas_gerado.json
config/mapa
```

Nenhuma dependência funcional permaneceu.

As únicas referências restantes a `mapa_caixas_gerado.json` pertencem a testes que utilizam `temp/`.

## Teste do gerador

Resultado:

```text
TESTE DO GERADOR DE FICHA + MAPA OMR

Quantidade de perguntas: 12

Páginas geradas:
- temp\ficha_teste_layout_1.png

Mapa OMR gerado:
- temp/mapa_caixas_gerado.json

Quantidade de páginas: 1
Caixas OMR registradas: 50

TESTE CONCLUÍDO
```

## Teste funcional do aplicativo

Depois da exclusão dos mapas antigos foram testados:

```text
criação/abertura de pesquisa
Onde devo marcar?
leitura OMR
salvamento
planilha local
arquivamento do PDF
```

Resultado:

```text
OK
```

A antiga pasta `config/` ficou sem arquivos e foi removida.

---

# 22. Regra crítica: PDF e mapa

Nunca utilizar:

```text
PDF da ficha A
        +
mapa da ficha B
```

O mapa pertence à estrutura e geometria de uma ficha específica.

O vínculo deve sempre ser preservado.

O fato de não existir mais um mapa global reduz o risco de utilizar acidentalmente coordenadas pertencentes a outra ficha.

---

# 23. OMR

Arquivo principal:

```text
engine/omr.py
```

Fluxo:

```text
Caixa OMR
    ↓
recorte
    ↓
remoção da margem interna
    ↓
tons de cinza
    ↓
análise dos pixels
    ↓
percentual escuro
    ↓
MARCADA / VAZIA
```

---

# 24. Parâmetros validados do OMR

Configuração atualmente utilizada:

```text
Margem interna: 7 pixels
Threshold de pixel escuro: 150
Limiar de marcação: 5%
```

Regra equivalente:

```python
marcada = percentual >= 5.0
```

Esses valores foram obtidos por calibração física e não devem ser alterados sem novos testes.

---

# 25. Calibração da margem interna

Durante os testes foi identificado que a borda preta da própria caixa poderia ser interpretada como marcação.

Resultados de calibração com ficha branca:

| Margem | Falsos positivos |
| -----: | ---------------: |
|      4 |               22 |
|      5 |                2 |
|      6 |                1 |
|  **7** |            **0** |
|      8 |                0 |
|     10 |                0 |

Foi escolhida:

```text
Margem = 7
```

por ser o menor valor testado que eliminou todos os falsos positivos da ficha branca.

---

# 26. Validação física do OMR

## Ficha branca de duas páginas

Página 1:

```text
Total: 70
Marcadas: 0
Vazias: 70
```

Página 2:

```text
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

```text
0 falsos positivos
```

---

# 27. Teste físico com marcações

Teste anterior:

```text
Total: 50 caixas
Marcadas manualmente: 12
```

Resultado:

```text
12/12 marcações reconhecidas
100%
```

Esses resultados são referência importante para futuras alterações no OMR.

---

# 28. Visualização "Onde devo marcar?"

Arquivo:

```text
area_omr.py
```

A funcionalidade:

```text
Onde devo marcar?
```

mostra sobre a ficha as regiões efetivamente analisadas pelo OMR.

Objetivos:

* explicar onde a marca deve ser feita;
* verificar alinhamento;
* validar o mapa;
* identificar problemas geométricos;
* auxiliar diagnóstico.

O destaque vermelho:

```text
existe apenas na visualização
```

Ele não modifica:

* PDF original;
* ficha gerada;
* ficha impressa.

A funcionalidade foi testada novamente depois da remoção dos mapas antigos e continuou funcionando normalmente.

---

# 29. Validação visual

Foram testados:

* ficha de uma página;
* ficha de duas páginas;
* aumento da fonte;
* redução da fonte;
* alteração da paginação.

As áreas destacadas permaneceram alinhadas às caixas OMR.

---

# 30. Impressão

Configuração recomendada:

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

Mudanças de escala podem alterar fisicamente a relação entre o formulário e as coordenadas esperadas.

---

# 31. Digitalização

Configuração utilizada nos testes:

```text
Scanner: 600 DPI
Formato: PDF
```

A página escaneada passa posteriormente pela homografia.

Pequenas diferenças de alinhamento podem ser corrigidas pelos ArUcos.

---

# 32. Leitor

Arquivo:

```text
engine/leitor.py
```

Responsável pela integração:

```text
PDF
 +
ArUco
 +
geometria
 +
normalização
 +
mapa da ficha
 +
OMR
        ↓
resultado estruturado
```

O leitor não deve ser responsável diretamente por XLSX ou Google Sheets.

O leitor recebe explicitamente o caminho do mapa correspondente à ficha.

---

# 33. Resultado estruturado

Um registro final reúne:

```text
Campos de identificação
        +
Respostas OMR
        +
Respostas abertas
```

Exemplo:

```text
Data = 02/09/2026
Código = 00152
Nome = Maria Silva
1.1 = Sim
1.2 = Não
1.3 = Bom
2.4 = "Necessita manutenção"
```

Esse registro é enviado para a camada de persistência.

---

# 34. Proteção contra campos manuais vazios

Antes do salvamento, são analisados:

* campos de identificação;
* perguntas abertas.

Se existirem campos vazios, o SDIP mostra uma única confirmação.

Exemplo:

```text
Existem campos manuais não preenchidos:

• Matrícula
• 2.4 Observações

Deseja salvar mesmo assim?
```

Se o operador responder:

```text
Não
```

o registro não é salvo e os dados permanecem na tela.

Se responder:

```text
Sim
```

o salvamento continua.

Campos OMR sem resposta não participam desse aviso.

---

# 35. Opção Manter

Campos de identificação podem utilizar:

```text
[ ] Manter
```

Objetivo:

preservar dados repetidos durante o processamento sequencial de várias fichas.

Exemplo:

```text
Data:          02/09/2026  [✓]
Entrevistador: Maria       [✓]
Setor:         Financeiro  [✓]
Código:        00152       [ ]
Nome:          João        [ ]
```

Depois do salvamento:

```text
Data          → permanece
Entrevistador → permanece
Setor         → permanece
Código        → limpa
Nome          → limpa
```

Perguntas abertas também são limpas.

`Manter` é temporário da sessão.

Não é persistido como configuração estrutural em:

* ficha;
* `.sdip`;
* XLSX;
* Google Sheets.

---

# 36. Planilha XLSX

Arquivo:

```text
engine/sheets.py
```

A planilha é derivada diretamente da estrutura da ficha.

Ordem:

```text
Campos de identificação
        ↓
Perguntas
```

Seções não criam colunas.

---

# 37. Estrutura da planilha

Exemplo:

```text
Data
Código
Nome
1.1 A obra foi concluída?
1.2 Houve problemas?
2.1 Observações
```

A linha 1 representa permanentemente a estrutura da pesquisa.

```text
Linha 1 = cabeçalhos
Linha 2 = primeiro registro
Linha 3 = segundo registro
Linha 4 = terceiro registro
...
```

Cada ficha processada adiciona uma nova linha.

---

# 38. Recursos XLSX

A implementação atual mantém:

* cabeçalho;
* primeira linha congelada;
* filtro automático;
* largura ajustada;
* tipos de dados;
* compatibilidade com Excel;
* preservação da estrutura.

A aplicação não deve recriar os cabeçalhos a cada ficha.

---

# 39. Ficha como fonte da planilha

Não existe uma estrutura tabular independente definida manualmente.

```text
Estrutura da ficha
        ↓
PlanilhaResultados.cabecalhos_da_ficha()
        ↓
Linha 1
```

Isso mantém correspondência entre:

```text
campo/pergunta da ficha
        ↕
coluna
        ↕
resposta
```

---

# 40. Google Sheets

O SDIP também possui destino online para resultados.

Arquitetura:

```text
SDIP
 ↓
HTTP
 ↓
Google Apps Script Web App
 ↓
Google Sheets
```

Arquivo responsável:

```text
engine/google_sheets_webapp.py
```

A implementação utiliza a biblioteca padrão:

```text
urllib
```

---

# 41. Decisão de arquitetura do Google Sheets

A implementação inicial baseada em:

```text
Google Cloud
Service Account
credentials.json
gspread
google-auth
```

foi abandonada.

A implementação atual utiliza:

```text
Google Sheets
        +
Google Apps Script
        +
Web App
```

Isso permite utilizar a integração sem obrigar o projeto a depender da configuração anterior de Service Account.

---

# 42. Configuração do Google Sheets

Fluxo:

```text
Usuário cria Google Sheet
        ↓
SDIP gera chave de integração
        ↓
SDIP gera código Apps Script
        ↓
Usuário cola no Apps Script
        ↓
Publica como Web App
        ↓
Obtém URL /exec
        ↓
Informa URL ao SDIP
        ↓
SDIP testa
        ↓
Pesquisa vinculada
```

---

# 43. Chave de integração

A chave é criada utilizando:

```python
secrets.token_urlsafe(32)
```

Ela é utilizada para impedir chamadas triviais ao Web App sem a chave configurada naquela pesquisa.

A chave não deve ser publicada em:

* README;
* documentação pública;
* screenshots;
* exemplos reais.

---

# 44. Validação estrutural do Google Sheets

Antes da gravação, o SDIP compara os cabeçalhos esperados com os encontrados.

São comparados:

```text
quantidade
nomes
ordem
```

Caso exista divergência:

```text
salvamento bloqueado
```

Exemplo:

```text
Esperado:
Código | Nome | 1.1 Pergunta

Encontrado:
Nome | Código | 1.1 Pergunta
```

Mesmo contendo os mesmos nomes, a estrutura é incompatível porque a ordem foi alterada.

Esse comportamento já foi testado alterando propositalmente cabeçalhos.

---

# 45. LockService

O Apps Script utiliza:

```javascript
LockService
```

para reduzir conflitos quando duas gravações são realizadas em períodos muito próximos.

Isso é particularmente importante quando várias máquinas utilizam uma mesma pesquisa.

---

# 46. Uso multiusuário

Arquitetura implementada:

```text
Máquina A ─┐
           │
Máquina B ─┼──→ Google Sheets
           │
Máquina C ─┘
```

Cada computador possui a mesma pesquisa, mas envia os registros para uma mesma planilha online.

A lógica está implementada.

A validação em várias máquinas físicas diferentes ainda faz parte dos testes obrigatórios do MVP.

---

# 47. Pacote de pesquisa `.sdip`

Arquivo:

```text
engine/pacote_pesquisa.py
```

O formato:

```text
.sdip
```

permite exportar uma pesquisa para outro computador.

---

# 48. Dados transportados pelo `.sdip`

O pacote pode preservar:

* ficha;
* `ficha_id`;
* `pesquisa_id`;
* versão;
* PDF;
* mapa OMR;
* logo;
* estrutura;
* Google Web App URL;
* chave de integração;
* cabeçalhos Google;
* regra de nomeação do PDF.

Isso permite que outra instalação do SDIP receba a mesma estrutura lógica da pesquisa.

---

# 49. Dados que não devem viajar no `.sdip`

Configurações específicas de uma máquina não são transportadas.

Exemplos:

```text
caminho do XLSX local
pasta local de PDFs processados
```

Motivo:

```text
C:\Pesquisa\Resultados
```

pode existir na máquina A e não existir na máquina B.

---

# 50. Integridade do `.sdip`

O sistema possui verificações para:

* pacote inválido;
* corrupção;
* ficha duplicada;
* pesquisa/versão já existente;
* conteúdo incompatível.

A importação não deve sobrescrever silenciosamente uma pesquisa existente.

---

# 51. RASCUNHO

Uma ficha recém-criada inicia como:

```text
RASCUNHO
```

Durante essa fase ela pode ser alterada antes de entrar efetivamente em produção.

---

# 52. PRODUÇÃO

Depois que a ficha é considerada válida e recebe um destino de resultados, passa a representar uma estrutura de coleta em produção.

Conceitualmente:

```text
Ficha
+
PDF
+
Mapa
+
estrutura de resultados
```

representam uma mesma versão.

A estrutura de uma pesquisa em produção deve ser preservada.

---

# 53. Nova versão

Alterações estruturais em uma pesquisa já em produção devem gerar nova versão.

Exemplo:

```text
Pesquisa
│
├── v1
│   ├── PDF
│   ├── mapa
│   └── planilha
│
└── v2
    ├── PDF
    ├── mapa
    └── nova estrutura
```

A nova versão:

* mantém a identidade da pesquisa;
* incrementa o número da versão;
* registra a versão anterior;
* volta para RASCUNHO;
* não herda automaticamente um destino estrutural incompatível da versão anterior.

---

# 54. Nome automático do PDF processado

Campos de identificação podem ser configurados com:

```text
[ ] Nome do PDF
```

Essa opção não altera visualmente a ficha.

Ela registra uma regra interna.

Exemplo:

```text
Código     [✓ Nome do PDF]
Nome       [✓ Nome do PDF]
Data       [ ]
```

Registro:

```text
Código = 00152
Nome = Maria Silva
```

Resultado:

```text
00152_Maria Silva.pdf
```

---

# 55. Regras do nome do PDF

* mais de um campo pode ser utilizado;
* a ordem segue o cabeçalho;
* campos vazios são ignorados;
* se todos estiverem vazios, o nome original é utilizado;
* caracteres inválidos do Windows são sanitizados;
* o PDF original não é removido;
* arquivos existentes não são sobrescritos.

Colisões:

```text
00152_Maria Silva.pdf
00152_Maria Silva_2.pdf
00152_Maria Silva_3.pdf
```

---

# 56. Pasta dos PDFs processados

Cada pesquisa possui um destino de arquivamento configurável por computador.

Exemplo:

```text
C:\Pesquisas\Processados
```

ou:

```text
\\Servidor\Pesquisas\Processados
```

A configuração é local.

---

# 57. Configuração local

Preferencialmente armazenada em:

```text
%LOCALAPPDATA%\SDIP\config_local.json
```

associada ao:

```text
pesquisa_id
```

O caminho não deve viajar dentro do `.sdip`.

O nome `config_local.json` não possui relação com a antiga pasta `config/` removida do projeto.

São conceitos diferentes:

```text
config/ antigo
→ mapas OMR globais obsoletos

%LOCALAPPDATA%\SDIP\config_local.json
→ preferências locais válidas da instalação
```

---

# 58. Destino indisponível

Se a pasta configurada não estiver mais acessível:

```text
detectar problema
        ↓
solicitar novo destino
        ou
cancelar
```

O sistema não deve salvar silenciosamente em outro local.

---

# 59. Segurança do salvamento

O salvamento envolve duas informações relacionadas:

```text
dados
+
PDF processado
```

O fluxo deve evitar produzir um estado parcial.

Exemplo indesejado:

```text
PDF arquivado

mas

registro não salvo
```

ou:

```text
registro salvo

mas

processamento considerado incompleto
```

A implementação possui tratamento para remover a nova cópia do PDF quando o registro de dados falha depois de sua criação.

---

# 60. Seleção de múltiplos PDFs

A tela de digitalização permite:

```text
Selecionar ficha(s) PDF
```

O operador pode escolher:

```text
1 arquivo
```

ou:

```text
vários arquivos
```

---

# 61. Fila de processamento

Com vários arquivos:

```text
Arquivo 1 de 10 — ficha001.pdf
Arquivo 2 de 10 — ficha002.pdf
Arquivo 3 de 10 — ficha003.pdf
...
```

Cada PDF representa uma ficha digitalizada para processamento.

Um PDF pode possuir mais de uma página.

---

# 62. Fluxo da fila

```text
Selecionar PDFs
        ↓
Abrir primeiro
        ↓
Ler ficha (OMR)
        ↓
Conferir
        ↓
Preencher campos
        ↓
Salvar
        ↓
Salvar dados
        ↓
Arquivar PDF
        ↓
Aplicar Manter
        ↓
Limpar demais campos
        ↓
Abrir próximo PDF
```

---

# 63. OMR não automático na fila

O próximo PDF é carregado automaticamente.

Por segurança, o OMR não é disparado automaticamente.

O operador precisa iniciar:

```text
Ler ficha (OMR)
```

em cada novo arquivo.

Isso cria um ponto explícito de controle.

---

# 64. Condições para avanço

A fila somente avança quando o salvamento atual é concluído corretamente.

Não avançar quando houver:

* data inválida;
* cancelamento;
* campos vazios não confirmados;
* erro no XLSX;
* erro no Google Sheets;
* erro no PDF;
* pasta de destino indisponível;
* erro no arquivamento.

O PDF atual permanece disponível para correção e nova tentativa.

---

# 65. Final da fila

Depois do último arquivo:

```text
Fila concluída
```

O estado deve indicar quantos arquivos foram processados.

---

# 66. Interface

A interface utiliza CustomTkinter.

Configuração atual da janela:

```text
1200 × 750
```

Tamanho mínimo:

```text
1000 × 600
```

A reorganização foi feita para melhorar o uso em notebooks e janelas menores.

---

# 67. Digitalizar / Preencher

Estrutura aproximada:

```text
┌──────────────────────┬────────────────────────────┐
│                      │ Ações                      │
│                      │                            │
│ PDF                  │ Campos                     │
│                      │                            │
│                      │ Respostas abertas          │
│                      │                            │
│                      │ Salvar                     │
└──────────────────────┴────────────────────────────┘
```

O divisor pode ser movimentado.

A ficha e os campos permanecem visíveis simultaneamente.

---

# 68. Criar / Editar

Estrutura:

```text
┌──────────────────────┬────────────────────────────┐
│ Configurações        │ Estrutura                  │
│                      │                            │
│ Cabeçalho            │ Seções                     │
│ Logo                 │ Perguntas                  │
│ Fonte                │ Opções                     │
│ Campos               │                            │
└──────────────────────┴────────────────────────────┘
```

Também possui divisor redimensionável.

---

# 69. Visualizador

Arquivo:

```text
ui/viewer.py
```

Recursos:

* ajuste automático;
* zoom;
* aumento;
* redução;
* faixa aproximada de 50% a 300%;
* scroll;
* navegação multipágina;
* redimensionamento;
* preservação da proporção.

O arquivo poderá ser revisado depois da validação real do MVP.

Não deve ser refatorado agora apenas por organização.

---

# 70. Componentes críticos

Os seguintes arquivos possuem comportamento físico já validado:

```text
engine/gerador_ficha.py
engine/geometria.py
engine/omr.py
```

Regra geral:

```text
não alterar sem bug comprovado
```

Alterações nesses componentes devem ser pequenas e justificadas.

A alteração recente de `engine/omr.py` foi uma exceção controlada: removeu apenas o fallback para um arquivo legado comprovadamente não utilizado.

Nenhum parâmetro OMR foi alterado.

---

# 71. Regra de manutenção do núcleo

Antes de alterar um componente validado:

```text
Problema observado
        ↓
Problema reproduzível?
        ↓
Qual componente causa?
        ↓
Alteração mínima
        ↓
Teste
        ↓
Comparação com resultado anterior
```

Não recalibrar OMR apenas porque um valor diferente parece teoricamente melhor.

Não substituir soluções funcionais por implementações mais elegantes apenas por preferência arquitetural.

---

# 72. Questão ainda pendente — Outros + Qual?

Existe um comportamento que ainda depende da confirmação do processo real dos usuários.

Exemplo:

```text
☐ Outros

Qual? __________________________
```

A decisão necessária é:

```text
O texto escrito em "Qual?"
deve virar uma coluna/valor estruturado?
```

Até essa decisão ser tomada:

* não assumir comportamento;
* não criar coluna automaticamente;
* não modificar a arquitetura para esse caso;
* observar o processo real utilizado pelos usuários.

Perguntas abertas independentes continuam funcionando normalmente.

---

# 73. Testes multi-PC ainda necessários

Antes de considerar a distribuição estável:

```text
[ ] importar .sdip em outra máquina
[ ] abrir pesquisa sem reconfigurar Google
[ ] fechar e abrir novamente
[ ] confirmar persistência da integração
[ ] salvar registros a partir de duas máquinas
[ ] testar gravações próximas no tempo
[ ] alterar cabeçalho Google e confirmar bloqueio
[ ] restaurar cabeçalho
[ ] confirmar funcionamento novamente
[ ] confirmar caminhos locais independentes
[ ] confirmar pasta de processados própria por máquina
```

---

# 74. Teste físico final

Fluxo prioritário:

```text
Criar ficha real
        ↓
Colocar em produção
        ↓
Imprimir A4 100%
        ↓
Preencher
        ↓
Scanner 600 DPI
        ↓
Selecionar PDFs
        ↓
OMR
        ↓
Conferência
        ↓
Campos manuais
        ↓
Salvar
        ↓
Google/XLSX
        ↓
PDF processado
        ↓
próxima ficha
```

Esse teste deve ser executado no ambiente real de trabalho antes de considerar o MVP estabilizado.

---

# 75. Testes negativos importantes

Devem ser testados:

```text
PDF sem ArUco
PDF incorreto
arquivo corrompido
página faltando
página duplicada
página invertida
página fora de ordem
imagem ruim
marca fraca
marca parcial
marca fora da caixa
pergunta objetiva sem resposta
campo manual vazio
data inválida
Google indisponível
cabeçalho Google alterado
XLSX indisponível
pasta de PDFs indisponível
```

O sistema deve preferencialmente:

```text
detectar
        ↓
informar
        ↓
não perder dados
        ↓
não avançar silenciosamente
```

---

# 76. Testes regressivos mantidos

Depois da remoção de scripts de diagnóstico obsoletos, permanecem relevantes:

```text
teste_gerador_ficha.py
teste_omr_2.py
teste_omr_margem7.py
```

Foram removidos anteriormente:

```text
teste_calibracao_margem.py
teste_diagnostico_ficha_gerada.py
teste_layout_ficha.py
teste_omr_png.py
teste_overlay_mapa.py
```

O `teste_gerador_ficha.py` utiliza atualmente:

```text
temp/mapa_caixas_gerado.json
```

O diretório `temp/` contém apenas artefatos temporários e não faz parte da arquitetura persistente da aplicação.

Em uma cópia limpa do projeto, pode ser necessário criar `temp/` antes de executar esse script de teste.

---

# 77. Empacotamento Windows

O projeto entrou na fase de geração e validação do executável.

A primeira estratégia utilizada foi:

```text
PyInstaller
+
onedir
```

A versão do PyInstaller utilizada na primeira build foi:

```text
6.22.2
```

Estrutura gerada:

```text
dist/
└── SDIP/
    ├── SDIP.exe
    ├── MANUAL_USUARIO_SDIP.pdf
    └── _internal/
```

O diretório inteiro deve permanecer junto.

Não distribuir apenas:

```text
SDIP.exe
```

quando a build é `onedir`.

---

# 78. Primeira build Windows

A primeira build foi gerada com:

```powershell
pyinstaller --noconfirm --clean --windowed --onedir --name SDIP --collect-all customtkinter app.py
```

Ela:

* foi criada corretamente;
* abriu localmente;
* funcionou fora da pasta original;
* foi compactada em ZIP;
* foi extraída novamente;
* continuou abrindo.

Portanto, o fluxo básico de empacotamento com PyInstaller foi tecnicamente funcional.

---

# 79. Detecção heurística na primeira build

Durante a validação de segurança do executável, a primeira build apresentou detecções heurísticas em alguns mecanismos antivírus.

Entre as classificações observadas estavam detecções genéricas relacionadas a comportamento suspeito, empacotamento ou machine learning.

Ao mesmo tempo, diversos mecanismos relevantes não detectaram ameaça.

Esse padrão é compatível com a possibilidade de falso positivo em executáveis empacotados com PyInstaller, mas isso **não é suficiente para autorizar distribuição sem nova validação**.

A decisão adotada foi:

```text
não liberar a build
não criar exceção no antivírus
não restaurar o arquivo apenas para continuar usando
não publicar Release
descartar a build
recuperar código-fonte limpo
recriar ambiente
gerar nova build
reanalisar
```

A primeira build nunca foi publicada como Release.

---

# 80. Recuperação do código-fonte

Depois do alerta da primeira build, o diretório local foi descartado.

O código-fonte atual foi obtido novamente a partir do repositório GitHub.

O pacote contendo apenas o código-fonte não apresentou a mesma detecção local observada no executável anterior.

Como o projeto foi obtido através de Download ZIP, o diretório não continha `.git`.

O histórico foi reconectado ao remoto através de:

```powershell
git init
git branch -M main
git remote add origin https://github.com/DiogoBarbosa23/SDIP.git
git fetch origin
git reset origin/main
```

Foi utilizado:

```text
git reset origin/main
```

sem `--hard`.

Isso permitiu recuperar a relação com o histórico remoto preservando alterações locais posteriores.

---

# 81. Nova build planejada

O ambiente virtual foi recriado.

As dependências do projeto foram instaladas novamente.

Antes da próxima build, instalar PyInstaller no ambiente novo caso ainda não esteja instalado.

Comando planejado:

```powershell
pip install pyinstaller
```

Depois:

```powershell
pyinstaller --version
```

Nova build:

```powershell
pyinstaller --noconfirm --clean --windowed --onedir --noupx --name SDIP --collect-all customtkinter app.py
```

O parâmetro:

```text
--noupx
```

será utilizado na nova tentativa.

Depois da geração, copiar o manual:

```powershell
Copy-Item .\docs\MANUAL_USUARIO_SDIP.pdf .\dist\SDIP\
```

---

# 82. Validação da nova build

Depois de gerar o executável:

1. confirmar que `SDIP.exe` foi criado;
2. testar abertura local;
3. verificar funcionamento básico;
4. calcular SHA-256;
5. analisar o novo executável;
6. avaliar as detecções;
7. somente depois compactar a distribuição.

Hash:

```powershell
Get-FileHash .\dist\SDIP\SDIP.exe -Algorithm SHA256
```

Não desativar antivírus apenas para permitir o teste.

Não adicionar exceção permanente apenas para forçar a execução.

---

# 83. Motivo para utilizar `onedir`

O projeto utiliza bibliotecas com recursos adicionais, principalmente:

* CustomTkinter;
* OpenCV;
* PyMuPDF;
* Pillow.

A distribuição inicial prioriza confiabilidade.

`onedir` também facilita:

* inspeção dos arquivos;
* diagnóstico de dependências;
* comparação de builds;
* identificação de problemas durante os testes.

Depois da validação poderá ser avaliado:

```text
onefile
```

caso exista vantagem prática.

Não é prioridade do MVP.

---

# 84. GitHub Release

O executável e o Release são elementos diferentes.

```text
Executável
→ aplicação compilada para Windows

Release
→ distribuição de uma versão do aplicativo
```

Fluxo esperado:

```text
Código
 ↓
PyInstaller
 ↓
SDIP.exe + arquivos internos
 ↓
análise da build
 ↓
teste local
 ↓
ZIP
 ↓
GitHub Release
 ↓
Download pelos usuários
```

Até o momento, nenhuma build executável foi publicada como Release.

---

# 85. Estratégia inicial de Release

A primeira publicação futura poderá funcionar como:

```text
build de teste
```

para validação nas máquinas do trabalho.

Depois da validação real:

```text
build validada
        ↓
Release estável
```

Somente uma build considerada adequada deve ser divulgada como versão estável.

---

# 86. Manuais

O projeto possui documentação de uso destinada a usuários não técnicos.

Arquivos:

```text
MANUAL_USUARIO.md
docs/MANUAL_USUARIO_SDIP.pdf
docs/manual_rapido_sdip.png
```

Objetivos:

* explicar o fluxo operacional;
* orientar criação e uso das pesquisas;
* explicar impressão e digitalização;
* reduzir dependência de suporte técnico;
* facilitar validação com usuários reais.

O manual técnico deste arquivo não substitui o manual do usuário.

---

# 87. Arquivos que não devem ser publicados

Nunca incluir:

```text
.venv/
credenciais
tokens
.env
PDFs reais com dados pessoais
planilhas com informações pessoais
arquivos temporários
imagens sensíveis
chaves de integração expostas
```

---

# 88. Dados produzidos pelos usuários

Os seguintes arquivos podem conter dados reais:

* PDFs digitalizados;
* XLSX;
* Google Sheets;
* respostas abertas;
* dados de identificação.

Eles devem ser tratados separadamente do código do projeto.

Não utilizar dados reais em:

* commits;
* Issues públicas;
* documentação;
* capturas de tela do README;
* exemplos públicos.

---

# 89. Repositório principal e versão institucional

Estratégia atual:

```text
Repositório pessoal
        ↓
desenvolvimento principal
        ↓
novas funcionalidades
        ↓
testes
        ↓
Releases
```

e:

```text
Repositório institucional
        ↓
versão estável
        ↓
documentação própria
        ↓
atualizações controladas
```

A versão institucional não precisa acompanhar todos os commits do projeto principal.

---

# 90. Autoria

O SDIP foi desenvolvido por **Diogo Barbosa**.

O projeto surgiu a partir de uma necessidade prática apresentada no ambiente de trabalho e foi desenvolvido como uma solução genérica capaz de ser reutilizada em diferentes pesquisas.

A disponibilização de versões para uso institucional não deve ser interpretada automaticamente como transferência da autoria ou do desenvolvimento contínuo do projeto principal, observadas as disposições legais e contratuais aplicáveis.

A documentação atual não classifica automaticamente o projeto como software de código aberto e não aplica licença permissiva sem decisão explícita sobre a política de distribuição do código-fonte.

---

# 91. Estado atual do MVP

Implementado:

```text
[x] criação dinâmica de ficha
[x] cabeçalho configurável
[x] tipos de campos
[x] datas
[x] logo
[x] seções
[x] perguntas fechadas
[x] respostas únicas
[x] respostas múltiplas
[x] perguntas abertas
[x] paginação automática
[x] layout em duas colunas
[x] ArUco
[x] homografia
[x] normalização
[x] OMR
[x] mapa automático próprio por ficha
[x] visualização das áreas OMR
[x] ficha ativa
[x] RASCUNHO / PRODUÇÃO
[x] versionamento
[x] XLSX
[x] Google Sheets
[x] validação estrutural
[x] integração multi-PC
[x] exportação .sdip
[x] importação .sdip
[x] validação de integridade
[x] alerta de campos manuais vazios
[x] datas DD/MM/AAAA
[x] opção Manter
[x] regra Nome do PDF
[x] arquivamento automático
[x] proteção contra sobrescrita
[x] destino local por computador
[x] seleção múltipla de PDFs
[x] fila
[x] avanço automático
[x] bloqueio de avanço em erro
[x] interface adaptada para notebook
[x] zoom e navegação de PDF
[x] manual do usuário
[x] manual PDF
[x] guia visual rápido
[x] remoção do mapa OMR global legado
```

---

# 92. Fase atual

O projeto não está mais na fase principal de implementação do MVP.

A fase atual é:

```text
MVP implementado
        ↓
limpeza final e documentação
        ↓
nova build Windows
        ↓
validação de segurança
        ↓
testes em máquinas diferentes
        ↓
teste físico real
        ↓
correção somente de bugs comprovados
        ↓
Release estável
```

---

# 93. Próximos passos imediatos

Sequência recomendada:

```text
1. concluir atualização da documentação
2. revisar git diff
3. revisar git status
4. confirmar que não existem mudanças inesperadas
5. commit da limpeza do mapeamento legado
6. push para origin/main
7. instalar PyInstaller no novo .venv
8. gerar nova build com --noupx
9. testar localmente
10. calcular hash
11. analisar executável
12. compactar somente se a build for considerada adequada
13. testar ZIP extraído
14. criar Release de teste
15. executar em máquina do trabalho
16. executar checklist físico
17. corrigir somente bugs reproduzíveis
18. gerar versão estável
```

Mensagem de commit sugerida para a limpeza atual:

```text
Remove residuos do mapeamento OMR legado
```

---

# 94. Refatoração

Durante a fase atual:

```text
NÃO realizar refatoração ampla
```

Mesmo que arquivos como:

```text
ui/main_window.py
ui/viewer.py
```

tenham crescido.

Primeiro:

```text
testar
        ↓
estabilizar
        ↓
distribuir
```

Depois:

```text
refatorar
```

---

# 95. Melhorias posteriores

Depois do MVP poderão ser avaliados:

* normalização avançada de identificadores;
* detecção de registros duplicados;
* governança multiusuário avançada;
* controle de alterações estruturais;
* votação ou aprovação de mudanças;
* revisão de edição de rascunhos;
* melhoria adicional de UX;
* testes automatizados;
* reorganização de código;
* otimizações;
* revisão de módulos grandes;
* possíveis melhorias no empacotamento.

Nenhum desses itens deve atrasar a validação do MVP atual.

---

# 96. Workflow de alteração

Antes de uma alteração relevante de código:

1. listar objetivamente as mudanças propostas;
2. identificar os arquivos afetados;
3. explicar a necessidade;
4. confirmar que existe motivo funcional;
5. obter autorização;
6. trabalhar sobre a versão atual do arquivo;
7. evitar alterações fora do escopo;
8. testar;
9. revisar `git diff`;
10. registrar em commit.

Mudanças em arquivos críticos exigem cautela adicional.

---

# 97. Regra para componentes validados

Antes de alterar:

```text
engine/gerador_ficha.py
engine/geometria.py
engine/omr.py
```

seguir:

```text
problema observado
        ↓
reproduzir
        ↓
identificar causa
        ↓
propor mudança mínima
        ↓
verificar impacto
        ↓
alterar
        ↓
testar
        ↓
comparar
        ↓
commit
```

Nunca modificar o núcleo apenas por suspeita.

---

# 98. Princípio final de manutenção

O SDIP possui componentes construídos e calibrados com testes físicos reais.

O fluxo de desenvolvimento deve permanecer:

```text
observar problema real
        ↓
reproduzir
        ↓
identificar causa
        ↓
propor mudança mínima
        ↓
testar
        ↓
validar
        ↓
commit
```

Não substituir soluções funcionais por alternativas teoricamente mais elegantes sem necessidade comprovada.

Não alterar parâmetros de OMR sem teste físico que justifique a mudança.

Não reintroduzir mapas OMR globais.

Cada ficha deve continuar utilizando seu próprio mapa.

---

# 99. Estado técnico em 03/09/2026

O estado atual é:

```text
MVP funcional implementado
        ↓
arquitetura de mapa OMR legado removida
        ↓
fluxo funcional revalidado
        ↓
documentação sendo sincronizada
        ↓
primeira build descartada antes do Release
        ↓
ambiente limpo recriado
        ↓
nova build pendente
        ↓
teste real no ambiente de trabalho
```

A remoção de:

```text
config/mapa_caixas.json
config/mapa_caixas_gerado.json
```

foi verificada e não comprometeu:

```text
geração de ficha
mapa OMR
Onde devo marcar?
leitura OMR
salvamento
```

A arquitetura atual exige explicitamente o mapa pertencente à ficha utilizada.

---

# Autor

**Diogo Barbosa**

SDIP — Sistema de Digitalização Inteligente de Pesquisas
