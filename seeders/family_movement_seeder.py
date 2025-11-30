from src.database.core import get_db
from src.entities.family import FamilyModel
from sqlalchemy.orm import Session
from src.entities.family import FamilyMovementModel

def seed_family_movements(db: Session):
    family = db.query(FamilyModel).first()
    if not family:
        print("No family found. Seed families first.")
        return
    movements = [
        FamilyMovementModel(reason="Pindah kerja", old_address="Jl. Mawar 1", new_address="Jl. Melati 2", family_id=family.family_id),
    ]
    db.bulk_save_objects(movements)
    db.commit()
    print("Seeded family movements.")

if __name__ == "__main__":
    db = next(get_db())
    seed_family_movements(db)
