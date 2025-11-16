"""
Master seeder untuk menjalankan semua seeder
"""
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from user_seeder import seed_users
from refresh_session_seeder import seed_refresh_sessions


def run_all_seeders():
    """
    Menjalankan semua seeder secara berurutan
    """
    print("\n" + "="*60)
    print("RUNNING ALL SEEDERS")
    print("="*60 + "\n")
    
    try:
        # 1. Seed users first
        print("Step 1: Seeding users...")
        print("-"*60)
        seed_users()
        
        print("\n")
        
        # 2. Seed refresh sessions
        print("Step 2: Seeding refresh sessions...")
        print("-"*60)
        seed_refresh_sessions()
        
        print("\n" + "="*60)
        print("ALL SEEDERS COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"ERROR: Seeding failed - {e}")
        print(f"{'='*60}\n")
        raise


if __name__ == "__main__":
    run_all_seeders()
