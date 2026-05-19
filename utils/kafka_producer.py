import os
import json
from kafka import KafkaProducer

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")

_producer = None

def get_kafka_producer():
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKERS],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
    return _producer

