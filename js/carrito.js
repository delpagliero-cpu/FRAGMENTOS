/* nuevos trapos — carrito
   ---------------------------------------------------------------------------
   Panel lateral, no página. El estado vive en localStorage y guarda sólo
   códigos, talles y cantidades: nunca precios. El precio para mostrar se lee
   de productos.json, y el precio que se cobra lo recalcula la función
   serverless leyendo el mismo archivo del lado del servidor. Si alguien edita
   el localStorage, no cambia lo que paga.
   --------------------------------------------------------------------------- */

import { datos, precio, precioDesde, escapar, foto } from "/js/sitio.js";

const CLAVE = "nt.carrito";
const WA = "https://wa.me/5493534136713";
/* Los datos de envío se recuerdan para no tener que reescribirlos, pero se
   borran al confirmar la compra: no hay motivo para dejar un DNI guardado. */
const DATOS = "nt.envio";
const MAX_POR_ITEM = 10;

/* estado ----------------------------------------------------------------- */

export function leer() {
  try {
    const v = JSON.parse(localStorage.getItem(CLAVE));
    return Array.isArray(v) ? v.filter(valido) : [];
  } catch {
    return [];
  }
}

function valido(i) {
  return i && typeof i.codigo === "string" && typeof i.talle === "string" &&
    Number.isInteger(i.cantidad) && i.cantidad > 0 && i.cantidad <= MAX_POR_ITEM;
}

function guardar(items) {
  try {
    localStorage.setItem(CLAVE, JSON.stringify(items));
  } catch {
    /* modo privado o almacenamiento lleno: el carrito sigue en memoria */
  }
  document.dispatchEvent(new CustomEvent("carrito:cambio"));
}

const mismaLinea = (a, b) =>
  a.codigo === b.codigo && a.talle === b.talle &&
  (a.variante || "") === (b.variante || "");

export function agregar(item) {
  const items = leer();
  const ya = items.find((i) => mismaLinea(i, item));
  if (ya) ya.cantidad = Math.min(MAX_POR_ITEM, ya.cantidad + item.cantidad);
  else items.push({ ...item });
  guardar(items);
}

export function cambiarCantidad(indice, cantidad) {
  const items = leer();
  if (!items[indice]) return;
  if (cantidad <= 0) items.splice(indice, 1);
  else items[indice].cantidad = Math.min(MAX_POR_ITEM, cantidad);
  guardar(items);
}

export function vaciar() {
  guardar([]);
}

export function contar() {
  return leer().reduce((n, i) => n + i.cantidad, 0);
}

/* precios para mostrar --------------------------------------------------- */

function precioDe(prenda, item) {
  if (prenda.variantes && item.variante) {
    const o = prenda.variantes.opciones.find((x) => x.valor === item.variante);
    if (o) return o.precio;
  }
  return precioDesde(prenda);
}

export async function detalle() {
  const d = await datos();
  const porCodigo = Object.fromEntries(d.prendas.map((p) => [p.codigo, p]));
  const lineas = [];
  let total = 0;
  let faltaPrecio = false;

  leer().forEach((item, indice) => {
    const p = porCodigo[item.codigo];
    if (!p) return;
    const unitario = precioDe(p, item);
    if (unitario == null) faltaPrecio = true;
    else total += unitario * item.cantidad;
    lineas.push({ indice, item, prenda: p, unitario });
  });

  return { lineas, total, faltaPrecio };
}

/* panel ------------------------------------------------------------------ */

let panel, fondo, ultimoFoco;

function armarPanel() {
  if (panel) return;
  fondo = document.createElement("div");
  fondo.className = "velo";
  fondo.hidden = true;
  fondo.addEventListener("click", cerrar);

  panel = document.createElement("aside");
  panel.className = "carrito";
  panel.hidden = true;
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-modal", "true");
  panel.setAttribute("aria-label", "carrito");

  document.body.append(fondo, panel);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !panel.hidden) cerrar();
    if (e.key === "Tab" && !panel.hidden) atraparFoco(e);
  });
}

/* El panel es modal: el tabulador no puede salirse hacia la página de atrás. */
function atraparFoco(e) {
  const focos = panel.querySelectorAll(
    'a[href], button:not([disabled]), input, [tabindex]:not([tabindex="-1"])');
  if (!focos.length) return;
  const primero = focos[0];
  const ultimo = focos[focos.length - 1];
  if (e.shiftKey && document.activeElement === primero) {
    e.preventDefault(); ultimo.focus();
  } else if (!e.shiftKey && document.activeElement === ultimo) {
    e.preventDefault(); primero.focus();
  }
}

export async function abrir() {
  armarPanel();
  ultimoFoco = document.activeElement;
  await pintar();
  fondo.hidden = false;
  panel.hidden = false;
  document.body.style.overflow = "hidden";
  panel.querySelector("[data-cerrar]")?.focus();
}

export function cerrar() {
  if (!panel) return;
  panel.hidden = true;
  fondo.hidden = true;
  document.body.style.overflow = "";
  ultimoFoco?.focus();
}

async function pintar() {
  const { lineas, total, faltaPrecio } = await detalle();

  const cuerpo = lineas.length
    ? lineas.map((l) => {
        const v = l.item.variante ? " · " + escapar(l.item.variante) : "";
        return (
          '<li class="carrito__linea">' +
          '<div class="carrito__foto">' +
          foto(l.prenda, 0, "88px", "marco--retrato") + "</div>" +
          '<div class="carrito__datos">' +
          '<p class="carrito__nombre">' + escapar(l.prenda.nombre) + "</p>" +
          '<p class="rotulo">talle ' + escapar(l.item.talle) + v + "</p>" +
          '<p class="carrito__precio t-cifra">' +
          (l.unitario == null
            ? '<span class="pendiente">precio PENDIENTE</span>'
            : precio(l.unitario)) + "</p>" +
          '<div class="carrito__cantidad">' +
          '<button class="carrito__mas" type="button" data-menos="' + l.indice +
          '" aria-label="quitar uno">−</button>' +
          '<span aria-live="polite">' + l.item.cantidad + "</span>" +
          '<button class="carrito__mas" type="button" data-mas="' + l.indice +
          '" aria-label="agregar uno">+</button>' +
          '<button class="carrito__quitar" type="button" data-quitar="' +
          l.indice + '">quitar</button>' +
          "</div></div></li>"
        );
      }).join("")
    : '<li class="carrito__vacio"><p class="t-cuerpo">Todavía no agregaste ' +
      "nada.</p><p class=\"t-chico\" style=\"margin-top:8px\">" +
      'Mirá <a href="/">las prendas</a>.</p></li>';

  const puedePagar = lineas.length && !faltaPrecio;

  panel.innerHTML =
    '<div class="carrito__cab">' +
    '<p class="kicker">carrito</p>' +
    '<button class="carrito__cerrar" type="button" data-cerrar ' +
    'aria-label="cerrar el carrito">✕</button></div>' +

    '<ul class="carrito__lista">' + cuerpo + "</ul>" +

    (lineas.length ?
      '<div class="carrito__pie">' +
      '<p class="carrito__total"><span class="rotulo">total</span>' +
      '<span class="t-cifra">' + precio(total) + "</span></p>" +
      (faltaPrecio
        ? '<p class="pendiente" style="margin-bottom:8px">hay una prenda sin ' +
          "precio cargado, todavía no se puede pagar</p>" : "") +
      '<button class="boton boton--ancho boton--invertido" type="button" ' +
      'data-mp' + (puedePagar ? "" : " disabled") + ">Pagar con Mercado Pago</button>" +
      '<button class="boton boton--ancho" type="button" data-transferencia ' +
      'style="margin-top:8px">Pagar por transferencia</button>' +
      '<p class="carrito__estado t-nota" role="status" data-estado></p>' +
      '<div class="carrito__transferencia" data-bloque-transferencia hidden>' +
      '<p class="rotulo">transferencia bancaria</p>' +
      '<p class="t-chico" style="margin-top:8px">Monto: ' +
      '<span class="t-cifra">' + precio(total) + "</span></p>" +
      '<p class="t-chico" style="margin-top:8px">Alias: ' +
      '<strong>nuevostrapos.archivo</strong></p>' +
      '<p class="t-chico" style="margin-top:8px">Mandame el comprobante por ' +
      "WhatsApp y te confirmo el pedido.</p>" +
      '<p style="margin-top:8px"><a class="boton" href="/contacto.html">' +
      "Ir a contacto</a></p></div>" +
      '<p class="compra__letrachica" style="margin-top:16px">Pagás dentro de ' +
      "Mercado Pago. No guardo ningún dato de tu tarjeta.</p>" +
      "</div>" : "");

  panel.querySelector("[data-cerrar]").addEventListener("click", cerrar);
  panel.querySelectorAll("[data-mas]").forEach((b) =>
    b.addEventListener("click", () => {
      const i = +b.dataset.mas;
      cambiarCantidad(i, leer()[i].cantidad + 1);
    }));
  panel.querySelectorAll("[data-menos]").forEach((b) =>
    b.addEventListener("click", () => {
      const i = +b.dataset.menos;
      cambiarCantidad(i, leer()[i].cantidad - 1);
    }));
  panel.querySelectorAll("[data-quitar]").forEach((b) =>
    b.addEventListener("click", () => cambiarCantidad(+b.dataset.quitar, 0)));

  panel.querySelector("[data-transferencia]")?.addEventListener("click", () => {
    const bloque = panel.querySelector("[data-bloque-transferencia]");
    bloque.hidden = !bloque.hidden;
  });

  panel.querySelector("[data-mp]")?.addEventListener("click", pedirDatos);
}

/* checkout --------------------------------------------------------------- */

/* datos de envío --------------------------------------------------------- */

const CAMPOS = [
  ["nombre", "nombre y apellido", "text", "name", true],
  ["celular", "celular", "tel", "tel", true],
  ["dni", "dni", "text", "off", true],
  ["direccion", "dirección y número", "text", "street-address", true],
  ["localidad", "localidad", "text", "address-level2", true],
  ["cp", "código postal", "text", "postal-code", true],
];

function datosGuardados() {
  try { return JSON.parse(localStorage.getItem(DATOS)) || {}; } catch { return {}; }
}

async function pedirDatos() {
  const previos = datosGuardados();
  const { total } = await detalle();

  panel.innerHTML =
    '<div class="carrito__cab">' +
    '<p class="kicker">datos de envío</p>' +
    '<button class="carrito__cerrar" type="button" data-cerrar ' +
    'aria-label="cerrar el carrito">✕</button></div>' +
    '<form class="carrito__form" data-envio novalidate>' +
    CAMPOS.map(([n, etiq, tipo, auto]) =>
      '<p><label class="etiqueta" for="c-' + n + '">' + etiq + '</label>' +
      '<input class="campo" id="c-' + n + '" name="' + n + '" type="' + tipo +
      '" autocomplete="' + auto + '" required value="' +
      escapar(previos[n] || "") + '"></p>').join("") +

    '<fieldset style="border:0"><legend class="etiqueta">envío</legend>' +
    '<div class="opciones" style="flex-direction:column;align-items:stretch">' +
    '<label class="opcion"><input class="opcion__control" type="radio" ' +
    'name="envio" value="cordoba"' + (previos.envio !== "pais" ? " checked" : "") +
    '><span class="opcion__cara" style="justify-content:flex-start">' +
    'Córdoba capital · sin cargo</span></label>' +
    '<label class="opcion"><input class="opcion__control" type="radio" ' +
    'name="envio" value="pais"' + (previos.envio === "pais" ? " checked" : "") +
    '><span class="opcion__cara" style="justify-content:flex-start">' +
    'Resto del país · a coordinar</span></label>' +
    "</div></fieldset>" +

    '<p class="t-nota" data-nota-envio></p>' +
    '<p class="carrito__estado t-nota" role="alert" data-estado></p>' +
    '<p class="carrito__total"><span class="rotulo">total</span>' +
    '<span class="t-cifra">' + precio(total) + "</span></p>" +
    '<button class="boton boton--ancho boton--invertido" type="submit">' +
    "Ir a pagar</button>" +
    '<button class="boton boton--ancho" type="button" data-volver ' +
    'style="margin-top:8px">Volver al carrito</button>' +
    "</form>";

  panel.querySelector("[data-cerrar]").addEventListener("click", cerrar);
  panel.querySelector("[data-volver]").addEventListener("click", pintar);

  const nota = panel.querySelector("[data-nota-envio]");
  const verNota = () => {
    const pais = panel.querySelector('input[name="envio"]:checked').value === "pais";
    nota.textContent = pais
      ? "Te escribo para coordinar el costo del envío antes de despacharlo."
      : "En la ciudad de Córdoba el envío no tiene costo.";
  };
  panel.querySelectorAll('input[name="envio"]').forEach(
    (r) => r.addEventListener("change", verNota));
  verNota();

  panel.querySelector("[data-envio]").addEventListener("submit", (ev) => {
    ev.preventDefault();
    enviar(ev.currentTarget);
  });
}

async function enviar(form) {
  const estado = form.querySelector("[data-estado]");
  const boton = form.querySelector('button[type="submit"]');
  const datos = {};
  for (const [n] of CAMPOS) datos[n] = form.elements[n].value.trim();
  datos.envio = form.elements.envio.value;

  const falta = CAMPOS.find(([n]) => !datos[n]);
  if (falta) {
    estado.textContent = "Falta completar " + falta[1] + ".";
    form.elements[falta[0]].focus();
    return;
  }
  if (datos.celular.replace(/\D/g, "").length < 8) {
    estado.textContent = "Revisá el celular: faltan números.";
    form.elements.celular.focus();
    return;
  }

  try { localStorage.setItem(DATOS, JSON.stringify(datos)); } catch {}

  estado.textContent = "";
  boton.disabled = true;
  boton.textContent = "Preparando el pago…";

  try {
    const r = await fetch("/api/crear-preferencia", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: leer(), envio: datos })
    });
    const data = await r.json();
    if (!r.ok || !data.init_point) {
      throw new Error(data.error || "no se pudo crear el pago");
    }
    location.href = data.init_point;
  } catch (e) {
    boton.disabled = false;
    boton.textContent = "Ir a pagar";
    const salto = String.fromCharCode(10);
    const { lineas } = await detalle();
    const texto = lineas.map((l) =>
      l.prenda.nombre + " · talle " + l.item.talle +
      (l.item.variante ? " · " + l.item.variante : "") +
      " x" + l.item.cantidad).join(salto);
    const mensaje = encodeURIComponent(
      "Hola! Quiero encargar:" + salto + texto + salto + salto +
      datos.nombre + " · " + datos.celular);
    estado.innerHTML =
      "No se pudo abrir el pago. " +
      '<a href="' + WA + "?text=" + mensaje + '" target="_blank" ' +
      'rel="noopener">Escribime por WhatsApp</a> y lo cerramos por ahí.';
    console.error(e);
  }
}

/* arranque --------------------------------------------------------------- */

export function conectar() {
  document.querySelectorAll("[data-abrir-carrito]").forEach((a) =>
    a.addEventListener("click", (e) => { e.preventDefault(); abrir(); }));
  document.addEventListener("carrito:cambio", () => {
    if (panel && !panel.hidden) pintar();
  });
  /* Si se abre el sitio en dos pestañas, el contador se mantiene igual. */
  addEventListener("storage", (e) => {
    if (e.key === CLAVE) document.dispatchEvent(new CustomEvent("carrito:cambio"));
  });
}
