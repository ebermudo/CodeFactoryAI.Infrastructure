# Infraestructura local propuesta

## Topología inicial

Docker Compose sólo para PostgreSQL y RabbitMQ. API .NET, Angular dev server, APIs/workers Python y runner arrancan como procesos host. Esto utiliza login Codex del host sin montar credenciales en Docker ni abrir runner hacia contenedores. Compose futuro podrá contener otros servicios tras decisión explícita.

Puertos propuestos, verificar colisiones: API HTTPS 7240, Angular 4200, agentes 8101-8107, runner 8190, PostgreSQL 5432, RabbitMQ AMQP 5672/management 15672. Bind host 127.0.0.1, red interna Docker, credenciales únicas y usuarios por servicio. TLS para API, orígenes/proxy definidos; servicios locales internos con identidad de servicio, migración a TLS mutuo si salen de loopback. Sin guest compartido, puertos públicos ni Docker socket en agentes.

```text
docker/
postgres/{init,backup}
rabbitmq/{definitions,policies}
scripts/{Test-Prerequisites,Start-Local,Stop-Local,Test-Local,Backup-Local,Restore-Local}.ps1
environments/
docs/
knowledge/global/
compose.yaml
.env.example
AGENTS.md
README.md
```

No crear esos servicios todavía. Configuración futura usa ../CodeFactoryAI.API, ../CodeFactoryAI.ClientAngular y ../CodeFactoryAI.Agents; PSScriptRoot para resolver rutas, no depender del cwd. Validar git roots/remotos al arrancar. .env local ignorado, ejemplo sólo nombres/valores ficticios, secretos fuera de comandos/logs. Volúmenes PostgreSQL/RabbitMQ persistentes; artefactos con ACL y backups separados. No borrar volúmenes al detener.

Start-Local: validar herramientas/versiones/contratos y puertos; docker compose config; iniciar dependencias y esperar health real con timeout; migración EF explícita serializada; iniciar API, workers y UI registrando PID/fecha/hash de ejecutable; readiness de cada uno antes de anunciar listo. Rollback de arranque detiene sólo procesos iniciados por el script. Start-Process -WindowStyle Hidden. Stop valida identidad de procesos y detiene con gracia; no mata procesos ajenos por coincidencia de nombre.

Observabilidad mínima: logs JSON redaccionados con correlationId, health checks liveness/readiness, métricas de cola/DLQ/outbox/leases y contador de fallos. No instalar stack de métricas pesado hasta necesidad. Logs persistentes con rotación y protección de datos.

Pruebas: validación estática Compose, checks de exposición loopback y configuración sin secretos, arranque real, reconexión broker, reinicio API/worker y persistencia de datos, backup/restore con hashes de artefactos. No se han ejecutado todavía. Versiones exactas e imágenes por digest se fijarán tras aprobación y verificación; no instalar nada automáticamente durante auditoría.
