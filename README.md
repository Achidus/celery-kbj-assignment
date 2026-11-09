# Implementasi Job Queue dengan Celery — Tugas KBJ

Proyek ini mengadaptasi program UTS client–broker–worker (aplikasi `SHORT` dan `LONG`) menjadi sistem asynchronous job queue menggunakan Celery dan RabbitMQ. Program juga menyediakan demonstrasi message handling Fan-Out, Topic, dan Wildcard.

## 1. Arsitektur

- **Producer** (`producer.py`): pembangkit data masukan otomatis.
- **Broker** (RabbitMQ): menerima pesan dan menempatkannya ke queue.
- **Celery Worker**: mengambil serta menjalankan task.
- **Result Backend** (`rpc://`): mengirimkan hasil task kembali ke pemanggil.
- **Flower**: dashboard monitoring worker dan task.

Alur task UTS:
- `SHORT` → `short_queue` → `tasks.process_short`
- `LONG` → `long_queue` → `tasks.process_long`

Routing memakai exchange bertipe `topic` bernama `uts_jobs`.

## 2. Persiapan

Disarankan Python 3.10 atau lebih baru.

```bash
python3 -m venv myvenv
source myvenv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Salin `.env.example` menjadi `.env` bila ingin mengubah konfigurasi broker. Konfigurasi default menggunakan RabbitMQ lokal dengan user/password `guest`.

## 3. Menjalankan RabbitMQ

Dengan Docker:

```bash
docker compose up -d
docker compose ps
```

RabbitMQ Management: http://localhost:15672  
Username: `guest`  
Password: `guest`

Port AMQP: `5672`.

## 4. Menjalankan program Celery (adaptasi UTS)

Buka beberapa terminal dari folder proyek dan aktifkan virtual environment pada masing-masing terminal.

**Terminal 1 — Worker untuk task SHORT:**

```bash
celery -A celery_app.app worker --loglevel=INFO --queues=short_queue --hostname=short@%h
```

**Terminal 2 — Worker untuk task LONG:**

```bash
celery -A celery_app.app worker --loglevel=INFO --queues=long_queue --concurrency=2 --hostname=long@%h
```

**Terminal 3 — Producer / input generator:**

```bash
python producer.py --count 10 --interval 0.5 --mode MIXED
```

Contoh pilihan:
```bash
python producer.py --count 5 --mode SHORT
python producer.py --count 5 --mode LONG
python producer.py --count 5 --mode MIXED --wait
```

`--wait` membuat producer menunggu hasil setiap task. Tanpa opsi itu, producer hanya mengirim pesan dan mencetak ID task.

## 5. Monitoring dengan Flower

**Terminal 4:**

```bash
celery -A celery_app.app flower --port=5555
```

Buka http://localhost:5555 untuk melihat worker, task aktif, task berhasil/gagal, dan statistik pemrosesan.

## 6. Uji Fan-Out, Topic, dan Wildcard

Jalankan consumer terlebih dahulu.

**Terminal 1 — Consumer:**
```bash
python routing_consumer.py --duration 120
```

**Terminal 2 — Producer demonstrasi:**
```bash
python routing_producer.py
```

Hasil yang diharapkan:

| Skema | Exchange / binding | Perilaku |
|---|---|---|
| Fan-Out | `demo_fanout` bertipe `fanout` | Semua pesan disalin ke seluruh queue yang terikat; routing key diabaikan. |
| Topic | `demo_topic`, misalnya `order.*` dan `payment.*` | Pesan diarahkan berdasarkan pola routing key. |
| Wildcard `*` | `sensor.*` | Cocok dengan tepat satu segmen setelah `sensor`, misalnya `sensor.temperature`. |
| Wildcard `#` | `sensor.#` | Cocok dengan nol atau lebih segmen setelah `sensor`, misalnya `sensor.temperature` dan `sensor.room.temperature.high`. |

Catatan: Pada RabbitMQ topic exchange, `*` berarti tepat satu kata/segmen dan `#` berarti nol atau lebih kata/segmen. Keduanya dipisahkan oleh titik (`.`).

## 7. Ringkasan perbedaan

1. **Fan-Out** digunakan ketika satu pesan harus diterima oleh semua queue penerima, tanpa seleksi routing key.
2. **Topic** digunakan ketika pesan harus diteruskan ke queue sesuai topik atau kategori routing key.
3. **Wildcard** merupakan pola binding pada topic exchange. Simbol `*` membatasi satu segmen, sedangkan `#` dapat mencakup beberapa segmen.

## 8. Bukti pengujian yang perlu dimasukkan ke laporan

Ambil screenshot:
1. RabbitMQ Management yang menunjukkan exchange dan queue.
2. Terminal worker `short_queue`.
3. Terminal worker `long_queue`.
4. Terminal producer saat mengirim beberapa task.
5. Flower yang menunjukkan worker online dan task berhasil.
6. Terminal consumer saat menerima pesan Fan-Out, Topic, dan Wildcard.

Jangan menuliskan hasil pengujian seolah-olah sudah dilakukan sebelum menjalankan program. Masukkan screenshot dan hasil aktual dari komputer masing-masing.

## 9. Struktur proyek

```text
celery_kbj_assignment/
├── celery_app.py
├── tasks.py
├── producer.py
├── routing_consumer.py
├── routing_producer.py
├── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

## 10. Menghentikan layanan

```bash
docker compose down
```

Untuk menghapus data RabbitMQ juga (opsional):
```bash
docker compose down -v
```

Perintah kedua menghapus volume data RabbitMQ.
