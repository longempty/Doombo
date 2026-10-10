"""Recolor change markers on TARGET page against BASE page (rows, tables, notes, edges) and rebuild the legend."""
import sys, re, html
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding="utf-8")

path, BASE, TARGET = sys.argv[1], sys.argv[2], sys.argv[3]
OPEN_ROWS = set(filter(None, sys.argv[4].split(","))) if len(sys.argv) > 4 else set()  # rows flagged "chưa chốt"

tree = ET.parse(path)
pages = {d.get("name"): d for d in tree.getroot().findall("diagram")}
base_cells = pages[BASE].find("mxGraphModel/root").findall("mxCell")
base = {c.get("id"): c for c in base_cells}
root = pages[TARGET].find("mxGraphModel/root")
byid = {c.get("id"): c for c in root.findall("mxCell")}

NEW_FILL, MOD_FILL, OPEN_FILL, CHANGE_STROKE = "#d5e8d4", "#ffe6cc", "#f8cecc", "#FF0000"
TAG = '<span style="color:#0050EF;"><b>(link Lookup_Code)</b></span>'


def style_get(style, key):
    for p in (style or "").split(";"):
        if p.startswith(key + "="):
            return p.split("=", 1)[1]
    return None


def set_style(style, **kv):
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


def is_table(c):
    return c is not None and c.get("parent") == "1" and "swimlane" in (c.get("style") or "")


def values_under(cells, pid):
    return {c.get("value") for c in cells if c.get("parent") == pid}


# ---- clear previous markers
for c in root.findall("mxCell"):
    st = c.get("style") or ""
    if is_table(byid.get(c.get("parent"))) and style_get(st, "fillColor") in (NEW_FILL, MOD_FILL, OPEN_FILL):
        c.set("style", set_style(st, fillColor="none"))
    elif is_table(c) and style_get(st, "fillColor") == MOD_FILL:
        c.set("style", set_style(st, fillColor=None))
    elif "shape=note" in st and style_get(st, "strokeColor") == CHANGE_STROKE:
        normal = {"#fff2cc": "#d6b656", "#e1d5e7": "#9673a6"}.get(style_get(st, "fillColor"))
        c.set("style", set_style(st, strokeColor=normal, strokeWidth=None))
    elif c.get("edge") == "1" and style_get(st, "strokeColor") == CHANGE_STROKE:
        c.set("style", set_style(st, strokeColor=None, strokeWidth=None))

# ---- color the diff (rows matched by id, else by identical label in the same table)
base_pairs = {(c.get("source"), c.get("target")) for c in base_cells if c.get("edge") == "1"}
base_pairs |= {(t, s) for s, t in base_pairs}
target_cells = root.findall("mxCell")
for c in target_cells:
    cid, st = c.get("id"), c.get("style") or ""
    b = base.get(cid)
    if is_table(byid.get(c.get("parent"))):
        if cid in OPEN_ROWS:
            fill = OPEN_FILL
        elif b is not None:
            fill = MOD_FILL if b.get("value") != c.get("value") else "none"
        else:
            fill = "none" if c.get("value") in values_under(base_cells, c.get("parent")) else NEW_FILL
        c.set("style", set_style(st, fillColor=fill))
    elif is_table(c) and b is not None and b.get("value") != c.get("value"):
        c.set("style", set_style(st, fillColor=MOD_FILL))
    elif c.get("parent") == "1" and "shape=note" in st and cid != "note_legend":
        if b is None or b.get("value") != c.get("value"):
            c.set("style", set_style(st, strokeColor=CHANGE_STROKE, strokeWidth=3))
    elif c.get("edge") == "1" and (c.get("source"), c.get("target")) not in base_pairs:
        c.set("style", set_style(st, strokeColor=CHANGE_STROKE, strokeWidth=2))

# ---- legend
clean = lambda v: html.unescape(re.sub(r"<[^>]+>", "", v or "")).split("  ")[0].strip()
def blabel(i):
    c = base.get(i)
    p = base.get(c.get("parent")) if c is not None else None
    return (clean(p.get("value")) + "." if p is not None and p.get("parent") == "1" else "") + clean(c.get("value") if c is not None else i)

removed_tables = [clean(c.get("value")) for c in base_cells if is_table(c) and c.get("id") not in byid]
removed_rows = [f"{clean(base[c.get('parent')].get('value'))}.{clean(c.get('value'))}" for c in base_cells
                if c.get("parent") in byid and is_table(base.get(c.get("parent"))) and c.get("id") not in byid
                and c.get("value") not in values_under(target_cells, c.get("parent"))]
new_pairs = {(c.get("source"), c.get("target")) for c in target_cells if c.get("edge") == "1"}
new_pairs |= {(t, s) for s, t in new_pairs}
removed_links = [f"{blabel(c.get('source'))} → {blabel(c.get('target'))}" for c in base_cells
                 if c.get("edge") == "1" and (c.get("source"), c.get("target")) not in new_pairs]
renamed_tables = [f"{clean(base[c.get('id')].get('value'))} → {clean(c.get('value'))}" for c in target_cells
                  if is_table(c) and c.get("id") in base and base[c.get("id")].get("value") != c.get("value")]

sw = lambda color: f'<span style="background-color:{color};">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>'
byid["note_legend"].set("value",
    f"<b>Chú thích thay đổi so với trang {BASE}{' (chính thức)' if BASE == 'Physical ERD' else ''}</b><br>"
    f"{sw(NEW_FILL)} thuộc tính mới (cả bảng mới)<br>"
    f"{sw(MOD_FILL)} thuộc tính sửa / tiêu đề bảng đổi tên<br>"
    + (f"{sw(OPEN_FILL)} <b>chưa chốt, cần trao đổi</b><br>" if OPEN_ROWS else "") +
    '<span style="color:#FF0000;"><b>▭ viền đỏ</b></span>: note mới / sửa<br>'
    '<span style="color:#FF0000;"><b>— đường đỏ</b></span>: quan hệ (FK) mới<br>'
    f"{sw('#FFF2CC')} bảng nền vàng: phát triển sau<br>"
    f"{TAG}: cột lưu Lookup_Int, tra bảng Lookup_Code.<br>"
    "<b>Bảng đổi tên:</b> " + ", ".join(renamed_tables) + "<br>"
    "<b>Bảng đã bỏ (header cũ, đã gộp):</b> " + ", ".join(removed_tables) + "<br>"
    "<b>Thuộc tính đã bỏ:</b><br>" + "<br>".join("– " + r for r in removed_rows) + "<br>"
    "<b>Liên kết đã bỏ:</b><br>" + "<br>".join("– " + r for r in removed_links))

tree.write(path, encoding="utf-8", xml_declaration=False)
print("renamed tables:", renamed_tables)
print("removed tables:", removed_tables)
print("removed rows:", removed_rows)
print("removed links:", removed_links)
print("ok")

