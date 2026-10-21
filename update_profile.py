"""Regenerate dark_mode.svg / light_mode.svg with live GitHub stats.

Inspired by https://github.com/DietrichGebert/DietrichGebert
Runs daily via GitHub Actions. Stdlib only, no external dependencies.
"""

import calendar
import html
import json
import os
import ssl
import subprocess
import urllib.request
from datetime import date, datetime, timezone

# ==============================================================================
# PROFILE CONFIGURATION
# ==============================================================================
USER = "abibhaskara"
BIRTHDAY = date(2009, 1, 15)  # Sesuaikan dengan tanggal lahir Anda
JOINED_YEAR = 2024          # Tahun akun GitHub dibuat
W = 56                       # Lebar kolom info dalam karakter

# ASCII Art portrait / logo (lebar ~38-42 karakter, tinggi ~27-28 baris)
ART = r"""
#*######%#=-==.      :#@@@@@@@@@@@@@@@
@*#%###%%#+-==.      :%@@@@@@@@@@@@@@@
@##%##%%%#+===.      :%@@@@@@@@@%%%%%%
@##%#%%%%#+===.   ...:#@%%%%########%%
++#%%%%%%#+===.     ..=##**+=+**%%%*=+
:+#%%%%%%#+==-         .*#*++*##%%%+--
-+##%%%%%#+==        .  .#####%%%#*+**
-*#%###%%#+=:    .-=:    *@%@@@@%%%%@@
-*%#####%#+=-  .:-*+=-: .%@@@@@%%@@@@@
-*%****###+==.-*==*+=+*--@@@@@@@@@@@@@
-*#*****##*+=**#*****##**@@@@@@@@@@@@@
-*#*++=+##*+=+##***+++**#@@@@@@@@@@@@@
-*##++*###*+==+****+=+*%@@@@@@@@@@@@@@
:*#%%#%%%%*+=+:=###****@@@@@@@@@@@@@@@
-*#%%%%%%%*+=+.-**#*++#@@@@@@@@@@@@@@@
=*%%%%%%%%*+==.+#**++**%@@@@@@@@@@@@@@
=*#%%%%%%%*++#%*###****+%@@@@@@@@@@@@@
=+#%%%%%%%%%@@@%##****+*@%%%@@@@@@@@@@
=*%%#%%@@@@@@@@@@%%*%@%@@@@@%%@@@@@@@@
=*##*@@@@@@@@@@@@@@@@@@@@@@@@@@%@@@@@@
-=#+#@@@@@@@@@@@@@@@@@@@@@@@@@@@@%%@@@
::=+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*+++
.:=#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%@*-
..+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*:
:+%@@@@@@@@@@@@@@@@@@@@@@@@@@@%%@@%@@#
:=%@@@@@%@@@@@@@@@@@@@@@@@@@@@%%@@@@@@
:-@@@@@@%@@@@@@@@@@@@@@@@@@@@%%%@@@%==
"""

# ==============================================================================
# AUTHENTICATION & NETWORK
# ==============================================================================
# Priority:
# 1. Environment GITHUB_TOKEN / ACCESS_TOKEN
# 2. Local `gh auth token` fallback for seamless development without manual export
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("ACCESS_TOKEN") or ""
if not TOKEN:
    try:
        TOKEN = subprocess.check_output(["gh", "auth", "token"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        TOKEN = ""

PRIV_TOKEN = os.environ.get("ACCESS_TOKEN") or TOKEN

# Safe SSL context fallback (works across macOS, Linux, and Windows)
try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    try:
        SSL_CTX = ssl.create_default_context()
    except Exception:
        SSL_CTX = None


def gh(url, payload=None, token=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"github-profile-generator/{USER}",
    }
    auth = token or TOKEN
    if auth:
        headers["Authorization"] = f"Bearer {auth}"

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode() if payload else None,
        headers=headers,
    )
    kwargs = {}
    if SSL_CTX is not None:
        kwargs["context"] = SSL_CTX

    with urllib.request.urlopen(req, **kwargs) as r:
        return r.status, json.loads(r.read() or "{}")


def graphql(query, variables=None, token=None):
    _, resp = gh("https://api.github.com/graphql", {"query": query, "variables": variables or {}}, token)
    if resp.get("errors"):
        raise RuntimeError(resp["errors"])
    return resp["data"]


# ==============================================================================
# CALCULATIONS & STATS
# ==============================================================================
def age(b, t):
    years = t.year - b.year - ((t.month, t.day) < (b.month, b.day))
    months = (t.month - b.month - (t.day < b.day)) % 12
    if t.day >= b.day:
        days = t.day - b.day
    else:
        pm_year, pm = (t.year, t.month - 1) if t.month > 1 else (t.year - 1, 12)
        days = calendar.monthrange(pm_year, pm)[1] - b.day + t.day
    return years, months, days


LOC_QUERY = """
query($owner: String!, $name: String!, $id: ID!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    defaultBranchRef { target { ... on Commit {
      history(first: 100, author: {id: $id}, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes { additions deletions }
      }
    } } }
  }
}"""


def loc(repo_names, user_id):
    add = rem = 0
    for name in repo_names:
        cursor = None
        try:
            while True:
                resp = graphql(
                    LOC_QUERY,
                    {"owner": USER, "name": name, "id": user_id, "cursor": cursor},
                    token=PRIV_TOKEN,
                )
                repo = resp.get("repository")
                if not repo:
                    break
                ref = repo.get("defaultBranchRef")
                if ref is None:
                    break  # empty repository
                h = ref["target"]["history"]
                add += sum(n["additions"] for n in h["nodes"])
                rem += sum(n["deletions"] for n in h["nodes"])
                if not h["pageInfo"]["hasNextPage"]:
                    break
                cursor = h["pageInfo"]["endCursor"]
        except Exception as e:
            print(f"loc {name}: {e}")
    return {"loc_add": add, "loc_del": rem, "loc": add - rem}


def fetch_stats():
    curr_year = datetime.now(timezone.utc).year
    yr_aliases = "\n".join(
        f'y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y + 1}-01-01T00:00:00Z")'
        " { totalCommitContributions restrictedContributionsCount }"
        for y in range(JOINED_YEAR, curr_year + 1)
    )
    contrib = graphql(f'query {{ user(login: "{USER}") {{ {yr_aliases} }} }}')["user"]
    commits = sum(
        v["totalCommitContributions"] + v["restrictedContributionsCount"]
        for v in contrib.values()
    )

    u = graphql(f"""
    query {{
      user(login: "{USER}") {{
        id
        followers {{ totalCount }}
        repositories(first: 100, ownerAffiliations: OWNER) {{
          totalCount
          nodes {{ name stargazerCount isFork }}
        }}
        repositoriesContributedTo(first: 1, contributionTypes: [COMMIT, PULL_REQUEST, REPOSITORY]) {{
          totalCount
        }}
      }}
    }}""", token=PRIV_TOKEN)["user"]

    stats = {
        "followers": u["followers"]["totalCount"],
        "repos": u["repositories"]["totalCount"],
        "contributed": u["repositoriesContributedTo"]["totalCount"],
        "stars": sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
        "commits": commits,
    }
    stats.update(loc([n["name"] for n in u["repositories"]["nodes"] if not n["isFork"]], u["id"]))
    return stats


# ==============================================================================
# THEMES & SVG RENDERING
# ==============================================================================
PALETTES = {
    "dark": {
        "bg": "#0d1117",
        "border": "#30363d",
        "art": "#8b949e",
        "h": "#58a6ff",
        "k": "#ffa657",
        "v": "#c9d1d9",
        "d": "#484f58",
        "g": "#3fb950",
        "r": "#f85149",
    },
    "light": {
        "bg": "#ffffff",
        "border": "#d0d7de",
        "art": "#57606a",
        "h": "#0969da",
        "k": "#953800",
        "v": "#24292f",
        "d": "#afb8c1",
        "g": "#1a7f37",
        "r": "#cf222e",
    },
}


def kv(key, val, width=W):
    dots = "." * max(width - len(key) - len(str(val)) - 3, 1)
    return [(f"{key}: ", "k"), (dots + " ", "d"), (str(val), "v")]


def kv2(k1, v1, k2, v2):
    left = kv(k1, v1, 30)
    return left + [(" | ", "d")] + kv(k2, v2, 23)


def rule(title=""):
    label = f"─ {title} " if title else ""
    return [(label, "h"), ("─" * (W - len(label)), "d")]


def info_lines(s):
    y, m, d = age(BIRTHDAY, date.today())
    n = lambda x: f"{x:,}"
    return [
        [(f"{USER.lower()}@github ", "h"), ("─" * (W - len(USER) - 8), "d")],
        [],
        kv("OS", "macOS"),
        kv("Uptime", f"{y} years, {m} months, {d} days"),
        kv("Role", "Student Researcher"),
        kv("IDE", "VS Code, Antigravity"),
        [],
        kv("Languages.Programming", "JavaScript, Python, HTML/CSS"),
        kv("Languages.Human", "Indonesian, English"),
        kv("Hobbies", "Research, System Design"),
        [],
        rule("Contact"),
        kv("Email", "hello@abibhaskara.com"),
        kv("Website", "abibhaskara.com"),
        [],
        rule("GitHub Stats"),
        kv2("Repos", f"{s['repos']} {{Contributed: {s['contributed']}}}", "Stars", n(s["stars"])),
        kv2("Commits", n(s["commits"]), "Followers", n(s["followers"])),
        [
            ("Lines of Code: ", "k"),
            (n(s["loc"]), "v"),
            (" ( ", "d"),
            (n(s["loc_add"]) + "++", "g"),
            (", ", "d"),
            (n(s["loc_del"]) + "--", "r"),
            (" )", "d"),
        ],
    ]


def render(mode, stats):
    p = PALETTES[mode]
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="840" height="500" viewBox="0 0 840 500" '
        'font-family="Consolas, Menlo, monospace" font-size="13px">',
        f'<rect x="0.5" y="0.5" width="839" height="499" rx="10" fill="{p["bg"]}" stroke="{p["border"]}"/>',
    ]
    # Draw ASCII art on left side
    for i, line in enumerate(ART.strip("\n").split("\n")):
        out.append(f'<text x="25" y="{40 + i * 15}" fill="{p["art"]}" xml:space="preserve">{html.escape(line)}</text>')

    # Draw Terminal Info on right side
    for i, segs in enumerate(info_lines(stats)):
        if not segs:
            continue
        spans = "".join(f'<tspan fill="{p[c]}">{html.escape(t)}</tspan>' for t, c in segs)
        out.append(f'<text x="390" y="{45 + i * 21}" xml:space="preserve">{spans}</text>')

    out.append("</svg>")
    return "\n".join(out)


def selfcheck():
    assert age(date(1989, 1, 15), date(2026, 7, 10)) == (37, 5, 25)
    assert age(date(2000, 3, 31), date(2026, 4, 1)) == (26, 0, 1)
    assert age(date(2000, 1, 1), date(2026, 1, 1)) == (26, 0, 0)
    assert len("".join(t for t, _ in kv("OS", "macOS, Linux"))) == W
    assert len("".join(t for t, _ in rule("Contact"))) == W
    assert len("".join(t for t, _ in kv2("Repos", "16 {Contributed: 2}", "Stars", "0"))) == W


if __name__ == "__main__":
    selfcheck()
    print("Selfcheck passed!")
    stats = fetch_stats()
    print("Fetched GitHub stats:", stats)
    for mode in PALETTES:
        with open(f"{mode}_mode.svg", "w", encoding="utf-8") as f:
            f.write(render(mode, stats))
    print("Successfully generated dark_mode.svg and light_mode.svg!")
