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
- seguridad.html: requisitos del producto que deben validarse antes de tratar datos reales.
- nosotros.html: propósito, disciplinas del equipo y principios.
- recursos.html: glosario y preguntas frecuentes.
- privacidad.html: información del sitio, distinta de los acuerdos de tratamiento de la plataforma.
- styles.css: tokens, base, navegación, portada y componentes compartidos.
- interiores.css: composiciones y componentes de las páginas de detalle.
- site.js: mejora progresiva; sin cookies, almacenamiento local, telemetría ni dependencias.
- assets/: marca, imágenes optimizadas, tipografía local y licencias.

El correo confirmado es **carlosromero@audittia.com**. Los enlaces abren la aplicación de correo del visitante; no envían nada automáticamente. No solicitar ni recibir historias clínicas por el canal inicial.

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

No publicar garantías sobre aislamiento, retención cero, cifrado de la plataforma o certificaciones sin pruebas y contratos. Antes de procesar expedientes reales se necesita la documentación técnica y jurídica correspondiente.

## Diseño y mantenimiento

Consulta [AUDITORIA.md](AUDITORIA.md) para los 20 cambios y resultados, y [CREDITOS.md](CREDITOS.md) para procedencia y licencias. Cabecera y pie se repiten deliberadamente en HTML estático; al modificarlos, mantener las ocho páginas sincronizadas y verificar aria-current en las interiores.

Los originales de imágenes/fuentes se conservan. El navegador recibe WebP responsive y tres fuentes WOFF2. No añadir recursos de terceros ni scripts inline sin revisar la CSP. Las animaciones usan opacity/transform durante 180–580 ms: hero, tarjetas al desplazarse, menú y respuestas. No tienen bucles ni parallax; el contenido base siempre es visible. Respetan prefers-reduced-motion incluso cuando cambia durante la sesión.
