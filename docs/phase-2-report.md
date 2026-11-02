# Fase 2 — Brain persistente: entrega y operación

La implementación abarca los cuatro repositorios independientes. No incluye Fase 3, ejecución autónoma ni instalación/onboarding RSC. Informes: [API](../../CodeFactoryAI.API/docs/phase-2-report.md), [Agents](../../CodeFactoryAI.Agents/docs/phase-2-report.md), [Angular](../../CodeFactoryAI.ClientAngular/docs/phase-2-report.md).

## Arquitectura y datos

API .NET es autoridad de escritura y revisión; PostgreSQL guarda metadatos y paquetes inmutables. El repositorio Git Infrastructure existente conserva commits oficiales en refs independientes por ámbito; no se modifica el HEAD/índice de trabajo para promover conocimiento. Python selecciona contexto por rol a través de puertos, y Angular consume endpoints reales. El Brain global y los proyectos son ámbitos distintos, incluidos el proyecto CodeFactoryAI y los proyectos de prueba.

Compose monta sólo el Git documental autorizado, metadatos de los cuatro repositorios registrados y estado local de claves/índices. PostgreSQL y RabbitMQ mantienen volúmenes persistentes. El contenedor migrate aplica EF Core, provisiona el operador inicial y los seeds, termina con código 0. El runtime API no recibe la contraseña bootstrap. Ni Codex ni sus credenciales se incorporan a contenedores.

## Arranque y diagnóstico

Desde C:\Users\ariad\Desktop\CodeFactoryAI:

~~~powershell
python CodeFactoryAI.Infrastructure/scripts/environment.py up
python CodeFactoryAI.Infrastructure/scripts/environment.py check
python CodeFactoryAI.Infrastructure/scripts/environment.py status
python CodeFactoryAI.Infrastructure/scripts/environment.py logs
python CodeFactoryAI.Infrastructure/scripts/environment.py restart
python CodeFactoryAI.Infrastructure/scripts/environment.py stop
~~~

Docker: Angular 4200, API 5240, Context Manager 8108, PostgreSQL 55432, RabbitMQ AMQP 55672 y management 15682, todos publicados en loopback. migrate es una tarea finalizada, no un servicio permanente.

Host con herramientas portables ya preparadas:

~~~powershell
python CodeFactoryAI.Infrastructure/scripts/environment.py up --mode host
~~~

Inicia ng serve, dotnet watch y Uvicorn reload como procesos supervisados y conserva PostgreSQL/RabbitMQ en Docker. Los contenedores api/client/context-manager quedan detenidos para evitar conflictos de puertos. Las terminales explícitas dev.py ui, dev.py api y dev.py context siguen disponibles. No se inicia el runner.

Frontend: http://127.0.0.1:4200/brain y /factory. API: http://127.0.0.1:5240/health/ready y /api/v1/system-health. Context Manager: http://127.0.0.1:8108/health/live. Usar 127.0.0.1 de forma consistente para cookies locales.

Usuario inicial operator; BRAIN_BOOTSTRAP_PASSWORD está sólo en .env ignorado. Leerlo localmente para login, sin copiarlo a documentación ni commits. Reejecutar provisión no cambia una contraseña existente. Estado/PIDs y logs: artifacts/local/environment. No matar procesos desconocidos si un puerto está ocupado.

## Backup y recuperación

En modo Docker, sin escritores host externos:

~~~powershell
CodeFactoryAI.Infrastructure/runner/.venv/Scripts/python.exe CodeFactoryAI.Infrastructure/scripts/backup_brain.py --verify-restore
~~~

Detiene temporalmente la API (única autoridad de escritura), hace pg_dump -Fc, git bundle --all y backup de claves Data Protection; firma un manifiesto SHA-256 y vuelve a arrancar/verificar API. Rechaza modo host para no producir un backup inconsistente dejando un escritor activo. Las pruebas concurrentes que escriben Git/DB deben estar detenidas durante backup.

--verify-restore crea una base PostgreSQL con identificador aleatorio dentro del servidor local existente, ejecuta pg_restore, verifica hashes de todas las revisiones/snapshots y comprueba recuperación de una ref desde bundle dentro de un namespace temporal del repositorio existente. Elimina sólo esa base/ref de prueba. No sobrescribe los datos activos ni crea repositorios adicionales.

Los backups contienen hashes de identidad y claves de sesión: son privados, ignorados y no se deben subir. Este procedimiento no es un backup de las colas RabbitMQ ni de los cuatro directorios de código. El outbox DB conserva el evento; recuperación de desastre con pérdida de broker requiere reconciliar entregas/deduplicación antes de reenvío. No hay procedimiento automático que sobrescriba producción.

Restauración operativa futura: detener todos los escritores, verificar manifiesto, conservar backup previo, restaurar dump en una base nueva, verificar bundle/objetos y refs oficiales contra punteros DB, recuperar claves bajo ACL local, configurar la nueva conexión y validar hashes/readiness antes de habilitar escrituras. No reemplazar HEAD ni purgar carpetas. La prueba realizada cubre restauración aislada; no simula pérdida total de la máquina.

## Pruebas y evidencias

Comando reproducible de la batería:

~~~powershell
python CodeFactoryAI.Infrastructure/scripts/validate_foundation.py
~~~

El nombre histórico se conserva; su informe identifica fase 2. Incluye contratos sin drift, restore bloqueado/build Release/xUnit, pytest Agents/runner, Ruff, mypy, Compose, integración/persistencia PostgreSQL y RabbitMQ, tipos/build/unidades/contratos Angular y Playwright estándar. Requiere servicios arrancados y dependencias locales ya preparadas.

E2E real adicional, desde CodeFactoryAI.ClientAngular con Node portable en PATH y PLAYWRIGHT_BROWSERS_PATH apuntando a Infrastructure/.tools/playwright:

~~~powershell
node node_modules/@playwright/test/cli.js test --config playwright.environment.config.ts brain
~~~

Registros completos ignorados: artifacts/local/validation/*.log, dotnet/foundation.trx, agents.xml, runner.xml, services.xml y summary.json. Evidencias de operación: artifacts/local/environment/checks.json, brain-restore.json y phase2-*-e2e.log; snapshot persistido en artifacts/local/brain-evidence/session.json. [Resumen versionado](evidence/phase-2-validation.json) conserva resultados y hashes sin credenciales. Capturas en ClientAngular/artifacts/local.

La prueba real de promoción interrumpida usa cinco puntos: intención reservada, candidato escrito antes de guardar su SHA, candidato preparado, ref publicada y finalización. Una nueva instancia de contexto retoma la intención; verifica revisión/outbox únicos y contenido Git. La prueba de navegador conserva paquete/hash después de reiniciar servicios. Outbox prueba fallo de conexión y posterior confirmación real, sin consumidores de ejecución.

## Decisiones, errores y límites

Se conservaron v1 y contratos runner; Brain usa v2. No embeddings ni pgvector. La búsqueda textual lee documentos Git verificados y aún no tiene índice de contenido PostgreSQL; medir volumen antes de optimizar. El presupuesto de contexto usa bytes UTF-8 como cota conservadora, no tokens exactos de un proveedor.

Durante el trabajo se corrigieron selector asíncrono, integración CSRF, propiedad de proyectos, generación/compatibilidad de contratos respuesta real al repetir registro de Brain, conflicto de alias y precondición de backup host. El formateo de artefactos generados produjo drift durante una prueba; se regeneraron desde esquemas y se volvió a verificar. Los fallos iniciales permanecen diferenciados de los resultados finales.

Sistema local de desarrollo: sin hardening multiusuario/producción, rotación administrada de claves, retención automática de backups o prueba de carga. Los montajes .git confían en el host. El filtro de secretos es heurístico. Las claves Data Protection están en almacenamiento local privado sin cifrado adicional de backup. Preservar refs y objetos Git; un push normal de master no sería copia del Brain, y no se ha hecho push.

RSC: [plan separado](../../CodeFactoryAI.Agents/docs/rsc-pilot-plan.md), candidato fijado sin instalar. Runner permanece bloqueado; no se invocó ningún proveedor de IA. Fase 3 requiere autorización explícita.

## Resultado de cierre verificado

Batería final: 16 comprobaciones aprobadas; 29 xUnit, 9 pytest Agents, 1 runner, 2 infraestructura, 3 Vitest, 57 fixtures Node y 3 Playwright estándar. E2E Brain adicional aprobado tanto en host como en Docker, incluyendo CSRF y límites de delegación. Backup final: 15 revisiones y 4 snapshots verificados en restauración aislada. Cinco contenedores saludables y migrate finalizado correctamente. Los logs conservan avisos de deprecación Python y de colores Node, sin convertirlos en fallos aprobados por omisión.

Commits de implementación: API 41f791b089a1dd759f17c3061c705e18fc033fa4, Agents c108bafe2197bef836d41a36c509895d4d586af2, Angular 2673052b205ac7dda285f876e4cb872199074f7b. El commit de Infrastructure contiene este informe y la evidencia versionada. El estado Git posterior se comprueba por separado para evitar un hash autorreferente.
