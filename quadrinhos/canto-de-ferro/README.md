# CANTO DE FERRO

> *"Todo metal lembra o que foi. O nosso, além disso, lembra quem o usou."*

**Canto de Ferro** é uma revista em quadrinhos original de ficção científica e aventura,
inspirada no espírito de *Transformers* (máquinas que vivem e mudam de forma), mas com
nome, mitologia, origem, vocabulário e personagens completamente inéditos.

Aqui não há alienígenas, não há planeta-máquina, não há disfarce. Os **Forjados** são
máquinas brasileiras que ganharam vida porque foram fabricadas com um minério que
*canta*: o **ferro-canto**, caído do céu sobre Minas Gerais em 1811. Durante dois
séculos, esse metal virou sino, canhão, trilho, trator, tear, barco e caminhão. E, de
tanto ser usado, aprendeu a lembrar.

## Conteúdo da pasta

| Arquivo | O que é |
|---|---|
| [`Canto-de-Ferro-01-Primeira-Tempera.pdf`](Canto-de-Ferro-01-Primeira-Tempera.pdf) | **A revista diagramada em PDF** (43 páginas, 17 × 26 cm): capa, bíblia, personagens, roteiro ilustrado e extras |
| [`01-biblia-do-universo.md`](01-biblia-do-universo.md) | Origem, regras do mundo, facções, glossário e tom da série |
| [`02-personagens.md`](02-personagens.md) | Fichas dos Forjados e dos humanos, com Ofício, Figura e voz |
| [`03-edicao-01-roteiro.md`](03-edicao-01-roteiro.md) | Roteiro completo da edição nº 1, *"Primeira Têmpera"*, página a página |
| [`04-plano-de-arco.md`](04-plano-de-arco.md) | Sinopse das 6 edições do primeiro arco e capas |

## Ficha técnica (proposta)

- **Formato:** 24 páginas de história + capa + 2 páginas de extras, mensal
- **Faixa etária:** a partir de 10 anos
- **Gênero:** ficção científica, aventura, drama de época (flashbacks 1811 a 1960)
- **Ambientação:** Minas Gerais e São Paulo, 2026, com raízes em Sabará, Ipanema (SP) e nas ferrovias do século XIX
- **Logline:** Quando o sino mais antigo de Minas é retirado da torre para ser derretido, ele desperta
  todas as máquinas que nasceram do mesmo metal e decide que a humanidade só se salva sendo refundida.
  Um caminhão de bombeiros aposentado e um estagiário de 16 anos são os únicos que o ouvem a tempo.

## Gerar o PDF

A revista é diagramada em HTML/CSS com ilustrações vetoriais (SVG) e renderizada pelo Chromium.
Os roteiros em Markdown são a fonte: o gerador lê `03-edicao-01-roteiro.md`, monta a grade de
quadros de cada página e produz o PDF.

```bash
cd quadrinhos/canto-de-ferro/build
python3 gen.py        # gera canto-de-ferro-01.html
node render.js        # requer playwright com Chromium; gera canto-de-ferro-01.pdf
```

Fontes (Bebas Neue, Oswald, Barlow Condensed, Bangers) estão em `build/fonts/`, licença SIL OFL.

## Arte

As ilustrações (capa, 11 retratos de personagens e 24 painéis, um por página do roteiro) estão em
`build/art/`. Foram geradas por IA (modelo NanoBanana 2.1 via Moda) a partir de prompts escritos
sobre as fichas e o roteiro, em estilo de graphic novel pintada com arte-final a nanquim, e
diagramadas pelo gerador: o quadro principal de cada página recebe a arte e os balões, legendas e
efeitos sonoros são sobrepostos por cima. Os quadros restantes mantêm a indicação de cena para o
desenhista.
