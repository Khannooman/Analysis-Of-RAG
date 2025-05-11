from typing import List, Dict, Set, Optional
from pathlib import Path
import logging
import shutil
import os
from datetime import datetime

from fastapi import UploadFile, HTTPException, status

from app.enums.env_keys import EnvKeys
from app.utils.utility_manager import UtilityManager
from app.utils.file_system import FileSystem

logger = logging.getLogger(__name__)

class FileUploadException(Exception):
    """Custom Exception for file upload operations."""
    pass

class FileUploadManager(UtilityManager):
    """Manages file upload operations with validation and error handling."""

    def __init__(self) -> None:
        """Initialize FileUploadManager."""
        super().__init__()
        self._allowed_extensions: Set[str] = set()
        self._upload_dir: Path = Path()
        self._initialize_config()

    def _initialize_config(self) -> None:
        """Initialize configuration from environment variables."""
        try:
            self._allowed_extensions = set(
                self.get_env_variable(EnvKeys.UPLOAD_ALLOWED_EXTENTIONS.value)
            )
            self._upload_dir = Path(self.get_env_variable(EnvKeys.UPLOAD_DIR.value))
        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            raise FileUploadException(f"Failed to initialize config: {str(e)}")

    def _validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file.

        Args:
            file: FastAPI UploadFile object

        Raises:
            HTTPException: If file validation fails
        """
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty filename"
            )

        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self._allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"File extension '{file_extension}' is not allowed"
            )

    async def _save_file(self, file: UploadFile, dest_path: Path) -> None:
        """
        Save uploaded file to destination.

        Args:
            file: FastAPI UploadFile object
            dest_path: Destination path for file

        Raises:
            FileUploadException: If file saving fails
        """
        try:
            with open(dest_path, 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)
            logger.info(f"File saved successfully: {dest_path}")
        except Exception as e:
            logger.error(f"Failed to save file {file.filename}: {str(e)}")
            raise FileUploadException(f"Failed to save file: {str(e)}")

    def _create_unique_filename(self, original_filename: str) -> str:
        """Create unique filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(original_filename)
        return f"{name}_{timestamp}{ext}"

    async def upload(self, files: List[UploadFile]) -> Dict[str, str]:
        """
        Upload multiple files with validation.

        Args:
            files: List of FastAPI UploadFile objects

        Returns:
            Dict containing upload status and directory

        Raises:
            HTTPException: If upload validation fails
            FileUploadException: If file operations fail
        """
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files provided"
            )

        try:
            # Ensure upload directory exists
            FileSystem().create_folder(folder_path=str(self._upload_dir))

            uploaded_files = []
            for file in files:
                # Validate file
                self._validate_file(file)

                # Create unique filename
                unique_filename = self._create_unique_filename(file.filename)
                file_path = self._upload_dir / unique_filename

                # Save file
                await self._save_file(file, file_path)
                uploaded_files.append(unique_filename)

            return {
                "message": "Files uploaded successfully",
                "directory": str(self._upload_dir),
                "files": uploaded_files
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Upload failed: {str(e)}"
            )



