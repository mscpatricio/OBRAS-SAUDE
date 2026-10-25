# Ilustrações vetoriais (SVG) para a revista Canto de Ferro
RUST="#c8501e"; BRONZE="#c9a24a"; IRON="#141518"; BONE="#f1ebdd"; RED="#b8261f"; DEEP="#2a1a12"; STEEL="#6b7280"

def vib(cx, cy, r0, n, color, w=1.2, op=0.35, step=14):
    """anéis concêntricos de vibração"""
    return "".join(f'<circle cx="{cx}" cy="{cy}" r="{r0+i*step}" fill="none" stroke="{color}" stroke-width="{w}" opacity="{op*(1-i/(n+1)):.2f}"/>' for i in range(n))

def ladder(x, y, w, h, rungs, color, sw=6):
    s=f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+h}" stroke="{color}" stroke-width="{sw}"/>'
    s+=f'<line x1="{x+w}" y1="{y}" x2="{x+w}" y2="{y+h}" stroke="{color}" stroke-width="{sw}"/>'
    for i in range(rungs+1):
        yy=y+i*h/rungs
        s+=f'<line x1="{x}" y1="{yy:.1f}" x2="{x+w}" y2="{yy:.1f}" stroke="{color}" stroke-width="{sw*0.7}"/>'
    return s

def cover_svg():
    W,H=680,1040
    s=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">'
    s+='''<defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1a0f0a"/><stop offset="0.35" stop-color="#6b2a12"/>
      <stop offset="0.62" stop-color="#c8501e"/><stop offset="0.8" stop-color="#e08a3c"/><stop offset="1" stop-color="#f1c27a"/>
    </linearGradient>
    <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1d1a17"/><stop offset="1" stop-color="#0b0a09"/></linearGradient>
    <linearGradient id="fig" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8f1f17"/><stop offset="1" stop-color="#3b0d0a"/></linearGradient>
    <radialGradient id="sun" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffe3a8"/><stop offset="0.6" stop-color="#f0a24a"/><stop offset="1" stop-color="#e08a3c" stop-opacity="0"/></radialGradient>
    </defs>'''
    s+=f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
    s+=f'<circle cx="480" cy="700" r="130" fill="url(#sun)" opacity="0.9"/>'
    # morros
    s+=f'<path d="M0 760 Q120 700 260 740 T520 720 T680 750 L680 1040 L0 1040Z" fill="#2b1b14" opacity="0.9"/>'
    s+=f'<path d="M0 800 Q180 760 340 790 T680 780 L680 1040 L0 1040Z" fill="#1a120e"/>'
    # torre barroca
    tx=470
    s+=f'<rect x="{tx}" y="380" width="110" height="420" fill="#120c09"/>'
    s+=f'<path d="M{tx-10} 380 L{tx+120} 380 L{tx+100} 330 Q{tx+55} 290 {tx+10} 330 Z" fill="#120c09"/>'
    s+=f'<path d="M{tx+30} 300 Q{tx+55} 250 {tx+80} 300 Z" fill="#120c09"/>'
    s+=f'<rect x="{tx+52}" y="225" width="6" height="40" fill="#120c09"/><rect x="{tx+43}" y="236" width="24" height="5" fill="#120c09"/>'
    # janela da torre (vazada)
    s+=f'<path d="M{tx+30} 470 L{tx+80} 470 L{tx+80} 400 Q{tx+55} 370 {tx+30} 400 Z" fill="#c8501e" opacity="0.85"/>'
    # Dobre: sino com braços na janela
    s+=f'<path d="M{tx+40} 460 L{tx+70} 460 L{tx+68} 420 Q{tx+55} 400 {tx+42} 420 Z" fill="#0a0705"/>'
    s+=f'<line x1="{tx+40}" y1="430" x2="{tx+16}" y2="405" stroke="#0a0705" stroke-width="3"/>'
    s+=f'<line x1="{tx+70}" y1="430" x2="{tx+96}" y2="402" stroke="#0a0705" stroke-width="3"/>'
    s+=vib(tx+55, 435, 40, 7, "#ffd9a0", 1.4, 0.5, 22)
    # chão
    s+=f'<rect x="0" y="880" width="{W}" height="160" fill="url(#ground)"/>'
    # Vigília de costas (figura geométrica)
    fx=150
    s+=f'<rect x="{fx+60}" y="1000" width="70" height="60" fill="#1c0906"/><rect x="{fx+200}" y="1000" width="70" height="60" fill="#1c0906"/>'  # pés
    s+=f'<rect x="{fx+70}" y="800" width="60" height="210" rx="8" fill="url(#fig)"/><rect x="{fx+200}" y="800" width="60" height="210" rx="8" fill="url(#fig)"/>'  # pernas
    s+=f'<path d="M{fx+40} 560 L{fx+290} 560 L{fx+270} 820 L{fx+60} 820 Z" fill="url(#fig)"/>'  # torso
    s+=f'<rect x="{fx-10}" y="540" width="350" height="70" rx="14" fill="#5a150f"/>'  # ombros
    s+=f'<rect x="{fx-30}" y="580" width="56" height="230" rx="10" fill="url(#fig)"/><rect x="{fx+304}" y="580" width="56" height="230" rx="10" fill="url(#fig)"/>'  # braços
    s+=f'<rect x="{fx+105}" y="455" width="120" height="100" rx="10" fill="#4a110c"/>'  # cabeça
    # escada nas costas
    s+=ladder(fx+130, 300, 70, 520, 13, "#d9d2c5", 7)
    s+=f'<rect x="{fx+125}" y="300" width="80" height="12" fill="#d9d2c5"/>'
    # faixas descascadas (tinta)
    s+=f'<rect x="{fx+60}" y="640" width="210" height="14" fill="{BONE}" opacity="0.75"/><rect x="{fx+60}" y="662" width="210" height="6" fill="{BONE}" opacity="0.5"/>'
    # Teo no ombro + Cálamo
    s+=f'<rect x="{fx+262}" y="490" width="22" height="52" rx="6" fill="#0a0705"/><circle cx="{fx+273}" cy="480" r="11" fill="#0a0705"/>'
    s+=f'<rect x="{fx+284}" y="505" width="18" height="22" rx="3" fill="#2b2b2b" stroke="#0a0705" stroke-width="2"/>'
    s+=f'<rect x="{fx+288}" y="500" width="10" height="6" fill="{BONE}"/>'
    # linhas de vibração no chão
    for i in range(6):
        s+=f'<path d="M0 {905+i*22} Q170 {895+i*22} 340 {905+i*22} T680 {905+i*22}" fill="none" stroke="#c8501e" stroke-width="1" opacity="{0.35-i*0.05:.2f}"/>'
    s+='</svg>'
    return s

def emblem(kind, size=300):
    v=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="{size}" height="{size}">'
    if kind=="vigilia":
        v+=vib(150,150,105,5,RED,2,0.3,12)
        v+=ladder(110,30,80,110,5,BONE,7)
        v+=f'<rect x="60" y="120" width="180" height="130" rx="14" fill="{RED}"/>'
        v+=f'<rect x="60" y="150" width="180" height="16" fill="{BONE}" opacity="0.85"/>'
        v+=f'<circle cx="100" cy="205" r="22" fill="#ffd34d"/><circle cx="200" cy="205" r="22" fill="#ffd34d"/>'
        for i in range(5): v+=f'<rect x="{128+i*10}" y="190" width="4" height="34" fill="{IRON}" opacity="0.6"/>'
        v+=f'<rect x="75" y="250" width="40" height="22" fill="{IRON}"/><rect x="185" y="250" width="40" height="22" fill="{IRON}"/>'
    elif kind=="mare":
        v+=f'<path d="M30 150 Q150 250 270 150 L270 110 L30 110 Z" fill="#2f5b7a"/>'
        v+=f'<path d="M30 110 Q90 30 150 90 Z" fill="#3f7fa8"/><path d="M270 110 Q210 30 150 90 Z" fill="#3f7fa8"/>'
        v+=f'<rect x="100" y="60" width="100" height="50" fill="{BONE}"/>'
        for i in range(3): v+=f'<path d="M20 {215+i*22} q25 -14 50 0 t50 0 t50 0 t50 0 t50 0" fill="none" stroke="#3f7fa8" stroke-width="4" opacity="{0.9-i*0.3}"/>'
    elif kind=="fuso":
        v+=f'<rect x="50" y="40" width="200" height="220" fill="none" stroke="#7a5b3a" stroke-width="12"/>'
        for i in range(12): v+=f'<line x1="{70+i*14.5}" y1="52" x2="{70+i*14.5}" y2="248" stroke="{BONE}" stroke-width="2.5" opacity="0.9"/>'
        v+=f'<rect x="40" y="130" width="220" height="24" fill="{RUST}"/>'
        v+=f'<ellipse cx="150" cy="142" rx="34" ry="10" fill="{BONE}"/>'
    elif kind=="cerrado":
        v+=f'<circle cx="95" cy="200" r="60" fill="{IRON}"/><circle cx="95" cy="200" r="30" fill="#e0a21a"/>'
        v+=f'<circle cx="230" cy="225" r="35" fill="{IRON}"/><circle cx="230" cy="225" r="16" fill="#e0a21a"/>'
        v+=f'<path d="M60 150 L200 150 L220 190 L60 190 Z" fill="#e0a21a"/><rect x="120" y="90" width="70" height="60" fill="#e0a21a"/>'
        v+=f'<rect x="200" y="100" width="14" height="60" fill="{IRON}"/>'
        v+=f'<rect x="130" y="100" width="50" height="35" fill="{IRON}" opacity="0.7"/>'
        for i in range(3): v+=f'<path d="M207 {90-i*18} q6 -8 0 -16" fill="none" stroke="{STEEL}" stroke-width="3" opacity="{0.8-i*0.25}"/>'
    elif kind=="calamo":
        v+=f'<rect x="100" y="40" width="100" height="90" fill="{BONE}"/>'
        v+=f'<rect x="60" y="120" width="180" height="40" rx="6" fill="{IRON}"/>'
        v+=f'<path d="M50 160 L250 160 L270 250 L30 250 Z" fill="#3a3d44"/>'
        for r in range(3):
            for c in range(9): v+=f'<circle cx="{70+c*20+r*8}" cy="{180+r*24}" r="7" fill="{BONE}"/>'
        v+=f'<rect x="110" y="60" width="80" height="4" fill="{IRON}" opacity="0.5"/><rect x="110" y="72" width="60" height="4" fill="{IRON}" opacity="0.5"/>'
    elif kind=="dobre":
        v+=vib(150,210,60,6,BRONZE,1.5,0.35,14)
        # sino invertido, quatro pétalas
        v+=f'<path d="M150 60 L70 230 Q110 250 150 240 Z" fill="#8a6a2a"/><path d="M150 60 L230 230 Q190 250 150 240 Z" fill="#b08a3a"/>'
        v+=f'<path d="M150 60 L120 235 L150 240 Z" fill="#6d5220"/><path d="M150 60 L180 235 L150 240 Z" fill="#c9a24a"/>'
        v+=f'<rect x="130" y="40" width="40" height="60" rx="8" fill="{IRON}"/>'
        v+=f'<circle cx="150" cy="30" r="18" fill="{IRON}"/><path d="M140 30 q10 6 20 0" fill="none" stroke="{BRONZE}" stroke-width="2.5"/>'
        v+=f'<line x1="130" y1="60" x2="60" y2="130" stroke="{IRON}" stroke-width="7"/><line x1="170" y1="60" x2="240" y2="130" stroke="{IRON}" stroke-width="7"/>'
        v+=f'<circle cx="150" cy="248" r="5" fill="{IRON}"/>'
    elif kind=="lastro":
        v+=f'<circle cx="150" cy="130" r="85" fill="{IRON}"/><circle cx="150" cy="130" r="60" fill="#2b2f36"/><circle cx="150" cy="130" r="22" fill="#ffd34d"/>'
        v+=f'<rect x="40" y="200" width="220" height="40" fill="#2b2f36"/>'
        v+=f'<path d="M50 240 L250 240 L280 280 L20 280 Z" fill="{IRON}"/>'
        for i in range(7): v+=f'<line x1="{45+i*35}" y1="240" x2="{35+i*35}" y2="280" stroke="{BONE}" stroke-width="3"/>'
        v+=f'<rect x="135" y="20" width="30" height="40" fill="{IRON}"/>'
    elif kind=="estilhaco":
        v+=f'<circle cx="110" cy="200" r="70" fill="none" stroke="{IRON}" stroke-width="14"/>'
        for a in range(0,360,45): v+=f'<line x1="110" y1="200" x2="{110+62*__import__("math").cos(a*3.1416/180):.1f}" y2="{200+62*__import__("math").sin(a*3.1416/180):.1f}" stroke="{IRON}" stroke-width="6"/>'
        v+=f'<path d="M80 150 L270 60 L285 88 L105 185 Z" fill="#3a3d44"/>'
        v+=f'<rect x="60" y="40" width="90" height="100" rx="16" fill="#9aa0a8"/>'
    elif kind=="grimpa":
        v+=f'<line x1="150" y1="60" x2="150" y2="280" stroke="{IRON}" stroke-width="8"/>'
        v+=f'<line x1="40" y1="180" x2="260" y2="180" stroke="{IRON}" stroke-width="6"/><path d="M260 180 L235 165 L235 195 Z" fill="{IRON}"/><circle cx="40" cy="180" r="12" fill="{IRON}"/>'
        v+=f'<path d="M110 150 L170 150 L200 120 L190 150 L205 150 L185 100 L170 60 Q150 70 150 90 L130 90 Q115 110 110 150Z" fill="{RUST}"/>'
        v+=f'<path d="M165 60 l8 -14 l6 14 l8 -12 l4 14 Z" fill="{RED}"/>'
        for lab,x,y in (("N",150,45),("S",150,300),("L",285,186),("O",15,186)):
            v+=f'<text x="{x}" y="{y}" font-family="Oswald" font-size="20" fill="{IRON}" text-anchor="middle" font-weight="700">{lab}</text>'
    v+='</svg>'
    return v

def timeline_svg():
    pts=[("1811","A Estrela cai em Sabará"),("1812","Dobre é fundido"),("1866","Canhões de Ipanema"),("1897","Guarda da Bigorna"),("1958","Vigília sai da fábrica"),("1983","Vigília desperta"),("2026","O sino desce da torre")]
    W=1000; s=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 150" width="100%">'
    s+=f'<line x1="30" y1="60" x2="{W-30}" y2="60" stroke="{RUST}" stroke-width="3"/>'
    n=len(pts)
    for i,(y,l) in enumerate(pts):
        x=50+i*(W-100)/(n-1)
        s+=f'<circle cx="{x:.0f}" cy="60" r="9" fill="{IRON}" stroke="{RUST}" stroke-width="3"/>'
        s+=f'<text x="{x:.0f}" y="38" text-anchor="middle" font-family="Bebas Neue" font-size="30" fill="{IRON}">{y}</text>'
        words=l.split(); mid=len(words)//2 or 1
        s+=f'<text x="{x:.0f}" y="92" text-anchor="middle" font-family="Barlow Condensed" font-size="17" fill="#444">{" ".join(words[:mid])}</text>'
        s+=f'<text x="{x:.0f}" y="112" text-anchor="middle" font-family="Barlow Condensed" font-size="17" fill="#444">{" ".join(words[mid:])}</text>'
    s+='</svg>'
    return s

def dobra_svg():
    """Ofício → Dobra → Figura em quatro faixas"""
    s=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" width="100%">'
    for i in range(4):
        x=i*250
        s+=f'<rect x="{x+10}" y="10" width="230" height="240" rx="10" fill="#faf7f0" stroke="#ddd"/>'
        s+=f'<text x="{x+22}" y="40" font-family="Bebas Neue" font-size="26" fill="{RUST}">{i+1}</text>'
        if i==0:
            s+=f'<rect x="{x+50}" y="150" width="150" height="60" rx="8" fill="{RED}"/><rect x="{x+60}" y="120" width="60" height="30" fill="{RED}"/>'
            s+=f'<circle cx="{x+80}" cy="215" r="16" fill="{IRON}"/><circle cx="{x+170}" cy="215" r="16" fill="{IRON}"/>'
            s+=ladder(x+120,128,70,12,2,BONE,4)
            s+=f'<text x="{x+125}" y="70" font-family="Oswald" font-size="16" fill="#333" text-anchor="middle">OFÍCIO</text>'
        elif i==1:
            s+=f'<rect x="{x+60}" y="130" width="140" height="70" rx="8" fill="{RED}"/><rect x="{x+60}" y="95" width="60" height="35" fill="{RED}" transform="rotate(-20 {x+60} 130)"/>'
            s+=f'<circle cx="{x+75}" cy="215" r="16" fill="{IRON}"/><circle cx="{x+185}" cy="200" r="16" fill="{IRON}"/>'
            s+=ladder(x+120,80,60,55,3,BONE,4)
            s+=vib(x+125,160,70,3,RUST,1.5,0.5,12)
            s+=f'<text x="{x+125}" y="70" font-family="Oswald" font-size="16" fill="#333" text-anchor="middle">A DOBRA COMEÇA</text>'
        elif i==2:
            s+=f'<path d="M{x+80} 120 L{x+170} 120 L{x+165} 215 L{x+85} 215 Z" fill="{RED}"/><rect x="{x+60}" y="110" width="130" height="24" rx="8" fill="#8f1f17"/>'
            s+=f'<rect x="{x+95}" y="70" width="60" height="42" rx="6" fill="#8f1f17"/>'
            s+=ladder(x+112,20,26,100,6,BONE,3)
            s+=vib(x+125,150,80,4,RUST,1.5,0.5,12)
            s+=f'<text x="{x+125}" y="245" font-family="Oswald" font-size="16" fill="#333" text-anchor="middle">O ACORDE SOA</text>'
        else:
            s+=f'<rect x="{x+100}" y="160" width="20" height="60" fill="#8f1f17"/><rect x="{x+130}" y="160" width="20" height="60" fill="#8f1f17"/>'
            s+=f'<path d="M{x+85} 95 L{x+165} 95 L{x+160} 165 L{x+90} 165 Z" fill="{RED}"/><rect x="{x+65}" y="88" width="120" height="20" rx="8" fill="#8f1f17"/>'
            s+=f'<rect x="{x+60}" y="100" width="18" height="70" rx="6" fill="{RED}"/><rect x="{x+172}" y="100" width="18" height="70" rx="6" fill="{RED}"/>'
            s+=f'<rect x="{x+105}" y="50" width="40" height="36" rx="6" fill="#4a110c"/><circle cx="{x+117}" cy="68" r="5" fill="#ffd34d"/><circle cx="{x+133}" cy="68" r="5" fill="#ffd34d"/>'
            s+=ladder(x+117,20,16,40,3,BONE,2)
            s+=f'<text x="{x+125}" y="245" font-family="Oswald" font-size="16" fill="#333" text-anchor="middle">FIGURA</text>'
    s+='</svg>'
    return s
