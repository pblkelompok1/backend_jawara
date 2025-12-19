from src.database.core import get_db
from src.entities.family import FamilyModel, RTModel
from sqlalchemy.orm import Session
import uuid

def seed_families(db: Session):
    # Get all RTs
    rts = db.query(RTModel).all()
    if not rts:
        print("No RT found. Seed RTs first.")
        return
    
    family_names = [
        "Keluarga Budi Santoso", "Keluarga Ahmad Dahlan", "Keluarga Siti Nurhaliza",
        "Keluarga Joko Widodo", "Keluarga Soekarno", "Keluarga Hatta",
        "Keluarga Kartini", "Keluarga Dewi Sartika", "Keluarga Cut Nyak Dien",
        "Keluarga Sudirman", "Keluarga Gatot Subroto", "Keluarga Diponegoro",
        "Keluarga Agus Salim", "Keluarga Ki Hajar Dewantara", "Keluarga Wahid Hasyim",
        "Keluarga Tan Malaka", "Keluarga Sutomo", "Keluarga Soepomo",
        "Keluarga Mohammad Yamin", "Keluarga Adam Malik"
    ]
    
    families = []
    for i, name in enumerate(family_names):
        # Distribute families across RTs
        rt = rts[i % len(rts)]
        families.append(
            FamilyModel(
                family_name=name, 
                kk_path="storage/default/document/1.pdf", 
                status="active",
                rt_id=rt.rt_id
            )
        )
    
    db.bulk_save_objects(families)
    db.commit()
    print(f"Seeded {len(families)} families across {len(rts)} RTs.")

if __name__ == "__main__":
    db = next(get_db())
    seed_families(db)
