# Evidencia y límites de compatibilidad

## Fuentes oficiales

- [Manual de Consulta Integrada](https://www.gob.pe/institucion/sunat/informes-publicaciones/454600-manual-de-consulta-integrada-de-validez-de-comprobantes-de-pago): autenticación client_credentials, URL con RUC del consultante, formato del cuerpo y códigos.
- [Referencia CPE del manual v2.0](https://cpe.sunat.gob.pe/sites/default/files/inline-files/Manual-de-Consulta-Integrada-de-Comprobante-de-Pago-por-ServicioWEB_v2_0.pdf): lectura documental; su descarga HTTP directa estaba bloqueada al establecer la línea base.
- [Consulta de validez](https://www.gob.pe/7311-consultar-la-validez-del-comprobante-de-pago): requisitos de consulta y precisión de importes.
- [Acceso RENIEC](https://www.gob.pe/13543-solicitar-acceso-al-servicio-de-verificacion-de-identidad-de-personas-en-reniec): condiciones de acceso; no contiene un contrato de operación suficiente para implementar el cliente real.

`contracts/sources.lock.json` registra la descarga verificable del PDF alojado en el dominio oficial gob.pe y su SHA-256. No redistribuimos ese documento ni importamos código, plantillas o pruebas de otros proyectos.

## Decisiones de interpretación

El manual llama al campo de observaciones `Observaciones`; el lector admite también `observaciones` como compatibilidad defensiva. Los casos son sintéticos: no se afirma haber observado ambas formas en producción. Las observaciones omitidas o null se normalizan a una colección vacía.

`estadoCp` se documenta como entero y el anexo representa códigos entre comillas. Se admiten enteros no negativos o strings de dígitos; se conserva el código desconocido. No se admiten booleanos, decimales ni un éxito sin datos de estado. Los campos extra se ignoran; no se promete retener el cuerpo original completo en esta versión.

El PDF señala `monto n(8,2)` y la página de consulta señala hasta 15 enteros y 2 decimales. El contrato admite el límite de la página y lo transporta exactamente; la aceptación de ese extremo por la API debe comprobarse con acceso autorizado. La validación RUC solo verifica once dígitos, no la existencia ni el dígito verificador.

El contrato inicial exige monto y una serie alfanumérica de cuatro caracteres: es un alcance acotado para comprobantes electrónicos, no soporte completo de documentos físicos ni de todos los casos institucionales.

## Qué prueban los tests

Los casos de `conformance/cases.json` son originales y sintéticos. Go y Python verifican los mismos 17 casos de entrada, 17 respuestas y 3 consultas de identidad. Además comprueban en loopback la construcción real de solicitudes, precisión decimal, cache/expiración del token, concurrencia, errores HTTP, límites y ausencia de redirecciones y reintentos.

Los tests no consultan SUNAT ni RENIEC. Un resultado verde acredita esos contratos y simulaciones, no disponibilidad ni homologación institucional. El proveedor de identidad no descubre ni verifica datos personales.

## Señales externas

`Official source watch` diferencia documento cambiado y fuente inaccesible. Un cambio de hash requiere revisión; no demuestra por sí solo una modificación normativa. Un hash igual tampoco garantiza que no exista una publicación más reciente en otra URL. No se modifican reglas ni se envían comprobantes reales desde CI.
