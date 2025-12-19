from sqlalchemy.orm import Session
from src.entities.report import ReportModel
from datetime import datetime, timedelta
import random


def seed_reports(db: Session):
    """Seed report data"""
    
    # Check if reports already exist
    existing_count = db.query(ReportModel).count()
    if existing_count > 0:
        print(f"✓ Reports already seeded ({existing_count} records)")
        return

    reports_data = [
        {
            "category": "keamanan",
            "report_name": "Lampu jalan mati di RT 01",
            "description": "Lampu jalan di dekat mushola sudah mati sejak 3 hari yang lalu. Mohon segera diperbaiki karena rawan pencurian dan kecelakaan.",
            "contact_person": "Budi Santoso - 081234567890",
            "status": "unsolved",
            "evidence": ["storage/report/lampu_mati_1.jpg", "storage/report/lampu_mati_2.jpg"]
        },
        {
            "category": "kebersihan",
            "report_name": "Sampah menumpuk di TPS RT 02",
            "description": "Sampah di TPS belum diangkut selama 1 minggu. Sudah mulai berbau dan mengundang lalat.",
            "contact_person": "Siti Aminah - 081987654321",
            "status": "inprogress",
            "evidence": ["storage/report/sampah_tps.jpg"]
        },
        {
            "category": "infrastruktur",
            "report_name": "Jalan berlubang di depan SD",
            "description": "Jalan berlubang cukup besar di depan SD Negeri 1. Berbahaya untuk anak-anak yang melintas.",
            "contact_person": "Ahmad Yani - 082345678901",
            "status": "unsolved",
            "evidence": ["storage/report/jalan_lubang.jpg"]
        },
        {
            "category": "sosial",
            "report_name": "Keributan di warung kopi",
            "description": "Sering terjadi keributan di warung kopi malam hari mengganggu warga sekitar.",
            "contact_person": "Ibu Ratna - 085678901234",
            "status": "solved",
            "evidence": []
        },
        {
            "category": "keamanan",
            "report_name": "Pencurian motor",
            "description": "Motor warga hilang di parkiran masjid pada malam hari. Mohon ditingkatkan keamanan.",
            "contact_person": "Pak RT - 081122334455",
            "status": "inprogress",
            "evidence": ["storage/report/cctv_pencurian.jpg"]
        },
        {
            "category": "kebersihan",
            "report_name": "Selokan tersumbat",
            "description": "Selokan di Gang Mawar tersumbat sampah. Saat hujan air meluap ke jalan.",
            "contact_person": "Bapak Joko - 087890123456",
            "status": "unsolved",
            "evidence": ["storage/report/selokan_1.jpg", "storage/report/selokan_2.jpg"]
        },
        {
            "category": "infrastruktur",
            "report_name": "Pagar lapangan rusak",
            "description": "Pagar besi lapangan bola rusak dan berkarat. Berbahaya untuk anak-anak.",
            "contact_person": "Pemuda RT 03 - 081234567890",
            "status": "inprogress",
            "evidence": ["storage/report/pagar_rusak.jpg"]
        },
        {
            "category": "lainnya",
            "report_name": "Pohon tumbang",
            "description": "Pohon besar tumbang menutupi jalan akibat angin kencang kemarin malam.",
            "contact_person": "Warga Gang Melati - 089012345678",
            "status": "solved",
            "evidence": ["storage/report/pohon_tumbang_1.jpg", "storage/report/pohon_tumbang_2.jpg"]
        },
        {
            "category": "keamanan",
            "report_name": "CCTV rusak",
            "description": "CCTV di pos keamanan RT 01 sudah rusak sejak 2 minggu lalu. Perlu diperbaiki.",
            "contact_person": "Pak Satpam - 085123456789",
            "status": "unsolved",
            "evidence": []
        },
        {
            "category": "kebersihan",
            "report_name": "Banyak nyamuk di kolam",
            "description": "Kolam ikan warga yang tidak terawat menjadi sarang nyamuk. Mohon ditindaklanjuti.",
            "contact_person": "Ibu Dewi - 081765432109",
            "status": "inprogress",
            "evidence": ["storage/report/kolam_nyamuk.jpg"]
        },
        {
            "category": "sosial",
            "report_name": "Anak-anak bermain di jalan raya",
            "description": "Banyak anak bermain bola di jalan raya. Sangat berbahaya dan mengganggu lalu lintas.",
            "contact_person": "Pak RT 02 - 082987654321",
            "status": "solved",
            "evidence": []
        },
        {
            "category": "infrastruktur",
            "report_name": "Drainase bocor",
            "description": "Drainase di dekat rumah nomor 15 bocor dan menggenang di jalan.",
            "contact_person": "Ibu Sari - 087654321098",
            "status": "unsolved",
            "evidence": ["storage/report/drainase_bocor.jpg"]
        }
    ]

    created_reports = []
    base_date = datetime.utcnow() - timedelta(days=30)

    for idx, data in enumerate(reports_data):
        # Vary the creation date
        created_date = base_date + timedelta(days=random.randint(0, 25))
        updated_date = created_date + timedelta(days=random.randint(0, 5))
        
        report = ReportModel(
            category=data["category"],
            report_name=data["report_name"],
            description=data["description"],
            contact_person=data["contact_person"],
            status=data["status"],
            evidence=data["evidence"],
            created_at=created_date,
            updated_at=updated_date
        )
        created_reports.append(report)

    db.add_all(created_reports)
    db.commit()
    
    print(f"✓ Seeded {len(created_reports)} reports")


if __name__ == "__main__":
    from src.database.core import SessionLocal
    
    db = SessionLocal()
    try:
        seed_reports(db)
    finally:
        db.close()
