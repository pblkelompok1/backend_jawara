"""
Seeder untuk tabel Resident
Menambahkan resident dummy untuk testing
"""
import sys
import os
from pathlib import Path
import uuid

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.database.core import SessionLocal
from src.entities.resident import ResidentModel


def seed_residents(db):
    """
    Seed data resident dummy
    """
    try:
        # Get first available family and occupation
        family = db.query(ResidentModel.family_rel.property.mapper.class_).first()
        occupation = db.query(ResidentModel.occupation_rel.property.mapper.class_).first()
        family_id = family.family_id if family else None
        occupation_id = occupation.occupation_id if occupation else None

        residents_data = [
            {
                "nik": str(uuid.uuid4())[:16],
                "name": "John Doe",
                "phone": "081234567890",
                "place_of_birth": "Jakarta",
                "date_of_birth": "1990-01-01",
                "gender": "male",
                "is_deceased": False,
                "family_role": "head",
                "religion": "Islam",
                "domicile_status": "active",
                "blood_type": "o",
                "profile_img_path": "default_profile.png",
                "ktp_path": "ktp_john.png",
                "kk_path": "kk_john.png",
                "birth_certificate_path": "birth_john.png",
                "family_id": family_id,
                "occupation_id": occupation_id
            }
        ]
        residents_created = 0
        for resident_data in residents_data:
            resident = ResidentModel(**resident_data)
            db.add(resident)
            residents_created += 1
            print(f"✓ Created resident: {resident_data['name']} with NIK: {resident_data['nik']}")
        db.commit()
        print(f"\n{'='*60}")
        print(f"Seeding completed! {residents_created} new resident(s) created.")
        print(f"{'='*60}")
    except Exception as e:
        db.rollback()
        print(f"Error seeding residents: {e}")
        raise

if __name__ == "__main__":
    print("Starting resident seeder...")
    print(f"{'='*60}")
    seed_residents()
