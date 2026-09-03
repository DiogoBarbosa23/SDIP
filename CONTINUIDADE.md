# CONTINUIDADE — SDIP

## Sistema de Digitalização Inteligente de Pesquisas

Este arquivo registra o estado técnico atual do SDIP e deve ser usado como ponto de retomada do desenvolvimento.

Antes de qualquer alteração relevante:

1. ler este arquivo;
2. consultar o `README.md`;
3. verificar o código atual;
4. executar `git status`;
5. verificar os últimos commits;
6. não reconstruir arquivos a partir de versões antigas;
7. preservar funcionalidades já validadas;
8. corrigir apenas problemas comprovados durante a estabilização do MVP.

---

# 1. Estado atual

O **MVP funcional do SDIP está implementado**.

Último commit remoto confirmado antes das alterações atuais:

```text
Branch: main

91c2a6c Remove testes e diagnosticos obsoletos
```

Depois desse commit foi feita uma limpeza adicional, ainda a ser registrada no Git, removendo resíduos da arquitetura antiga de mapeamento manual/global:

```text
config/mapa_caixas.json        → removido
config/mapa_caixas_gerado.json → removido
engine/omr.py                  → fallback global removido
teste_gerador_ficha.py         → mapa de teste movido para temp/
```

A remoção foi validada por:

* compilação de `engine/omr.py` e `teste_gerador_ficha.py`;
* verificação de todas as chamadas de `OMRReader`;
* confirmação de que todas passam `mapa_path` explicitamente;
* busca global por referências aos mapas antigos;
* geração de ficha de teste;
* geração do mapa de teste em `temp/`;
* teste de `Onde devo marcar?`;
* leitura OMR;
* salvamento em planilha local;
* arquivamento local;
* repetição do fluxo depois que os JSONs antigos já haviam sido removidos.

O comportamento atual está correto:

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

Não existe mais dependência funcional de:

```text
config/mapa_caixas.json
```

A pasta `config/` antiga ficou sem função e foi removida.

---

# 2. Situação da distribuição Windows

Uma primeira build utilizando PyInstaller chegou a ser gerada e executada localmente.

Estrutura utilizada:

```text
dist/
└── SDIP/
    ├── SDIP.exe
    ├── MANUAL_USUARIO_SDIP.pdf
    └── _internal/
```

Comando utilizado na primeira tentativa:

```powershell
pyinstaller --noconfirm --clean --windowed --onedir --name SDIP --collect-all customtkinter app.py
```

O executável abriu corretamente e também funcionou depois de compactado e extraído em outra pasta local.

Entretanto, durante a validação de segurança, o executável gerado recebeu detecções heurísticas de alguns mecanismos antivírus.

O arquivo **não foi publicado como Release**.

A build anterior foi descartada e o projeto foi recuperado novamente a partir do código-fonte armazenado no GitHub.

O código-fonte baixado do GitHub não apresentou a mesma detecção local.

A próxima build deverá ser feita novamente em ambiente virtual limpo.

Comando planejado:

```powershell
pyinstaller --noconfirm --clean --windowed --onedir --noupx --name SDIP --collect-all customtkinter app.py
```

Depois da geração:

1. verificar o executável localmente;
2. calcular o hash SHA-256;
3. realizar nova análise do executável;
4. somente distribuir caso o resultado seja considerado aceitável;
5. não criar exceção no antivírus apenas para forçar a execução;
6. não publicar a build anterior.

---

# 3. Objetivo do projeto

O SDIP é uma aplicação desktop em Python para automatizar:

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
leitura OMR
        ↓
conferência
        ↓
estruturação dos dados
        ↓
salvamento
        ↓
arquivamento do PDF
```

O sistema foi criado para permitir que pesquisas em papel sejam convertidas em dados estruturados sem que o usuário precise compreender:

* coordenadas;
* ArUco;
* homografia;
* OMR;
* thresholds;
* estrutura interna do mapa.

---

# 4. Tecnologias atuais

Ambiente principal:

```text
Windows
Python 3.13.x
.venv
```

Principais tecnologias:

* Python;
* CustomTkinter;
* Tkinter;
* OpenCV;
* ArUco;
* NumPy;
* Pillow;
* PyMuPDF;
* homografia;
* OMR;
* XLSX;
* Google Sheets;
* Google Apps Script;
* JSON;
* Git;
* GitHub.

A integração atual com Google Sheets **não utiliza mais**:

```text
gspread
google-auth
Service Account
credentials.json
```

Ela utiliza Google Apps Script publicado como Web App.

---

# 5. Estrutura principal

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
├── documentacao.md
├── CONTINUIDADE.md
├── requirements.txt
└── README.md
```

A pasta antiga `config/` não faz mais parte da arquitetura atual.

---

# 6. Regra de desenvolvimento durante estabilização

Até concluir os testes reais do MVP:

**não refatorar código funcional apenas por organização.**

Alterações permitidas:

* bugs comprovados;
* erros que bloqueiem o fluxo;
* correções exigidas pelos testes reais;
* ajustes mínimos necessários para empacotamento/distribuição.

Não realizar agora:

* reorganização arquitetural ampla;
* divisão de arquivos apenas porque ficaram grandes;
* criação de abstrações sem necessidade;
* troca de soluções já validadas;
* otimizações sem problema demonstrado.

A limpeza do mapeamento OMR legado foi uma exceção deliberada e limitada, porque os arquivos haviam sido comprovadamente substituídos pela arquitetura atual e todos os usos foram verificados antes da remoção.

---

# 7. Componentes críticos protegidos

Os arquivos abaixo formam o núcleo físico já validado:

```text
engine/gerador_ficha.py
engine/geometria.py
engine/omr.py
```

Eles não devem ser modificados antes dos testes reais, exceto se existir um bug reproduzível ou uma alteração mínima previamente verificada e autorizada.

Parâmetros OMR atualmente validados:

```text
Margem interna: 7 px
Threshold de pixel escuro: 150
Limiar de marcação: 5%
```

Resolução normalizada:

```text
1191 × 1684
```

ArUco:

```text
DICT_4X4_50
```

OpenCV validado:

```text
4.12.0
```

---

# 8. Arquitetura atual do mapa OMR

Cada ficha possui seu próprio mapa:

```text
fichas/
└── <ficha_id>/
    └── mapa_omr.json
```

O fluxo atual passa o caminho do mapa explicitamente.

Em `engine/omr.py`, o construtor passou de:

```python
def __init__(
    self,
    mapa_path="config/mapa_caixas.json",
    margem=7
):
```

para:

```python
def __init__(
    self,
    mapa_path,
    margem=7
):
```

Todas as chamadas encontradas de `OMRReader` fornecem `mapa_path`.

Foram verificadas chamadas em:

```text
engine/leitor.py
teste_omr_2.py
teste_omr_margem7.py
```

Não reintroduzir um mapa global padrão.

---

# 9. Limpeza da arquitetura OMR antiga

Arquivos removidos:

```text
config/mapa_caixas.json
config/mapa_caixas_gerado.json
```

## `config/mapa_caixas.json`

Era um mapa global/manual proveniente da arquitetura antiga.

O fluxo atual não o utilizava.

A aplicação foi executada e testada depois da remoção.

Resultados:

```text
Onde devo marcar? → OK
OMR               → OK
Salvamento        → OK
```

## `config/mapa_caixas_gerado.json`

Era utilizado apenas como saída do script de teste:

```text
teste_gerador_ficha.py
```

O destino foi alterado para:

```text
temp/mapa_caixas_gerado.json
```

O script foi executado depois da alteração.

Resultado:

```text
TESTE CONCLUÍDO

Páginas geradas:
- temp\ficha_teste_layout_1.png

Mapa OMR gerado:
- temp/mapa_caixas_gerado.json

Quantidade de páginas: 1
Caixas OMR registradas: 50
```

A referência utilizada por `teste_omr_margem7.py` já apontava para `temp/`.

---

# 10. Validação física já realizada

## Ficha branca de duas páginas

```text
Total de caixas: 140
Marcadas: 0
Vazias: 140
```

Resultado:

```text
0 falsos positivos
```

## Teste físico anterior

```text
Marcações reais: 12
Marcações reconhecidas: 12
```

Resultado:

```text
12/12
100%
```

Esses resultados não substituem a nova validação nas máquinas e no fluxo real de trabalho.

---

# 11. Criação de pesquisas

O editor permite configurar:

* nome da pesquisa;
* título;
* logo;
* tamanho da fonte;
* campos de identificação;
* tipos dos campos;
* campos de data;
* seções;
* perguntas fechadas;
* respostas únicas;
* respostas múltiplas;
* perguntas abertas;
* opções;
* campos utilizados para nomear o PDF.

O sistema gera automaticamente:

* layout;
* duas colunas;
* paginação;
* caixas OMR;
* ArUcos;
* coordenadas;
* mapa OMR;
* áreas de perguntas abertas;
* cabeçalho;
* PDF.

---

# 12. Rascunho, produção e versão

Fluxo conceitual:

```text
RASCUNHO
    ↓
geração
    ↓
validação
    ↓
PRODUÇÃO
```

Uma ficha em produção representa uma estrutura de coleta já definida.

Alterações estruturais posteriores devem gerar:

```text
NOVA VERSÃO
```

A nova versão:

* mantém o `pesquisa_id`;
* incrementa a versão;
* registra a versão anterior;
* volta para RASCUNHO;
* não reutiliza automaticamente a planilha da versão anterior.

---

# 13. Planilha XLSX

O destino local continua disponível.

A estrutura é derivada diretamente da ficha:

```text
campos de identificação
        ↓
perguntas
```

Seções não geram colunas.

Cada ficha processada gera uma nova linha.

A planilha possui:

* cabeçalho fixo;
* primeira linha congelada;
* filtros;
* largura de colunas;
* tratamento de dados;
* compatibilidade com Excel.

A ficha é a fonte de verdade da estrutura tabular.

---

# 14. Google Sheets

Integração implementada através de:

```text
Google Sheets
        +
Google Apps Script
        +
Web App
```

Arquivo:

```text
engine/google_sheets_webapp.py
```

Fluxo:

```text
usuário cria Google Sheet
        ↓
SDIP gera chave + Apps Script
        ↓
usuário publica como Web App
        ↓
obtém URL /exec
        ↓
SDIP testa conexão
        ↓
SDIP vincula pesquisa
```

A aplicação utiliza:

* chave de integração;
* URL do Web App;
* cabeçalhos esperados;
* validação de estrutura antes de inserir registros.

A implementação utiliza a biblioteca padrão `urllib`.

Não depende de faturamento do Google Cloud.

---

# 15. Proteção da estrutura do Google Sheets

Antes do salvamento, o SDIP compara:

```text
estrutura esperada
        ×
estrutura encontrada
```

São validados:

* títulos;
* quantidade;
* ordem das colunas.

Se houver divergência:

```text
salvamento bloqueado
```

O sistema apresenta diagnóstico em vez de gravar dados em colunas incorretas.

Esse comportamento já foi testado alterando propositalmente cabeçalhos.

---

# 16. Uso em vários computadores

O Google Sheets permite:

```text
Máquina A ─┐
           │
Máquina B ─┼──→ mesma planilha
           │
Máquina C ─┘
```

O Apps Script utiliza `LockService` para reduzir conflitos em gravações concorrentes.

Ainda precisa ser validado em máquinas físicas diferentes no ambiente de trabalho.

---

# 17. Pacotes `.sdip`

Foi implementada exportação/importação de pesquisas através do formato:

```text
.sdip
```

Arquivo:

```text
engine/pacote_pesquisa.py
```

O pacote preserva:

* `ficha_id`;
* `pesquisa_id`;
* versão;
* estrutura;
* PDF;
* mapa OMR;
* logo;
* configuração Google;
* regra de nomeação dos PDFs.

Configurações específicas do computador não devem viajar no pacote.

Exemplos:

```text
caminho do XLSX local
pasta dos PDFs processados
```

Também existem verificações contra:

* pacote inválido;
* corrupção;
* pesquisa duplicada;
* ficha duplicada.

---

# 18. Campos manuais vazios

Antes de salvar, o SDIP verifica:

* campos de identificação;
* perguntas abertas.

Se existirem campos vazios:

```text
uma única confirmação
        ↓
lista todos os campos vazios
```

Escolha `Não`:

```text
não salva
não perde os dados
```

Escolha `Sim`:

```text
salva mesmo com campos vazios
```

Perguntas OMR sem marcação não entram nessa confirmação.

---

# 19. Datas

Campos configurados como data utilizam:

```text
DD/MM/AAAA
```

O SDIP valida:

* formato;
* ano com quatro dígitos;
* dia;
* mês;
* existência real da data.

Data preenchida de forma inválida bloqueia o salvamento.

Campo de data vazio continua permitido mediante a confirmação de campos manuais vazios.

---

# 20. Opção Manter

Campos de identificação possuem:

```text
[ ] Manter
```

Depois de um salvamento bem-sucedido:

```text
campo marcado como Manter
→ permanece preenchido

campo não marcado
→ é limpo

pergunta aberta
→ é limpa
```

A configuração é temporária da sessão.

Ela não altera:

* ficha;
* `.sdip`;
* XLSX;
* Google Sheets.

---

# 21. Nome automático do PDF

Durante a criação da pesquisa, campos de identificação podem receber:

```text
[ ] Nome do PDF
```

Os campos selecionados definem o nome do PDF processado.

Exemplo:

```text
Código = 00152
Nome = Maria Silva
```

Resultado:

```text
00152_Maria Silva.pdf
```

Regras:

* vários campos são permitidos;
* ordem igual à ordem do cabeçalho;
* campos vazios são ignorados;
* se todos estiverem vazios, usa o nome original;
* caracteres inválidos do Windows são tratados;
* arquivos nunca são sobrescritos.

Colisões:

```text
arquivo.pdf
arquivo_2.pdf
arquivo_3.pdf
```

---

# 22. Pasta dos PDFs processados

Cada pesquisa possui uma pasta de destino configurada localmente em cada computador.

A configuração não é incluída no `.sdip`.

Persistência local:

```text
%LOCALAPPDATA%\SDIP\config_local.json
```

com fallback local quando necessário.

A configuração é associada ao `pesquisa_id`.

Pode ser utilizada uma pasta de rede.

Se o destino estiver indisponível:

```text
solicitar outro local

ou

cancelar
```

Nunca salvar silenciosamente em outro lugar.

---

# 23. Segurança do salvamento

O salvamento combina:

```text
registro de dados
        +
arquivamento do PDF processado
```

Em caso de falha de persistência:

* não avançar;
* manter os dados;
* manter o resultado OMR;
* evitar cópia órfã do PDF;
* permitir correção e nova tentativa.

---

# 24. Fila de múltiplos PDFs

A seleção utiliza múltiplos arquivos:

```text
Selecionar ficha(s) PDF
```

É possível selecionar:

```text
1 PDF

ou

vários PDFs
```

Com vários arquivos:

```text
Arquivo 1 de N
Arquivo 2 de N
Arquivo 3 de N
...
```

Fluxo:

```text
selecionar PDFs
        ↓
carregar primeiro
        ↓
Ler ficha (OMR)
        ↓
conferir
        ↓
salvar
        ↓
dados + PDF concluídos
        ↓
carregar próximo automaticamente
```

O OMR **não roda automaticamente** no próximo arquivo.

O operador precisa clicar novamente:

```text
Ler ficha (OMR)
```

A fila só avança depois de um salvamento completo.

---

# 25. Situações em que a fila não avança

Não avançar quando houver:

* data inválida;
* cancelamento;
* recusa da confirmação de campos vazios;
* erro no XLSX;
* erro no Google Sheets;
* erro na pasta dos PDFs;
* erro no arquivamento;
* qualquer falha de salvamento.

Depois do último arquivo:

```text
Fila concluída
```

---

# 26. Interface

A interface foi reorganizada para notebooks e janelas menores.

Configuração principal:

```text
geometry: 1200x750
minsize: 1000x600
```

## Digitalizar

Estrutura aproximada:

```text
PDF | formulário / ações
```

Divisor redimensionável.

## Criar / Editar

Estrutura aproximada:

```text
configurações | estrutura da ficha
```

Divisor redimensionável.

O botão `Salvar resultado` permanece acessível na parte superior da área operacional.

---

# 27. Visualizador

O visualizador suporta:

* ajuste automático;
* zoom;
* aumentar;
* diminuir;
* faixa aproximada de 50% a 300%;
* scroll;
* redimensionamento;
* navegação multipágina.

O arquivo `ui/viewer.py` pode ser revisado futuramente, mas **não deve ser refatorado antes da validação do MVP**.

---

# 28. Onde devo marcar?

A funcionalidade:

```text
Onde devo marcar?
```

continua integrada ao produto.

Ela exibe visualmente a região efetivamente analisada pelo OMR.

O destaque vermelho:

```text
aparece apenas na visualização
```

Não modifica:

* PDF original;
* ficha impressa.

Arquivo:

```text
area_omr.py
```

---

# 29. Funcionalidades consideradas concluídas no MVP

```text
[x] geração automática de fichas
[x] layout automático
[x] paginação
[x] seções
[x] perguntas únicas
[x] perguntas múltiplas
[x] perguntas abertas
[x] cabeçalho configurável
[x] campos de data
[x] logo
[x] fonte configurável
[x] ficha ativa
[x] RASCUNHO / PRODUÇÃO / versões
[x] ArUco
[x] homografia
[x] normalização
[x] mapa OMR automático por ficha
[x] leitura OMR
[x] Onde devo marcar?
[x] XLSX
[x] vínculo ficha → planilha
[x] Google Sheets
[x] validação estrutural Google Sheets
[x] .sdip
[x] importação/exportação entre computadores
[x] alerta de campos manuais vazios
[x] validação de data
[x] Manter
[x] Nome do PDF
[x] arquivamento do PDF processado
[x] proteção contra sobrescrita
[x] pasta local de processados
[x] seleção de vários PDFs
[x] fila de processamento
[x] avanço automático
[x] proteção contra avanço em erro
[x] interface adaptada para notebooks
[x] manual do usuário
[x] manual em PDF
[x] guia visual rápido
[x] remoção do mapeamento OMR global legado
```

---

# 30. Testes ainda obrigatórios

O MVP está funcionalmente implementado, mas ainda precisa ser validado no ambiente real.

## Distribuição Windows

```text
[ ] instalar PyInstaller no novo .venv
[ ] gerar nova build com --noupx
[ ] analisar novo executável
[ ] confirmar que a build é adequada para distribuição
[ ] testar ZIP extraído em pasta diferente
[ ] executar em máquina sem Python instalado
```

## Máquinas do trabalho

```text
[ ] importar .sdip
[ ] fechar e abrir novamente
[ ] Google Sheets continuar vinculado
[ ] Google Sheets receber registros
[ ] duas máquinas usarem a mesma pesquisa
[ ] caminhos locais permanecerem independentes
[ ] pasta de PDFs ser configurada individualmente
```

## Fluxo físico

```text
[ ] imprimir A4 em 100%
[ ] preencher manualmente
[ ] digitalizar em 600 DPI
[ ] detectar ArUcos
[ ] aplicar homografia
[ ] executar OMR
[ ] validar respostas
[ ] validar perguntas abertas
[ ] validar campos manuais
[ ] salvar
[ ] conferir planilha
[ ] conferir PDF arquivado
```

## Fila

```text
[ ] selecionar vários PDFs reais
[ ] confirmar ordem
[ ] validar Arquivo X de N
[ ] salvar arquivo atual
[ ] confirmar avanço
[ ] confirmar Manter
[ ] confirmar limpeza dos demais campos
[ ] validar último arquivo
[ ] confirmar Fila concluída
```

## Falhas

```text
[ ] Google indisponível
[ ] cabeçalho Google alterado
[ ] XLSX indisponível
[ ] pasta de PDFs indisponível
[ ] data inválida
[ ] campos vazios
[ ] PDF inválido
[ ] PDF sem ArUco
[ ] página faltando
[ ] arquivo duplicado
```

---

# 31. Próximas etapas imediatas

A sequência atual é:

```text
1. concluir a limpeza documental atual
2. revisar git diff e git status
3. registrar a limpeza do mapeamento legado em commit
4. enviar o commit para origin/main
5. confirmar ambiente virtual limpo
6. instalar PyInstaller
7. gerar nova build Windows com --noupx
8. analisar o novo executável antes da distribuição
9. testar a build localmente
10. compactar a pasta dist/SDIP/
11. testar o ZIP extraído
12. somente então criar Release de teste
13. baixar na máquina do trabalho
14. executar checklist real
15. corrigir somente bugs comprovados
16. gerar build estável
17. publicar Release estável
```

---

# 32. Empacotamento Windows

A distribuição continuará utilizando inicialmente:

```text
onedir
```

em vez de `onefile`.

Objetivo:

```text
dist/
└── SDIP/
    ├── SDIP.exe
    └── _internal/
```

O diretório inteiro deverá ser distribuído.

Não copiar somente `SDIP.exe`.

Nova tentativa planejada:

```powershell
pyinstaller --noconfirm --clean --windowed --onedir --noupx --name SDIP --collect-all customtkinter app.py
```

Depois do build, copiar o manual:

```powershell
Copy-Item .\docs\MANUAL_USUARIO_SDIP.pdf .\dist\SDIP\
```

Verificar hash:

```powershell
Get-FileHash .\dist\SDIP\SDIP.exe -Algorithm SHA256
```

Não distribuir um executável que ainda esteja sob dúvida de segurança.

---

# 33. Primeira build descartada

A primeira build:

* foi gerada com PyInstaller;
* utilizou `onedir`;
* abriu localmente;
* funcionou quando compactada e extraída;
* não chegou a ser publicada.

Durante a análise, alguns mecanismos apresentaram detecções heurísticas/genéricas.

A decisão foi:

```text
não liberar
não ignorar o alerta
não criar exceção apenas para executar
descartar a build
recriar o ambiente
gerar nova build
reanalisar
```

O código-fonte obtido novamente do GitHub permaneceu como base confiável para a nova tentativa.

---

# 34. GitHub Release

O Release é diferente do executável.

```text
EXE
→ programa gerado

GitHub Release
→ forma de distribuir uma versão desse programa
```

Fluxo:

```text
código
    ↓
PyInstaller
    ↓
dist/SDIP/
    ↓
análise da build
    ↓
teste local
    ↓
ZIP
    ↓
GitHub Release de teste
    ↓
download na máquina do trabalho
```

Somente depois da validação real deverá ser publicada uma versão considerada estável.

---

# 35. Repositórios

Estratégia:

```text
Repositório pessoal
→ projeto principal
→ desenvolvimento
→ histórico
→ releases

Repositório institucional
→ versão estável aprovada
→ documentação institucional
→ atualização quando necessário
```

O repositório institucional não precisa acompanhar cada commit do desenvolvimento principal.

---

# 36. Segurança e dados

Nunca publicar:

* dados pessoais;
* PDFs reais com informações pessoais;
* resultados de pesquisas reais;
* tokens;
* chaves expostas em documentação;
* `.env`;
* `.venv`;
* arquivos temporários;
* credenciais.

A chave de integração do Google Sheets deve ser tratada como informação operacional da pesquisa.

---

# 37. Autoria e distribuição

O SDIP foi desenvolvido por **Diogo Barbosa**.

O projeto surgiu a partir de uma necessidade prática apresentada no ambiente de trabalho, mas o projeto principal é mantido separadamente pelo autor.

A documentação deve preservar a distinção entre:

```text
autoria/desenvolvimento principal
        e
versão institucional disponibilizada para uso
```

Questões patrimoniais continuam sujeitas às disposições legais e contratuais aplicáveis.

Não utilizar licença permissiva automaticamente sem uma decisão explícita sobre a política futura de distribuição do código-fonte.

---

# 38. Itens posteriores ao MVP

Não são prioridade durante a validação atual:

* normalização avançada de identificadores;
* detecção de registros duplicados;
* governança multiusuário avançada;
* votação/aprovação de alterações estruturais;
* revisão do comportamento de rascunhos;
* refatoração do `main_window.py`;
* refatoração do `viewer.py`;
* reorganização arquitetural;
* testes automatizados completos;
* otimizações não necessárias;
* melhorias cosméticas sem impacto operacional.

---

# 39. Regra de correção

Durante os testes:

```text
problema observado
        ↓
reproduzir
        ↓
identificar arquivo responsável
        ↓
avaliar se componente já foi validado
        ↓
propor alteração mínima
        ↓
autorizar
        ↓
alterar
        ↓
testar
        ↓
commit
```

Nunca modificar o núcleo apenas por suspeita.

---

# 40. Workflow para alterações de código

Antes de gerar código:

1. listar objetivamente todas as mudanças propostas;
2. identificar arquivos afetados;
3. explicar o motivo;
4. aguardar autorização.

Depois da autorização:

1. trabalhar sobre o código atual;
2. gerar arquivos completos quando a alteração for relevante;
3. evitar blocos parciais que possam causar substituições incorretas;
4. não modificar áreas fora do escopo;
5. testar a mudança;
6. revisar o diff;
7. registrar em commit.

---

# 41. Regra para arquivos críticos

Não alterar sem problema comprovado:

```text
engine/gerador_ficha.py
engine/geometria.py
engine/omr.py
```

Exceções precisam ser:

* pequenas;
* justificadas;
* verificadas contra todos os usos;
* testadas antes e depois;
* registradas claramente.

A alteração atual em `engine/omr.py` atende a esses critérios porque removeu somente o fallback para um mapa antigo comprovadamente não utilizado.

---

# 42. Testes regressivos mantidos

Depois da limpeza de testes obsoletos, continuam relevantes:

```text
teste_gerador_ficha.py
teste_omr_2.py
teste_omr_margem7.py
```

O `teste_gerador_ficha.py` agora escreve seu mapa de teste em:

```text
temp/mapa_caixas_gerado.json
```

O diretório `temp/` não faz parte da arquitetura permanente do produto.

---

# 43. Estado de retomada — 03/09/2026

Ao retomar o projeto, verificar primeiro:

```powershell
git status
git log --oneline -5
```

As alterações atuais esperadas antes do próximo commit são:

```text
deleted:    config/mapa_caixas.json
deleted:    config/mapa_caixas_gerado.json
modified:   engine/omr.py
modified:   teste_gerador_ficha.py
modified:   README.md
modified:   documentacao.md
modified:   CONTINUIDADE.md
```

Antes do commit:

1. executar `git diff --stat`;
2. conferir que não existem mudanças fora do escopo;
3. executar uma última busca por referências antigas;
4. confirmar que o aplicativo continua abrindo;
5. somente então registrar a limpeza.

Mensagem de commit sugerida:

```text
Remove residuos do mapeamento OMR legado
```

Como o repositório local foi reconectado ao remoto depois de um Download ZIP, confirmar o upstream.

Se necessário:

```powershell
git push -u origin main
```

---

# 44. Ponto exato atual

O MVP funcional está implementado.

A arquitetura antiga de mapas OMR globais foi removida e funcionalmente validada.

A primeira build Windows foi descartada antes de qualquer Release após apresentar detecções heurísticas que exigem nova validação.

O código-fonte atual foi recuperado novamente a partir do GitHub e está sendo utilizado em ambiente virtual novo.

O próximo marco é:

```text
fechar a limpeza atual no Git
        ↓
gerar nova build Windows
        ↓
validar segurança
        ↓
testar localmente
        ↓
Release de teste
        ↓
teste real no trabalho
```

Até concluir essa etapa, manter a regra:

**nenhuma refatoração ampla e nenhuma alteração no núcleo sem um problema reproduzível.**
