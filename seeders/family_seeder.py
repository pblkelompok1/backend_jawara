from src.database.core import get_db
from src.entities.family import FamilyModel
from sqlalchemy.orm import Session
import uuid

def seed_families(db: Session):
    # Assume at least one RT exists
    rt = db.query(FamilyModel).first()
    if not rt:
        print("No RT found. Seed RTs first.")
        return
    families = [
        FamilyModel(family_name="Keluarga Budi Santoso", kk_path="storage/kk/budi_santoso.png", status="active"),
        FamilyModel(family_name="Keluarga Ahmad Dahlan", kk_path="storage/kk/ahmad_dahlan.png", status="active"),
        FamilyModel(family_name="Keluarga Siti Nurhaliza", kk_path="storage/kk/siti_nurhaliza.png", status="active"),
    ]
    db.bulk_save_objects(families)
    db.commit()
    print("Seeded families.")

if __name__ == "__main__":
    db = next(get_db())
    seed_families(db)
