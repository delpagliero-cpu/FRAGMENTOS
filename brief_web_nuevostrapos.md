# Brief de construcción — tienda online nuevos trapos

Este documento es la especificación completa del sitio. Todo el copy que aparece acá es final y va tal cual, sin reescribir. Lo único pendiente son las imágenes y las medidas de producto, marcados como PENDIENTE.

---

## 1. Objetivo

Tienda online para una marca de diseño de autor argentina. Veinte prendas, venta bajo modalidad pre-order, pago integrado con Mercado Pago.

La página tiene que ser simple y clara. El objetivo es que alguien entre, entienda qué es la marca en diez segundos, encuentre la prenda y compre sin fricción. No es un sitio experimental ni una pieza de portfolio.

## 2. Stack

- Repositorio existente en GitHub, deploy en Vercel, dominio propio ya configurado.
- HTML, CSS y JavaScript. Sin framework pesado.
- Una función serverless en Vercel para generar la preferencia de pago de Mercado Pago.
- Los datos de producto viven en un único archivo `productos.json`. Las páginas de producto se generan a partir de ese archivo, no se escriben a mano una por una.

**Importante sobre credenciales:** el access token de Mercado Pago va en variables de entorno de Vercel. Nunca en el repositorio, nunca en código del lado del cliente.

## 3. Sistema visual

- Fondo: off-white `#FFFBF8`. Es el fondo de todo el sitio, no blanco puro.
- Texto y trazos: negro.
- Acentos, solo donde haga falta señalar algo: rojo sangre y celeste opaco. Uso mínimo.
- Tipografía: Nitti Typewriter Open. Si no está disponible la licencia web, usar una monoespaciada de reemplazo y dejarlo anotado. Todo en minúscula, incluidos títulos y navegación.
- Wordmark: `nuevos trapos` en minúscula, con un círculo lleno reemplazando la "o" de "nuevos".
- Sin sombras, sin bordes redondeados, sin degradados, sin animaciones de entrada.
- Mucho aire. El espacio en blanco es parte de la identidad, no un sobrante.
- Los botones son rectángulos de borde fino, negro sobre off-white. Al pasar el mouse se invierten.

La regla general: el diseño se calla y las prendas hablan. Las fotos son lo único saturado de la página.

## 4. Estructura

Cuatro páginas más el panel de carrito y tres pantallas de retorno de pago.

1. Home
2. Tienda
3. Sobre la marca
4. Ficha de producto (generada desde `productos.json`)
5. Carrito (panel lateral, no página)
6. Pago aprobado / pendiente / rechazado

Navegación fija arriba: wordmark al centro, links a la izquierda (tienda, sobre la marca), carrito a la derecha.

---

## 5. Home

### Bloque 1 — barra de aviso

Una sola línea, arriba de todo, fondo negro y texto off-white. Rota entre dos mensajes cada seis segundos:

> envíos a todo el país
> 3 cuotas sin interés

No mencionar plazos de producción acá. La disponibilidad se comunica en cada producto, no antes.

### Bloque 2 — hero

Imagen a ancho completo. PENDIENTE: foto editorial vertical.

Encima, el wordmark grande y debajo una línea:

> ropa que se lee.

Botón: `ver la colección`

### Bloque 3 — texto de entrada

Centrado, ancho de lectura acotado, mucho aire arriba y abajo:

> Veinte prendas construidas a partir de una investigación sobre la contracultura argentina de los años setenta y ochenta, traducida a materiales, siluetas y superficies.

### Bloque 4 — tira de prendas

Fila horizontal de prendas recortadas sobre el fondo off-white, con aire generoso arriba y abajo. Scroll horizontal en pantallas chicas.
PENDIENTE: recortes en PNG con fondo transparente.

### Bloque 5 — acceso por tipología

Grilla simple, sin imágenes, solo texto sobre off-white con un borde fino. Cada uno lleva a su sección en la tienda:

sacos y abrigos · vestidos · pantalones y faldas · remeras · shorts · sweaters

### Bloque 6 — cómo se hace

Tres columnas, texto solo:

**fuente**
Cada prenda parte de una obra concreta de la contracultura argentina. Una misa, una canción, una revista, una performance.

**operación**
De esa obra no se copia la imagen: se traduce lo que hace. La saturación, la repetición, la transparencia, el volumen.

**prenda**
Eso se convierte en decisiones materiales. Qué tela, qué peso, qué caída, qué se muestra y qué se tapa.

### Bloque 7 — selección

Cuatro prendas destacadas con foto, nombre, precio y estado. PENDIENTE: definir cuáles cuatro.

### Bloque 8 — tu prenda, una sola para vos

Recién acá se comunica el pre-order, después de que la persona ya vio las prendas.

> Algunas piezas están hechas y salen en 48 horas. El resto se produce cuando lo pedís: tu prenda se hace una sola vez, para vos, y llega en una o dos semanas.

Debajo, en texto más chico:

> También tomo pedidos especiales. Fiestas, novias, piezas únicas.

Botón: `escribime`

### Bloque 9 — pie

Campo de newsletter con la línea: `dejá tu mail y te aviso cuándo sale lo próximo`
Links: instagram, preguntas frecuentes, términos y condiciones, contacto.
Abajo de todo, el wordmark en tamaño grande ocupando el ancho.

---

## 6. Tienda

Una sola página con secciones ancladas por tipología. Filtro fijo arriba que hace scroll suave hasta cada sección.

Orden de las secciones: sacos y abrigos, vestidos, pantalones y faldas, remeras, shorts, sweaters.

Cada producto en la grilla muestra: foto, nombre en minúscula, precio y disponibilidad. Nada más.
Las que están hechas llevan una marca discreta `48 h` sobre la foto.

Grilla de tres columnas en escritorio, dos en tablet, una en teléfono.

---

## 7. Ficha de producto

Dos columnas arriba. Izquierda la galería, derecha la información de compra fija mientras se hace scroll.

Galería: tres imágenes por prenda. PENDIENTE.

Columna derecha, en este orden exacto:

1. Nombre
2. Precio y cuotas
3. Disponibilidad: `entrega en 48 h` o `hecho para vos · 1 a 2 semanas`
4. Selector de talle, con link a la tabla de medidas
5. Selector de manga (solo en las remeras de lycra, cambia el precio)
6. Botón `comprar`
7. Debajo del botón, en texto chico: envíos y alias para transferencia

La disponibilidad va **antes** del botón, no después.

Debajo, cuatro bloques. Los tres últimos son desplegables y arrancan cerrados:

- Descripción, siempre visible
- Cómo está hecha: material, proceso e intervención manual. Solo lo que le sirve a quien compra.
- Medidas: tabla por talle. PENDIENTE.
- Origen: de qué obra sale la prenda. Dos oraciones, no más.

En la ficha no van códigos internos, porcentajes de mezcla ni datos de moldería. Sí va todo lo que es trabajo a mano, porque es lo que justifica el precio.

Cierra con una imagen editorial a ancho completo.

---

## 8. Sobre la marca

Texto corrido, ancho de lectura acotado, con imágenes intercaladas. Poco texto y mucho aire. PENDIENTE: imágenes.

### Primer bloque

> Esto empezó hace dos años.
>
> El diseño de autor no se sostiene solo con arte, requiere procesos productivos y planificación. Y la moda, cuando es lenguaje y no decoración, puede acompañar a quienes no se resignan a que dé todo igual.

### Segundo bloque

> Fragmentos parte de una investigación sobre la contracultura argentina de los setenta y ochenta. La colección no copia esas imágenes: traduce lo que hacían. La transparencia que muestra a medias. La repetición que insiste. El volumen que agranda el cuerpo en vez de contenerlo.

---

## 9. Preguntas frecuentes

**¿Cuánto tarda mi pedido?**
Entre una y dos semanas desde que se confirma el pago. Las remeras y los shorts salen más rápido. Los tejidos a mano y el denim llevan el plazo completo.

**¿Cómo son los talles?**
Trabajo con S, M y L en una línea amplia, pensada para que la prenda no dependa de un calce ajustado. En cada ficha están las medidas exactas. Si dudás entre dos talles, escribime.

**¿Puedo cambiar la prenda?**
Como cada pieza se produce a pedido, no hago cambios por arrepentimiento. Sí resuelvo cualquier problema de confección o falla del producto. Escribime y lo vemos.

**¿Hacen envíos?**
PENDIENTE: definir zonas, costos y plazos de envío.

**¿Puedo retirar en persona?**
PENDIENTE: confirmar si hay retiro en Córdoba.

**¿Cómo cuido las prendas?**
Cada prenda viene con sus instrucciones y están también en la ficha. En general: agua fría, lavado a mano en las piezas tejidas y estampadas, nada de secarropas. Las estampas nunca se planchan de frente.

**¿Por qué se hace a pedido?**
Para no acumular stock ni desperdiciar tela, y para poder revisar cada prenda una por una antes de que salga.

---

## 10. Pago

Integración con Mercado Pago Checkout Pro.

- Métodos: tarjeta de crédito, débito, dinero en cuenta de Mercado Pago, efectivo.
- Plazo de acreditación configurado a 14 días.
- Transferencia bancaria como segunda opción, visible en el checkout con el alias. PENDIENTE: alias.
- Cuotas: PENDIENTE: definir en cuántas y si con o sin interés.
- Seña: PENDIENTE: confirmar si se cobra el total o un porcentaje al momento del pedido.

Tres pantallas de retorno, simples, centradas, con wordmark, estado del pedido y número de orden:

- **Aprobado:** `listo. tu pedido entró.` Más el número de orden y el plazo estimado.
- **Pendiente:** `tu pago está en proceso.` Aviso de que se confirma por mail cuando se acredite.
- **Rechazado:** `el pago no se pudo procesar.` Botón para reintentar y el alias como alternativa.

---

## 11. Productos

Veinte prendas. Estructura de cada entrada en `productos.json`: codigo, nombre, tipologia, materialidad, tecnica, talles, estado, plazo, precio, variantes, descripcion, ficha_tecnica, origen, imagenes.

Todas: talles S, M y L. Estado `disponible`, plazo `1 a 2 semanas`.
Falta en todas: composición exacta, datos de construcción, tabla de medidas y disponibilidad real. PENDIENTE.

### Sacos y abrigos

**FRAG-SA-01 · ricota** · saco · denim · $200.000
Descripción: Saco largo de denim, de calce amplio y hombro caído, pensado para usarse abierto y sobre otras capas. El denim arranca rígido y va cediendo con el uso, así que la prenda se acomoda al cuerpo de quien la lleva. Funciona sobre una remera o cerrado, casi como un vestido.
Ficha: Denim 100% algodón. Lavar del revés en agua fría. Secar a la sombra. Planchar del revés.
Origen: La Misa Ricotera. La masa que ocupa el espacio se traduce en una silueta que agranda la presencia del cuerpo en vez de contenerla.

**FRAG-SA-02 · la multitud** · parka · denim · $150.000
Descripción: Parka de denim con volumen expandido en el cuerpo y en las mangas. La silueta no sigue el entalle: agranda. Admite capas debajo sin ajustar y es la pieza más abrigada de la colección.
Ficha: Denim 100% algodón. Lavar del revés en agua fría. Secar a la sombra. Planchar del revés.
Origen: La Misa Ricotera. El volumen como presencia compartida, el cuerpo que ocupa más lugar del que le corresponde.

**FRAG-SA-03 · tejido social** · saco largo · lana · tejido artesanal · $75.000
Descripción: Saco largo tejido a mano en lana roja, de punto irregular y superficie viva. Cada pieza se teje entera a mano, así que ninguna sale igual a la otra. Pesa y abriga.
Ficha: Lana. Tejido a mano. Lavar a mano en agua fría con jabón neutro. No retorcer. Secar en plano sobre una toalla.
Origen: La Misa Ricotera. Tejer como acción de unir lo fragmentado: la reconstrucción del tejido social hecha materia, con el rojo como marca de la herida.
NOTA: revisar este precio, está por debajo del sweater con la misma técnica.

### Pantalones y faldas

**FRAG-PA-01 · dinosaurio** · pantalón · denim · $80.000
Descripción: PENDIENTE completar qué lo distingue del otro modelo. Se sostiene por la estructura de la tela, sin necesidad de calce ajustado.
Ficha: Denim 100% algodón. Lavar del revés en agua fría. Secar a la sombra.
Origen: Los Dinosaurios. La tensión entre peso y fragilidad: el denim aporta estructura, y el calce amplio esquiva el entalle disciplinado.

**FRAG-PA-02 · los que están** · pantalón · denim · $80.000
Descripción: PENDIENTE completar qué lo distingue del otro modelo. La caída de la tela arma la silueta desde el peso y no desde el ajuste.
Ficha: Denim 100% algodón. Lavar del revés en agua fría. Secar a la sombra.
Origen: Los Dinosaurios. El juego de pesos: lo que permanece frente a lo que desaparece.

**FRAG-FA-01 · plaza** · falda · denim · $95.000
Descripción: Falda de denim. Se lleva con las piezas adherentes de la colección o sola, con el saco encima.
Ficha: Denim 100% algodón. Lavar del revés en agua fría. Secar a la sombra.
Origen: Las imágenes del Juicio a las Juntas en la calle. El espacio público como lugar donde la imagen circula y se vuelve visible.

### Vestidos

**FRAG-VE-01 · misa** · vestido · lana · tejido artesanal · $350.000
Descripción: Vestido largo tejido a mano en lana roja, de punto abierto. La textura irregular deja pasar la luz y cambia según cómo cae sobre el cuerpo. Se usa solo o sobre una segunda piel.
Ficha: Lana. Tejido a mano. Lavar a mano en agua fría con jabón neutro. No retorcer. Secar en plano.
Origen: La Misa Ricotera. El tejido como reunión: el punto abierto muestra lo que se unió y lo que quedó sin cerrar.

**FRAG-VE-02 · alicia** · vestido · microtul · $75.000
Descripción: Vestido de microtul translúcido, que deja ver de manera parcial lo que hay debajo. La transparencia no expone del todo: muestra y reserva al mismo tiempo. Va sobre otra prenda o sobre el cuerpo, según cuánto quieras mostrar.
Ficha: Microtul. Lavar a mano en agua fría. No retorcer. No planchar en contacto directo.
Origen: Alicia en el país de las maravillas. La doble lectura: decir algo bajo la apariencia de otra cosa.

**FRAG-VE-03 · rapport** · vestido · lycra de seda · sublimación · $90.000
Descripción: Vestido largo de lycra de seda, manga larga con recortes, estampado con el logo de la marca en rapport sobre toda la superficie. La repetición cubre la prenda entera, sin centro ni jerarquía, y los recortes abren zonas del cuerpo que la estampa no llega a tapar. Se adhiere al cuerpo y acompaña el movimiento.
Ficha: Lycra de seda. Estampado por sublimación digital. Manga larga con recortes. Lavar del revés a mano en agua fría. No usar secarropas. Planchar del revés en temperatura baja.
Origen: La repetición como memoria persistente. Lo que insiste no desaparece: vuelve, ocupa superficie y no se deja borrar.

### Sweaters

**FRAG-SW-01 · a mano** · sweater · lana · tejido artesanal · $150.000
Descripción: Sweater tejido a mano. El punto es denso y la superficie irregular, con las marcas propias del trabajo manual a la vista. Abriga de verdad y sirve como capa media o como pieza principal.
Ficha: Lana. Tejido a mano. Lavar a mano en agua fría con jabón neutro. Secar en plano.
Origen: La Misa Ricotera. El hacer manual como construcción de comunidad: las irregularidades no se corrigen, quedan.

### Remeras

**FRAG-RE-01 · quién es la ley** · remera · jersey de algodón · DTF · $30.000
Descripción: Remera de jersey de algodón con estampa frontal en DTF. Calce recto, para usar sola o debajo de las piezas de abrigo.
Ficha: Jersey 100% algodón. Estampado DTF. Lavar del revés en agua fría. No planchar sobre la estampa. No usar secarropas.
Origen: El Juicio a las Juntas. La pregunta por la ley se vuelve inscripción sobre el cuerpo: lo que se dijo en la calle vuelve a circular.

**FRAG-RE-02 · cerdos** · remera · jersey de algodón · DTF · $30.000
Descripción: Remera de jersey de algodón con la tapa de Cerdos & Peces estampada en DTF. La imagen se traslada tal como circulaba: recorte, tipografía y contraste duro. Calce recto, para usar sola o como capa base.
Ficha: Jersey 100% algodón. Estampado DTF. Lavar del revés en agua fría. No planchar sobre la estampa. No usar secarropas.
Origen: Cerdos & Peces. La gráfica de circulación marginal: el impreso que pasaba de mano en mano ahora se lleva puesto.

**FRAG-RE-03 · trapos** · remera · jersey de algodón · DTF · $30.000
Descripción: Remera de jersey de algodón con el logo de nuevos trapos estampado en DTF. Es la pieza más directa de la colección y la puerta de entrada a la marca. Calce recto, para todos los días.
Ficha: Jersey 100% algodón. Estampado DTF. Lavar del revés en agua fría. No planchar sobre la estampa. No usar secarropas.
Origen: La marca como archivo. El wordmark funciona como el contenedor que ordena la saturación del resto de la colección.

**FRAG-RE-06 · país de las maravillas** · remera · microtul · sublimación · $55.000
Descripción: Remera de microtul, liviana y translúcida, con estampa sublimada. Deja ver parcialmente lo que lleva debajo, así que funciona como capa sobre otra prenda o directamente sobre el cuerpo.
Ficha: Microtul. Estampado por sublimación digital. Lavar a mano en agua fría. No retorcer. No planchar en contacto directo.
Origen: Alicia en el país de las maravillas. El camuflaje: mostrar sin mostrar del todo, exposición controlada.

Las cuatro que siguen tienen variante de manga: corta $35.000, larga $45.000. Es un selector dentro de la misma ficha, no productos separados.

**FRAG-RE-07 · charly** · remera · lycra de seda · sublimación
Descripción: Remera de lycra de seda con el rostro de Charly sublimado. La imagen queda dentro de la fibra, no encima, así que aguanta el uso sin descascararse. El calce es adherente en las dos versiones.
Ficha: Lycra de seda. Estampado por sublimación digital. Lavar del revés a mano en agua fría. No usar secarropas. Planchar del revés en temperatura baja.
Origen: Los Dinosaurios. La canción que decía bajo censura lo que no se podía decir de frente, ahora puesta sobre el cuerpo.

**FRAG-RE-08 · batato** · remera · lycra de seda · sublimación
Descripción: Remera de lycra de seda con la figura de Batato sublimada. La estampa se integra a la fibra y acompaña el movimiento del cuerpo.
Ficha: Lycra de seda. Estampado por sublimación digital. Lavar del revés a mano en agua fría. No usar secarropas. Planchar del revés en temperatura baja.
Origen: Batato Barea. La teatralidad y el desborde: el cuerpo disidente que se construye a sí mismo como escena.

**FRAG-RE-09 · bandera** · remera · lycra de seda · sublimación
Descripción: Remera de lycra de seda con estampa pictórica en celeste y rojo. La mancha se extiende por toda la superficie sin repetirse, así que el recorte cae distinto en cada talle.
Ficha: Lycra de seda. Estampado por sublimación digital. Lavar del revés a mano en agua fría. No usar secarropas. Planchar del revés en temperatura baja.
Origen: Paleta de la colección. El celeste opaco como identidad nacional puesta en crisis y el rojo como herida histórica, juntos y sin resolver.

**FRAG-RE-10 · rapport** · remera · lycra de seda · sublimación
Descripción: Remera de lycra de seda con el logo de nuevos trapos repetido en rapport sobre toda la superficie. La repetición cubre la prenda entera, sin centro ni jerarquía.
Ficha: Lycra de seda. Estampado por sublimación digital. Lavar del revés a mano en agua fría. No usar secarropas. Planchar del revés en temperatura baja.
Origen: La repetición como memoria persistente. Lo que insiste no desaparece: vuelve, ocupa superficie y no se deja borrar.

### Shorts

**FRAG-SH-01 · 2001** · short · lycra de seda · sublimación · $75.000
Descripción: Short de lycra de seda con la estampa de Argentina en llamas, de calce adherente. La imagen queda dentro de la fibra y cubre la pieza entera. Acompaña el cuerpo sin restringirlo y funciona como base debajo de las prendas translúcidas o solo.
Ficha: Lycra de seda. Estampado por sublimación digital. Lavar del revés a mano en agua fría. No usar secarropas.
Origen: La crisis de 2001. El registro de la calle en llamas como imagen que vuelve.

**FRAG-SH-02 · bandera** · short · lycra de seda · sublimación · $75.000
Descripción: Short de lycra de seda con estampa pictórica en celeste y rojo, la misma de la remera bandera. La mancha se extiende sin repetirse, así que el recorte cae distinto en cada talle. Calce adherente.
Ficha: Lycra de seda. Estampado por sublimación digital. Lavar del revés a mano en agua fría. No usar secarropas.
Origen: Paleta de la colección. El celeste opaco como identidad nacional puesta en crisis y el rojo como herida histórica, juntos y sin resolver.

---

## 12. Cómo manejar lo que falta

Todo lo marcado PENDIENTE tiene que quedar como espacio reservado, no eliminado ni rellenado con contenido inventado.

- Imágenes: usar un rectángulo en un gris apenas más oscuro que el fondo, con el nombre del archivo que va a ir ahí. Sin íconos ni texto tipo "placeholder".
- Medidas: dejar la tabla armada con las filas correspondientes y las celdas vacías.
- Datos de composición y construcción: dejar la línea en la ficha técnica lista para completar.

Que las imágenes y las medidas se puedan cargar después editando solamente `productos.json`, sin tocar el HTML.

---

## 13. Lo que no hay que hacer

- No inventar textos, precios, medidas ni datos de producto que no estén en este documento.
- No agregar secciones que no estén acá.
- No usar animaciones, transiciones llamativas ni efectos de scroll.
- No usar mayúsculas en títulos ni en la navegación.
- No poner el token de Mercado Pago en el repositorio.
- No crear una sección de conjuntos ni de combos.
