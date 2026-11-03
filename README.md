# Peru SDK

[![CI](https://github.com/DataScienceResearchPeru/peru-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/DataScienceResearchPeru/peru-sdk/actions/workflows/ci.yml)

SDKs nativos para integrar servicios del Estado peruano, con contratos comunes y pruebas de conformidad. Licencia MIT.

**Prueba mínima en desarrollo.** Go y Python ejecutan implementaciones propias: no requieren un motor compartido, PHP, un servidor intermedio ni un compilador adicional para instalar el paquete Python. No hay dependencias de terceros en el runtime de esta prueba.

## Alcance comprobado

| Capacidad | Go | Python | Evidencia |
|---|---|---|---|
| Modelos desde JSON Schema | Sí | Sí | Generación reproducible y validación del corpus |
| Consulta Integrada SUNAT | Cliente HTTP | Cliente HTTP | Solicitudes contra servidor local y respuestas sintéticas |
| OAuth2 `client_credentials` | Sí | Sí | Expiración, caché y renovación concurrente con servidor local |
| Consulta de identidad | Proveedor simulado | Proveedor simulado | Datos sintéticos; contrato provisional |
| Integración real con SUNAT o RENIEC | No verificada | No verificada | Sin credenciales ni consultas reales |
| Emisión UBL, firma y CDR | Pendiente | Pendiente | Fuera del alcance inicial |

Las pruebas no acreditan aceptación por una institución. El proveedor RENIEC no consulta personas ni representa un endpoint oficial. El nombre del paquete Python todavía no implica disponibilidad en PyPI.

## Probar sin credenciales

Requisitos: Go 1.26+ y Python 3.11+. Los scripts de generación necesitan ambos; cada SDK funciona independientemente.

```bash
git clone https://github.com/DataScienceResearchPeru/peru-sdk.git
cd peru-sdk
python3 -m pip install ./sdk-python
python3 examples/offline.py
go -C sdk-go run ./examples/offline
```

Los ejemplos son locales y no realizan peticiones HTTP.

### Go

```go
service, err := reniec.NewMockIdentityService([]reniec.Identity{
    {DNI: "00000001", GivenNames: "PERSONA", FirstSurname: "PRUEBA", SecondSurname: "SINTETICA"},
})
if err != nil {
    return err
}
person, err := service.Lookup(ctx, reniec.IdentityQuery{DNI: "00000001"})
```

Imports: `github.com/DataScienceResearchPeru/peru-sdk/sdk-go/reniec` y `.../sunat`. Se puede consumir el módulo desde Git; todavía no hay versión estable. Fijar un commit para reproducibilidad.

### Python

```python
from peru_sdk.reniec import Identity, IdentityQuery, MockIdentityService

service = MockIdentityService([
    Identity("00000001", "PERSONA", "PRUEBA", "SINTETICA"),
])
person = service.lookup(IdentityQuery("00000001"))
```

## Cliente SUNAT

El cliente implementa Consulta Integrada, no emisión de comprobantes. El RUC de la ruta es el de quien consulta; el RUC del cuerpo es el del emisor. La autenticación es `client_credentials`, no la Clave SOL ni el flujo de SIRE/GRE.

Ejemplo Python para una integración que ya tenga sus datos y credenciales autorizadas:

```python
from peru_sdk.sunat import OAuth2TokenProvider, ValidityClient, ValidityQuery

# client_id, client_secret y requester_ruc los proporciona tu aplicación.
tokens = OAuth2TokenProvider(client_id, client_secret)
client = ValidityClient(requester_ruc, tokens)
query = ValidityQuery(
    issuer_ruc=issuer_ruc,
    document_type="01",
    series="F001",
    number=123,
    issued_on="2026-11-02",
    amount="118.00",
)
# Esta llamada sí utiliza la red y los endpoints SUNAT de producción.
result = client.check(query)
```

En Go se usan `sunat.NewOAuth2TokenSource`, `sunat.NewValidityClient` y `client.Check(ctx, query)`. También hay proveedores de token estático. No se leen secretos automáticamente del entorno ni se escriben logs.

`document_status` conserva el código de SUNAT, incluso si es desconocido. El código `0` significa comprobante no informado según el manual: **no es un error de transporte ni una aceptación**. Un resultado tampoco determina deducibilidad tributaria.

Los importes públicos son strings decimales. Se transmiten como números JSON exactos, sin conversión a `float`. Las fechas públicas usan `YYYY-MM-DD` y se convierten a `dd/mm/yyyy` para esta operación.

Por defecto: timeout HTTP de 10 segundos, respuesta limitada a 1 MiB, TLS normal y sin redirecciones ni reintentos automáticos. HTTP sin TLS solo se permite en direcciones IP de loopback para pruebas. Go admite cancelación con `context.Context`; Python ofrece timeout por operación HTTP, sin cliente async en esta etapa. Se preservan códigos desconocidos y se ignoran campos adicionales de respuestas compatibles.

## Contratos y generación

```text
contracts/        Modelos públicos y procedencia de fuentes
conformance/      Casos sintéticos compartidos
tools/            Generador, comprobaciones y vigilancia de fuentes
sdk-go/           Implementación Go
sdk-python/       Implementación Python
examples/         Ejemplos locales
```

El generador soporta un subconjunto explícito de JSON Schema: objetos cerrados con campos obligatorios, strings, patrones compatibles con ambos lenguajes, fechas, enteros acotados y arrays de strings. Rechaza keywords no soportadas. No es un generador universal ni genera la lógica HTTP, fiscal o criptográfica.

```bash
python3 tools/generate.py
python3 tools/generate.py --check
```

La segunda orden falla si un modelo difiere del contrato. Los archivos generados se versionan y no se editan manualmente.

## Pruebas y CI/CD

```bash
go -C sdk-go test -race ./...
python3 -m unittest discover -s sdk-python/tests -v
python3 -m pip install -r tools/requirements.txt
python3 tools/check_contracts.py
python3 tools/check_packages.py
```

La suite Python requiere instalar primero `./sdk-python`. Las únicas dependencias adicionales de validación son de desarrollo. `check_packages.py` construye e instala una wheel en un destino aislado, ejecuta sus pruebas fuera del repositorio y compila un consumidor Go externo. Los temporales se crean en subdirectorios únicos de `/var/tmp`.

En cada push/PR, CI comprueba contratos, generación, ambos SDKs, condiciones de error y consumo del paquete instalado. Incluye Go mínimo/actual, race detector, Go sin cgo y Python 3.11/3.14 en Linux y Windows. Los tests HTTP solo acceden a loopback; las instalaciones de herramientas sí requieren acceso a sus registros.

El workflow manual **Build preview distributions** produce wheel, sdist, código fuente y hashes como artefactos de GitHub. No publica automáticamente en PyPI ni crea versiones estables. Para Go, una futura versión del módulo ubicado en `sdk-go/` requiere una etiqueta como `sdk-go/v0.1.0`.

El workflow semanal **Official source watch** compara el hash del PDF oficial accesible: salida 0 sin cambios, 1 documento cambiado y 2 fuente inaccesible. Es una señal separada de las regresiones del SDK. No modifica reglas ni demuestra que el documento vigilado sea el más reciente.

## Fuentes, límites y próximos pasos

La procedencia y las limitaciones están en [docs/compatibility.md](docs/compatibility.md); las decisiones en [docs/architecture.md](docs/architecture.md).

Próximos pasos: contrastar el cliente SUNAT con una consulta real autorizada; obtener el contrato y acceso correspondiente de RENIEC; ampliar pruebas de compatibilidad; incorporar una factura UBL acotada con verificación independiente de firma. La publicación estable y las credenciales de registros se configurarán después de comprobar esos hitos.

Este proyecto no está afiliado a SUNAT ni a RENIEC.
