from src.database.core import get_db
from src.entities.user import UserModel
from sqlalchemy.orm import Session
from src.entities.resident import OccupationModel
from src.entities.family import FamilyModel
from src.entities.resident import ResidentModel
from src.entities.home import HomeModel
from sqlalchemy.dialects.postgresql import UUID
import uuid

def seed_rt(db: Session):
    # Assume at least one user exists for RT head
    user = db.query(UserModel).first()
    if not user:
        print("No user found for RT head. Seed users first.")
        return
    rt = FamilyModel(
        family_name="RT 01",
        kk_path="storage/default/default_kk.png",
        status="active"
    )
    db.add(rt)
    db.commit()
    print("Seeded RT.")

if __name__ == "__main__":
    db = next(get_db())
    seed_rt(db)
