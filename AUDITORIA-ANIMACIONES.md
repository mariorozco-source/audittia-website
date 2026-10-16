# Auditoría de animaciones · AUDITTIA

Fecha: 15 de octubre de 2026. Alcance: las ocho páginas HTML, `site.js`, `styles.css` e `interiores.css` del proyecto local.

## Criterio de evaluación

Para este sitio corporativo, el movimiento debe ayudar a reconocer una interacción o acompañar el descubrimiento de contenido, sin retrasar la lectura ni repetir una presentación al navegar. No existe una duración universal que certifique una web como «profesional»: las cifras siguientes son decisiones de diseño para AUDITTIA.

Referencias técnicas:

- [W3C, Animation from Interactions, WCAG 2.3.3 (AAA)](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions): el movimiento no esencial activado por interacciones debe poder desactivarse. Aplicar este criterio no equivale a certificar todo el sitio como WCAG AAA.
- [W3C, técnica C39](https://www.w3.org/WAI/WCAG22/Techniques/css/C39.html): respetar la preferencia de movimiento reducido.
- [web.dev, animaciones de alto rendimiento](https://web.dev/articles/animations-guide): preferir `opacity` y `transform` para desplazamientos animados y evitar propiedades que recalculen la disposición.

## Hallazgos y ajustes

| Elemento | Antes | Resultado |
| --- | --- | --- |
| Entrada de páginas, incluida Plataforma y Seguridad | Textos del hero animados individualmente durante 480 ms, retrasos de hasta 140 ms; imagen durante 580 ms con 70 ms de retraso. Se repetía en cada navegación. | Eliminada en todas las rutas. Título, imagen y acciones disponibles inmediatamente. |
| Bloques al bajar | Desplazamiento de 12 px, opacidad inicial del 55 %, duración de 440 ms y retrasos de hasta 90 ms. | Fundido desde opacidad 0 y recorrido de 18 px durante 480 ms. Los procesos usan 22 px y 560 ms, con 200 ms de separación entre comienzos; las tarjetas, 100 ms. Espera máxima: 480 ms. Cada bloque se consume una vez por documento; volver sobre él no repite la entrada. |
| Cobertura editorial | Varios componentes interiores carecían de entrada al hacer scroll. | Incluye franjas de misión, textos editoriales, beneficios, historia, avisos, listas, comparación de seguridad, ilustraciones documentales y preguntas, además de tarjetas y encabezados existentes. Se excluyen padres/hijos duplicados. |
| Botones | Elevación de 2 px y sombra animada. | Cambio breve de color; posición fija. |
| Tarjetas de acceso | Elevación de 4 px y sombra animada. | Cambio de borde y fondo; posición fija al pasar el cursor. |
| Flechas de enlaces | Desplazamiento horizontal de 4 px. | Flechas estables. |
| Indicador de navegación | Subrayado que se expandía horizontalmente. | Fundido de opacidad de 160 ms; el estado de página actual permanece visible. También reconoce foco por teclado. |
| Menú móvil | Entrada vertical de −5 px, 180 ms. | Fundido de 160 ms sin desplazamiento. Cerrar cancela la animación pendiente. |
| Respuestas de preguntas frecuentes | Entrada vertical de −4 px, 220 ms. | Fundido de 180 ms sin desplazamiento; el desplegado conserva el comportamiento nativo de `details`. |
| Enlaces a secciones | Desplazamiento suave global, incluso para trayectos largos. | Navegación directa, sin recorrer y animar secciones intermedias. Se conserva el espacio reservado para la cabecera fija. |
| Regreso, foco y pestañas | Cancelación por movimiento reducido; protección del foco sólo antes de iniciar una animación. | Se conserva lo anterior y se cancela también al recibir foco, ocultar la página o navegar. Al restaurar una página se omite el contenido ya visible. |

La primera revisión reducía el movimiento a 6 px y un fundido del 85 % al 100 %, sin escalonamiento. Tras la revisión visual del usuario, se amplió la presencia de las entradas y se añadió una secuencia para procesos y tarjetas. Se conserva la ausencia de animación al cambiar de página, de bucles, de parallax y de dependencias, además del funcionamiento sin JavaScript. Privacidad mantiene su lectura estática y la página 404 su respuesta directa.

## Reglas de mantenimiento

- No añadir animaciones de entrada al hero, la página completa, la navegación o el pie.
- Animar bloques coherentes, sin escalonar cada línea ni animar un contenedor y sus descendientes a la vez.
- Preparar con `.motion-pending` únicamente bloques fuera del primer viewport y después de comprobar las APIs de animación y observación. El HTML base, la impresión y el modo de movimiento reducido permanecen visibles. El foco por teclado libera inmediatamente el bloque; al cancelar la observación se retira toda preparación pendiente.
- No repetir entradas al subir y volver a bajar. Una nueva visita que carga otro documento puede volver a animar sus bloques inferiores.
- Respetar cambios de `prefers-reduced-motion` durante la sesión y cancelar inmediatamente las animaciones activas.
- Conservar el desplazamiento nativo del navegador; no interceptar la rueda, el gesto táctil ni las teclas de navegación.

## Verificación

`scripts/check_browser.py` cubre ocho páginas en cinco anchuras con movimiento reducido, funcionamiento sin JavaScript, menú y preguntas. La cobertura de movimiento normal comprueba las ocho rutas a 390 y 1440 px: carga sin entradas, descubrimiento al bajar, ausencia de repeticiones y de animaciones anidadas, límites de duración y espera, navegación superior, enlaces con fragmento y cancelación al activar movimiento reducido. También comprueba la opacidad visible de los tres pasos a 100, 300 y 700 ms: primero sólo el 1, luego 1 y 2, finalmente los tres; incluye la liberación del contenido pendiente por foco y movimiento reducido.

La revisión de código abarca todos los mecanismos de movimiento del sitio. Las pruebas locales de navegador no equivalen a pruebas en todos los dispositivos físicos ni a una auditoría completa de accesibilidad.

Resultados del 15 de octubre de 2026:

- `python3 scripts/check_site.py`: ocho páginas y 362 referencias correctas.
- `node --check site.js` y `git diff --check`: sin errores.
- Playwright con Google Chrome local: 40 comprobaciones de renderizado (ocho páginas × cinco anchuras), sin desbordamientos, imágenes rotas ni animaciones bajo movimiento reducido.
- Movimiento normal: 16 recorridos (ocho páginas × móvil/escritorio) correctos. Secuencia visual 1 → 2 → 3 comprobada a 100, 300 y 700 ms en ambas anchuras. Navegación a Plataforma/Seguridad, fragmentos, foco y movimiento reducido correctos después de este ajuste.
- Menú por teclado, cierre con Escape, preguntas frecuentes y funcionamiento sin JavaScript correctos. Sin errores de consola detectados.
- Inspección visual de Plataforma en escritorio y Seguridad en móvil, incluida su sección de controles. En esta revisión se inspeccionó también la secuencia del proceso de inicio en sus estados intermedio y completo.

Los cambios están en el proyecto local; esta revisión no publica una nueva versión en GitHub Pages.
