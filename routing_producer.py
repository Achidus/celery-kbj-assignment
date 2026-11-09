"""Mengirim contoh pesan ke exchange Fan-Out dan Topic."""
from kombu import Connection, Exchange, Producer

BROKER = "amqp://guest:guest@localhost:5672//"

def main():
    fanout = Exchange("demo_fanout", type="fanout", durable=True)
    topic = Exchange("demo_topic", type="topic", durable=True)

    messages = [
        (fanout, "", {"scheme": "FAN-OUT", "message": "Pengumuman untuk semua queue"}),
        (topic, "order.created", {"scheme": "TOPIC", "message": "Pesanan dibuat"}),
        (topic, "payment.completed", {"scheme": "TOPIC", "message": "Pembayaran selesai"}),
        (topic, "sensor.temperature", {"scheme": "WILDCARD", "message": "Suhu terdeteksi"}),
        (topic, "sensor.room.temperature.high",
         {"scheme": "WILDCARD", "message": "Suhu ruangan tinggi"}),
        (topic, "inventory.stock.low",
         {"scheme": "WILDCARD", "message": "Stok rendah"}),
    ]

    with Connection(BROKER) as connection:
        producer = Producer(connection)
        for exchange, routing_key, body in messages:
            producer.publish(
                body,
                exchange=exchange,
                routing_key=routing_key,
                serializer="json",
                declare=[exchange],
                delivery_mode=2,
            )
            print(f"[SENT] exchange={exchange.name} key={routing_key or '(kosong)'} body={body}")
    print("Selesai mengirim demonstrasi Fan-Out, Topic, dan Wildcard.")

if __name__ == "__main__":
    main()
