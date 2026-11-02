# CodeFactoryAI.Infrastructure

Infraestructura local y runner independiente de Foundation. [Informe completo](docs/foundation-report.md) · [Evidencias](docs/evidence/foundation-validation.json) · [Plan inicial](docs/phase-0.md).

Desde la raíz conjunta, en PowerShell (sin cambiar políticas globales):

```text
python CodeFactoryAI.Infrastructure/scripts/setup_foundation.py
docker compose --env-file CodeFactoryAI.Infrastructure/.env -f CodeFactoryAI.Infrastructure/compose.yaml up -d --wait --wait-timeout 180
python CodeFactoryAI.Infrastructure/scripts/validate_foundation.py
python CodeFactoryAI.Infrastructure/scripts/dev.py ui
```

Setup descarga herramientas portables con hashes oficiales y dependencias locales; no instala herramientas globales. En la sesión actual ya están preparadas. .env contiene secretos locales y se ignora en Git. Setup conserva valores existentes y añade claves requeridas ausentes. No compartir .env. PostgreSQL/RabbitMQ usan volúmenes persistentes y sólo puertos loopback 55432/55672/15682. No ejecutar down -v para detener.

```text
docker compose --env-file CodeFactoryAI.Infrastructure/.env -f CodeFactoryAI.Infrastructure/compose.yaml stop
```

Para API: `python CodeFactoryAI.Infrastructure/scripts/dev.py api`. Para runner desactivado: `python CodeFactoryAI.Infrastructure/scripts/dev.py runner`; no lanza Codex y responde 423 a ejecución autenticada. Su paquete y venv residen en runner. Ejecución autónoma bloqueada hasta validación futura de aislamiento.

Scripts PowerShell equivalentes disponibles en scripts; si la política local los bloquea, usar las rutas Python anteriores sin alterar política global. Logs/JUnit/TRX en artifacts/local/validation. Cada repositorio sigue siendo independiente. [AGENTS](AGENTS.md).
