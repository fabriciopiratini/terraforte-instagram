---
name: slides-terraforte
description: Use esta skill sempre que precisar criar a arte de um post da Terra Forte — carrossel, post de imagem única ou capa — gerando slides.html e exportando PNGs 1080x1350. É o caminho PADRÃO de arte do projeto. Trigger quando o usuário pedir para criar arte, slides, carrossel, imagem do post, "gerar os PNGs" ou "montar a arte". Para peças especiais (convite de evento, material que o usuário quer editar à mão) use arte-canva-terraforte.
---

# Skill: Slides em HTML — Terra Forte

Fluxo padrão: texto do post aprovado → `slides.html` → PNGs → revisão → publicação.

## Onde fica cada coisa
- Post: `posts/AAAA-MM/AAAA-MM-DD-tema.md` (seção `## Arte` é o roteiro dos slides)
- Arte: pasta com o **mesmo nome** do .md → `posts/AAAA-MM/AAAA-MM-DD-tema/slides.html`
- PNGs: `python ferramentas/gerar_slides.py posts/AAAA-MM/AAAA-MM-DD-tema` → `slide-01.png`, `slide-02.png`…
- Modelo de referência: `posts/2026-10/2026-10-01-quem-e-a-terra-forte/slides.html` — **copie e adapte**, não comece do zero.

## Identidade fixa (não perguntar ao usuário)
| Token | Valor | Uso |
|---|---|---|
| marrom | #522800 | capa, fundo principal, texto em fundo claro |
| amarelo | #FFCB2A | destaque de palavra, botão, números |
| verde | #059734 | CTA, "como a Terra Forte faz" |
| creme | #F6F1EA | slides de conteúdo (nunca branco puro) |
| Fonte | Montserrat 400–800 | tudo; Playfair Display itálico só para "Terra Forte" em destaque |
| Logos | `marca/logo.png` (símbolo), `marca/PNG.png` (logo com nome, sobre caixa creme) | |
| Contato | copiar do slide CTA do modelo | |

## Regras técnicas do modelo
- Cada slide é `<section class="slide ...">`; o script conta as seções e renderiza `?s=1`, `?s=2`…
- Canvas real de **1080x1350** (não escalar). Tamanhos mínimos: título 72px, texto 36px, rodapé 26px — público de 35 a 65+ lê no celular.
- Caminhos relativos a partir da pasta do post: `../../../marca/logo.png`, `../../../midia/campo/foto.jpg`.
- Rodapé (logo + "2 / 6") em todos os slides menos capa e CTA.
- Capa termina com "ARRASTE PARA O LADO →"; último slide não tem.
- Alternar fundos (marrom → creme → creme → marrom/foto → verde → CTA) para dar ritmo.
- Foto de fundo: `<img>` com `object-fit:cover` + camada escura `rgba(0,0,0,.45)` por cima; texto com `z-index` maior.
- Ícones: SVG inline simples, traço 2.4, cor da marca. Nada de emoji na arte.

## Sequências prontas
| Tipo | Slides |
|---|---|
| Informativo (padrão) | capa-gancho → problema → consequência → solução → como a Terra Forte faz → CTA |
| Lista ("3 erros", "4 documentos") | capa → 1 item por slide → CTA |
| Passo a passo | capa → por que importa → passos 1-3 → CTA |
| Imagem única | 1 slide: gancho grande + logo + contato |

Gancho da capa segue o tom da marca: pergunta sobre a dor do cliente ou fato prático. **Nunca** frase polêmica, promessa de resultado ou número inventado.

## Privacidade (inegociável)
Antes de usar foto de `midia/`, confira: sem placa, rosto de cliente, documento, matrícula, tela com coordenadas ou vista que identifique propriedade privada. Na dúvida, pergunte.

## Fluxo de revisão
1. Gerar `slides.html` + PNGs.
2. Conferir os PNGs (Read) — texto cortado, sobreposição com rodapé, contraste.
3. Mostrar ao usuário e perguntar: **"Quais slides precisam de ajuste?"**
4. Corrigir só os slides apontados e renderizar de novo.
5. **Toda publicação tem legenda:** com a arte aprovada, ajustar `## Legenda` do .md ao texto final dos slides (mesmo CTA, contato, máx. 5 hashtags) e apresentar ao usuário.
6. Com arte e legenda aprovadas → rodar `revisao-conteudo-terraforte` → publicar com `publicar-instagram-terraforte`.
7. **Cópia no servidor do escritório:** com arte e legenda aprovadas, copiar os PNGs e a legenda para `D:\_ESCRITÓRIO_\_SERVIÇOS_\_ARQUIVOS_AUXILIARES_\ESCRITÓRIO\MARKETING\NOVO INSTAGRAM\PUBLI_N`, criando a pasta com o próximo número livre (PUBLI_1 = Terra Brasil). Conferir as pastas existentes antes de numerar.
