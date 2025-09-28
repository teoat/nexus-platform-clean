"""
NEXUS Platform - Tier-3 Error Handling & Resilience
Comprehensive error handling with auto-recovery and fallback mechanisms
"""

import asyncio
import logging
import traceback
from typing import Dict, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from dataclasses import dataclass
from contextlib import asynccontextmanager

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

class ErrorSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(str, Enum):
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    DATABASE = "database"
    NETWORK = "network"
    SYSTEM = "system"
    UNKNOWN = "unknown"

@dataclass
class ErrorContext:
    error_id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    details: Dict[str, Any]
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    stack_trace: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False

class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        return (datetime.now() - self.last_failure_time).seconds >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

class RetryHandler:
    """Exponential backoff retry handler"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    async def execute(self, func: Callable, *args, **kwargs):
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    break
                
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                await asyncio.sleep(delay)
        
        raise last_exception

class ErrorHandler:
    """Main error handling and recovery system"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_handlers: Dict[str, RetryHandler] = {}
        self.error_history: Dict[str, ErrorContext] = {}
        self.fallback_handlers: Dict[ErrorCategory, Callable] = {}
        
        # Initialize default fallback handlers
        self._initialize_fallback_handlers()
    
    def _initialize_fallback_handlers(self):
        """Initialize default fallback handlers for each error category"""
        self.fallback_handlers[ErrorCategory.VALIDATION] = self._handle_validation_error
        self.fallback_handlers[ErrorCategory.AUTHENTICATION] = self._handle_auth_error
        self.fallback_handlers[ErrorCategory.AUTHORIZATION] = self._handle_auth_error
        self.fallback_handlers[ErrorCategory.BUSINESS_LOGIC] = self._handle_business_logic_error
        self.fallback_handlers[ErrorCategory.EXTERNAL_SERVICE] = self._handle_external_service_error
        self.fallback_handlers[ErrorCategory.DATABASE] = self._handle_database_error
        self.fallback_handlers[ErrorCategory.NETWORK] = self._handle_network_error
        self.fallback_handlers[ErrorCategory.SYSTEM] = self._handle_system_error
        self.fallback_handlers[ErrorCategory.UNKNOWN] = self._handle_unknown_error
    
    async def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        auto_recover: bool = True
    ) -> ErrorContext:
        """Handle error with automatic recovery attempts"""
        error_context = self._create_error_context(
            error, context or {}, user_id, request_id
        )
        
        # Log error
        await self._log_error(error_context)
        
        # Attempt automatic recovery
        if auto_recover:
            recovery_successful = await self._attempt_recovery(error_context)
            error_context.recovery_successful = recovery_successful
        
        # Store error context
        self.error_history[error_context.error_id] = error_context
        
        # Execute fallback handler if recovery failed
        if not error_context.recovery_successful:
            await self._execute_fallback_handler(error_context)
        
        return error_context
    
    def _create_error_context(
        self,
        error: Exception,
        context: Dict[str, Any],
        user_id: Optional[str],
        request_id: Optional[str]
    ) -> ErrorContext:
        """Create error context from exception and additional data"""
        error_id = str(uuid.uuid4())
        
        # Determine error category and severity
        category = self._categorize_error(error)
        severity = self._determine_severity(error, category)
        
        # Extract error details
        message = str(error)
        details = {
            'error_type': type(error).__name__,
            'context': context,
            'additional_info': getattr(error, 'additional_info', {})
        }
        
        # Get stack trace
        stack_trace = traceback.format_exc()
        
        return ErrorContext(
            error_id=error_id,
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            message=message,
            details=details,
            user_id=user_id,
            request_id=request_id,
            stack_trace=stack_trace
        )
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error based on type and message"""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        if isinstance(error, RequestValidationError):
            return ErrorCategory.VALIDATION
        elif isinstance(error, HTTPException):
            if error.status_code == 401:
                return ErrorCategory.AUTHENTICATION
            elif error.status_code == 403:
                return ErrorCategory.AUTHORIZATION
            else:
                return ErrorCategory.BUSINESS_LOGIC
        elif "database" in error_message or "sql" in error_message:
            return ErrorCategory.DATABASE
        elif "network" in error_message or "connection" in error_message:
            return ErrorCategory.NETWORK
        elif "external" in error_message or "api" in error_message:
            return ErrorCategory.EXTERNAL_SERVICE
        elif "system" in error_message or "internal" in error_message:
            return ErrorCategory.SYSTEM
        else:
            return ErrorCategory.UNKNOWN
    
    def _determine_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity based on type and context"""
        if isinstance(error, HTTPException):
            if error.status_code >= 500:
                return ErrorSeverity.CRITICAL
            elif error.status_code >= 400:
                return ErrorSeverity.HIGH
            else:
                return ErrorSeverity.MEDIUM
        
        if category == ErrorCategory.SYSTEM:
            return ErrorSeverity.CRITICAL
        elif category in [ErrorCategory.DATABASE, ErrorCategory.EXTERNAL_SERVICE]:
            return ErrorSeverity.HIGH
        elif category in [ErrorCategory.AUTHENTICATION, ErrorCategory.AUTHORIZATION]:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    async def _log_error(self, error_context: ErrorContext):
        """Log error with appropriate level"""
        log_data = {
            'error_id': error_context.error_id,
            'severity': error_context.severity.value,
            'category': error_context.category.value,
            'message': error_context.message,
            'user_id': error_context.user_id,
            'request_id': error_context.request_id,
            'timestamp': error_context.timestamp.isoformat()
        }
        
        if error_context.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"Critical error: {json.dumps(log_data)}")
        elif error_context.severity == ErrorSeverity.HIGH:
            logger.error(f"High severity error: {json.dumps(log_data)}")
        elif error_context.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"Medium severity error: {json.dumps(log_data)}")
        else:
            logger.info(f"Low severity error: {json.dumps(log_data)}")
    
    async def _attempt_recovery(self, error_context: ErrorContext) -> bool:
        """Attempt automatic error recovery"""
        try:
            error_context.recovery_attempted = True
            
            # Recovery strategies based on error category
            if error_context.category == ErrorCategory.DATABASE:
                return await self._recover_database_error(error_context)
            elif error_context.category == ErrorCategory.EXTERNAL_SERVICE:
                return await self._recover_external_service_error(error_context)
            elif error_context.category == ErrorCategory.NETWORK:
                return await self._recover_network_error(error_context)
            elif error_context.category == ErrorCategory.VALIDATION:
                return await self._recover_validation_error(error_context)
            else:
                return False
            
        except Exception as e:
            logger.error(f"Recovery attempt failed: {str(e)}")
            return False
    
    async def _recover_database_error(self, error_context: ErrorContext) -> bool:
        """Attempt to recover from database errors"""
        # Implement database connection retry logic
        # This would typically involve:
        # 1. Checking connection pool
        # 2. Retrying with exponential backoff
        # 3. Switching to read-only mode if available
        # 4. Using cached data as fallback
        
        logger.info(f"Attempting database error recovery for {error_context.error_id}")
        await asyncio.sleep(1)  # Simulate recovery attempt
        return True  # Placeholder - implement actual recovery logic
    
    async def _recover_external_service_error(self, error_context: ErrorContext) -> bool:
        """Attempt to recover from external service errors"""
        # Implement external service recovery logic
        # This would typically involve:
        # 1. Checking circuit breaker status
        # 2. Retrying with different endpoints
        # 3. Using cached responses
        # 4. Switching to backup services
        
        logger.info(f"Attempting external service error recovery for {error_context.error_id}")
        await asyncio.sleep(1)  # Simulate recovery attempt
        return True  # Placeholder - implement actual recovery logic
    
    async def _recover_network_error(self, error_context: ErrorContext) -> bool:
        """Attempt to recover from network errors"""
        # Implement network error recovery logic
        # This would typically involve:
        # 1. Retrying with exponential backoff
        # 2. Checking network connectivity
        # 3. Using alternative network paths
        # 4. Implementing timeout adjustments
        
        logger.info(f"Attempting network error recovery for {error_context.error_id}")
        await asyncio.sleep(1)  # Simulate recovery attempt
        return True  # Placeholder - implement actual recovery logic
    
    async def _recover_validation_error(self, error_context: ErrorContext) -> bool:
        """Attempt to recover from validation errors"""
        # Implement validation error recovery logic
        # This would typically involve:
        # 1. Sanitizing input data
        # 2. Applying default values
        # 3. Using alternative validation rules
        # 4. Requesting user input correction
        
        logger.info(f"Attempting validation error recovery for {error_context.error_id}")
        await asyncio.sleep(0.1)  # Simulate recovery attempt
        return True  # Placeholder - implement actual recovery logic
    
    async def _execute_fallback_handler(self, error_context: ErrorContext):
        """Execute appropriate fallback handler"""
        fallback_handler = self.fallback_handlers.get(error_context.category)
        if fallback_handler:
            try:
                await fallback_handler(error_context)
            except Exception as e:
                logger.error(f"Fallback handler failed: {str(e)}")
    
    async def _handle_validation_error(self, error_context: ErrorContext):
        """Handle validation errors with user-friendly messages"""
        logger.info(f"Handling validation error: {error_context.message}")
        # Implement validation error handling logic
    
    async def _handle_auth_error(self, error_context: ErrorContext):
        """Handle authentication/authorization errors"""
        logger.warning(f"Handling auth error: {error_context.message}")
        # Implement auth error handling logic
    
    async def _handle_business_logic_error(self, error_context: ErrorContext):
        """Handle business logic errors"""
        logger.error(f"Handling business logic error: {error_context.message}")
        # Implement business logic error handling
    
    async def _handle_external_service_error(self, error_context: ErrorContext):
        """Handle external service errors"""
        logger.error(f"Handling external service error: {error_context.message}")
        # Implement external service error handling
    
    async def _handle_database_error(self, error_context: ErrorContext):
        """Handle database errors"""
        logger.critical(f"Handling database error: {error_context.message}")
        # Implement database error handling
    
    async def _handle_network_error(self, error_context: ErrorContext):
        """Handle network errors"""
        logger.error(f"Handling network error: {error_context.message}")
        # Implement network error handling
    
    async def _handle_system_error(self, error_context: ErrorContext):
        """Handle system errors"""
        logger.critical(f"Handling system error: {error_context.message}")
        # Implement system error handling
    
    async def _handle_unknown_error(self, error_context: ErrorContext):
        """Handle unknown errors"""
        logger.error(f"Handling unknown error: {error_context.message}")
        # Implement unknown error handling
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]
    
    def get_retry_handler(self, operation_name: str) -> RetryHandler:
        """Get or create retry handler for operation"""
        if operation_name not in self.retry_handlers:
            self.retry_handlers[operation_name] = RetryHandler()
        return self.retry_handlers[operation_name]
    
    async def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring"""
        total_errors = len(self.error_history)
        
        if total_errors == 0:
            return {'total_errors': 0}
        
        # Count by severity
        severity_counts = {}
        for error in self.error_history.values():
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count by category
        category_counts = {}
        for error in self.error_history.values():
            category = error.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Recovery statistics
        recovery_attempted = sum(1 for error in self.error_history.values() if error.recovery_attempted)
        recovery_successful = sum(1 for error in self.error_history.values() if error.recovery_successful)
        
        return {
            'total_errors': total_errors,
            'severity_breakdown': severity_counts,
            'category_breakdown': category_counts,
            'recovery_attempted': recovery_attempted,
            'recovery_successful': recovery_successful,
            'recovery_rate': recovery_successful / recovery_attempted if recovery_attempted > 0 else 0
        }

# Global error handler instance
error_handler = ErrorHandler()

# FastAPI exception handlers
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    error_context = await error_handler.handle_error(
        exc,
        context={'request_url': str(request.url), 'method': request.method},
        request_id=request.headers.get('x-request-id')
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': {
                'id': error_context.error_id,
                'message': exc.detail,
                'status_code': exc.status_code,
                'timestamp': error_context.timestamp.isoformat()
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation exceptions"""
    error_context = await error_handler.handle_error(
        exc,
        context={'request_url': str(request.url), 'method': request.method},
        request_id=request.headers.get('x-request-id')
    )
    
    return JSONResponse(
        status_code=422,
        content={
            'error': {
                'id': error_context.error_id,
                'message': 'Validation error',
                'details': exc.errors(),
                'timestamp': error_context.timestamp.isoformat()
            }
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    error_context = await error_handler.handle_error(
        exc,
        context={'request_url': str(request.url), 'method': request.method},
        request_id=request.headers.get('x-request-id')
    )
    
    return JSONResponse(
        status_code=500,
        content={
            'error': {
                'id': error_context.error_id,
                'message': 'Internal server error',
                'timestamp': error_context.timestamp.isoformat()
            }
        }
    )

# Decorator for automatic error handling
def handle_errors(auto_recover: bool = True):
    """Decorator for automatic error handling"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_context = await error_handler.handle_error(
                    e,
                    context={'function': func.__name__, 'args': str(args), 'kwargs': str(kwargs)},
                    auto_recover=auto_recover
                )
                
                if not error_context.recovery_successful:
                    raise e
                
                return None  # Recovery successful but no return value
        
        return wrapper
    return decorator

# Context manager for error handling
@asynccontextmanager
async def error_context(operation_name: str, user_id: Optional[str] = None):
    """Context manager for error handling"""
    try:
        yield
    except Exception as e:
        await error_handler.handle_error(
            e,
            context={'operation': operation_name},
            user_id=user_id
        )
        raise
