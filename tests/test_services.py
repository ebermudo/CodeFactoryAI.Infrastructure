"""Real service integration; only test-owned queue is created/deleted."""

from pathlib import Path
from uuid import uuid4

import pika
import psycopg


def config() -> dict[str, str]:
    path = Path(__file__).parents[1] / ".env"
    return dict(
        line.split("=", 1)
        for line in path.read_text().splitlines()
        if line and not line.startswith("#")
    )


def test_postgres_transaction_round_trip() -> None:
    settings = config()
    with psycopg.connect(
        host="127.0.0.1",
        port=55432,
        dbname="codefactory",
        user="factory",
        password=settings["POSTGRES_PASSWORD"],
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE TEMP TABLE foundation_probe (id uuid PRIMARY KEY, payload text NOT NULL)"
            )
            value = uuid4()
            cursor.execute(
                "INSERT INTO foundation_probe VALUES (%s,%s)",
                (value, "real-persistence"),
            )
            cursor.execute("SELECT payload FROM foundation_probe WHERE id=%s", (value,))
            assert cursor.fetchone() == ("real-persistence",)
        connection.rollback()


def test_rabbitmq_persistent_publish_confirm_and_manual_ack() -> None:
    settings = config()
    credentials = pika.PlainCredentials("factory", settings["RABBITMQ_PASSWORD"])
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            "127.0.0.1", 55672, credentials=credentials, blocked_connection_timeout=10
        )
    )
    queue = "foundation-test-" + uuid4().hex
    try:
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)
        channel.confirm_delivery()
        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=b"foundation-contract-v1",
            properties=pika.BasicProperties(delivery_mode=2),
            mandatory=True,
        )
        method, properties, body = channel.basic_get(queue=queue, auto_ack=False)
        assert method is not None
        assert properties.delivery_mode == 2
        assert body == b"foundation-contract-v1"
        channel.basic_ack(delivery_tag=method.delivery_tag)
        assert (
            channel.queue_declare(queue=queue, passive=True).method.message_count == 0
        )
    finally:
        if connection.is_open:
            connection.channel().queue_delete(queue=queue)
            connection.close()
