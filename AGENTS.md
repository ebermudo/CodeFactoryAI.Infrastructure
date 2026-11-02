# Instrucciones para CodeFactoryAI.Infrastructure

## Alcance y autorización

Trabajar exclusivamente en este repositorio y en sus tres hermanos autorizados dentro de Desktop/CodeFactoryAI. Verificar git rev-parse --show-toplevel, git remote -v y git status antes de cada fase. No crear repositorios, monorepo ni submódulos; no cambiar remotos ni realizar push. No tocar la copia Angular fuera de esta raíz.

El usuario aprobó Fase 1 y autorizó Fase 2 — Brain & Persistent Knowledge completa. No avanzar a Fase 3, ejecutar agentes autónomos ni instalar/ejecutar onboarding RSC. Sólo análisis y plan RSC separado. Mantener runner independiente y bloqueado. No instalar herramientas globales sin autorización. Escritura/promoción oficiales sólo en API con validación y aprobación humana; Python selecciona contexto mediante puertos. Git y PostgreSQL deben ser recuperables, snapshots inmutables y proyectos aislados. Commits locales por hitos; no push.

## Ingeniería

DDD, CQRS, Clean Architecture; una clase pública principal por fichero. Controladores y rutas sin negocio ni persistencia directa. Domain puro; Application define puertos; Infrastructure implementa adaptadores. Dependencias explícitas, cancelación y errores observables. Mantener contratos en API y consumir artefactos generados con versión y hash. No copiar definiciones manualmente.

Consultar documentación vigente antes de cambiar contratos. Actualizar ADR, evidencia y README al cambiar decisiones. No presentar mocks o planes como funciones reales. Tests automatizados con proveedores falsos identificados; la prueba Codex real exige ejecución explícita y controlada. No activar APIs facturadas.

## Seguridad y calidad

No leer ni copiar tokens de proveedores, no incluir secretos en Git, logs o Brain. Prohibido shell=True con prompts. Rutas autorizadas y worktrees exclusivos por desarrollador; un worktree no constituye aislamiento de seguridad. Evidencias reales y hallazgos verificables; aprobación crítica determinista. No desactivar controles para aprobar pruebas.

Antes de cerrar cada hito: comprobar diff, contratos, pruebas pertinentes y documentar límites; crear commit local coherente sin incluir cambios ajenos.

## Diseño de referencia

Leer [diseño](docs/phase-0.md) y [plan conjunto](../CodeFactoryAI.Infrastructure/docs/phase-0.md). Infraestructura coordina arranque y compatibilidad sin copiar código entre repositorios. Servicios ligados a loopback; nunca montar Docker socket en agentes.
