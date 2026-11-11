# AUDITTIA · sitio institucional

Sitio estático en español: siete páginas informativas y una página 404. Sin framework, instalación ni servidor de aplicación. JavaScript local sólo mejora el menú y añade animaciones opcionales; el contenido, la navegación y las preguntas funcionan sin él.

## Ver el sitio

Desde la carpeta del proyecto:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Abre http://127.0.0.1:8000/ (sin punto después de index.html). Si aparece un listado de carpetas, el servidor se inició fuera del proyecto. Si el puerto está ocupado, usa otro, como 8765. No inicies el servidor desde tu carpeta personal.

## Organización

- index.html: resumen, accesos por necesidad, método, revisión humana, entidades y contacto.
- plataforma.html: proceso y verificaciones; la interfaz ilustrada no es una aplicación real.
- para-entidades.html: EPS, firmas auditoras e IPS.
- seguridad.html: controles incorporados al motor, alcance de la retención cero, diferenciales y condiciones de puesta en marcha. Evidencia y límites en SEGURIDAD-CONTENIDO.md.
- nosotros.html: propósito, disciplinas del equipo y principios.
- recursos.html: glosario y preguntas frecuentes.
- privacidad.html: información del sitio, distinta de los acuerdos de tratamiento de la plataforma.
- styles.css: tokens, base, navegación, portada y componentes compartidos.
- interiores.css: composiciones y componentes de las páginas de detalle.
- site.js: mejora progresiva; sin cookies, almacenamiento local, telemetría ni dependencias.
- assets/: marca, imágenes optimizadas, tipografía local y licencias.

El correo confirmado es **notificaciones@audittia.com**. El botón **Prueba gratis** del encabezado (y los CTA principales) lleva a `factura-gratis.html` (qué incluye, normas, requisitos); su botón abre un correo con asunto «Prueba gratis de AUDITTIA» y el texto «Estoy interesado en una prueba gratis de AUDITTIA.»; la factura se recibe solo con un acuerdo de tratamiento de datos firmado. El tutorial (cuentas inventadas, sin vencimiento) se pide con el asunto «Acceso al tutorial de AUDITTIA». No hay formulario. El enlace **Ingresar** a la plataforma está comentado en el encabezado de las ocho páginas (`https://piloto.audittia.com`): se activa quitando el comentario cuando exista el servidor y su registro DNS. Los enlaces abren la aplicación de correo del visitante; no envían nada automáticamente. No solicitar ni recibir historias clínicas por el canal inicial.

## Verificar cambios

```bash
python3 scripts/check_site.py
git diff --check
```

El validador usa sólo Python estándar: comprueba H1, idioma, metadatos, CSP, imagen social, enlaces/fragmentos locales, recursos CSS, IDs y contenido provisional. No confirma entrega del correo, disponibilidad de URLs externas ni cumplimiento legal.

Prueba opcional con Playwright instalado y un navegador disponible:

```bash
python3 scripts/check_browser.py --base-url http://127.0.0.1:8000
```

Si utilizas Chrome ya instalado, añade `--browser-path "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`. Para accesibilidad automática, pasa un axe-core local y revisado con `--axe-script /ruta/axe.min.js`. Ninguna de estas herramientas se incluye en el sitio publicado.

La prueba de navegador cubre ocho páginas a 360, 390, 820, 1024 y 1440 px; menú por teclado, FAQ, imágenes, errores de consola, movimiento reducido y funcionamiento sin JavaScript. La accesibilidad exige además revisión humana.

## Preparar sólo los archivos públicos

```bash
python3 scripts/build_site.py
python3 scripts/check_site.py --root .site
```

El script crea una carpeta **nueva** .site. No sobrescribe ni borra una salida anterior. En ejecuciones posteriores usa, por ejemplo, `--output .site-revision-2`. La carpeta contiene HTML, CSS, JS, assets, CNAME, .nojekyll, robots y sitemap; excluye scripts, documentos y configuración de desarrollo.

## Publicación actual y límites

Producción: https://audittia.com en **GitHub Pages**. El dominio se conserva en la configuración de Pages; CNAME se mantiene por compatibilidad, pero no configura el dominio con workflows personalizados. El flujo deploy.yml publica sólo el artefacto .site después de validarlo; se ejecuta al actualizar main o de forma manual. Requiere que el origen de Pages esté configurado como GitHub Actions. Generar .site localmente **no publica nada**.

El workflow validate.yml añade comprobaciones en pull requests. deploy.yml vuelve a validar el código y el artefacto antes de su trabajo de publicación: si falla la construcción, no despliega. Sólo el trabajo deploy recibe permisos pages:write e id-token:write; no recibe permisos para escribir en el repositorio. La protección de rama no se modificó y puede configurarse por separado.

No subir información confidencial: aunque el artefacto no incluye documentación ni herramientas de desarrollo, el repositorio sigue siendo público. Los informes de esta revisión no contienen secretos.

La CSP y la política de referrer están en cada HTML. GitHub Pages no permite configurar aquí todos los encabezados HTTP: HSTS, nosniff, Permissions-Policy y protección anti-iframe siguen requiriendo una solución compatible en la capa de alojamiento. No se simulan mediante etiquetas meta no soportadas. No cambiar DNS, MX ni registros de Google Workspace al actualizar archivos.

Las afirmaciones de seguridad deben corresponder al alcance documentado en SEGURIDAD-CONTENIDO.md. La activación ZDR consta en la documentación del motor; falta archivar su confirmación escrita. No extenderla a funciones no elegibles, almacenamiento local ni informes. El aislamiento entre entidades, el cifrado de la plataforma y las certificaciones requieren evidencia propia. Antes de incorporar expedientes de una entidad se necesita la documentación técnica y jurídica correspondiente.

## Diseño y mantenimiento

Consulta [AUDITORIA.md](AUDITORIA.md) para los 20 cambios y resultados, y [CREDITOS.md](CREDITOS.md) para procedencia y licencias. Cabecera y pie se repiten deliberadamente en HTML estático; al modificarlos, mantener las ocho páginas sincronizadas y verificar aria-current en las interiores.

Los originales de imágenes/fuentes se conservan. El navegador recibe WebP responsive y tres fuentes WOFF2. No añadir recursos de terceros ni scripts inline sin revisar la CSP. La navegación y los heroes no tienen animaciones de entrada. La ilustración de Plataforma incluye un recorrido interno independiente. Al bajar, los bloques nuevos aparecen con opacity/transform durante 480–560 ms y 18–22 px de recorrido. Los pasos comienzan en orden con 200 ms de separación y las tarjetas con 100 ms; la espera máxima es 480 ms. Cada bloque aparece una sola vez por documento. Menú y respuestas usan fundidos de 160–180 ms; botones y tarjetas mantienen su posición al pasar el cursor. Los enlaces a secciones llegan directamente. No hay bucles ni parallax. El HTML base es visible; sólo con JavaScript y las APIs disponibles se preparan bloques fuera de pantalla para su aparición. El foco, los fragmentos y el movimiento reducido liberan el contenido pendiente. Se respeta prefers-reduced-motion incluso cuando cambia durante la sesión. Criterios, hallazgos y alcance en [AUDITORIA-ANIMACIONES.md](AUDITORIA-ANIMACIONES.md).

## Videos ambientales

Los cinco videos de Inicio, Para entidades, Seguridad y Prueba gratis se reproducen silenciados e inline, con repetición nativa continua. Se eliminó la espera de cinco segundos sobre el último fotograma, que parecía un bloqueo en móvil. Cada video tiene una versión MP4 H.264 de 640 × 360 para pantallas de hasta 760 px y conserva la de 1280 × 720 para escritorio. Las versiones móviles no contienen audio, tienen el índice MP4 al inicio (`faststart`) y un límite de bitrate de 700 kbit/s.

`site.js` precarga el video cuando está a 250 px de entrar en pantalla y sólo lo reproduce mientras alguna parte es visible. Al salir de pantalla, ocultar la pestaña o abandonar la página, pausa el video y cancela la recuperación. Al volver, continúa usando el mismo elemento. Si la reproducción no avanza durante diez segundos, intenta una sola recarga; si sigue atascada, muestra la imagen de respaldo. Un error de red se puede recuperar al volver la conexión. Si el navegador bloquea autoplay, muestra el respaldo y vuelve a intentar dentro del siguiente toque o interacción del usuario. Con movimiento reducido se muestra la imagen sin descargar el MP4; sin JavaScript queda la portada nativa estática.

Los elementos usan `data-video-ambiental` y una imagen hermana `data-video-fallback`. No se añaden controles visibles. La reproducción automática sin un mecanismo de pausa en la página mantiene la limitación de accesibilidad respecto a WCAG 2.2.2 ya documentada; los botones se retiraron por solicitud del propietario.

Comprobaciones del controlador sin dependencias: `node --test scripts/check_video_runtime.cjs`. Para comprobar los archivos y la reproducción real en Chrome, inicia el servidor local y abre `/scripts/check_video_browser.html`, manteniendo la ventana en primer plano; el botón ejecuta seis escenarios con viewport móvil y de escritorio, cambio de fuente, avance, repetición, scroll y restauración de página. Este archivo está en `scripts/` y se excluye de la publicación. Las pruebas opcionales de Playwright están en `scripts/check_video.py`, con `--video-selector "#video-portada"` o `--video-selector "#video-equipo"` y los argumentos de servidor y navegador.

## Demostración de Plataforma

`demo.js` anima únicamente el recuadro conceptual de `plataforma.html`: un cursor simulado selecciona Factura, Historia clínica, Órdenes, Autorizaciones y Registros, actualizando el contexto del panel. El estado permanece pendiente de auditor; no se simula una aprobación. El recorrido dura 4,9 segundos y se ejecuta una sola vez por documento cuando al menos el 55 % del recuadro es visible. Se pausa fuera de pantalla o al ocultar la pestaña, recalcula posiciones al cambiar el tamaño y queda estático con movimiento reducido o sin JavaScript. No añade controles ni envía datos. Pruebas: `scripts/check_demo.py` con los mismos argumentos de servidor y navegador que las pruebas de video.
