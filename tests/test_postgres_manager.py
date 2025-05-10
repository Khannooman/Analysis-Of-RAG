import pytest
from unittest.mock import Mock, patch
from app.databases.postgres_database_manager import PostgreManager, PostgreException

@pytest.fixture
def postgres_manager():
    with patch('app.databases.postgres_database_manager.PostgreManager._initialize_credentials'), \
         patch('app.databases.postgres_database_manager.PostgreManager._setup_connection'):
        return PostgreManager()

def test_singleton_pattern():
    manager1 = PostgreManager()
    manager2 = PostgreManager()
    assert manager1 is manager2

def test_invalid_port():
    with pytest.raises(PostgreException):
        PostgreManager(port="invalid")