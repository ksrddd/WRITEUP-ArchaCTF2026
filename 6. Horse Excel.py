import zipfile
import xml.etree.ElementTree as ET
import re
from PIL import Image
import numpy as np

XLSM = "horse_8bit_14x14_ctf.xlsm"

NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

def col_to_num(col):
    n = 0
    for ch in col:
        n = n * 26 + (ord(ch) - 64)
    return n

def num_to_col(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

def split_ref(r):
    m = re.match(r"([A-Z]+)(\d+)", r)
    return col_to_num(m.group(1)), int(m.group(2))

def argb_to_rgb(argb):
    if argb is None:
        return (255, 255, 255)
    if len(argb) == 8:
        return (int(argb[2:4], 16), int(argb[4:6], 16), int(argb[6:8], 16))
    if len(argb) == 6:
        return (int(argb[0:2], 16), int(argb[2:4], 16), int(argb[4:6], 16))
    return (255, 255, 255)

with zipfile.ZipFile(XLSM) as z:
    sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    styles = ET.fromstring(z.read("xl/styles.xml"))

    # fills
    fills = []
    for fill in styles.find("s:fills", NS).findall("s:fill", NS):
        pat = fill.find("s:patternFill", NS)
        if pat is None:
            fills.append(None); continue
        fg = pat.find("s:fgColor", NS)
        bg = pat.find("s:bgColor", NS)
        fills.append({
            "fg": fg.get("rgb") if fg is not None else None,
            "bg": bg.get("rgb") if bg is not None else None,
            "fg_theme": fg.get("theme") if fg is not None else None,
        })

    # style index -> fillId
    xfs = styles.find("s:cellXfs", NS).findall("s:xf", NS)
    style_fill = [int(xf.get("fillId")) for xf in xfs]

    # fillId -> rgb
    fill_rgb = {}
    for fid, f in enumerate(fills):
        if f is None:
            fill_rgb[fid] = None
        else:
            fill_rgb[fid] = f["fg"] or f["bg"]

    style_rgb = {i: fill_rgb.get(fid) for i, fid in enumerate(style_fill)}

    # cell -> style
    cell_style = {}
    for c in sheet.findall(".//s:c", NS):
        r = c.get("r")
        s_idx = c.get("s")
        if s_idx is not None:
            cell_style[r] = int(s_idx)

    # read A1:N14 colors
    img = np.zeros((14, 14, 3), dtype=np.uint8)
    pal = []
    idx_grid = np.zeros((14, 14), dtype=int)

    for row in range(1, 15):
        for col in range(1, 15):
            ref = f"{num_to_col(col)}{row}"
            s_idx = cell_style.get(ref, 0)
            rgb = argb_to_rgb(style_rgb.get(s_idx))
            img[row-1, col-1] = rgb
            if rgb not in pal:
                pal.append(rgb)
            idx_grid[row-1, col-1] = pal.index(rgb)

    print("Palette (index -> RGB):")
    for i, p in enumerate(pal):
        print(i, p)

    print("\n14x14 color index grid (A1:N14):")
    for r in idx_grid:
        print(" ".join(str(x) for x in r))

    out = Image.fromarray(img, "RGB").resize((280, 280), Image.NEAREST)
    out.save("horse_grid_extracted.png")
    print("\nSaved: horse_grid_extracted.png")
