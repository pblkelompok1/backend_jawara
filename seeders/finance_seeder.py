"""
Seeder untuk tabel Finance (Fee dan Finance Transaction)
"""
from src.database.core import get_db
from src.entities.finance import FeeModel, FeeTransactionModel, FinanceTransactionModel, PaymentStatus, AutomationMode, TransactionMethod
from src.entities.family import FamilyModel
from sqlalchemy.orm import Session
from datetime import date, timedelta
import random

def seed_finance(db: Session):
    """
    Seed data untuk Fee, FeeTransaction, dan FinanceTransaction
    """
    try:
        # Get all families for fee transactions
        families = db.query(FamilyModel).all()
        if not families:
            print("No families found. Seed families first.")
            return
        
        # ===== 1. Create Fee Models (10 fees) =====
        fees_data = [
            {
                "fee_name": "Iuran Kebersihan",
                "amount": 50000,
                "charge_date": date(2025, 1, 1),
                "description": "Iuran kebersihan bulanan untuk RT",
                "fee_category": "Bulanan",
                "automation_mode": AutomationMode.off.value,
                "due_date": date(2025, 1, 10)
            },
            {
                "fee_name": "Iuran Keamanan",
                "amount": 75000,
                "charge_date": date(2025, 1, 1),
                "description": "Iuran keamanan lingkungan",
                "fee_category": "Bulanan",
                "automation_mode": AutomationMode.off.value,
                "due_date": date(2025, 1, 15)
            },
            {
                "fee_name": "Iuran Sampah",
                "amount": 30000,
                "charge_date": date(2025, 1, 1),
                "description": "Iuran pengangkutan sampah",
                "fee_category": "Bulanan",
                "automation_mode": AutomationMode.off.value,
                "due_date": date(2025, 1, 10)
            },
            {
                "fee_name": "Iuran Listrik Jalan",
                "amount": 20000,
                "charge_date": date(2025, 1, 1),
                "description": "Iuran listrik penerangan jalan",
                "fee_category": "Bulanan",
                "automation_mode": AutomationMode.off.value,
                "due_date": date(2025, 1, 20)
            },
            {
                "fee_name": "Iuran Perawatan Taman",
                "amount": 25000,
                "charge_date": date(2025, 1, 1),
                "description": "Iuran perawatan taman lingkungan",
                "fee_category": "Bulanan",
                "automation_mode": AutomationMode.off.value,
                "due_date": date(2025, 1, 15)
            },
            {
                "fee_name": "Iuran Posyandu",
                "amount": 15000,
                "charge_date": date(2025, 1, 15),
                "description": "Iuran kegiatan posyandu",
                "fee_category": "Bulanan",
                "automation_mode": AutomationMode.off.value,
                "due_date": date(2025, 1, 31)
            },
            {
                "fee_name": "Iuran Kas RT",
                "amount": 10000,
                "charge_date": date(2025, 1, 1),
                "description": "Iuran kas RT bulanan",
                "fee_category": "Bulanan",
                "automation_mode": AutomationMode.off.value,
                "due_date": date(2025, 1, 10)
            },
            {
                "fee_name": "Iuran 17 Agustus",
                "amount": 100000,
                "charge_date": date(2025, 8, 1),
                "description": "Iuran perayaan kemerdekaan",
                "fee_category": "Tahunan",
                "automation_mode": AutomationMode.off.value,
                "due_date": date(2025, 8, 15)
            },
            {
                "fee_name": "Iuran Gotong Royong",
                "amount": 50000,
                "charge_date": date(2025, 1, 7),
                "description": "Iuran kegiatan gotong royong mingguan",
                "fee_category": "Mingguan",
                "automation_mode": AutomationMode.off.value,
                "due_date": date(2025, 1, 14)
            },
            {
                "fee_name": "Iuran Renovasi Balai RT",
                "amount": 200000,
                "charge_date": date(2025, 3, 1),
                "description": "Iuran renovasi balai RT",
                "fee_category": "Insidental",
                "automation_mode": AutomationMode.off.value,
                "due_date": date(2025, 3, 20)
            }
        ]
        
        fees = []
        for fee_data in fees_data:
            fee = FeeModel(**fee_data)
            db.add(fee)
            fees.append(fee)
            print(f"✓ Created fee: {fee_data['fee_name']} - Rp {fee_data['amount']:,}")
        
        db.commit()
        db.refresh(fees[0])  # Refresh to get IDs
        
        print(f"\n{'='*60}")
        print(f"Created {len(fees)} fees")
        print(f"{'='*60}\n")
        
        # ===== 2. Create Fee Transactions (15 transactions) =====
        fee_transactions_created = 0
        statuses = [PaymentStatus.paid.value] * 10 + [PaymentStatus.unpaid.value] * 3 + [PaymentStatus.pending.value] * 2
        random.shuffle(statuses)
        
        for i in range(15):
            family = random.choice(families)
            fee = random.choice(fees)
            status = statuses[i]
            method = random.choice([TransactionMethod.cash.value, TransactionMethod.qris.value])
            
            # Generate random date in last 60 days
            days_ago = random.randint(0, 60)
            transaction_date = date.today() - timedelta(days=days_ago)
            
            fee_transaction = FeeTransactionModel(
                transaction_date=transaction_date,
                fee_id=fee.fee_id,
                amount=fee.amount,
                transaction_method=method,
                status=status,
                family_id=family.family_id,
                evidence_path="storage/default/default_evidence.pdf"
            )
            db.add(fee_transaction)
            fee_transactions_created += 1
            print(f"✓ Created fee transaction: {family.family_name} - {fee.fee_name} ({status})")
        
        db.commit()
        print(f"\n{'='*60}")
        print(f"Created {fee_transactions_created} fee transactions")
        print(f"{'='*60}\n")
        
        # ===== 3. Create Finance Transactions (20 transactions) =====
        finance_data = [
            # =========================
            #        PEMASUKAN
            # =========================
            {"name": "Sumbangan Warga", "amount": 500000, "category": "Donasi"},
            {"name": "Bantuan Pemerintah", "amount": 2000000, "category": "Bantuan"},
            {"name": "Sumbangan HUT RT", "amount": 750000, "category": "Donasi"},
            {"name": "Hasil Lelang", "amount": 300000, "category": "Lain-lain"},
            {"name": "Sumbangan Karang Taruna", "amount": 400000, "category": "Donasi"},
            {"name": "Dana Hibah", "amount": 1500000, "category": "Bantuan"},
            {"name": "Sumbangan Ibu PKK", "amount": 350000, "category": "Donasi"},
            {"name": "Hasil Bazar RT", "amount": 600000, "category": "Kegiatan"},
            {"name": "Sumbangan Posyandu", "amount": 250000, "category": "Donasi"},
            {"name": "Dana CSR Perusahaan", "amount": 3000000, "category": "Bantuan"},

            # Tambahan 50 pemasukan
            {"name": "Iuran Kebersihan Bulanan", "amount": 100000, "category": "Iuran"},
            {"name": "Iuran Keamanan Bulanan", "amount": 150000, "category": "Iuran"},
            {"name": "Iuran Sampah Bulanan", "amount": 80000, "category": "Iuran"},
            {"name": "Sumbangan Acara Maulid", "amount": 400000, "category": "Donasi"},
            {"name": "Sumbangan Acara Tahun Baru", "amount": 500000, "category": "Donasi"},
            {"name": "Bantuan Kecamatan", "amount": 1200000, "category": "Bantuan"},
            {"name": "Hasil Parkir Kegiatan", "amount": 200000, "category": "Kegiatan"},
            {"name": "Hasil Penjualan Makanan", "amount": 180000, "category": "Lain-lain"},
            {"name": "Sumbangan Pemuda Gereja", "amount": 350000, "category": "Donasi"},
            {"name": "Sumbangan Perayaan Natal", "amount": 450000, "category": "Donasi"},
            {"name": "Donasi Jumat Berkah", "amount": 220000, "category": "Donasi"},
            {"name": "Donasi Anak Yatim", "amount": 500000, "category": "Donasi"},
            {"name": "Bantuan Sosial Provinsi", "amount": 2500000, "category": "Bantuan"},
            {"name": "Hasil Sewa Tenda", "amount": 300000, "category": "Lain-lain"},
            {"name": "Hasil Sewa Kursi", "amount": 120000, "category": "Lain-lain"},
            {"name": "Hasil Sewa Sound System", "amount": 250000, "category": "Lain-lain"},
            {"name": "Donasi Pos Ronda", "amount": 200000, "category": "Donasi"},
            {"name": "Donasi Perbaikan Jalan", "amount": 300000, "category": "Donasi"},
            {"name": "Donasi Jumat Bersih", "amount": 150000, "category": "Donasi"},
            {"name": "Donasi Bencana Alam", "amount": 600000, "category": "Donasi"},
            {"name": "Donasi Renovasi Mushola", "amount": 800000, "category": "Donasi"},
            {"name": "Makanan Kegiatan Terjual", "amount": 170000, "category": "Kegiatan"},
            {"name": "Hasil Parkir Warga", "amount": 90000, "category": "Lain-lain"},
            {"name": "Sumbangan Alumni Warga", "amount": 300000, "category": "Donasi"},
            {"name": "Sumbangan Lomba RT", "amount": 250000, "category": "Donasi"},
            {"name": "Iuran Ronda", "amount": 100000, "category": "Iuran"},
            {"name": "Iuran Kas RT", "amount": 200000, "category": "Iuran"},
            {"name": "Iuran Lampu Jalan", "amount": 160000, "category": "Iuran"},
            {"name": "Donasi Kebersihan", "amount": 180000, "category": "Donasi"},
            {"name": "Donasi Renovasi Posyandu", "amount": 600000, "category": "Donasi"},
            {"name": "Dana Bantuan Yayasan", "amount": 1700000, "category": "Bantuan"},
            {"name": "Kontribusi Tokoh Masyarakat", "amount": 500000, "category": "Donasi"},
            {"name": "Dana CSR UMKM", "amount": 1200000, "category": "Bantuan"},
            {"name": "Hasil Penjualan Merchandise", "amount": 140000, "category": "Lain-lain"},
            {"name": "Hasil Kegiatan Karang Taruna", "amount": 250000, "category": "Kegiatan"},
            {"name": "Sumbangan Aqiqah", "amount": 300000, "category": "Donasi"},
            {"name": "Sumbangan Pernikahan Warga", "amount": 350000, "category": "Donasi"},
            {"name": "Dana Sosial RT", "amount": 250000, "category": "Iuran"},
            {"name": "Donasi Pengajian", "amount": 200000, "category": "Donasi"},
            {"name": "Hasil Kerja Bakti", "amount": 80000, "category": "Lain-lain"},
            {"name": "Hasil Lomba 17-an", "amount": 100000, "category": "Kegiatan"},
            {"name": "Hasil Donasi Warga Baru", "amount": 150000, "category": "Donasi"},
            {"name": "Hasil Kupon Amal", "amount": 200000, "category": "Lain-lain"},
            {"name": "Hasil Donasi Online", "amount": 350000, "category": "Donasi"},
            {"name": "Dana Kegiatan RW", "amount": 400000, "category": "Bantuan"},
            {"name": "Dana Subsidi Kota", "amount": 1800000, "category": "Bantuan"},
            {"name": "Donasi Penyuluhan Kesehatan", "amount": 220000, "category": "Donasi"},
            {"name": "Donasi Tahunan Warga", "amount": 500000, "category": "Donasi"},

            # =========================
            #        PENGELUARAN
            # =========================
            {"name": "Pembelian Perlengkapan Kebersihan", "amount": -450000, "category": "Operasional"},
            {"name": "Biaya Renovasi Balai RT", "amount": -2500000, "category": "Pembangunan"},
            {"name": "Pembelian Sound System", "amount": -1200000, "category": "Aset"},
            {"name": "Biaya Kegiatan 17 Agustus", "amount": -1800000, "category": "Kegiatan"},
            {"name": "Gaji Satpam", "amount": -1500000, "category": "Operasional"},
            {"name": "Listrik dan Air", "amount": -350000, "category": "Operasional"},
            {"name": "Pembelian Tanaman Taman", "amount": -500000, "category": "Operasional"},
            {"name": "Biaya Posyandu Bulanan", "amount": -200000, "category": "Kegiatan"},
            {"name": "Pembelian Tenda", "amount": -800000, "category": "Aset"},
            {"name": "Biaya Gotong Royong", "amount": -150000, "category": "Kegiatan"},

            # Tambahan 50 pengeluaran
            {"name": "Perbaikan Jalan RT", "amount": -2000000, "category": "Pembangunan"},
            {"name": "Pembelian Kursi", "amount": -700000, "category": "Aset"},
            {"name": "Pembelian Meja", "amount": -400000, "category": "Aset"},
            {"name": "Biaya Bazar RT", "amount": -300000, "category": "Kegiatan"},
            {"name": "Biaya Beli Cat Jalan", "amount": -250000, "category": "Operasional"},
            {"name": "Perawatan Taman", "amount": -180000, "category": "Operasional"},
            {"name": "Biaya Perbaikan Saluran Air", "amount": -900000, "category": "Pembangunan"},
            {"name": "Pembelian Lampu Jalan", "amount": -300000, "category": "Aset"},
            {"name": "Pembelian Kabel Listrik", "amount": -150000, "category": "Operasional"},
            {"name": "Pembelian Microphone", "amount": -250000, "category": "Aset"},
            {"name": "Honor Petugas Kebersihan", "amount": -500000, "category": "Operasional"},
            {"name": "Gaji Keamanan Tambahan", "amount": -800000, "category": "Operasional"},
            {"name": "Biaya Konsumsi Rapat", "amount": -120000, "category": "Kegiatan"},
            {"name": "Biaya Sewa Panggung", "amount": -600000, "category": "Kegiatan"},
            {"name": "Pembelian Spanduk", "amount": -150000, "category": "Operasional"},
            {"name": "Pembelian Cat", "amount": -200000, "category": "Operasional"},
            {"name": "Biaya Turnamen RT", "amount": -350000, "category": "Kegiatan"},
            {"name": "Biaya Keamanan Acara", "amount": -250000, "category": "Operasional"},
            {"name": "Pembelian Speaker", "amount": -600000, "category": "Aset"},
            {"name": "Pembelian Penerangan Taman", "amount": -320000, "category": "Aset"},
            {"name": "Pembelian Peralatan Posyandu", "amount": -450000, "category": "Kegiatan"},
            {"name": "Biaya Administrasi", "amount": -100000, "category": "Operasional"},
            {"name": "Perbaikan Toilet Umum", "amount": -600000, "category": "Pembangunan"},
            {"name": "Pembelian Tempat Sampah", "amount": -200000, "category": "Aset"},
            {"name": "Pembelian Karpet Balai", "amount": -400000, "category": "Aset"},
            {"name": "Biaya Pelatihan Kader", "amount": -350000, "category": "Kegiatan"},
            {"name": "Pembelian Buku Administrasi", "amount": -80000, "category": "Operasional"},
            {"name": "Biaya Kegiatan Sosial", "amount": -500000, "category": "Kegiatan"},
            {"name": "Gaji Marbot Mushola", "amount": -300000, "category": "Operasional"},
            {"name": "Perbaikan Atap Balai", "amount": -1600000, "category": "Pembangunan"},
            {"name": "Pembelian Cat Tembok", "amount": -250000, "category": "Operasional"},
            {"name": "Pembelian Seragam Satpam", "amount": -350000, "category": "Operasional"},
            {"name": "Biaya Transportasi Kegiatan", "amount": -200000, "category": "Kegiatan"},
            {"name": "Pembelian Aksesoris Balai", "amount": -300000, "category": "Aset"},
            {"name": "Perbaikan Listrik Rusak", "amount": -500000, "category": "Operasional"},
            {"name": "Perbaikan Jalan Gang", "amount": -1500000, "category": "Pembangunan"},
            {"name": "Biaya Penyemprotan Fogging", "amount": -450000, "category": "Operasional"},
            {"name": "Pembelian Obat Kebersihan", "amount": -90000, "category": "Operasional"},
            {"name": "Biaya Masak Kegiatan RT", "amount": -280000, "category": "Kegiatan"},
            {"name": "Honor Pengajar Posyandu", "amount": -200000, "category": "Kegiatan"},
            {"name": "Pembelian Kanopi Balai", "amount": -2200000, "category": "Aset"},
            {"name": "Perbaikan Lampu Jalan", "amount": -170000, "category": "Operasional"},
            {"name": "Pembelian Printer", "amount": -1500000, "category": "Aset"},
            {"name": "Biaya Internet Balai", "amount": -300000, "category": "Operasional"},
            {"name": "Pembelian Kipas Angin", "amount": -350000, "category": "Aset"},
            {"name": "Biaya Pengiriman Dokumen", "amount": -50000, "category": "Operasional"},
            {"name": "Pembelian Galon Air", "amount": -60000, "category": "Operasional"},
            {"name": "Perawatan APAR", "amount": -200000, "category": "Operasional"},
            {"name": "Pembelian Karung Sampah", "amount": -40000, "category": "Operasional"},
            {"name": "Pembelian Tirai Balai", "amount": -200000, "category": "Aset"},
            {"name": "Biaya Rapat Bulanan", "amount": -150000, "category": "Kegiatan"},
            {"name": "Biaya Operasional Lainnya", "amount": -100000, "category": "Operasional"},
        ]

        
        finance_transactions_created = 0
        for i, finance_info in enumerate(finance_data):
            # Generate random date in last 90 days
            days_ago = random.randint(0, 90)
            transaction_date = date.today() - timedelta(days=days_ago)
            
            finance_transaction = FinanceTransactionModel(
                name=finance_info["name"],
                amount=finance_info["amount"],
                category=finance_info["category"],
                transaction_date=transaction_date,
                evidence_path="storage/default/default_evidence.pdf"
            )
            db.add(finance_transaction)
            finance_transactions_created += 1
            
            transaction_type = "Pemasukan" if finance_info["amount"] > 0 else "Pengeluaran"
            print(f"✓ Created finance transaction: {finance_info['name']} - Rp {abs(finance_info['amount']):,} ({transaction_type})")
        
        db.commit()
        print(f"\n{'='*60}")
        print(f"Created {finance_transactions_created} finance transactions")
        print(f"{'='*60}")
        print("Finance seeding completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding finance: {e}")
        raise

if __name__ == "__main__":
    db = next(get_db())
    seed_finance(db)
