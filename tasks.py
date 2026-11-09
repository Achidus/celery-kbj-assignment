import time
from celery_app import app

@app.task(bind=True, name="tasks.process_short")
def process_short(self, payload):
    """Padanan aplikasi UTS SHORT: pekerjaan ringan."""
    started = time.time()
    message = str(payload.get("message", ""))
    # Simulasi proses ringan, bukan beban komputasi riil.
    result = {
        "task_id": self.request.id,
        "application": "SHORT",
        "worker": self.request.hostname,
        "input": message,
        "output": message.upper(),
        "processing_seconds": round(time.time() - started, 6),
        "status": "SUCCESS",
    }
    print(f"[SHORT] {result}", flush=True)
    return result


@app.task(bind=True, name="tasks.process_long")
def process_long(self, payload):
    """Padanan aplikasi UTS LONG: pekerjaan lebih berat."""
    started = time.time()
    message = str(payload.get("message", ""))
    delay = float(payload.get("delay", 3))
    time.sleep(max(0, min(delay, 30)))
    result = {
        "task_id": self.request.id,
        "application": "LONG",
        "worker": self.request.hostname,
        "input": message,
        "output": message[::-1],
        "processing_seconds": round(time.time() - started, 6),
        "status": "SUCCESS",
    }
    print(f"[LONG] {result}", flush=True)
    return result
