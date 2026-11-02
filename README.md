# CodeFactoryAI.Infrastructure

Arranque completo de desarrollo, exclusivamente Fase 1. [Guía y diagnóstico](docs/local-development.md) · [Evidencias reales](docs/evidence/local-environment.json).

Desde la raíz conjunta CodeFactoryAI:

```powershell
python CodeFactoryAI.Infrastructure/scripts/environment.py up
```

Deja Angular, API, PostgreSQL y RabbitMQ activos en Docker y espera sus comprobaciones de salud. migrate aplica la migración y termina con código 0. No requiere herramientas globales Node/.NET.

- Frontend: http://127.0.0.1:4200/factory
- API: http://127.0.0.1:5240/api/v1/system-health
- Readiness SQL/AMQP: http://127.0.0.1:5240/health/ready
- RabbitMQ management: http://127.0.0.1:15682

```powershell
python CodeFactoryAI.Infrastructure/scripts/environment.py status
python CodeFactoryAI.Infrastructure/scripts/environment.py logs
python CodeFactoryAI.Infrastructure/scripts/environment.py check
python CodeFactoryAI.Infrastructure/scripts/environment.py restart
python CodeFactoryAI.Infrastructure/scripts/environment.py stop
```

Modo host con ng serve y dotnet watch, más PostgreSQL/RabbitMQ en Docker:

```powershell
python CodeFactoryAI.Infrastructure/scripts/environment.py up --mode host
```

Usa las herramientas portables ya preparadas; si faltan, ejecutar explícitamente scripts/setup_foundation.py. dev.py ui/api sigue disponible para terminales de primer plano; mantenerlas abiertas. El comando gestionado registra procesos y logs y detecta puertos ajenos, sin matar procesos desconocidos. Los modos comparten URLs y cambian sin compartir node_modules/bin/obj entre sistemas.

.env contiene secretos locales ignorados en Git; no se incluyen en imágenes. Los volúmenes persisten al detener. No se monta Docker socket ni credenciales Codex. El runner permanece independiente y su ejecución bloqueada; environment.py no lo inicia. Fase 2/RSC no se han integrado.

[Informe Foundation original](docs/foundation-report.md) · [Instrucciones](AGENTS.md).
