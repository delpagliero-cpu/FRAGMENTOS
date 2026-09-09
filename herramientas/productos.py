# -*- coding: utf-8 -*-
import json
from pathlib import Path

RAIZ = Path(r"C:\Users\delpa\Downloads\TIENDA NUEVOS TRAPOS REPO")
man = json.loads((RAIZ / "img" / "manifiesto.json").read_text(encoding="utf-8"))
IMG = {k: v["imagenes"] for k, v in man["prendas"].items()}
RATIO = man["ratios"]

TALLES = ["m", "l"]

# Disponibilidad por talle. Puede haber un M hecho y un L que haya que producir,
# así que el estado es del talle y no de la prenda.
#   "ya"      -> hay stock, sale en 1 a 5 días
#   "pedido"  -> se produce cuando lo piden, 1 a 2 semanas
#   "agotado" -> no se puede comprar
# Hoy arrancan todas en "pedido", que es lo que dice el brief. Delfi marca las
# que tiene hechas editando solamente este archivo.
STOCK_POR_PEDIDO = {t: "pedido" for t in TALLES}

# Lo que Delfi tiene hecho hoy y sale en 1 a 5 días.
# Todo lo que declaró es talle M. Para sumar o sacar stock se edita acá y se
# vuelve a correr este script y construir.py.
HECHO_EN_M = [
    "FRAG-SA-01",  # ricota — saco de jean
    "FRAG-SA-02",  # la multitud — parka de jean
    "FRAG-SA-03",  # tejido social — saco rojo largo tejido
    "FRAG-VE-03",  # rapport — vestido largo de lycra con el logo
    "FRAG-VE-04",  # vestido rojo corto
    "FRAG-PA-01",  # dinosaurio — el jean
    "FRAG-FA-01",  # plaza — la pollera (tiene dos unidades)
    "FRAG-RE-01",  # quién es la ley
    "FRAG-RE-02",  # cerdos
    "FRAG-RE-07",  # charly   ) las de lycra, en las dos mangas: quien
    "FRAG-RE-08",  # batato   ) compra elige corta o larga y las dos
    "FRAG-RE-10",  # rapport  ) salen en 1 a 5 días.
    "FRAG-SH-01",  # 2001 — short de lycra
    "FRAG-SH-02",  # bandera — short de lycra
    "FRAG-SW-01",  # a mano — sweater tejido
]
MEDIDAS = {"columnas": [], "valores": {t: {} for t in TALLES}}

DENIM = ["Denim 100% algodón.", "Lavar del revés en agua fría.", "Secar a la sombra."]
DENIM_P = DENIM + ["Planchar del revés."]
LANA = ["Lana.", "Tejido a mano.", "Lavar a mano en agua fría con jabón neutro."]
LYCRA = ["Lycra de seda.", "Estampado por sublimación digital.",
         "Lavar del revés a mano en agua fría.", "No usar secarropas."]
LYCRA_P = LYCRA + ["Planchar del revés en temperatura baja."]
DTF = ["Jersey 100% algodón.", "Estampado DTF.", "Lavar del revés en agua fría.",
       "No planchar sobre la estampa.", "No usar secarropas."]
MICRO = ["Microtul.", "Lavar a mano en agua fría.", "No retorcer.",
         "No planchar en contacto directo."]

MANGA = {"etiqueta": "manga", "opciones": [
    {"valor": "corta", "precio": 35000}, {"valor": "larga", "precio": 45000}]}

P = []
NOTAS = {}


def add(codigo, slug, nombre, seccion, tipologia, materialidad, tecnica, precio,
        descripcion, ficha, origen, variantes=None, pendiente=None, nota=None):
    # El nombre de fantasía solo no dice qué es la prenda. Se antepone la
    # tipología salvo que el nombre ya la traiga ("vestido rojo").
    completo = (nombre if nombre.startswith(tipologia)
                else "%s %s" % (tipologia, nombre))
    P.append({
        "codigo": codigo, "slug": slug, "nombre": completo, "seccion": seccion,
        "tipologia": tipologia, "materialidad": materialidad, "tecnica": tecnica,
        "talles": TALLES, "estado": "disponible", "plazo": "1 a 2 semanas",
        "precio": precio, "variantes": variantes,
        # El M es el que Delfi tiene hecho. El L siempre se produce a pedido.
        "stock": {"m": "ya" if codigo in HECHO_EN_M else "pedido",
                  "l": "pedido"},
        "descripcion": descripcion,
        "ficha_tecnica": ficha, "composicion_pendiente": True,
        "construccion_pendiente": True, "origen": origen,
        "medidas": json.loads(json.dumps(MEDIDAS)),
        "imagenes": IMG.get(codigo, [])})
    # `nota` queda como recordatorio acá en el código y NO se escribe al JSON:
    # datos/productos.json lo sirve Vercel en abierto y son notas internas.
    # Lo mismo con `pendiente`: es un recordatorio interno, no dato de venta.
    for etiqueta, texto in (("nota", nota), ("pendiente", pendiente)):
        if texto:
            NOTAS.setdefault(codigo, []).append("%s: %s" % (etiqueta, texto))


# sacos y abrigos
add("FRAG-SA-01", "ricota", "ricota", "sacos y abrigos", "saco", "denim", None, 200000,
    "Saco largo de denim, de calce amplio y hombro caído, pensado para usarse abierto y sobre otras capas. El denim arranca rígido y va cediendo con el uso, así que la prenda se acomoda al cuerpo de quien la lleva. Funciona sobre una remera o cerrado, casi como un vestido.",
    DENIM_P,
    "La masa que ocupa el espacio se traduce en una silueta que agranda la presencia del cuerpo en vez de contenerla.")

add("FRAG-SA-02", "la-multitud", "la multitud", "sacos y abrigos", "parka", "denim", None, 150000,
    "Parka de denim con volumen expandido en el cuerpo y en las mangas. La silueta no sigue el entalle: agranda. Admite capas debajo sin ajustar y es la pieza más abrigada de la colección.",
    DENIM_P,
    "El volumen como presencia compartida, el cuerpo que ocupa más lugar del que le corresponde.")

add("FRAG-SA-03", "tejido-social", "tejido social", "sacos y abrigos", "saco largo", "lana", "tejido artesanal", 75000,
    "Saco largo tejido a mano en lana roja, de punto irregular y superficie viva. Cada pieza se teje entera a mano, así que ninguna sale igual a la otra. Pesa y abriga.",
    LANA + ["No retorcer.", "Secar en plano sobre una toalla."],
    "Tejer como acción de unir lo fragmentado: la reconstrucción del tejido social hecha materia, con el rojo como marca de la herida.",
    nota="revisar este precio, está por debajo del sweater con la misma técnica")

# vestidos
add("FRAG-VE-01", "misa", "misa", "vestidos", "vestido", "lana", "tejido artesanal", 350000,
    "Vestido largo tejido a mano en lana roja, de punto abierto. La textura irregular deja pasar la luz y cambia según cómo cae sobre el cuerpo. Se usa solo o sobre una segunda piel.",
    LANA + ["No retorcer.", "Secar en plano."],
    "El tejido como reunión: el punto abierto muestra lo que se unió y lo que quedó sin cerrar.")

add("FRAG-VE-02", "alicia", "alicia", "vestidos", "vestido", "microtul", None, 75000,
    "Vestido de microtul translúcido, que deja ver de manera parcial lo que hay debajo. La transparencia no expone del todo: muestra y reserva al mismo tiempo. Va sobre otra prenda o sobre el cuerpo, según cuánto quieras mostrar.",
    MICRO,
    "Alicia en el país de las maravillas. La doble lectura: decir algo bajo la apariencia de otra cosa.")

# Fuera del brief. La descripción la escribí mirando las fotos, a pedido de
# Delfi; falta que la apruebe. Precio, ficha técnica y origen siguen vacíos.
add("FRAG-VE-04", "vestido-rojo", "vestido rojo", "vestidos", "vestido", "punto", "tejido artesanal", 100000,
    "Vestido corto de punto en hilo rojo con brillo, de textura irregular y transparencias. Manga corta, espalda profunda que cae drapeada y flecos largos en el ruedo que siguen el movimiento. Se usa solo o sobre una segunda piel.",
    ["Tejido de punto en hilo con brillo.",
     "Manga corta y espalda descubierta con caída drapeada.",
     "Flecos en el ruedo.",
     "Lavar a mano en agua fría con jabón neutro.",
     "No retorcer. Secar en plano sobre una toalla."], None,
    pendiente="descripción escrita a partir de las fotos, falta que la apruebes",
    nota="no está en el brief. Falta ficha técnica y origen.")

add("FRAG-VE-03", "vestido-rapport", "rapport", "vestidos", "vestido", "lycra de seda", "sublimación", 90000,
    "Vestido largo de lycra de seda, manga larga con recortes, estampado con el logo de la marca en rapport sobre toda la superficie. La repetición cubre la prenda entera, sin centro ni jerarquía, y los recortes abren zonas del cuerpo que la estampa no llega a tapar. Se adhiere al cuerpo y acompaña el movimiento.",
    ["Lycra de seda.", "Estampado por sublimación digital.", "Manga larga con recortes.",
     "Lavar del revés a mano en agua fría.", "No usar secarropas.",
     "Planchar del revés en temperatura baja."],
    "La repetición como memoria persistente. Lo que insiste no desaparece: vuelve, ocupa superficie y no se deja borrar.")

# pantalones y faldas
add("FRAG-PA-01", "dinosaurio", "dinosaurio", "pantalones y faldas", "pantalón", "denim", None, 80000,
    "Se sostiene por la estructura de la tela, sin necesidad de calce ajustado.", DENIM,
    "Los Dinosaurios. La tensión entre peso y fragilidad: el denim aporta estructura, y el calce amplio esquiva el entalle disciplinado.")

add("FRAG-FA-01", "plaza", "plaza", "pantalones y faldas", "falda", "denim", None, 95000,
    "Falda de denim. Se lleva con las piezas adherentes de la colección o sola, con el saco encima.", DENIM,
    "Las imágenes del Juicio a las Juntas en la calle. El espacio público como lugar donde la imagen circula y se vuelve visible.")

# remeras
add("FRAG-RE-01", "quien-es-la-ley", "quién es la ley", "remeras", "remera", "jersey de algodón", "DTF", 30000,
    "Remera de jersey de algodón con estampa frontal en DTF. Calce recto, para usar sola o debajo de las piezas de abrigo.", DTF,
    "El Juicio a las Juntas. La pregunta por la ley se vuelve inscripción sobre el cuerpo: lo que se dijo en la calle vuelve a circular.")

add("FRAG-RE-02", "cerdos", "cerdos", "remeras", "remera", "jersey de algodón", "DTF", 30000,
    "Remera de jersey de algodón con la tapa de Cerdos & Peces estampada en DTF. La imagen se traslada tal como circulaba: recorte, tipografía y contraste duro. Calce recto, para usar sola o como capa base.", DTF,
    "Cerdos & Peces. La gráfica de circulación marginal: el impreso que pasaba de mano en mano ahora se lleva puesto.")

add("FRAG-RE-03", "trapos", "trapos", "remeras", "remera", "jersey de algodón", "DTF", 30000,
    "Remera de jersey de algodón con el logo de nuevos trapos estampado en DTF. Es la pieza más directa de la colección y la puerta de entrada a la marca. Calce recto, para todos los días.", DTF,
    "La marca como archivo. El wordmark funciona como el contenedor que ordena la saturación del resto de la colección.")

add("FRAG-RE-06", "pais-de-las-maravillas", "país de las maravillas", "remeras", "remera", "microtul", "sublimación", 55000,
    "Remera de microtul, liviana y translúcida, con estampa sublimada. Deja ver parcialmente lo que lleva debajo, así que funciona como capa sobre otra prenda o directamente sobre el cuerpo.",
    ["Microtul.", "Estampado por sublimación digital.", "Lavar a mano en agua fría.",
     "No retorcer.", "No planchar en contacto directo."],
    "Alicia en el país de las maravillas. El camuflaje: mostrar sin mostrar del todo, exposición controlada.")

add("FRAG-RE-07", "charly", "charly", "remeras", "remera", "lycra de seda", "sublimación", 35000,
    "Remera de lycra de seda con el rostro de Charly sublimado. La imagen queda dentro de la fibra, no encima, así que aguanta el uso sin descascararse. El calce es adherente en las dos versiones.",
    LYCRA_P,
    "Los Dinosaurios. La canción que decía bajo censura lo que no se podía decir de frente, ahora puesta sobre el cuerpo.",
    variantes=json.loads(json.dumps(MANGA)))

add("FRAG-RE-08", "batato", "batato", "remeras", "remera", "lycra de seda", "sublimación", 35000,
    "Remera de lycra de seda con la figura de Batato sublimada. La estampa se integra a la fibra y acompaña el movimiento del cuerpo.",
    LYCRA_P,
    "Batato Barea. La teatralidad y el desborde: el cuerpo disidente que se construye a sí mismo como escena.",
    variantes=json.loads(json.dumps(MANGA)))

add("FRAG-RE-10", "remera-rapport", "rapport", "remeras", "remera", "lycra de seda", "sublimación", 35000,
    "Remera de lycra de seda con el logo de nuevos trapos repetido en rapport sobre toda la superficie. La repetición cubre la prenda entera, sin centro ni jerarquía.",
    LYCRA_P,
    "La repetición como memoria persistente. Lo que insiste no desaparece: vuelve, ocupa superficie y no se deja borrar.",
    variantes=json.loads(json.dumps(MANGA)))

# shorts
add("FRAG-SH-01", "2001", "2001", "shorts", "short", "lycra de seda", "sublimación", 75000,
    "Short de lycra de seda con la estampa de Argentina en llamas, de calce adherente. La imagen queda dentro de la fibra y cubre la pieza entera. Acompaña el cuerpo sin restringirlo y funciona como base debajo de las prendas translúcidas o solo.",
    LYCRA,
    "La crisis de 2001. El registro de la calle en llamas como imagen que vuelve.")

add("FRAG-SH-02", "short-bandera", "bandera", "shorts", "short", "lycra de seda", "sublimación", 75000,
    "Short de lycra de seda con estampa pictórica en celeste y rojo, la misma de la remera bandera. La mancha se extiende sin repetirse, así que el recorte cae distinto en cada talle. Calce adherente.",
    LYCRA,
    "Paleta de la colección. El celeste opaco como identidad nacional puesta en crisis y el rojo como herida histórica, juntos y sin resolver.")

# sweaters
add("FRAG-SW-01", "a-mano", "a mano", "sweaters", "sweater", "lana", "tejido artesanal", 150000,
    "Sweater tejido a mano. El punto es denso y la superficie irregular, con las marcas propias del trabajo manual a la vista. Abriga de verdad y sirve como capa media o como pieza principal.",
    LANA + ["Secar en plano."],
    "El hacer manual como construcción de comunidad: las irregularidades no se corrigen, quedan.")

add("FRAG-TEST", "prueba", "prueba de pago", "remeras", "prueba", None, None, 100,
    "Producto de prueba para verificar el circuito de pago. No es una prenda "
    "a la venta y no aparece en la tienda.",
    [], None)
P[-1]["oculto"] = True

doc = {
    "moneda": "ARS",
    "anchos_imagen": man["anchos"],
    "ratios_imagen": RATIO,
    "secciones": ["sacos y abrigos", "vestidos", "pantalones y faldas",
                  "remeras", "shorts", "sweaters"],
    # Bloque 7 del home. Elegidas por Delfi: el vestido tejido largo, la remera
    # de lycra de batato, un pantalón de jean y el saco largo de jean.
    # De los dos pantalones de jean va dinosaurio, que es el que tiene fotos.
    "destacadas": ["FRAG-VE-01", "FRAG-RE-08", "FRAG-PA-01", "FRAG-SA-01"],
    "prendas": P,
}
(RAIZ / "datos").mkdir(exist_ok=True)
(RAIZ / "datos" / "productos.json").write_text(
    json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

secs = {}
for p in P:
    secs.setdefault(p["seccion"], []).append(p["codigo"])
if NOTAS:
    print()
    print("notas internas (no se publican):")
    for c, ns in NOTAS.items():
        for n in ns:
            print("  %s — %s" % (c, n))
print()
print("prendas:", len(P))
for s in doc["secciones"]:
    print("  %-24s %s" % (s, len(secs[s])))
print("sin imagenes:", [p["codigo"] for p in P if not p["imagenes"]])
print("con variantes:", [p["codigo"] for p in P if p["variantes"]])
slugs = [p["slug"] for p in P]
print("slugs unicos:", len(set(slugs)) == len(slugs))
