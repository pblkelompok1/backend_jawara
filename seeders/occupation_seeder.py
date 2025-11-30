from src.database.core import get_db
from src.entities.resident import OccupationModel
from sqlalchemy.orm import Session

def seed_occupations(db: Session):
    occupations = [
        OccupationModel(occupation_name="Pegawai Negeri Sipil"),
        OccupationModel(occupation_name="Karyawan Swasta"),
        OccupationModel(occupation_name="Wiraswasta"),
        OccupationModel(occupation_name="Pelajar/Mahasiswa"),
        OccupationModel(occupation_name="Buruh"),
        OccupationModel(occupation_name="Petani"),
    ]
    db.bulk_save_objects(occupations)
    db.commit()
    print("Seeded occupations.")

if __name__ == "__main__":
    db = next(get_db())
    seed_occupations(db)
