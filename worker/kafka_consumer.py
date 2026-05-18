import os
import json
import redis
from kafka import KafkaConsumer

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")

def run_worker():
    r = redis.from_url(REDIS_URL, decode_responses=True)

    consumer = KafkaConsumer(
        'user-activity',
        bootstrap_servers=[KAFKA_BROKERS],
        group_id='analytics-group',
        value_serializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='latest'
    )

    print("👷 Background Python Worker running and streaming 'user-activity' channel...")

    for message in consumer:
        try:
            payload = message.value
            user_id = payload['userId']
            project_id = payload['projectId']
            timestamp = payload['timestamp']

            redis_key = f"user:history:{user_id}"

            # Execute an atomic pipeline to update score and cap the list to the last 20 elements
            pipe = r.pipeline()
            pipe.zadd(redis_key, {project_id: timestamp})
            pipe.zremrangebyrank(redis_key, 0, -21)
            pipe.execute()

            print(f"Processed interaction: User {user_id} -> Project {project_id}")

        except Exception as e:
            print(f"Error compiling incoming event instance step data: {e}")

if __name__ == '__main__':
    run_worker()