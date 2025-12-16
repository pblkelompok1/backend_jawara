"""
Master seeder untuk menjalankan semua seeder
"""
import sys
import os
from pathlib import Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add src directory to path if not already present
src_path = str(Path(__file__).parent.parent / 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from user_seeder import seed_users
from resident_seeder import seed_residents
from refresh_session_seeder import seed_refresh_sessions
from occupation_seeder import seed_occupations
from rt_seeder import seed_rt
from family_seeder import seed_families
from home_seeder import seed_homes
from home_history_seeder import seed_home_history
from family_movement_seeder import seed_family_movements
from finance_seeder import seed_finance
from activity_seeder import seed_activities
from transaction_method_seeder import seed_transaction_methods
from marketplace_seeder import seed_marketplace
from report_seeder import seed_reports
from letter_seeder import seed_letters


def run_all_seeders():
    """
    Menjalankan semua seeder secara berurutan
    """
    from src.database.core import SessionLocal
    db = SessionLocal()
    from src.entities.resident import ResidentModel, OccupationModel
    from src.entities.user import UserModel
    from src.entities.family import FamilyModel, FamilyMovementModel, RTModel
    from src.entities.home import HomeModel, HomeHistoryModel
    from src.entities.refresh_session import RefreshSessionModel
    from src.entities.finance import FeeModel, FeeTransactionModel, FinanceTransactionModel
    from src.entities.activity import ActivityModel, DashboardBannerModel
    from src.entities.marketplace import TransactionMethodModel, ProductModel, ProductTransactionModel, ListProductTransactionModel, ProductRatingModel
    from src.entities.report import ReportModel
    from src.entities.letter import LetterModel, LetterTransactionModel

    print("Step 0: Deleting all data from tables...")
    print("-"*60)
    # Delete letter tables
    db.query(LetterTransactionModel).delete()
    db.query(LetterModel).delete()
    # Delete report tables
    db.query(ReportModel).delete()
    # Delete marketplace tables first (foreign keys)
    db.query(ProductRatingModel).delete()
    db.query(ListProductTransactionModel).delete()
    db.query(ProductTransactionModel).delete()
    db.query(ProductModel).delete()
    db.query(TransactionMethodModel).delete()
    # Delete activity tables
    db.query(DashboardBannerModel).delete()
    db.query(ActivityModel).delete()
    # Delete finance tables
    db.query(FeeTransactionModel).delete()
    db.query(FinanceTransactionModel).delete()
    db.query(FeeModel).delete()
    # Delete home and family tables
    db.query(HomeHistoryModel).delete()
    db.query(HomeModel).delete()
    db.query(FamilyMovementModel).delete()
    db.query(ResidentModel).delete()
    db.query(FamilyModel).delete()
    db.query(RTModel).delete()
    db.query(OccupationModel).delete()
    db.query(RefreshSessionModel).delete()
    db.query(UserModel).delete()
    db.commit()
    print("All data deleted.\n")

    print("\n" + "="*60)
    print("RUNNING ALL SEEDERS")
    print("="*60 + "\n")
    try:
        print("Step 1: Seeding occupations...")
        print("-"*60)
        seed_occupations(db)
        print("\n")

        print("Step 2: Seeding users...")
        print("-"*60)
        seed_users()
        print("\n")

        print("Step 3: Seeding RTs...")
        print("-"*60)
        seed_rt(db)
        print("\n")

        print("Step 4: Seeding families...")
        print("-"*60)
        seed_families(db)
        print("\n")

        print("Step 5: Seeding residents...")
        print("-"*60)
        seed_residents(db)
        print("\n")

        print("Step 6: Seeding homes...")
        print("-"*60)
        seed_homes(db)
        print("\n")

        print("Step 7: Seeding home history...")
        print("-"*60)
        seed_home_history(db)
        print("\n")

        print("Step 8: Seeding family movements...")
        print("-"*60)
        seed_family_movements(db)
        print("\n")

        print("Step 9: Seeding finance (fees & transactions)...")
        print("-"*60)
        seed_finance(db)
        print("\n")

        print("Step 10: Seeding refresh sessions...")
        print("-"*60)
        seed_refresh_sessions()
        print("\n")

        print("Step 11: Seeding activities...")
        print("-"*60)
        seed_activities()
        print("\n")

        print("Step 12: Seeding transaction methods...")
        print("-"*60)
        seed_transaction_methods()
        print("\n")

        print("Step 13: Seeding marketplace...")
        print("-"*60)
        seed_marketplace(db)
        print("\n")

        print("Step 14: Seeding reports...")
        print("-"*60)
        seed_reports(db)
        print("\n")

        print("Step 15: Seeding letter types...")
        print("-"*60)
        seed_letters(db)
        print("\n" + "="*60)
        print("ALL SEEDERS COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")
        db.close()
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"ERROR: Seeding failed - {e}")
        print(f"{'='*60}\n")
        raise


if __name__ == "__main__":
    run_all_seeders()
