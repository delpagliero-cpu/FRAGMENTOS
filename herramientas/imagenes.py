import json, hashlib, re, sys
from pathlib import Path
from PIL import Image, ImageOps

RAIZ = Path(r"C:\Users\delpa\Downloads\TIENDA NUEVOS TRAPOS REPO")
ORIG = RAIZ / "Imagenes de prendas"
DEST = RAIZ / "img" / "prendas"
ANCHOS = [600, 1000, 1600]
CALIDAD = 78

DEST.mkdir(parents=True, exist_ok=True)
manifiesto, cache, ratios = {}, {}, {}

for carpeta in sorted(ORIG.iterdir()):
    if not carpeta.is_dir():
        continue
    m = re.match(r"(FRAG-[A-Z]{2}-\d{2})", carpeta.name)
    if not m:
        print("!! sin codigo:", carpeta.name); continue
    codigo = m.group(1)
    fotos = sorted(p for p in carpeta.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    salidas = []
    for foto in fotos:
        digest = hashlib.sha1(foto.read_bytes()).hexdigest()[:10]
        if digest in cache:
            salidas.append(cache[digest]); continue
        im = ImageOps.exif_transpose(Image.open(foto)).convert("RGB")
        w, h = im.size
        base = f"{digest}"
        for ancho in ANCHOS:
            if ancho > w:
                continue
            alto = round(h * ancho / w)
            im.resize((ancho, alto), Image.LANCZOS).save(
                DEST / f"{base}-{ancho}.webp", "WEBP", quality=CALIDAD, method=6)
        cache[digest] = base
        ratios[base] = round(w / h, 4)
        salidas.append(base)
        print(f"  {codigo}  {foto.name} -> {base}  ({w}x{h})")
    manifiesto[codigo] = {"carpeta": carpeta.name, "imagenes": salidas}

(RAIZ / "img" / "manifiesto.json").write_text(
    json.dumps({"anchos": ANCHOS, "ratios": ratios, "prendas": manifiesto},
               ensure_ascii=False, indent=2), encoding="utf-8")
print("\nprendas con carpeta:", len(manifiesto))
print("imagenes unicas:", len(cache))
