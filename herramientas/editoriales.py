# -*- coding: utf-8 -*-
"""Derivados web de las fotos editoriales.

Los originales pesan ~26 MB cada uno y quedan fuera del repo. Acá se eligen a
mano las que se usan y se generan en tres anchos. Para sumar una editorial:
agregarla a SELECCION y volver a correr el script.
"""
import json
import os
from PIL import Image, ImageOps

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RAIZ, "Imagenes editoriales", "fotod tesis Delfi")
DST = os.path.join(RAIZ, "img", "editoriales")
ANCHOS = [900, 1600, 2400]
CALIDAD = 76

# nombre corto -> archivo original
SELECCION = {
    "hero": "DSC09527.jpg",
    "ed-01": "DSC09443.jpg",
    "ed-02": "DSC09248.jpg",
    "ed-03": "DSC09190.jpg",
    "ed-04": "DSC09163.jpg",
    "ed-05": "DSC09102.jpg",
    "ed-06": "DSC09384.jpg",
    "ed-07": "DSC09071.jpg",
    "ed-08": "DSC09033.jpg",
    "ed-09": "DSC09335.jpg",
}

os.makedirs(DST, exist_ok=True)
meta = {}

for nombre, archivo in SELECCION.items():
    ruta = os.path.join(SRC, archivo)
    if not os.path.exists(ruta):
        print("!! falta:", archivo)
        continue
    im = ImageOps.exif_transpose(Image.open(ruta)).convert("RGB")
    w, h = im.size
    for ancho in ANCHOS:
        if ancho > w:
            continue
        alto = round(h * ancho / w)
        im.resize((ancho, alto), Image.LANCZOS).save(
            os.path.join(DST, "%s-%d.webp" % (nombre, ancho)),
            "WEBP", quality=CALIDAD, method=6)
    meta[nombre] = {"origen": archivo, "ratio": round(w / h, 4),
                    "orientacion": "apaisada" if w > h else "vertical"}
    print("  %-8s %-16s %dx%d  %s" % (nombre, archivo, w, h, meta[nombre]["orientacion"]))

with open(os.path.join(RAIZ, "img", "editoriales.json"), "w", encoding="utf-8") as f:
    json.dump({"anchos": ANCHOS, "imagenes": meta}, f, ensure_ascii=False, indent=2)
print("\nlistas:", len(meta))
