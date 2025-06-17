"""
Comprehensive error handling and resilience framework
"""

import logging
import traceback
import functools
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from flask import jsonify, request
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ErrorCodes:
    """Standardized error codes for the application"""
    
    # Input validation errors (1000-1999)
    INVALID_INPUT = 1001
    MISSING_REQUIRED_FIELD = 1002
    INVALID_VIN_FORMAT = 1003
    INVALID_PRICE_RANGE = 1004
    INVALID_YEAR_RANGE = 1005
    INVALID_MILEAGE_RANGE = 1006
    
    # Database errors (2000-2999)
    DATABASE_CONNECTION_ERROR = 2001
    DATABASE_QUERY_ERROR = 2002
    RECORD_NOT_FOUND = 2003
    DUPLICATE_RECORD = 2004
    DATABASE_TIMEOUT = 2005
    
    # External service errors (3000-3999)
    AI_SERVICE_UNAVAILABLE = 3001
    AI_SERVICE_TIMEOUT = 3002
    AI_SERVICE_QUOTA_EXCEEDED = 3003
    VIN_DECODER_ERROR = 3004
    EXTERNAL_API_ERROR = 3005
    
    # Business logic errors (4000-4999)
    INSUFFICIENT_DATA = 4001
    CALCULATION_ERROR = 4002
    MATCHING_ERROR = 4003
    SCORING_ERROR = 4004
    
    # System errors (5000-5999)
    INTERNAL_SERVER_ERROR = 5001
    SERVICE_UNAVAILABLE = 5002
    RATE_LIMIT_EXCEEDED = 5003
    MEMORY_ERROR = 5004
    DISK_SPACE_ERROR = 5005

class ApplicationError(Exception):
    """Base application error class"""
    
    def __init__(self, message: str, error_code: int = ErrorCodes.INTERNAL_SERVER_ERROR, 
                 details: Optional[Dict] = None, cause: Optional[Exception] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response"""
        return {
            'error': True,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

class ValidationError(ApplicationError):
    """Input validation error"""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        details = {}
        if field:
            details['field'] = field
        if value is not None:
            details['invalid_value'] = str(value)
        
        super().__init__(
            message=message,
            error_code=ErrorCodes.INVALID_INPUT,
            details=details
        )

class DatabaseError(ApplicationError):
    """Database operation error"""
    
    def __init__(self, message: str, operation: str = None, table: str = None, cause: Exception = None):
        details = {}
        if operation:
            details['operation'] = operation
        if table:
            details['table'] = table
        
        super().__init__(
            message=message,
            error_code=ErrorCodes.DATABASE_QUERY_ERROR,
            details=details,
            cause=cause
        )

class ExternalServiceError(ApplicationError):
    """External service error"""
    
    def __init__(self, message: str, service: str = None, status_code: int = None, cause: Exception = None):
        details = {}
        if service:
            details['service'] = service
        if status_code:
            details['status_code'] = status_code
        
        super().__init__(
            message=message,
            error_code=ErrorCodes.EXTERNAL_API_ERROR,
            details=details,
            cause=cause
        )

class BusinessLogicError(ApplicationError):
    """Business logic error"""
    
    def __init__(self, message: str, operation: str = None, cause: Exception = None):
        details = {}
        if operation:
            details['operation'] = operation
        
        super().__init__(
            message=message,
            error_code=ErrorCodes.CALCULATION_ERROR,
            details=details,
            cause=cause
        )

class InputValidator:
    """Comprehensive input validation"""
    
    @staticmethod
    def validate_vin(vin: str) -> str:
        """Validate VIN format"""
        if not vin:
            raise ValidationError("VIN is required", field="vin")
        
        vin = vin.strip().upper()
        
        if len(vin) != 17:
            raise ValidationError(
                "VIN must be exactly 17 characters",
                field="vin",
                value=vin
            )
        
        # Check for invalid characters (I, O, Q are not allowed in VINs)
        invalid_chars = set('IOQ')
        if any(char in invalid_chars for char in vin):
            raise ValidationError(
                "VIN contains invalid characters (I, O, Q not allowed)",
                field="vin",
                value=vin
            )
        
        # Basic alphanumeric check
        if not vin.isalnum():
            raise ValidationError(
                "VIN must contain only letters and numbers",
                field="vin",
                value=vin
            )
        
        return vin
    
    @staticmethod
    def validate_price(price: Any, field_name: str = "price") -> float:
        """Validate price value"""
        if price is None:
            raise ValidationError(f"{field_name} is required", field=field_name)
        
        try:
            price = float(price)
        except (ValueError, TypeError):
            raise ValidationError(
                f"{field_name} must be a valid number",
                field=field_name,
                value=price
            )
        
        if price < 0:
            raise ValidationError(
                f"{field_name} cannot be negative",
                field=field_name,
                value=price
            )
        
        if price > 1000000:  # $1M limit
            raise ValidationError(
                f"{field_name} exceeds maximum allowed value",
                field=field_name,
                value=price
            )
        
        return price
    
    @staticmethod
    def validate_year(year: Any) -> int:
        """Validate vehicle year"""
        if year is None:
            raise ValidationError("Year is required", field="year")
        
        try:
            year = int(year)
        except (ValueError, TypeError):
            raise ValidationError(
                "Year must be a valid integer",
                field="year",
                value=year
            )
        
        current_year = datetime.now().year
        
        if year < 1900:
            raise ValidationError(
                "Year cannot be before 1900",
                field="year",
                value=year
            )
        
        if year > current_year + 2:  # Allow 2 years in future for model years
            raise ValidationError(
                f"Year cannot be more than 2 years in the future",
                field="year",
                value=year
            )
        
        return year
    
    @staticmethod
    def validate_mileage(mileage: Any) -> int:
        """Validate vehicle mileage"""
        if mileage is None:
            raise ValidationError("Mileage is required", field="mileage")
        
        try:
            mileage = int(mileage)
        except (ValueError, TypeError):
            raise ValidationError(
                "Mileage must be a valid integer",
                field="mileage",
                value=mileage
            )
        
        if mileage < 0:
            raise ValidationError(
                "Mileage cannot be negative",
                field="mileage",
                value=mileage
            )
        
        if mileage > 1000000:  # 1M miles limit
            raise ValidationError(
                "Mileage exceeds reasonable maximum",
                field="mileage",
                value=mileage
            )
        
        return mileage
    
    @staticmethod
    def validate_string_field(value: Any, field_name: str, required: bool = True, 
                            max_length: int = 255, min_length: int = 1) -> Optional[str]:
        """Validate string field"""
        if value is None or value == '':
            if required:
                raise ValidationError(f"{field_name} is required", field=field_name)
            return None
        
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip()
        
        if len(value) < min_length:
            raise ValidationError(
                f"{field_name} must be at least {min_length} characters",
                field=field_name,
                value=value
            )
        
        if len(value) > max_length:
            raise ValidationError(
                f"{field_name} cannot exceed {max_length} characters",
                field=field_name,
                value=value
            )
        
        return value
    
    @staticmethod
    def validate_pagination(page: Any = None, per_page: Any = None) -> tuple[int, int]:
        """Validate pagination parameters"""
        # Default values
        default_page = 1
        default_per_page = 20
        max_per_page = 100
        
        # Validate page
        if page is not None:
            try:
                page = int(page)
                if page < 1:
                    raise ValidationError("Page must be 1 or greater", field="page", value=page)
            except (ValueError, TypeError):
                raise ValidationError("Page must be a valid integer", field="page", value=page)
        else:
            page = default_page
        
        # Validate per_page
        if per_page is not None:
            try:
                per_page = int(per_page)
                if per_page < 1:
                    raise ValidationError("Per page must be 1 or greater", field="per_page", value=per_page)
                if per_page > max_per_page:
                    raise ValidationError(
                        f"Per page cannot exceed {max_per_page}",
                        field="per_page",
                        value=per_page
                    )
            except (ValueError, TypeError):
                raise ValidationError("Per page must be a valid integer", field="per_page", value=per_page)
        else:
            per_page = default_per_page
        
        return page, per_page

class CircuitBreaker:
    """Circuit breaker pattern for external service calls"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
            else:
                raise ExternalServiceError(
                    "Service temporarily unavailable (circuit breaker open)",
                    service=func.__name__
                )
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset circuit breaker
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
            
            raise e

class RetryHandler:
    """Retry handler with exponential backoff"""
    
    @staticmethod
    def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, 
                          max_delay: float = 60.0, backoff_factor: float = 2.0):
        """Decorator for retrying functions with exponential backoff"""
        
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        
                        if attempt == max_retries:
                            # Last attempt failed
                            break
                        
                        # Calculate delay with exponential backoff
                        delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                        
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        
                        time.sleep(delay)
                
                # All retries failed
                raise ExternalServiceError(
                    f"Operation failed after {max_retries + 1} attempts",
                    service=func.__name__,
                    cause=last_exception
                )
            
            return wrapper
        return decorator

class ErrorHandler:
    """Global error handler for Flask applications"""
    
    @staticmethod
    def register_error_handlers(app):
        """Register error handlers with Flask app"""
        
        @app.errorhandler(ApplicationError)
        def handle_application_error(error):
            logger.error(f"Application error: {error.message}", exc_info=error.cause)
            return jsonify(error.to_dict()), 400
        
        @app.errorhandler(ValidationError)
        def handle_validation_error(error):
            logger.warning(f"Validation error: {error.message}")
            return jsonify(error.to_dict()), 400
        
        @app.errorhandler(DatabaseError)
        def handle_database_error(error):
            logger.error(f"Database error: {error.message}", exc_info=error.cause)
            return jsonify(error.to_dict()), 500
        
        @app.errorhandler(ExternalServiceError)
        def handle_external_service_error(error):
            logger.error(f"External service error: {error.message}", exc_info=error.cause)
            return jsonify(error.to_dict()), 503
        
        @app.errorhandler(BusinessLogicError)
        def handle_business_logic_error(error):
            logger.error(f"Business logic error: {error.message}", exc_info=error.cause)
            return jsonify(error.to_dict()), 422
        
        @app.errorhandler(404)
        def handle_not_found(error):
            return jsonify({
                'error': True,
                'error_code': ErrorCodes.RECORD_NOT_FOUND,
                'message': 'Resource not found',
                'details': {'path': request.path},
                'timestamp': datetime.utcnow().isoformat()
            }), 404
        
        @app.errorhandler(405)
        def handle_method_not_allowed(error):
            return jsonify({
                'error': True,
                'error_code': ErrorCodes.INVALID_INPUT,
                'message': 'Method not allowed',
                'details': {
                    'method': request.method,
                    'path': request.path
                },
                'timestamp': datetime.utcnow().isoformat()
            }), 405
        
        @app.errorhandler(500)
        def handle_internal_server_error(error):
            logger.error(f"Internal server error: {str(error)}", exc_info=True)
            return jsonify({
                'error': True,
                'error_code': ErrorCodes.INTERNAL_SERVER_ERROR,
                'message': 'Internal server error',
                'details': {},
                'timestamp': datetime.utcnow().isoformat()
            }), 500

def safe_execute(func: Callable, *args, **kwargs) -> tuple[Any, Optional[Exception]]:
    """Safely execute a function and return result or exception"""
    try:
        result = func(*args, **kwargs)
        return result, None
    except Exception as e:
        logger.error(f"Error executing {func.__name__}: {str(e)}", exc_info=True)
        return None, e

def log_performance(func):
    """Decorator to log function performance"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > 5.0:  # Log slow operations
                logger.warning(f"Slow operation: {func.__name__} took {execution_time:.2f}s")
            else:
                logger.debug(f"Performance: {func.__name__} took {execution_time:.2f}s")
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error in {func.__name__} after {execution_time:.2f}s: {str(e)}")
            raise
    
    return wrapper

# Global instances
circuit_breaker = CircuitBreaker()
retry_handler = RetryHandler()

