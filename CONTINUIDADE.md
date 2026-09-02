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

Estado do Git após o fechamento das funcionalidades:

```text
Branch: main
Último commit funcional/documentação:
63701d7 Adiciona fila de PDFs e atualiza documentacao
```

Estado confirmado:

```text
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

O projeto está entrando na fase de:

```text
MVP implementado
        ↓
build do executável
        ↓
testes nas máquinas do trabalho
        ↓
correção apenas de bugs comprovados
        ↓
versão estável
        ↓
GitHub Release
```

---

# 2. Objetivo do projeto

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

# 3. Tecnologias atuais

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

# 4. Estrutura principal

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
├── config/
├── area_omr.py
├── app.py
├── requirements.txt
├── README.md
└── CONTINUIDADE.md
```

---

# 5. Regra de desenvolvimento durante estabilização

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

---

# 6. Componentes críticos protegidos

Os arquivos abaixo formam o núcleo físico já validado:

```text
engine/gerador_ficha.py
engine/geometria.py
engine/omr.py
```

Eles não devem ser modificados antes dos testes reais, exceto se existir um bug reproduzível.

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

# 7. Validação física já realizada

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

# 8. Criação de pesquisas

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

# 9. Rascunho, produção e versão

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

# 10. Planilha XLSX

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

# 11. Google Sheets

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

# 12. Proteção da estrutura do Google Sheets

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

# 13. Uso em vários computadores

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

# 14. Pacotes .sdip

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

# 15. Campos manuais vazios

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

# 16. Datas

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

# 17. Opção Manter

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

# 18. Nome automático do PDF

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

# 19. Pasta dos PDFs processados

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

# 20. Segurança do salvamento

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

# 21. Fila de múltiplos PDFs

Última funcionalidade obrigatória do MVP implementada.

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

# 22. Situações em que a fila não avança

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

# 23. Interface

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

# 24. Visualizador

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

# 25. Onde devo marcar?

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

# 26. Funcionalidades consideradas concluídas no MVP

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
[x] mapa OMR
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
```

---

# 27. Testes ainda obrigatórios

O MVP está funcionalmente implementado, mas ainda precisa ser validado no ambiente real.

## Máquinas do trabalho

Testar:

```text
[ ] instalar/executar build em máquina diferente
[ ] executar sem Python instalado
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

# 28. Próximas etapas imediatas

A sequência atual é:

```text
1. atualizar CONTINUIDADE.md
2. remover README_ANTIGO.md
3. salvar documentação no Git
4. gerar build Windows
5. testar localmente
6. compactar build
7. disponibilizar como Release de teste
8. baixar na máquina do trabalho
9. executar checklist real
10. corrigir somente bugs comprovados
11. gerar build estável
12. publicar Release estável
```

---

# 29. Empacotamento Windows

PyInstaller instalado no ambiente atual:

```text
PyInstaller 6.22.2
```

A primeira distribuição será testada utilizando:

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

Comando inicial planejado:

```powershell
pyinstaller --noconfirm --clean --windowed --onedir --name SDIP --collect-all customtkinter app.py
```

Esse comando ainda precisa ser executado e validado.

Antes do build, verificar se os artefatos do PyInstaller estão ignorados pelo Git:

```text
build/
dist/
*.spec
```

A decisão sobre manter ou versionar um `.spec` definitivo pode ser tomada depois que a configuração de empacotamento estiver validada.

---

# 30. GitHub Release

O Release é diferente do executável.

```text
EXE
→ programa gerado

GitHub Release
→ forma de distribuir uma versão desse programa
```

Fluxo planejado:

```text
código
    ↓
PyInstaller
    ↓
dist/SDIP/
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

# 31. Repositórios

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

# 32. Segurança e dados

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

# 33. Autoria e distribuição

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

# 34. Itens posteriores ao MVP

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

# 35. Regra de correção

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

# 36. Workflow para alterações de código

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
5. testar;
6. registrar o resultado;
7. fazer commit quando aprovado.

---

# 37. Encerramento de sessão

Antes de encerrar uma etapa importante:

```powershell
git status
```

Se aprovado:

```powershell
git add ...
git commit -m "..."
git push
```

Depois:

```powershell
git status
```

Estado ideal:

```text
nothing to commit, working tree clean
```

---

# 38. Ponto exato de retomada

Estado em **02/09/2026**:

```text
MVP funcional implementado
        ↓
item de fila de PDFs validado
        ↓
README atualizado
        ↓
código enviado ao GitHub
        ↓
PyInstaller 6.22.2 instalado
        ↓
CONTINUIDADE sendo atualizada
        ↓
próximo passo:
GERAR O EXECUTÁVEL DE TESTE
```

Antes de executar o PyInstaller:

```text
1. remover README_ANTIGO.md
2. salvar CONTINUIDADE.md
3. verificar .gitignore
4. garantir git status limpo
```

Depois:

```text
gerar build
→ testar SDIP.exe
→ compactar pasta
→ GitHub Release de teste
→ testes nas máquinas do trabalho
```

Não iniciar novas funcionalidades antes dessa validação.

---

# Autor

**Diogo Barbosa**

SDIP — Sistema de Digitalização Inteligente de Pesquisas
