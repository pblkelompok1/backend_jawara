from src.database.core import get_db
from src.entities.user import UserModel
from sqlalchemy.orm import Session
from src.entities.family import RTModel

def seed_rt(db: Session):
    # Assume at least one user exists for RT head
    user = db.query(UserModel).filter(UserModel.role == 'admin').first()
    if not user:
        print("No admin user found for RT head. Seed users first.")
        return
    
    rts = [
        RTModel(rt_name="RT 01", user_id=user.user_id),
        RTModel(rt_name="RT 02", user_id=user.user_id),
        RTModel(rt_name="RT 03", user_id=user.user_id),
    ]
    db.bulk_save_objects(rts)
    db.commit()
    print("Seeded RTs.")

if __name__ == "__main__":
    db = next(get_db())
    seed_rt(db)
