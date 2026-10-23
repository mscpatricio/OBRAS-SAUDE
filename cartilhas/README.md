# Cartilhas — Atendimento Odontológico à Pessoa com TEA

Coautoria: **Dr. Patrício Almeida**.

Material educativo em estilo HQ (inspirado na cartilha "Higiene Bucal" das HQs do Lucas),
composto por duas peças que trabalham juntas:

| Peça | Para quem | Arquivo-fonte | PDF |
|---|---|---|---|
| **Cartilha do cirurgião-dentista** (8 páginas A4): manejo antes, durante e depois da consulta, informativo sobre o TEA e ficha do perfil do paciente | Dentista e equipe do consultório | `cartilha-dentista/index.html` | `dist/Cartilha-Cirurgiao-Dentista-TEA.pdf` |
| **Cartilha "Minha visita ao dentista"** (15 páginas A4): história social detalhada em 20 passos, cada um com ilustração grande, "o que eu posso sentir" (som, luz, gosto, toque, cheiro) e "o que eu posso fazer"; páginas "Quem eu vou encontrar", "O que tem na sala do dentista", "Meus sinais", checklist "Eu consegui!" com espaço para carimbos e guia para quem cuida | Paciente e cuidadores (entregue pelo dentista) | `cartilha-paciente/index.html` | `dist/Cartilha-Minha-Visita-ao-Dentista.pdf` |
| **Cartilha de Enfermagem na UBS** (8 páginas A4, **autoria: Dr. Patrício Almeida**): atendimento de enfermagem à pessoa com TEA na Unidade Básica de Saúde: antes, durante (acolhimento, triagem, vacina, curativo, coleta), depois, história social “Minha vacina na UBS”, informativo e ficha | Enfermeiros, técnicos, ACS e recepção da UBS | `cartilha-enfermagem/index.html` | `dist/Cartilha-Enfermagem-UBS-TEA.pdf` |
| **Cartilha Emergência e Internação Hospitalar** (8 páginas A4, **autoria: Dr. Patrício Almeida**): a pessoa com TEA no pronto-socorro (classificação de risco, dor, procedimentos, crise de sobrecarga) e na internação (admissão, rotina visual, noite, exames, cirurgia, alta), história social “Eu no hospital”, escala de dor e ficha | Enfermagem, equipe médica e multiprofissional do hospital | `cartilha-hospital/index.html` | `dist/Cartilha-Hospital-Emergencia-Internacao-TEA.pdf` |
| **Cartilha da criança na UBS** “Minha ida ao posto de saúde” (14 páginas, autoria Dr. Patrício Almeida): 18 passos (temperatura, balança, braçadeira, dedinho de luz, ouvidor, vacina, sangue, curativo, remédio), pessoas e objetos do posto, sinais, Eu consegui! e guia para quem cuida | Criança e cuidadores | `crianca-ubs/config.js` | `dist/Cartilha-Crianca-UBS-Minha-Ida-ao-Posto.pdf` |
| **Cartilha da criança no hospital** “Eu no hospital” (12 páginas, autoria Dr. Patrício Almeida): 14 passos (carinhas da dor, pulseira, exame, sangue/soro, raio-X, quarto, plantões, remédio, comida, noite, cirurgia, alta), pessoas e objetos do hospital | Criança e cuidadores | `crianca-hospital/config.js` | `dist/Cartilha-Crianca-Hospital-Eu-no-Hospital.pdf` |
| **Cartilha para pais: dentista** (8 páginas, coautoria): antes, no dia, sinais e crise, depois, direitos e dúvidas, checklist e passaporte do TEA | Pais e cuidadores | `pais-dentista/config.js` | `dist/Cartilha-Pais-Dentista-TEA.pdf` |
| **Cartilha para pais: UBS** (8 páginas, autoria Dr. Patrício Almeida): mesma estrutura, para consultas, vacinas, exames e curativos no posto | Pais e cuidadores | `pais-ubs/config.js` | `dist/Cartilha-Pais-UBS-TEA.pdf` |
| **Cartilha para pais: hospital** (8 páginas, autoria Dr. Patrício Almeida): mesma estrutura, para emergência, internação, exames, cirurgia e alta | Pais e cuidadores | `pais-hospital/config.js` | `dist/Cartilha-Pais-Hospital-TEA.pdf` |
| **App para iOS e Android** (PWA + Capacitor): perfis **Dentista** (modo consulta, checklists, pacientes, informativo) e **Criança** (história em 20 passos com voz, sinais PARE, Eu consegui!). Veja `app/README.md` | Dentista, paciente e cuidadores | `app/www/` | `dist/App-Minha-Visita-ao-Dentista.html` (arquivo único, abre no celular) |
| **Card resumido "Minha visita ao dentista"** (frente e verso A4): versão curta em 10 passos, sinais combinados, checklist e mini-card recortável | Paciente e cuidadores (acesso rápido) | `card-paciente/index.html` | `dist/Card-Minha-Visita-ao-Dentista.pdf` |

A cartilha mescla os três formatos pedidos: **sequência visual da consulta**, **história social ilustrada**
e **passo a passo em quadrinhos**.

## Estrutura

```
cartilhas/
├── shared/
│   ├── ill.js        # biblioteca de ilustrações vetoriais (personagens, cenário, balões, ícones)
│   ├── style.css     # estilo de impressão compartilhado (A4, fontes, caixas)
│   ├── crianca.js / crianca.css   # gerador das cartilhas da criança (história social)
│   ├── pais.js / pais.css         # gerador das cartilhas para pais e cuidadores
│   └── fonts/        # Baloo 2, Comic Neue e Nunito (Google Fonts, licença OFL)
├── cartilha-dentista/index.html
├── cartilha-enfermagem/index.html
├── cartilha-hospital/index.html
├── cartilha-paciente/index.html   # os 20 passos ficam em um array no fim do arquivo
├── card-paciente/index.html
├── crianca-ubs/, crianca-hospital/      # config.js + index.html; gerados por shared/crianca.js
├── pais-dentista/, pais-ubs/, pais-hospital/  # config.js + index.html; gerados por shared/pais.js
├── app/                           # aplicativo (ver app/README.md)
├── build/
│   ├── render.mjs         # gera PDF + PNG de cada página com o Chromium (Playwright)
│   └── preview-cenas.html # página de teste com todas as cenas
└── dist/                  # PDFs finais e PNGs de pré-visualização de cada página
```

Todas as ilustrações são SVG geradas em `shared/ill.js`: cada cena é uma função
(`SCENES.nome`) montada com personagens (`KID`, `DENTIST`, `MOM`, `RECEP`), objetos
(cadeira, refletor, balcão, TV, brinde…) e balões de fala. Para trocar uma expressão,
pose, cor de roupa ou texto de balão, basta editar a cena correspondente.

## Como editar e gerar os PDFs

1. Abra `cartilha-dentista/index.html` ou `card-paciente/index.html` no navegador para
   visualizar (as ilustrações são montadas ao carregar a página).
2. Edite os textos direto no HTML; as cenas em `shared/ill.js`.
3. Gere os PDFs (precisa de Node 18+ e do pacote `playwright` com Chromium):

```bash
npm i -D playwright            # uma vez; ou use uma instalação global
node cartilhas/build/render.mjs            # gera as três peças
node cartilhas/build/render.mjs card-paciente   # só uma delas
node cartilhas/build/render.mjs preview-cenas   # PNGs com todas as cenas, para revisão
```

Os arquivos saem em `cartilhas/dist/`. O PDF é vetorial (texto selecionável), em A4,
pronto para impressão. Para imprimir o card em frente e verso, use "virar na borda longa".

## Personalização sugerida

- Preencher os créditos na última página da cartilha (concepção, revisão técnica, edição).
- Inserir o logotipo da instituição na capa (há espaço no rodapé) e no verso do card.
- Ajustar nomes e falas dos personagens para refletir a equipe real do consultório.
- Se quiser ilustrações em outro estilo, as cenas podem ser substituídas por imagens
  (`<img>`) mantendo o mesmo layout.
