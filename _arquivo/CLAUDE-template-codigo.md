\# ⚙️ MODO SETUP — entrevista de inicialização (apague esta seção depois de preencher)



> \*\*Instrução ao Claude:\*\* ao iniciar a sessão, se esta seção MODO SETUP ainda existir

> ou se houver `\[placeholders]` no arquivo, ANTES de qualquer outra tarefa:

>

> 1. Conduza a entrevista abaixo. Faça as perguntas em grupos curtos, \*\*uma letra de

>    cada vez\*\*, e espere minha resposta antes de seguir para a próxima.

> 2. O que você conseguir \*\*inferir lendo o repositório\*\* — linguagem, versão, estrutura

>    de pastas, scripts de build/test (`pyproject.toml`, `package.json`, `Makefile`,

>    `requirements.txt`) — detecte sozinho e apenas \*\*confirme\*\* comigo. Não pergunte o

>    que dá para descobrir no próprio repo.

> 3. Escreva minhas respostas nas seções correspondentes deste arquivo.

> 4. \*\*Apague esta seção MODO SETUP inteira\*\* e qualquer `\[placeholder]` que tenha sobrado.

> 5. Termine com um resumo de 3 linhas do que ficou registrado.

>

> \*\*Perguntas da entrevista:\*\*

> - \*\*A)\*\* Nome do projeto e objetivo em uma frase (o que faz e para quem)?

> - \*\*B)\*\* Linguagem + versão, tipo (CLI / API / lib / script / web / outro) e gerenciador

>   de pacotes? (Confirme o que você já detectou no repo.)

> - \*\*C)\*\* Posso assumir a estrutura de pastas e os comandos (instalar, rodar, testar, lint)

>   que detectei no repo? Se faltar ou estiver errado, me corrija.

> - \*\*D)\*\* Convenções obrigatórias deste projeto (estilo de código, nomes, formato de saída,

>   idioma dos comentários)?

> - \*\*E)\*\* Há dados ou arquivos sensíveis? Quais pastas/extensões nunca devem ser

>   versionadas nem lidas por você?



\---



\# \[NOME DO PROJETO]



> Os princípios de comportamento, estilo e segurança estão no `\~/.claude/CLAUDE.md` global.

> Este arquivo guarda apenas o CONTEXTO deste projeto. Alvo de tamanho: < 100 linhas.



\## Objetivo

\[Uma frase: o que este projeto faz e para quem.]



\## Stack

\- Linguagem: \[linguagem + versão]   (gerenciador: \[pip / uv / poetry / npm / ...])

\- Tipo: \[CLI / API / lib / script / web]

\- Principais libs/serviços: \[...]



\## Mapa do projeto (índice de caminhos — NÃO escaneie o repo)

\- `\[pasta]/` — \[o que contém]

\- `\[pasta]/` — \[o que contém]

\- `tests/` — testes



\## Comandos

\- Instalar deps: `\[...]`

\- Rodar: `\[...]`

\- Testar: `\[...]`

\- Lint/format: `\[...]`



\## Convenções deste projeto

\- \[Estilo de nomes, padrões de saída, idioma dos comentários...]

\- Para regras longas e estáveis, importe em vez de colar aqui:  @docs/specs.md



\## Dados sensíveis deste projeto

(A regra geral de segurança já está no global. Aqui só listamos ONDE ela se aplica neste repo.)

\- \[Pastas/extensões que ficam fora do Git e que você NÃO deve ler.]

