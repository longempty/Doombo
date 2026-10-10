"""Per-entity changelog of TARGET page vs BASE page."""
import sys, re, html
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding="utf-8")

path, BASE, TARGET = sys.argv[1], sys.argv[2], sys.argv[3]
pages = {d.get("name"): d for d in ET.parse(path).getroot().findall("diagram")}
bcells = pages[BASE].find("mxGraphModel/root").findall("mxCell")
tcells = pages[TARGET].find("mxGraphModel/root").findall("mxCell")
b = {c.get("id"): c for c in bcells}
t = {c.get("id"): c for c in tcells}
clean = lambda v: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", v or ""))).strip()
is_table = lambda c: c is not None and c.get("parent") == "1" and "swimlane" in (c.get("style") or "")
is_note = lambda c: c.get("parent") == "1" and "shape=note" in (c.get("style") or "")


def rows(cells, tid):
    return [c for c in cells if c.get("parent") == tid]


def owner(cells_by_id, cid):
    c = cells_by_id.get(cid)
    while c is not None and c.get("parent") not in ("1", "0", None):
        c = cells_by_id.get(c.get("parent"))
    return c


def label(cells_by_id, cid):
    c = cells_by_id.get(cid)
    p = cells_by_id.get(c.get("parent")) if c is not None else None
    return (clean(p.get("value")) + "." if is_table(p) else "") + clean(c.get("value") if c is not None else cid)


def pairs(cells):
    return {frozenset((c.get("source"), c.get("target"))) for c in cells if c.get("edge") == "1"}


bp, tp = pairs(bcells), pairs(tcells)
for tab in [c for c in tcells if is_table(c)] + [c for c in bcells if is_table(c) and c.get("id") not in t]:
    tid = tab.get("id")
    old, new = b.get(tid), t.get(tid)
    lines = []
    if new is None:
        status = "BẢNG ĐÃ BỎ"
    elif old is None:
        status = "BẢNG MỚI"
    elif clean(old.get("value")) != clean(new.get("value")):
        status = f"ĐỔI TÊN từ {clean(old.get('value'))}"
    else:
        status = ""
    if new is not None and old is not None:
        old_rows, new_rows = rows(bcells, tid), rows(tcells, tid)
        old_vals = {r.get("value") for r in old_rows}
        new_vals = {r.get("value") for r in new_rows}
        for r in new_rows:
            o = b.get(r.get("id"))
            if o is not None and o.get("value") != r.get("value"):
                lines.append(f"  ~ {clean(o.get('value'))}  →  {clean(r.get('value'))}")
            elif o is None and r.get("value") not in old_vals:
                lines.append(f"  + {clean(r.get('value'))}")
        for r in old_rows:
            if r.get("id") not in t and r.get("value") not in new_vals:
                lines.append(f"  - {clean(r.get('value'))}")
    elif new is not None:
        lines += [f"  + {clean(r.get('value'))}" for r in rows(tcells, tid)]
    for c in tcells:
        if c.get("edge") == "1" and owner(t, c.get("source")) is new and new is not None \
                and frozenset((c.get("source"), c.get("target"))) not in bp:
            lines.append(f"  FK+ {label(t, c.get('source'))} → {label(t, c.get('target'))}")
    for c in bcells:
        if c.get("edge") == "1" and owner(b, c.get("source")) is old and old is not None \
                and frozenset((c.get("source"), c.get("target"))) not in tp:
            lines.append(f"  FK- {label(b, c.get('source'))} → {label(b, c.get('target'))}")
    name = clean((new if new is not None else old).get("value"))
    fill = ""
    if new is not None and old is not None:
        f = lambda c: (re.search(r"fillColor=([^;]+)", c.get("style") or "") or [None, None])[1]
        if f(old) != f(new):
            fill = f"  [màu header: {f(old)} → {f(new)}]"
    if status or lines or fill:
        print(f"## {name}" + (f" — {status}" if status else "") + fill)
        print("\n".join(lines) if lines else "  (chỉ đổi màu / vị trí)")

print("\n## NOTES")
for c in tcells:
    if c.get("edge") != "1" and is_note(c) and c.get("id") != "note_legend":
        o = b.get(c.get("id"))
        if o is None:
            print("  + " + clean(c.get("value"))[:70])
        elif o.get("value") != c.get("value"):
            print("  ~ " + clean(c.get("value"))[:70])
for c in bcells:
    if is_note(c) and c.get("id") not in t:
        print("  - " + clean(c.get("value"))[:70])
