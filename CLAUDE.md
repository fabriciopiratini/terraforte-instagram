# Terra Forte — Gestão do Instagram

> Princípios gerais de comportamento/segurança estão no `~/.claude/CLAUDE.md` global.
> Aqui fica só o contexto da marca e do projeto. Fontes completas em `marca/`.

## Objetivo
Divulgar os serviços para captar novos clientes em Piratini e cidades da região,
criando a consciência de que **imóvel irregular é risco financeiro** — e a Terra Forte é a solução.

## Marca
- Escritório com 13 anos de experiência; tecnologia e equipamentos de última geração.
- Propósito: proteger o patrimônio do cliente — documentação que reflete a realidade física do imóvel.
- Bandeiras: capacidade técnica, credibilidade, experiência.
- Valores: confiança, conhecimento técnico, tecnologia, seriedade.

## Serviços (lista oficial)
1. Georreferenciamento (certificação INCRA)
2. Localização de parcela
3. Extinção de condomínio
4. Topografia rural e urbana
5. CAR — Cadastro Ambiental Rural
6. Detalhamento de lavoura com drone
7. Estruturação de crédito bancário
8. Regularização urbana

## Equipe (nomes autorizados em posts)
- Fabrício Lucas · Milena Lucas · Aloncio Garcia

## Fatos confirmados
- CAR é exigido para o crédito rural e para o registro do imóvel no cartório.

## Público
- 35 a 65+ anos, patrimônio consolidado: produtores rurais, proprietários de imóveis rurais/urbanos.
- Precisam regularizar para compra, venda, arrendamento, financiamento, doação, inventário.
- **Persona Antônio, 48:** prático, sem tempo para burocracia, valoriza o "aperto de mão".
  Dor: imóvel irregular travando negócios, litígio com confrontantes, perder dinheiro.
  Desejo: escritório técnico que resolva de ponta a ponta.
- **Não é público:** quem busca só o mais barato sem ligar para precisão.

## Tom de voz
- Sério, claro, acessível. Traduzir o "juridiquês" em consequência prática.
- Mensagem central: o serviço não é simples, mas temos a competência para resolver.
- Estrutura preferida: **problema do cliente → consequência → solução Terra Forte → CTA**.
- Termo técnico só quando necessário, e sempre explicado.

## Regras inegociáveis
- Proibido: gírias, política, religião.
- Nunca expor dados de clientes em posts: nomes, matrículas, CPF, coordenadas ou
  imagens que identifiquem propriedades privadas sem autorização.

## Linhas editoriais
| Linha | Função |
|---|---|
| Informativos | Criar a necessidade: mostrar o problema e a solução (inclui "Notícia do agro") |
| Bastidores | Rotina de campo e escritório; provar competência e estrutura |
| Autoridade & Eventos | 13 anos, capacidade técnica, Expointer, Expodireto, dias de campo |

**Frequência:** 2 posts por semana — terça (Informativo) e quinta (Bastidores ou Autoridade & Eventos, alternando).

## Dúvidas frequentes (fonte de pautas)
- Preciso fazer localização de parcela ou extinção de condomínio?
- Quem é obrigado a fazer georreferenciamento?
- Preciso de CAR?
- Como obter registro por usucapião?
- Quanto custa? (orçamento)

## Mapa de pastas
- `marca/` — Manual de Voz e Planejamento Estratégico (PDFs originais)
- `calendario/` — um arquivo por mês: `AAAA-MM.md`
- `posts/AAAA-MM/` — um arquivo por post: `AAAA-MM-DD-tema-curto.md`
- `posts/radio/AAAA-MM/` — spots de rádio (.md + .docx)
- Cópias no servidor do escritório (`D:\_ESCRITÓRIO_\_SERVIÇOS_\_ARQUIVOS_AUXILIARES_\ESCRITÓRIO\MARKETING\`):
  Instagram aprovado → `NOVO INSTAGRAM\PUBLI_N` (próximo número livre; PUBLI_1 = Terra Brasil) · rádio → `RÁDIO`
- `midia/{campo,escritorio,equipe,eventos}/` — fotos e vídeos brutos
- `_arquivo/` — arquivos antigos/fora de uso (não usar como referência)
- `marca/logo.png` (símbolo redondo) · `marca/PNG.png` (logo com nome) · `marca/NOVO ENDEREÇO.jpeg` (contatos)
- `posts/AAAA-MM/<post>/slides.html` → PNGs com `python ferramentas/gerar_slides.py <pasta-do-post>` (arte padrão; Canva só para peças especiais)
- `ferramentas/publicar_instagram.py` — publica/agenda post com `Status: aprovado` (credenciais em `.env`, nunca ler)
- `.claude/skills/` — skills da marca: redação, planejamento, slides (HTML), arte (Canva), publicação, revisão, notícias, rádio

## Fluxo de publicação
Claude cria → usuário aprova no chat → Claude publica. Nunca publicar sem aprovação explícita do post.

## Git
Repositório privado: github.com/fabriciopiratini/terraforte-instagram (branch `main`).
Skill criada, alterada ou atualizada → commit + push automático. Demais mudanças, só quando o usuário pedir.

## Formato de arquivo de post
```
Status: rascunho | aprovado | publicado
Data: AAAA-MM-DD   Formato: feed | carrossel | reels | story
Linha: Informativo | Bastidores | Autoridade & Eventos
Serviço: <da lista oficial>
## Arte (texto das telas / briefing visual)
## Legenda
## Hashtags
```
