import argparse
import time
from kombu import Connection, Exchange, Queue, Consumer

BROKER = "amqp://guest:guest@localhost:5672//"

def build_queues():
    fanout = Exchange("demo_fanout", type="fanout", durable=True)
    topic = Exchange("demo_topic", type="topic", durable=True)

    return [
        Queue("fanout_queue_a", exchange=fanout, routing_key=""),
        Queue("fanout_queue_b", exchange=fanout, routing_key=""),
        Queue("topic_queue_order", exchange=topic, routing_key="order.*"),
        Queue("topic_queue_payment", exchange=topic, routing_key="payment.*"),
        Queue("wildcard_one_segment", exchange=topic, routing_key="sensor.*"),
        Queue("wildcard_many_segments", exchange=topic, routing_key="sensor.#"),
    ]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=120)
    args = parser.parse_args()

    with Connection(BROKER) as connection:
        channel = connection.channel()
        consumers = []

        for queue in build_queues():
            def make_callback(name):
                def callback(body, message):
                    print("\n" + "=" * 55)
                    print("PESAN DITERIMA")
                    print(f"Queue       : {name}")
                    print(f"Routing Key : {message.delivery_info.get('routing_key')}")
                    print(f"Message     : {body}")
                    print("=" * 55, flush=True)
                    message.ack()
                return callback

            consumer = Consumer(
                channel,
                queues=[queue],
                callbacks=[make_callback(queue.name)],
                accept=["json"]
            )
            consumer.consume()
            consumers.append(consumer)

        print("\n=== CONSUMER FAN-OUT, TOPIC & WILDCARD AKTIF ===")
        print("Menunggu pesan dari Producer...\n")

        deadline = time.time() + args.duration

        while time.time() < deadline:
            try:
                connection.drain_events(timeout=1)
            except TimeoutError:
                pass

        for consumer in consumers:
            consumer.cancel()

if __name__ == "__main__":
    main()
