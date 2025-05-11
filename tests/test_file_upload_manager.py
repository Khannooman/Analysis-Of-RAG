import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from fastapi import UploadFile, HTTPException

from app.utils.upload_documents import FileUploadManager, FileUploadException

@pytest.fixture
def mock_env_variables():
    return {
        "UPLOAD_ALLOWED_EXTENTIONS": [".txt", ".pdf", ".doc"],
        "UPLOAD_DIR": "/tmp/uploads"
    }

@pytest.fixture
def file_upload_manager(mock_env_variables):
    with patch.dict('os.environ', mock_env_variables):
        manager = FileUploadManager()
        manager._initialize_config()
        return manager

@pytest.fixture
def mock_file():
    file = Mock(spec=UploadFile)
    file.filename = "test.txt"
    file.file = Mock()
    return file

@pytest.mark.asyncio
async def test_upload_success(file_upload_manager, mock_file):
    with patch('app.utils.file_system.FileSystem.create_folder'), \
         patch('builtins.open', mock_open := Mock()), \
         patch('shutil.copyfileobj'):
        
        result = await file_upload_manager.upload([mock_file])
        
        assert "message" in result
        assert "directory" in result
        assert "files" in result
        mock_open.assert_called_once()

@pytest.mark.asyncio
async def test_upload_invalid_extension(file_upload_manager):
    mock_file = Mock(spec=UploadFile)
    mock_file.filename = "test.invalid"
    
    with pytest.raises(HTTPException) as exc_info:
        await file_upload_manager.upload([mock_file])
    
    assert exc_info.value.status_code == 406

@pytest.mark.asyncio
async def test_upload_empty_files(file_upload_manager):
    with pytest.raises(HTTPException) as exc_info:
        await file_upload_manager.upload([])
    
    assert exc_info.value.status_code == 400