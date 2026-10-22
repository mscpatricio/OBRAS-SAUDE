# App "Minha visita ao dentista" — iOS e Android

Coautoria: **Dr. Patrício Almeida**.

Aplicativo com o mesmo material das cartilhas, em dois perfis:

| Perfil | O que tem |
|---|---|
| **Criança / família** | História social em 20 passos (ilustração, frase, "o que eu posso sentir", "o que eu posso fazer"), leitura em voz alta, marcação "já aconteceu"; **Meus sinais** em tela cheia (PARE, pausa, tudo bem) com botão PARE sempre visível; "Quem eu vou encontrar" (com campo para o nome real do dentista e do auxiliar); "O que tem na sala" (12 objetos); "Eu consegui!" com conquistas, estrelas e registro das visitas. |
| **Dentista / equipe** | **Modo consulta**: contagem "até 10 e paro" em voz alta, cronômetro da consulta, sinais para mostrar e sequência visual de 10 quadros para tocar ao concluir; checklists **Antes / Durante / Depois** com marcação; **Pacientes**: perfil sensorial (ficha da cartilha), registro das consultas por degrau alcançado, "Copiar ficha" para o prontuário; **Informativo** (o TEA no consultório, o que dizer e evitar, sinais de sobrecarga). |

É um **PWA** (Progressive Web App): HTML, CSS e JavaScript puros, sem dependências, com
funcionamento off-line (service worker) e ícones. Os dados ficam somente no aparelho
(`localStorage`); nada é enviado a servidores.

## Testar agora (sem instalar nada)

```bash
cd cartilhas/app
npx http-server www -p 8080 -c-1
# abra http://localhost:8080 no navegador (ou no celular, na mesma rede)
```

No celular, use **"Adicionar à tela de início"** (Safari no iOS, Chrome no Android) para
instalar como app, com ícone e tela cheia.

## Publicar como app nas lojas (Capacitor)

Precisa de Node 18+, e do Xcode (iOS) ou Android Studio (Android).

```bash
cd cartilhas/app
npm install
npm run cap:add        # cria as pastas android/ e ios/
npm run cap:sync       # copia www/ para os projetos nativos
npm run android        # abre no Android Studio → Build / Run
npm run ios            # abre no Xcode → Run (precisa de um Mac)
```

Identificador do app: `br.com.dentistatea.app` (altere em `capacitor.config.json` antes do
primeiro `cap:add`). Os ícones de loja podem ser gerados a partir de
`www/icons/icon-512.png` (por exemplo com `@capacitor/assets`).

## Estrutura

```
app/
├── www/
│   ├── index.html          # casca do app
│   ├── app.js              # telas, navegação (#/rota), armazenamento, voz
│   ├── app.css             # estilo (mobile first, mesmo visual das cartilhas)
│   ├── data.js             # todo o conteúdo: passos, pessoas, objetos, checklists, fichas
│   ├── sw.js               # service worker (modo off-line)
│   ├── manifest.webmanifest
│   ├── icons/              # ícones do app (gerados por build-icons.mjs)
│   └── shared/             # ill.js (ilustrações vetoriais) e fontes, copiados de ../shared
├── capacitor.config.json
├── build-icons.mjs         # gera os ícones PNG
├── screenshots.mjs         # captura as telas em viewport de celular
└── test-flow.mjs           # teste automatizado do fluxo principal
```

Para alterar textos, edite `www/data.js`. Para alterar ilustrações, edite
`../shared/ill.js` e copie para `www/shared/ill.js`.

## Rotas

`#/` escolha de perfil · `#/crianca` · `#/crianca/historia/N` · `#/crianca/sinais` ·
`#/crianca/pessoas` · `#/crianca/sala` · `#/crianca/consegui` · `#/crianca/config` ·
`#/dentista` · `#/dentista/consulta` · `#/dentista/lista/antes|durante|depois` ·
`#/dentista/pacientes` · `#/dentista/paciente/novo|ID` · `#/dentista/info`
