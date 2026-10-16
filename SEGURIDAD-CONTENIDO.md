# Evidencia del contenido de Seguridad

Revisión: 15 de octubre de 2026 (Colombia). Este documento es de mantenimiento y no se incluye en el artefacto público.

Fuente local: proyecto hermano `AUDITIA REPO/auditoria-cuentas-saas`, rama `mario/fase-3`, commit base `524ce0a`. Se inspeccionaron código, pruebas y documentación, sin abrir expedientes reales, credenciales ni grabaciones. Las pruebas se ejecutaron sobre el árbol local de trabajo; al cierre había cambios concurrentes en el cliente de IA y sus pruebas, ajenos a esta actualización del sitio. Esta tarea no modificó el motor. Esta revisión de contenido no demuestra un despliegue de la plataforma ni constituye un pentest.

## Correspondencia de las afirmaciones

Las rutas siguientes son relativas al repositorio del motor.

| Contenido público | Evidencia inspeccionada | Alcance |
| --- | --- | --- |
| Sustitución de identificadores antes del análisis | `src/motor/seudonimizar/index.ts`, `semilla.ts`, `seudonimizar/regex-co.ts`; pruebas en `tests/seudonimizar/` | Identificadores reconocidos por patrones, contexto y semilla. No es anonimización ni garantía de detección universal. |
| Segunda capa de nombres | `src/motor/llm/proteger.ts`, `tests/llm-proteger.test.ts` | Se aplica a los extractos e instrucciones destinados a la API. Hay límites declarados para palabras comunes y apellidos ambiguos. No se publican porcentajes generales. |
| Envío bloqueado si la compuerta detecta identificadores | `src/motor/llm/cliente.ts:llamar`, `auditar-caso.ts:verificarPaso`; `tests/llm.test.ts` | La verificación precede a la llamada. La afirmación se limita a lo detectado; no promete ausencia absoluta de datos identificables. |
| Extractos por tarea y cálculos en el motor | `src/motor/llm/paso*.ts`, `src/motor/reglas/`, `auditar-caso.ts` | No se afirma que todos los extractos sean breves ni que nunca se envíe un soporte completo. |
| Mapa de identidad en memoria | `seudonimizar/index.ts:resumenPersistible`, `llm/proteger.ts`, `auditar-caso.ts` | El mapa no forma parte de las consultas ni del resumen persistible. Los documentos fuente y el informe siguen siendo sensibles. |
| Control de resultados intermedios y permisos de archivos | `src/motor/salida.ts`, `tests/salida.test.ts`, `tests/seudonimizar/manifiesto.test.ts` | Verificación antes de escribir, creación exclusiva, carpetas 0700 y archivos 0600 fuera del repositorio. Estos permisos no equivalen a cifrado. |
| Claves fuera del navegador y cliente de servidor sin grabación | `src/motor/llm/cliente.ts:crearClienteServidor` | Código del cliente preparado para servidor. No acredita despliegue, gestión centralizada de secretos ni permisos de la futura plataforma. |
| Restitución local de identidad en el informe | `src/motor/informe/reidentificar-informe.ts`, `cli.ts`; `tests/docx.test.ts` | Validación de marcadores del caso y secciones permitidas. El Word puede contener datos personales y se identifica como confidencial. |
| Citas y revisión humana | `src/motor/llm/paso*.ts`, `CONTEXTO_DEL_PROYECTO.md` | Las verificaciones de citas y la validación por el auditor forman parte del proceso; no se promete exactitud absoluta ni aprobación automática. |
| ZDR activada en la organización el 14/10/2026 | `CLAUDE.md`, `CONTEXTO_DEL_PROYECTO.md`, sección 6.3 | Activación registrada en la documentación interna. No se accedió a la consola del proveedor; falta archivar la confirmación escrita, como indica el propio contexto. El texto público atribuye la activación al registro y exige documentación en la puesta en marcha. |
| API de mensajes y caché del instructivo | `src/motor/llm/cliente.ts`, `tests/llm.test.ts` | Solo el instructivo lleva `cache_control`; no los extractos clínicos. Esto no significa ausencia de procesamiento transitorio. No se usan Batch ni Files en el motor inspeccionado. |
| Retención y uso para entrenamiento del proveedor | [Documentación oficial de Anthropic](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention), consultada el 15/10/2026 | ZDR depende de organización, workspace, modelo y funciones elegibles; existen excepciones por seguridad y obligaciones legales. El proveedor declara que no entrena con datos retenidos sin permiso expreso. No se presenta ZDR como una certificación. |
| Sitio sin seguimiento ni carga de expedientes | HTML, `site.js`, CSP y `privacidad.html` de este repositorio | Sin formularios de carga, cookies de seguimiento ni analítica incorporada. El alojamiento y el correo tienen condiciones propias. |

## Límites que conserva la página

- El contenido describe avances del motor a octubre de 2026, sin convertirlos en garantías de una plataforma multiusuario desplegada.
- No se atribuyen negligencia, venta de datos ni malas prácticas a competidores. La comparación presenta criterios verificables y la respuesta de AUDITTIA.
- La seudonimización conserva fechas, diagnósticos y valores. Los extractos siguen siendo sensibles y pueden tener riesgo de reidentificación por contexto.
- El entorno local de desarrollo conserva respuestas para repetir pruebas. El cliente de servidor no graba. No se promete retención cero de los documentos de AUDITTIA.
- El aislamiento entre entidades, los roles, el cifrado de infraestructura, las copias, la eliminación y los plazos requieren validación y acuerdos propios.
- La confirmación escrita ZDR, la finalidad y las instrucciones de tratamiento deben documentarse antes de la puesta en marcha con cada entidad.
- No se anuncian certificaciones ISO, SOC, HIPAA, cumplimiento normativo acreditado ni seguridad absoluta.

## Verificación de esta actualización

- Validación estática del sitio y del artefacto público: ocho páginas, referencias locales, metadatos y políticas del navegador.
- Prueba de navegador existente: 40 renderizados (ocho páginas a 360, 390, 820, 1024 y 1440 px), sin desbordamientos, imágenes rotas ni errores de consola. Menú, movimiento reducido y funcionamiento sin JavaScript correctos.
- Inspección visual de Seguridad en escritorio y móvil; comprobación adicional de las preguntas con teclado y sin JavaScript, enlace a controles y ancho de 320 px con preguntas abiertas. Tras ajustar las dos referencias en Recursos, se comprueba de nuevo esa página en los cinco tamaños.
- Pruebas del motor con datos sintéticos y API simulada: **143 pruebas correctas en 14 archivos**. Comando: `npm test -- tests/seudonimizar tests/llm-proteger.test.ts tests/llm.test.ts tests/salida.test.ts tests/docx.test.ts`.
- Sin llamadas reales a la API, lectura de expedientes ni cambios al motor. No se verificó la configuración de una cuenta del proveedor ni un despliegue en producción.

Publicación autorizada por el propietario el 15 de octubre de 2026 mediante el workflow de GitHub Pages. El resultado del despliegue se consulta en GitHub Actions. Este documento de evidencia no forma parte del artefacto del sitio generado por `scripts/build_site.py`; el repositorio de código es público.
