# 📝 Transaction Status - Contoh Request & Response

## 🔧 Quick Testing Guide

### **Base URL**
```
http://localhost:8000
```

---

## 1️⃣ Create Transaction (Buyer)

### **Request**
```http
POST /marketplace/transactions
Content-Type: application/json

{
  "address": "Jl. Kebon Jeruk No. 123, RT 001/RW 002",
  "description": "Tolong kirim sore hari",
  "transaction_method_id": 1,
  "is_cod": false,
  "items": [
    {
      "product_id": "123e4567-e89b-12d3-a456-426614174000",
      "quantity": 2
    },
    {
      "product_id": "123e4567-e89b-12d3-a456-426614174001",
      "quantity": 1
    }
  ]
}
```

### **Response (201 Created)**
```json
{
  "product_transaction_id": "abc12345-e89b-12d3-a456-426614174000",
  "address": "Jl. Kebon Jeruk No. 123, RT 001/RW 002",
  "description": "Tolong kirim sore hari",
  "status": "BELUM_DIBAYAR",
  "total_price": 15000,
  "payment_proof_path": null,
  "is_cod": false,
  "user_id": "user123-uuid",
  "buyer_name": "John Doe",
  "transaction_method_id": 1,
  "transaction_method_name": "Transfer Bank BCA",
  "items": [
    {
      "product_id": "123e4567-e89b-12d3-a456-426614174000",
      "product_name": "Sayur Kangkung Segar",
      "quantity": 2,
      "price_at_transaction": 5000,
      "total_price": 10000
    },
    {
      "product_id": "123e4567-e89b-12d3-a456-426614174001",
      "product_name": "Tomat Merah",
      "quantity": 1,
      "price_at_transaction": 5000,
      "total_price": 5000
    }
  ],
  "total_amount": 15000,
  "created_at": "2025-12-19T10:00:00Z",
  "updated_at": "2025-12-19T10:00:00Z"
}
```

---

## 2️⃣ Update Status: BELUM_DIBAYAR → PROSES

### **Scenario:** Seller confirms payment received

### **Request**
```http
PUT /marketplace/transactions/abc12345-e89b-12d3-a456-426614174000/status
Content-Type: application/json

{
  "status": "PROSES"
}
```

### **Response (200 OK)**
```json
{
  "product_transaction_id": "abc12345-e89b-12d3-a456-426614174000",
  "status": "PROSES",
  "updated_at": "2025-12-19T10:15:00Z",
  ...
}
```

---

## 3️⃣ Update Status: PROSES → SIAP_DIAMBIL

### **Scenario:** Order ready for pickup

### **Request**
```http
PUT /marketplace/transactions/abc12345-e89b-12d3-a456-426614174000/status
Content-Type: application/json

{
  "status": "SIAP_DIAMBIL"
}
```

### **Response (200 OK)**
```json
{
  "product_transaction_id": "abc12345-e89b-12d3-a456-426614174000",
  "status": "SIAP_DIAMBIL",
  "updated_at": "2025-12-19T11:00:00Z",
  ...
}
```

---

## 4️⃣ Update Status: PROSES → SEDANG_DIKIRIM

### **Scenario:** Order is being delivered

### **Request**
```http
PUT /marketplace/transactions/abc12345-e89b-12d3-a456-426614174000/status
Content-Type: application/json

{
  "status": "SEDANG_DIKIRIM"
}
```

### **Response (200 OK)**
```json
{
  "product_transaction_id": "abc12345-e89b-12d3-a456-426614174000",
  "status": "SEDANG_DIKIRIM",
  "updated_at": "2025-12-19T11:30:00Z",
  ...
}
```

---

## 5️⃣ Update Status: SEDANG_DIKIRIM → SELESAI

### **Scenario:** Order delivered & completed

### **Request**
```http
PUT /marketplace/transactions/abc12345-e89b-12d3-a456-426614174000/status
Content-Type: application/json

{
  "status": "SELESAI"
}
```

### **Response (200 OK)**
```json
{
  "product_transaction_id": "abc12345-e89b-12d3-a456-426614174000",
  "status": "SELESAI",
  "updated_at": "2025-12-19T14:00:00Z",
  ...
}
```

**⚠️ Important:** 
- Stock berkurang sesuai quantity
- `sold_count` bertambah untuk setiap produk
- Tidak bisa update status lagi setelah SELESAI

---

## 6️⃣ Update Status: * → DITOLAK

### **Scenario:** Order rejected/cancelled

### **Request**
```http
PUT /marketplace/transactions/abc12345-e89b-12d3-a456-426614174000/status
Content-Type: application/json

{
  "status": "DITOLAK"
}
```

### **Response (200 OK)**
```json
{
  "product_transaction_id": "abc12345-e89b-12d3-a456-426614174000",
  "status": "DITOLAK",
  "updated_at": "2025-12-19T10:20:00Z",
  ...
}
```

**⚠️ Important:** 
- Stock tidak berkurang
- Bisa ditolak dari status manapun (kecuali SELESAI/DITOLAK)

---

## ❌ Error Examples

### **Error 1: Wrong Format (with space)**

**Request**
```json
{
  "status": "Siap Diambil"
}
```

**Response (422 Unprocessable Entity)**
```json
{
  "detail": [
    {
      "type": "string_pattern_mismatch",
      "loc": ["body", "status"],
      "msg": "String should match pattern '^(BELUM_DIBAYAR|PROSES|SIAP_DIAMBIL|SEDANG_DIKIRIM|SELESAI|DITOLAK)$'",
      "input": "Siap Diambil",
      "ctx": {
        "pattern": "^(BELUM_DIBAYAR|PROSES|SIAP_DIAMBIL|SEDANG_DIKIRIM|SELESAI|DITOLAK)$"
      }
    }
  ]
}
```

### **Error 2: Wrong Case (lowercase)**

**Request**
```json
{
  "status": "selesai"
}
```

**Response (422 Unprocessable Entity)**
```json
{
  "detail": [
    {
      "type": "string_pattern_mismatch",
      "loc": ["body", "status"],
      "msg": "String should match pattern '^(BELUM_DIBAYAR|PROSES|SIAP_DIAMBIL|SEDANG_DIKIRIM|SELESAI|DITOLAK)$'",
      "input": "selesai",
      "ctx": {
        "pattern": "^(BELUM_DIBAYAR|PROSES|SIAP_DIAMBIL|SEDANG_DIKIRIM|SELESAI|DITOLAK)$"
      }
    }
  ]
}
```

### **Error 3: Invalid Status**

**Request**
```json
{
  "status": "PENDING"
}
```

**Response (422 Unprocessable Entity)**
```json
{
  "detail": [
    {
      "type": "string_pattern_mismatch",
      "loc": ["body", "status"],
      "msg": "String should match pattern '^(BELUM_DIBAYAR|PROSES|SIAP_DIAMBIL|SEDANG_DIKIRIM|SELESAI|DITOLAK)$'",
      "input": "PENDING",
      "ctx": {
        "pattern": "^(BELUM_DIBAYAR|PROSES|SIAP_DIAMBIL|SEDANG_DIKIRIM|SELESAI|DITOLAK)$"
      }
    }
  ]
}
```

### **Error 4: Transaction Not Found**

**Request**
```http
PUT /marketplace/transactions/invalid-uuid/status
```

**Response (404 Not Found)**
```json
{
  "detail": "Transaction not found"
}
```

---

## 🧪 cURL Examples

### **Update to PROSES**
```bash
curl -X PUT "http://localhost:8000/marketplace/transactions/abc12345-e89b-12d3-a456-426614174000/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "PROSES"}'
```

### **Update to SIAP_DIAMBIL**
```bash
curl -X PUT "http://localhost:8000/marketplace/transactions/abc12345-e89b-12d3-a456-426614174000/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "SIAP_DIAMBIL"}'
```

### **Update to SEDANG_DIKIRIM**
```bash
curl -X PUT "http://localhost:8000/marketplace/transactions/abc12345-e89b-12d3-a456-426614174000/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "SEDANG_DIKIRIM"}'
```

### **Update to SELESAI**
```bash
curl -X PUT "http://localhost:8000/marketplace/transactions/abc12345-e89b-12d3-a456-426614174000/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "SELESAI"}'
```

### **Update to DITOLAK**
```bash
curl -X PUT "http://localhost:8000/marketplace/transactions/abc12345-e89b-12d3-a456-426614174000/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "DITOLAK"}'
```

---

## 📊 Status Flow Diagram

```
┌─────────────────┐
│ BELUM_DIBAYAR   │ (Initial State)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌────────┐
│PROSES  │  │DITOLAK │ (Final State)
└───┬────┘  └────────┘
    │
    ├─────────────┐
    │             │
    ▼             ▼
┌──────────────┐ ┌────────────────┐
│SIAP_DIAMBIL  │ │SEDANG_DIKIRIM  │
└──────┬───────┘ └────────┬───────┘
       │                  │
       └────────┬─────────┘
                ▼
           ┌─────────┐
           │SELESAI  │ (Final State)
           └─────────┘
```

**Legend:**
- **Initial State:** BELUM_DIBAYAR (auto-set saat create transaction)
- **Active States:** PROSES, SIAP_DIAMBIL, SEDANG_DIKIRIM
- **Final States:** SELESAI, DITOLAK (tidak bisa diubah lagi)

---

## ✅ Validation Checklist

Sebelum kirim request, pastikan:

- [ ] Status dalam **UPPERCASE**
- [ ] Gunakan **UNDERSCORE** bukan spasi
- [ ] Status ada dalam list valid (6 status)
- [ ] Transaction ID valid (UUID format)
- [ ] Content-Type: application/json
- [ ] JSON valid (no trailing comma, proper quotes)

---

## 🎯 Frontend Implementation Tip

```dart
// Jangan hard-code string!
// ❌ WRONG
await updateStatus(transactionId, "Siap Diambil");

// ✅ CORRECT
await updateStatus(transactionId, TransactionStatus.siapDiambil.backendValue);
```

---

**Last Updated:** 19 Desember 2025  
**Backend Version:** v1.0.0
