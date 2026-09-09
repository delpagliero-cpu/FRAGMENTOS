/* Notificaciones de pago de Mercado Pago.
 * ---------------------------------------------------------------------------
 * Hace falta porque los pagos en efectivo (Rapipago, Pago Fácil) se acreditan
 * uno o dos días después de generada la orden: la persona ya se fue del sitio
 * y nadie se entera de que pagó salvo por acá.
 *
 * Mercado Pago reintenta si no recibe un 200, así que este endpoint contesta
 * 200 apenas puede y hace el trabajo después.
 * --------------------------------------------------------------------------- */

const crypto = require("crypto");

/* Valida la firma del header x-signature contra MP_WEBHOOK_SECRET.
   El manifiesto es "id:<data.id>;request-id:<x-request-id>;ts:<ts>;" */
function firmaValida(req, secreto) {
  const firma = req.headers["x-signature"];
  const pedido = req.headers["x-request-id"];
  if (!firma || typeof firma !== "string") return false;

  const partes = Object.fromEntries(
    firma.split(",").map((p) => p.split("=").map((s) => s.trim()))
  );
  const ts = partes.ts;
  const v1 = partes.v1;
  if (!ts || !v1) return false;

  const id = (req.query && (req.query["data.id"] || req.query.id)) || "";
  const manifiesto = `id:${String(id).toLowerCase()};request-id:${pedido};ts:${ts};`;
  const esperado = crypto.createHmac("sha256", secreto)
    .update(manifiesto).digest("hex");

  const a = Buffer.from(esperado, "utf8");
  const b = Buffer.from(v1, "utf8");
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

async function traerPago(id, token) {
  const r = await fetch(`https://api.mercadopago.com/v1/payments/${id}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!r.ok) throw new Error("no se pudo leer el pago " + id + ": " + r.status);
  return r.json();
}

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).end();
  }

  const token = process.env.MP_ACCESS_TOKEN;
  const secreto = process.env.MP_WEBHOOK_SECRET;

  /* Sin secreto configurado no se valida nada: se registra y se corta, para
     no procesar avisos de cualquiera que descubra la URL. */
  if (!secreto) {
    console.error("falta MP_WEBHOOK_SECRET: no puedo validar la notificación");
    return res.status(200).end();
  }
  if (!firmaValida(req, secreto)) {
    console.warn("notificación con firma inválida, la descarto");
    return res.status(401).end();
  }

  /* Se contesta enseguida: si Mercado Pago no recibe el 200, reintenta. */
  res.status(200).end();

  try {
    let cuerpo = req.body;
    if (typeof cuerpo === "string") cuerpo = JSON.parse(cuerpo);
    const tipo = (cuerpo && cuerpo.type) || (req.query && req.query.type);
    if (tipo !== "payment") return;

    const id = (cuerpo && cuerpo.data && cuerpo.data.id) ||
               (req.query && req.query["data.id"]);
    if (!id || !token) return;

    const pago = await traerPago(id, token);

    /* Acá va lo que haya que hacer cuando un pago cambia de estado: avisar por
       mail, marcar la orden, descontar stock. Por ahora queda registrado en los
       logs de Vercel, que es donde Delfi puede verlo.
       PENDIENTE: definir a dónde se notifica una venta acreditada. */
    console.log("pago actualizado", {
      orden: pago.external_reference,
      estado: pago.status,
      detalle: pago.status_detail,
      medio: pago.payment_type_id,
      monto: pago.transaction_amount,
      mail: pago.payer && pago.payer.email
    });
  } catch (e) {
    console.error("error procesando la notificación", e);
  }
};
