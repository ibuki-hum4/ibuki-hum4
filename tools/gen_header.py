"""Generate animated terminal-style header SVGs (dark / light) for the profile README."""
import sys
import unicodedata
from pathlib import Path
from xml.sax.saxutils import escape

ACCENT = "#E8452C"
THEMES = {
    "dark": dict(bg="#0a0a0a", border="#262626", bar="#141414", text="#e6e6e6", muted="#8a8a8a"),
    "light": dict(bg="#ffffff", border="#d0d7de", bar="#f6f8fa", text="#0a0a0a", muted="#6e7781"),
}

W, H = 820, 290
FS = 15
ASCII_W = FS * 0.6
WIDE_W = FS * 1.0
LINE_H = 26
X0 = 28
Y0 = 74
CPS = 28  # typed characters per second

# (kind, segments) — kind "cmd" is typed, "out" appears at once
LINES = [
    ("cmd", [("accent", "$ "), ("text", "whoami")]),
    ("out", [("text", "やーはり / Yāhari"), ("muted", "  —  Full-Stack · Infrastructure · Japan")]),
    ("cmd", [("accent", "$ "), ("text", "cat now.txt")]),
    ("out", [("muted", "building  "), ("accent", "senr/"), ("text", " Senri 千里 — a Web Standards framework for every runtime")]),
    ("out", [("muted", "running   "), ("text", "HoshID · bare-metal Kubernetes · Proxmox")]),
    ("cmd", [("accent", "$ "), ("text", "echo $PHILOSOPHY")]),
    ("out", [("text", "Build things that are useful, reliable, and maintainable.")]),
]


def text_width(s: str) -> float:
    return sum(WIDE_W if unicodedata.east_asian_width(c) in "WF" else ASCII_W for c in s)


def build(theme: str) -> str:
    t = THEMES[theme]
    color = {"accent": ACCENT, "text": t["text"], "muted": t["muted"]}
    defs, body = [], []
    clock = 0.6
    for i, (kind, segs) in enumerate(LINES):
        y = Y0 + i * LINE_H
        full = "".join(s for _, s in segs)
        width = text_width(full) + 4
        if kind == "cmd":
            n = len(full)
            dur = max(n / CPS, 0.25)
        else:
            dur = 0.01
        tspans = "".join(f'<tspan fill="{color[c]}">{escape(s)}</tspan>' for c, s in segs)
        defs.append(
            f'<clipPath id="c{i}"><rect x="{X0 - 2}" y="{y - FS}" width="0" height="{LINE_H}">'
            f'<animate attributeName="width" from="0" to="{width:.1f}" begin="{clock:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
            f"</rect></clipPath>"
        )
        body.append(f'<text x="{X0}" y="{y}" clip-path="url(#c{i})" xml:space="preserve">{tspans}</text>')
        clock += dur + (0.35 if kind == "cmd" else 0.15)

    # final blinking cursor prompt
    y = Y0 + len(LINES) * LINE_H
    body.append(
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{clock:.2f}s" dur="0.01s" fill="freeze"/>'
        f'<text x="{X0}" y="{y}" fill="{ACCENT}">$</text>'
        f'<rect x="{X0 + ASCII_W * 2:.1f}" y="{y - FS + 2}" width="{ASCII_W:.1f}" height="{FS + 2}" fill="{t["text"]}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/>'
        f"</rect></g>"
    )

    dots = "".join(
        f'<circle cx="{24 + k * 18}" cy="22" r="6" fill="{c}"/>'
        for k, c in enumerate(["#ff5f57", "#febc2e", "#28c840"])
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="やーはり / Yāhari — Full-Stack Developer, Infrastructure Engineer">
<title>やーはり / Yāhari</title>
<defs>{''.join(defs)}</defs>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{t['bg']}" stroke="{t['border']}"/>
<path d="M0.5 44 V10.5 a10 10 0 0 1 10 -10 H{W - 10.5} a10 10 0 0 1 10 10 V44 Z" fill="{t['bar']}" stroke="{t['border']}"/>
{dots}
<text x="{W / 2}" y="27" text-anchor="middle" fill="{t['muted']}" font-family="'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="12">ibuki-hum4@github: ~</text>
<g font-family="'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, 'Noto Sans Mono CJK JP', monospace" font-size="{FS}">
{chr(10).join(body)}
</g>
</svg>
"""


def main(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (out / f"header-{theme}.svg").write_text(build(theme), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
