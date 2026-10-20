#!/usr/bin/env python3
"""Builds the profile README graphics (light + dark) and the stack icon block.

Edit the data below, then run:  python3 assets/build.py
"""
import json
import random
import re
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent
README = OUT.parent / "README.md"

THEMES = {
    "dark": dict(card="#11161d", border="#2a313c", text="#e6edf3", muted="#9198a1",
                 faint="#1a2029", accent="#ff7a45", accent2="#ffb86b", glow=".16",
                 cells=["#1f252e", "#5a2e1c", "#9a4423", "#d9602e", "#ff7a45"]),
    "light": dict(card="#f8f9fb", border="#d8dee4", text="#1f2328", muted="#59636e",
                  faint="#eef1f4", accent="#c94a14", accent2="#e8873a", glow=".10",
                  cells=["#eef1f4", "#fbd3bd", "#f5a57a", "#e2703d", "#c94a14"]),
}

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

# The wide card at the top of the grid.
HERO = dict(slug="onescan", name="OneScan Menu", tag="SaaS · live", live=True,
            link="onescan.menu",
            lines=["Multi-tenant SaaS for restaurants: QR menus,",
                   "table reservations and kitchen-to-table ordering.",
                   "16 menu templates, in any language."],
            stack=["Next.js", "PostgreSQL", "Drizzle", "Better Auth", "Stripe", "next-intl"],
            qr="qr-onescan.json")

# The 2x2 grid below it, in reading order.
PROJECTS = [
    dict(slug="tin-ai-hub", name="Tin AI Hub", tag="self-hosted",
         lines=["Private mobile AI hub on local models.",
                "Legal, coder and marketer agents with memory."],
         stack=["Hono", "Next.js", "pgvector", "MCP"]),
    dict(slug="rtr", name="RTR Engineering", tag="client · live", live=True, link=True,
         lines=["Company website for an engineering firm,",
                "with a CMS the team edits themselves."],
         stack=["React", "Strapi", "Docker", "Caddy"]),
    dict(slug="neural-trader", name="Neural Trader", tag="trading",
         lines=["Intraday and swing trading bot with backtests,",
                "local-LLM checks and a live dashboard."],
         stack=["Node.js", "SQLite", "IBKR", "Docker"]),
    dict(slug="pricewatch", name="PriceWatch", tag="self-hosted",
         lines=["Tracks prices and store promotions, plus",
                "second-hand and Bulgarian real estate."],
         stack=["FastAPI", "React", "SQLite", "Playwright"]),
]

# Icons from skillicons.dev, in reading order. (id, tooltip)
ICONS = [
    ("ts", "TypeScript"), ("js", "JavaScript"), ("python", "Python"),
    ("react", "React"), ("nextjs", "Next.js"), ("tailwind", "Tailwind CSS"),
    ("sass", "Sass / SCSS"), ("nodejs", "Node.js"), ("fastapi", "FastAPI"),
    ("graphql", "GraphQL"), ("postgres", "PostgreSQL"), ("mongodb", "MongoDB"),
    ("sqlite", "SQLite"), ("docker", "Docker"), ("cloudflare", "Cloudflare"),
    ("linux", "Linux"), ("git", "Git"), ("jest", "Jest"),
]

STYLE = """<style>
    .pulse { animation: pulse 2.4s ease-out infinite; transform-box: fill-box; transform-origin: center; }
    @keyframes pulse { 0% { transform: scale(1); opacity: .55; } 80%, 100% { transform: scale(2.6); opacity: 0; } }
    .cell { animation: pop .5s ease-out both; }
    @keyframes pop { from { opacity: 0; } }
    .cursor { animation: blink 1.1s steps(1) infinite; }
    @keyframes blink { 50% { opacity: 0; } }
    @media (prefers-reduced-motion: reduce) { .pulse, .cell, .cursor { animation: none; } }
  </style>"""


def frame(w, h, t, glow_x, glow_y):
    """Card background: border plus a soft accent glow in one corner."""
    return f'''<defs>
    <radialGradient id="glow" cx="{glow_x}" cy="{glow_y}" r="0.75">
      <stop offset="0" stop-color="{t["accent"]}" stop-opacity="{t["glow"]}"/>
      <stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{t["accent"]}"/><stop offset="1" stop-color="{t["accent2"]}"/></linearGradient>
  </defs>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="16" fill="{t["card"]}"/>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="16" fill="url(#glow)" stroke="{t["border"]}"/>'''


def eyebrow(x, y, p, t):
    """Small mono label above the title, with a pulsing dot for live projects."""
    label = escape(p["tag"].upper())
    dot = (f'<circle class="pulse" cx="{x + 4}" cy="{y - 4}" r="4" fill="{t["accent"]}"/>'
           if p.get("live") else "")
    return (f'{dot}<circle cx="{x + 4}" cy="{y - 4}" r="4" fill="{t["accent"]}"/>'
            f'<text x="{x + 16}" y="{y}" font-family="{MONO}" font-size="12" letter-spacing="1.2" '
            f'fill="{t["accent"]}">{label}</text>')


def pills(x, y, items, t):
    out = []
    for s in items:
        pw = 18 + len(s) * 7.6
        out.append(
            f'<rect x="{x:.0f}" y="{y}" width="{pw:.0f}" height="26" rx="13" fill="{t["faint"]}" stroke="{t["border"]}"/>'
            f'<text x="{x + pw / 2:.0f}" y="{y + 17.5}" text-anchor="middle" font-family="{MONO}" '
            f'font-size="12.5" fill="{t["muted"]}">{escape(s)}</text>')
        x += pw + 8
    return "".join(out)


def lines(x, y, rows, t, size=15.5, step=24):
    return "".join(
        f'<text x="{x}" y="{y + i * step}" font-family="{SANS}" font-size="{size}" fill="{t["muted"]}">{escape(r)}</text>'
        for i, r in enumerate(rows))


def arrow(x, y, t):
    """Top-right ↗ hint that the card is a link."""
    return (f'<path d="M{x} {y + 10}L{x + 10} {y}M{x + 2} {y}H{x + 10}V{y + 8}" fill="none" '
            f'stroke="{t["muted"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')


def svg(w, h, label, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(label)}">\n  {STYLE}\n  {body}\n</svg>\n')


def header(t):
    w, h = 1200, 300
    rnd = random.Random(7)
    # Contribution-graph motif on the right, fading in toward the edge.
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
            cells.append(
                f'<rect class="cell" style="animation-delay:{(c * rows + r) * 0.012:.3f}s" '
                f'x="{x0 + c * (size + gap)}" y="{y0 + r * (size + gap)}" width="{size}" height="{size}" '
                f'rx="4" fill="{t["cells"][level]}" opacity="{0.25 + 0.75 * fade:.2f}"/>')
    body = f'''{frame(w, h, t, "0.95", "0.5")}
  {"".join(cells)}
  <text x="56" y="92" font-family="{MONO}" font-size="18" fill="{t["muted"]}">~ $ whoami<tspan class="cursor" fill="{t["accent"]}"> ▍</tspan></text>
  <text x="54" y="160" font-family="{SANS}" font-size="62" font-weight="700" fill="{t["text"]}" letter-spacing="-1.5">Vasil Tinev</text>
  <rect x="56" y="182" width="72" height="5" rx="2.5" fill="url(#g)"/>
  <text x="56" y="226" font-family="{SANS}" font-size="24" fill="{t["text"]}">Full-stack web developer</text>
  <text x="56" y="258" font-family="{SANS}" font-size="18" fill="{t["muted"]}">Web products, SaaS and self-hosted AI tools</text>'''
    return svg(w, h, "Vasil Tinev, full-stack web developer", body)


def hero(p, t):
    w, h = 900, 250
    rows = json.loads((OUT / p["qr"]).read_text())
    n, quiet = len(rows), 2
    tile, pad = 186, 14
    cell = (tile - 2 * pad) / (n + 2 * quiet)
    tx, ty = w - 32 - tile, (h - tile) // 2
    # QR stays dark-on-white in both themes so phones can always scan it.
    mods = "".join(
        f'<rect x="{tx + pad + (x + quiet) * cell:.2f}" y="{ty + pad + (y + quiet) * cell:.2f}" '
        f'width="{cell + 0.05:.2f}" height="{cell + 0.05:.2f}"/>'
        for y, r in enumerate(rows) for x, v in enumerate(r) if v == "1")
    body = f'''{frame(w, h, t, "0.0", "0.0")}
  {eyebrow(32, 46, p, t)}
  <text x="32" y="90" font-family="{SANS}" font-size="30" font-weight="700" fill="{t["text"]}" letter-spacing="-0.5">{escape(p["name"])}</text>
  <text x="{tx - 44}" y="46" text-anchor="end" font-family="{MONO}" font-size="14" fill="{t["accent"]}">{escape(p["link"])}</text>
  {arrow(tx - 36, 34, t)}
  {lines(32, 126, p["lines"], t, size=16.5, step=25)}
  {pills(32, 196, p["stack"], t)}
  <rect x="{tx}" y="{ty}" width="{tile}" height="{tile}" rx="14" fill="#ffffff" stroke="{t["border"]}"/>
  <g fill="#14181f">{mods}</g>'''
    return svg(w, h, f'{p["name"]}: {" ".join(p["lines"])}', body)


def card(p, t):
    w, h = 440, 206
    body = f'''{frame(w, h, t, "1.0", "0.0")}
  {eyebrow(28, 42, p, t)}
  {arrow(w - 40, 32, t) if p.get("link") else ""}
  <text x="28" y="78" font-family="{SANS}" font-size="22" font-weight="650" fill="{t["text"]}">{escape(p["name"])}</text>
  {lines(28, 110, p["lines"], t)}
  {pills(28, 160, p["stack"], t)}'''
    return svg(w, h, f'{p["name"]}: {" ".join(p["lines"])}', body)


def icon_block():
    """One <picture> per icon so each gets its own hover tooltip (title)."""
    tags = []
    for i, name in ICONS:
        base = f"https://skillicons.dev/icons?i={i}&theme="
        tags.append(
            f'<picture><source media="(prefers-color-scheme: dark)" srcset="{base}dark">'
            f'<img src="{base}light" alt="{name}" title="{name}" width="44" height="44"></picture>')
    return "<p>\n" + "\n".join(tags) + "\n</p>"


for name, t in THEMES.items():
    (OUT / f"header-{name}.svg").write_text(header(t))
    (OUT / f"{HERO['slug']}-{name}.svg").write_text(hero(HERO, t))
    for p in PROJECTS:
        (OUT / f"{p['slug']}-{name}.svg").write_text(card(p, t))

readme = README.read_text()
new = re.sub(r"(<!-- icons:start -->).*?(<!-- icons:end -->)",
             lambda m: m.group(1) + "\n" + icon_block() + "\n" + m.group(2), readme, flags=re.S)
README.write_text(new)
print("built", len(list(OUT.glob("*.svg"))), "svgs; icons", "updated" if new != readme else "unchanged")
