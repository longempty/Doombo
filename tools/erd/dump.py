import sys, re, html
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")
path = sys.argv[1]
tree = ET.parse(path)
root = tree.getroot()

def clean(v):
    v = v or ""
    v = re.sub(r"<br\s*/?>", " | ", v)
    v = re.sub(r"<[^>]+>", "", v)
    return html.unescape(v).strip()

for d in root.findall("diagram"):
    print("=" * 30, "PAGE:", d.get("name"))
    model = d.find("mxGraphModel")
    cells = model.find("root").findall("mxCell")
    byid = {c.get("id"): c for c in cells}
    children = {}
    for c in cells:
        children.setdefault(c.get("parent"), []).append(c)
    for c in cells:
        if c.get("vertex") == "1" and c.get("parent") == "1":
            g = c.find("mxGeometry")
            geo = f"x={g.get('x')} y={g.get('y')} w={g.get('width')} h={g.get('height')}" if g is not None else ""
            style = c.get("style") or ""
            fill = re.search(r"fillColor=([^;]+)", style)
            kind = "swimlane" if "swimlane" in style else ("shape=" + (re.search(r"shape=([^;]+)", style).group(1) if "shape=" in style else style.split(";")[0]))
            print(f"\n[{c.get('id')}] {clean(c.get('value'))!r} ({kind}, fill={fill.group(1) if fill else None}) {geo}")
            for ch in children.get(c.get("id"), []):
                gg = ch.find("mxGeometry")
                print(f"    - [{ch.get('id')}] {clean(ch.get('value'))}  (y={gg.get('y') if gg is not None else ''} h={gg.get('height') if gg is not None else ''})")
    print("\n--- EDGES ---")
    def label(i):
        c = byid.get(i)
        if c is None: return str(i)
        p = byid.get(c.get("parent"))
        if p is not None and p.get("parent") == "1" and "swimlane" in (p.get("style") or ""):
            return f"{clean(p.get('value'))}.{clean(c.get('value'))}"
        return clean(c.get("value")) or i
    for c in cells:
        if c.get("edge") == "1":
            style = c.get("style") or ""
            s = re.search(r"startArrow=([^;]+)", style); e = re.search(r"endArrow=([^;]+)", style)
            print(f"[{c.get('id')}] {label(c.get('source'))} -> {label(c.get('target'))}  start={s.group(1) if s else None} end={e.group(1) if e else None} val={clean(c.get('value'))!r}")
