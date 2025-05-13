from typing import Generator, Optional, Dict, Any, Union, List, TypeVar, cast
from tenacity import retry, stop_after_attempt, wait_exponential
from functools import lru_cache
from contextlib import contextmanager
from pathlib import Path
import logging
import traceback
import os

from sqlalchemy import create_engine, text, exc
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.engine import URL, Engine
from sqlalchemy.exc import SQLAlchemyError

from app.utils.utility_manager import UtilityManager
from app.enums.env_keys import EnvKeys
from app.configs.postgre_config import PostgreConfig

T = TypeVar('T')

class PostgreException(Exception):
    """Custom exception for postgres-related error"""
    pass

class PostgreManager(UtilityManager):
    """Manages PostgreSQL database connections and operations using SQLAlchemy."""
    
    _instance: Optional['PostgreManager'] = None
    _MAX_RETRIES = 3
    _POOL_SIZE = 5
    _MAX_OVERFLOW = 10
    
    def __new__(cls, *args, **kwargs) -> 'PostgreManager':
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[Union[int, str]] = None,
        database: Optional[str] = None,
        password: Optional[str] = None,
        schema: Optional[str] = None,
        user: Optional[str] = None,
        ssl_mode: Optional[str] = None
    ) -> None:
        """Initialize database connection with given credentials or environment variables."""
        if hasattr(self, 'initialized') and self.initialized:
            return
            
        self.config = self._initialize_credentials(host, port, database, schema, user, password, ssl_mode)
        self._setup_connection()
        self.initialized = True

    @lru_cache()
    def _initialize_credentials(self, host, port, database, schema, user, password, ssl_mode) -> PostgreConfig:
        """Set up database credentials from parameters or environment variables."""
        try:
            return PostgreConfig(
                host=host or self.get_env_variable(EnvKeys.POSTGRES_DB_HOST.value),
                port=port or self.get_env_variable(EnvKeys.POSTGRES_DB_PORT.value),
                database=database or self.get_env_variable(EnvKeys.POSTGRES_DB_NAME.value),
                schema=schema or self.get_env_variable(EnvKeys.POSTGRES_DB_SCHEMA.value),
                user=user or self.get_env_variable(EnvKeys.POSTGRES_DB_USER.value),
                password=password or self.get_env_variable(EnvKeys.POSTGRES_DB_PASSWORD.value),
                ssl_mode=ssl_mode or self.get_env_variable(EnvKeys.POSTGRES_SSLMODE.value)
            )
        except ValueError as e:
            raise PostgreException(f"Invalid port number: {str(e)}")

    @retry(
        stop=stop_after_attempt(_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def _setup_connection(self) -> None:
        """Set up database connection with retry logic."""
        try:
            connection_url = self._create_connection_url()
            self.engine = create_engine(
                connection_url,
                pool_size=self._POOL_SIZE,
                max_overflow=self._MAX_OVERFLOW,
                pool_timeout=30,
                pool_pre_ping=True
            )
            
            session_factory = sessionmaker(bind=self.engine)
            self._session = scoped_session(session_factory)
            
            # Verify connection
            self._verify_connection()
            
        except Exception as e:
            logging.error(f"Failed to initialize database connection: {str(e)}")
            logging.debug(traceback.format_exc())
            raise PostgreException(f"Failed to initialize database connection: {str(e)}")

    def _create_connection_url(self) -> URL:
        """Create SQLAlchemy connection URL."""
        return URL.create(
            'postgresql+psycopg2',
            username=self.config.user,
            password=self.config.password,
            host=self.config.host,
            database=self.config.database,
            port=self.config.port,
            query={'sslmode': self.config.ssl_mode}
        )

    def _verify_connection(self) -> None:
        """Verify database connection is working."""
        with self.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logging.info("Database connection established successfully")

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        fetch_one: bool = False,
        return_json: bool = False
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """
        Execute a SQL query with optional parameters.
        
        Args:
            query: SQL query string
            params: Optional dictionary of query parameters
            fetch_one: If True, fetch single row, otherwise fetch all rows
            return_json: If True, return results as JSON objects
            
        Returns:
            Query results in requested format, or None/error dictionary if query fails
        
        Raises:
            SQLAlchemyError: If there's an error executing the query
        """
        with self.session_scope() as session:
            try:
                params = self._sanitize_params(params or {})
                logging.debug(f"Executing query: {query}")
                logging.debug(f"Query parameters: {params}")

                result = session.execute(text(query), params)
                
                if not (query.strip().lower().startswith("select") or "returning" in query.lower()):
                    return None

                return self._process_query_results(result, fetch_one, return_json)

            except SQLAlchemyError as e:
                logging.error(f"Database query error: {str(e)}")
                logging.debug(traceback.format_exc())
                raise PostgreException(f"Database query error: {str(e)}")

    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize query parameters."""
        return {
            k: str(v) if isinstance(v, (int, float)) or (
                isinstance(v, str) and len(v) == 36
            ) else v 
            for k, v in params.items()
        }
    
    def _read_schema_file(self):
        """
        Read schema.sql file content

        Returns:
            str: SQL schema content

        Raises:
            PostgreException If schema file cannot be read
        """
        try:
            project_dir = self.get_project_dir()
            schema_path = os.path.join(project_dir, 'schema.sql')
            with open(schema_path, 'r') as f:
                return f.read()
        
        except Exception as e:
            error_msg = f"Failed to read schema file: {str(e)}"
            logging.error(error_msg)
            raise PostgreException(error_msg)
            
    
    def _create_table(self) -> None:
        """
        Create Table based on provided Schema

        Raises:
            PostgreException: If table rcreation fails
        """
        try:
            schema = self._read_schema_file()
            with self.session_scope() as session:
                for query in schema.split(";"):
                    query = query.strip()
                    if query:
                        session.execute(text(query))

                logging.info("Database table created successfully")
                
        except SQLAlchemyError as e:
            error_msg = f"failed to create tables: {str(e)}"
            logging.error(error_msg)
            logging.debug(traceback.format_exc)
            raise PostgreException(error_msg)

    def _process_query_results(
        self,
        result: Any,
        fetch_one: bool,
        return_json: bool
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """Process query results based on specified format."""
        if not return_json:
            return result.fetchone() if fetch_one else result.fetchall()
        
        columns = result.keys()
        if fetch_one:
            row = result.fetchone()
            return dict(zip(columns, row)) if row else None
        
        return [dict(zip(columns, row)) for row in result.fetchall()]

    def health_check(self) -> bool:
        """Check if database connection is healthy."""
        try:
            self._verify_connection()
            return True
        except Exception as e:
            logging.error(f"Database health check failed: {str(e)}")
            return False
        
    def get_session(self) -> Session:
        """Get a new database session"""
        if not hasattr(self, '_session'):
            raise PostgreException("Database session not initialized")
        return self._session

    def cleanup(self) -> None:
        """Cleanup database connections."""
        if hasattr(self, '_session'):
            self._session.remove()
        if hasattr(self, 'engine'):
            self.engine.dispose()



