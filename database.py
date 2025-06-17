"""
Enhanced database configuration with PostgreSQL support and scalability improvements
"""

import os
from urllib.parse import urlparse
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool, StaticPool
import logging

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration with support for multiple database types"""
    
    @staticmethod
    def get_database_url():
        """
        Get database URL with environment-based configuration
        Supports PostgreSQL, MySQL, and SQLite with automatic fallback
        """
        # Check for explicit database URL
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            # Handle Heroku postgres:// URLs
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            return database_url
        
        # Check for PostgreSQL configuration
        pg_host = os.environ.get('POSTGRES_HOST', 'localhost')
        pg_port = os.environ.get('POSTGRES_PORT', '5432')
        pg_db = os.environ.get('POSTGRES_DB', 'pricing_intelligence')
        pg_user = os.environ.get('POSTGRES_USER')
        pg_password = os.environ.get('POSTGRES_PASSWORD')
        
        if pg_user and pg_password:
            return f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
        
        # Check for MySQL configuration
        mysql_host = os.environ.get('MYSQL_HOST')
        mysql_port = os.environ.get('MYSQL_PORT', '3306')
        mysql_db = os.environ.get('MYSQL_DB', 'pricing_intelligence')
        mysql_user = os.environ.get('MYSQL_USER')
        mysql_password = os.environ.get('MYSQL_PASSWORD')
        
        if mysql_host and mysql_user and mysql_password:
            return f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
        
        # Fallback to SQLite
        db_path = os.environ.get('SQLITE_PATH', 'pricing_intelligence.db')
        return f"sqlite:///{db_path}"
    
    @staticmethod
    def get_engine_config(database_url):
        """
        Get SQLAlchemy engine configuration based on database type
        """
        parsed = urlparse(database_url)
        db_type = parsed.scheme.split('+')[0]
        
        config = {
            'echo': os.environ.get('SQL_ECHO', 'false').lower() == 'true',
            'future': True,  # Use SQLAlchemy 2.0 style
        }
        
        if db_type == 'postgresql':
            # PostgreSQL configuration
            config.update({
                'poolclass': QueuePool,
                'pool_size': int(os.environ.get('DB_POOL_SIZE', '10')),
                'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '20')),
                'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', '30')),
                'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '3600')),
                'pool_pre_ping': True,  # Validate connections before use
                'connect_args': {
                    'connect_timeout': 10,
                    'application_name': 'pricing_intelligence_platform'
                }
            })
            
        elif db_type == 'mysql':
            # MySQL configuration
            config.update({
                'poolclass': QueuePool,
                'pool_size': int(os.environ.get('DB_POOL_SIZE', '10')),
                'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '20')),
                'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', '30')),
                'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '3600')),
                'pool_pre_ping': True,
                'connect_args': {
                    'connect_timeout': 10,
                    'charset': 'utf8mb4'
                }
            })
            
        elif db_type == 'sqlite':
            # SQLite configuration
            config.update({
                'poolclass': StaticPool,
                'connect_args': {
                    'check_same_thread': False,
                    'timeout': 20
                }
            })
            
        return config
    
    @staticmethod
    def create_engine(database_url=None):
        """
        Create SQLAlchemy engine with appropriate configuration
        """
        if not database_url:
            database_url = DatabaseConfig.get_database_url()
        
        engine_config = DatabaseConfig.get_engine_config(database_url)
        
        try:
            engine = create_engine(database_url, **engine_config)
            
            # Test connection
            with engine.connect() as conn:
                conn.execute('SELECT 1')
            
            logger.info(f"Database engine created successfully: {urlparse(database_url).scheme}")
            return engine
            
        except Exception as e:
            logger.error(f"Failed to create database engine: {str(e)}")
            
            # Fallback to SQLite if other database fails
            if not database_url.startswith('sqlite'):
                logger.warning("Falling back to SQLite database")
                fallback_url = "sqlite:///pricing_intelligence_fallback.db"
                fallback_config = DatabaseConfig.get_engine_config(fallback_url)
                return create_engine(fallback_url, **fallback_config)
            
            raise

class DatabaseMigrations:
    """Database migration management"""
    
    @staticmethod
    def get_migration_dir():
        """Get migrations directory path"""
        return os.path.join(os.path.dirname(__file__), '..', 'migrations')
    
    @staticmethod
    def init_migrations():
        """Initialize migration directory structure"""
        migration_dir = DatabaseMigrations.get_migration_dir()
        os.makedirs(migration_dir, exist_ok=True)
        
        # Create versions directory
        versions_dir = os.path.join(migration_dir, 'versions')
        os.makedirs(versions_dir, exist_ok=True)
        
        # Create alembic.ini if it doesn't exist
        alembic_ini_path = os.path.join(migration_dir, 'alembic.ini')
        if not os.path.exists(alembic_ini_path):
            alembic_ini_content = """
[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = 

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
            with open(alembic_ini_path, 'w') as f:
                f.write(alembic_ini_content.strip())
        
        logger.info("Migration directory initialized")

class CacheConfig:
    """Caching configuration for performance optimization"""
    
    @staticmethod
    def get_cache_config():
        """Get cache configuration"""
        cache_type = os.environ.get('CACHE_TYPE', 'simple')
        
        config = {
            'CACHE_TYPE': cache_type,
            'CACHE_DEFAULT_TIMEOUT': int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300')),
        }
        
        if cache_type == 'redis':
            config.update({
                'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
                'CACHE_KEY_PREFIX': 'pricing_intelligence:',
            })
        elif cache_type == 'memcached':
            config.update({
                'CACHE_MEMCACHED_SERVERS': os.environ.get('MEMCACHED_SERVERS', 'localhost:11211').split(','),
                'CACHE_KEY_PREFIX': 'pricing_intelligence:',
            })
        
        return config

class PerformanceConfig:
    """Performance optimization configuration"""
    
    @staticmethod
    def get_performance_config():
        """Get performance-related configuration"""
        return {
            # Database query optimization
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_pre_ping': True,
                'pool_recycle': 300,
            },
            
            # Request handling
            'MAX_CONTENT_LENGTH': int(os.environ.get('MAX_CONTENT_LENGTH', str(50 * 1024 * 1024))),  # 50MB
            'SEND_FILE_MAX_AGE_DEFAULT': int(os.environ.get('SEND_FILE_MAX_AGE_DEFAULT', '31536000')),  # 1 year
            
            # JSON handling
            'JSON_SORT_KEYS': False,  # Faster JSON serialization
            'JSONIFY_PRETTYPRINT_REGULAR': False,  # Compact JSON in production
            
            # Session configuration
            'PERMANENT_SESSION_LIFETIME': int(os.environ.get('SESSION_LIFETIME', '3600')),  # 1 hour
            
            # Security
            'SESSION_COOKIE_SECURE': os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true',
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Lax',
        }

class ScalabilityConfig:
    """Configuration for horizontal scaling and load balancing"""
    
    @staticmethod
    def get_wsgi_config():
        """Get WSGI server configuration for production"""
        return {
            'bind': f"0.0.0.0:{os.environ.get('PORT', '5001')}",
            'workers': int(os.environ.get('GUNICORN_WORKERS', '4')),
            'worker_class': os.environ.get('GUNICORN_WORKER_CLASS', 'sync'),
            'worker_connections': int(os.environ.get('GUNICORN_WORKER_CONNECTIONS', '1000')),
            'max_requests': int(os.environ.get('GUNICORN_MAX_REQUESTS', '1000')),
            'max_requests_jitter': int(os.environ.get('GUNICORN_MAX_REQUESTS_JITTER', '100')),
            'timeout': int(os.environ.get('GUNICORN_TIMEOUT', '30')),
            'keepalive': int(os.environ.get('GUNICORN_KEEPALIVE', '2')),
            'preload_app': True,
            'access_log_format': '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s',
        }
    
    @staticmethod
    def get_load_balancer_config():
        """Get load balancer configuration"""
        return {
            'health_check_path': '/health',
            'health_check_interval': int(os.environ.get('HEALTH_CHECK_INTERVAL', '30')),
            'health_check_timeout': int(os.environ.get('HEALTH_CHECK_TIMEOUT', '5')),
            'sticky_sessions': os.environ.get('STICKY_SESSIONS', 'false').lower() == 'true',
        }

class MonitoringConfig:
    """Configuration for monitoring and observability"""
    
    @staticmethod
    def get_monitoring_config():
        """Get monitoring configuration"""
        return {
            'ENABLE_METRICS': os.environ.get('ENABLE_METRICS', 'true').lower() == 'true',
            'METRICS_PORT': int(os.environ.get('METRICS_PORT', '9090')),
            'ENABLE_TRACING': os.environ.get('ENABLE_TRACING', 'false').lower() == 'true',
            'JAEGER_ENDPOINT': os.environ.get('JAEGER_ENDPOINT'),
            'LOG_LEVEL': os.environ.get('LOG_LEVEL', 'INFO'),
            'STRUCTURED_LOGGING': os.environ.get('STRUCTURED_LOGGING', 'true').lower() == 'true',
        }

