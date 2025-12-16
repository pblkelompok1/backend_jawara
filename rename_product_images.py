"""
Script untuk merename semua file di storage/default/product
menjadi format sequential: 1.png, 2.png, 3.png, dst.
"""
import os
from pathlib import Path

def rename_product_images():
    # Path ke folder product
    product_dir = Path("storage/default/product")
    
    if not product_dir.exists():
        print(f"❌ Folder {product_dir} tidak ditemukan!")
        return
    
    # Get all files (exclude directories)
    files = [f for f in product_dir.iterdir() if f.is_file()]
    
    print(f"📁 Ditemukan {len(files)} file di {product_dir}")
    print("\n" + "="*60)
    
    # Sort files by name untuk konsistensi
    files.sort(key=lambda x: x.name)
    
    # Create temporary directory untuk menghindari conflict
    temp_dir = product_dir / "temp_rename"
    temp_dir.mkdir(exist_ok=True)
    
    # Step 1: Move all files to temp with new names
    print("\n🔄 Step 1: Renaming files...")
    for i, file_path in enumerate(files, start=1):
        # Get extension (default to .png if no extension)
        ext = file_path.suffix.lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
            ext = '.png'
        
        new_name = f"{i}{ext}"
        temp_path = temp_dir / new_name
        
        print(f"  {file_path.name} → {new_name}")
        file_path.rename(temp_path)
    
    # Step 2: Move all files back to product directory
    print("\n🔄 Step 2: Moving files back...")
    for file_path in temp_dir.iterdir():
        target_path = product_dir / file_path.name
        file_path.rename(target_path)
        print(f"  ✓ {file_path.name}")
    
    # Remove temp directory
    temp_dir.rmdir()
    
    print("\n" + "="*60)
    print(f"✅ Berhasil rename {len(files)} file!")
    print(f"📂 Lokasi: {product_dir.absolute()}")
    
    # Show final list
    print("\n📋 Hasil akhir:")
    final_files = sorted([f.name for f in product_dir.iterdir() if f.is_file()])
    for fname in final_files:
        print(f"  - {fname}")

if __name__ == "__main__":
    print("🚀 Starting product images rename script...")
    print("="*60)
    rename_product_images()
    print("\n✨ Done!")
