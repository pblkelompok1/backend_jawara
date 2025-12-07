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
        from src.entities.family import FamilyModel
        from src.entities.resident import OccupationModel
        from datetime import date
        
        family = db.query(FamilyModel).first()
        occupation = db.query(OccupationModel).first()
        
        if not family or not occupation:
            print("No family or occupation found. Seed families and occupations first.")
            return
        
        family_id = family.family_id
        occupation_id = occupation.occupation_id

        residents_data = [
            {
                "nik": "1234567890123456",
                "name": "John Doe",
                "phone": "081234567890",
                "place_of_birth": "Jakarta",
                "date_of_birth": date(1990, 1, 1),
                "gender": "male",
                "is_deceased": False,
                "family_role": "head",
                "religion": "Islam",
                "domicile_status": "resident",
                "status": "approved",
                "blood_type": "o",
                "profile_img_path": "storage/default/default_profile.png",
                "ktp_path": "storage/ktp/ktp_john.png",
                "kk_path": "storage/kk/kk_john.png",
                "birth_certificate_path": "storage/birth_certificate/birth_john.png",
                "family_id": family_id,
                "occupation_id": occupation_id
            },
            {
                "nik": "1234567890123457",
                "name": "Jane Doe",
                "phone": "081234567891",
                "place_of_birth": "Bandung",
                "date_of_birth": date(1992, 5, 15),
                "gender": "female",
                "is_deceased": False,
                "family_role": "wife",
                "religion": "Islam",
                "domicile_status": "resident",
                "status": "approved",
                "blood_type": "a",
                "profile_img_path": "storage/default/default_profile.png",
                "ktp_path": "storage/ktp/ktp_jane.png",
                "kk_path": "storage/kk/kk_john.png",
                "birth_certificate_path": "storage/birth_certificate/birth_jane.png",
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
