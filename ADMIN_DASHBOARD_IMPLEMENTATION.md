# Admin Dashboard API - Backend Implementation Summary

**Created:** December 19, 2025  
**Module:** `src/admin/`  
**Endpoints:** 2 API endpoints untuk admin dashboard

---

## 🎯 Apa yang Sudah Dibuat?

Backend sudah mengimplementasikan **2 endpoint admin dashboard** sesuai requirement dokumen yang diberikan:

1. **`GET /admin/statistics`** - Statistik umum dashboard
2. **`GET /admin/finance/summary`** - Ringkasan keuangan RT/RW

---

## 📡 Endpoint 1: Admin Statistics

### URL
```
GET /admin/statistics
```

### Deskripsi
Endpoint ini memberikan **5 statistik penting** untuk ditampilkan di dashboard admin dalam bentuk summary cards.

### Request Headers
```
Authorization: Bearer {your_jwt_token}
Content-Type: application/json
```

### Response Success (200 OK)
```json
{
  "success": true,
  "data": {
    "totalResidents": 245,
    "activeUsers": 189,
    "pendingRegistrations": 12,
    "newReportsToday": 5,
    "pendingLetters": 8
  }
}
```

### Field Explanation

| Field | Tipe | Arti | Cara Hitung |
|-------|------|------|-------------|
| `totalResidents` | int | Total penduduk yang sudah disetujui | User dengan `role='citizen'` dan `status='approved'` |
| `activeUsers` | int | User aktif (login 30 hari terakhir) | *Saat ini sama dengan totalResidents karena field `last_login` belum ada* |
| `pendingRegistrations` | int | Registrasi yang menunggu approval | User dengan `role='citizen'` dan `status='pending'` |
| `newReportsToday` | int | Laporan warga yang masuk hari ini | Report dengan `created_at` = hari ini |
| `pendingLetters` | int | Pengajuan surat yang menunggu | LetterTransaction dengan `status='pending'` |

### Contoh Penggunaan di Flutter
```dart
// Service call
final response = await http.get(
  Uri.parse('$baseUrl/admin/statistics'),
  headers: {
    'Authorization': 'Bearer $token',
    'Content-Type': 'application/json',
  },
);

if (response.statusCode == 200) {
  final data = json.decode(response.body);
  final stats = AdminStatistics.fromJson(data['data']);
  
  // Gunakan di widget
  print('Total Penduduk: ${stats.totalResidents}');
  print('Aktif: ${stats.activeUsers}');
}
```

### Model Dart yang Dibutuhkan
```dart
class AdminStatistics {
  final int totalResidents;
  final int activeUsers;
  final int pendingRegistrations;
  final int newReportsToday;
  final int pendingLetters;

  AdminStatistics({
    required this.totalResidents,
    required this.activeUsers,
    required this.pendingRegistrations,
    required this.newReportsToday,
    required this.pendingLetters,
  });

  factory AdminStatistics.fromJson(Map<String, dynamic> json) {
    return AdminStatistics(
      totalResidents: json['totalResidents'] as int,
      activeUsers: json['activeUsers'] as int,
      pendingRegistrations: json['pendingRegistrations'] as int,
      newReportsToday: json['newReportsToday'] as int,
      pendingLetters: json['pendingLetters'] as int,
    );
  }
}
```

---

## 💰 Endpoint 2: Finance Summary

### URL
```
GET /admin/finance/summary
```

### Deskripsi
Endpoint ini memberikan **ringkasan keuangan** RT/RW termasuk pemasukan, pengeluaran, saldo, dan jumlah transaksi.

### Request Headers
```
Authorization: Bearer {your_jwt_token}
Content-Type: application/json
```

### Response Success (200 OK)
```json
{
  "success": true,
  "data": {
    "totalIncome": 15750000.0,
    "totalExpense": 8420000.0,
    "balance": 7330000.0,
    "transactionCount": 156
  }
}
```

### Field Explanation

| Field | Tipe | Arti | Cara Hitung |
|-------|------|------|-------------|
| `totalIncome` | float | Total pemasukan (IDR) | Sum dari `fee_transaction.amount` dengan `status='paid'` |
| `totalExpense` | float | Total pengeluaran (IDR) | *Saat ini 0.0 karena database belum tracking expense* |
| `balance` | float | Saldo (IDR) | `totalIncome - totalExpense` |
| `transactionCount` | int | Total transaksi | Count semua `fee_transaction` |

### Contoh Penggunaan di Flutter
```dart
// Service call
final response = await http.get(
  Uri.parse('$baseUrl/admin/finance/summary'),
  headers: {
    'Authorization': 'Bearer $token',
    'Content-Type': 'application/json',
  },
);

if (response.statusCode == 200) {
  final data = json.decode(response.body);
  final finance = FinanceSummary.fromJson(data['data']);
  
  // Format untuk display
  final formatter = NumberFormat.currency(locale: 'id_ID', symbol: 'Rp ', decimalDigits: 0);
  print('Pemasukan: ${formatter.format(finance.totalIncome)}');
  // Output: Pemasukan: Rp 15.750.000
}
```

### Model Dart yang Dibutuhkan
```dart
class FinanceSummary {
  final double totalIncome;
  final double totalExpense;
  final double balance;
  final int transactionCount;

  FinanceSummary({
    required this.totalIncome,
    required this.totalExpense,
    required this.balance,
    required this.transactionCount,
  });

  factory FinanceSummary.fromJson(Map<String, dynamic> json) {
    return FinanceSummary(
      totalIncome: (json['totalIncome'] as num).toDouble(),
      totalExpense: (json['totalExpense'] as num).toDouble(),
      balance: (json['balance'] as num).toDouble(),
      transactionCount: json['transactionCount'] as int,
    );
  }
}
```

### Format Display di UI
```dart
// Gunakan NumberFormat dari intl package
import 'package:intl/intl.dart';

final currencyFormatter = NumberFormat.currency(
  locale: 'id_ID',
  symbol: 'Rp ',
  decimalDigits: 0,
);

// Pemasukan card
Text(currencyFormatter.format(finance.totalIncome))
// Output: Rp 15.750.000

// Balance card
Text(
  currencyFormatter.format(finance.balance),
  style: TextStyle(
    color: finance.balance >= 0 ? Colors.green : Colors.red,
  ),
)
```

---

## 🔒 Authentication & Authorization

### Status Saat Ini
⚠️ **Authentication belum diaktifkan** - Endpoint bisa diakses tanpa token untuk development.

### Yang Akan Ditambahkan
```python
# Di controller.py, uncomment baris berikut:
# from src.auth.dependencies import get_current_admin_user

@router.get("/statistics")
def get_admin_statistics(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)  # ← Aktifkan ini
):
    # Validasi role
    if current_user.role not in ['admin', 'rt', 'rw']:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Admin role required."
        )
    ...
```

### Role yang Diizinkan
- `admin` - Administrator penuh
- `rt` - Ketua RT
- `rw` - Ketua RW

**TIDAK** diizinkan untuk `citizen` (warga biasa).

---

## ⚠️ Error Responses

### Format Error
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Pesan error yang user-friendly"
  }
}
```

### Error Codes yang Mungkin

| Status | Code | Message | Penyebab |
|--------|------|---------|----------|
| 401 | `UNAUTHORIZED` | Invalid or missing token | Token tidak ada / expired |
| 403 | `FORBIDDEN` | Access denied. Admin role required | User bukan admin |
| 500 | `INTERNAL_SERVER_ERROR` | Failed to retrieve statistics | Error database / server |

### Handling Error di Flutter
```dart
try {
  final response = await http.get(url, headers: headers);
  
  if (response.statusCode == 200) {
    final data = json.decode(response.body);
    if (data['success'] == true) {
      return AdminStatistics.fromJson(data['data']);
    }
  } else if (response.statusCode == 401) {
    // Redirect ke login
    throw Exception('Session expired. Please login again.');
  } else if (response.statusCode == 403) {
    // Tidak punya akses
    throw Exception('You do not have permission to access this page.');
  } else {
    // Error lainnya
    final error = json.decode(response.body);
    throw Exception(error['error']['message']);
  }
} catch (e) {
  print('Error fetching statistics: $e');
  rethrow;
}
```

---

## 📊 Database Tables yang Digunakan

### Statistics Endpoint
1. **`m_user`** - untuk `totalResidents`, `activeUsers`, `pendingRegistrations`
2. **`m_report`** - untuk `newReportsToday`
3. **`t_letter_transaction`** - untuk `pendingLetters`

### Finance Endpoint
1. **`t_fee_transaction`** - untuk semua data keuangan

---

## 🔧 Notes Penting untuk Frontend Developer

### 1. Format Angka
```dart
// SALAH ❌
Text('Rp ${finance.totalIncome}')  
// Output: Rp 15750000.0 (susah dibaca)

// BENAR ✅
import 'package:intl/intl.dart';

final formatter = NumberFormat.currency(
  locale: 'id_ID', 
  symbol: 'Rp ', 
  decimalDigits: 0
);
Text(formatter.format(finance.totalIncome))
// Output: Rp 15.750.000 (mudah dibaca)
```

### 2. Timezone
Backend menggunakan **UTC** untuk semua datetime. Untuk "hari ini", backend otomatis convert ke `date.today()`.

### 3. Null Safety
Semua field **dijamin tidak null**. Jika tidak ada data, backend return `0` atau `0.0`, bukan `null`.

### 4. Refresh Data
```dart
// Pull-to-refresh pattern
RefreshIndicator(
  onRefresh: () async {
    await _loadStatistics();
    await _loadFinanceSummary();
  },
  child: ListView(...)
)
```

### 5. Caching (Optional)
Karena data tidak perlu real-time, bisa di-cache 5-10 menit:
```dart
class AdminService {
  AdminStatistics? _cachedStats;
  DateTime? _lastFetch;
  
  Future<AdminStatistics> getStatistics() async {
    final now = DateTime.now();
    
    // Use cache if less than 5 minutes old
    if (_cachedStats != null && 
        _lastFetch != null && 
        now.difference(_lastFetch!) < Duration(minutes: 5)) {
      return _cachedStats!;
    }
    
    // Fetch fresh data
    final stats = await _fetchFromApi();
    _cachedStats = stats;
    _lastFetch = now;
    return stats;
  }
}
```

---

## 🚀 Testing Endpoints

### Menggunakan cURL

**Test Statistics:**
```bash
curl -X GET "http://localhost:8000/admin/statistics" \
  -H "Content-Type: application/json"
```

**Test Finance Summary:**
```bash
curl -X GET "http://localhost:8000/admin/finance/summary" \
  -H "Content-Type: application/json"
```

### Menggunakan Postman / Thunder Client

1. **Method:** GET
2. **URL:** `http://localhost:8000/admin/statistics`
3. **Headers:**
   - `Content-Type: application/json`
   - (Nanti) `Authorization: Bearer {token}`
4. **Expected Response:** Status 200 dengan JSON data

---

## 🐛 Known Limitations & TODOs

### 1. Active Users
**Current:** `activeUsers` sama dengan `totalResidents`  
**Reason:** Field `last_login` belum ada di `UserModel`  
**TODO:** Tambahkan field `last_login TIMESTAMP` ke database, update saat user login

### 2. Expense Tracking
**Current:** `totalExpense` selalu `0.0`  
**Reason:** Database hanya track income (fee_transaction), tidak ada expense tracking  
**TODO:** Tambah table atau field untuk expense, atau gunakan negative amount

### 3. Authentication
**Current:** Endpoint bisa diakses tanpa auth (untuk development)  
**TODO:** Uncomment auth dependencies di controller setelah auth system ready

---

## 📦 File Structure

```
src/admin/
├── __init__.py          # Module init
├── schemas.py           # Pydantic models untuk request/response
├── service.py           # Business logic & database queries
└── controller.py        # FastAPI endpoints (router)
```

---

## 🎨 UI Integration Example

### Dashboard Cards Layout
```dart
class AdminDashboard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return FutureBuilder<AdminStatistics>(
      future: adminService.getStatistics(),
      builder: (context, snapshot) {
        if (!snapshot.hasData) return CircularProgressIndicator();
        
        final stats = snapshot.data!;
        
        return Column(
          children: [
            // Total Penduduk Card
            StatCard(
              icon: Icons.people_rounded,
              title: 'Total Penduduk',
              value: stats.totalResidents.toString(),
              subtitle: '+${stats.activeUsers} aktif',
              color: Colors.blue,
            ),
            
            // Pending Registrations Card
            StatCard(
              icon: Icons.person_add_rounded,
              title: 'Registrasi Pending',
              value: stats.pendingRegistrations.toString(),
              subtitle: 'Menunggu approval',
              color: Colors.orange,
            ),
            
            // Reports Today Card
            StatCard(
              icon: Icons.report_rounded,
              title: 'Laporan Hari Ini',
              value: stats.newReportsToday.toString(),
              subtitle: 'Laporan baru',
              color: Colors.red,
            ),
            
            // Pending Letters Card
            StatCard(
              icon: Icons.email_rounded,
              title: 'Surat Pending',
              value: stats.pendingLetters.toString(),
              subtitle: 'Belum diproses',
              color: Colors.purple,
            ),
          ],
        );
      },
    );
  }
}
```

### Finance Summary Cards
```dart
class FinanceSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return FutureBuilder<FinanceSummary>(
      future: adminService.getFinanceSummary(),
      builder: (context, snapshot) {
        if (!snapshot.hasData) return CircularProgressIndicator();
        
        final finance = snapshot.data!;
        final formatter = NumberFormat.currency(
          locale: 'id_ID', 
          symbol: 'Rp ', 
          decimalDigits: 0
        );
        
        return Row(
          children: [
            // Pemasukan Card
            Expanded(
              child: FinanceCard(
                icon: Icons.trending_up,
                label: 'Pemasukan',
                amount: formatter.format(finance.totalIncome),
                color: Colors.green,
              ),
            ),
            
            // Pengeluaran Card
            Expanded(
              child: FinanceCard(
                icon: Icons.trending_down,
                label: 'Pengeluaran',
                amount: formatter.format(finance.totalExpense),
                color: Colors.red,
              ),
            ),
            
            // Saldo Card
            Expanded(
              child: FinanceCard(
                icon: Icons.account_balance_wallet,
                label: 'Saldo',
                amount: formatter.format(finance.balance),
                color: finance.balance >= 0 ? Colors.blue : Colors.red,
              ),
            ),
          ],
        );
      },
    );
  }
}
```

---

## 📞 Support

Jika ada pertanyaan atau butuh perubahan:

1. **Error saat hit endpoint?** → Check console log backend untuk detail error
2. **Data tidak sesuai harapan?** → Verify database content dulu
3. **Butuh field tambahan?** → Contact backend developer untuk update schema
4. **Authentication error?** → Pastikan token valid dan role = admin/rt/rw

---

## ✅ Checklist untuk Frontend

- [ ] Buat model `AdminStatistics` di Flutter
- [ ] Buat model `FinanceSummary` di Flutter
- [ ] Implementasi service call dengan http/dio
- [ ] Tambahkan error handling untuk 401/403/500
- [ ] Format currency dengan `intl` package
- [ ] Implementasi pull-to-refresh
- [ ] (Optional) Tambahkan caching 5-10 menit
- [ ] Test dengan data real dari backend

---

**Last Updated:** December 19, 2025  
**Backend Module:** `src/admin/`  
**API Version:** 1.0.0
