"""Probe persistence by restarting only this Compose project's services."""

from pathlib import Path
import subprocess
from uuid import uuid4
import pika
import psycopg

root = Path(__file__).resolve().parents[1]
settings = dict(
    line.split("=", 1)
    for line in (root / ".env").read_text().splitlines()
    if line and not line.startswith("#")
)
compose = [
    "docker",
    "compose",
    "--env-file",
    str(root / ".env"),
    "-f",
    str(root / "compose.yaml"),
]
probe = uuid4().hex
with psycopg.connect(
    host="127.0.0.1",
    port=55432,
    dbname="codefactory",
    user="factory",
    password=settings["POSTGRES_PASSWORD"],
) as db:
    db.execute(
        "CREATE TABLE IF NOT EXISTS foundation_persistence_probe(id text PRIMARY KEY)"
    )
    db.execute("INSERT INTO foundation_persistence_probe VALUES (%s)", (probe,))
credentials = pika.PlainCredentials("factory", settings["RABBITMQ_PASSWORD"])


def rabbit():
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            "127.0.0.1",
            55672,
            credentials=credentials,
            connection_attempts=10,
            retry_delay=2,
        )
    )


queue = "foundation-persistence-" + probe
with rabbit() as connection:
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.confirm_delivery()
    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=probe.encode(),
        properties=pika.BasicProperties(delivery_mode=2),
        mandatory=True,
    )
subprocess.run(compose + ["restart"], check=True, timeout=90)
subprocess.run(
    compose + ["up", "-d", "--wait", "--wait-timeout", "120"], check=True, timeout=150
)
with psycopg.connect(
    host="127.0.0.1",
    port=55432,
    dbname="codefactory",
    user="factory",
    password=settings["POSTGRES_PASSWORD"],
) as db:
    assert db.execute(
        "SELECT id FROM foundation_persistence_probe WHERE id=%s", (probe,)
    ).fetchone() == (probe,)
    db.execute("DELETE FROM foundation_persistence_probe WHERE id=%s", (probe,))
with rabbit() as connection:
    channel = connection.channel()
    method, _, body = channel.basic_get(queue=queue, auto_ack=False)
    assert method is not None and body == probe.encode()
    channel.basic_ack(method.delivery_tag)
    channel.queue_delete(queue=queue)
print(
    "PASS: committed PostgreSQL data and persistent RabbitMQ message survived restart"
)
