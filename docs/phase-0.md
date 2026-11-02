# Entrega Fase 0 · CodeFactoryAI

Estado histórico: arquitectura aprobada y Fase 1 autorizada por el usuario el 2026-11-02. Foundation ya está validada; ver [informe actual](foundation-report.md). El resto de este documento conserva el plan inicial. Fase 2 fue autorizada y tiene [informe propio](phase-2-report.md). RSC y Fase 3 siguen sin autorización.

## Documentos de revisión

- [Auditoría y herramientas](audit.md)
- [Arquitectura .NET](../../CodeFactoryAI.API/docs/architecture.md), [modelo de datos](../../CodeFactoryAI.API/docs/data-model.md), [workflow](../../CodeFactoryAI.API/docs/workflow.md)
- [Contratos](../../CodeFactoryAI.API/docs/contracts.md) y borradores JSON Schema en API/docs/contracts-draft
- [Runner y agentes](../../CodeFactoryAI.Agents/docs/runtime-design.md), [Brain y RSC](../../CodeFactoryAI.Agents/docs/brain-integration.md)
- [Pantallas Angular y navegación](../../CodeFactoryAI.ClientAngular/docs/ux-design.md)
- [Arranque local](local-infrastructure.md), [ADRs](../../CodeFactoryAI.API/docs/adr/decisions.md)

## Hitos y criterios de salida

| Fase | Repositorios | Entregable y comprobación antes de continuar |
|---|---|---|
| 0 | los cuatro | rutas/remotos/estado y herramientas, diseños, contratos borrador, riesgos, commits de documentación; aprobación humana |
| 1 | los cuatro | SDK y Node compatibles, solución .NET y CQRS, Angular 22 shell con Workspace/Delivery vacíos reales, paquetes Python, Compose, contratos generados; builds, lint, tipos, tests básicos e integración DB/MQ |
| 2 | API, Agents, Infrastructure | Brain global/proyecto, snapshots y recuperación; promoción tras validación y recuperación de fallo Git/DB; RSC sólo tras plan exacto aceptado |
| 3 | Agents, API, Infrastructure | runner Windows y proveedor Codex, worktrees/ACL, timeout/cancelación; pruebas de escape y credenciales; no autonomía sin evidencia de aislamiento |
| 4 | API, Agents, Infrastructure | workflow durable, outbox/inbox, fencing, reintentos, DLQ, control humano; pruebas de crash/redelivery/reinicio |
| 5 | Agents, API | roles especializados y revisores, verifier y gate determinista; criterios y resultados verificables con proveedor falso |
| 6 | ClientAngular, API | Workspace y Delivery completos, proyectos, monitor, Brain, settings; integración real, Playwright, teclado/móvil y estados de fallo |
| 7 | los cuatro | app nueva real con backend/frontend/DB/auth/CRUD/tests/docs/reviews/informe, límites Codex explícitos; evidencia y aprobación humana antes de promoción Brain |

La UI tiene atención desde Fase 1: tokens/shell y componentes de Workspace/Delivery se validan antes de llenar otras pantallas. La Fase 6 completa integración y experiencia, no pospone todo el trabajo visual al final.

Antes de cada hito: identificar repos afectados, comprobar Git y dependencias, verificar versión/hash de contratos, planificar, implementar, probar, revisar capas, documentar y hacer commit local coherente. Toda fase conserva errores pendientes y evidencias; no continuar por mera existencia de archivos.

## Backlog inicial ordenado

| ID | Trabajo | Depende de | Evidencia esperada |
|---|---|---|---|
| FND-01 | preflight, fijación SDK/Node/Python e imágenes | aprobación Fase 1 | versiones, lockfiles y matriz reproducible |
| FND-02 | solución .NET, CQRS y tests de arquitectura | FND-01 | build/xUnit y referencias válidas |
| FND-03 | contratos v1 y generadores C#/Python/TS | FND-02 | fixtures positivas/negativas, diff cero |
| FND-04 | Compose, usuarios, health y backups | FND-01 | inicio/reinicio y restore verificable |
| UI-01 | tokens, shell, Workspace y Delivery componentes | FND-01 | revisión visual, teclado, responsive |
| SEC-01 | identidad local, antiforgery y permisos | FND-02 | 401/403/CSRF y recurso ajeno bloqueados |
| BRN-01 | Brain Git/DB y snapshots | FND-03/04 | hashes, selección/obsolescencia y recuperación |
| RSC-01 | piloto y plan exacto RSC | BRN-01, aprobación separada | diff y pruebas Windows/Codex |
| RUN-01 | puerto proveedor y runner sin acceso arbitrario | FND-03, SEC-01 | timeout/kill/ACL y estado durable |
| ORC-01 | workflow y outbox/inbox/fencing | BRN-01, RUN-01 | fallos inyectados y reinicio sin doble efecto |
| AGT-01 | todos los roles y políticas | ORC-01 | resultados tipados y findings verificables |
| UI-02 | datos reales y SignalR/replay | ORC-01, UI-01 | E2E creación, reconexión y cancelación |
| DEL-01 | gate y Delivery Review integrado | AGT-01, UI-02 | aprobación bloqueada y excepciones auditadas |
| REAL-01 | aplicación nueva completa controlada | anteriores | pruebas reales, informe, commits y Brain |

## Riesgos y decisiones pendientes

| Riesgo | Respuesta / condición |
|---|---|
| SDK/Node ausentes | instalar/fijar antes de Fase 1; no declarar compilaciones realizadas |
| Codex alfa ligado a VS Code | validar versión soportada y pruebas de contrato; no depender de ruta fija |
| Cuota/sesión de suscripción | autenticación detectada no garantiza cuota; una ejecución física inicial, bloqueo y reanudación manual |
| Código generado hostil | worktree no aísla; gate de sandbox/VM y QA sin credenciales |
| Hooks RSC cambian | fijar versión/SHA, piloto, respaldo; gate propio independiente |
| Fallo parcial Git/DB/broker | outbox/inbox y reconciliación, evidencias inmutables, fencing |
| UI muestra éxito sin evidencia | estados unknown/no ejecutado y aprobación del servidor |
| Incompatibilidad entre repos | manifest de hashes/commits, generación y fixtures cruzadas |
| Prompt prohíbe repos nuevos pero E2E crea app | acordar sandbox de aplicación dentro de repos autorizado o permiso explícito antes de REAL-01 |

Se propone usuario único local, cookie segura + Identity, Material/CDK compatible con Angular 22, dispatcher propio, PostgreSQL 17/RabbitMQ 4 y paralelismo físico inicial 1. Estas son decisiones de diseño para aprobar, no instalaciones realizadas. Pendientes para fases posteriores: política definitiva de retención, mecanismo de aislamiento validado, versión estable de CLI y plan RSC exacto.

## Prueba real de aceptación

Aplicación propuesta: gestor de tareas con usuarios, login, proyectos y CRUD de tareas; .NET 10, Angular 22 y PostgreSQL. Matriz ligada a requisitos: crear desde prompt, persistir ejecución, obtener Brain, distribuir RabbitMQ, invocar Codex, generar backend/frontend/auth/CRUD, ejecutar unit/integración/E2E, cuatro reviews/verificación, correcciones acotadas, revisión humana y promoción Brain. Interrumpir API/worker y recuperar ejecución. Adjuntar commit exacto, comandos, salidas, tiempos y artefactos; cobertura sólo si se mide. Prueba con proveedor falso no satisface REAL-01. No declarar plataforma completada antes de esta prueba.

## Aprobación solicitada al cierre

Aprobar o corregir este diseño y autorizar Fase 1. La integración RSC espera después un plan concreto de onboarding con archivos y hash; esta aprobación de arquitectura no lo sustituye. No hay solicitud de push ni de gasto API.
