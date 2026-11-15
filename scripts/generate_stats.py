#!/usr/bin/env python3
"""Generate self-hosted GitHub stats cards (SVG) -- no third-party image server.

Writes:
  assets/stats-light.svg, assets/stats-dark.svg - one card: commits hero number,
  repo/star/PR tiles and a language donut (top languages by bytes, non-fork repos)

Needs only the Python standard library. Reads GITHUB_TOKEN and GH_USER from the
environment. Use --demo to render with sample data (no network).
"""
import json
import math
import os
import sys
import urllib.parse
import urllib.request
from html import escape

API = "https://api.github.com"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

EXCLUDE_LANGS = {"Jupyter Notebook"}  # set to set() to include notebooks
TOP_N = 6

THEMES = {
    "light": dict(bg="#ffffff", border="#d0d7de", text="#1f2328", sec="#656d76", tile="#f6f8fa",
                  series=["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6"]),
    "dark": dict(bg="#0d1117", border="#30363d", text="#e6edf3", sec="#8b949e", tile="#161b22",
                 series=["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#9085e9"]),
}


def gh(path, params=None):
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-stats-generator",
        **({"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}
           if os.environ.get("GITHUB_TOKEN") else {}),
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch(user):
    profile = gh(f"/users/{user}")
    repos, page = [], 1
    while True:
        batch = gh(f"/users/{user}/repos", {"per_page": 100, "page": page, "type": "owner"})
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    own = [r for r in repos if not r["fork"]]

    langs = {}
    for r in own:
        try:
            for name, size in gh(f"/repos/{user}/{r['name']}/languages").items():
                langs[name] = langs.get(name, 0) + size
        except Exception as exc:  # one bad repo should not kill the card
            print(f"warn: languages for {r['name']}: {exc}", file=sys.stderr)

    def count(path, q):
        try:
            return gh(path, {"q": q, "per_page": 1})["total_count"]
        except Exception as exc:
            print(f"warn: {q}: {exc}", file=sys.stderr)
            return 0

    return {
        "name": profile.get("name") or user,
        "stars": sum(r["stargazers_count"] for r in own),
        "repos": profile["public_repos"],
        "followers": profile["followers"],
        "commits": count("/search/commits", f"author:{user}"),
        "prs": count("/search/issues", f"author:{user} type:pr"),
        "issues": count("/search/issues", f"author:{user} type:issue"),
        "langs": langs,
    }


def demo():
    return {
        "name": "Ramiz P A", "stars": 2, "repos": 16, "followers": 0,
        "commits": 113, "prs": 1, "issues": 0,
        "langs": {"TypeScript": 588, "Python": 183, "Astro": 94, "Batchfile": 39,
                  "PowerShell": 30, "CSS": 23},
    }


def card(d, theme):
    t = THEMES[theme]
    langs = {k: v for k, v in d["langs"].items() if k not in EXCLUDE_LANGS}
    total = sum(langs.values()) or 1
    ranked = sorted(langs.items(), key=lambda kv: kv[1], reverse=True)[:TOP_N]
    shown = sum(v for _, v in ranked) or 1

    circ = 2 * math.pi * 44
    segs, start = [], 0.0
    for i, (_, size) in enumerate(ranked):
        share = size / shown
        seg = max(share * circ - 2.2, 0.6)  # small gap between segments
        segs.append(
            f'<circle cx="60" cy="60" r="44" stroke="{t["series"][i]}" '
            f'stroke-dasharray="{seg:.2f} {circ:.2f}" stroke-dashoffset="{-start * circ:.2f}"/>')
        start += share

    tiles = [("Repos", d["repos"]), ("Stars", d["stars"]), ("Pull requests", d["prs"])]
    tile_svg = []
    for i, (label, value) in enumerate(tiles):
        x = 265 + i * 128
        tile_svg.append(
            f'<rect x="{x}" y="66" width="118" height="54" rx="8" fill="{t["tile"]}"/>'
            f'<text x="{x+12}" y="86" class="sec sm">{escape(label)}</text>'
            f'<text x="{x+12}" y="110" class="val">{value:,}</text>')

    legend = []
    for i, (name, size) in enumerate(ranked):
        col, row = i % 2, i // 2
        x, y = 265 + col * 190, 160 + row * 26
        legend.append(
            f'<rect x="{x}" y="{y-9}" width="10" height="10" rx="2" fill="{t["series"][i]}"/>'
            f'<text x="{x+18}" y="{y}" class="body">{escape(name)}</text>'
            f'<text x="{x+170}" y="{y}" text-anchor="end" class="sec body">{size/total*100:.1f}%</text>')

    desc = (f"{d['commits']} commits, {d['repos']} repos, {d['stars']} stars, {d['prs']} pull requests. "
            "Top languages: " + ", ".join(f"{n} {s/total*100:.1f}%" for n, s in ranked))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="660" height="252" viewBox="0 0 660 252" role="img" aria-labelledby="t d">
<title id="t">{escape(d['name'])} on GitHub</title><desc id="d">{escape(desc)}</desc>
<style>
text{{font-family:'Segoe UI',-apple-system,Helvetica,Arial,sans-serif;fill:{t['text']}}}
.sec{{fill:{t['sec']}}} .sm{{font-size:12px}} .body{{font-size:13px}}
.title{{font-size:16px;font-weight:600}} .val{{font-size:22px;font-weight:600}}
.hero{{font-family:Georgia,'Times New Roman',serif;font-size:34px}}
</style>
<rect x="0.5" y="0.5" width="659" height="251" rx="12" fill="{t['bg']}" stroke="{t['border']}"/>
<g transform="translate(30 36) scale(1.6667)">
<g transform="rotate(-90 60 60)" fill="none" stroke-width="14">{''.join(segs)}</g>
<text x="60" y="62" text-anchor="middle" class="hero" style="font-size:22px">{d['commits']:,}</text>
<text x="60" y="76" text-anchor="middle" class="sec" style="font-size:8px">commits</text>
</g>
<text x="265" y="36" class="title">{escape(d['name'])} on GitHub</text>
<text x="630" y="36" text-anchor="end" class="sec sm">{d['issues']} issues · {d['followers']} followers</text>
{''.join(tile_svg)}
<line x1="265" y1="138" x2="630" y2="138" stroke="{t['border']}"/>
{''.join(legend)}
</svg>
"""


def main():
    data = demo() if "--demo" in sys.argv else fetch(os.environ.get("GH_USER", "ramizpa"))
    os.makedirs(OUT, exist_ok=True)
    for theme in THEMES:
        name = f"stats-{theme}.svg"
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(card(data, theme))
        print("wrote", name)


if __name__ == "__main__":
    main()
