# 🚀 QUICK REFERENCE: Transaction Status API

**Last Updated:** 19 Desember 2025

---

## ⚡ TL;DR untuk Frontend

### **Format Status yang BENAR:**
```
BELUM_DIBAYAR   ✅
PROSES          ✅
SIAP_DIAMBIL    ✅
SEDANG_DIKIRIM  ✅
SELESAI         ✅
DITOLAK         ✅
```

### **Format yang SALAH:**
```
Siap Diambil    ❌ (spasi, bukan underscore)
siap_diambil    ❌ (lowercase)
SIAP DIAMBIL    ❌ (spasi)
Selesai         ❌ (mixed case)
```

---

## 🔥 Quick Implementation

### **1. Buat Enum (Dart)**
```dart
enum TransactionStatus {
  belumDibayar('BELUM_DIBAYAR', 'Belum Dibayar'),
  proses('PROSES', 'Proses'),
  siapDiambil('SIAP_DIAMBIL', 'Siap Diambil'),
  sedangDikirim('SEDANG_DIKIRIM', 'Sedang Dikirim'),
  selesai('SELESAI', 'Selesai'),
  ditolak('DITOLAK', 'Ditolak');

  final String backendValue;
  final String displayText;
  const TransactionStatus(this.backendValue, this.displayText);
  
  static TransactionStatus fromBackend(String value) {
    return values.firstWhere((s) => s.backendValue == value);
  }
}
```

### **2. Update Service**
```dart
Future<void> updateStatus(String id, TransactionStatus status) async {
  await _dio.put(
    '/marketplace/transactions/$id/status',
    data: {'status': status.backendValue},  // ← Ini yang dikirim
  );
}
```

### **3. Parse Response**
```dart
factory TransactionModel.fromJson(Map<String, dynamic> json) {
  return TransactionModel(
    status: TransactionStatus.fromBackend(json['status']),  // ← Parse
  );
}
```

### **4. UI Display**
```dart
Text(transaction.status.displayText)  // ← Display di UI
```

---

## 📌 API Endpoint

```
PUT /marketplace/transactions/{transaction_id}/status
```

**Request Body:**
```json
{
  "status": "SIAP_DIAMBIL"
}
```

**Response (200):**
```json
{
  "product_transaction_id": "uuid",
  "status": "SIAP_DIAMBIL",
  "updated_at": "2025-12-19T10:30:00Z",
  ...
}
```

---

## ⚠️ Special Rules

1. **Status SELESAI** → Stock berkurang, sold_count naik
2. **SELESAI & DITOLAK** → Final states (tidak bisa diubah)
3. Format **CASE-SENSITIVE** & **UNDERSCORE**

---

## 🔗 Full Documentation

- Lengkap: `BACKEND_RESPONSE_TRANSACTION_STATUS.md`
- Examples: `TRANSACTION_STATUS_EXAMPLES.md`

---

**Questions?** Contact Backend Team
