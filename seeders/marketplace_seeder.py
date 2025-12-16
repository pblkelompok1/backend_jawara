"""
Seeder untuk marketplace (Product, Transaction, Rating)
"""
import sys
import os
from pathlib import Path
import random
from datetime import datetime, timedelta

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.database.core import SessionLocal
from src.entities.marketplace import (
    ProductModel, ProductTransactionModel, ListProductTransactionModel,
    ProductRatingModel, TransactionMethodModel, ProductCategoryEnum, TransactionStatusEnum
)
from src.entities.user import UserModel


def seed_marketplace(db):
    """
    Seed marketplace data: products, transactions, and ratings
    """
    try:
        print("Starting marketplace seeding...")
        print(f"{'='*60}")
        
        # Get all users for distribution
        users = db.query(UserModel).all()
        if not users:
            print("❌ No users found. Seed users first.")
            return
        
        # Get all transaction methods
        methods = db.query(TransactionMethodModel).all()
        if not methods:
            print("❌ No transaction methods found. Seed transaction methods first.")
            return
        
        print(f"✓ Found {len(users)} users and {len(methods)} transaction methods")
        
        # ============== SEED PRODUCTS ==============
        print(f"\n{'='*60}")
        print("SEEDING PRODUCTS...")
        print(f"{'='*60}")
        
        product_templates = {
            ProductCategoryEnum.MAKANAN: [
                {"name": "Nasi Goreng Spesial", "price": 25000, "desc": "Nasi goreng dengan telur, ayam, dan sayuran"},
                {"name": "Mie Ayam Bakso", "price": 20000, "desc": "Mie ayam dengan bakso sapi pilihan"},
                {"name": "Sate Ayam 10 tusuk", "price": 30000, "desc": "Sate ayam bumbu kacang"},
                {"name": "Gado-gado", "price": 15000, "desc": "Sayuran dengan bumbu kacang"},
                {"name": "Bakso Sapi", "price": 18000, "desc": "Bakso sapi asli dengan kuah gurih"},
                {"name": "Ayam Goreng Krispy", "price": 22000, "desc": "Ayam goreng renyah dengan nasi"},
                {"name": "Soto Ayam", "price": 17000, "desc": "Soto ayam kuning khas Jawa"},
                {"name": "Nasi Uduk Komplit", "price": 20000, "desc": "Nasi uduk dengan lauk lengkap"},
            ],
            ProductCategoryEnum.PAKAIAN: [
                {"name": "Kaos Polos Cotton", "price": 50000, "desc": "Kaos cotton combed 30s"},
                {"name": "Kemeja Batik", "price": 150000, "desc": "Kemeja batik motif modern"},
                {"name": "Celana Jeans", "price": 180000, "desc": "Celana jeans denim premium"},
                {"name": "Jaket Hoodie", "price": 120000, "desc": "Jaket hoodie fleece hangat"},
                {"name": "Gamis Syari", "price": 200000, "desc": "Gamis syari bahan jersey"},
                {"name": "Rok Plisket", "price": 85000, "desc": "Rok plisket wanita"},
                {"name": "Dress Casual", "price": 130000, "desc": "Dress casual untuk hangout"},
            ],
            ProductCategoryEnum.BAHAN_MASAK: [
                {"name": "Beras Premium 5kg", "price": 75000, "desc": "Beras premium pulen"},
                {"name": "Minyak Goreng 2L", "price": 35000, "desc": "Minyak goreng kemasan 2 liter"},
                {"name": "Telur Ayam 1kg", "price": 28000, "desc": "Telur ayam negeri segar"},
                {"name": "Gula Pasir 1kg", "price": 15000, "desc": "Gula pasir putih"},
                {"name": "Tepung Terigu 1kg", "price": 12000, "desc": "Tepung terigu protein sedang"},
                {"name": "Cabai Merah 1kg", "price": 45000, "desc": "Cabai merah segar"},
                {"name": "Bawang Merah 1kg", "price": 40000, "desc": "Bawang merah berkualitas"},
                {"name": "Ayam Potong 1kg", "price": 38000, "desc": "Ayam potong segar"},
            ],
            ProductCategoryEnum.JASA: [
                {"name": "Cuci Motor", "price": 15000, "desc": "Jasa cuci motor manual"},
                {"name": "Cuci Mobil", "price": 50000, "desc": "Jasa cuci mobil lengkap"},
                {"name": "Service AC", "price": 150000, "desc": "Service AC dengan bongkar pasang"},
                {"name": "Les Privat Matematika", "price": 100000, "desc": "Les privat matematika per pertemuan"},
                {"name": "Jahit Baju", "price": 50000, "desc": "Jasa jahit baju custom"},
                {"name": "Potong Rambut", "price": 25000, "desc": "Potong rambut pria/wanita"},
            ],
            ProductCategoryEnum.ELEKTRONIK: [
                {"name": "Charger HP Type-C", "price": 35000, "desc": "Charger fast charging type-c"},
                {"name": "Earphone Bluetooth", "price": 150000, "desc": "Earphone bluetooth TWS"},
                {"name": "Power Bank 10000mAh", "price": 120000, "desc": "Power bank kapasitas 10000mAh"},
                {"name": "Kabel Data 2 Meter", "price": 25000, "desc": "Kabel data USB type-c 2 meter"},
                {"name": "Speaker Bluetooth", "price": 200000, "desc": "Speaker bluetooth portable"},
                {"name": "Lampu LED 10W", "price": 30000, "desc": "Lampu LED hemat energi"},
                {"name": "Mouse Wireless", "price": 80000, "desc": "Mouse wireless 2.4GHz"},
            ]
        }
        
        # Get available product images from storage/default/product
        product_img_dir = Path(__file__).parent.parent / "storage" / "default" / "product"
        available_images = []
        if product_img_dir.exists():
            available_images = [f"storage/default/product/{f.name}" for f in product_img_dir.iterdir() if f.is_file()]
            print(f"✓ Found {len(available_images)} product images")
        else:
            print(f"⚠ Warning: {product_img_dir} not found, using placeholder")
            available_images = ["storage/default/product/1.jpg"]
        
        products = []
        product_count = 0
        
        for category, items in product_templates.items():
            for item in items:
                seller = random.choice(users)
                stock = random.randint(5, 100)
                
                # Select 2-5 random images for this product
                num_images = random.randint(2, min(5, len(available_images)))
                product_images = random.sample(available_images, num_images)
                
                product = ProductModel(
                    name=item["name"],
                    price=item["price"],
                    category=category,
                    stock=stock,
                    view_count=random.randint(0, 500),
                    status=random.choice(["active", "active", "active", "inactive"]),  # 75% active
                    sold_count=random.randint(0, 50),
                    description=item["desc"],
                    more_detail={
                        "weight": f"{random.randint(100, 5000)}g",
                        "condition": "new",
                        "brand": random.choice(["Local", "Import", "Homemade", "Premium"])
                    },
                    images_path=product_images,
                    user_id=seller.user_id
                )
                products.append(product)
                db.add(product)
                product_count += 1
                
                if product_count % 10 == 0:
                    print(f"✓ Created {product_count} products...")
        
        db.commit()
        print(f"\n✅ Successfully seeded {len(products)} products across {len(product_templates)} categories")
        
        # Refresh products to get IDs
        db.expire_all()
        products = db.query(ProductModel).all()
        
        # ============== SEED TRANSACTIONS ==============
        print(f"\n{'='*60}")
        print("SEEDING TRANSACTIONS...")
        print(f"{'='*60}")
        
        addresses = [
            "Jl. Mawar No. 10, RT 01/RW 02",
            "Jl. Melati No. 25, RT 02/RW 03",
            "Jl. Anggrek Blok A No. 5",
            "Jl. Dahlia Raya No. 15",
            "Jl. Flamboyan No. 8, RT 03/RW 01",
            "Jl. Kenanga No. 12",
            "Jl. Tulip No. 20, RT 01/RW 05",
            "Jl. Bougenville No. 7"
        ]
        
        statuses = [
            TransactionStatusEnum.BELUM_DIBAYAR,
            TransactionStatusEnum.PROSES,
            TransactionStatusEnum.SEDANG_DIKIRIM,
            TransactionStatusEnum.SELESAI
        ]
        transactions = []
        
        # Create 30 transactions
        for idx in range(30):
            buyer = random.choice(users)
            method = random.choice(methods)
            address = random.choice(addresses)
            status = random.choice(statuses)
            is_cod = random.choice([True, False])
            
            # Create transaction
            transaction = ProductTransactionModel(
                user_id=buyer.user_id,
                address=address,
                description=f"Pesanan #{idx+1}",
                transaction_method_id=method.transaction_method_id,
                status=status,
                is_cod=is_cod
            )
            db.add(transaction)
            db.flush()
            
            # Add 1-4 products to transaction
            num_items = random.randint(1, 4)
            selected_products = random.sample(products, min(num_items, len(products)))
            
            total_price = 0
            for product in selected_products:
                quantity = random.randint(1, 3)
                transaction_item = ListProductTransactionModel(
                    product_id=product.product_id,
                    product_transaction_id=transaction.product_transaction_id,
                    quantity=quantity,
                    price_at_transaction=product.price
                )
                db.add(transaction_item)
                total_price += product.price * quantity
                
                # Reduce stock if completed
                if status == TransactionStatusEnum.SELESAI:
                    product.stock = max(0, product.stock - quantity)
            
            # Set total price
            transaction.total_price = total_price
            
            transactions.append(transaction)
            
            if (idx + 1) % 10 == 0:
                print(f"✓ Created {idx + 1} transactions...")
        
        db.commit()
        print(f"\n✅ Successfully seeded {len(transactions)} transactions")
        
        # ============== SEED RATINGS ==============
        print(f"\n{'='*60}")
        print("SEEDING RATINGS...")
        print(f"{'='*60}")
        
        rating_descriptions = [
            "Produk bagus, sesuai deskripsi!",
            "Pengiriman cepat, packing rapi",
            "Harga terjangkau, kualitas oke",
            "Sangat puas dengan pembelian ini",
            "Recommended seller!",
            "Produk sesuai ekspektasi",
            "Kualitas standar, harga pas",
            "Pelayanan ramah, produk bagus",
            "Kurang memuaskan",
            "Biasa saja",
            "Lumayan untuk harganya",
            "Mantap banget!",
            "Worth it untuk dibeli",
            None,  # Some ratings without description
            None
        ]
        
        ratings = []
        rated_pairs = set()  # Track (user_id, product_id) to avoid duplicates
        
        # Create 50 ratings
        rating_count = 0
        attempts = 0
        while rating_count < 50 and attempts < 200:
            attempts += 1
            user = random.choice(users)
            product = random.choice(products)
            
            pair = (str(user.user_id), str(product.product_id))
            if pair in rated_pairs:
                continue
            
            # Don't let seller rate their own product
            if product.user_id == user.user_id:
                continue
            
            rated_pairs.add(pair)
            
            rating = ProductRatingModel(
                product_id=product.product_id,
                user_id=user.user_id,
                rating_value=random.randint(1, 5),
                description=random.choice(rating_descriptions)
            )
            ratings.append(rating)
            db.add(rating)
            rating_count += 1
            
            if rating_count % 10 == 0:
                print(f"✓ Created {rating_count} ratings...")
        
        db.commit()
        print(f"\n✅ Successfully seeded {len(ratings)} ratings")
        
        # ============== SUMMARY ==============
        print(f"\n{'='*60}")
        print("MARKETPLACE SEEDING SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Products: {len(products)}")
        print(f"✅ Transactions: {len(transactions)}")
        print(f"✅ Ratings: {len(ratings)}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding marketplace: {e}")
        raise


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_marketplace(db)
    finally:
        db.close()
