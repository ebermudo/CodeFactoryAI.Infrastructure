# Informe Fase 1 · Infrastructure y cierre conjunto

## Cambios y estructura

Infraestructura en compose.yaml con PostgreSQL 17 (imagen resuelta a 17.11) y RabbitMQ 4.3.6 management; ambas imágenes fijadas por digest. [Versionado PostgreSQL](https://www.postgresql.org/support/versioning/) y [ramas RabbitMQ](https://www.rabbitmq.com/release-information). Red Docker propia, volúmenes persistentes, health checks y bind exclusivo a loopback. Puertos: PostgreSQL 55432, AMQP 55672 y management 15682. Secretos aleatorios en .env ignorado; .env.example usa marcadores. El usuario factory es el administrador local de Foundation; separar credenciales de migración/aplicación antes de habilitar workloads de agentes.

Herramientas portables en .tools: .NET SDK 10.0.403, Node 24.22.2 y dotnet-ef 10.0.14; no se instalaron herramientas globales. toolchain.json conserva hashes oficiales de los archivos .NET/Node. scripts contiene bootstrap/setup, dev, validación, scripts PowerShell de inicio/parada y prueba de persistencia. La política PowerShell global permanece intacta; las rutas Python permiten operar sin cambiarla.

runner es paquete/proceso y entorno virtual independiente. ExecutionProvider define Execute/Cancel/Status/Result y detecciones de autenticación/cuota/disponibilidad para futuros adaptadores. Contratos generados desde API. La fábrica FastAPI exige token de servicio para solicitudes; devuelve 423 a ejecución autenticada y 401 sin identidad. No existe adaptador CLI ni permiso configurable para habilitar autonomía en Foundation. Las credenciales Codex del host nunca se leen ni se copian.

## Evidencias reales

scripts/validate_foundation.py terminó con 16 comprobaciones aprobadas, todas con exitCode=0. [Resumen con hashes](evidence/foundation-validation.json). Logs, TRX, JUnit XML y capturas permanecen locales e ignorados; los hashes del resumen permiten contrastarlos.

| Repositorio | Validación final |
|---|---|
| API | restore locked, build Release (0 warnings/0 errors), 10 xUnit, migración y repositorio PostgreSQL real, 27 fixtures .NET |
| Agents | 4 pytest, 27 fixtures Python, Ruff y mypy estricto |
| Infrastructure | 1 test de seguridad del runner, 2 integraciones reales PostgreSQL/RabbitMQ, Compose válido y prueba real de persistencia tras restart |
| Angular | build producción, tipos de contratos, 3 Vitest, 27 casos Ajv, 3 Playwright Chromium |

El test de persistencia verifica commit PostgreSQL y mensaje RabbitMQ durable/persistente con publisher confirm antes de reiniciar; después comprueba ambos y limpia únicamente sus propios datos/cola. No elimina volúmenes ni datos del usuario. Se verificó el estado saludable de ambos contenedores tras recreación y reinicio. Esto prueba persistencia de infraestructura, no recuperación de workflow todavía inexistente.

## Incidencias y correcciones

- Fuera de PATH/registro no se encontraron .NET/Node. Se descargaron archivos portables verificados por SHA-512/SHA-256 desde fuentes oficiales, dentro de Infrastructure.
- La revisión automática rechazó ng new --force por posible sobrescritura de documentación. Se crearon los archivos Angular individualmente.
- La política Windows bloqueó .ps1. No se cambió globalmente; setup/dev/validate Python resuelven la operación.
- Paquetes .NET iniciales presentaron vulnerabilidades transitivas y conflicto EF; actualizados/alineados sin desactivar controles.
- El round-trip C# detectó null en opcionales ausentes; generador corregido y tres ecosistemas validados después.
- RabbitMQ ping no garantizaba AMQP listo tras restart; health check reforzado y reconexión acotada en el probe. Prueba final aprobada.
- La revisión automática rechazó activar todos los feature flags del broker. Se omitió esa acción; la actualización de imágenes conservó volúmenes y pasó pruebas sin modificar flags.
- Permanecen avisos de deprecación Starlette/AnyIO y de colores Playwright; se registran, no se ocultan.

## Alcance pendiente y decisiones

No se ha iniciado Fase 2. Brain/RSC, workflow/outbox/inbox, workers, adaptadores físicos Codex/Claude, aislamiento y ejecución autónoma están pendientes. No se ejecutaron tareas Codex, aplicaciones generadas ni servicios de pago. No se ha hecho push. La prueba real de creación de aplicaciones pertenece a la Fase 7.

Foundation proporciona estructura, contratos y UI revisable; no acredita que la factoría esté operativa. Identidad de usuario final, guards/interceptors, privilegios de aplicación separados y futura conexión al workflow siguen pendientes de sus hitos autorizados. Los endpoints de proyectos están protegidos y las acciones de ejecución permanecen desactivadas.

Cada repositorio tiene un informe propio y un commit local de Foundation. El conjunto se identificará en delivery-foundation.json: referencia propia de Infrastructure por el commit que contiene el manifiesto, evitando autorreferencia imposible.
