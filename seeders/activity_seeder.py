"""
Seeder untuk tabel Activity dan Dashboard Banner
"""

from src.database.core import SessionLocal
from src.entities.activity import ActivityModel, DashboardBannerModel, ActivityStatus, ActivityCategory
from datetime import datetime, timedelta
import random


def seed_activities():
    """
    Seed data activity dengan berbagai kategori dan status
    """
    db = SessionLocal()
    
    try:
        # Data aktivitas yang akan di-seed
        activities_data = [
            {
                "activity_name": "Kerja Bakti Lingkungan RT 01",
                "description": "Kegiatan gotong royong membersihkan lingkungan RT 01, membersihkan selokan, memotong rumput liar, dan menata taman warga.",
                "start_date": datetime.now() + timedelta(days=7),
                "end_date": datetime.now() + timedelta(days=7, hours=3),
                "location": "Seluruh Area RT 01",
                "organizer": "Pengurus RT 01",
                "status": ActivityStatus.akan_datang.value,
                "banner_img": f"storage/default/event_banner/{random.randint(1, 3)}.png",
                "preview_images": [
                    "storage/activity/1.png",
                    "storage/activity/2.png",
                    "storage/activity/3.png"
                ],
                "category": ActivityCategory.sosial.value
            },
            {
                "activity_name": "Pengajian Rutin Bulanan",
                "description": "Pengajian rutin bulanan untuk seluruh warga RT 01 dengan tema kali ini tentang akhlak mulia dalam bertetangga.",
                "start_date": datetime.now() + timedelta(days=3),
                "end_date": datetime.now() + timedelta(days=3, hours=2),
                "location": "Masjid Al-Ikhlas RT 01",
                "organizer": "Takmir Masjid RT 01",
                "status": ActivityStatus.akan_datang.value,
                "banner_img": f"storage/default/event_banner/{random.randint(1, 3)}.png",
                "preview_images": [
                    "storage/activity/1.png",
                    "storage/activity/2.png"
                ],
                "category": ActivityCategory.keagamaan.value
            },
            {
                "activity_name": "Turnamen Futsal Antar RT",
                "description": "Kompetisi futsal antar RT se-kelurahan dalam rangka mempererat tali silaturahmi dan meningkatkan sportivitas warga.",
                "start_date": datetime.now() - timedelta(days=2),
                "end_date": datetime.now() + timedelta(days=5),
                "location": "Lapangan Futsal Kelurahan",
                "organizer": "Karang Taruna RT 01",
                "status": ActivityStatus.ongoing.value,
                "banner_img": f"storage/default/event_banner/{random.randint(1, 3)}.png",
                "preview_images": [
                    "storage/activity/1.png",
                    "storage/activity/2.png",
                    "storage/activity/3.png",
                ],
                "category": ActivityCategory.olahraga.value
            },
            {
                "activity_name": "Pelatihan Digital Marketing UMKM",
                "description": "Workshop pelatihan digital marketing untuk pelaku UMKM di lingkungan RT 01 agar bisa memasarkan produk secara online.",
                "start_date": datetime.now() - timedelta(days=15),
                "end_date": datetime.now() - timedelta(days=15, hours=-5),
                "location": "Balai RT 01",
                "organizer": "Dinas Koperasi & UMKM",
                "status": ActivityStatus.selesai.value,
                "banner_img": f"storage/default/event_banner/{random.randint(1, 3)}.png",
                "preview_images": [
                    "storage/activity/pelatihan_1.png",
                    "storage/activity/pelatihan_2.png"
                ],
                "category": ActivityCategory.pendidikan.value
            },
            {
                "activity_name": "Bimbingan Belajar Gratis Anak SD",
                "description": "Program bimbingan belajar gratis untuk anak-anak SD di lingkungan RT 01, fokus pada matematika dan bahasa Indonesia.",
                "start_date": datetime.now() + timedelta(days=14),
                "end_date": datetime.now() + timedelta(days=14, hours=2),
                "location": "Rumah Pak RT",
                "organizer": "Pemuda RT 01",
                "status": ActivityStatus.akan_datang.value,
                "banner_img": f"storage/default/event_banner/{random.randint(1, 3)}.png",
                "preview_images": [
                    "storage/activity/1.png",
                    "storage/activity/2.png",
                    "storage/activity/3.png"
                ],
                "category": ActivityCategory.pendidikan.value
            },
            {
                "activity_name": "Lomba 17 Agustus RT 01",
                "description": "Berbagai perlombaan menyambut HUT RI: balap karung, makan kerupuk, tarik tambang, dan masih banyak lagi!",
                "start_date": datetime.now() - timedelta(days=120),
                "end_date": datetime.now() - timedelta(days=120, hours=-6),
                "location": "Lapangan RT 01",
                "organizer": "Panitia 17 Agustus RT 01",
                "status": ActivityStatus.selesai.value,
                "banner_img": f"storage/default/event_banner/{random.randint(1, 3)}.png",
                "preview_images": [
                    "storage/activity/1.png",
                    "storage/activity/2.png",
                    "storage/activity/3.png",
                    "storage/activity/4.png",
                    "storage/activity/5.png"
                ],
                "category": ActivityCategory.sosial.value
            },
            {
                "activity_name": "Senam Sehat Bersama",
                "description": "Senam sehat rutin setiap minggu untuk meningkatkan kesehatan warga RT 01. Terbuka untuk semua umur!",
                "start_date": datetime.now() + timedelta(days=2),
                "end_date": datetime.now() + timedelta(days=2, hours=1),
                "location": "Lapangan RT 01",
                "organizer": "PKK RT 01",
                "status": ActivityStatus.akan_datang.value,
                "banner_img": f"storage/default/event_banner/{random.randint(1, 3)}.png",
                "preview_images": [
                    "storage/activity/1.png",
                    "storage/activity/2.png"
                ],
                "category": ActivityCategory.olahraga.value
            },
            {
                "activity_name": "Santunan Anak Yatim",
                "description": "Kegiatan sosial memberikan santunan kepada anak-anak yatim dan dhuafa di lingkungan RT 01.",
                "start_date": datetime.now() - timedelta(days=30),
                "end_date": datetime.now() - timedelta(days=30, hours=-3),
                "location": "Balai RT 01",
                "organizer": "Takmir Masjid RT 01",
                "status": ActivityStatus.selesai.value,
                "banner_img": f"storage/default/event_banner/{random.randint(1, 3)}.png",
                "preview_images": [
                    "storage/activity/1.png",
                    "storage/activity/2.png",
                    "storage/activity/3.png"
                ],
                "category": ActivityCategory.keagamaan.value
            },
            {
                "activity_name": "Rapat Koordinasi RT",
                "description": "Rapat koordinasi bulanan membahas berbagai isu dan program kerja RT 01 untuk bulan depan.",
                "start_date": datetime.now() + timedelta(days=10),
                "end_date": None,  # Single event tanpa end_date
                "location": "Balai RT 01",
                "organizer": "Pengurus RT 01",
                "status": ActivityStatus.akan_datang.value,
                "banner_img": f"storage/default/event_banner/{random.randint(1, 3)}.png",
                "preview_images": [],
                "category": ActivityCategory.lainnya.value
            },
            {
                "activity_name": "Festival Kuliner Warga",
                "description": "Festival kuliner menampilkan berbagai masakan khas dari warga RT 01. Ada lomba masak dan bazaar makanan!",
                "start_date": datetime.now() + timedelta(days=21),
                "end_date": datetime.now() + timedelta(days=21, hours=8),
                "location": "Lapangan RT 01",
                "organizer": "PKK RT 01",
                "status": ActivityStatus.akan_datang.value,
                "banner_img": f"storage/default/event_banner/{random.randint(1, 3)}.png",
                "preview_images": [
                    "storage/activity/1.png",
                    "storage/activity/2.png",
                    "storage/activity/3.png"
                ],
                "category": ActivityCategory.sosial.value
            }
        ]
        
        print("🌱 Seeding activities...")
        
        # Insert activities
        created_activities = []
        for activity_data in activities_data:
            activity = ActivityModel(**activity_data)
            db.add(activity)
            db.flush()  # Flush to get the activity_id
            created_activities.append(activity)
            print(f"  ✓ Activity created: {activity.activity_name}")
        
        db.commit()
        
        # Create dashboard banners (pilih 3 aktivitas acak untuk banner)
        print("\n🌱 Seeding dashboard banners...")
        
        # Pilih aktivitas dengan status akan_datang atau ongoing untuk banner
        banner_candidates = [a for a in created_activities if a.status in [ActivityStatus.akan_datang.value, ActivityStatus.ongoing.value]]
        
        # Pilih maksimal 3 untuk ditampilkan di banner
        selected_for_banner = random.sample(banner_candidates, min(3, len(banner_candidates)))
        
        for position, activity in enumerate(selected_for_banner, start=1):
            banner = DashboardBannerModel(
                position=position,
                activity_id=activity.activity_id
            )
            db.add(banner)
            print(f"  ✓ Banner position {position}: {activity.activity_name}")
        
        db.commit()
        
        print(f"\n✅ Successfully seeded {len(created_activities)} activities and {len(selected_for_banner)} dashboard banners!")
        
    except Exception as e:
        print(f"❌ Error seeding activities: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting activity seeder...")
    seed_activities()
    print("Activity seeder completed!")
