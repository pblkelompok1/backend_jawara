from src.database.core import get_db
from src.entities.home import HomeModel
from src.entities.family import FamilyModel
from src.entities.home import HomeHistoryModel
from sqlalchemy.orm import Session
from datetime import date

def seed_home_history(db: Session):
    home = db.query(HomeModel).first()
    family = db.query(FamilyModel).first()
    if not home or not family:
        print("No home or family found. Seed homes and families first.")
        return
    histories = [
        HomeHistoryModel(home_id=home.home_id, family_id=family.family_id, moved_in_date=date(2020, 1, 1), moved_out_date=None),
    ]
    db.bulk_save_objects(histories)
    db.commit()
    print("Seeded home history.")

if __name__ == "__main__":
    db = next(get_db())
    seed_home_history(db)
