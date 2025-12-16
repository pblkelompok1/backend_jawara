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
        from src.entities.family import FamilyModel
        from src.entities.resident import OccupationModel
        from datetime import date
        import random
        
        families = db.query(FamilyModel).all()
        occupations = db.query(OccupationModel).all()
        
        if not families or not occupations:
            print("No family or occupation found. Seed families and occupations first.")
            return
        
        first_names_male = [
            "Ahmad", "Budi", "Candra", "Doni", "Eko", "Fajar", "Guntur", "Hadi",
            "Indra", "Joko", "Kurnia", "Lukas", "Made", "Nanda", "Omar"
        ]
        
        first_names_female = [
            "Ani", "Bella", "Citra", "Dewi", "Eka", "Fitri", "Gita", "Hani",
            "Ika", "Jasmine", "Kartika", "Linda", "Maya", "Nisa", "Oktavia"
        ]
        
        last_names = [
            "Santoso", "Wijaya", "Kusuma", "Pratama", "Saputra", "Lestari",
            "Hidayat", "Setiawan", "Permana", "Utami", "Rahayu", "Wibowo"
        ]
        
        places = [
            "Jakarta", "Bandung", "Surabaya", "Yogyakarta", "Semarang",
            "Medan", "Makassar", "Palembang", "Malang", "Depok"
        ]
        
        religions = ["Islam", "Kristen", "Katolik", "Hindu", "Buddha"]
        blood_types = ["a", "b", "ab", "o"]
        
        residents_data = []
        nik_base = 3173010101900000
        
        for i, family in enumerate(families[:20]):
            occupation = occupations[i % len(occupations)]
            
            # Head of family (male)
            gender = "male"
            first_name = first_names_male[i % len(first_names_male)]
            last_name = last_names[i % len(last_names)]
            residents_data.append({
                "nik": str(nik_base + (i * 2)),
                "name": f"{first_name} {last_name}",
                "phone": f"08{random.randint(1000000000, 9999999999)}",
                "place_of_birth": places[i % len(places)],
                "date_of_birth": date(1970 + (i % 25), 1 + (i % 12), 1 + (i % 28)),
                "gender": gender,
                "is_deceased": False,
                "family_role": "head",
                "religion": religions[i % len(religions)],
                "domicile_status": "resident",
                "status": "approved" if i % 10 != 0 else "pending",
                "blood_type": blood_types[i % len(blood_types)],
                "profile_img_path": "storage/default/default_profile.png",
                "ktp_path": f"storage/default/document/{(i % 2) + 1}.pdf",
                "kk_path": f"storage/default/document/{(i % 2) + 1}.pdf",
                "birth_certificate_path": f"storage/default/document/{(i % 2) + 1}.pdf",
                "family_id": family.family_id,
                "occupation_id": occupation.occupation_id
            })
            
            # Wife (female)
            first_name_wife = first_names_female[i % len(first_names_female)]
            residents_data.append({
                "nik": str(nik_base + (i * 2) + 1),
                "name": f"{first_name_wife} {last_name}",
                "phone": f"08{random.randint(1000000000, 9999999999)}",
                "place_of_birth": places[(i + 1) % len(places)],
                "date_of_birth": date(1972 + (i % 25), 1 + ((i + 1) % 12), 1 + ((i + 1) % 28)),
                "gender": "female",
                "is_deceased": False,
                "family_role": "wife",
                "religion": religions[i % len(religions)],
                "domicile_status": "resident",
                "status": "approved" if i % 10 != 0 else "pending",
                "blood_type": blood_types[(i + 1) % len(blood_types)],
                "profile_img_path": "storage/default/default_profile.png",
                "ktp_path": f"storage/default/document/{(i % 2) + 1}.pdf",
                "kk_path": f"storage/default/document/{(i % 2) + 1}.pdf",
                "birth_certificate_path": f"storage/default/document/{(i % 2) + 1}.pdf",
                "family_id": family.family_id,
                "occupation_id": occupations[(i + 1) % len(occupations)].occupation_id
            })
        
        residents_created = 0
        for resident_data in residents_data:
            resident = ResidentModel(**resident_data)
            db.add(resident)
            residents_created += 1
            if residents_created % 10 == 0:
                print(f"✓ Created {residents_created} residents...")
        
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
