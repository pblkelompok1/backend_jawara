# Backend Jawara - API Documentation

Backend aplikasi Jawara menggunakan FastAPI untuk mendukung sistem manajemen perumahan/kompleks.

## 📁 Struktur Proyek

```
backend_jawara/
├── src/
│   ├── __init__.py              # Package marker
│   ├── main.py                  # Entry point aplikasi FastAPI
│   ├── api.py                   # Router registration
│   ├── exceptions.py            # Custom exception handler
│   ├── rate_limit.py            # Rate limiting dengan Redis
│   ├── logging_config.py        # Konfigurasi logging
│   ├── file_controller.py       # File serving endpoint
│   │
│   ├── auth/                    # Modul Autentikasi
│   │   ├── __init__.py
│   │   ├── controller.py        # Auth endpoints (login, register, dll)
│   │   ├── schemas.py           # Pydantic schemas untuk validasi
│   │   └── service.py           # Business logic autentikasi
│   │
│   ├── resident/                # Modul Warga
│   │   ├── __init__.py
│   │   ├── controller.py        # Resident CRUD endpoints
│   │   ├── schemas.py           # Resident data schemas
│   │   └── service.py           # Resident business logic
│   │
│   ├── finance/                 # Modul Keuangan
│   │   ├── __init__.py
│   │   ├── controller.py        # Finance endpoints
│   │   ├── schemas.py           # Finance schemas
│   │   └── service.py           # Finance business logic
│   │
│   ├── marketplace/             # Modul Marketplace
│   │   ├── __init__.py
│   │   ├── controller.py        # Marketplace endpoints
│   │   ├── schemas.py           # Product/marketplace schemas
│   │   └── service.py           # Marketplace logic
│   │
│   ├── ai/                      # Modul AI/ML
│   │   ├── _init_.py
│   │   ├── controller.py        # AI endpoints
│   │   ├── model_loader.py      # ML model loading
│   │   ├── schemas.py           # AI request/response schemas
│   │   └── service.py           # AI processing logic
│   │
│   ├── activity/                # Modul Aktivitas
│   │   ├── __init__.py
│   │   ├── controller.py        # Activity endpoints
│   │   ├── schemas.py           # Activity schemas
│   │   └── service.py           # Activity logic
│   │
│   ├── letter/                  # Modul Surat
│   │   ├── __init__.py
│   │   ├── controller.py        # Letter request endpoints
│   │   ├── schemas.py           # Letter schemas
│   │   └── service.py           # Letter processing logic
│   │
│   ├── database/                # Database Configuration
│   │   ├── __init__.py
│   │   ├── core.py              # Database connection & session
│   │   └── __pycache__/
│   │
│   ├── entities/                # Database Models (ORM)
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── resident.py          # Resident model
│   │   ├── family.py            # Family model
│   │   ├── finance.py           # Finance model
│   │   ├── home.py              # Home model
│   │   ├── marketplace.py       # Marketplace model
│   │   ├── activity.py          # Activity model
│   │   └── refresh_session.py   # Refresh token model
│   │
│   └── logs/                    # Application logs
│
├── storage/                     # File storage (KTP, profile, dll)
│   ├── profile/
│   └── ktp/
│
└── requirements.txt             # Python dependencies
```

## 🔧 Penjelasan File Utama

### Core Files

- **`main.py`** - Entry point aplikasi dengan konfigurasi CORS, middleware, exception handler, dan startup events
- **`api.py`** - Registrasi semua router dari berbagai modul
- **`exceptions.py`** - Custom exception handler untuk error handling yang konsisten
- **`rate_limit.py`** - Rate limiting menggunakan Redis untuk mencegah abuse
- **`logging_config.py`** - Setup logging dengan Loguru (console + file rotation)
- **`file_controller.py`** - Endpoint untuk serving files (KTP, foto profil, dll)

### Modul Structure

Setiap modul memiliki struktur yang konsisten:
- **`controller.py`** - Mendefinisikan API endpoints (routes)
- **`schemas.py`** - Pydantic models untuk request/response validation
- **`service.py`** - Business logic dan interaksi dengan database

## 🚀 Instalasi dan Setup

### Prerequisites

- Python 3.8+
- PostgreSQL/MySQL (sesuai database yang digunakan)
- Redis (opsional, untuk rate limiting)

### 1. Clone Repository

```bash
git clone <repository-url>
cd backend_jawara
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Buat file `.env` di root project:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/jawara_db

# JWT Secret
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis (Optional)
REDIS_URL=redis://localhost:6379

# Storage
STORAGE_PATH=./storage
```

### 5. Setup Database

```bash
# Jalankan migrasi database
alembic upgrade head

# Atau jalankan seeder jika tersedia
python -m src.database.seeder
```

### 6. Create Storage Directories

```bash
mkdir -p storage/profile storage/ktp
```

### 7. Run Application

#### Development Mode

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 8. Access API Documentation

Setelah aplikasi berjalan, akses:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📝 API Endpoints Overview

### Authentication (`/auth`)
- `POST /auth/register` - Registrasi user baru
- `POST /auth/login` - Login user
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout user

### Residents (`/residents`)
- `GET /residents` - List semua residents
- `GET /residents/{id}` - Detail resident
- `POST /residents` - Create resident baru
- `PUT /residents/{id}` - Update resident
- `DELETE /residents/{id}` - Delete resident

### Finance (`/finance`)
- `GET /finance` - List transaksi keuangan
- `POST /finance` - Create transaksi baru
- `GET /finance/reports` - Generate laporan keuangan

### Marketplace (`/marketplace`)
- `GET /marketplace/products` - List produk
- `POST /marketplace/products` - Create produk baru
- `GET /marketplace/banners` - List banner marketplace

### Letters (`/letter`)
- `POST /letter/request` - Request surat
- `GET /letter/history` - Riwayat permintaan surat
- `GET /letter/{id}` - Detail surat

### AI (`/ai`)
- `POST /ai/predict` - AI prediction endpoint
- AI endpoints untuk fitur machine learning

### Files (`/files`)
- `GET /files/{file_path}` - Serve file (KTP, profile, dll)

## ✅ To-Do List (Completed)

### Backend Development - Alex
- ✅ Memperbarui Database
- ✅ Memperbarui Seeder
- ✅ Memperbaiki Bug atau Logic yang keliru (CRUD)
- ✅ Request Surat screen
- ✅ Laporan Screen
- ✅ Managemen Banner (dashboard + marketplace)
- ✅ Rework Registrasi pending (sekarang kurang bagus sih)

### AI/ML Development - Ninis
- ✅ Rapikan BE
- ✅ Rapikan UI

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Database**: PostgreSQL/MySQL
- **Caching**: Redis
- **Logging**: Loguru
- **Authentication**: JWT
- **Rate Limiting**: FastAPI-Limiter

## 🔒 Security Features

- JWT-based authentication
- Password hashing
- Rate limiting untuk API endpoints
- CORS configuration
- Input validation dengan Pydantic
- File path security checks
- Exception handling yang aman

## 📊 Logging

Aplikasi menggunakan Loguru untuk logging dengan fitur:
- Console logging dengan warna
- File rotation (10 MB)
- Retention 7 hari
- Automatic compression (zip)
- Log files tersimpan di folder `logs/`

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src tests/
```

## 📦 Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/jawara_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: jawara_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
  
  redis:
    image: redis:alpine
```

## 👥 Tim Pengembang

- **Alex** - FullStack Developer
- **Ninis** - ML/AI Developer
- **Candra** - Frontend Developer
- **Ekya** - FullStack Developer

## 📄 License

[Specify your license here]

## 📞 Contact & Support

Untuk pertanyaan atau dukungan, silakan hubungi tim pengembang.

---

**Version**: 1.0.0  
**Last Updated**: December 2025
