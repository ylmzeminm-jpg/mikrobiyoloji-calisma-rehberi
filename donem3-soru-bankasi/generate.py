import re
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC_FIZYO = ROOT.parent.parent / "fizyopato soruları.txt"
SRC_MIKRO_HTML = ROOT.parent / "mikrosorulari.html"
OUT = ROOT / "index.html"

# ---------------------------------------------------------------------------
# Section metadata: section name (as it appears in fizyopato soruları.txt)
#   -> (anchor id, emoji, badge class, display label)
# ---------------------------------------------------------------------------
FIZYO_SECTIONS = [
    ("27 FİNAL",     "fz-27final", "🟣", "exam27", "27 FİNAL"),
    ("26 FİNAL",     "fz-26final", "🌸", "exam26", "26 FİNAL"),
    ("26 BÜTÜNLEME", "fz-26but",   "🔷", "exam26b", "26 BÜTÜNLEME"),
    ("25 FİNAL",     "fz-25final", "🟠", "exam25", "25 FİNAL"),
    ("24 FİNAL",     "fz-24final", "🔵", "exam24", "24 FİNAL"),
    ("23 FİNAL",     "fz-23final", "🟢", "exam23", "23 FİNAL"),
    ("29 D3M1",      "fz-29d3m1",  "⚪", "d3m1", "29 D3M1"),
    ("29 D3M2",      "fz-29d3m2",  "🔴", "d3m2", "29 D3M2"),
    ("29 D3M3",      "fz-29d3m3",  "🟡", "d3m3", "29 D3M3"),
    ("29 D3M4",      "fz-29d3m4",  "🟦", "d3m4", "29 D3M4"),
    ("29 D3M5",      "fz-29d3m5",  "🟥", "d3m5", "29 D3M5"),
]
FIZYO_META = {name: meta for name, *meta in FIZYO_SECTIONS}

MIKRO_SECTIONS = [
    ("sec-27final", "🟣", "exam27", "27 FİNAL"),
    ("sec-26final", "🌸", "exam26", "26 FİNAL"),
    ("sec-26but",   "🔷", "exam26b", "26 BÜTÜNLEME"),
    ("sec-25final", "🟠", "exam25", "25 FİNAL"),
    ("sec-24final", "🔵", "exam24", "24 FİNAL"),
    ("sec-23final", "🟢", "exam23", "23 FİNAL"),
    ("sec-29d3m2",  "🔴", "d3m2", "29 D3M2"),
    ("sec-29d3m3",  "🟡", "d3m3", "29 D3M3"),
]

CEVAP_RE = re.compile(r"^CEVAP:\s*([A-E])\s*(?:\((.*)\))?\s*$")
QSTART_RE = re.compile(r"^(\d+)\)\s*(.*)$")
OPTION_RE = re.compile(r"^([A-E])\)\s*(.*)$")
SECTION_RE = re.compile(r"^=+\n(.+)\n=+$")
UNSURE_RE = re.compile(r"tartış|emin değil|emin olmayarak", re.IGNORECASE)


def parse_fizyo(text):
    """Returns dict: section name -> list of question dicts."""
    blocks = re.split(r"\n\s*\n", text.strip())
    sections = {}
    current = None
    for block in blocks:
        block = block.strip("\n")
        m = SECTION_RE.match(block)
        if m:
            current = m.group(1).strip()
            sections[current] = []
            continue
        if current is None:
            continue  # title/source-note block before first section
        lines = block.split("\n")
        qm = QSTART_RE.match(lines[0])
        if not qm:
            continue
        number = qm.group(1)
        stem_lines = [qm.group(2)]
        i = 1
        while i < len(lines) and not OPTION_RE.match(lines[i]) and not CEVAP_RE.match(lines[i]):
            stem_lines.append(lines[i])
            i += 1
        options = []
        while i < len(lines):
            om = OPTION_RE.match(lines[i])
            if not om:
                break
            options.append((om.group(1), om.group(2)))
            i += 1
        cevap_letter, cevap_note = None, None
        if i < len(lines):
            cm = CEVAP_RE.match(lines[i])
            if cm:
                cevap_letter, cevap_note = cm.group(1), cm.group(2)
        sections[current].append({
            "number": number,
            "stem": stem_lines,
            "options": options,
            "cevap_letter": cevap_letter,
            "cevap_note": cevap_note,
        })
    return sections


def render_fizyo_card(q, emoji, badge_class, label):
    text_lines = list(q["stem"]) + [f"{l}) {t}" for l, t in q["options"]]
    soru_text = html.escape("\n".join(text_lines), quote=False)
    card = [
        '<div class="topic-card">',
        '<div class="topic-header">',
        f'<h3>Soru {q["number"]}</h3>',
        f'<span class="badge {badge_class}">{emoji} {label}</span>',
        '</div>',
        f'<div class="soru-text">{soru_text}</div>',
    ]
    if q["cevap_letter"]:
        answer_class = "answer unsure" if (q["cevap_note"] and UNSURE_RE.search(q["cevap_note"])) else "answer"
        card.append('<details class="q">')
        card.append('<summary>✅ Cevabı Gör</summary>')
        card.append(f'<div class="{answer_class}">✔️ Doğru cevap: <b>{q["cevap_letter"]}</b></div>')
        if q["cevap_note"]:
            card.append(f'<div class="qbody">{html.escape(q["cevap_note"], quote=False)}</div>')
        card.append('</details>')
    else:
        card.append('<div class="no-cozum">❓ Bu soru için kaynak dosyada cevap anahtarı bulunamadı.</div>')
    card.append('</div>')
    return "\n".join(card)


def build_fizyo_sections(sections):
    out = []
    subnav = []
    total_q = 0
    total_cevap = 0
    for name, anchor, emoji, badge_class, label in FIZYO_SECTIONS:
        qs = sections.get(name, [])
        total_q += len(qs)
        total_cevap += sum(1 for q in qs if q["cevap_letter"])
        subnav.append(f'<a href="#{anchor}">{emoji} {label} ({len(qs)})</a>')
        out.append(f'<section id="{anchor}">')
        out.append(f'<h2 class="section-title">{emoji} {label} <span class="badge {badge_class}">{len(qs)} soru</span></h2>')
        for q in qs:
            out.append(render_fizyo_card(q, emoji, badge_class, label))
        out.append('</section>')
    return "\n".join(out), "\n".join(subnav), total_q, total_cevap


def extract_mikro(html_text):
    start = html_text.index('<section id="sec-27final">')
    end = html_text.index('<footer>')
    body = html_text[start:end].rstrip()

    subnav = []
    for anchor, emoji, badge_class, label in MIKRO_SECTIONS:
        m = re.search(
            r'<section id="' + re.escape(anchor) + r'">\s*<h2 class="section-title">.*?<span class="badge ' + re.escape(badge_class) + r'">(\d+) soru</span>',
            html_text, re.DOTALL,
        )
        count = m.group(1) if m else "?"
        subnav.append(f'<a href="#{anchor}">{emoji} {label} ({count})</a>')
    return body, "\n".join(subnav)


def main():
    fizyo_sections = parse_fizyo(SRC_FIZYO.read_text(encoding="utf-8"))
    fizyo_html, fizyo_subnav, fizyo_total, fizyo_cevap = build_fizyo_sections(fizyo_sections)

    mikro_html_raw = SRC_MIKRO_HTML.read_text(encoding="utf-8")
    mikro_body, mikro_subnav = extract_mikro(mikro_html_raw)
    mikro_total_m = re.search(r'<div class="num">(\d+)</div>\s*<div class="label">Toplam soru</div>', mikro_html_raw)
    mikro_cevap_m = re.search(r'<div class="num">(\d+)</div>\s*<div class="label">Cevabı bulunan</div>', mikro_html_raw)
    mikro_total = mikro_total_m.group(1) if mikro_total_m else "?"
    mikro_cevap = mikro_cevap_m.group(1) if mikro_cevap_m else "?"

    grand_total = int(mikro_total) + fizyo_total
    grand_cevap = int(mikro_cevap) + fizyo_cevap

    page = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dönem 3 Soru Bankası – Mikrobiyoloji &amp; Fizyopatoloji Çıkmış Soruları</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

<header class="hero">
  <h1>📚 Dönem 3 Soru Bankası</h1>
  <p>Mikrobiyoloji ve Fizyopatoloji çıkmış soruları tek sayfada – {grand_total} soru</p>
  <p style="font-size:.8rem; opacity:.75;">27, 26, 25, 24, 23. Dönem Final (+ 26. Dönem Bütünleme) ile 29 D3M1-D3M5 modül sınavlarından derlendi. Her sorunun altındaki "Cevabı Gör" kutusuna tıklayarak doğru cevabı görebilirsin.</p>
  <div class="search-wrap">
    <input type="text" id="searchInput" placeholder="🔍 Soru, etken veya cevap ara..." oninput="microSearch(this.value)" autocomplete="off">
  </div>
</header>

<nav class="toc">
  <a href="#ozet">📊 Özet</a>
  <a href="#mikrobiyoloji">🦠 Mikrobiyoloji Soruları</a>
  <a href="#fizyopatoloji">🩺 Fizyopatoloji Soruları</a>
</nav>

<main>

<section id="ozet">
<h2 class="section-title">📊 Soru Bankası Özeti</h2>
<p class="section-desc">Bu sayfa, Mikrobiyoloji/Parazitoloji/Viroloji/Mikoloji/İmmünoloji ve Fizyopatoloji konularındaki çıkmış soruları tek bir aranabilir sayfada birleştirir.</p>

<div class="stat-grid">
  <div class="stat-box"><div class="num">{grand_total}</div><div class="label">Toplam soru</div></div>
  <div class="stat-box"><div class="num">{mikro_total}</div><div class="label">Mikrobiyoloji</div></div>
  <div class="stat-box"><div class="num">{fizyo_total}</div><div class="label">Fizyopatoloji</div></div>
  <div class="stat-box"><div class="num">{grand_cevap}</div><div class="label">Cevabı bulunan</div></div>
</div>

<h3>🦠 Mikrobiyoloji bölümleri</h3>
<div class="subnav">
{mikro_subnav}
</div>

<h3>🩺 Fizyopatoloji bölümleri</h3>
<div class="subnav">
{fizyo_subnav}
</div>

<div class="note">📌 <b>Nasıl kullanılır:</b> Her kart bir soruyu (kökü + şıkları) gösterir. "✅ Cevabı Gör" yazısına tıkladığında doğru cevap (yeşil kutu) açılır. Sarı kutular <b>"(emin değil)"</b> işaretli, tartışmalı/teyide açık cevaplardır. Üstteki arama kutusu bu sayfadaki tüm soru, şık ve cevap metinlerinde arama yapar.</div>
</section>

<h2 id="mikrobiyoloji" class="subject-divider">🦠 Mikrobiyoloji Soruları ({mikro_total})</h2>

{mikro_body}

<h2 id="fizyopatoloji" class="subject-divider">🩺 Fizyopatoloji Soruları ({fizyo_total})</h2>

{fizyo_html}

</main>

<footer>
<p>📚 Dönem 3 Soru Bankası — Mikrobiyoloji bölümü <a href="../mikrosorulari.html" style="color:#5eead4;">Mikrobiyoloji Çalışma Rehberi</a>'nden, Fizyopatoloji bölümü "fizyopato soruları.txt" kaynağından derlenmiştir.</p>
</footer>

<script src="search.js"></script>
</body>
</html>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"Yazıldı: {OUT}")
    print(f"Mikro: {mikro_total} soru (cevaplı: {mikro_cevap})")
    print(f"Fizyopato: {fizyo_total} soru (cevaplı: {fizyo_cevap})")
    print(f"Toplam: {grand_total} soru (cevaplı: {grand_cevap})")


if __name__ == "__main__":
    main()
