# 📘 User Profile API Usage Guide (Frontend)

Panduan singkat untuk frontend developer (Flutter) dalam mengambil username, email, dan foto profil user menggunakan API backend.

---

## 1. Mendapatkan User ID & Role

### Endpoint
- **POST** `/auth/me`
- **Headers:**
  - `Authorization: Bearer <access_token>`

### Response Contoh
```json
{
  "user_id": "string",
  "role": "string"
}
```

### Catatan
- Endpoint ini mengembalikan user_id dan role.
- Email biasanya didapat saat login/signup, atau tambahkan pada response backend jika perlu.

### Contoh Flutter (Dio)
```dart
final response = await dio.post(
  '/auth/me',
  options: Options(headers: {'Authorization': 'Bearer $token'}),
);
final userId = response.data['user_id'];
final role = response.data['role'];
```

---

## 2. Mendapatkan Nama & Foto Profil

### Endpoint
- **GET** `/resident/me`
- **Headers:**
  - `Authorization: Bearer <access_token>`

### Response Contoh
```json
{
  "resident_id": "string",
  "nik": "string",
  "name": "string",
  "phone": "string",
  "profile_img_path": "storage/profile/xxxx.jpg",
  ...
}
```

### Catatan
- `name` = nama lengkap user (bisa digunakan sebagai username).
- `profile_img_path` = path foto profil user (akses: `${baseUrl}/${profile_img_path}`).

### Contoh Flutter (Dio)
```dart
final response = await dio.get(
  '/resident/me',
  options: Options(headers: {'Authorization': 'Bearer $token'}),
);
final name = response.data['name'];
final profileImgPath = response.data['profile_img_path'];
final profileImgUrl = '$baseUrl/$profileImgPath';
```

---

## Prompt Copilot Frontend

> Dapatkan data user (username/nama, email jika tersedia, dan foto profil) dengan:
> 1. Panggil `POST /auth/me` untuk mendapatkan user_id dan role (sertakan token).
> 2. Panggil `GET /resident/me` untuk mendapatkan nama dan path foto profil (sertakan token).
> 3. Untuk foto profil, gabungkan baseUrl dengan `profile_img_path`.
> 4. Email biasanya didapat saat login/signup, atau tambahkan pada response backend jika perlu.

---

Jika butuh contoh implementasi lebih lanjut (misal: model Dart, provider, widget), silakan minta detail tambahan!
