# Auditoría y rediseño de AUDITTIA

Fecha: 17 de septiembre de 2026 (Colombia). Alcance: diseño, experiencia de uso, accesibilidad, arquitectura del sitio estático, contenido público, rendimiento de recursos y endurecimiento del navegador. Se inspeccionaron las siete páginas originales, el dominio publicado y la nueva versión local, que añade una página 404.

**Estado de esta auditoría: versión local validada antes de publicación.** Posteriormente el propietario autorizó publicar en audittia.com. Se añadió deploy.yml para desplegar sólo el artefacto validado mediante GitHub Actions, conservando el dominio y HTTPS. Este informe documenta el diagnóstico inicial; el estado de la publicación se consulta en GitHub Actions. No se modifican DNS, correo ni cuentas del proveedor.

## Diagnóstico

El sitio tenía una buena base: identidad azul/lima, contenido en español, HTML semántico, navegación entre páginas y recursos locales. HTTPS ya funcionaba. El principal problema no era un fallo del servidor: era la combinación de contenido provisional, recorridos comerciales interrumpidos y demasiada repetición visual.

La auditoría encontró 41 enlaces de correo sin destinatario real, marcadores de métricas y nombres visibles, una política con 21 apartados vacíos y afirmaciones de seguridad del producto que este repositorio no permite comprobar. En escritorio, la portada superaba los 11.500 píxeles de alto.

No se encontró evidencia de una vulnerabilidad crítica explotable en el alcance revisado. Esto **no equivale a un pentest**, una certificación de accesibilidad, una revisión jurídica ni una auditoría de la aplicación SaaS. El repositorio no contiene su backend, bases de datos, autenticación, proveedores de IA ni acuerdos de tratamiento.

## Método y evidencias iniciales

- Inspección de HTML y CSS, recursos, enlaces, metadatos, despliegue y contenido de las siete páginas.
- Navegación y renderizado en Chrome: 390, 820, 1024 y 1440 px antes del cambio; cinco tamaños en la nueva versión.
- Capturas, comprobación de imágenes, desbordamientos, consola, teclado, menú, FAQ y reducción de movimiento.
- Diagnóstico HTTP/HTTPS público, sin escaneo intrusivo ni autenticación; inspección de configuración pública de GitHub Pages.
- Pruebas de accesibilidad con axe-core 4.13.0 en móvil y escritorio, más revisión visual. Los hallazgos automáticos requieren interpretación.

Evidencia del original, antes de modificarlo: contacto roto en index.html y todas las interiores; métricas provisionales en index.html aproximadamente líneas 315–329; nombres pendientes en nosotros.html aproximadamente líneas 50–58; apartados vacíos en privacidad.html aproximadamente líneas 68–170; garantías no demostrables en index.html y seguridad.html. Las líneas actuales cambiaron por el rediseño.

No se atribuyeron fallos inexistentes: las páginas originales ya tenían un H1, foco visible, reducción de movimiento y navegación móvil funcional; no se encontró desbordamiento horizontal ni enlaces internos a archivos ausentes en la muestra inicial.

## Los 20 cambios propuestos y su implementación

Prioridad alta: impide contacto o afecta confianza. Media: mejora comprensión, accesibilidad o defensa. Normal: presentación, recuperación y mantenimiento. “Aplicado” significa en esta versión local, no en producción.

| # | Prioridad | Falencia y cambio propuesto | Implementación / estado |
|---|---|---|---|
| 1 | Alta | Los 41 mailto tenían un marcador. Conectar todos los recorridos comerciales con un destinatario confirmado. | **Aplicado:** carlosromero@audittia.com en cabecera, contenido y pie. El usuario confirmó el correo; no se envió ningún mensaje ni se probó la entrega del buzón. |
| 2 | Alta | Portada excesiva y repetida respecto de las interiores. Convertirla en una introducción con rutas claras. | **Aplicado:** siete secciones principales; metodología completa, controles y glosario permanecen en sus páginas. |
| 3 | Media | Titular de 19 palabras, mayúsculas y bloque muy alto. Priorizar una propuesta de valor breve y dos acciones distinguibles. | **Aplicado:** “Más claridad en cada cuenta médica”, acción comercial y acceso a la plataforma. |
| 4 | Media | La exploración dependía de leer bloques largos. Introducir accesos orientados a tareas. | **Aplicado:** plataforma, perfil de entidad y seguridad inmediatamente después del hero, con destino y texto descriptivos. |
| 5 | Media | Tipografía condensada dominante y cinco archivos TTF pesados. Mejorar lectura y reducir variantes. | **Aplicado:** Work Sans 400/600/700, titulares en frase, pesos coherentes y WOFF2 locales. Licencias y originales conservados. |
| 6 | Media | Espaciado y superficies grandes alargaban la lectura. Establecer una escala y rejillas adaptables. | **Aplicado:** contenedor de 1200 px, márgenes fluidos, separación consistente y cambios de columnas en tablet/móvil. |
| 7 | Normal | Tarjetas y bandas de color competían entre sí. Definir bordes, radios y elevación por función. | **Aplicado:** bordes finos, radios de 8–24 px, sombras discretas y menos superficies saturadas. |
| 8 | Media | Una sola fotografía se repetía en varios contextos. Añadir imágenes editoriales distintas y pertinentes. | **Aplicado:** médica en portada, revisión colaborativa en bloque humano y dos médicos en Entidades. Créditos/licencia en CREDITOS.md; no se presentan como clientes o fundadores. |
| 9 | Media | Imágenes sin estrategia explícita de carga. Optimizar formatos, tamaño y prioridad. | **Aplicado:** variantes WebP 640/1200, srcset, sizes, dimensiones, decoding async, prioridad del hero y carga diferida bajo el primer viewport. |
| 10 | Media | Interiores y diagramas no tenían suficiente diferenciación editorial. Diseñar composiciones propias y legibles. | **Aplicado:** heroes, perfiles, pasos, diagramas documentales, controles, roles, glosario y documentos en interiores.css. La UI de Plataforma está rotulada como conceptual. |
| 11 | Alta | Nombres y cifras provisionales deterioraban credibilidad. Publicar sólo información respaldada. | **Aplicado:** roles profesionales en vez de nombres ficticios, beneficios cualitativos y eliminación de porcentajes pendientes/texto de implementación. |
| 12 | Alta | Privacidad contenía 21 apartados vacíos. Sustituirlos por información útil sobre el sitio real. | **Aplicado:** seis apartados sobre navegación, hosting, recursos, correo, precauciones y límites del servicio. No se presenta como política jurídica definitiva de la plataforma. |
| 13 | Alta | Se afirmaban retención cero, aislamiento y cifrado del SaaS sin evidencia en el repositorio. Separar objetivos de controles verificados. | **Aplicado al contenido:** requisitos sujetos a validación técnica/contractual; sin certificaciones ni garantías inventadas. La validación del producto sigue pendiente fuera del alcance. |
| 14 | Media | El menú móvil no cerraba con Escape ni clic exterior. Mejorar su interacción sin dependencia de JS. | **Aplicado:** cierre progresivo y foco de vuelta al control con Escape; details conserva funcionalidad sin JavaScript. |
| 15 | Media | Enlaces secundarios pequeños y necesidad de revisar contraste/semántica tras el rediseño. Verificar acceso por teclado y legibilidad. | **Aplicado:** objetivos más cómodos, foco visible, regiones nombradas, textos alternativos y contraste corregido. Se preservan enlace de salto y FAQ nativa. |
| 16 | Normal | Faltaba continuidad visual en la lectura. Añadir movimiento breve, útil y opcional. | **Aplicado:** entrada del hero, apariciones escalonadas de tarjetas en portada e interiores, menú y respuestas. Duración de 180–580 ms y retrasos acotados. Sin parallax, reproducción continua ni contenido inicialmente oculto; respeta movimiento reducido y cancela animaciones si cambia la preferencia. |
| 17 | Media | Faltaban canonical, imagen social, favicon, robots y sitemap. Completar descubrimiento y presentación al compartir. | **Aplicado:** metadatos por página, tarjeta social local, icono derivado del logo, mapa de siete URLs y 404 noindex. No garantiza posicionamiento ni validación de todas las plataformas sociales. |
| 18 | Media | Faltaban políticas de defensa del navegador. Restringir orígenes y documentar límites del hosting. | **Parcial:** CSP estricta y no-referrer por meta en ocho páginas; recursos locales y sin inline. HSTS, nosniff, Permissions-Policy y anti-iframe HTTP requieren configuración compatible del alojamiento; no se simulan mediante meta. |
| 19 | Media | Publicación de raíz sin validación propia, documentación desactualizada y exposición de archivos auxiliares. Añadir controles y un artefacto limitado. | **Implementado para la publicación autorizada:** validación estática, prueba de navegador, build de lista explícita y deploy.yml con publicación dependiente de las comprobaciones. README actualizado. La protección de rama sigue siendo un ajuste administrativo independiente. |
| 20 | Normal | La recuperación de rutas inexistentes usaba el error genérico del proveedor. Crear una salida útil y coherente. | **Aplicado:** 404 institucional con regreso al inicio, navegación y rutas absolutas para que sus recursos funcionen también en direcciones anidadas. |

## Resultados medidos

| Medida | Antes | Nueva versión |
|---|---:|---:|
| Altura de portada, 1440 px | 11.541 px | 4.401 px |
| Altura de portada, 390 px | 15.932 px | 6.450 px |
| Enlaces con destinatario provisional | 41 | 0 |
| Apartados vacíos de privacidad | 21 | 0 |
| Archivos de fuentes declarados | 5 TTF, 519.828 bytes | 3 WOFF2, 66.888 bytes |
| CSS necesario para portada | 58.242 bytes | Aproximadamente 22 KB |

La altura cambia levemente con viewport, fuente y FAQ abiertas. La reducción de fuentes es de aproximadamente 87% en tamaño de archivos, **no** una promesa del mismo porcentaje de mejora de carga. No se midieron Core Web Vitals de usuarios reales ni se inventaron puntuaciones Lighthouse.

Pruebas de la versión nueva:

- Validación estática de ocho HTML y 361 referencias: enlaces, fragmentos, imágenes responsive y recursos CSS.
- 35 renderizados iniciales de siete páginas en 360, 390, 820, 1024 y 1440 px: sin desbordamientos, imágenes rotas ni errores de consola/CSP/JavaScript.
- Prueba final reproducible ampliada a ocho páginas, incluida 404, en scripts/check_browser.py: **40 renderizados, cero desbordamientos, cero imágenes rotas, cero errores de consola y cero fallos de las comprobaciones funcionales**.
- Menú con Escape/clic exterior; FAQ y navegación sin JavaScript; reducción de movimiento sin animaciones; imágenes diferidas cargadas al desplazarse.
- axe-core en ocho páginas a 390 y 1440 px, con FAQ abiertas: **cero violaciones automáticas detectadas** tras corregir tres textos de contraste y la región de utilidad. Quedan avisos de revisión manual de contraste: se inspeccionaron en portada los símbolos decorativos con aria-hidden y el pie de fotografía, cuyo contraste sobre blanco es 6,16:1. Cero violaciones automáticas no certifica WCAG ni sustituye pruebas con tecnologías de asistencia.
- Artefacto final .site-final validado, con 37 archivos públicos y sin README, scripts, informes, .git ni configuración de desarrollo. El script no borra ni sobrescribe salidas anteriores.

## Seguridad: qué se verificó y qué no

### Dominio y alojamiento observados

HTTPS de audittia.com responde 200. HTTP y www redirigían a HTTPS del dominio principal durante la inspección inicial. GitHub Pages indicaba HTTPS obligatorio y certificado aprobado para ambos nombres, con vencimiento indicado 16 de diciembre de 2026. Se volvió a comprobar HTTPS sin ignorar la verificación del certificado.

El sitio publicado aún es la versión anterior: la última comprobación conserva la respuesta de GitHub Pages y no incorpora automáticamente los cambios locales. No se modificaron registros de Workspace ni MX.

### Superficie del sitio estático

No hay login, pagos, formularios de envío, subida de historias clínicas ni backend en este proyecto. Las fuentes, fotografías y el pequeño script se sirven localmente. No se añadió analítica, cookies, almacenamiento local ni SDK externo.

La política del navegador restringe scripts, estilos, imágenes y fuentes al mismo origen; bloquea conexiones iniciadas por scripts, objetos, base-uri y envíos de formularios. La etiqueta está antes de los recursos. Se eliminaron estilos inline para no recurrir a unsafe-inline.

La ausencia de formularios **no significa ausencia de todo tratamiento**: [GitHub documenta el registro de direcciones IP por seguridad en Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection). El enlace mailto abre el servicio de correo del visitante; el sitio no envía mensajes.

### Pendientes del alojamiento y de la aplicación

La respuesta HTTP examinada carece de CSP por encabezado, HSTS, X-Content-Type-Options, Referrer-Policy por encabezado, Permissions-Policy y protección anti-iframe. CSP/referrer por meta son mejoras parciales; [frame-ancestors no admite meta](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/frame-ancestors). Se necesita una capa de alojamiento que permita esos encabezados para completar este endurecimiento. Esta carencia no demuestra por sí sola una explotación.

GitHub publicaba main desde la raíz y la rama no estaba protegida en la consulta realizada. README.md era accesible públicamente; .git/config devolvía 404. Un workflow de validación no bloquea por sí solo la publicación actual de raíz: hay que configurar el uso del artefacto y las reglas de rama.

No se verificaron controles del SaaS: separación entre entidades, borrado, retención de proveedores de IA, cifrado en reposo, gestión de claves, trazabilidad, backups, autenticación ni respuesta a incidentes. Requieren arquitectura real, pruebas específicas y documentación contractual antes de usar datos de pacientes.

## Decisiones de diseño y referencias

De [Medicare en español](https://es.medicare.gov/) se tomó la organización por tareas y la claridad de acceso. De [Didi Hirsch](https://didihirsch.org/) se tomó el equilibrio entre fotografía humana, bloques editoriales y rutas por audiencia. La interpretación para AUDITTIA conserva su logo y azul/lima; no reutiliza marcas ajenas, testimonios, cifras, plugins ni código de seguimiento.

La página de Recursos y las interiores conservan información suficiente para decisiones institucionales. La portada prioriza comprensión y contacto. El movimiento es discreto y no sustituye contenido, navegación o evidencia.

Las fotos tienen licencia Pexels, no se describen como “sin copyright” ni como usuarios reales. Fuentes y créditos están documentados en CREDITOS.md.

## Repetir las comprobaciones

Consulta README.md para iniciar el servidor y ejecutar:

1. python3 scripts/check_site.py
2. python3 scripts/check_browser.py con Playwright y navegador disponibles; axe-core local es opcional.
3. python3 scripts/build_site.py con una salida nueva.
4. python3 scripts/check_site.py --root .site

Antes de publicar: revisar visualmente la versión final, decidir el origen de publicación en Pages y confirmar los pendientes técnicos/jurídicos del servicio. Este informe es apto para un repositorio público: no contiene credenciales ni datos clínicos.

Fuentes técnicas complementarias: [CSP y sus límites](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP), [HTTPS en GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https), [protección de ramas](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches), [axe-core](https://github.com/dequelabs/axe-core).
