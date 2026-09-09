/* Crea la preferencia de pago de Mercado Pago (Checkout Pro).
 * ---------------------------------------------------------------------------
 * Lo importante de este archivo: el navegador manda SÓLO códigos, talles y
 * cantidades. Los precios se vuelven a leer acá de datos/productos.json. Si
 * alguien edita el carrito en su navegador para pagar $1, el precio que se
 * cobra sigue siendo el del archivo.
 *
 * El access token va en variables de entorno de Vercel. Nunca en el repo.
 * --------------------------------------------------------------------------- */

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const MAX_LINEAS = 30;
const MAX_POR_ITEM = 10;

function leerCatalogo() {
  const p = path.join(process.cwd(), "datos", "productos.json");
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

/* Número de orden legible: NT-<fecha>-<azar>. Va como external_reference y es
   lo que se le muestra a la persona en la pantalla de retorno. */
function numeroDeOrden() {
  const d = new Date();
  const fecha = d.toISOString().slice(2, 10).replace(/-/g, "");
  const azar = crypto.randomBytes(2).toString("hex").toUpperCase();
  return `NT-${fecha}-${azar}`;
}

function precioDeLinea(prenda, variante) {
  if (prenda.variantes && prenda.variantes.opciones.length) {
    const o = prenda.variantes.opciones.find((x) => x.valor === variante);
    if (!o) return null;
    return o.precio;
  }
  return prenda.precio;
}

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "usá POST" });
  }

  const token = process.env.MP_ACCESS_TOKEN;
  const sitio = process.env.URL_SITIO;
  if (!token || !sitio) {
    console.error("faltan MP_ACCESS_TOKEN o URL_SITIO");
    return res.status(500).json({ error: "el pago no está configurado" });
  }

  let entrada = req.body;
  if (typeof entrada === "string") {
    try { entrada = JSON.parse(entrada); } catch { entrada = null; }
  }
  const pedidos = entrada && Array.isArray(entrada.items) ? entrada.items : null;
  if (!pedidos || !pedidos.length || pedidos.length > MAX_LINEAS) {
    return res.status(400).json({ error: "carrito vacío o inválido" });
  }

  let catalogo;
  try {
    catalogo = leerCatalogo();
  } catch (e) {
    console.error("no se pudo leer productos.json", e);
    return res.status(500).json({ error: "no se pudo leer el catálogo" });
  }
  const porCodigo = Object.fromEntries(catalogo.prendas.map((p) => [p.codigo, p]));

  const items = [];
  for (const linea of pedidos) {
    const prenda = porCodigo[linea && linea.codigo];
    if (!prenda) {
      return res.status(400).json({ error: "hay una prenda que no existe" });
    }

    const cantidad = Number(linea.cantidad);
    if (!Number.isInteger(cantidad) || cantidad < 1 || cantidad > MAX_POR_ITEM) {
      return res.status(400).json({ error: "cantidad inválida" });
    }

    const talle = String(linea.talle || "");
    if (!prenda.talles.includes(talle)) {
      return res.status(400).json({ error: "talle inválido" });
    }
    if (prenda.stock && prenda.stock[talle] === "agotado") {
      return res.status(409).json({
        error: `${prenda.nombre} en talle ${talle} está agotado`
      });
    }

    const variante = linea.variante ? String(linea.variante) : null;
    if (prenda.variantes && !variante) {
      return res.status(400).json({ error: "falta elegir " + prenda.variantes.etiqueta });
    }

    const unitario = precioDeLinea(prenda, variante);
    if (unitario == null) {
      return res.status(409).json({
        error: `${prenda.nombre} todavía no tiene precio cargado`
      });
    }

    items.push({
      id: prenda.codigo,
      title: `${prenda.nombre} · talle ${talle}` + (variante ? ` · ${variante}` : ""),
      quantity: cantidad,
      unit_price: unitario,
      currency_id: catalogo.moneda || "ARS",
      category_id: "fashion"
    });
  }

  /* Datos de envío. No hay base de datos: viajan dentro de la preferencia,
     así que Delfi los ve en el detalle de la orden en su panel de Mercado
     Pago, incluso si el pago fue en efectivo y se acreditó dos días después. */
  const env = (entrada && entrada.envio) || {};
  const texto = (v, max) => String(v == null ? "" : v).trim().slice(0, max || 120);
  const envio = {
    nombre: texto(env.nombre),
    celular: texto(env.celular, 40),
    dni: texto(env.dni, 20),
    direccion: texto(env.direccion, 160),
    localidad: texto(env.localidad),
    cp: texto(env.cp, 20),
    zona: env.envio === "pais" ? "resto del país" : "Córdoba capital",
  };
  if (!envio.nombre || !envio.celular || !envio.direccion) {
    return res.status(400).json({ error: "faltan los datos de envío" });
  }

  const orden = numeroDeOrden();
  const base = sitio.replace(/\/+$/, "");

  const partes = envio.nombre.split(" ");
  const preferencia = {
    items,
    payer: {
      name: partes[0],
      surname: partes.slice(1).join(" ") || partes[0],
      phone: { number: envio.celular },
      identification: { type: "DNI", number: envio.dni },
      address: {
        street_name: envio.direccion,
        zip_code: envio.cp,
      },
    },
    external_reference: orden,
    statement_descriptor: "NUEVOSTRAPOS",
    /* Mercado Pago rechaza localhost acá: tiene que ser el dominio real. */
    back_urls: {
      success: `${base}/pago/aprobado.html`,
      pending: `${base}/pago/pendiente.html`,
      failure: `${base}/pago/rechazado.html`
    },
    auto_return: "approved",
    notification_url: `${base}/api/webhook`,
    /* binary_mode false deja pasar los pagos en efectivo, que entran como
       pendientes hasta que la persona paga en Rapipago o Pago Fácil. */
    binary_mode: false,
    metadata: {
      orden,
      envio_nombre: envio.nombre,
      envio_celular: envio.celular,
      envio_dni: envio.dni,
      envio_direccion: envio.direccion,
      envio_localidad: envio.localidad,
      envio_cp: envio.cp,
      envio_zona: envio.zona,
    }
  };

  try {
    const r = await fetch("https://api.mercadopago.com/checkout/preferences", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        /* Evita crear dos preferencias si el navegador reintenta. */
        "X-Idempotency-Key": orden
      },
      body: JSON.stringify(preferencia)
    });

    const data = await r.json();
    if (!r.ok) {
      console.error("mercado pago rechazó la preferencia", r.status, data);
      return res.status(502).json({ error: "Mercado Pago rechazó el pago" });
    }

    const enPruebas = token.startsWith("TEST-");
    const destino = enPruebas ? (data.sandbox_init_point || data.init_point)
                              : data.init_point;

    console.log("preferencia creada",
                { orden, id: data.id, enPruebas, zona: envio.zona });
    return res.status(200).json({ init_point: destino, orden });
  } catch (e) {
    console.error("error creando la preferencia", e);
    return res.status(502).json({ error: "no se pudo contactar a Mercado Pago" });
  }
};
