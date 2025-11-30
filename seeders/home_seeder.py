from src.database.core import get_db
from src.entities.home import HomeModel
from src.entities.family import FamilyModel
from sqlalchemy.orm import Session

def seed_homes(db: Session):
    family = db.query(FamilyModel).first()
    if not family:
        print("No family found. Seed families first.")
        return
    homes = [
        HomeModel(home_name="Rumah Budi", home_address="Jl. Mawar 1", status="active", family_id=family.family_id),
        HomeModel(home_name="Rumah Ahmad", home_address="Jl. Melati 2", status="active", family_id=family.family_id),
    ]
    db.bulk_save_objects(homes)
    db.commit()
    print("Seeded homes.")

if __name__ == "__main__":
    db = next(get_db())
    seed_homes(db)
