# utils/kafka_producer.py
import os
import json
import threading
from kafka import KafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_SERVERS", "localhost:9092").split(",")
KAFKA_TOPIC = "user-activity"

_producer = None
_lock = threading.Lock()

def _get_producer():
    """Thread-safe lazy initialization for the Kafka Producer connection."""
    global _producer
    if _producer is None:
        with _lock:
            if _producer is None:
                try:
                    _producer = KafkaProducer(
                        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                        # High availability settings
                        acks=1,
                        retries=3
                    )
                except Exception as e:
                    print(f"[Warning] Could not initialize Kafka Producer: {e}")
                    _producer = False # Sentinel to prevent infinite reconnect attempts
    return _producer

def send_activity_event(user_id: str, project_id: int, event_type: str):
    """
    Pushes an analytics or interaction event to Kafka asynchronously.
    """
    producer = _get_producer()
    if not producer:
        # Graceful degradation if Kafka cluster is offline
        return

    payload = {
        "user_id": user_id,
        "project_id": project_id,
        "event_type": event_type,
    }
    
    try:
        # kafka-python's send() is asynchronous by default and executes on an internal background thread pool
        producer.send(KAFKA_TOPIC, value=payload)
    except Exception as e:
        print(f"[Kafka Error] Failed to dispatch background event message: {e}")