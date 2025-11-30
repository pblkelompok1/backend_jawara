"""
Seeder untuk tabel RefreshSession
Menambahkan refresh session dummy untuk testing
"""

from datetime import datetime, timedelta
import uuid

from src.database.core import SessionLocal
from src.entities.user import UserModel
from src.entities.refresh_session import RefreshSessionModel
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_token(token: str) -> str:
    """Hash refresh token"""
    return pwd_context.hash(token)


def seed_refresh_sessions():
    """
    Seed data refresh session untuk user yang sudah ada
    """
    db = SessionLocal()
    
    try:
        # Ambil semua user
        users = db.query(UserModel).all()
        
        if not users:
            print("No users found. Please run user_seeder first.")
            return
        
        sessions_created = 0
        
        for user in users:
            # Check jika user sudah punya refresh session
            existing_session = db.query(RefreshSessionModel).filter(
                RefreshSessionModel.user_id == user.user_id
            ).first()
            
            if not existing_session:
                # Buat dummy refresh token
                dummy_token = f"refresh_token_{user.email}_{uuid.uuid4()}"
                
                session = RefreshSessionModel(
                    user_id=user.user_id,
                    refresh_token_hash=hash_token(dummy_token),
                    expires_at=datetime.now() + timedelta(days=30),
                    created_at=datetime.now(),
                    revoked=False
                )
                db.add(session)
                sessions_created += 1
                print(f"✓ Created refresh session for user: {user.email}")
            else:
                print(f"⊘ Refresh session already exists for user: {user.email}")
        
        db.commit()
        print(f"\n{'='*60}")
        print(f"Seeding completed! {sessions_created} new refresh session(s) created.")
        print(f"{'='*60}")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding refresh sessions: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting refresh session seeder...")
    print(f"{'='*60}")
    seed_refresh_sessions()
