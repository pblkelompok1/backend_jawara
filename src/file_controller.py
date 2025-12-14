from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import os
import mimetypes

router = APIRouter(
    prefix='/files',
    tags=['File Service']
)

# Base storage directory
BASE_STORAGE_DIR = "storage"

@router.get("/{file_path:path}")
async def get_file(file_path: str):
    """
    Serve files from storage directory.
    
    Args:
        file_path: Path to file, contoh: storage/profile/xxx.jpg atau storage/ktp/xxx.jpg
    
    Returns:
        File content with proper content-type for display in browser/Flutter
    """
    try:
        # Security: ensure the path doesn't try to escape storage directory
        # Remove any leading slashes and resolve the path
        clean_path = file_path.lstrip("/").lstrip("\\")
        
        # Construct full file path
        full_path = Path(clean_path)
        
        # Check if file exists
        if not full_path.exists() or not full_path.is_file():
            raise HTTPException(
                status_code=404,
                detail=f"File tidak ditemukan: {file_path}"
            )
        
        # Security check: ensure file is within storage directory
        try:
            full_path.resolve().relative_to(Path(BASE_STORAGE_DIR).resolve())
        except ValueError:
            # File is outside storage directory
            raise HTTPException(
                status_code=403,
                detail="Akses ke file ini tidak diizinkan"
            )
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(str(full_path))
        if content_type is None:
            content_type = "application/octet-stream"
        
        # Return file with proper content type for inline display
        return FileResponse(
            path=str(full_path),
            media_type=content_type,
            filename=full_path.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error mengakses file: {str(e)}"
        )
