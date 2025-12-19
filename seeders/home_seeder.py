from src.database.core import get_db
from src.entities.home import HomeModel
from src.entities.family import FamilyModel
from sqlalchemy.orm import Session

def seed_homes(db: Session):
    families = db.query(FamilyModel).all()
    if not families:
        print("No family found. Seed families first.")
        return
    
    streets = [
        "Jl. Mawar", "Jl. Melati", "Jl. Kenanga", "Jl. Anggrek", "Jl. Dahlia",
        "Jl. Cempaka", "Jl. Flamboyan", "Jl. Kamboja", "Jl. Teratai", "Jl. Sakura",
        "Jl. Bougenville", "Jl. Tulip", "Jl. Aster", "Jl. Lavender", "Jl. Lily"
    ]
    
    home_types = ["Rumah Sederhana", "Rumah Permanen", "Rumah Kontrakan"]
    
    homes = []
    for i in range(25):
        family = families[i % len(families)]
        street = streets[i % len(streets)]
        home_type = home_types[i % len(home_types)]
        home_number = (i // len(streets)) + 1
        
        homes.append(
            HomeModel(
                home_name=f"{home_type} {i+1}",
                home_address=f"{street} No. {home_number}",
                status="active",
                family_id=family.family_id
            )
        )
    
    db.bulk_save_objects(homes)
    db.commit()
    print(f"Seeded {len(homes)} homes across {len(families)} families.")

if __name__ == "__main__":
    db = next(get_db())
    seed_homes(db)
