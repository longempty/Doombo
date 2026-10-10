"""Helpers for editing ERD tables in Doombo.drawio with the conventions used in this project.

Usage (edit the working page, then recolor):
    from erd_lib import ErdPage
    p = ErdPage("Doombo.drawio", "New Version")
    p.add_row("cziWY0EkAAtVQsHl7tzw-5", "acc_new_col", "New_Col (int)")
    p.relayout("cziWY0EkAAtVQsHl7tzw-5")
    p.save()
    # then: python tools/erd/recolor.py Doombo.drawio "Physical ERD" "New Version" ""

Tables are draw.io swimlanes (parent="1"); each attribute is a child text cell stacked at
startSize + 30*i. FK edges connect attribute cells (source/target = row ids). Keep existing ids
when editing so recolor.py / changelog.py can diff against the official page.
"""
import xml.etree.ElementTree as ET

TABLE_STYLE = ("swimlane;fontStyle=0;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;"
               "resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;align=center;fontSize=14;")
ROW_STYLE = ("text;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;spacingLeft=4;spacingRight=4;"
             "overflow=hidden;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;rotatable=0;whiteSpace=wrap;html=1;")
EDGE_STYLE = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
RULE_NOTE = ("shape=note;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;align=left;"
             "spacingLeft=8;spacingRight=8;verticalAlign=top;")
LOOKUP_NOTE = ("shape=note;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;align=left;"
               "spacingLeft=6;verticalAlign=top;")
DEFERRED_FILL = "light-dark(#FFF2CC,#CCCC00)"          # "phát triển sau" tables
LINK = '&nbsp;&nbsp;<span style="color:#0050EF;"><b>(link Lookup_Code)</b></span>'  # append to lookup columns


def style_get(style, key):
    for p in (style or "").split(";"):
        if p.startswith(key + "="):
            return p.split("=", 1)[1]
    return None


def set_style(style, **kv):
    """Set / replace style keys; a value of None removes the key."""
    parts = [p for p in (style or "").split(";") if p]
    keys = [p.split("=", 1)[0] for p in parts]
    for k, v in kv.items():
        if v is None:
            if k in keys:
                i = keys.index(k)
                parts.pop(i)
                keys.pop(i)
        elif k in keys:
            parts[keys.index(k)] = f"{k}={v}"
        else:
            parts.append(f"{k}={v}")
            keys.append(k)
    return ";".join(parts) + ";"


def lookup_note(title, obj, values, extra=""):
    """Purple lookup declaration text: values are numbered 1..n (= Lookup_Int)."""
    return f"<b>{title}</b><br>Lookup_Object = {obj}{extra}<br>" + "<br>".join(
        f"{i} – {v}" for i, v in enumerate(values, 1))


class ErdPage:
    def __init__(self, path, page_name):
        self.path = path
        self.tree = ET.parse(path)
        self.page = next(d for d in self.tree.getroot().findall("diagram") if d.get("name") == page_name)
        self.root = self.page.find("mxGraphModel/root")
        self.byid = {c.get("id"): c for c in self.root.findall("mxCell")}

    # ---- basic access
    def children(self, pid):
        return [c for c in self.root.findall("mxCell") if c.get("parent") == pid]

    def val(self, cid, value=None):
        if value is None:
            return self.byid[cid].get("value")
        self.byid[cid].set("value", value)

    def replace_in(self, cid, old, new):
        v = self.byid[cid].get("value")
        assert old in v, f"{cid}: text not found: {old[:50]}"
        self.byid[cid].set("value", v.replace(old, new))

    def restyle(self, cid, **kv):
        self.byid[cid].set("style", set_style(self.byid[cid].get("style"), **kv))

    def geo(self, cid, **kw):
        g = self.byid[cid].find("mxGeometry")
        for k, v in kw.items():
            g.set(k, str(v))

    # ---- structure
    def remove(self, cid):
        for ch in self.children(cid):
            self.remove(ch.get("id"))
        self.root.remove(self.byid.pop(cid))

    def _cell(self, cid, attrs, geom):
        c = ET.Element("mxCell", {"id": cid, **attrs})
        ET.SubElement(c, "mxGeometry", {**geom, "as": "geometry"})
        self.byid[cid] = c
        return c

    def add_row(self, table, cid, value, after=None):
        """Insert an attribute row (after `after` row id, default: last row). Call relayout() afterwards."""
        c = self._cell(cid, {"parent": table, "style": ROW_STYLE, "value": value, "vertex": "1"},
                       {"width": "100", "height": "30"})
        if after is None:
            kids = self.children(table)
            after = kids[-1].get("id") if kids else table
        self.root.insert(list(self.root).index(self.byid[after]) + 1, c)
        return c

    def order_rows(self, table, ids):
        assert {r.get("id") for r in self.children(table)} <= set(ids), "order_rows would drop rows"
        rows = [self.byid[i] for i in ids]
        for r in rows:
            self.root.remove(r)
        pos = list(self.root).index(self.byid[table])
        for k, r in enumerate(rows, 1):
            self.root.insert(pos + k, r)

    def relayout(self, table, width=None):
        """Restack rows (y = startSize + 30*i) and fit table height; optionally set width."""
        t = self.byid[table]
        st = t.get("style")
        start = int(st.split("startSize=")[1].split(";")[0]) if "startSize=" in st else 26
        g = t.find("mxGeometry")
        if width is not None:
            g.set("width", str(width))
        y = start
        for row in self.children(table):
            rg = row.find("mxGeometry")
            rg.set("y", str(y))
            rg.set("width", g.get("width"))
            y += int(float(rg.get("height", "30")))
        g.set("height", str(y))

    def add_table(self, tid, name, x, y, width, rows, deferred=False):
        """rows = [(row_id, label), ...]; deferred=True paints it as 'phát triển sau'."""
        st = TABLE_STYLE + (f"fillColor={DEFERRED_FILL};" if deferred else "")
        self.root.append(self._cell(tid, {"parent": "1", "style": st, "value": name, "vertex": "1"},
                                    {"x": str(x), "y": str(y), "width": str(width), "height": "26"}))
        for rid, label in rows:
            self.root.append(self._cell(rid, {"parent": tid, "style": ROW_STYLE, "value": label, "vertex": "1"},
                                        {"width": str(width), "height": "30"}))
        self.relayout(tid)

    def add_edge(self, cid, source_row, target_row):
        assert source_row in self.byid and target_row in self.byid, (cid, source_row, target_row)
        self.root.append(self._cell(cid, {"edge": "1", "parent": "1", "source": source_row,
                                          "style": EDGE_STYLE, "target": target_row}, {"relative": "1"}))

    def add_note(self, cid, html_value, x, y, width, height, style=RULE_NOTE):
        self.root.append(self._cell(cid, {"parent": "1", "style": style, "value": html_value, "vertex": "1"},
                                    {"x": str(x), "y": str(y), "width": str(width), "height": str(height)}))

    def drop_dangling_edges(self):
        for c in list(self.root.findall("mxCell")):
            if c.get("edge") == "1" and any(c.get(k) and c.get(k) not in self.byid for k in ("source", "target")):
                self.remove(c.get("id"))

    def save(self):
        self.drop_dangling_edges()
        self.tree.write(self.path, encoding="utf-8", xml_declaration=False)
