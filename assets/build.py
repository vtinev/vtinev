#!/usr/bin/env python3
"""Builds the profile README graphics (light + dark versions).

Edit the data below, then run:  python3 assets/build.py
"""
import random
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent

THEMES = {
    "dark": dict(bg="#0d1117", card="#151b23", border="#30363d", text="#e6edf3",
                 muted="#9198a1", faint="#21262d", accent="#ff7a45", accent2="#ffb86b",
                 cells=["#21262d", "#5a2e1c", "#9a4423", "#d9602e", "#ff7a45"]),
    "light": dict(bg="#ffffff", card="#f6f8fa", border="#d1d9e0", text="#1f2328",
                  muted="#59636e", faint="#eff2f5", accent="#c94a14", accent2="#e8873a",
                  cells=["#eff2f5", "#fbd3bd", "#f5a57a", "#e2703d", "#c94a14"]),
}

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

PROJECTS = [
    dict(slug="onescan", name="OneScan Menu", tag="SaaS · live",
         lines=["QR-scannable digital menus for restaurants.",
                "6 languages, 12 menu templates, Stripe billing."],
         stack=["Next.js", "Drizzle", "Postgres", "Stripe"]),
    dict(slug="tin-ai-hub", name="Tin AI Hub", tag="self-hosted",
         lines=["Private mobile AI hub on local models.",
                "Legal, coder and marketer agents with memory."],
         stack=["Hono", "Next.js", "pgvector", "MCP"]),
    dict(slug="neural-trader", name="Neural Trader", tag="trading",
         lines=["Intraday and swing trading bot with backtests,",
                "local-LLM checks and a live dashboard."],
         stack=["Node.js", "SQLite", "IBKR", "Docker"]),
    dict(slug="pricewatch", name="PriceWatch", tag="self-hosted",
         lines=["Tracks prices for products, second-hand and",
                "Bulgarian real estate, with Telegram alerts."],
         stack=["FastAPI", "React", "SQLite", "Playwright"]),
]


def header(t):
    w, h = 1200, 300
    rnd = random.Random(7)
    # Contribution-graph motif on the right, fading out toward the text.
    cols, rows, size, gap = 26, 7, 18, 5
    x0 = w - 48 - cols * (size + gap) + gap
    y0 = (h - (rows * (size + gap) - gap)) // 2
    cells = []
    for c in range(cols):
        fade = c / (cols - 1)
        for r in range(rows):
            level = 0
            if rnd.random() < 0.25 + 0.6 * fade:
                level = min(4, 1 + int(rnd.random() * 4 * (0.4 + fade)))
            delay = round((c * rows + r) * 0.012, 3)
            cells.append(
                f'<rect class="cell" style="animation-delay:{delay}s" x="{x0 + c * (size + gap)}" '
                f'y="{y0 + r * (size + gap)}" width="{size}" height="{size}" rx="4" '
                f'fill="{t["cells"][level]}" opacity="{0.25 + 0.75 * fade:.2f}"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Vasil Tinev, full-stack web developer">
  <style>
    .cell {{ animation: pop .5s ease-out both; }}
    @keyframes pop {{ from {{ opacity: 0; }} }}
    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{ .cell, .cursor {{ animation: none; }} }}
  </style>
  <defs>
    <linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{t["accent2"]}"/></linearGradient>
  </defs>
  <rect width="{w}" height="{h}" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>
  {"".join(cells)}
  <text x="56" y="92" font-family="{MONO}" font-size="18" fill="{t["muted"]}">~ $ whoami<tspan class="cursor" fill="{t["accent"]}"> ▍</tspan></text>
  <text x="54" y="160" font-family="{SANS}" font-size="62" font-weight="700" fill="{t["text"]}" letter-spacing="-1.5">Vasil Tinev</text>
  <rect x="56" y="182" width="72" height="5" rx="2.5" fill="url(#g)"/>
  <text x="56" y="226" font-family="{SANS}" font-size="24" fill="{t["text"]}">Full-stack web developer</text>
  <text x="56" y="258" font-family="{SANS}" font-size="18" fill="{t["muted"]}">Web products, SaaS and self-hosted AI tools</text>
</svg>
'''


def card(p, t):
    w, h = 440, 200
    pills, x = [], 28
    for s in p["stack"]:
        pw = 16 + len(s) * 7.6
        pills.append(
            f'<rect x="{x}" y="148" width="{pw:.0f}" height="26" rx="13" fill="{t["faint"]}" stroke="{t["border"]}"/>'
            f'<text x="{x + pw / 2:.0f}" y="165.5" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="{t["muted"]}">{escape(s)}</text>')
        x += pw + 8
    tag_w = 18 + len(p["tag"]) * 7
    body = "".join(
        f'<text x="28" y="{100 + i * 24}" font-family="{SANS}" font-size="15.5" fill="{t["muted"]}">{escape(l)}</text>'
        for i, l in enumerate(p["lines"]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(p["name"])}">
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="{t["card"]}" stroke="{t["border"]}"/>
  <rect x="28" y="30" width="10" height="10" rx="3" fill="{t["accent"]}"/>
  <text x="48" y="44" font-family="{SANS}" font-size="21" font-weight="650" fill="{t["text"]}">{escape(p["name"])}</text>
  <rect x="{w - 28 - tag_w:.0f}" y="26" width="{tag_w:.0f}" height="24" rx="12" fill="none" stroke="{t["accent"]}" stroke-opacity=".6"/>
  <text x="{w - 28 - tag_w / 2:.0f}" y="42.5" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{t["accent"]}">{escape(p["tag"])}</text>
  {body}
  {"".join(pills)}
</svg>
'''


for name, t in THEMES.items():
    (OUT / f"header-{name}.svg").write_text(header(t))
    for p in PROJECTS:
        (OUT / f"{p['slug']}-{name}.svg").write_text(card(p, t))
print("built", len(list(OUT.glob("*.svg"))), "svgs")
