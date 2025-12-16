from sqlalchemy.orm import Session
from src.entities.letter import LetterModel


def seed_letters(db: Session):
    """Seed letter types (master data)"""
    
    # Check if letters already exist
    existing_count = db.query(LetterModel).count()
    if existing_count > 0:
        print(f"✓ Letters already seeded ({existing_count} records)")
        return

    letters_data = [
        {
            "letter_name": "Surat Keterangan Domisili",
            "template_path": "src/letter/template/domisili_new.html"
        },
        {
            "letter_name": "Surat Keterangan Usaha",
            "template_path": "src/letter/template/pernyataan_usaha_new.html"
        }
    ]

    created_letters = []
    for data in letters_data:
        letter = LetterModel(
            letter_name=data["letter_name"],
            template_path=data["template_path"]
        )
        created_letters.append(letter)

    db.add_all(created_letters)
    db.commit()
    
    print(f"✓ Seeded {len(created_letters)} letter types")


if __name__ == "__main__":
    from src.database.core import SessionLocal
    
    db = SessionLocal()
    try:
        seed_letters(db)
    finally:
        db.close()
