# SDIP

## Sistema de Digitalização Inteligente de Pesquisas

O **SDIP** é uma aplicação desktop desenvolvida em **Python** para automatizar a criação, impressão, digitalização, leitura e organização de pesquisas preenchidas manualmente em papel.

O sistema transforma fichas físicas em dados estruturados utilizando **processamento de imagens, marcadores ArUco, correção geométrica por homografia e OMR (Optical Mark Recognition)**.

O projeto surgiu a partir de uma necessidade real de trabalho: reduzir o processo manual envolvido na criação, aplicação, conferência, digitalização e digitação de pesquisas realizadas em formulários impressos.

A proposta do SDIP é ser uma solução genérica, capaz de atender diferentes pesquisas e instituições sem depender de um formulário fixo.

---

## Documentação

Para detalhes sobre arquitetura, funcionamento interno, calibração do OMR, decisões técnicas, integrações e testes realizados, consulte:

[Documentação técnica do SDIP](documentacao.md)

# Fluxo principal

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
Imprimir em A4 / 100%
      ↓
Preenchimento manual
      ↓
Digitalizar uma ou várias fichas em PDF
      ↓
Selecionar os PDFs no SDIP
      ↓
Abrir primeiro arquivo da fila
      ↓
Detectar ArUcos
      ↓
Corrigir geometria
      ↓
Executar leitura OMR
      ↓
Conferir e preencher campos manuais
      ↓
Validar dados
      ↓
Salvar resultado
      ↓
Registrar em XLSX ou Google Sheets
      ↓
Arquivar cópia do PDF processado
      ↓
Carregar automaticamente o próximo PDF
      ↓
Repetir até concluir a fila
```

---

# Principais funcionalidades

## Criação de pesquisas

O SDIP permite configurar:

* nome da pesquisa;
* título;
* logo;
* campos personalizados de identificação;
* tipo dos campos de identificação;
* campos de data;
* seções;
* perguntas;
* respostas únicas;
* respostas múltiplas;
* perguntas abertas;
* opções de resposta;
* tamanho da fonte;
* campos que participarão do nome do PDF processado.

O sistema gera automaticamente:

* layout da ficha;
* distribuição em duas colunas;
* paginação;
* caixas OMR;
* marcadores ArUco;
* áreas destinadas às respostas abertas;
* mapa de coordenadas OMR;
* PDF final da pesquisa.

O usuário não precisa definir coordenadas manualmente.

---

# Campos de identificação

Cada pesquisa pode possuir campos próprios de identificação.

Exemplos:

```text
Data
Nome
CPF
Matrícula
Código
Comunidade
Setor
Entrevistador
Número do imóvel
Protocolo
```

Esses campos passam a fazer parte da estrutura da pesquisa e também podem ser utilizados para:

* identificar cada registro;
* compor as colunas da planilha;
* manter valores entre fichas consecutivas;
* gerar automaticamente o nome dos PDFs processados.

---

# Campos de data

Campos configurados com o tipo `Data` utilizam obrigatoriamente o padrão:

```text
DD/MM/AAAA
```

Exemplo válido:

```text
02/09/2026
```

O SDIP verifica:

* formato completo;
* quatro dígitos no ano;
* separadores;
* existência real da data.

Exemplos inválidos:

```text
02/09/26
2/9/2026
2026-09-02
31/02/2026
15/13/2026
```

Uma data inválida impede o salvamento até que seja corrigida.

Campos de data vazios continuam permitidos, mas entram na validação de campos manuais não preenchidos.

---

# Opção Manter

Na tela de digitalização, cada campo de identificação possui a opção:

```text
[ ] Manter
```

Ela permite preservar valores que serão utilizados novamente nas próximas fichas da mesma sequência.

Exemplo:

```text
Data:          02/09/2026    [✓ Manter]
Entrevistador: João          [✓ Manter]
Setor:         Financeiro    [✓ Manter]

Nome:          Maria         [ ]
Matrícula:     12345         [ ]
```

Depois de salvar:

```text
Data          → permanece
Entrevistador → permanece
Setor         → permanece

Nome          → é limpo
Matrícula     → é limpa
```

Perguntas abertas são limpas para a próxima ficha.

A opção `Manter` é operacional e temporária. Ela não altera a estrutura permanente da pesquisa nem é transportada como configuração da ficha.

---

# Proteção contra campos manuais em branco

Antes de salvar um resultado, o SDIP verifica:

* campos de identificação;
* perguntas abertas.

Caso existam campos vazios, uma única confirmação apresenta todos os campos encontrados.

Exemplo:

```text
Existem campos manuais não preenchidos:

• Matrícula
• 12 Observações

Deseja salvar o resultado mesmo assim?
```

O operador pode escolher:

```text
Não
→ retornar ao formulário sem perder os dados

Sim
→ salvar normalmente com os campos correspondentes vazios
```

A validação não interfere em alternativas objetivas que não foram marcadas no OMR.

---

# Nome automático dos PDFs processados

Durante a criação da pesquisa, cada campo de identificação possui a opção:

```text
[ ] Nome do PDF
```

Essa opção é apenas uma configuração interna e **não altera visualmente a ficha impressa**.

Ela define quais campos serão utilizados para nomear automaticamente o PDF processado.

Exemplo:

```text
Campo          Tipo       Nome do PDF
----------------------------------------
Data           Data       [ ]
Código         Texto      [✓]
Nome           Texto      [✓]
Entrevistador  Texto      [ ]
```

Durante o preenchimento:

```text
Código: 00152
Nome: Maria Silva
```

O PDF será arquivado como:

```text
00152_Maria Silva.pdf
```

Quando vários campos forem selecionados, a ordem utilizada é a mesma ordem dos campos no cabeçalho.

Campos selecionados que estiverem vazios são ignorados.

Se todos os campos escolhidos estiverem vazios, o nome original do PDF digitalizado é utilizado.

Caracteres incompatíveis com nomes de arquivos no Windows são tratados automaticamente.

Arquivos existentes nunca são sobrescritos.

Exemplo:

```text
00152_Maria Silva.pdf
00152_Maria Silva_2.pdf
00152_Maria Silva_3.pdf
```

---

# Pasta dos PDFs processados

Cada pesquisa pode possuir uma pasta local destinada ao arquivamento dos PDFs processados.

Exemplo:

```text
C:\Pesquisas\Pesquisa de Satisfação\Processados
```

A pasta é configurada uma única vez **por pesquisa e por computador**.

Essa configuração fica armazenada localmente pelo SDIP e não é incluída no pacote `.sdip`.

Isso evita transportar caminhos inválidos entre computadores.

Exemplo:

```text
Computador A
C:\Pesquisas\Processados

Computador B
D:\Arquivos\Pesquisa

Computador C
\\Servidor\Pesquisas\Processados
```

Se a pasta configurada deixar de existir ou ficar indisponível, o SDIP solicita outro local em vez de salvar silenciosamente em uma pasta diferente.

---

# Processamento de múltiplos PDFs

O SDIP permite selecionar **uma ou várias fichas PDF ao mesmo tempo**.

Ao selecionar vários arquivos, é criada uma fila de processamento.

Exemplo:

```text
Arquivo 1 de 15 — ficha_001.pdf
Arquivo 2 de 15 — ficha_002.pdf
Arquivo 3 de 15 — ficha_003.pdf
...
Arquivo 15 de 15 — ficha_015.pdf
```

O fluxo é sequencial:

```text
Selecionar vários PDFs
        ↓
Abrir arquivo 1
        ↓
Executar OMR
        ↓
Conferir
        ↓
Salvar
        ↓
Arquivar PDF
        ↓
Abrir automaticamente arquivo 2
        ↓
Executar OMR
        ↓
...
```

O OMR **não é executado automaticamente** no próximo arquivo.

O operador continua responsável por clicar em:

```text
Ler ficha (OMR)
```

Isso mantém uma etapa explícita de controle entre uma ficha e outra.

---

## Avanço automático da fila

O próximo PDF somente é carregado depois que o resultado atual é concluído corretamente.

O SDIP não avança quando ocorre:

* cancelamento do salvamento;
* data inválida;
* confirmação de campos vazios recusada;
* erro na planilha XLSX;
* erro no Google Sheets;
* erro durante o arquivamento do PDF;
* qualquer falha que impeça a conclusão do registro.

Nesse caso, o PDF atual permanece disponível para correção.

Depois que a última ficha é salva, o sistema informa a conclusão da fila.

```text
Fila concluída.
15 arquivos foram processados.
```

---

# Fluxo operacional de várias fichas

Com as funções de fila, `Manter` e arquivamento automático, o fluxo operacional pode ser:

```text
Selecionar 30 PDFs
      ↓
Arquivo 1 de 30
      ↓
Ler OMR
      ↓
Conferir
      ↓
Manter Data e Entrevistador
      ↓
Salvar
      ↓
Dados enviados
      ↓
PDF arquivado
      ↓
Arquivo 2 de 30 carregado automaticamente
      ↓
Data e Entrevistador permanecem
      ↓
Ler OMR
      ↓
...
      ↓
Arquivo 30 de 30
      ↓
Salvar
      ↓
Fila concluída
```

---

# Segurança do salvamento

O fluxo foi projetado para reduzir a possibilidade de perda silenciosa ou inconsistência.

O resultado somente é considerado concluído depois das etapas obrigatórias.

Em caso de erro:

* os campos digitados permanecem disponíveis;
* o resultado OMR não é descartado indevidamente;
* a fila não avança;
* o operador recebe uma mensagem de erro;
* um PDF criado durante uma operação incompleta pode ser removido para evitar inconsistência.

---

# Interface adaptada para notebooks

A interface foi reorganizada para aproveitar melhor notebooks e janelas menores.

## Criar / Editar ficha

A tela utiliza duas áreas lado a lado:

```text
┌────────────────────────┬──────────────────────────────┐
│ Configuração           │ Estrutura da ficha           │
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

---

## Digitalizar / Preencher

A ficha e os campos são exibidos simultaneamente:

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

# Visualizador de PDF

O visualizador permite acompanhar a ficha durante a conferência e digitalização.

Recursos:

* ajuste automático à área disponível;
* preservação da proporção;
* visualização da página completa;
* zoom;
* aumento e redução de zoom;
* retorno ao modo ajustado;
* scroll quando a página está ampliada;
* redimensionamento junto com a interface;
* navegação entre páginas.

---

# OMR

Cada alternativa de uma pergunta fechada recebe automaticamente uma caixa OMR.

Fluxo:

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

Esses parâmetros fazem parte do núcleo validado e não devem ser alterados sem novos testes físicos.

---

# ArUco e correção geométrica

Cada página utiliza quatro marcadores ArUco.

Configuração:

```text
Dicionário: DICT_4X4_50
OpenCV validado: 4.12.0
```

Fluxo:

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

Resolução normalizada:

```text
1191 × 1684 pixels
```

---

# Mapa OMR

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

# Resultado final

Cada registro combina:

```text
Campos de identificação
        +
Respostas OMR
        +
Respostas abertas
```

O resultado pode ser armazenado em:

```text
Planilha XLSX local
ou
Google Sheets compartilhado
```

O PDF correspondente também pode ser arquivado automaticamente.

---

# Planilha XLSX

O SDIP pode utilizar uma planilha `.xlsx` vinculada à pesquisa.

Sua estrutura é derivada diretamente da ficha:

```text
Campos do cabeçalho
        ↓
Perguntas
```

As seções são apenas organizacionais e não geram colunas.

Cada ficha processada adiciona uma nova linha.

A planilha possui:

* cabeçalho;
* primeira linha congelada;
* filtro automático;
* organização das colunas;
* tratamento de dados;
* compatibilidade com Excel.

---

# Google Sheets

O SDIP suporta salvamento online em **Google Sheets**.

A integração utiliza:

```text
Google Sheets
      +
Google Apps Script
      +
Web App
```

Não é necessário utilizar:

* Google Cloud com faturamento;
* Service Account;
* `credentials.json`;
* `gspread`.

O próprio SDIP gera:

* chave de integração;
* código do Apps Script;
* estrutura esperada dos cabeçalhos.

Fluxo:

```text
Criar Google Sheet
      ↓
Abrir Extensões → Apps Script
      ↓
Copiar código gerado pelo SDIP
      ↓
Implantar como Web App
      ↓
Copiar URL /exec
      ↓
Vincular no SDIP
```

Depois da configuração, a pesquisa pode enviar registros diretamente para a planilha compartilhada.

---

# Proteção da estrutura do Google Sheets

Antes de inserir um registro, o SDIP compara:

```text
Estrutura esperada pela pesquisa
            ×
Estrutura real da planilha
```

São verificados:

* quantidade de colunas;
* nomes;
* ordem;
* campos ausentes;
* campos adicionais.

Se a estrutura tiver sido alterada de forma incompatível, a inserção é bloqueada.

Isso reduz o risco de gravar respostas em colunas incorretas.

---

# Uso em vários computadores

Uma mesma pesquisa pode ser instalada em computadores diferentes.

Exemplo:

```text
Máquina A ─┐
           │
Máquina B ─┼──→ Google Sheets compartilhado
           │
Máquina C ─┘
```

As máquinas podem utilizar a mesma estrutura e enviar resultados para uma única planilha online.

O Apps Script utiliza mecanismo de bloqueio para reduzir conflitos durante gravações simultâneas.

---

# Exportação e importação de pesquisas

O SDIP possui um formato próprio de pacote:

```text
.sdip
```

Esse pacote permite transferir uma pesquisa entre computadores.

Ele pode incluir:

* estrutura da pesquisa;
* versão;
* identificadores;
* PDF da ficha;
* mapa OMR;
* logo;
* configuração do Google Sheets;
* regras de nomeação dos PDFs.

Configurações locais do computador não são transportadas.

Exemplos:

```text
caminho do XLSX local
pasta local dos PDFs processados
```

Fluxo:

```text
Computador A
      ↓
Exportar pesquisa.sdip
      ↓
Computador B
      ↓
Importar
      ↓
Mesma estrutura da pesquisa
```

O pacote possui verificações de integridade para detectar arquivos inválidos, alterados ou corrompidos.

---

# Ficha como fonte de verdade

A estrutura da pesquisa serve de referência para todo o fluxo:

```text
Estrutura da pesquisa
        ├── PDF
        ├── Mapa OMR
        ├── Campos de preenchimento
        ├── Estrutura da planilha
        └── Regra de nomeação dos PDFs
```

Isso reduz divergências entre a ficha física e os dados armazenados.

---

# Ciclo de vida das pesquisas

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

Alterações estruturais posteriores devem gerar uma nova versão.

---

# Impressão

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
Escala automática
```

Alterações de escala podem modificar fisicamente a posição das caixas e marcadores.

---

# Digitalização

Configuração utilizada nos testes físicos:

```text
Scanner: 600 DPI
Formato: PDF
```

As páginas são corrigidas geometricamente antes da leitura OMR.

---

# Validação física

O núcleo OMR já passou por testes físicos.

## Ficha branca

Teste com duas páginas:

```text
Total: 140 caixas
Marcadas: 0
Vazias: 140
```

Resultado:

```text
0 falsos positivos
```

---

## Teste com marcações

Teste anterior:

```text
Marcações reais: 12
Marcações reconhecidas: 12
```

Resultado:

```text
12/12
100%
```

Novos testes físicos continuarão sendo realizados conforme o sistema evolui.

---

# Tecnologias

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
* Google Sheets
* Google Apps Script
* Web Apps
* JSON
* Git
* GitHub

---

# Estrutura principal

```text
SDIP/
│
├── engine/
│   ├── gerador_ficha.py
│   ├── geometria.py
│   ├── omr.py
│   ├── leitor.py
│   ├── fichas_manager.py
│   ├── google_sheets_webapp.py
│   ├── pacote_pesquisa.py
│   └── sheets.py
│
├── ui/
│   ├── main_window.py
│   ├── formulario_ficha.py
│   ├── form_panel.py
│   └── viewer.py
│
├── config/
│
├── area_omr.py
├── app.py
├── requirements.txt
└── README.md
```

---

# Componentes críticos

Os seguintes componentes fazem parte do núcleo físico já validado:

```text
engine/gerador_ficha.py
engine/geometria.py
engine/omr.py
```

Alterações nesses arquivos devem ser realizadas somente quando houver um problema comprovado por testes.

Durante a estabilização do MVP, o comportamento já validado desses componentes deve ser preservado.

---

# Instalação para desenvolvimento

## 1. Criar ambiente virtual

```powershell
python -m venv .venv
```

## 2. Ativar no PowerShell

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

## 3. Instalar dependências

```powershell
pip install -r requirements.txt
```

## 4. Executar

```powershell
python app.py
```

A pasta `.venv/` é local e não deve ser enviada ao repositório.

---

# Estado atual

## MVP implementado

* [x] Geração automática de fichas
* [x] Layout automático em duas colunas
* [x] Paginação automática
* [x] Campos personalizados de identificação
* [x] Tipos de campos de identificação
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
* [x] Google Sheets via Apps Script Web App
* [x] Validação da estrutura do Google Sheets
* [x] Uso da mesma pesquisa em diferentes computadores
* [x] Exportação de pesquisas `.sdip`
* [x] Importação de pesquisas `.sdip`
* [x] Validação de integridade dos pacotes
* [x] Proteção contra campos manuais em branco
* [x] Validação de datas em `DD/MM/AAAA`
* [x] Opção `Manter` nos campos de identificação
* [x] Definição de campos para nomear PDFs
* [x] Nome automático dos PDFs processados
* [x] Proteção contra sobrescrita dos PDFs
* [x] Pasta local de PDFs processados por pesquisa
* [x] Seleção de múltiplos PDFs
* [x] Fila sequencial de processamento
* [x] Indicador `Arquivo X de N`
* [x] Avanço automático para o próximo PDF
* [x] Bloqueio do avanço quando o salvamento falha
* [x] Finalização e aviso de fila concluída
* [x] Interface adaptada para notebooks
* [x] Painéis redimensionáveis
* [x] Visualizador de PDF com zoom
* [x] Scroll nas principais áreas da interface

---

# Etapa atual: validação do MVP

O conjunto principal de funcionalidades previstas para o MVP foi implementado.

A próxima etapa é validar o sistema em condições reais de trabalho.

## Testes pendentes

* [ ] Executar o SDIP em diferentes máquinas
* [ ] Importar a mesma pesquisa `.sdip` em mais de um computador
* [ ] Confirmar persistência do Google Sheets após fechar e abrir o programa
* [ ] Confirmar que caminhos locais não são transportados entre máquinas
* [ ] Configurar pasta de PDFs individualmente em cada computador
* [ ] Processar múltiplos PDFs em sequência
* [ ] Validar `Manter` durante uma fila real
* [ ] Validar datas
* [ ] Validar aviso de campos vazios
* [ ] Validar nomes automáticos dos PDFs
* [ ] Validar nomes duplicados `_2`, `_3`
* [ ] Validar salvamento em XLSX
* [ ] Validar salvamento em Google Sheets
* [ ] Testar envio quase simultâneo de computadores diferentes
* [ ] Alterar propositalmente um cabeçalho do Google Sheets e confirmar bloqueio
* [ ] Restaurar o cabeçalho e confirmar funcionamento
* [ ] Testar impressão A4 em 100%
* [ ] Testar scanner real em 600 DPI
* [ ] Validar ArUco
* [ ] Validar homografia
* [ ] Validar OMR
* [ ] Validar o fluxo completo com usuários reais

---

# Depois da validação

* [ ] Corrigir somente bugs comprovados nos testes
* [ ] Gerar versão estável
* [ ] Empacotar aplicação em `.exe`
* [ ] Testar o `.exe` em máquina sem ambiente Python configurado
* [ ] Criar GitHub Release
* [ ] Disponibilizar executável para download
* [ ] Disponibilizar versão institucional estável

---

# Evoluções posteriores

Itens que não fazem parte do fechamento imediato do MVP:

* [ ] Normalização avançada de identificadores
* [ ] Detecção e alerta de registros duplicados
* [ ] Revisão do comportamento de edição de rascunhos
* [ ] Governança avançada para pesquisas multiusuário
* [ ] Controle de alterações estruturais
* [ ] Refatoração técnica
* [ ] Redução de componentes excessivamente grandes
* [ ] Melhorias adicionais de UX
* [ ] Testes automatizados estruturados

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

A chave de integração utilizada pelo Google Sheets não deve ser publicada em documentação pública, exemplos ou capturas de tela.

---

# Desenvolvimento do projeto

O SDIP foi idealizado e desenvolvido por **Diogo Barbosa** como uma solução para automatizar processos relacionados a pesquisas realizadas em papel.

O projeto surgiu depois que uma necessidade prática foi apresentada no ambiente de trabalho e foi desenvolvido por iniciativa do autor como uma solução reutilizável, não limitada a uma única pesquisa ou instituição.

O projeto principal continua sendo desenvolvido separadamente, com evolução de funcionalidades, testes, documentação e novas versões.

---

# Versão institucional

Uma organização que utiliza o SDIP pode manter em seu próprio repositório uma **versão institucional estável e previamente validada**.

O repositório institucional não precisa acompanhar cada alteração realizada durante o desenvolvimento do projeto principal.

Fluxo recomendado:

```text
Projeto principal
      ↓
Desenvolvimento
      ↓
Testes
      ↓
Versão considerada estável
      ↓
Distribuição para a organização
```

Assim, a equipe pode continuar utilizando uma versão conhecida enquanto novas funcionalidades são desenvolvidas separadamente.

Uma atualização institucional pode ser realizada quando uma nova versão tiver sido testada e considerada adequada para uso.

---

# Separação dos repositórios

```text
Repositório principal
→ desenvolvimento contínuo
→ novas funcionalidades
→ testes
→ documentação
→ roadmap
→ releases

Repositório institucional
→ versão estável
→ utilização pela equipe
→ documentação de uso
→ atualização quando necessário
```

A disponibilização de uma versão institucional não exige que o repositório da organização acompanhe continuamente o repositório principal.

---

# Autoria e direitos

O SDIP foi desenvolvido por **Diogo Barbosa**.

O código-fonte, arquitetura, documentação e demais componentes originais do projeto permanecem vinculados à autoria de seu desenvolvedor, observadas eventuais disposições legais ou contratuais aplicáveis.

A disponibilização gratuita de uma versão para utilização por uma instituição não implica, por si só, cessão do desenvolvimento contínuo ou dos direitos sobre o projeto principal.

Não é autorizada a venda, relicenciamento, apropriação da autoria ou exploração comercial do código por terceiros sem autorização expressa do autor.

O objetivo atual do projeto é disponibilizar uma solução útil para instituições que precisem transformar pesquisas físicas em dados estruturados, sem finalidade comercial por parte do autor.

**Todos os direitos reservados.**

---

# Política de versões

* O repositório principal recebe o desenvolvimento contínuo.
* Alterações em desenvolvimento permanecem no projeto principal.
* Versões destinadas aos usuários devem passar por validação antes da distribuição.
* Repositórios institucionais podem permanecer em uma versão estável.
* Não é necessário atualizar instalações institucionais a cada commit.
* Novas versões estáveis podem ser publicadas através do GitHub Releases.
* Uma instalação institucional pode ser atualizada quando houver necessidade ou quando uma nova versão tiver sido aprovada.

---

# Objetivo

O SDIP busca reduzir etapas manuais deste processo:

```text
criação
+
impressão
+
preenchimento manual
+
digitalização
+
interpretação
+
digitação
+
organização
```

transformando-o em:

```text
criar
→ imprimir
→ preencher
→ escanear
→ processar
→ conferir
→ salvar
```

O objetivo é preservar a flexibilidade das pesquisas em papel enquanto reduz o trabalho necessário para transformar as respostas em dados estruturados e utilizáveis.

---

# Autor

**Diogo Barbosa**

SDIP — Sistema de Digitalização Inteligente de Pesquisas
