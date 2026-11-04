#!/usr/bin/env python3
"""Draws a sprint's map as one self-contained HTML page (references/templates.md → Sprint map): rows are
the app areas the cards touch (their board columns), columns are the waves in run order, each card a tile,
solid arrows for blocker links and dashed ones for "lands after". The arrows are routed here, at right
angles, through the gaps between waves and between areas, so none crosses a card; nothing is placed by hand.

Input, a JSON file:
  {"sprint": name, "project": slug, "due": date, "headline": text (optional), "lede": text (optional),
   "cards": [{"id", "title", "area", "wave", "step", "size", "state", "db", "gets"}],
   "links": [[blocker, blocked]], "after": [[first, then]]}
  state: delivered · doing · paused · waiting. A card with no wave (a sprint's debug card) is left out.
  The road after the last wave comes from the project's recipe (`recipe.py`): the staging card when the
  recipe names one, the production card or the release's own deploy.

Usage:
  sprint_map.py DATA.json [--recipe bandit.yaml] [--out MAP.html]   write the page (stdout without --out)
  sprint_map.py DATA.json --geometry                                print the card boxes and arrow segments as JSON
The page carries <meta name="sprint-map-waves-done" content="1,2">: the waves it drew as done (checker SP12).
Exit codes: 0 ok · 2 bad input.
"""
import argparse
import html
import json
import subprocess
import sys
from pathlib import Path

LEFT, TOP, COLW, NW, NH, PAD, SLOT = 150, 60, 210, 170, 88, 26, 104
PALETTE = [("#4d8a0f", "#e7f3d6", "#8fcf4a", "#1f2d14"), ("#1f6fb8", "#dcebf8", "#6fb2f0", "#142636"),
           ("#b4690e", "#f8ead3", "#f0a94a", "#33240f"), ("#7048c2", "#ebe3f8", "#b39af0", "#251d38"),
           ("#0f766e", "#d5f0ec", "#4fd1c5", "#10302d"), ("#b4235a", "#f9dfe8", "#f07aa8", "#3a1424")]
STATE = {"delivered": "✓ Delivered", "doing": "In progress", "paused": "⏸ Paused", "waiting": ""}


def layout(data):
    cards = [c for c in data.get("cards", []) if c.get("wave")]
    areas = []
    for c in sorted(cards, key=lambda c: (c["wave"], c.get("step", 0))):
        if c.get("area", "Other") not in areas:
            areas.append(c.get("area", "Other"))
    waves = max([c["wave"] for c in cards] or [1])
    # A lane is as tall as its fullest cell; cards in one cell stack.
    cells = {}
    for c in sorted(cards, key=lambda c: c.get("step", 0)):
        cells.setdefault((areas.index(c.get("area", "Other")), c["wave"]), []).append(c)
    rows = [max([len(v) for (a, _), v in cells.items() if a == i] or [1]) for i in range(len(areas))]
    tops, y = [], TOP
    for r in rows:
        tops.append(y)
        y += 2 * PAD + r * SLOT - (SLOT - NH)
    box = {}
    for (a, w), group in cells.items():
        for k, c in enumerate(group):
            x = LEFT + (w - 1) * COLW + (COLW - NW) / 2
            box[c["id"]] = (x, tops[a] + PAD + k * SLOT, NW, NH)
    height = y + 20
    return cards, areas, waves, tops, rows, box, height


def route(box, tops, areas, links, waves):
    """Right-angle paths: out of the source's right edge, along the gutter after its wave, along the gap
    above the target's area, down the gutter before the target's wave, into its left edge."""
    paths, gut, chan = [], {}, {}
    lane_of = {}
    for cid, (x, y, w, h) in box.items():
        lane_of[cid] = max(i for i, t in enumerate(tops) if t <= y)
    for kind, a, b in links:
        if a not in box or b not in box:
            continue
        ax, ay, aw, ah = box[a]
        bx, by, bw, bh = box[b]
        sy, ty = ay + ah / 2, by + bh / 2
        g1 = ax + aw + (COLW - NW) / 2          # gutter after the source's wave
        g2 = bx - (COLW - NW) / 2               # gutter before the target's wave
        k1 = gut.setdefault(round(g1), 0); gut[round(g1)] += 1
        off1 = ((k1 % 7) - 3) * 4
        if abs(g1 - g2) < 1 and lane_of[a] == lane_of[b]:
            pts = [(ax + aw, sy), (g1 + off1, sy), (g1 + off1, ty), (bx, ty)]
        else:
            lane = lane_of[b]
            c = tops[lane] + 6                  # the gap above the target's area
            k2 = chan.setdefault(lane, 0); chan[lane] += 1
            cy = c + ((k2 % 4)) * 4
            k3 = gut.setdefault(round(g2), 0); gut[round(g2)] += 1
            off2 = ((k3 % 7) - 3) * 4
            pts = [(ax + aw, sy), (g1 + off1, sy), (g1 + off1, cy), (g2 + off2, cy), (g2 + off2, ty), (bx, ty)]
        paths.append((kind, a, b, pts))
    return paths


def road(recipe):
    def opt(key):
        here = Path(__file__).resolve().parent / "recipe.py"
        args = [sys.executable, str(here)] + (["--file", recipe] if recipe else []) + ["opt", key]
        r = subprocess.run(args, capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else "none"
    staging = opt("handover.staging.column") != "none"
    production = opt("handover.production.column") != "none"
    steps = [("Merged and pushed", "Each card lands on the trunk; the last wave that changes code pushes it.", False)]
    if staging:
        steps.append(("Staging", "The final push fills the staging card for you to fire.", False))
        steps.append(("You test on staging", "Fixes go through the sprint's debug step.", True))
    else:
        steps.append(("You test", "Fixes go through the sprint's debug step.", True))
    steps.append(("Release", "On your deploy word: release, then the production card for you to fire." if production
                  else "On your deploy word: release runs the deploy, watches it and confirms the running version.", False))
    return steps


def page(data, recipe):
    cards, areas, waves, tops, rows, box, height = layout(data)
    links = [("block", a, b) for a, b in data.get("links", [])] + [("after", a, b) for a, b in data.get("after", [])]
    paths = route(box, tops, areas, links, waves)
    width = LEFT + waves * COLW + 20
    done = sorted({c["wave"] for c in cards} - {c["wave"] for c in cards if c.get("state") != "delivered"})
    color = {a: PALETTE[i % len(PALETTE)] for i, a in enumerate(areas)}
    e = html.escape
    svg = []
    for i, a in enumerate(areas):
        h = 2 * PAD + rows[i] * SLOT - (SLOT - NH)
        svg.append(f'<rect x="0" y="{tops[i] + 4}" width="{width}" height="{h - 8}" rx="10" class="lane l{i}"/>'
                   f'<text x="14" y="{tops[i] + h / 2}" class="lane-label">{e(a)}</text>')
    for w in range(1, waves + 1):
        x = LEFT + (w - 1) * COLW
        if w > 1:
            svg.append(f'<line x1="{x}" y1="{TOP - 10}" x2="{x}" y2="{height - 20}" class="gridline"/>')
        svg.append(f'<text x="{x + COLW / 2}" y="{TOP - 22}" text-anchor="middle" class="wave-label{" done" if w in done else ""}">'
                   f'WAVE {w}{" · DONE" if w in done else ""}</text>')
    for kind, a, b, pts in paths:
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        word = "blocks" if kind == "block" else "lands before"
        svg.append(f'<path d="{d}" class="edge{" order" if kind == "after" else ""}" marker-end="url(#arr)" '
                   f'data-from="{e(a)}" data-to="{e(b)}"><title>{e(a)} {word} {e(b)}</title></path>')
    for c in cards:
        x, y, w, h = box[c["id"]]
        i = areas.index(c.get("area", "Other"))
        title = str(c.get("title", ""))
        cut = title.rfind(" ", 0, 24) if len(title) > 24 else len(title)
        t1, t2 = title[:cut], title[cut:].strip()[:26]
        mark = STATE.get(c.get("state", "waiting"), "")
        svg.append(
            f'<g class="node" tabindex="0" data-id="{e(c["id"])}" role="img" aria-label="{e(c["id"])}, step {c.get("step", "")}, '
            f'wave {c["wave"]}: {e(title)}{", " + e(mark) if mark else ""}">'
            f'<rect class="box b{i}" x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/>'
            f'<rect class="spine s{i}" x="{x}" y="{y}" width="6" height="{h}" rx="3"/>'
            f'<circle class="s{i}" cx="{x + w - 16}" cy="{y + 16}" r="10"/>'
            f'<text x="{x + w - 16}" y="{y + 20}" text-anchor="middle" class="step">{e(str(c.get("step", "")))}</text>'
            f'<text x="{x + 16}" y="{y + 22}" class="id t{i}">{e(c["id"])}</text>'
            f'<text x="{x + 16}" y="{y + 42}" class="ttl">{e(t1)}</text>'
            f'<text x="{x + 16}" y="{y + 58}" class="ttl sub">{e(t2)}</text>'
            f'<text x="{x + 16}" y="{y + 76}" class="meta">{e(str(c.get("size", "")))}</text>'
            + (f'<text x="{x + w - 12}" y="{y + 76}" text-anchor="end" class="meta db">DB</text>' if c.get("db") and not mark else "")
            + (f'<text x="{x + w - 12}" y="{y + 76}" text-anchor="end" class="mark">{e(mark)}</text>' if mark else "")
            + "</g>")
    legend = "".join(f'<span><i class="sw s{i}"></i>{e(a)}</span>' for i, a in enumerate(areas))
    blockers = {}
    for a, b in data.get("links", []):
        blockers.setdefault(b, []).append(a)
    order = "".join(
        f'<tr><td class="n">{e(str(c.get("step", "")))}</td><td class="n">{e(c["id"])}</td><td>{e(str(c.get("gets", "")))}</td>'
        f'<td><span class="chip c{areas.index(c.get("area", "Other"))}">{e(c.get("area", "Other"))}</span></td>'
        f'<td class="waits">{e(", ".join(blockers.get(c["id"], [])) or "nothing")}</td>'
        f'<td class="now">{e(STATE.get(c.get("state", "waiting")) or "Waiting")}</td></tr>'
        for c in sorted(cards, key=lambda c: c.get("step", 0)))
    you_cls = ' class="you"'
    steps = "".join(f'<li{you_cls if you else ""}><i class="dot">{n}</i><div><b>{e(t)}</b><span>{e(s)}</span></div></li>'
                    for n, (t, s, you) in enumerate(road(recipe), 1))
    css_lanes = "".join(
        f".l{i}{{fill:{p[1]}}} .b{i}{{stroke:{p[0]}}} .s{i}{{fill:{p[0]}}} .t{i}{{fill:{p[0]}}} .sw.s{i}{{background:{p[0]}}} "
        f".c{i}{{background:{p[1]};color:{p[0]}}} @media (prefers-color-scheme: dark){{.l{i}{{fill:{p[3]}}} .b{i}{{stroke:{p[2]}}} "
        f".s{i}{{fill:{p[2]}}} .t{i}{{fill:{p[2]}}} .sw.s{i}{{background:{p[2]}}} .c{i}{{background:{p[3]};color:{p[2]}}}}}\n"
        for i, p in enumerate(color[a] for a in areas))
    effort = data.get("effort")
    facts = [f"<b>{len(cards)}</b> cards", f"<b>{waves}</b> waves", f"<b>{len(done)}</b> waves delivered",
             f"<b>{len(data.get('links', []))}</b> blocker links",
             f"<b>{sum(1 for c in cards if c.get('db'))}</b> database changes"] + ([f"Effort <b>{e(str(effort))}</b>"] if effort else [])
    return TEMPLATE.format(
        title=e(f"Sprint {data.get('sprint', '')} map"), eyebrow=e(f"{data.get('project', '')} · Sprint {data.get('sprint', '')}"
                                                                   + (f" · due {data['due']}" if data.get("due") else "")),
        headline=e(data.get("headline") or f"Sprint {data.get('sprint', '')}"), lede=e(data.get("lede") or ""),
        facts="".join(f"<span>{f}</span>" for f in facts), legend=legend, width=width, height=height, svg="".join(svg),
        order=order, road=steps, css_lanes=css_lanes, done=",".join(map(str, done)))


def geometry(data):
    cards, areas, waves, tops, rows, box, height = layout(data)
    links = [("block", a, b) for a, b in data.get("links", [])] + [("after", a, b) for a, b in data.get("after", [])]
    return {"boxes": box, "paths": [{"kind": k, "from": a, "to": b, "points": p}
                                     for k, a, b, p in route(box, tops, areas, links, waves)]}


TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="sprint-map-waves-done" content="{done}"><title>{title}</title><style>
:root{{--bg:#f4f6f8;--panel:#fff;--ink:#17202a;--muted:#5b6774;--line:#d7dde4;--grid:#e8ecf0;--edge:#7b8794;--hot:#17202a;--done:#2f7d32}}
@media (prefers-color-scheme: dark){{:root{{--bg:#0f1419;--panel:#161d24;--ink:#e8edf2;--muted:#95a2b0;--line:#2a3540;--grid:#1d262f;--edge:#6f7d8b;--hot:#f2f5f8;--done:#7bd389}}}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;padding:28px max(16px,env(safe-area-inset-left)) 48px}}
.wrap{{max-width:1480px;margin:0 auto;display:flex;flex-direction:column;gap:28px}} .eyebrow{{font:600 12px ui-monospace,monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}}
h1{{margin:0;font-size:clamp(26px,4vw,36px);line-height:1.15}} h2{{margin:0;font-size:18px}} .lede{{margin:0;color:var(--muted);max-width:70ch}}
.facts{{display:flex;flex-wrap:wrap;gap:8px 20px;color:var(--muted);font-size:14px}} .facts b{{color:var(--ink)}}
.panel{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:12px;min-width:0}}
.legend{{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:13px;color:var(--muted)}} .legend span{{display:inline-flex;align-items:center;gap:6px}}
.sw{{width:12px;height:12px;border-radius:3px;display:inline-block}} .scroll{{overflow-x:auto}} svg{{display:block;min-width:{width}px;width:100%;height:auto}}
.lane{{opacity:.55}} .lane-label{{font-size:13px;font-weight:600;fill:var(--ink)}} .wave-label{{font:600 12px ui-monospace,monospace;fill:var(--muted);letter-spacing:.06em}} .wave-label.done{{fill:var(--done)}}
.gridline{{stroke:var(--grid)}} .edge{{fill:none;stroke:var(--edge);stroke-width:1.6}} .edge.order{{stroke-dasharray:5 5}}
.box{{fill:var(--panel);stroke-width:1.5}} .id{{font:600 12px ui-monospace,monospace}} .ttl{{font-size:12.5px;font-weight:600;fill:var(--ink)}} .ttl.sub{{font-weight:500}}
.meta{{font-size:11px;fill:var(--muted)}} .db{{fill:#c2410c;font-weight:600}} .mark{{font-size:11px;font-weight:600;fill:var(--done)}} .step{{font:600 11px ui-monospace,monospace;fill:var(--panel)}}
.node{{outline:none}} .node:focus-visible .box{{stroke-width:3}} svg.focus .edge{{opacity:.15}} svg.focus .edge.hot{{opacity:1;stroke:var(--hot);stroke-width:2.4}} svg.focus .node{{opacity:.35}} svg.focus .node.hot{{opacity:1}}
.cols{{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:20px}} @media (max-width:860px){{.cols{{grid-template-columns:minmax(0,1fr)}}}}
table{{border-collapse:collapse;width:100%;font-size:14px}} th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}} th{{font-size:12px;color:var(--muted);text-transform:uppercase}}
td.n{{font-family:ui-monospace,monospace;white-space:nowrap}} td.waits,td.now{{color:var(--muted)}} .chip{{font-size:12px;padding:1px 8px;border-radius:999px;font-weight:600;white-space:nowrap}}
.road{{list-style:none;margin:0;padding:0}} .road li{{display:grid;grid-template-columns:28px 1fr;gap:12px;padding-bottom:16px}} .road .dot{{width:28px;height:28px;border-radius:50%;border:2px solid var(--line);display:grid;place-items:center;font:600 12px ui-monospace,monospace;color:var(--muted)}}
.road li.you .dot{{border-color:var(--ink);color:var(--ink)}} .road b{{display:block}} .road span{{color:var(--muted);font-size:14px}}
{css_lanes}</style></head><body><div class="wrap">
<header><div class="eyebrow">{eyebrow}</div><h1>{headline}</h1><p class="lede">{lede}</p><div class="facts">{facts}</div></header>
<section class="panel"><h2>Sprint map</h2><div class="legend">{legend}<span>── blocks</span><span>- - lands after (shared screen, no link)</span></div>
<p class="lede">Point at or tab to a card to light up what it waits for and what waits for it.</p>
<div class="scroll"><svg id="map" viewBox="0 0 {width} {height}" role="img" aria-label="{title}">
<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--edge)"/></marker></defs>
{svg}</svg></div></section>
<div class="cols"><section class="panel"><h2>Run order</h2><div class="scroll"><table><thead><tr><th>#</th><th>Card</th><th>What you get</th><th>Area</th><th>Waits for</th><th>Now</th></tr></thead><tbody>{order}</tbody></table></div></section>
<section class="panel"><h2>After the last wave</h2><ol class="road">{road}</ol></section></div></div>
<script>(function(){{var svg=document.getElementById("map");function on(id){{svg.classList.add("focus");var keep={{}};keep[id]=1;
svg.querySelectorAll(".edge").forEach(function(p){{var h=p.dataset.from===id||p.dataset.to===id;p.classList.toggle("hot",h);if(h){{keep[p.dataset.from]=1;keep[p.dataset.to]=1}}}});
svg.querySelectorAll(".node").forEach(function(n){{n.classList.toggle("hot",!!keep[n.dataset.id])}})}}
function off(){{svg.classList.remove("focus");svg.querySelectorAll(".hot").forEach(function(n){{n.classList.remove("hot")}})}}
svg.querySelectorAll(".node").forEach(function(n){{var id=n.dataset.id;n.addEventListener("mouseenter",function(){{on(id)}});n.addEventListener("mouseleave",off);n.addEventListener("focus",function(){{on(id)}});n.addEventListener("blur",off)}})}})();</script>
</body></html>
"""


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--recipe")
    ap.add_argument("--out")
    ap.add_argument("--geometry", action="store_true")
    a = ap.parse_args(argv)
    try:
        data = json.loads(Path(a.data).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"sprint_map: cannot read {a.data}: {exc}", file=sys.stderr)
        return 2
    if a.geometry:
        print(json.dumps(geometry(data)))
        return 0
    text = page(data, a.recipe)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
