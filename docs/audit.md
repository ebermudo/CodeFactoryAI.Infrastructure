# Auditoría de Fase 0

Fecha: 2026-11-02, Europe/Madrid. Evidencias obtenidas en PowerShell en la sesión del asistente.

## Repositorios

La petición inicial señalaba Desktop/<repositorio>. No existen allí. El usuario confirmó Desktop/CodeFactoryAI/<repositorio>. Los cuatro git rev-parse --show-toplevel coinciden con esta raíz; git remote -v devuelve origin fetch/push HTTPS github.com/ebermudo/<nombre>.git en cada caso. git status --short vacío. Cada carpeta contenía únicamente .git y no existía AGENTS.md previo. git rev-parse --verify HEAD falla por ausencia de commits; rama inicial master. No es un fallo de integridad. git ls-remote --heads origin completó sin errores y sin devolver ramas en los cuatro repositorios. Esto confirma lectura remota y ausencia de ramas anunciadas, pero no permiso de push.

## Herramientas observadas

| Herramienta | Evidencia | Consecuencia |
|---|---|---|
| .NET | No localizado en PATH ni Program Files/dotnet/dotnet.exe | Instalar SDK 10 antes de compilar |
| Node / npm / ng | No localizados en PATH; node.exe tampoco en Program Files/nodejs | Instalar Node compatible y CLI local de Angular 22 |
| Python | 3.12.10 | Base propuesta; crear venv por repositorio en Fase 1 |
| pytest, Ruff, mypy, FastAPI, Pydantic, jsonschema | No importables por Python actual | No se han instalado ni ejecutado |
| Docker CLI / Engine | 29.9.2; docker info responde 29.9.2 y OSType linux | Motor accesible; no se han arrancado servicios |
| Docker Compose | v5.6.1 | Comando disponible; compose de producto aún inexistente |
| Git | 2.55.0.windows.3 | Identidad local disponible para commits |
| Codex | 0.164.0-alpha.11.1 | Binario incluido en extensión VS Code; no es instalación estable independiente |
| Autenticación Codex | codex login status: Logged in using ChatGPT | Sesión detectada; no prueba cuota, plan Plus ni inferencia efectiva |

El binario Codex está en la extensión openai.chatgpt-26.1021.22027-win32-x64. Su ruta cambiará al actualizar la extensión: resolver por configuración/descubrimiento y validar versión. codex exec --help confirma stdin, --json, --output-schema, --sandbox, --cd, --ignore-user-config y --ephemeral en este binario. No se ejecutó codex exec.

## Versiones propuestas y fuentes

- .NET 10: fijar parche de SDK compatible al comenzar Fase 1 en global.json. [Descargas oficiales](https://dotnet.microsoft.com/en-us/download/dotnet/10.0).
- Angular 22.0.x: Node ^22.22.3 o ^24.15.0 o ^26.0.0; TypeScript >=6.0.0 <6.1.0. Propuesta Node 24 compatible y RxJS 7 compatible, con versiones exactas en lockfile tras verificar registro. [Matriz oficial](https://angular.dev/reference/versions).
- Python 3.12, PostgreSQL 17 y RabbitMQ 4 como objetivos del diseño; parches, imágenes/digests y compatibilidad de drivers se verificarán antes de instalar. No se afirma que estas imágenes estén ya disponibles localmente.

No se han realizado pruebas funcionales, builds, análisis de vulnerabilidades ni E2E. La comprobación de documentación y contratos de esta entrega no acredita funcionamiento de la plataforma.
