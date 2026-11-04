# Publicación por SDK

## Go

El módulo está en la raíz de peru-sdk-go. VERSION determina la próxima versión, inicialmente 0.1.0-alpha.1. Release tiene publish=false por defecto: construye una distribución fuente aislada, ejecuta su suite y compila un consumidor externo.

Después de fusionar, ejecutar Release desde main con publish=true. El job verifica hashes y commit, crea la etiqueta v<VERSION> y la release de GitHub. GITHUB_TOKEN tiene escritura solo en ese job. No sobrescribe etiquetas ni archivos con otro contenido; una reejecución completa archivos faltantes y conserva los ya comprobados.

Go resuelve el módulo desde Git; no hay que subir un ejecutable ni configurar una cuenta de registro. Después de publicar: go get github.com/DataScienceResearchPeru/peru-sdk-go@v0.1.0-alpha.1.

## Python

Release construye wheel y sdist y ejecuta los tests del sdist contra la wheel instalada fuera del checkout. Solo dist/ se envía a PyPI; procedencia y hashes se conservan en manifest/.

Configurar un Trusted Publisher pendiente o existente en una cuenta PyPI del proyecto:

| Campo | Valor |
| --- | --- |
| Proyecto | peru-sdk, sujeto a disponibilidad |
| Owner | DataScienceResearchPeru |
| Repository | peru-sdk-python |
| Workflow | release.yml |
| Environment | pypi |

El tag debe coincidir exactamente con pyproject.toml: inicialmente v0.1.0a1. Su push activa construcción, validación y publicación OIDC. También puede ejecutarse Release sobre esa etiqueta con publish=true. La ejecución manual predeterminada solo prepara artefactos. La publicación externa necesita esa configuración inicial de cuenta; no se ha completado una publicación PyPI en esta migración.

## Otros ecosistemas e infraestructura

Cada lenguaje nuevo tendrá empaquetado propio y consumirá la batería común por versión. Java/Maven y TypeScript/npm todavía no están implementados; no se crean paquetes vacíos en sus registros.

Los jobs ordinarios no reciben credenciales de registros. La configuración k3s no cambia: estos workflows usan runners de GitHub. No se añaden runners al host.
