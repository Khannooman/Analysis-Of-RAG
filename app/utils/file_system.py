import logging
import os
from pathlib import Path, PurePath
from typing import Union

class FileSystem:
    """Class for handling file system operations with security measures."""

    def __init__(self) -> None:
        """Initialize FileSystem with default upload directory."""
        self.UPLOAD_DIR = 'uploads'
    
    def create_file(self, file_path: str) -> None:
        """
        Create a new file with restricted permissions.

        Args:
            file_path (str): Path where the file should be created

        Raises:
            ValueError: If path contains symbolic links
            OSError: If file creation fails
        """
        file_path = self.clean_path(path=file_path)
        if not file_path.exists():
            with open(file_path, "x", opener=lambda path, flags: os.open(path, flags, 0o600)):
                logging.info("File created with restricted permissions.")

    def create_folder(self, folder_path: str) -> None:
        """
        Create a new folder with restricted permissions.

        Args:
            folder_path (str): Path where the folder should be created

        Raises:
            ValueError: If path contains symbolic links
            OSError: If folder creation fails
        """
        folder_path = self.clean_path(path=folder_path)
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True, mode=0o700)
            logging.info("Folder created with restricted permissions.")

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from the filesystem.

        Args:
            file_path (str): Path of the file to delete

        Returns:
            bool: True if deletion was successful, False otherwise

        Raises:
            ValueError: If path contains symbolic links
        """
        file_path = self.clean_path(path=file_path)
        try:
            file_path.unlink()
            logging.info("File deleted successfully.")
            return True
        except FileNotFoundError:
            logging.warning("File not found.")
            return False
        except PermissionError:
            logging.error("Permission denied when deleting file.")
            return False
        except Exception as e:
            logging.error("Error deleting file")
            return False

    def delete_folder(self, folder_path: Union[str, Path]) -> bool:
        """
        Delete a folder and all its contents.

        Args:
            folder_path (Union[str, Path]): Path of the folder to delete

        Returns:
            bool: True if deletion was successful, False otherwise

        Raises:
            ValueError: If path contains symbolic links
        """
        folder_path = self.clean_path(path=folder_path)
        try:
            import shutil
            shutil.rmtree(folder_path)
            logging.info("Folder deleted successfully.")
            return True
        except FileNotFoundError:
            logging.warning("Folder not found.")
            return False
        except PermissionError:
            logging.error("Permission denied when deleting folder.")
            return False
        except Exception as e:
            logging.error("Error deleting folder")
            return False

    def create_and_get_upload_dir(self, folder_name: str) -> Path:
        """
        Create and return path to upload directory.

        Args:
            folder_name (str): Name of the folder to create in upload directory

        Returns:
            Path: Path to the created upload directory

        Raises:
            ValueError: If UPLOAD_DIR is not set or path contains symbolic links
        """
        if not self.UPLOAD_DIR:
            raise ValueError("UPLOAD_DIR environment variable is not set")

        base_upload_path = Path(self.UPLOAD_DIR).resolve()
        upload_location = self.clean_path(base_upload_path / folder_name)
        upload_location.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        return upload_location

    def clean_path(self, path: Union[str, Path]) -> Path:
        """
        Clean and validate file path for security.

        Args:
            path (Union[str, Path]): Path to clean and validate

        Returns:
            Path: Cleaned and validated path

        Raises:
            ValueError: If path contains symbolic links or is otherwise invalid
        """
        cleaned_path = Path(path).resolve()
        if cleaned_path.is_symlink():
            raise ValueError("Access denied. Path is a symbolic link and cannot be accessed.")
        
        return cleaned_path

    def get_project_dir(self) -> Path:
        """
        Get the root project directory.

        Returns:
            Path: Absolute path to project root directory

        Raises:
            ValueError: If project directory is invalid or inaccessible
        """
        project_dir = Path(__file__).resolve().parent.parent.parent
        if not project_dir.is_dir():
            raise ValueError("Project directory is not valid or accessible.")
        return project_dir
