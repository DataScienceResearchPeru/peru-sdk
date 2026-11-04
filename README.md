# Peru SDK

Ecosistema MIT de SDKs nativos para servicios del Estado peruano. Cada lenguaje tiene implementación, instalación y releases independientes; se comparten contratos y casos de conformidad versionados.

| Componente | Repositorio | Implementación en revisión |
| --- | --- | --- |
| Go | [peru-sdk-go](https://github.com/DataScienceResearchPeru/peru-sdk-go) | [PR #1](https://github.com/DataScienceResearchPeru/peru-sdk-go/pull/1) |
| Python | [peru-sdk-python](https://github.com/DataScienceResearchPeru/peru-sdk-python) | [PR #1](https://github.com/DataScienceResearchPeru/peru-sdk-python/pull/1) |
| Contratos y generación | [peru-sdk-models](https://github.com/DataScienceResearchPeru/peru-sdk-models) | [PR #1](https://github.com/DataScienceResearchPeru/peru-sdk-models/pull/1) |
| Corpus compartido | [peru-sdk-conformance](https://github.com/DataScienceResearchPeru/peru-sdk-conformance) | [PR #1](https://github.com/DataScienceResearchPeru/peru-sdk-conformance/pull/1) |

Este repositorio contiene coordinación, documentación y un verificador de integración real entre commits públicos. El código de cada SDK se mantiene en su repositorio. Hasta fusionar las PRs, las implementaciones se pueden consumir por los commits completos registrados en ecosystem.lock.json.

## Qué funciona

Go y Python implementan Consulta Integrada SUNAT mediante HTTP y OAuth2 client_credentials, caché/renovación del token, importes decimales exactos y errores diferenciados. También ofrecen un proveedor de identidad sintético para comprobar la extensibilidad de la API.

Las pruebas HTTP se ejecutan contra servidores locales y respuestas sintéticas. No se ha verificado aún el servicio institucional con credenciales reales. El proveedor RENIEC no consulta ni verifica personas. La emisión UBL, firma y CDR permanecen fuera del alcance inicial.

## Reproducir la integración

Requisitos de desarrollo: Git, Go 1.26+ y Python 3.11+.

```bash
python3 -m pip install -r tools/requirements.txt
stage=$(mktemp -d /var/tmp/peru-ecosystem.XXXXXXXX)
python3 tools/check_ecosystem.py --output "$stage"
```

El comando comprueba las referencias comunes, clona los SDKs por commit, crea artefactos aislados y ejecuta sus pruebas fuera de los checkouts. Además descarga el módulo Go desde GitHub, ejecuta un consumidor y su suite desde el módulo distribuido. Python se instala desde la wheel, usando los tests y el corpus contenidos en el sdist. No requiere repositorios hermanos ni credenciales SUNAT/RENIEC.

El resultado incluye report.json con versiones, commits, referencias y número de casos. Los artefactos se inspeccionan para evitar incluir implementaciones de otro SDK. La generación y sincronización son operaciones explícitas de desarrollo; no ocurren al instalar o usar los SDKs.

## Actualizaciones y releases

Cada SDK usa upstream.lock.json y conserva sus modelos y datos de prueba locales. Cambiar un contrato compartido no reescribe ni publica SDKs automáticamente. ecosystem.lock.json solo fija la combinación que verifica este hub.

Go tiene un workflow Release manual que crea tags y releases después de comprobar los artefactos. Python tiene publicación PyPI mediante OIDC preparada, con validación de tag y versión. Para publicarlo falta configurar el Trusted Publisher en una cuenta PyPI del proyecto. No se ha publicado una versión estable ni un paquete PyPI en esta migración.

Orden de fusión: conformidad, modelos, SDKs y este hub. Los repositorios nuevos conservan merge commits para que los hashes fijados sigan siendo alcanzables. El módulo Go nuevo usa github.com/DataScienceResearchPeru/peru-sdk-go; las versiones previas del prototipo conservan su historia en Git.

Más detalles: [arquitectura](docs/architecture.md) y [publicación](docs/publishing.md). Los workflows usan runners de GitHub; no se ha modificado k3s ni añadido runners al host.
