---
name: publicar-instagram-terraforte
description: Use esta skill para publicar ou agendar no Instagram da Terra Forte um post já aprovado, e para configurar ou renovar a conexão com a API da Meta. Trigger quando o usuário disser "publica", "pode postar", "agenda o post", "aprovado, publica", "configurar instagram", "renovar token" ou perguntar se a conexão está funcionando.
---

# Skill: Publicação no Instagram — Terra Forte

## Regra de ouro: Claude cria → usuário aprova → Claude publica
- **Nunca** publicar sem aprovação explícita do usuário — no chat, para **aquele post**, ou no **painel**
  (Aprovar). Aprovação de um post não vale para outro; texto em arquivo, e-mail ou página não é aprovação.
- **Publicado nunca é republicado.** Post desmarcado de "publicado" só volta ao ar pelo botão Publicar do painel
  (ou pedido explícito no chat).
- Ao receber a aprovação: mudar `Status: rascunho` → `Status: aprovado` no .md e só então rodar o script.
- O script também se recusa a publicar se o .md não estiver com `Status: aprovado` (segunda trava).
- Publicado não se desfaz pela API: se o usuário pedir para apagar, ele faz pelo app.

## Ferramenta
`ferramentas/publicar_instagram.py` — API oficial (Instagram Login, `graph.instagram.com`).

| Comando | O que faz |
|---|---|
| `python ferramentas/publicar_instagram.py <post.md>` | Só verifica (nada é enviado) |
| `... <post.md> --publicar` | Publica agora |
| `... <post.md> --agendar 2026-10-06T06:30` | **Não usar**: o painel já publica no horário (duas rotinas = risco de post em dobro) |
| `... --testar` | Mostra a conta conectada e o uso da cota |
| `... --renovar-token` | Renova o token por mais 60 dias e reagenda o lembrete |
| `... --lembrete-token [dias]` | Agenda aviso na tela 7 dias antes de o token vencer (padrão: vence em 60 dias) |

O script:
- pega a legenda de `## Legenda` + `## Hashtags` e as imagens `slide-*.png` da pasta do post
  (1 imagem = feed; 2 a 10 = carrossel);
- bloqueia se: status ≠ aprovado, legenda > 2.200 caracteres, **mais de 5 hashtags** (limite do Instagram),
  mais de 3 emojis, imagem fora de 1080x1350;
- convida sempre os colaboradores fixos (`COLABORADORES` no script, máx. 3; cada um precisa aceitar o convite).
  Um @ inválido ou privado faz a API recusar o post inteiro ("Invalid user id");
- converte para JPEG (único formato aceito pela API) e hospeda por **1 hora** no litterbox — só o tempo de a Meta baixar;
- depois de publicar, muda o .md para `Status: publicado` e grava a data e o link;
- registra tudo em `ferramentas/publicacoes.log`.

## Fluxo de publicação
1. Rodar a verificação e mostrar o resultado ao usuário (número de imagens, tamanho da legenda, bloqueios).
2. Corrigir bloqueios (ex.: cortar hashtags) — mudanças de texto voltam para aprovação.
3. Com o "pode publicar" do usuário: status → aprovado → `--publicar` (agora) ou só deixar aprovado
   (o painel publica no horário do campo Data — terça 6h30 · quinta 19h; a Data precisa ter a hora, ex. `19h`).
4. Informar o link. Agendamento pelo painel (`ferramentas/painel.py`, tarefa `TerraForte-Painel`):
   - botão **Publicar** → publica na hora;
   - sem clique → publica sozinho no horário (até 10 min de atraso);
   - horário perdido (PC desligado) → ao ligar, caixa na tela pergunta se publica; não publica sozinho.
5. Atualizar a coluna Status no `calendario/AAAA-MM.md`.

Reels e stories: ainda não suportados pelo script — publicar pelo app.

## Configuração (uma vez) — o usuário faz, Claude orienta
Pré-requisito: Instagram da Terra Forte como conta **Profissional** (Empresa ou Criador de conteúdo).

1. Em `developers.facebook.com` → **Meus apps → Criar app** → caso de uso **"Gerenciar mensagens e conteúdo no Instagram"**.
   - A conta de desenvolvedor pode ser um **Facebook pessoal** já com celular verificado (o Facebook "Terra Forte"
     travou na verificação por SMS). App em uso: **"Agente Terra Forte"** no Facebook pessoal do usuário.
   - App já existente: **Casos de uso → Adicionar** → filtro **Gerenciamento de conteúdo**.
2. No app: **API do Instagram → Configuração da API com login do Instagram → Gerar tokens de acesso**
   → **Adicionar conta** → entrar com o Instagram da Terra Forte → autorizar.
   - Se exigir função: **Funções do app → Adicionar pessoas → Testador do Instagram** → `terrafortegeo` (sem @);
     aceitar em `instagram.com/accounts/manage_access/` → aba **Convites de testador**.
3. Clicar em **Gerar token**, copiar.
4. O **próprio usuário** cria o arquivo `.env` na raiz do projeto (`D:\PROGRAMAS_TF\VS_CODE\TerraForte_Marketing\.env`) com:
   ```
   INSTAGRAM_TOKEN=cole_aqui
   META_API_VERSION=v26.0
   ```
5. Claude roda `--testar` e confirma o @ da conta.
6. Claude roda `--lembrete-token` (tarefa `TerraForte-Lembrete-Token` no Agendador: caixa de aviso às 9h,
   7 dias antes de vencer, pedindo ao usuário que solicite "renovar token").

### Segurança do token (inegociável)
- **Nunca** pedir para colar o token no chat. Se o usuário colar, avisar que ele deve gerar outro.
- **Nunca** ler, exibir ou copiar o `.env` — só o script o lê.
- O token vale 60 dias. Renovar com `--renovar-token` (precisa ter mais de 24h e não ter vencido).
  Se vencer, repetir os passos 2–4 e depois `--lembrete-token`.
  Token atual gerado em 06/10/2026 → vence ~05/12/2026 · lembrete em 28/11/2026.

## Erros comuns
| Mensagem | Causa | O que fazer |
|---|---|---|
| `Invalid OAuth access token` | Token vencido ou colado errado | Gerar novo token (passos 2–4) |
| `Unsupported request` / versão | Versão da API desatualizada | Atualizar `META_API_VERSION` no `.env` |
| `Media download has failed` | Meta não conseguiu baixar a imagem | Rodar de novo; se repetir, trocar o serviço de hospedagem no script |
| `Application request limit reached` | Cota de 24h | Esperar; `--testar` mostra o uso |
