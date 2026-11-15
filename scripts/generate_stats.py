#!/usr/bin/env python3
"""Generate self-hosted GitHub stats cards (SVG) -- no third-party image server.

Writes:
  assets/stats.svg      - stars / commits / PRs / issues / repos / followers
  assets/languages.svg  - top languages by bytes across your own (non-fork) repos

Needs only the Python standard library. Reads GITHUB_TOKEN and GH_USER from the
environment. Use `--demo` to render with sample data (no network).
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from html import escape

API = "https://api.github.com"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

# "radical" colours, same look as the old cards
BG, BORDER = "#141321", "#e4e2e2"
TITLE, TEXT, ICON, MUTED = "#fe428e", "#a9fef7", "#f8d847", "#6b7a90"
LANG_COLORS = [
    "#fe428e", "#f8d847", "#a9fef7", "#8b5cf6", "#38bdf8",
    "#fb923c", "#4ade80", "#f472b6",
]
EXCLUDE_LANGS = {"Jupyter Notebook"}  # set to {} to include notebooks


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
        "name": "Ramiz", "stars": 12, "repos": 24, "followers": 58,
        "commits": 934, "prs": 41, "issues": 9,
        "langs": {"Python": 520000, "Jupyter Notebook": 900000, "JavaScript": 140000,
                  "Shell": 60000, "HTML": 45000, "C#": 30000},
    }


def svg_wrap(w, h, title, body, desc):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">
  <title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>
  <style>
    .title{{font:600 18px 'Segoe UI',Ubuntu,Sans-Serif;fill:{TITLE}}}
    .lbl{{font:400 14px 'Segoe UI',Ubuntu,Sans-Serif;fill:{TEXT}}}
    .val{{font:700 14px 'Segoe UI',Ubuntu,Sans-Serif;fill:{TEXT}}}
    .pct{{font:400 12px 'Segoe UI',Ubuntu,Sans-Serif;fill:{MUTED}}}
    .ico{{fill:{ICON}}}
  </style>
  <rect x="0.5" y="0.5" rx="4.5" width="{w-1}" height="{h-1}" fill="{BG}" stroke="{BORDER}" stroke-opacity="0.35"/>
  <text x="25" y="35" class="title">{escape(title)}</text>
{body}
</svg>
"""


def stats_card(d):
    rows = [
        ("Total Stars Earned", d["stars"]),
        ("Total Commits", d["commits"]),
        ("Total PRs", d["prs"]),
        ("Total Issues", d["issues"]),
        ("Public Repos", d["repos"]),
        ("Followers", d["followers"]),
    ]
    body = []
    for i, (label, value) in enumerate(rows):
        y = 70 + i * 25
        body.append(f'  <circle cx="33" cy="{y-5}" r="4" class="ico"/>')
        body.append(f'  <text x="48" y="{y}" class="lbl">{escape(label)}:</text>')
        body.append(f'  <text x="250" y="{y}" class="val">{value:,}</text>')
    h = 70 + len(rows) * 25 + 5
    return svg_wrap(350, h, f"{d['name']}'s GitHub Stats", "\n".join(body),
                    ", ".join(f"{k}: {v}" for k, v in rows))


def langs_card(d, top=6):
    langs = {k: v for k, v in d["langs"].items() if k not in EXCLUDE_LANGS}
    total = sum(langs.values()) or 1
    ranked = sorted(langs.items(), key=lambda kv: kv[1], reverse=True)[:top]
    shown_total = sum(v for _, v in ranked) or 1
    bar_x, bar_w = 25, 300
    body, x = [], bar_x
    body.append(f'  <clipPath id="c"><rect x="{bar_x}" y="55" width="{bar_w}" height="10" rx="5"/></clipPath>')
    body.append('  <g clip-path="url(#c)">')
    for i, (_, size) in enumerate(ranked):
        w = bar_w * size / shown_total
        body.append(f'    <rect x="{x:.2f}" y="55" width="{w:.2f}" height="10" fill="{LANG_COLORS[i % len(LANG_COLORS)]}"/>')
        x += w
    body.append("  </g>")
    for i, (name, size) in enumerate(ranked):
        col, row = i % 2, i // 2
        cx, cy = 25 + col * 160, 95 + row * 25
        color = LANG_COLORS[i % len(LANG_COLORS)]
        body.append(f'  <circle cx="{cx+5}" cy="{cy-4}" r="5" fill="{color}"/>')
        body.append(f'  <text x="{cx+16}" y="{cy}" class="lbl">{escape(name)}</text>')
        body.append(f'  <text x="{cx+140}" y="{cy}" text-anchor="end" class="pct">{size/total*100:.1f}%</text>')
    h = 95 + ((len(ranked) + 1) // 2) * 25 + 10
    return svg_wrap(350, h, "Top Languages", "\n".join(body),
                    ", ".join(f"{n} {s/total*100:.1f}%" for n, s in ranked))


def main():
    data = demo() if "--demo" in sys.argv else fetch(os.environ.get("GH_USER", "ramizpa"))
    os.makedirs(OUT, exist_ok=True)
    for name, svg in (("stats.svg", stats_card(data)), ("languages.svg", langs_card(data))):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(svg)
        print("wrote", name)


if __name__ == "__main__":
    main()
