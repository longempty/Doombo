"""Promote the working page to the official page once the user approves a round.

    python tools/erd/compile_official.py Doombo.drawio
    python tools/erd/recolor.py Doombo.drawio "Physical ERD" "New Version" ""

- Copies "New Version" over "Physical ERD" (same page id / position), strips every change marker
  (row fills, renamed-table header fill, red note borders, red edges) and removes note_legend.
- Keeps the conventions: purple lookup notes, yellow "phát triển sau" tables, blue (link Lookup_Code) tags.
- "New Version" stays as the working page; re-run recolor.py right after so its markers reset.
"""
import sys, copy, re
import xml.etree.ElementTree as ET
from erd_lib import set_style, style_get

NEW_FILL, MOD_FILL, OPEN_FILL, RED = "#d5e8d4", "#ffe6cc", "#f8cecc", "#FF0000"

path = sys.argv[1]
tree = ET.parse(path)
mxfile = tree.getroot()
pages = {d.get("name"): d for d in mxfile.findall("diagram")}
old_official, working = pages["Physical ERD"], pages["New Version"]

official = copy.deepcopy(working)
official.set("name", "Physical ERD")
official.set("id", old_official.get("id"))
root = official.find("mxGraphModel/root")
byid = {c.get("id"): c for c in root.findall("mxCell")}
is_table = lambda c: c is not None and c.get("parent") == "1" and "swimlane" in (c.get("style") or "")

for c in list(root.findall("mxCell")):
    st = c.get("style") or ""
    if c.get("id") == "note_legend":
        root.remove(c)
    elif is_table(byid.get(c.get("parent"))) and style_get(st, "fillColor") in (NEW_FILL, MOD_FILL, OPEN_FILL):
        c.set("style", set_style(st, fillColor="none"))
    elif is_table(c) and style_get(st, "fillColor") == MOD_FILL:
        c.set("style", set_style(st, fillColor=None))
    elif "shape=note" in st and style_get(st, "strokeColor") == RED:
        normal = {"#fff2cc": "#d6b656", "#e1d5e7": "#9673a6"}.get(style_get(st, "fillColor"))
        c.set("style", set_style(st, strokeColor=normal, strokeWidth=None))
    elif c.get("edge") == "1" and style_get(st, "strokeColor") == RED:
        c.set("style", set_style(st, strokeColor=None, strokeWidth=None))

idx = list(mxfile).index(old_official)
mxfile.remove(old_official)
mxfile.insert(idx, official)
tree.write(path, encoding="utf-8", xml_declaration=False)

left = sum(1 for c in root.findall("mxCell")
           if re.search(r"fillColor=(#d5e8d4|#ffe6cc|#f8cecc)|strokeColor=#FF0000", c.get("style") or ""))
print("pages:", [d.get("name") for d in mxfile.findall("diagram")], "| markers left on official:", left)
print("next: python tools/erd/recolor.py", path, '"Physical ERD" "New Version" ""')
