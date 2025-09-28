import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from pathlib import Path
try:
    import redis
except ImportError:
    redis = None
try:
    from .conflict_detection import ConflictDetector, ConflictType, ConflictSeverity
except ImportError:
    # Mock classes if conflict_detection module is not available
    class ConflictDetector:
        def __init__(self): pass
        def detect_conflicts(self, *args, **kwargs): return []
    class ConflictType:
        NAMING = "naming"
        FUNCTIONALITY = "functionality"
    class ConflictSeverity:
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"

try:
    from .audit_logging import AuditLogQueryEngine, AuditLogLevel, OperationType
except ImportError:
    # Mock classes if audit_logging module is not available
    class AuditLogQueryEngine:
        def __init__(self): pass
        def log_operation(self, *args, **kwargs): pass
    class AuditLogLevel:
        INFO = "info"
        WARNING = "warning"
        ERROR = "error"
    class OperationType:
        CREATE = "create"
        UPDATE = "update"
        DELETE = "delete"
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, start_http_server
except ImportError:
    # Mock prometheus_client if not available
    class MockCounter:
        def __init__(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
        def inc(self, *args, **kwargs): pass
    class MockHistogram:
        def __init__(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
        def observe(self, *args, **kwargs): pass
    class MockGauge:
        def __init__(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
        def set(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
        def dec(self, *args, **kwargs): pass
    
    Counter = MockCounter
    Histogram = MockHistogram
    Gauge = MockGauge
    generate_latest = lambda: b""
    start_http_server = lambda *args, **kwargs: None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AliasType(Enum):
    """Types of aliases supported by the SSOT registry."""
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    CONTEXTUAL = "contextual"
    MIGRATION = "migration"
    SYSTEM = "system"
    APPLICATION = "application"
    FRENLY_AI = "frenly_ai"

class AliasStatus(Enum):
    """Status of aliases"""
    ACTIVE = "active"
    EXPIRED = "expired"
    DEPRECATED = "deprecated"
    PENDING_APPROVAL = "pending_approval"

class ValidationError(Exception):
    """Validation error for aliases"""
    pass

class AliasNotFoundError(Exception):
    """Alias not found error"""
    pass

class ConflictError(Exception):
    """Alias conflict error"""
    pass

class ExpiredAliasError(Exception):
    """Expired alias error"""
    pass

@dataclass
class SSOTAnchor:
    """SSOT Anchor definition"""
    id: str
    family: str
    description: str
    format: str
    source_hint: str
    owner: str
    version: str
    centrality_score: float
    modification_policy: str
    validation_rules: List[str]
    generates: List[str]
    aliasing: Dict[str, Any]
    registered_at: str = ""

    def __post_init__(self):
        if not self.registered_at:
            self.registered_at = datetime.utcnow().isoformat()

@dataclass
class AliasDefinition:
    """Alias definition"""
    name: str
    canonical: str
    context: str
    type: AliasType
    status: AliasStatus
    description: str
    created_by: str
    created_at: str
    expires_at: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    last_updated: str = ""

    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.utcnow().isoformat()
        if isinstance(self.type, str):
            self.type = AliasType(self.type)
        if isinstance(self.status, str):
            self.status = AliasStatus(self.status)

    def is_expired(self) -> bool:
        if self.expires_at:
            return datetime.utcnow() > datetime.fromisoformat(self.expires_at)
        return False

@dataclass
class AuditEntry:
    """Audit log entry for SSOT changes"""
    timestamp: str
    operation: str
    entity_type: str
    entity_id: str
    details: Dict[str, Any]
    performed_by: str
    context: str

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()

class AliasManager:
    """Manages alias operations and provides a simplified interface to the SSOT registry."""
    
    def __init__(self, registry_instance: Optional['SSOTRegistry'] = None):
        self.registry = registry_instance or SSOTRegistry()
    
    async def create_alias(self, name: str, canonical: str, context: str = "default", 
                          alias_type: AliasType = AliasType.PERMANENT, 
                          description: str = "", ttl: Optional[int] = None) -> bool:
        """Create a new alias."""
        try:
            await self.registry.add_alias(
                alias_name=name,
                canonical_name=canonical,
                context=context,
                alias_type=alias_type,
                description=description,
                ttl=ttl
            )
            return True
        except Exception as e:
            logger.error(f"Failed to create alias {name}: {e}")
            return False
    
    async def resolve_alias(self, alias_name: str, context: str = "default") -> Optional[str]:
        """Resolve an alias to its canonical name."""
        try:
            result = await self.registry.resolve_alias(alias_name, context)
            return result.get('canonical_name') if result else None
        except Exception as e:
            logger.error(f"Failed to resolve alias {alias_name}: {e}")
            return None
    
    async def delete_alias(self, alias_name: str, context: str = "default") -> bool:
        """Delete an alias."""
        try:
            await self.registry.remove_alias(alias_name, context)
            return True
        except Exception as e:
            logger.error(f"Failed to delete alias {alias_name}: {e}")
            return False
    
    async def list_aliases(self, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all aliases, optionally filtered by context."""
        try:
            return await self.registry.list_aliases(context)
        except Exception as e:
            logger.error(f"Failed to list aliases: {e}")
            return []


class SSOTRegistry:
    def __init__(self, config_path: Path = Path("config/ssot_registry.json"),
                 governance_path: Path = Path("config/alias_governance.yaml"),
                 caching_config_path: Path = Path("config/caching.yaml")):
        self.config_path = config_path
        self.governance_path = governance_path
        self.caching_config_path = caching_config_path
        self.anchors: Dict[str, SSOTAnchor] = {}
        self.aliases: Dict[str, Dict[str, AliasDefinition]] = {} # context -> alias_name -> AliasDefinition
        self.audit_log: List[AuditEntry] = []
        self.governance_rules: Dict[str, Any] = {}
        self.lock = asyncio.Lock() # For concurrent access control
        self._dirty = False # Flag to indicate if registry has unsaved changes
        self.redis_client: Optional[redis.Redis] = None
        self.cache_ttl: int = 3600 # Default TTL for cache entries

        # Initialize conflict detection and audit logging
        self.conflict_detector = ConflictDetector(self)
        self.audit_engine = AuditLogQueryEngine()

        # Load existing data
        self._load_registry()
        self._load_governance_rules()
        self._load_caching_config()

        # Start background tasks (only if event loop is running)
        try:
            asyncio.get_running_loop()
            asyncio.create_task(self._cleanup_expired_aliases())
            asyncio.create_task(self._periodic_save())
            asyncio.create_task(self._periodic_conflict_detection())
        except RuntimeError:
            # No event loop running, skip background tasks
            pass

        self._initialize_metrics()
        try:
            # Start Prometheus HTTP server for metrics
            start_http_server(8002) # Port 8002 for metrics
            logger.info("Prometheus metrics server started on port 8002")
        except Exception as e:
            logger.error(f"Error starting Prometheus metrics server: {e}")

    def _load_registry(self):
        """Load registry data from persistent storage"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    # Handle both list and dict formats for anchors
                    anchors_data = data.get('anchors', {})
                    if isinstance(anchors_data, list):
                        self.anchors = {anchor['id']: SSOTAnchor(**anchor) for anchor in anchors_data}
                    else:
                        self.anchors = {k: SSOTAnchor(**v) for k, v in anchors_data.items()}
                    self.aliases = {}
                    for context, aliases_data in data.get('aliases', {}).items():
                        self.aliases[context] = {k: AliasDefinition(**v) for k, v in aliases_data.items()}
                    self.audit_log = [AuditEntry(**v) for v in data.get('audit_log', [])]
                logger.info(f"SSOT Registry loaded from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading SSOT Registry: {e}")

    def _save_registry(self):
        """Save registry data to persistent storage if dirty"""
        if not self._dirty:
            return

        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump({
                    'anchors': {k: asdict(v) for k, v in self.anchors.items()},
                    'aliases': {context: {k: asdict(v) for k, v in aliases.items()} for context, aliases in self.aliases.items()},
                    'audit_log': [asdict(v) for v in self.audit_log]
                }, f, indent=2)
            self._dirty = False
            logger.info(f"SSOT Registry saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving SSOT Registry: {e}")

    def _load_governance_rules(self):
        """Load governance rules from YAML configuration"""
        try:
            if self.governance_path.exists():
                import yaml
                with open(self.governance_path, 'r') as f:
                    self.governance_rules = yaml.safe_load(f).get('alias_governance', {})
                logger.info(f"Governance rules loaded from {self.governance_path}")
            else:
                logger.warning(f"Governance file not found at {self.governance_path}. Using default empty rules.")
        except Exception as e:
            logger.error(f"Error loading governance rules: {e}")

    def _load_caching_config(self):
        """Load caching configuration from YAML file and initialize Redis client."""
        try:
            if redis is None:
                logger.warning("redis not available. Caching disabled.")
                self.redis_client = None
                return

            if self.caching_config_path.exists():
                import yaml
                with open(self.caching_config_path, 'r') as f:
                    caching_config = yaml.safe_load(f).get('redis', {})
                if caching_config.get('host') and caching_config.get('port'):
                    self.redis_client = redis.from_url(
                        f"redis://{caching_config['host']}:{caching_config['port']}/{caching_config.get('db', 0)}",
                        decode_responses=True
                    )
                    self.cache_ttl = caching_config.get('ttl', 3600)
                    logger.info(f"Redis client initialized for caching with TTL: {self.cache_ttl}s")
                else:
                    logger.warning("Redis configuration incomplete in caching.yaml. Caching disabled.")
            else:
                logger.warning(f"Caching config file not found at {self.caching_config_path}. Caching disabled.")
        except Exception as e:
            logger.error(f"Error loading caching configuration or initializing Redis: {e}")
            self.redis_client = None # Ensure client is None on error
    
    def _initialize_metrics(self):
        """Initializes Prometheus metrics based on configuration."""
        from prometheus_client import REGISTRY

        def get_or_create_counter(name, description, labelnames):
            try:
                return Counter(name, description, labelnames)
            except ValueError:
                # Metric already exists, get it from registry
                return REGISTRY._names_to_collectors[name]

        def get_or_create_histogram(name, description, labelnames, buckets=None):
            try:
                return Histogram(name, description, labelnames, buckets=buckets)
            except ValueError:
                # Metric already exists, get it from registry
                return REGISTRY._names_to_collectors[name]

        def get_or_create_gauge(name, description, labelnames):
            try:
                return Gauge(name, description, labelnames)
            except ValueError:
                # Metric already exists, get it from registry
                return REGISTRY._names_to_collectors[name]

        self.metrics = {
            "ssot_alias_creations_total": get_or_create_counter(
                "ssot_alias_creations_total",
                "Total number of SSOT alias creation attempts.",
                ["status", "context"]
            ),
            "ssot_alias_updates_total": get_or_create_counter(
                "ssot_alias_updates_total",
                "Total number of SSOT alias update attempts.",
                ["status", "context"]
            ),
            "ssot_alias_deactivations_total": get_or_create_counter(
                "ssot_alias_deactivations_total",
                "Total number of SSOT alias deactivation attempts.",
                ["status", "context"]
            ),
            "ssot_alias_resolutions_total": get_or_create_counter(
                "ssot_alias_resolutions_total",
                "Total number of SSOT alias resolution attempts.",
                ["status", "context"]
            ),
            "ssot_alias_resolution_duration_seconds": get_or_create_histogram(
                "ssot_alias_resolution_duration_seconds",
                "Histogram of SSOT alias resolution durations.",
                ["context"],
                buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0]
            ),
            "ssot_active_aliases_count": get_or_create_gauge(
                "ssot_active_aliases_count",
                "Current number of active SSOT aliases.",
                ["context"]
            ),
            "ssot_expired_aliases_count": get_or_create_gauge(
                "ssot_expired_aliases_count",
                "Current number of expired SSOT aliases.",
                ["context"]
            ),
            "ssot_validation_failures_total": get_or_create_counter(
                "ssot_validation_failures_total",
                "Total number of SSOT validation failures.",
                ["rule", "operation"]
            ),
            "ssot_audit_log_entries_total": get_or_create_counter(
                "ssot_audit_log_entries_total",
                "Total number of audit log entries recorded for SSOT operations.",
                ["action"]
            ),
        }
        logger.info("Prometheus metrics initialized.")

    async def register_anchor(self, anchor_id: str, config: Dict[str, Any]):
        """Register a new SSOT anchor"""
        async with self.lock:
            try:
                if anchor_id in self.anchors:
                    raise ConflictError(f"Anchor '{anchor_id}' already exists.")
                anchor = SSOTAnchor(id=anchor_id, **config)
                self.anchors[anchor_id] = anchor
                self._log_operation("register_anchor", "SSOTAnchor", anchor_id, {"config": config}, "system")
                self._dirty = True # Mark registry as dirty
                self.metrics["ssot_alias_creations_total"].labels(status="success", context="system").inc()
                self.metrics["ssot_active_aliases_count"].labels(context="system").inc() # Assuming anchors are aliases in a broad sense
                logger.info(f"Registered SSOT anchor: {anchor_id}")
                return anchor
            except Exception as e:
                self.metrics["ssot_alias_creations_total"].labels(status="failure", context="system").inc()
                raise e

    async def get_anchor(self, anchor_id: str) -> Optional[SSOTAnchor]:
        """Retrieve an SSOT anchor by its ID, utilizing cache."""
        async with self.lock:
            if self.redis_client:
                cache_key = self._get_cache_key("anchor", anchor_id)
                cached_anchor = await self.redis_client.get(cache_key)
                if cached_anchor:
                    logger.debug(f"Cache hit for anchor: {anchor_id}")
                    return SSOTAnchor(**json.loads(cached_anchor))

            anchor = self.anchors.get(anchor_id)
            if anchor and self.redis_client:
                await self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(asdict(anchor)))
                logger.debug(f"Cached anchor: {anchor_id}")
            return anchor

    async def add_alias(self, alias_name: str, canonical_name: str, context: str,
                        alias_type: AliasType, description: str, created_by: str,
                        expires_in_days: Optional[int] = None,
                        requires_approval: bool = False) -> AliasDefinition:
        """Add a new alias for an anchor, with governance validation."""
        async with self.lock:
            try:
                if context not in self.aliases:
                    self.aliases[context] = {}

                if alias_name in self.aliases[context]:
                    raise ConflictError(f"Alias '{alias_name}' already exists in context '{context}'.")

                if canonical_name not in self.anchors:
                    raise AliasNotFoundError(f"Canonical anchor '{canonical_name}' not found.")

                # Apply governance rules
                self._validate_alias_governance(alias_name, context, alias_type, canonical_name, expires_in_days)

                expires_at = None
                if expires_in_days:
                    expires_at = (datetime.utcnow() + timedelta(days=expires_in_days)).isoformat()
                elif alias_type == AliasType.TEMPORARY:
                    default_ttl = self.governance_rules.get('rules', {}).get('expiration', {}).get('default_ttl', '90d')
                    days = self._parse_duration_to_days(default_ttl)
                    expires_at = (datetime.utcnow() + timedelta(days=days)).isoformat()

                status = AliasStatus.PENDING_APPROVAL if requires_approval else AliasStatus.ACTIVE

                alias_def = AliasDefinition(
                    name=alias_name,
                    canonical=canonical_name,
                    context=context,
                    type=alias_type,
                    status=status,
                    description=description,
                    created_by=created_by,
                    created_at=datetime.utcnow().isoformat(),
                    expires_at=expires_at
                )
                self.aliases[context][alias_name] = alias_def
                self._log_operation("add_alias", "AliasDefinition", alias_name, asdict(alias_def), created_by, context)
                self._dirty = True # Mark registry as dirty
                self.metrics["ssot_alias_creations_total"].labels(status="success", context=context).inc()
                self.metrics["ssot_active_aliases_count"].labels(context=context).inc()
                logger.info(f"Added alias '{alias_name}' for '{canonical_name}' in context '{context}' with status '{status.value}'")
                return alias_def
            except Exception as e:
                self.metrics["ssot_alias_creations_total"].labels(status="failure", context=context).inc()
                raise e

    async def resolve_alias(self, alias_name: str, context: str) -> str:
        """Resolve an alias to its canonical name, utilizing cache."""
        async with self.lock:
            with self.metrics["ssot_alias_resolution_duration_seconds"].labels(context=context).time():
                try:
                    if self.redis_client:
                        cache_key = self._get_cache_key("resolved_alias", alias_name, context)
                        cached_canonical = await self.redis_client.get(cache_key)
                        if cached_canonical:
                            logger.debug(f"Cache hit for resolved alias: {alias_name} in context {context}")
                            self.metrics["ssot_alias_resolutions_total"].labels(status="cache_hit", context=context).inc()
                            # Handle both bytes (without decode_responses) and str (with decode_responses)
                            if isinstance(cached_canonical, bytes):
                                return cached_canonical.decode('utf-8')
                            return cached_canonical

                    if context not in self.aliases or alias_name not in self.aliases[context]:
                        raise AliasNotFoundError(f"Alias '{alias_name}' not found in context '{context}'.")

                    alias_def = self.aliases[context][alias_name]

                    if alias_def.status != AliasStatus.ACTIVE:
                        raise ValidationError(f"Alias '{alias_name}' is not active (status: {alias_def.status.value}).")

                    if alias_def.is_expired():
                        raise ExpiredAliasError(f"Alias '{alias_name}' has expired.")

                    self._log_operation("resolve_alias", "AliasDefinition", alias_name, {"resolved_to": alias_def.canonical}, "system", context)
                    
                    if self.redis_client:
                        await self.redis_client.setex(cache_key, self.cache_ttl, alias_def.canonical)
                        logger.debug(f"Cached resolved alias: {alias_name} in context {context}")
                    
                    self.metrics["ssot_alias_resolutions_total"].labels(status="success", context=context).inc()
                    return alias_def.canonical
                except Exception as e:
                    status = "failure"
                    if isinstance(e, AliasNotFoundError):
                        status = "not_found"
                    elif isinstance(e, ExpiredAliasError):
                        status = "expired"
                    elif isinstance(e, ValidationError):
                        status = "validation_error"
                    self.metrics["ssot_alias_resolutions_total"].labels(status=status, context=context).inc()
                    raise e

    SENSITIVE_KEYS = ["password", "api_key", "secret", "token"] # Example sensitive keys

    def _log_operation(self, operation: str, entity_type: str, entity_id: str, details: Dict[str, Any], performed_by: str, context: str = "system"):
        """Internal method to log operations, with sensitive data sanitization."""
        sanitized_details = {k: v for k, v in details.items() if k not in self.SENSITIVE_KEYS}
        
        entry = AuditEntry(
            timestamp=datetime.utcnow().isoformat(),
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            details=sanitized_details,
            performed_by=performed_by,
            context=context
        )
        self.audit_log.append(entry)
        self.metrics["ssot_audit_log_entries_total"].labels(action=operation).inc()
        
        # Also log to the audit engine
        try:
            asyncio.create_task(self.audit_engine.log_operation(
                operation=operation,
                entity_type=entity_type,
                entity_id=entity_id,
                details=sanitized_details,
                performed_by=performed_by,
                context=context,
                log_level=AuditLogLevel.INFO
            ))
        except Exception as e:
            logger.error(f"Failed to log operation to audit engine: {e}")

    def _validate_alias_governance(self, alias_name: str, context: str, alias_type: AliasType, canonical_name: str, expires_in_days: Optional[int] = None):
        """Validate alias against governance rules."""
        try:
            # Basic validation - can be expanded
            if not alias_name or not context:
                raise ValidationError("Alias name and context cannot be empty.")
            # Add more complex governance rules here
            # Example: Check if canonical_name exists in anchors
            if canonical_name not in self.anchors:
                raise ValidationError(f"Canonical anchor '{canonical_name}' does not exist.")
            
            # Example: Prevent certain alias types in specific contexts
            if context == "global" and alias_type == AliasType.TEMPORARY:
                raise ValidationError("Temporary aliases are not allowed in the 'global' context.")

            # Placeholder for additional compliance checks
            # Example: Ensure all aliases have an owner for GDPR compliance
            if not self.anchors[canonical_name].owner:
                raise ValidationError(f"SSOT Anchor '{canonical_name}' must have an owner for compliance.")
            
            # Example: Check data retention policies for specific alias types
            if alias_type == AliasType.MIGRATION and expires_in_days is None:
                raise ValidationError("Migration aliases must have an expiration date for data retention compliance.")

        except ValidationError as e:
            self.metrics["ssot_validation_failures_total"].labels(rule="governance_check", operation="add_alias").inc()
            self._log_operation(
                "security_event",
                "ValidationError",
                alias_name,
                {"reason": str(e), "context": context, "alias_type": alias_type.value, "canonical_name": canonical_name},
                "system", # Or actual user if available
                context
            )
            raise e

    def _parse_duration_to_days(self, duration_str: str) -> int:
        """Parses a duration string (e.g., '90d', '1y') into days."""
        if duration_str.endswith('d'):
            return int(duration_str[:-1])
        elif duration_str.endswith('w'):
            return int(duration_str[:-1]) * 7
        elif duration_str.endswith('m'): # months
            return int(duration_str[:-1]) * 30 # Approximation
        elif duration_str.endswith('y'):
            return int(duration_str[:-1]) * 365 # Approximation
        return 0 # Default to no expiration

    def _get_cache_key(self, prefix: str, *args) -> str:
        """Generates a consistent cache key."""
        return f"{prefix}:" + ":".join(str(arg) for arg in args)

    async def _periodic_save(self, interval_seconds: int = 300):
        """Periodically saves the registry if there are unsaved changes."""
        while True:
            await asyncio.sleep(interval_seconds)
            async with self.lock:
                if self._dirty:
                    self._save_registry()

    async def _cleanup_expired_aliases(self):
        """Background task to periodically clean up expired aliases."""
        while True:
            await asyncio.sleep(3600) # Check every hour
            async with self.lock:
                logger.info("Running expired alias cleanup...")
                changes_made = False
                for context in list(self.aliases.keys()): # Iterate over a copy of keys
                    aliases_in_context = self.aliases[context]
                    for alias_name in list(aliases_in_context.keys()): # Iterate over a copy of keys
                        alias_def = aliases_in_context[alias_name]
                        if alias_def.is_expired():
                            del aliases_in_context[alias_name]
                            self._log_operation("remove_expired_alias", "AliasDefinition", alias_name, asdict(alias_def), "system", context)
                            self.metrics["ssot_expired_aliases_count"].labels(context=context).inc()
                            self.metrics["ssot_active_aliases_count"].labels(context=context).dec()
                            logger.info(f"Removed expired alias '{alias_name}' from context '{context}'.")
                            changes_made = True
                    if not aliases_in_context: # Remove context if empty
                        del self.aliases[context]

                if changes_made:
                    self._dirty = True
                    # Update gauges for active and expired aliases
                    for context, aliases_in_context in self.aliases.items():
                        self.metrics["ssot_active_aliases_count"].labels(context=context).set(len(aliases_in_context))
                    logger.info("Expired alias cleanup completed. Registry marked as dirty.")
                else:
                    logger.info("No expired aliases found.")
    
    async def _periodic_conflict_detection(self):
        """Background task to periodically detect conflicts"""
        while True:
            await asyncio.sleep(1800)  # Check every 30 minutes
            try:
                logger.info("Running periodic conflict detection...")
                conflicts = await self.conflict_detector.detect_all_conflicts()
                
                if conflicts:
                    logger.warning(f"Detected {len(conflicts)} conflicts")
                    # Auto-resolve conflicts that can be auto-resolved
                    auto_resolutions = await self.conflict_detector.auto_resolve_conflicts()
                    if auto_resolutions:
                        logger.info(f"Auto-resolved {len(auto_resolutions)} conflicts")
                else:
                    logger.info("No conflicts detected")
                    
            except Exception as e:
                logger.error(f"Error in periodic conflict detection: {e}")
    
    async def detect_conflicts(self) -> List[Any]:
        """Detect conflicts in the SSOT registry"""
        return await self.conflict_detector.detect_all_conflicts()
    
    async def resolve_conflict(self, conflict_id: str, strategy: str, 
                             resolution_details: Dict[str, Any], resolved_by: str) -> Any:
        """Resolve a specific conflict"""
        from .conflict_detection import ResolutionStrategy
        strategy_enum = ResolutionStrategy(strategy)
        return await self.conflict_detector.resolve_conflict(
            conflict_id, strategy_enum, resolution_details, resolved_by
        )
    
    async def get_audit_report(self, query_params: Dict[str, Any] = None) -> Any:
        """Generate audit report"""
        from .audit_logging import AuditQuery, ReportFormat
        
        if query_params is None:
            query_params = {}
        
        query = AuditQuery(**query_params)
        return await self.audit_engine.generate_report(
            query=query,
            title="SSOT Audit Report",
            description="Comprehensive audit report for SSOT operations",
            format=ReportFormat.JSON
        )
    
    async def get_conflict_statistics(self) -> Dict[str, Any]:
        """Get conflict statistics"""
        return self.conflict_detector.get_conflict_statistics()
    
    async def get_audit_statistics(self, query_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get audit statistics"""
        from .audit_logging import AuditQuery
        
        if query_params is None:
            query_params = {}
        
        query = AuditQuery(**query_params)
        return await self.audit_engine.get_audit_statistics(query)

# Global registry instance
registry = SSOTRegistry()

# Export for easy access
__all__ = ['SSOTRegistry', 'SSOTAnchor', 'AliasDefinition', 'AuditEntry', 'AliasType', 'AliasStatus', 'ValidationError', 'AliasNotFoundError', 'ConflictError', 'ExpiredAliasError', 'registry']