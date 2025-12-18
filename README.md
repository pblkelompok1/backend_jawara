# Backend Jawara - API Documentation

Backend aplikasi Jawara menggunakan FastAPI untuk mendukung sistem manajemen perumahan/kompleks.

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

### 5. Setup Database & Seeder

```bash
# Jalankan migrasi database
alembic upgrade head

# Jalankan seeder untuk initial data
python -m src.database.seeder
```

#### Default User Credentials

Setelah menjalankan seeder, berikut adalah akun default yang tersedia:

| Email | Password | Role |
|-------|----------|------|
| admin@jawara.com | password123 | Admin |
| rw@jawara.com | password123 | RW |
| rt@jawara.com | password123 | RT |
| secretary@jawara.com | password123 | Secretary |
| treasurer@jawara.com | password123 | Treasurer |
| citizen@jawara.com | password123 | Citizen |
| citizen2@jawara.com | password123 | Citizen |

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

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src tests/
```

## 👥 Tim Pengembang

- **Alex** - FullStack Developer
- **Ninis** - ML/AI Developer
- **Candra** - Frontend Developer
- **Ekya** - FullStack Developer

---

**Version**: 1.0.0  
**Last Updated**: December 2025
