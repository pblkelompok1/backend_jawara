# Database Migration & Seeder

Dokumentasi untuk menjalankan migration dan seeder database Jawara Backend.

## Prerequisites

Pastikan dependencies sudah terinstall:
```bash
pip install -r requirements.txt
```

Pastikan file `.env` sudah dikonfigurasi dengan `DATABASE_URL`:
```
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

---

## Migration dengan Alembic

### 1. Menjalankan Migration

Untuk membuat tabel-tabel di database:

```bash
alembic upgrade head
```

### 2. Melihat Status Migration

```bash
alembic current
```

### 3. Rollback Migration

Untuk rollback ke migration sebelumnya:

```bash
alembic downgrade -1
```

Untuk rollback semua migration:

```bash
alembic downgrade base
```

### 4. Membuat Migration Baru (Auto-generate)

Setelah membuat/mengubah model di `src/entities/`:

```bash
alembic revision --autogenerate -m "description of changes"
```

### 5. Membuat Migration Baru (Manual)

```bash
alembic revision -m "description of changes"
```

---

## Seeder

### 1. Menjalankan Semua Seeder

Untuk menjalankan semua seeder sekaligus:

```bash
python seeders/run_seeders.py
```

### 2. Menjalankan Seeder Individual

**User Seeder:**
```bash
python seeders/user_seeder.py
```

**Refresh Session Seeder:**
```bash
python seeders/refresh_session_seeder.py
```

---

## Data Seeder Default

### Users
Seeder akan membuat user dengan email dan role berikut:

| Email | Password | Role |
|-------|----------|------|
| admin@jawara.com | password123 | admin |
| rw@jawara.com | password123 | rw |
| rt@jawara.com | password123 | rt |
| secretary@jawara.com | password123 | secretary |
| treasurer@jawara.com | password123 | treasurer |
| citizen@jawara.com | password123 | citizen |
| citizen2@jawara.com | password123 | citizen |

### Refresh Sessions
Seeder akan membuat refresh session dummy untuk setiap user dengan:
- Token hash yang unik
- Expire time 30 hari dari sekarang
- Status tidak revoked

---

## Workflow Lengkap

### Setup Database dari Awal

1. **Pastikan database PostgreSQL sudah berjalan**

2. **Jalankan migration untuk membuat tabel:**
```bash
alembic upgrade head
```

3. **Jalankan seeder untuk mengisi data:**
```bash
python seeders/run_seeders.py
```

### Update Schema (Setelah Perubahan Model)

1. **Buat migration auto-generate:**
```bash
alembic revision --autogenerate -m "add new column"
```

2. **Review migration file di `alembic/versions/`**

3. **Jalankan migration:**
```bash
alembic upgrade head
```

4. **Update seeder jika diperlukan**

---

## Troubleshooting

### Error: "Can't locate revision identified by 'xxxxx'"
```bash
alembic stamp head
```

### Error: "Target database is not up to date"
```bash
alembic upgrade head
```

### Reset Database Completely
```bash
# Rollback semua migration
alembic downgrade base

# Drop semua tabel manual atau recreate database
# psql: DROP DATABASE database_name; CREATE DATABASE database_name;

# Jalankan ulang migration
alembic upgrade head

# Jalankan ulang seeder
python seeders/run_seeders.py
```

---

## Struktur File

```
jawara_backend/
├── alembic/
│   ├── versions/
│   │   └── 001_create_user_and_refresh_session_tables.py
│   ├── env.py
│   └── script.py.mako
├── seeders/
│   ├── user_seeder.py
│   ├── refresh_session_seeder.py
│   └── run_seeders.py
├── alembic.ini
└── src/
    └── entities/
        ├── user.py
        └── refresh_session.py
```

---

## Notes

- Seeder bersifat **idempotent** - aman dijalankan berkali-kali, tidak akan membuat duplikat data
- Migration **harus** dijalankan sebelum seeder
- Jangan lupa update `.env` file dengan DATABASE_URL yang benar
- Untuk production, gunakan password yang lebih aman
