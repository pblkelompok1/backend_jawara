# Backend Jawara

Backend app for Jawara mobile TI3H Kelompok 1

## 📋 Prerequisites

Sebelum menjalankan aplikasi, pastikan sudah terinstall:

- **Python 3.8+**
- **PostgreSQL** (database utama)
- **Redis** (opsional, untuk rate limiting dan caching)

## 🚀 Cara Menjalankan Aplikasi

### 1. Clone Repository

```bash
git clone https://github.com/pblkelompok1/backend_jawara.git
cd backend_jawara
```

### 2. Setup Virtual Environment (Recommended)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/MacOS:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database PostgreSQL

**Buat database baru:**

```sql
CREATE DATABASE jawara_db;
```

Atau via command line PostgreSQL:
```bash
psql -U postgres
CREATE DATABASE jawara_db;
\q
```

### 5. Konfigurasi Environment Variables

Copy file `.env-example` menjadi `.env`:

```bash
copy .env-example .env
```

Edit file `.env` dan sesuaikan dengan konfigurasi Anda:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/jawara_db
SECRET_KEY=your-secret-key-here-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Tips untuk SECRET_KEY:**
```bash
# Generate random secret key (Python)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. Setup Redis (Opsional)

Redis digunakan untuk rate limiting dan caching. Jika tidak menggunakan Redis, Anda perlu memodifikasi kode.

**Windows:**
- Download Redis dari [https://github.com/microsoftarchive/redis/releases](https://github.com/microsoftarchive/redis/releases)
- Atau gunakan Docker: `docker run -d -p 6379:6379 redis`

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**MacOS:**
```bash
brew install redis
brew services start redis
```

**Cek Redis berjalan:**
```bash
redis-cli ping
# Response: PONG
```

**Jika tidak menggunakan Redis:**

Edit file `src/main.py` dan comment/hapus bagian rate limit:

```python
# @app.on_event("startup")
# async def startup_event():
#     redis_url = "redis://localhost:6379"
#     await init_rate_limit(redis_url)
```

### 7. Jalankan Database Migration

Buat tabel-tabel di database:

```bash
alembic upgrade head
```

### 8. Jalankan Seeder (Opsional)

Isi database dengan data dummy untuk testing:

```bash
python seeders/run_seeders.py
```

**Data default yang akan dibuat:**

| Email | Password | Role |
|-------|----------|------|
| admin@jawara.com | password123 | admin |
| rw@jawara.com | password123 | rw |
| rt@jawara.com | password123 | rt |
| secretary@jawara.com | password123 | secretary |
| treasurer@jawara.com | password123 | treasurer |
| citizen@jawara.com | password123 | citizen |
| citizen2@jawara.com | password123 | citizen |

### 9. Jalankan Aplikasi

**Development mode:**

```bash
fastapi dev src/main.py
```

Atau:

```bash
uvicorn src.main:app --reload
```

**Production mode:**

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Aplikasi akan berjalan di: **http://localhost:8000**

### 10. Akses API Documentation

FastAPI menyediakan dokumentasi API otomatis:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Command Reference

### Database Migration

```bash
# Jalankan migration
alembic upgrade head

# Cek status migration
alembic current

# Rollback migration terakhir
alembic downgrade -1

# Rollback semua migration
alembic downgrade base

# Buat migration baru (auto-generate)
alembic revision --autogenerate -m "description"

# Buat migration baru (manual)
alembic revision -m "description"
```

### Seeder

```bash
# Jalankan semua seeder
python seeders/run_seeders.py

# Jalankan seeder spesifik
python seeders/user_seeder.py
python seeders/refresh_session_seeder.py
```

## 📁 Struktur Project

```
backend_jawara/
├── alembic/                    # Database migration files
│   ├── versions/               # Migration scripts
│   └── env.py
├── seeders/                    # Database seeders
│   ├── run_seeders.py
│   ├── user_seeder.py
│   └── refresh_session_seeder.py
├── src/
│   ├── auth/                   # Authentication module
│   ├── database/               # Database configuration
│   ├── entities/               # Database models/entities
│   ├── finance/                # Finance module
│   ├── marketplace/            # Marketplace module
│   ├── population/             # Population module
│   ├── api.py                  # API routes registration
│   ├── exceptions.py           # Custom exceptions
│   ├── main.py                 # Application entry point
│   └── rate_limit.py           # Rate limiting configuration
├── .env                        # Environment variables (create from .env-example)
├── .env-example                # Environment variables template
├── alembic.ini                 # Alembic configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError"
```bash
# Pastikan virtual environment aktif
# Install ulang dependencies
pip install -r requirements.txt
```

### Error: "connection refused" (PostgreSQL)
```bash
# Cek PostgreSQL service berjalan
# Windows: services.msc -> PostgreSQL
# Linux: sudo systemctl status postgresql
# MacOS: brew services list
```

### Error: "connection refused" (Redis)
```bash
# Jika tidak menggunakan Redis, comment kode rate limit di main.py
# Atau jalankan Redis:
# Windows: redis-server.exe
# Linux/MacOS: redis-server
```

### Error: "Target database is not up to date"
```bash
alembic upgrade head
```

### Error: "Can't locate revision"
```bash
alembic stamp head
```

### Reset Database Completely
```bash
# Rollback semua migration
alembic downgrade base

# Drop dan recreate database
# psql -U postgres
# DROP DATABASE jawara_db;
# CREATE DATABASE jawara_db;
# \q

# Jalankan ulang migration
alembic upgrade head

# Jalankan ulang seeder
python seeders/run_seeders.py
```

## 📝 Notes

- Untuk development, gunakan `fastapi dev` atau `uvicorn --reload`
- Untuk production, gunakan `uvicorn` tanpa `--reload` dan set workers
- Redis **opsional**, tapi direkomendasikan untuk production
- Seeder bersifat **idempotent** - aman dijalankan berkali-kali
- Jangan commit file `.env` ke repository!
- Untuk production, gunakan password yang kuat dan secret key yang unik

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Migration & Seeder Guide](./MIGRATION_SEEDER.md)

## 👥 Contributors

TI3H Kelompok 1

## 📄 License

[Add your license here]
