import sys, re, html
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding="utf-8")
path, page, what = sys.argv[1], sys.argv[2], sys.argv[3]
d = [d for d in ET.parse(path).getroot().findall("diagram") if d.get("name") == page][0]
cells = d.find("mxGraphModel/root").findall("mxCell")
byid = {c.get("id"): c for c in cells}
def clean(v, keep_br=False):
    v = v or ""
    if keep_br:
        v = re.sub(r"<br\s*/?>|</div>|<div>", "\n", v)
    v = html.unescape(re.sub(r"<[^>]+>", "", v)).replace("\xa0", " ")
    return "\n".join(re.sub(r"[ \t]+", " ", l).strip() for l in v.split("\n") if l.strip()) if keep_br else re.sub(r"\s+", " ", v).strip()
is_table = lambda c: c is not None and c.get("parent") == "1" and "swimlane" in (c.get("style") or "")
def owner(cid):
    c = byid.get(cid)
    while c is not None and c.get("parent") not in ("1", "0", None):
        c = byid.get(c.get("parent"))
    return c
def label(cid):
    c = byid[cid]; p = byid.get(c.get("parent"))
    return (clean(p.get("value")) + "." if is_table(p) else "") + clean(c.get("value")).split(" (")[0]
if what == "tables":
    for t in sorted([c for c in cells if is_table(c)], key=lambda c: clean(c.get("value")).lower()):
        deferred = "CCCC00" in (t.get("style") or "")
        rows = [clean(r.get("value")) for r in cells if r.get("parent") == t.get("id")]
        print(f"#### {clean(t.get('value'))}" + ("  — *(phát triển sau)*" if deferred else ""))
        for r in rows:
            print(f"- {r}")
        fks = [f"{label(e.get('source'))} → {label(e.get('target'))}" for e in cells
               if e.get("edge") == "1" and owner(e.get("source")) is t and is_table(owner(e.get("target")))]
        if fks:
            print("- FK: " + "; ".join(fks))
        print()
elif what == "notes":
    for c in cells:
        st = c.get("style") or ""
        if c.get("parent") == "1" and "shape=note" in st and c.get("id") != "note_legend":
            kind = "LOOKUP" if "e1d5e7" in st.lower() else "NOTE"
            print(f"[{kind}] id={c.get('id')}\n{clean(c.get('value'), True)}\n")
