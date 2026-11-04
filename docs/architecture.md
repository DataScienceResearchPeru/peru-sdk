# SDKs independientes y contratos compartidos

peru-sdk coordina el ecosistema y comprueba integración entre commits concretos. Las implementaciones y credenciales de publicación pertenecen a los repositorios de cada SDK.

- peru-sdk-conformance mantiene los casos sintéticos y su manifiesto de integridad.
- peru-sdk-models mantiene esquemas, fuentes y generación por lenguaje.
- peru-sdk-go mantiene el módulo Go, su corpus local y sus releases.
- peru-sdk-python mantiene el paquete Python, su corpus local y publicación PyPI.

Cada SDK fija commits completos y hashes de los insumos comunes en upstream.lock.json. Los modelos y el corpus se conservan dentro del SDK: instalar, usar o ejecutar sus pruebas nativas no requiere un checkout hermano. Regenerar es una operación explícita de desarrollo, comprobada en un job sin permisos de publicación.

ecosystem.lock.json fija los componentes comprobados juntos. Una corrección de un SDK puede publicarse independientemente; el lock del hub se actualiza para comprobar la nueva combinación. No es necesario que las versiones públicas coincidan.

El verificador descarga cada SDK por commit, construye su distribución y la consume fuera del checkout. También descarga el módulo Go público y ejecuta sus pruebas desde un consumidor externo. Audita archivos para impedir incluir otro SDK en un paquete. Los informes registran commits y hashes.

Los repositorios nuevos permiten merge commits y deshabilitan squash/rebase para conservar las referencias completas fijadas en locks. Si se decide reescribir esas referencias, deben actualizarse los locks y comprobarse la integración.

Se conserva el cliente HTTP SUNAT, autenticación client_credentials, importes exactos y errores diferenciados. RENIEC sigue siendo exclusivamente sintético; emisión UBL y firma permanecen pendientes. La compatibilidad institucional real requiere una comprobación autorizada posterior.
