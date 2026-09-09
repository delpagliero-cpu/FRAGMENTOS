# -*- coding: utf-8 -*-
"""Genera producto/<slug>/index.html a partir de datos/productos.json.

Las fichas no se escriben a mano: se generan todas desde el JSON. Para cargar
fotos, medidas o textos alcanza con editar datos/productos.json y volver a
correr:

    python herramientas/construir.py

El encabezado y el pie se leen de index.html, así nunca se desincronizan de
las páginas escritas a mano.
"""
import html
import json
import os
import re
import shutil

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANCHOS = [600, 1000, 1600]
SITIO = "https://www.nuevostrapos.com.ar"  # sin barra final
WA = "https://wa.me/5493534136713"
IG = "https://www.instagram.com/nuevostrapos.archivo/"

# Editoriales disponibles para el cierre de cada ficha.
CIERRES = ["ed-01", "ed-02", "ed-03", "ed-04", "ed-05",
           "ed-06", "ed-07", "ed-08", "ed-09"]


def e(s):
    return html.escape(str(s), quote=True)


def plata(n):
    return "$" + format(int(n), ",d").replace(",", ".")


def precio_publicable(p):
    """Sin precio no hay compra posible, así que la prenda no se publica."""
    if p.get("variantes"):
        return any(o.get("precio") for o in p["variantes"]["opciones"])
    return p.get("precio") is not None


def leer(nombre):
    with open(os.path.join(RAIZ, nombre), encoding="utf-8") as f:
        return f.read()


def trozo(fuente, etiqueta, clase):
    """Saca <header class="encabezado">…</header> o el <footer> de index.html."""
    m = re.search(
        r'<%s class="%s[^"]*".*?</%s>' % (etiqueta, clase, etiqueta),
        fuente, re.S)
    if not m:
        raise SystemExit("no encontre el %s en index.html" % etiqueta)
    return m.group(0)


def imagen(hash_, alt, sizes, clase="marco--retrato", carga="lazy"):
    if not hash_:
        return ('<div class="marco %s marco--vacio">'
                '<span class="marco__archivo">%s</span></div>' % (clase, e(alt)))
    srcset = ", ".join("/img/prendas/%s-%d.webp %dw" % (hash_, a, a)
                       for a in ANCHOS)
    return (
        '<div class="marco %s">'
        '<img class="marco__img" alt="%s" src="/img/prendas/%s-1000.webp" '
        'srcset="%s" sizes="%s" loading="%s" decoding="async"></div>'
        % (clase, e(alt), hash_, srcset, sizes, carga)
    )


def galeria(p):
    """Todas las fotos que haya. Si no hay ninguna, tres huecos reservados."""
    if not p["imagenes"]:
        return "".join(
            imagen(None, "%s-%d.jpg" % (p["codigo"], i + 1),
                   "(min-width: 900px) 55vw, 100vw")
            for i in range(3))
    return "".join(
        imagen(h, p["nombre"], "(min-width: 900px) 55vw, 100vw",
               carga="eager" if i == 0 else "lazy")
        for i, h in enumerate(p["imagenes"]))


ROTULO_STOCK = {"ya": "1 a 5 días", "pedido": "1 a 2 sem.", "agotado": "agotado"}


def opciones(nombre, etiqueta, valores, precios=None, estados=None):
    filas = []
    # Si algún talle está hecho, arranca seleccionado ése: es el que sale en
    # 1 a 5 días y es la mejor noticia que le podemos dar a quien entra.
    primero = next((i for i, v in enumerate(valores)
                    if estados and estados.get(v) == "ya"), None)
    if primero is None:
        primero = next((i for i, v in enumerate(valores)
                        if not estados or estados.get(v) != "agotado"), None)
    for i, v in enumerate(valores):
        etiq = e(v)
        if precios and precios[i] is not None:
            etiq += " · " + plata(precios[i])
        est = estados.get(v) if estados else None
        if est:
            etiq += "<small>%s</small>" % e(ROTULO_STOCK.get(est, est))
        filas.append(
            '<label class="opcion" aria-label="talle %s, %s">'
            '<input class="opcion__control" type="radio" name="%s" value="%s"'
            ' data-estado="%s"%s%s>'
            '<span class="opcion__cara%s">%s</span></label>'
            % (e(v), e(ROTULO_STOCK.get(est, "")) if est else "sin dato",
               nombre, e(v), e(est or ""),
               " disabled" if est == "agotado" else "",
               " checked" if i == primero else "",
               " opcion__cara--ya" if est == "ya" else "", etiq))
    return (
        '<div class="compra__grupo">'
        '<span class="etiqueta" id="et-%s">%s</span>'
        '<div class="opciones" role="radiogroup" aria-labelledby="et-%s">%s</div>'
        "</div>"
        % (nombre, e(etiqueta), nombre, "".join(filas))
    )


def tabla_medidas(p):
    cols = p["medidas"]["columnas"]
    cabeza = ("<tr><th></th>" + "".join("<th>%s</th>" % e(c) for c in cols)
              + "</tr>") if cols else ""
    ancho = max(len(cols), 3)
    cuerpo = "".join(
        '<tr><th scope="row">%s</th>%s</tr>'
        % (e(t), "".join("<td>%s</td>" % e(p["medidas"]["valores"].get(t, {}).get(c, ""))
                         for c in cols) if cols else "<td></td>" * ancho)
        for t in p["talles"])
    aviso = ("" if cols else
             '<caption class="t-nota" style="text-align:left;'
             'padding-bottom:8px">Si dudás entre dos talles, escribime.</caption>')
    return '<table class="medidas t-cifra">%s<tbody>%s</tbody></table>' % (aviso, cuerpo)


def desplegable(titulo, cuerpo):
    return (
        '<details class="desplegable"><summary class="desplegable__titulo">%s'
        '<span class="desplegable__signo" aria-hidden="true"></span></summary>'
        '<div class="desplegable__cuerpo t-chico">%s</div></details>'
        % (e(titulo), cuerpo)
    )


def ficha(p, encabezado, pie, cierre):
    precio_base = p["precio"]
    if p["variantes"]:
        precio_base = min(o["precio"] for o in p["variantes"]["opciones"])

    if precio_base is None:
        bloque_precio = '<p class="compra__precio pendiente">precio PENDIENTE</p>'
    else:
        bloque_precio = ('<p class="compra__precio t-cifra" data-precio>%s</p>'
                         % plata(precio_base))
    # Las cuotas no se deciden acá. Con Checkout Pro, payment_methods.installments
    # sólo fija un tope, y las cuotas sin interés se activan en la cuenta de
    # Mercado Pago. Quien compra las ve en el checkout de Mercado Pago, que es
    # donde el dato es cierto. Afirmarlas en la ficha sería prometer de más.

    st = p.get("stock") or {}
    primer = next((t for t in p["talles"] if st.get(t) == "ya"), None)
    if primer is None:
        primer = next((t for t in p["talles"] if st.get(t) != "agotado"), None)
    disp = ("entrega en 1 a 5 días" if st.get(primer) == "ya"
            else "hecho para vos · " + p["plazo"])

    selectores = opciones("talle", "talle", p["talles"],
                          estados=p.get("stock"))
    selectores += ('<p class="compra__medidas"><a href="#medidas">'
                   "tabla de medidas</a></p>")
    if p["variantes"]:
        v = p["variantes"]
        selectores += opciones(
            "variante", v["etiqueta"],
            [o["valor"] for o in v["opciones"]],
            [o["precio"] for o in v["opciones"]])

    # cómo está hecha
    lineas = "".join("<p>%s</p>" % e(l) for l in p["ficha_tecnica"])
    # La composición exacta todavía no está cargada. Es una nota interna, no
    # algo que le sirva a quien compra, así que no se muestra en la ficha:
    # queda marcada en productos.json hasta que Delfi la complete.

    bloques = ""
    if p["descripcion"]:
        bloques += ('<div class="ficha__descripcion t-cuerpo"><p>%s</p>%s</div>'
                    % (e(p["descripcion"]),
                       ('<p class="pendiente t-nota">%s</p>'
                        % e(p["descripcion_pendiente"]))
                       if p.get("descripcion_pendiente") else ""))
    else:
        bloques += ('<div class="ficha__descripcion"><p class="pendiente">'
                    "descripción PENDIENTE</p></div>")

    bloques += desplegable("cómo está hecha", lineas or
                           '<p class="pendiente">PENDIENTE</p>')
    bloques += ('<details class="desplegable" id="medidas">'
                '<summary class="desplegable__titulo">medidas'
                '<span class="desplegable__signo" aria-hidden="true"></span>'
                '</summary><div class="desplegable__cuerpo">%s</div></details>'
                % tabla_medidas(p))
    bloques += desplegable("origen", "<p>%s</p>" % e(p["origen"]) if p["origen"]
                           else '<p class="pendiente">origen PENDIENTE</p>')

    portada = ("/img/prendas/%s-1000.webp" % p["imagenes"][0]
               if p["imagenes"] else "/img/editoriales/hero-1600.webp")

    return TEMPLATE % {
        "titulo": e(p["nombre"]) + " — nuevos trapos",
        "descripcion": e(p["descripcion"] or p["nombre"]),
        "portada": portada,
        "encabezado": encabezado,
        "pie": pie,
        "nombre": e(p["nombre"]),
        "precio": bloque_precio,
        "disponibilidad": e(disp),
        "selectores": selectores,
        "galeria": galeria(p),
        "bloques": bloques,
        "cierre": cierre,
        "codigo": e(p["codigo"]),
        "sitio": SITIO,
        "ruta": "/producto/%s/" % p["slug"],
    }


TEMPLATE = """<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(titulo)s</title>
<meta name="description" content="%(descripcion)s">
<meta property="og:title" content="%(titulo)s">
<meta property="og:description" content="%(descripcion)s">
<meta property="og:type" content="product">
<meta property="og:image" content="%(sitio)s%(portada)s">
<meta property="og:url" content="%(sitio)s%(ruta)s">
<link rel="canonical" href="%(sitio)s%(ruta)s">
<meta property="og:locale" content="es_AR">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Courier+Prime:wght@400;700&family=Special+Elite&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/base.css">
<link rel="stylesheet" href="/css/sitio.css">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/img/wordmark.svg" type="image/svg+xml">
</head>
<body>

<a class="saltar" href="#contenido">saltar al contenido</a>

%(encabezado)s

<main id="contenido">
  <div class="contenedor">
    <div class="ficha">

      <div class="galeria">%(galeria)s</div>

      <div class="compra" data-compra data-codigo="%(codigo)s">
        <h1 class="compra__nombre">%(nombre)s</h1>
        %(precio)s
        <p class="compra__disponibilidad"><span class="marca"></span><span data-entrega>%(disponibilidad)s</span></p>
        %(selectores)s
        <div class="compra__accion">
          <button class="boton boton--ancho boton--invertido" type="button" data-comprar>Comprar</button>
          <p class="t-nota pendiente" data-comprar-estado role="status"></p>
          <p class="compra__letrachica">
            Pagás en Mercado Pago. No guardo ningún dato de tu tarjeta.<br>
            Envíos a todo el país. <a href="/contacto.html">Escribime</a> para
            saber el costo a tu zona.<br>
            También podés pagar por transferencia.
          </p>
          <div class="pagos" aria-label="medios de pago">
            <span>crédito</span><span>débito</span><span>Rapipago</span>
            <span>Pago Fácil</span><span>Mercado Pago</span><span>cuotas sin tarjeta</span>
          </div>
        </div>
      </div>

    </div>

    <div class="ficha__bloques">%(bloques)s</div>

    <div class="confianza">
      <div class="confianza__item">
        <h2 class="confianza__titulo">cuándo llega</h2>
        <p class="confianza__texto">Lo que está hecho sale en 1 a 5 días. Lo que se produce a pedido llega en una o dos semanas desde que se acredita el pago.</p>
      </div>
      <div class="confianza__item">
        <h2 class="confianza__titulo">cómo se paga</h2>
        <p class="confianza__texto">El pago se hace dentro de Mercado Pago, no en este sitio. Tarjeta, efectivo, dinero en cuenta o transferencia.</p>
      </div>
      <div class="confianza__item">
        <h2 class="confianza__titulo">si algo sale mal</h2>
        <p class="confianza__texto">Cualquier falla de confección o problema del producto lo resuelvo. Escribime y lo vemos.</p>
      </div>
      <div class="confianza__item">
        <h2 class="confianza__titulo">quién está atrás</h2>
        <p class="confianza__texto">Delfina Pagliero, Córdoba. Cada prenda la reviso una por una antes de que salga.</p>
      </div>
    </div>
  </div>

  <div class="ficha__editorial">%(cierre)s</div>
</main>

%(pie)s

<script type="module">
import { aviso, pintarContador, medirEncabezado, marcarPagina } from "/js/sitio.js";
import { conectar as conectarCarrito, agregar, abrir } from "/js/carrito.js";
aviso(document.querySelector(".aviso"));
pintarContador();
medirEncabezado();
marcarPagina();
conectarCarrito();
document.addEventListener("carrito:cambio", pintarContador);
document.querySelector("[data-newsletter]").addEventListener("submit", (ev) => {
  ev.preventDefault();
  ev.target.querySelector("[data-newsletter-estado]").textContent =
    "todavía no está conectado.";
});

/* La entrega sigue al talle elegido: puede haber un M hecho y un L a pedido. */
const ROTULOS = { ya: "entrega en 1 a 5 días", pedido: "hecho para vos · 1 a 2 semanas" };
const linea = document.querySelector("[data-entrega]");
document.querySelectorAll('input[name="talle"]').forEach((r) => {
  r.addEventListener("change", () => {
    if (linea && ROTULOS[r.dataset.estado]) linea.textContent = ROTULOS[r.dataset.estado];
  });
});

/* El precio sigue al selector de manga. */
const precios = %%(preciosJson)s;
const caja = document.querySelector("[data-precio]");
document.querySelectorAll('input[name="variante"]').forEach((r) => {
  r.addEventListener("change", () => {
    if (caja && precios[r.value] !== undefined) caja.textContent = precios[r.value];
  });
});

/* El carrito llega en la etapa 5. */
/* Comprar suma al carrito con el talle y la variante elegidos y abre el panel. */
document.querySelector("[data-comprar]").addEventListener("click", () => {
  const compra = document.querySelector("[data-compra]");
  const talle = compra.querySelector('input[name="talle"]:checked');
  const variante = compra.querySelector('input[name="variante"]:checked');
  const estado = document.querySelector("[data-comprar-estado]");
  if (!talle) { estado.textContent = "elegí un talle"; return; }
  estado.textContent = "";
  agregar({
    codigo: compra.dataset.codigo,
    talle: talle.value,
    variante: variante ? variante.value : null,
    cantidad: 1
  });
  abrir();
});
</script>

</body>
</html>
"""


TEMPLATE_TEXTO = """<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(titulo)s</title>
<meta name="description" content="%(descripcion)s">
<meta property="og:title" content="%(titulo)s">
<meta property="og:description" content="%(descripcion)s">
<meta property="og:type" content="website">
<meta property="og:image" content="%(sitio)s/img/editoriales/hero-1600.webp">
<meta property="og:url" content="%(sitio)s%(ruta)s">
<link rel="canonical" href="%(sitio)s%(ruta)s">
<meta property="og:locale" content="es_AR">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Courier+Prime:wght@400;700&family=Special+Elite&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/base.css">
<link rel="stylesheet" href="/css/sitio.css">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/img/wordmark.svg" type="image/svg+xml">
</head>
<body>

<a class="saltar" href="#contenido">saltar al contenido</a>

%(encabezado)s

<main id="contenido">
%(cuerpo)s
</main>

%(pie)s

<script type="module">
import { aviso, pintarContador, medirEncabezado } from "/js/sitio.js";
import { conectar as conectarCarrito } from "/js/carrito.js";
aviso(document.querySelector(".aviso"));
pintarContador();
medirEncabezado();
conectarCarrito();
document.addEventListener("carrito:cambio", pintarContador);
document.querySelector("[data-newsletter]").addEventListener("submit", (ev) => {
  ev.preventDefault();
  ev.target.querySelector("[data-newsletter-estado]").textContent =
    "todavía no está conectado.";
});
</script>

</body>
</html>
"""


def editorial(nombre, alto="clamp(260px, 52vh, 620px)"):
    return (
        '<div class="sobre__imagen"><img src="/img/editoriales/%s-1600.webp" '
        'srcset="/img/editoriales/%s-900.webp 900w, '
        '/img/editoriales/%s-1600.webp 1600w, '
        '/img/editoriales/%s-2400.webp 2400w" sizes="100vw" alt="" '
        'loading="lazy" decoding="async" style="height:%s"></div>'
        % (nombre, nombre, nombre, nombre, alto)
    )


# Copy literal de los §5 y §8 del brief. Acá vive todo el concepto: la tienda
# quedó en el home para que se entre y se vean las prendas de una.
SOBRE = (
    '<h1 class="solo-lector">sobre la marca</h1>'
    + editorial("hero", "clamp(320px, 62vh, 720px)") +
    '<div class="contenedor sobre">'

    '<p class="kicker">la colección</p>'
    '<div class="sobre__bloque t-destacado" style="margin-top:var(--e-3)">'
    "<p>Veinte prendas construidas a partir de una investigación sobre la "
    "contracultura argentina de los años setenta y ochenta, traducida a "
    "materiales, siluetas y superficies.</p>"
    "</div>"

    + editorial("ed-04") +

    '<p class="kicker">la idea</p>'
    '<div class="sobre__bloque t-destacado" style="margin-top:var(--e-3)">'
    "<p>Esto empezó hace dos años.</p>"
    "<p>El diseño de autor no se sostiene solo con arte, requiere procesos "
    "productivos y planificación. Y la moda, cuando es lenguaje y no "
    "decoración, puede acompañar a quienes no se resignan a que dé todo igual.</p>"
    "</div>"

    '<div class="sobre__bloque t-destacado" style="margin-top:var(--e-4)">'
    "<p>Fragmentos parte de una investigación sobre la contracultura argentina "
    "de los setenta y ochenta. La colección no copia esas imágenes: traduce lo "
    "que hacían. La transparencia que muestra a medias. La repetición que "
    "insiste. El volumen que agranda el cuerpo en vez de contenerlo.</p>"
    "</div>"

    + editorial("ed-08") +

    '<p class="kicker">cómo se hace</p>'
    '<div class="columnas" style="margin-top:var(--e-4)">'
    '<div><h2 class="columna__titulo">fuente</h2>'
    '<p class="t-cuerpo">Cada prenda parte de una obra concreta de la '
    "contracultura argentina. Una misa, una canción, una revista, una "
    "performance.</p></div>"
    '<div><h2 class="columna__titulo">operación</h2>'
    '<p class="t-cuerpo">De esa obra no se copia la imagen: se traduce lo que '
    "hace. La saturación, la repetición, la transparencia, el volumen.</p></div>"
    '<div><h2 class="columna__titulo">prenda</h2>'
    '<p class="t-cuerpo">Eso se convierte en decisiones materiales. Qué tela, '
    "qué peso, qué caída, qué se muestra y qué se tapa.</p></div>"
    "</div>"

    '<p style="margin-top:var(--e-6)">'
    '<a class="boton" href="/">Ver las prendas</a></p>'
    "</div>"
)

# Copy literal del §9. Las dos PENDIENTE quedan marcadas, no inventadas.
PREGUNTAS = [
    ("¿Cuánto tarda mi pedido?",
     "Entre una y dos semanas desde que se confirma el pago. Las remeras y los "
     "shorts salen más rápido. Los tejidos a mano y el denim llevan el plazo "
     "completo.", False),
    ("¿Cómo son los talles?",
     "Trabajo con S, M y L en una línea amplia, pensada para que la prenda no "
     "dependa de un calce ajustado. En cada ficha están las medidas exactas. Si "
     "dudás entre dos talles, escribime.", False),
    ("¿Puedo cambiar la prenda?",
     "Como cada pieza se produce a pedido, no hago cambios por arrepentimiento. "
     "Sí resuelvo cualquier problema de confección o falla del producto. "
     "Escribime y lo vemos.", False),
    # Copy escrito por mí, no está en el brief: reemplaza los dos PENDIENTE que
    # se veían en la página. No afirma nada que no sepamos.
    ("¿Hacen envíos?",
     "Sí, a todo el país. Escribime y te paso el costo hasta tu zona.", False),
    ("¿Puedo retirar en persona?",
     "Escribime y lo vemos.", False),
    ("¿Cómo cuido las prendas?",
     "Cada prenda viene con sus instrucciones y están también en la ficha. En "
     "general: agua fría, lavado a mano en las piezas tejidas y estampadas, "
     "nada de secarropas. Las estampas nunca se planchan de frente.", False),
    ("¿Por qué se hace a pedido?",
     "Para no acumular stock ni desperdiciar tela, y para poder revisar cada "
     "prenda una por una antes de que salga.", False),
]

# Los títulos son la estructura, no el texto. El contenido legal lo escribe
# Delfi (o quien la asesore): no se inventa acá.
TERMINOS_PUNTOS = [
    "quién vende",
    "precios y moneda",
    "medios de pago",
    "plazos de producción y entrega",
    "envíos",
    "cambios, devoluciones y fallas",
    "botón de arrepentimiento",
    "datos personales",
]


def pagina_preguntas():
    filas = "".join(
        '<div class="pregunta"><h2 class="pregunta__titulo">%s</h2>%s</div>'
        % (e(t),
           ('<p class="pendiente">PENDIENTE · %s</p>' % e(r)) if pend
           else ('<p class="t-cuerpo">%s</p>' % e(r)))
        for t, r, pend in PREGUNTAS)
    return ('<div class="contenedor preguntas">'
            '<h1 class="t-titulo" style="margin-bottom:var(--e-5)">'
            "preguntas frecuentes</h1>" + filas + "</div>")


def pagina_contacto():
    """Página propia: los canales se muestran y recién al tocarlos se sale.
    Tocar "contacto" ya no dispara WhatsApp de una."""
    return (
        '<div class="contenedor" style="padding-block:var(--e-6)">'
        '<p class="kicker">contacto</p>'
        '<h1 class="t-titulo" style="margin-top:var(--e-2)">contacto</h1>'
        '<p class="t-cuerpo lectura" style="margin-top:var(--e-2)">'
        "Para consultar por un talle, encargar una pieza especial o resolver "
        "cualquier problema con un pedido.</p>"

        '<div class="confianza" style="margin-top:var(--e-5)">'

        '<div class="confianza__item">'
        '<h2 class="confianza__titulo">WhatsApp</h2>'
        '<p class="t-cuerpo t-cifra" style="margin-block:var(--e-1)">'
        "+54 9 3534 13-6713</p>"
        '<p class="confianza__texto">Lo más rápido para dudas de talle o encargos.</p>'
        '<p style="margin-top:var(--e-2)">'
        '<a class="boton" href="%s" target="_blank" rel="noopener">'
        "Abrir WhatsApp</a></p>"
        "</div>"

        '<div class="confianza__item">'
        '<h2 class="confianza__titulo">Instagram</h2>'
        '<p class="t-cuerpo" style="margin-block:var(--e-1)">@nuevostrapos.archivo</p>'
        '<p class="confianza__texto">Las prendas puestas, los procesos y lo que va saliendo.</p>'
        '<p style="margin-top:var(--e-2)">'
        '<a class="boton" href="%s" target="_blank" rel="noopener">'
        "Abrir Instagram</a></p>"
        "</div>"

        "</div>"

        '<div class="datos" style="margin-top:var(--e-5)">'
        '<div><p class="rotulo">marca</p>'
        '<p class="datos__valor">nuevos trapos</p></div>'
        '<div><p class="rotulo">a cargo</p>'
        '<p class="datos__valor">Delfina Pagliero</p></div>'
        '<div><p class="rotulo">dónde</p>'
        '<p class="datos__valor">córdoba, argentina</p></div>'
        '<div><p class="rotulo">envíos</p>'
        '<p class="datos__valor">a todo el país</p></div>'
        "</div>"
        "</div>" % (WA, IG)
    )


WORDMARK_SVG = (
    '<svg viewBox="0 0 780 105" fill="currentColor" role="img" '
    'aria-label="nuevos trapos" '
    'style="width:min(100%,300px);margin-inline:auto">'
    '<g font-family="Special Elite, Courier New, monospace" font-size="100">'
    '<text x="0" y="80" textLength="240" lengthAdjust="spacing">nuev</text>'
    '<circle cx="270" cy="54.2" r="25.8"/>'
    '<text x="300" y="80" textLength="480" lengthAdjust="spacing">s trapos</text>'
    "</g></svg>")


# Copy literal del §10 del brief.
RETORNOS = {
    "aprobado": {
        "titulo": "pago aprobado",
        "estado": "listo. tu pedido entró.",
        "cuerpo": "<p class=\"t-cuerpo\">Te llega un mail de Mercado Pago con el "
                  "comprobante. Si es una prenda hecha sale en 1 a 5 días; si se "
                  "produce a pedido llega en una o dos semanas.</p>",
        "acciones": '<a class="boton" href="/">Seguir mirando</a>'
                    '<a class="boton" href="/contacto.html">Escribime</a>',
        "vaciar": True,
    },
    "pendiente": {
        "titulo": "pago pendiente",
        "estado": "tu pago está en proceso.",
        "cuerpo": "<p class=\"t-cuerpo\">Cuando se acredite te confirmo por mail "
                  "y ahí arranca la producción.</p>"
                  "<p class=\"t-chico\" style=\"margin-top:16px\">Si elegiste "
                  "Rapipago o Pago Fácil, todavía falta un paso: Mercado Pago te "
                  "mandó un cupón por mail y tenés que pagarlo en el local. El "
                  "pedido queda reservado hasta entonces.</p>",
        "acciones": '<a class="boton" href="/">Seguir mirando</a>'
                    '<a class="boton" href="/contacto.html">Escribime</a>',
        "vaciar": False,
    },
    "rechazado": {
        "titulo": "pago rechazado",
        "estado": "el pago no se pudo procesar.",
        "cuerpo": "<p class=\"t-cuerpo\">No se hizo ningún cobro. Podés "
                  "intentarlo de nuevo con otro medio de pago.</p>"
                  "<p class=\"t-chico\" style=\"margin-top:16px\">También podés "
                  "pagar por transferencia: escribime y te paso el alias.</p>",
        "acciones": '<a class="boton boton--invertido" href="/">Volver a intentar</a>'
                    '<a class="boton" href="/contacto.html">Escribime</a>',
        "vaciar": False,
    },
}


def pagina_retorno(clave):
    r = RETORNOS[clave]
    limpiar = (
        'try { localStorage.removeItem("nt.carrito"); } catch (e) {}'
        if r["vaciar"] else "")
    guion = (
        '<script type="module">'
        'const q = new URLSearchParams(location.search);'
        'const caja = document.querySelector("[data-orden]");'
        'caja.textContent = q.get("external_reference") || "no informado";'
        + limpiar +
        "</scr" + "ipt>")
    return (
        '<div class="contenedor retorno">'
        + WORDMARK_SVG +
        '<h1 class="retorno__estado">%s</h1>' % e(r["estado"])
        + r["cuerpo"] +
        '<p class="rotulo" style="margin-top:24px">número de orden</p>'
        '<p class="retorno__orden" data-orden>—</p>'
        '<div class="retorno__acciones">%s</div>' % r["acciones"]
        + "</div>" + guion
    )


def pagina_terminos():
    # Los títulos quedan como comentario HTML: le sirven a Delfi para saber qué
    # escribir, y no le muestran al comprador una página llena de huecos.
    puntos = "<!-- estructura a completar:" + " · ".join(TERMINOS_PUNTOS) + " -->"
    return (
        '<div class="contenedor terminos">'
        '<h1 class="t-titulo" style="margin-bottom:var(--e-3)">'
        "términos y condiciones</h1>"
        '<p class="t-cuerpo lectura" style="margin-bottom:var(--e-4)">'
        "Estoy redactando los términos y condiciones de compra. Mientras "
        "tanto, cualquier duda sobre un pedido la resuelvo por WhatsApp.</p>"
        + puntos +
        '<p class="t-nota" style="margin-top:var(--e-4)">'
        "Ante cualquier duda sobre una compra, "
        '<a href="%s" target="_blank" rel="noopener">Escribime</a>.</p>'
        "</div>" % WA
    )


def main():
    prods = json.loads(leer("datos/productos.json"))
    indice = leer("index.html")
    encabezado = trozo(indice, "header", "encabezado")
    pie = trozo(indice, "footer", "contenedor pie")

    destino = os.path.join(RAIZ, "producto")
    if os.path.isdir(destino):
        shutil.rmtree(destino)

    vendibles = [p for p in prods["prendas"] if precio_publicable(p)]
    ocultas = [p["codigo"] for p in prods["prendas"] if not precio_publicable(p)]

    for i, p in enumerate(vendibles):
        cierre = CIERRES[i % len(CIERRES)]
        img_cierre = (
            '<img src="/img/editoriales/%s-1600.webp" '
            'srcset="/img/editoriales/%s-900.webp 900w, '
            '/img/editoriales/%s-1600.webp 1600w, '
            '/img/editoriales/%s-2400.webp 2400w" sizes="100vw" '
            'alt="" loading="lazy" decoding="async" '
            'style="width:100%%;height:clamp(320px,60vh,700px);object-fit:cover">'
            % (cierre, cierre, cierre, cierre))

        precios = {}
        if p["variantes"]:
            for o in p["variantes"]["opciones"]:
                precios[o["valor"]] = plata(o["precio"])

        cuerpo = ficha(p, encabezado, pie, img_cierre)
        cuerpo = cuerpo.replace("%(preciosJson)s",
                                json.dumps(precios, ensure_ascii=False))

        carpeta = os.path.join(destino, p["slug"])
        os.makedirs(carpeta, exist_ok=True)
        with open(os.path.join(carpeta, "index.html"), "w", encoding="utf-8") as f:
            f.write(cuerpo)
        print("  producto/%s/" % p["slug"])

    print("\nfichas generadas:", len(vendibles), "de", len(prods["prendas"]))
    if ocultas:
        print("sin publicar por falta de precio:", ", ".join(ocultas))

    paginas = [
        ("sobre.html", "sobre la marca — nuevos trapos",
         "El diseño de autor no se sostiene solo con arte, requiere procesos "
         "productivos y planificación.", SOBRE),
        ("preguntas.html", "preguntas frecuentes — nuevos trapos",
         "Plazos, talles, cambios, envíos y cuidado de las prendas.",
         pagina_preguntas()),
        ("pago/aprobado.html", "pago aprobado — nuevos trapos",
         "Tu pedido entró.", pagina_retorno("aprobado")),
        ("pago/pendiente.html", "pago pendiente — nuevos trapos",
         "Tu pago está en proceso.", pagina_retorno("pendiente")),
        ("pago/rechazado.html", "pago rechazado — nuevos trapos",
         "El pago no se pudo procesar.", pagina_retorno("rechazado")),
        ("contacto.html", "contacto — nuevos trapos",
         "WhatsApp e Instagram de nuevos trapos. Córdoba, Argentina.",
         pagina_contacto()),
        ("terminos.html", "términos y condiciones — nuevos trapos",
         "Términos y condiciones de compra.", pagina_terminos()),
    ]
    for archivo, titulo, desc, cuerpo in paginas:
        destino_pag = os.path.join(RAIZ, archivo)
        os.makedirs(os.path.dirname(destino_pag), exist_ok=True)
        with open(destino_pag, "w", encoding="utf-8") as f:
            f.write(TEMPLATE_TEXTO % {
                "titulo": e(titulo), "descripcion": e(desc),
                "encabezado": encabezado, "pie": pie, "cuerpo": cuerpo,
                "sitio": SITIO, "ruta": "/" + archivo})
        print("  " + archivo)


if __name__ == "__main__":
    main()
