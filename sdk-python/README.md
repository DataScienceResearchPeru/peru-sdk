# Peru SDK para Python

Prueba mínima nativa, Python 3.11+, sin dependencias de runtime de terceros. Incluye Consulta Integrada SUNAT y un proveedor de identidad exclusivamente sintético. No implementa emisión, firma ni un cliente oficial RENIEC.

Instalar desde el checkout con `python3 -m pip install ./sdk-python`. El nombre declarado del paquete no implica publicación en PyPI. La versión inicial es `0.1.0.dev0`.

```python
from peru_sdk.reniec import Identity, IdentityQuery, MockIdentityService

service = MockIdentityService([
    Identity("00000001", "PERSONA", "PRUEBA", "SINTETICA"),
])
print(service.lookup(IdentityQuery("00000001")))
```

Para SUNAT: `peru_sdk.sunat.ValidityClient`, `ValidityQuery`, `StaticToken` y `OAuth2TokenProvider`. La consulta usa `client_credentials`; los importes se expresan como strings decimales exactos. Se puede comprobar una respuesta sintética sin red con `parse_validity_response`.

Una llamada a `ValidityClient.check` sí puede consultar SUNAT; el comportamiento real todavía no ha sido verificado con credenciales autorizadas. El proveedor simulado de identidad nunca accede a la red.

Errores institucionales y de protocolo: `peru_sdk.errors.SDKError`, con `kind`, `operation`, `status` y `code`. Entrada inválida: `ValueError`. Las representaciones de proveedores de token ocultan los secretos; no se formatean cuerpos remotos en las excepciones públicas.

La documentación, contratos y pruebas de conformidad están en el [repositorio](https://github.com/DataScienceResearchPeru/peru-sdk). Licencia MIT.
