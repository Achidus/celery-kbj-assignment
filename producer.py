import argparse
import random
import time
from celery_app import app
from tasks import process_short, process_long

def send_one(app_type, number, wait_result=False):
    payload = {
        "message": f"Data UTS nomor {number}",
        "delay": random.choice([2, 3, 4]),
        "sequence": number,
    }
    if app_type == "SHORT":
        async_result = process_short.delay(payload)
    else:
        async_result = process_long.delay(payload)

    print(
        f"[PRODUCER] #{number} jenis={app_type} "
        f"task_id={async_result.id} status=QUEUED",
        flush=True,
    )
    if wait_result:
        print(f"[RESULT] {async_result.get(timeout=60)}", flush=True)

def main():
    parser = argparse.ArgumentParser(description="Producer / input generator Celery")
    parser.add_argument("--count", type=int, default=10, help="Jumlah pesan")
    parser.add_argument("--interval", type=float, default=0.5, help="Jeda antar pesan")
    parser.add_argument(
        "--mode", choices=["MIXED", "SHORT", "LONG"], default="MIXED",
        help="Jenis beban yang dikirim"
    )
    parser.add_argument("--wait", action="store_true", help="Tunggu hasil setiap task")
    args = parser.parse_args()

    for number in range(1, args.count + 1):
        app_type = args.mode if args.mode != "MIXED" else random.choice(["SHORT", "LONG"])
        send_one(app_type, number, args.wait)
        time.sleep(max(0, args.interval))

if __name__ == "__main__":
    main()
