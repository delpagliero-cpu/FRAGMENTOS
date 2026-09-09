/* nuevos trapos — comportamiento compartido
   ---------------------------------------------------------------------------
   Sin dependencias. Todo lo que necesita datos de producto los lee de
   datos/productos.json, así cargar fotos o medidas es editar ese archivo y
   nada más.
   --------------------------------------------------------------------------- */

/* datos ------------------------------------------------------------------ */

let _datos = null;

export async function datos() {
  if (!_datos) {
    const r = await fetch("/datos/productos.json", { cache: "no-cache" });
    if (!r.ok) throw new Error("no se pudo leer productos.json: " + r.status);
    _datos = await r.json();
  }
  return _datos;
}

/* formato ---------------------------------------------------------------- */

export function precio(n) {
  if (n === null || n === undefined) return "";
  return "$" + n.toLocaleString("es-AR");
}

/* Hay entrega inmediata si al menos un talle está hecho. */
export function hayStock(p) {
  return !!p.stock && Object.values(p.stock).some((v) => v === "ya");
}

export function talleComprable(p) {
  return !p.stock || Object.values(p.stock).some((v) => v !== "agotado");
}

export function disponibilidad(p) {
  if (hayStock(p)) return "entrega en 1 a 5 días";
  return "hecho para vos · " + p.plazo;
}

/* Sin precio no se puede comprar, así que la prenda no se muestra en la
   tienda. Vuelve sola en cuanto se le carga el precio en productos.json. */
export function publicable(p) {
  if (p.oculto) return false;
  if (p.variantes && p.variantes.opciones.length) {
    return p.variantes.opciones.some((o) => o.precio != null);
  }
  return p.precio != null;
}

/* Precio a mostrar en grilla: si la prenda tiene variantes, la más barata,
   que es la que queda seleccionada por defecto en la ficha. */
export function precioDesde(p) {
  if (p.variantes && p.variantes.opciones.length) {
    return Math.min(...p.variantes.opciones.map((o) => o.precio));
  }
  return p.precio;
}

/* imágenes --------------------------------------------------------------- */

const ANCHOS = [600, 1000, 1600];

/* Placeholder del §12: rectángulo apenas más oscuro que el fondo con el
   nombre del archivo que va a ir ahí. Sin ícono y sin la palabra placeholder. */
export function foto(prenda, indice, sizes, clase) {
  const marco = clase || "marco--retrato";
  const hash = prenda.imagenes[indice];
  if (!hash) {
    const archivo = prenda.codigo + "-" + (indice + 1) + ".jpg";
    return (
      '<div class="marco ' + marco + ' marco--vacio">' +
      '<span class="marco__archivo">' + archivo + "</span></div>"
    );
  }
  const srcset = ANCHOS.map(
    (a) => "/img/prendas/" + hash + "-" + a + ".webp " + a + "w"
  ).join(", ");
  return (
    '<div class="marco ' + marco + '">' +
    '<img class="marco__img" alt="' + escapar(prenda.nombre) + '"' +
    ' src="/img/prendas/' + hash + '-1000.webp"' +
    ' srcset="' + srcset + '"' +
    ' sizes="' + sizes + '"' +
    ' loading="lazy" decoding="async"></div>'
  );
}

export function escapar(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

/* tarjeta de prenda ------------------------------------------------------ */

/* Las tipologías que se acercan necesitan pedir una imagen más grande: si no,
   el navegador elige la chica y al ampliarla se ve borrosa. */
const ACERCADAS = { remera: 1.75, sweater: 1.45, short: 1.6, "pantalón": 1.35, falda: 1.4 };

function sizesSegunTipo(sizes, tipologia) {
  const z = ACERCADAS[tipologia];
  if (!z) return sizes;
  return sizes.replace(/(\d+)vw/g, (m, n) => Math.round(+n * z) + "vw");
}

export function tarjeta(p, sizes) {
  const sello = hayStock(p)
    ? '<span class="prenda__ya">1 a 5 días</span>' : "";
  const pr = precioDesde(p);
  return (
    "<article>" +
    '<a class="prenda__enlace" data-tipo="' + escapar(p.tipologia || "") +
    '" href="/producto/' + p.slug + '/">' +
    '<div class="prenda__foto">' +
    foto(p, 0, sizesSegunTipo(sizes, p.tipologia)) + sello + "</div>" +
    '<div class="prenda__datos">' +
    '<p class="prenda__nombre">' + escapar(p.nombre) + "</p>" +
    (pr ? '<p class="prenda__precio t-cifra">' + precio(pr) + "</p>"
        : '<p class="prenda__precio pendiente">precio PENDIENTE</p>') +
    '<p class="prenda__disponibilidad"><span class="marca"></span>' +
    escapar(disponibilidad(p)) + "</p>" +
    (talleComprable(p) ? "" :
      '<p class="prenda__disponibilidad">sin talles disponibles</p>') +
    "</div></a></article>"
  );
}

/* tira del home ---------------------------------------------------------- */

/* No hay recortes en PNG con fondo transparente, así que la tira va con las
   fotos de producto. Sólo entran las prendas que ya tienen foto. */
export function tiraPrenda(p) {
  return (
    '<a class="tira__prenda" href="/producto/' + p.slug + '/"' +
    ' aria-label="' + escapar(p.nombre) + '">' +
    foto(p, 0, "clamp(150px, 40vw, 220px)") +
    "</a>"
  );
}

/* barra de aviso --------------------------------------------------------- */

/* Reemplazo seco cada 6 s, sin fundido: el brief prohíbe animaciones.
   Los dos mensajes viven en el DOM; el lector de pantalla lee el bloque una
   sola vez (aria-live off) y no se lo interrumpe cada seis segundos. */
export function aviso(nodo) {
  const mensajes = [...nodo.querySelectorAll("[data-aviso]")];
  if (mensajes.length < 2) return;
  let i = 0;
  const paso = () => {
    if (document.hidden) return;
    mensajes[i].hidden = true;
    i = (i + 1) % mensajes.length;
    mensajes[i].hidden = false;
  };
  setInterval(paso, 6000);
}

/* encabezado ------------------------------------------------------------- */

/* El encabezado es pegajoso y cambia de alto entre teléfono y escritorio.
   Publicarlo como variable CSS deja que las anclas y la columna de compra
   se posicionen solas, sin números mágicos. */
export function medirEncabezado() {
  const enc = document.querySelector(".encabezado");
  if (!enc) return;
  const aplicar = () => {
    document.documentElement.style.setProperty(
      "--alto-encabezado", Math.round(enc.getBoundingClientRect().height) + "px"
    );
  };
  aplicar();
  /* La fuente web cambia el alto del encabezado cuando termina de cargar, y el
     filtro se inyecta después de este llamado. */
  if (document.fonts) document.fonts.ready.then(aplicar);
  addEventListener("load", aplicar);
  if (window.ResizeObserver) new ResizeObserver(aplicar).observe(enc);
  else addEventListener("resize", aplicar);
}

/* En el teléfono el encabezado se lleva demasiado alto de pantalla. Se esconde
   al bajar y vuelve al subir, que es cuando la persona busca el menú. En
   escritorio no hace falta: hay lugar de sobra. */
export function ocultarAlBajar() {
  const raiz = document.documentElement;
  let anterior = scrollY;
  let ultimo = 0;

  const revisar = () => {
    if (!matchMedia("(max-width: 799px)").matches) {
      raiz.classList.remove("enc-oculto");
      anterior = scrollY;
      return;
    }
    const y = scrollY;
    const bajando = y > anterior;
    /* Arriba de todo siempre se ve, y no reacciona a movimientos mínimos. */
    if (y < 140 || Math.abs(y - anterior) < 6) { anterior = y; return; }
    raiz.classList.toggle("enc-oculto", bajando);
    anterior = y;
  };

  /* Con un temporizador y no con requestAnimationFrame: rAF se congela cuando
     la pestaña no está a la vista y el encabezado quedaba trabado. */
  addEventListener("scroll", () => {
    const ahora = Date.now();
    if (ahora - ultimo < 80) return;
    ultimo = ahora;
    revisar();
  }, { passive: true });
}

/* Marca en el menú la página en la que estás. Sin esto no hay forma de saber
   dónde estás parado dentro del sitio. */
export function marcarPagina() {
  const aqui = location.pathname.replace(/index\.html$/, "");
  document.querySelectorAll(".doc__der a[href]").forEach((a) => {
    const destino = a.getAttribute("href").replace(/index\.html$/, "");
    const enTienda = destino === "/" &&
      (aqui === "/" || aqui.startsWith("/producto/"));
    if (enTienda || (destino !== "/" && aqui.startsWith(destino))) {
      a.setAttribute("aria-current", "page");
    }
  });
}

/* Lleva a una sección dejándola por debajo del encabezado pegajoso.
   El alto se mide en el momento del salto y no se lee de la variable CSS:
   así nunca queda desactualizado si el encabezado cambió de alto. */
export function irASeccion(id, empujar) {
  const destino = document.getElementById(id);
  if (!destino) return;
  /* Se descuenta todo lo que quede pegado arriba: la barra negra y el filtro
     son dos elementos separados y los dos tapan el destino. */
  const alto = [".encabezado", ".filtro"].reduce((suma, sel) => {
    const el = document.querySelector(sel);
    if (!el) return suma;
    const pos = getComputedStyle(el).position;
    return (pos === "sticky" || pos === "fixed")
      ? suma + el.getBoundingClientRect().height : suma;
  }, 0);
  const quieto = matchMedia("(prefers-reduced-motion: reduce)").matches;
  scrollTo({
    top: destino.getBoundingClientRect().top + scrollY - alto - 16,
    behavior: quieto ? "auto" : "smooth"
  });
  if (empujar) history.pushState(null, "", "#" + id);
}

export function conectarFiltro(enlaces) {
  enlaces.forEach((a) => {
    a.addEventListener("click", (ev) => {
      const id = a.getAttribute("href").slice(1);
      if (!document.getElementById(id)) return;
      ev.preventDefault();
      irASeccion(id, true);
    });
  });
}

/* Marca en el filtro la sección que se está mirando. */
export function seguirSecciones(enlaces, secciones) {
  if (!("IntersectionObserver" in window) || !secciones.length) return;
  const porId = new Map(enlaces.map((a) => [a.getAttribute("href").slice(1), a]));
  const visibles = new Set();
  const obs = new IntersectionObserver((entradas) => {
    for (const e of entradas) {
      if (e.isIntersecting) visibles.add(e.target.id);
      else visibles.delete(e.target.id);
    }
    const primera = secciones.find((s) => visibles.has(s.id));
    enlaces.forEach((a) => a.removeAttribute("aria-current"));
    if (primera && porId.has(primera.id)) {
      porId.get(primera.id).setAttribute("aria-current", "true");
    }
  }, { rootMargin: "-45% 0px -45% 0px" });
  secciones.forEach((s) => obs.observe(s));
}

/* carrito — sólo la cáscara; la lógica completa llega en la etapa 5 -------- */

export const CARRITO_CLAVE = "nt.carrito";

export function leerCarrito() {
  try {
    return JSON.parse(localStorage.getItem(CARRITO_CLAVE)) || [];
  } catch {
    return [];
  }
}

export function contarCarrito() {
  return leerCarrito().reduce((n, i) => n + (i.cantidad || 0), 0);
}

export function pintarContador() {
  const n = contarCarrito();
  document.querySelectorAll("[data-carrito-cuenta]").forEach((el) => {
    el.textContent = n ? String(n) : "";
    el.hidden = !n;
  });
}
