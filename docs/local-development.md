# Entorno local corregido · Fase 1

## Diagnóstico comprobado

Antes de la corrección no existían listeners en 4200/5240 y Compose sólo contenía PostgreSQL/RabbitMQ. Al reproducir dev.py ui, Angular compiló y respondió HTTP 200: sus rutas, Node portable y dependencias estaban disponibles. Es un comando de primer plano, no un servicio persistente; debe mantenerse abierta su terminal. No había logs históricos que permitieran atribuir el cierre anterior a una excepción concreta. Faltaban el arranque conjunto, los servicios web Compose, el proxy y readiness real de la API.

Ahora environment.py administra arranque, salud y diagnósticos; no cambia la política global PowerShell. Las rutas se resuelven desde el script, sin depender del directorio de trabajo. Los cuatro repositorios mantienen sus raíces y remotos originales.

## Un comando de arranque

Desde la raíz conjunta CodeFactoryAI:

```powershell
python CodeFactoryAI.Infrastructure/scripts/environment.py up
```

Requiere Python 3.12, Git y Docker Desktop con contenedores Linux. Construye las imágenes, crea .env aleatorio si falta y espera dependencias y salud. No necesita Node/.NET globales. El primer build descarga imágenes/dependencias; los siguientes usan caché. Finaliza con URLs y deja los servicios desacoplados en Docker. No instala ni inicia el runner.

| Servicio | Dirección local |
|---|---|
| Angular | http://127.0.0.1:4200/factory |
| API · estado de Foundation | http://127.0.0.1:5240/api/v1/system-health |
| API · readiness SQL/AMQP | http://127.0.0.1:5240/health/ready |
| API · liveness de proceso | http://127.0.0.1:5240/health/live |
| RabbitMQ management | http://127.0.0.1:15682 |
| PostgreSQL | 127.0.0.1:55432 |
| RabbitMQ AMQP | 127.0.0.1:55672 |

api y client aparecen en Docker Desktop junto a postgres y rabbitmq. migrate es un servicio puntual que aplica migraciones y termina con código 0; no debe permanecer ejecutándose. La API no ofrece Swagger UI ni login todavía; usar los endpoints de salud anteriores para verificarla. /api/v1/projects devuelve 401 mientras no exista identidad de usuario.

## Detener, reiniciar y diagnosticar

```powershell
python CodeFactoryAI.Infrastructure/scripts/environment.py status
python CodeFactoryAI.Infrastructure/scripts/environment.py check
python CodeFactoryAI.Infrastructure/scripts/environment.py logs
python CodeFactoryAI.Infrastructure/scripts/environment.py restart
python CodeFactoryAI.Infrastructure/scripts/environment.py stop
```

stop conserva volúmenes y sólo detiene servicios de este Compose y procesos host registrados. No usar down -v para una parada normal. status incluye puertos y procesos administrados. check acredita frontend, proxy, API, SQL, AMQP y CORS. logs recoge salida Docker o logs host. Ante un puerto ajeno ocupado se aborta con un mensaje: no se mata un proceso desconocido. Si Docker Desktop no está arrancado o no usa Linux, se informa del error.

Equivalente manual Docker (rutas relativas a Infrastructure): docker compose --env-file .env -f compose.yaml up -d --build --wait --wait-timeout 240. El comando Python añade las comprobaciones HTTP y de proxy.

## Desarrollo en el host

```powershell
python CodeFactoryAI.Infrastructure/scripts/environment.py up --mode host
```

Arranca PostgreSQL/RabbitMQ en Docker, detiene los web containers propios para liberar puertos, aplica migraciones y lanza Angular y dotnet watch como procesos Windows ocultos/desacoplados con logs. Usa las herramientas portables ya preparadas en Infrastructure/.tools. Si faltan, ejecutar explícitamente scripts/setup_foundation.py; no instala herramientas globales. No se comparte node_modules ni bin/obj entre Windows y Linux.

Para volver a todos los servicios en Docker: environment.py up. Se detienen únicamente los árboles de procesos registrados, comprobando PID y fecha de creación para evitar terminar un PID reutilizado. El modo host desacoplado está implementado para Windows.

También se conserva el modo manual de primer plano, en terminales separadas (no mezclar con un entorno que ya ocupa esos puertos):

```powershell
python CodeFactoryAI.Infrastructure/scripts/dev.py api
python CodeFactoryAI.Infrastructure/scripts/dev.py ui
```

Mantener abiertas esas terminales; Ctrl+C detiene el servicio. API usa dotnet watch por defecto; --no-watch permite dotnet run. Angular usa ng serve. Los logs del modo gestionado están en Infrastructure/artifacts/local/environment/{api,ui,migrations}.log. En Docker, Angular sincroniza src mediante bind mount de sólo lectura y polling; para cambios del backend se reconstruye con environment.py up. La recarga en caliente de ambos módulos está validada en modo host.

## Configuración y límites

- Dockerfiles y .dockerignore viven en API y ClientAngular. Compose sólo en Infrastructure, con contextos relativos. Imágenes base fijadas por digest; servicios web sin root, sin modo privilegiado ni socket Docker.
- .env local sigue ignorado. No se pasan secretos como build args ni se incluyen en contextos de construcción. API recibe sólo conexión PostgreSQL/RabbitMQ; frontend recibe sólo CODEFACTORY_API_TARGET. No se inyectan credenciales de Codex ni RUNNER_SERVICE_TOKEN a contenedores.
- proxy.conf.cjs envía /api/**, /health/** y /openapi/** al backend. Host: http://127.0.0.1:5240; Docker: http://api:8080. El navegador mantiene el mismo origen. No cambiar ese destino por localhost dentro del contenedor.
- CORS sólo se habilita en Development y permite los orígenes explícitos 127.0.0.1:4200 y localhost:4200, sin wildcard. Los orígenes externos no reciben permiso CORS. Autorización y cookie Secure permanecen intactas.
- Liveness no depende de infraestructura. Readiness ejecuta SELECT 1 real y abre conexión/canal AMQP con credenciales; devuelve 200/503 con estados sanitizados, nunca connection strings. Health checks de Compose usan readiness y dependencias ordenadas.
- El administrador local factory sigue limitado al entorno Foundation. El login de usuario y separación de cuentas de aplicación/migración continúan pendientes de sus hitos. Esta corrección no habilita ejecuciones de agentes.

## Pruebas y evidencias

```powershell
python CodeFactoryAI.Infrastructure/scripts/validate_environment.py
python CodeFactoryAI.Infrastructure/scripts/inspect_environment.py
python CodeFactoryAI.Infrastructure/scripts/validate_foundation.py
```

validate_environment provoca caídas controladas de los servicios de este proyecto, comprueba readiness 503/liveness 200/proxy 503, arranca cada dependencia y reinicia los cuatro servicios. No ejecutar esa prueba simultáneamente con otras pruebas HTTP que requieran disponibilidad continua. inspect_environment guarda sólo datos sanitizados de contenedores y acredita ausencia de Codex/credenciales del runner y ejecución sin root.

Tras arrancar modo host: scripts/validate_hot_reload.py verifica cambios temporales por HTTP y restaura siempre los bytes originales. La prueba se ejecutó y pasó para Angular y dotnet watch. No deja cambios de prueba en Git.

Para Chromium contra el entorno activo y Node portable: `python CodeFactoryAI.Infrastructure/scripts/run_environment_browser.py`. Desde ClientAngular, con herramientas en PATH, también funciona `npx playwright test --config playwright.environment.config.ts`. Los E2E de regresión generales usan 4210, para no competir con el 4200 de desarrollo. El arranque de workers de Vitest se corrigió mediante el parche upstream 4.0.18; no se omiten pruebas ni se modifican dependencias instaladas a mano. El verificador de Foundation usa salida UTF-8 para conservar errores completos en Windows.

Evidencia versionada: [local-environment.json](evidence/local-environment.json). Logs detallados y resultados TRX/JUnit permanecen en artifacts/local/validation y artifacts/local/environment, ignorados. La validación final conserva las 16 comprobaciones de Foundation aprobadas, ahora con 11 tests .NET, además de la prueba Chromium del proxy real. RSC/Fase 2 no se han iniciado; el runner permanece independiente y desactivado.
