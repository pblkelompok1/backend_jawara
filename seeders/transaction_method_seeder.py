from sqlalchemy.orm import Session
from src.entities.marketplace import TransactionMethodModel
from src.database.core import SessionLocal

def seed_transaction_methods():
    """Seed transaction methods"""
    db: Session = SessionLocal()
    
    try:
        # Check if already seeded
        existing = db.query(TransactionMethodModel).first()
        if existing:
            print("Transaction methods already seeded, skipping...")
            return
        
        methods = [
            {
                "method_name": "Cash on Delivery (COD)",
                "description": "Bayar saat barang diterima",
                "is_active": True
            },
            {
                "method_name": "Transfer Bank",
                "description": "Transfer ke rekening penjual",
                "is_active": True
            },
            {
                "method_name": "E-Wallet",
                "description": "Pembayaran melalui dompet digital (GoPay, OVO, Dana, dll)",
                "is_active": True
            },
            {
                "method_name": "QRIS",
                "description": "Pembayaran menggunakan QRIS",
                "is_active": True
            }
        ]
        
        for method_data in methods:
            method = TransactionMethodModel(**method_data)
            db.add(method)
        
        db.commit()
        print(f"✅ Successfully seeded {len(methods)} transaction methods")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding transaction methods: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_transaction_methods()
