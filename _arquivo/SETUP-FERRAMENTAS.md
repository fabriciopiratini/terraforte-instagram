# Setup de ferramentas — configuração única da máquina (não vai no CLAUDE.md)

Os textos que você me passou misturam três camadas. Separá-las é o segredo da eficiência:

| Camada | O quê | Onde fica |
|---|---|---|
| Infraestrutura | RTK, Headroom, GSD | Instalado 1x na máquina (hooks/CLI). **Fora** do CLAUDE.md |
| Comportamento | Princípios Karpathy, estilo conciso | `~/.claude/CLAUDE.md` (global) |
| Contexto | Stack, mapa de pastas, comandos | `CLAUDE.md` de cada projeto |

Colocar "ativar RTK" como checklist dentro do CLAUDE.md **não funciona** — o Claude lê o
arquivo, mas quem ativa essas ferramentas é a configuração da máquina, não o texto.

---

## 1. RTK (Rust Token Killer) — recomendado
Proxy que filtra/comprime a saída de comandos de terminal antes de virar contexto
(60–90% de economia em `git status`, `pytest`, `npm install`, etc.). Binário Rust único,
multiplataforma (funciona no seu Windows).

- Repo: github.com/rtk-ai/rtk
- Instala como **hook PreToolUse** no `settings.json` do Claude Code — todo comando Bash
  passa por ele automaticamente. Siga o guia de instalação do repo (NÃO é `rtk init`).
- Verifique a economia depois com: `rtk gain`

## 2. Headroom — teste com cautela (atrito no Windows)
Comprime tool outputs/logs/RAG antes de chegar ao modelo; tem `headroom learn` que escreve
correções no CLAUDE.md.
- **Caveat real:** o app desktop tem macOS como alvo estável e Linux experimental; o pacote
  `headroom-ai` (pip) compila extensão C++ (hnswlib). No Windows exige toolchain de build.
- Sugestão: só adote depois que RTK já estiver te dando ganho. Ferramenta poderosa, mas é a
  de instalação mais frágil das três no seu ambiente.

## 3. GSD (Get Shit Done) — ótimo para projetos do zero
Framework de planejamento em fases + subagentes com contexto limpo. Multiplataforma.
- Instalar: `npx get-shit-done-cc`  (depois reinicie o Claude Code)
- Use: `/gsd:help`, `/gsd:new-project`
- **Segurança:** o GSD sugere rodar com `claude --dangerously-skip-permissions`. Para você,
  que lida com matrículas, dados de clientes e processos INCRA, **evite** o skip global —
  prefira configurar permissões explícitas (ver seção 6). Conveniência não vale o risco aqui.

## 4. Karpathy Skills — JÁ embutido
Os "4 princípios" (pensar antes, simplicidade, mudança cirúrgica, critério de sucesso) são
literalmente um CLAUDE.md. Já estão no seu `CLAUDE.global.md` — não precisa instalar nada.

---

## 5. Comandos reais de sessão (higiene de contexto)
Todos confirmados no Claude Code atual:
- `/clear` — limpa a conversa ao trocar de assunto/terminar tarefa atômica. **Prefira a `/compact`.**
- `/compact` — resume e comprime o histórico (use por volta de 60–70% de ocupação).
- `/context` — mostra o uso atual do contexto.
- `/btw <pergunta>` — pergunta lateral efêmera, **não** entra no histórico. Ótimo para dúvidas rápidas.
- `/branch` (antigo `/fork`) — bifurca a conversa antes de algo arriscado.
- `/rewind` — volta a um checkpoint anterior.
- `/cost` — uso de tokens da sessão.

## 6. Exclusão de arquivos (o jeito que de fato funciona)
`.claudemrignore` e `claudemr` eu **não** consegui confirmar que existem — provável confusão
com `.geminiignore` (do Gemini CLI). Use estes mecanismos reais:

**a) `.gitignore`** — mantém dados pesados/sensíveis fora do repo:
```gitignore
data/
*.jxl
*.gpkg
*.tif
*.las
*.laz
.env
*_matricula*.pdf
```

**b) Regras de permissão no `settings.json`** do projeto (`.claude/settings.json`) —
bloqueia o Claude de ler caminhos sensíveis, independente do comando:
```json
{
  "permissions": {
    "deny": [
      "Read(./data/**)",
      "Read(./**/*.env)",
      "Read(./**/*matricula*)"
    ]
  }
}
```

## 7. Mitos corrigidos
- **"Regra das 200 linhas da Anthropic":** não é regra oficial. O limite prático útil de um
  CLAUDE.md fica em torno de **80–120 linhas** — além disso as instruções competem entre si.
- **"GLM 4.7":** a versão pública conhecida é a GLM 4.6 (Zhipu). Sem impacto para este setup.
- **Roteamento de modelo:** a ideia de usar modelo rápido/barato para 80% e reservar o mais
  forte para arquitetura/debug é sólida — no Claude Code troque com `/model` durante a sessão.
