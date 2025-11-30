"""
Seeder untuk tabel User
Menambahkan user default untuk setiap role
"""


from src.database.core import SessionLocal, engine, Base
from src.entities.user import UserModel, UserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password menggunakan bcrypt"""
    return pwd_context.hash(password)


def seed_users():
    """
    Seed data user untuk semua role
    Password default: password123
    """
    db = SessionLocal()
    
    try:
        # Data user yang akan di-seed
        users_data = [
            {
                "email": "admin@jawara.com",
                "password": "password123",
                "role": UserRole.admin.value
            },
            {
                "email": "rw@jawara.com",
                "password": "password123",
                "role": UserRole.rw.value
            },
            {
                "email": "rt@jawara.com",
                "password": "password123",
                "role": UserRole.rt.value
            },
            {
                "email": "secretary@jawara.com",
                "password": "password123",
                "role": UserRole.secretary.value
            },
            {
                "email": "treasurer@jawara.com",
                "password": "password123",
                "role": UserRole.treasurer.value
            },
            {
                "email": "citizen@jawara.com",
                "password": "password123",
                "role": UserRole.citizen.value
            },
            {
                "email": "citizen2@jawara.com",
                "password": "password123",
                "role": UserRole.citizen.value
            }
        ]
        
        # Check jika user sudah ada
        existing_emails = {user.email for user in db.query(UserModel).all()}
        
        users_created = 0
        for user_data in users_data:
            if user_data["email"] not in existing_emails:
                user = UserModel(
                    email=user_data["email"],
                    password_hash=hash_password(user_data["password"]),
                    role=user_data["role"],
                    resident_id=user_data.get("resident_id")
                )
                db.add(user)
                users_created += 1
                print(f"✓ Created user: {user_data['email']} with role: {user_data['role']}")
            else:
                print(f"⊘ User already exists: {user_data['email']}")
        
        db.commit()
        print(f"\n{'='*60}")
        print(f"Seeding completed! {users_created} new user(s) created.")
        print(f"{'='*60}")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding users: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting user seeder...")
    print(f"{'='*60}")
    seed_users()
