---
name: arte-canva-terraforte
description: Use esta skill para peças especiais da Terra Forte no Canva — convite de evento, banner, material impresso, ou quando o usuário pedir explicitamente o Canva ou quiser editar a arte à mão. Carrosséis e posts do dia a dia usam slides-terraforte (HTML), que é o caminho padrão. Trigger quando o usuário mencionar Canva, banner, convite, material impresso ou briefing de arte para o Canva.
---

# Skill: Arte e Design — Terra Forte (via Canva Pro)

Esta skill define como criar peças visuais para a Terra Forte usando o Canva Pro integrado.

## Identidade Visual

### Paleta de cores
- **Marrom** #522800 — cor principal, transmite terra, solidez
- **Amarelo** #FFCB2A — destaques, CTAs, energia
- **Verde** #059734 — natureza, agro, crescimento
- **Branco** #FFFFFF — fundos, respiro, limpeza
- **Preto** #000000 — textos principais

### Combinações recomendadas
- Fundo marrom + texto branco + destaque amarelo (mais impactante)
- Fundo branco + texto preto + elementos em verde e marrom (mais limpo)
- Fundo verde + texto branco + destaque amarelo (para temas agro)

### Diretrizes visuais
- Visual **limpo e profissional** — poucos elementos, bem organizados
- **Fotos reais** do trabalho de campo sempre que possível (buscar na pasta `midia/`)
- Logo da Terra Forte **sempre presente**
- Evitar: excesso de elementos decorativos, cliparts, fotos genéricas de banco de imagem
- Tipografia: fontes sólidas, legíveis, sem serifas decorativas excessivas

## Formatos por tipo de conteúdo

### Post Instagram (feed)
- Formato: 1080x1350px (retrato 4:5)
- Usar para: imagem única com texto sobreposto, foto de campo, antes/depois

### Carrossel Instagram
- Formato: 1080x1350px por slide
- Slides: 5 a 7 (ideal)
- Estrutura:
  - Slide 1: Capa com gancho forte (pergunta ou afirmação impactante)
  - Slides 2-5: Conteúdo educativo, 1 ideia por slide
  - Slide 6: Resumo ou conclusão
  - Slide 7: CTA + contato da Terra Forte
- Manter consistência visual entre slides (mesmas cores, fontes, estilo)

### Story Instagram
- Formato: 1080x1920px (9:16)
- Usar para: bastidores rápidos, enquetes, divulgação de post novo

## REGRAS CRÍTICAS DE IMAGEM E LOGO

### Uso de imagens fornecidas pelo usuário
- **OBRIGATÓRIO:** Quando o usuário indicar uma imagem específica (arquivo em `midia/`, upload, etc.), essa imagem DEVE ser usada na arte final.
- Fluxo: pegar a imagem em `midia/` → fazer upload como asset no Canva → usar o asset_id na geração do design (parâmetro asset_ids) ou inserir via edição.
- O upload do Canva exige URL pública; se a foto só existir localmente, pedir ao usuário que a envie ao Canva e informe o nome do asset.
- NUNCA criar arte com imagem genérica quando o usuário forneceu uma foto específica.
- NUNCA usar foto que identifique cliente, documento, matrícula ou propriedade privada sem autorização.

### Logomarca da Terra Forte
- **OBRIGATÓRIO:** Toda peça deve incluir a logomarca da Terra Forte.
- Antes de criar a arte, buscar a logomarca no Canva usando search-designs (query: "logo Terra Forte" ou "logomarca") para encontrar o asset.
- Se não encontrar via search, verificar nos brand kits (list-brand-kits) onde a logo pode estar registrada.
- A logo deve ser posicionada de forma visível mas não dominante (canto inferior é o padrão).

## Como criar no Canva (fluxo de trabalho)

### Passo 1: Definir o briefing
Antes de criar, definir:
- Tipo de peça (post único, carrossel, story)
- Tema/assunto do conteúdo
- Texto principal que vai na arte
- Se precisa de foto (qual tipo — campo, equipe, equipamento, lavoura)
- Qual serviço está sendo divulgado
- **Se o usuário forneceu imagem específica** — anotar o link/arquivo

### Passo 2: Preparar assets
- **Se o usuário forneceu foto:** fazer upload no Canva como asset
- **Se não forneceu:** verificar se há fotos adequadas em `midia/{campo,escritorio,equipe,eventos}/`
- Se não houver foto específica, criar arte com ícones e elementos gráficos
- Priorizar sempre fotos reais sobre elementos genéricos
- **Sempre:** buscar a logomarca da Terra Forte no Canva para incluir na peça

### Passo 3: Criar a arte no Canva
Ao usar a ferramenta do Canva, ser específico no prompt:
- Informar as cores exatas (#522800, #FFCB2A, #059734, #FFFFFF, #000000)
- Descrever o layout desejado
- Incluir o texto que deve aparecer na arte
- Especificar o formato (instagram_post para feed, your_story para stories)
- **Se tem asset_id de foto do usuário:** incluir no parâmetro asset_ids
- **Se tem asset_id da logo:** incluir no parâmetro asset_ids

### Passo 4: Revisar
Verificar antes de apresentar:
- As cores estão corretas?
- O texto está legível?
- A logo está presente?
- O visual está limpo e profissional?
- Não tem erros de português?

## Exemplos de prompts para o Canva

### Post educativo
```
Crie um post para Instagram (1080x1350) sobre georreferenciamento rural.
Cores: fundo marrom #522800, texto branco, destaque amarelo #FFCB2A.
Título: "Seu imóvel rural precisa de georreferenciamento"
Subtítulo: "Saiba por que é obrigatório"
Estilo: profissional, limpo, com ícone de mapa/localização.
Logo Terra Forte no canto inferior.
```

### Carrossel educativo
```
Crie um carrossel de 5 slides para Instagram (1080x1350 cada) sobre
"5 motivos para regularizar seu imóvel rural".
Paleta: marrom #522800, amarelo #FFCB2A, verde #059734, branco.
Slide 1: Capa com título impactante
Slides 2-5: Um motivo por slide com ícone ilustrativo
Slide 5: CTA "Fale com a Terra Forte"
Estilo profissional e limpo.
```

## Texto sobre imagens: regras de legibilidade
- Texto claro sobre fundo escuro (branco sobre marrom)
- Texto escuro sobre fundo claro (preto/marrom sobre branco/amarelo)
- Se usar foto de fundo, aplicar overlay escuro semi-transparente antes do texto
- Tamanho mínimo de fonte: títulos grandes e legíveis, subtítulos menores mas ainda claros
- Máximo de texto por slide de carrossel: 1 título + 2-3 linhas de corpo
