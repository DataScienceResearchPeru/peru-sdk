# Decisiones iniciales

## Implementación y contrato

Go y Python son implementaciones nativas independientes. No se distribuye un motor compartido ni se ejecutan subprocesos para prestar las operaciones del SDK. Compartimos contratos de datos, procedencia y casos de conformidad, no implementación de negocio.

Los modelos se generan desde un subconjunto limitado de JSON Schema 2020-12. El generador es una herramienta de desarrollo escrita en Python y utiliza gofmt; no forma parte de los paquetes instalables. Los adaptadores HTTP, OAuth y normalización de respuesta se implementan en cada lenguaje y se contrastan con el mismo corpus.

La lógica de emisión fiscal no existe todavía. No creamos un sistema de plugins, un motor de reglas, una ABI o una abstracción universal de instituciones antes de tener casos que los necesiten.

## Fronteras

- Cada cliente recibe su proveedor de token y opciones de transporte. No hay credenciales globales.
- OAuth de Consulta Integrada se separa del cliente de consulta. Su token se almacena en memoria con renovación sincronizada y margen de expiración.
- Los errores públicos no incluyen cuerpos remotos, tokens ni secretos. El código institucional, cuando es un string acotado seguro, queda disponible por separado.
- Los errores de consulta se separan del estado del comprobante. Un código de estado desconocido se conserva.
- RENIEC tiene una interfaz y un proveedor sintético; la interfaz es provisional hasta conocer el contrato autorizado.
- No hay reintentos automáticos ni promesa de exactamente una ejecución.

## Versiones y publicación

El paquete Python empieza en 0.1.0.dev0. Los contratos tienen identificadores propios; su forma actual no es una promesa de estabilidad de producción. Antes de una release se revisarán cambios públicos y se etiquetará el módulo Go con el prefijo de su subdirectorio.

CI verifica paquetes instalados antes de producir distribuciones de prueba. No se configuran tokens de publicación ni un pipeline de publicación a registros que todavía no administramos. La ejecución manual de distribución produce artefactos y hashes para revisión.

## Trabajo pendiente que afecta a decisiones futuras

La comprobación normativa automatizada comienza con un documento descargable. No puede detectar validaciones no publicadas por SUNAT. Las integraciones reales y la vigilancia de otras fuentes se incorporarán como señales separadas de las pruebas locales. Los nuevos lenguajes deberán ejecutar el mismo corpus y conservar su ergonomía propia.
