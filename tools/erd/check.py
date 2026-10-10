import sys, re, html
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding="utf-8")

t = ET.parse(sys.argv[1]).getroot()
d = [d for d in t.findall("diagram") if d.get("name") == sys.argv[2]][0]
cells = d.find("mxGraphModel/root").findall("mxCell")
byid = {c.get("id"): c for c in cells}
clean = lambda v: html.unescape(re.sub(r"<[^>]+>", " ", v or "")).split("  ")[0][:60].strip()

boxes = []
for c in cells:
    if c.get("vertex") == "1" and c.get("parent") == "1":
        g = c.find("mxGeometry"); x = float(g.get("x", 0)); y = float(g.get("y", 0))
        boxes.append((clean(c.get("value"))[:30], x, y, x + float(g.get("width")), y + float(g.get("height"))))
n = 0
for i, a in enumerate(boxes):
    for b in boxes[i + 1:]:
        if a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]:
            n += 1; print("OVERLAP:", a[0], "|", b[0])
print("shapes:", len(boxes), "overlaps:", n)

print("\n-- highlighted --")
for c in cells:
    s = c.get("style") or ""
    m = re.search(r"fillColor=(#d5e8d4|#ffe6cc)", s)
    tag = {"#d5e8d4": "NEW", "#ffe6cc": "MOD"}.get(m.group(1)) if m else ("RED" if "strokeColor=#FF0000" in s else None)
    if tag:
        p = byid.get(c.get("parent"))
        owner = clean(p.get("value")) + "." if p is not None and p.get("parent") == "1" else ""
        print(f"{tag:4} {owner}{clean(c.get('value'))}")
