"""
ETL Pipeline for NEXUS Platform
Extract, Transform, Load processes for data analytics and reporting
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import redis
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

logger = logging.getLogger(__name__)

class ETLConfig:
    """ETL Configuration"""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.data_warehouse_url = os.getenv("DATA_WAREHOUSE_URL", self.database_url)
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.batch_size = int(os.getenv("ETL_BATCH_SIZE", "1000"))
        self.etl_interval_minutes = int(os.getenv("ETL_INTERVAL_MINUTES", "15"))

class DataExtractor:
    """Extract data from various sources"""

    def __init__(self, config: ETLConfig):
        self.config = config
        self.engine = create_async_engine(config.database_url)
        self.redis = redis.from_url(config.redis_url)

    async def extract_user_data(self, last_updated: Optional[datetime] = None) -> pd.DataFrame:
        """Extract user data"""
        async with AsyncSession(self.engine) as session:
            query = """
                SELECT
                    id,
                    username,
                    email,
                    role,
                    status,
                    created_at,
                    updated_at,
                    last_login_at,
                    login_count,
                    email_verified
                FROM users
            """

            if last_updated:
                query += f" WHERE updated_at > '{last_updated.isoformat()}'"

            result = await session.execute(text(query))
            rows = result.fetchall()

            return pd.DataFrame([dict(row._mapping) for row in rows])

    async def extract_transaction_data(self, last_updated: Optional[datetime] = None) -> pd.DataFrame:
        """Extract transaction data"""
        async with AsyncSession(self.engine) as session:
            query = """
                SELECT
                    t.id,
                    t.user_id,
                    t.type,
                    t.amount,
                    t.currency,
                    t.status,
                    t.created_at,
                    t.updated_at,
                    t.description,
                    u.username,
                    u.email
                FROM transactions t
                LEFT JOIN users u ON t.user_id = u.id
            """

            if last_updated:
                query += f" WHERE t.updated_at > '{last_updated.isoformat()}'"

            result = await session.execute(text(query))
            rows = result.fetchall()

            return pd.DataFrame([dict(row._mapping) for row in rows])

    async def extract_audit_logs(self, last_updated: Optional[datetime] = None) -> pd.DataFrame:
        """Extract audit logs"""
        async with AsyncSession(self.engine) as session:
            query = """
                SELECT
                    id,
                    user_id,
                    action,
                    resource_type,
                    resource_id,
                    ip_address,
                    user_agent,
                    created_at,
                    metadata
                FROM audit_logs
            """

            if last_updated:
                query += f" WHERE created_at > '{last_updated.isoformat()}'"

            result = await session.execute(text(query))
            rows = result.fetchall()

            return pd.DataFrame([dict(row._mapping) for row in rows])

    async def extract_metrics_data(self, time_range: timedelta = timedelta(hours=1)) -> pd.DataFrame:
        """Extract metrics data from Redis"""
        try:
            # Get metrics keys
            keys = self.redis.keys("metrics:*")

            metrics_data = []
            cutoff_time = datetime.now() - time_range

            for key in keys:
                data = self.redis.get(key)
                if data:
                    metric = json.loads(data)
                    if datetime.fromisoformat(metric.get('timestamp', '2000-01-01')) > cutoff_time:
                        metrics_data.append(metric)

            return pd.DataFrame(metrics_data)

        except Exception as e:
            logger.error(f"Failed to extract metrics data: {e}")
            return pd.DataFrame()

class DataTransformer:
    """Transform data for analytics"""

    @staticmethod
    def transform_user_data(df: pd.DataFrame) -> pd.DataFrame:
        """Transform user data"""
        if df.empty:
            return df

        # Convert timestamps
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        df['last_login_at'] = pd.to_datetime(df['last_login_at'])

        # Calculate user engagement metrics
        df['account_age_days'] = (datetime.now() - df['created_at']).dt.days
        df['days_since_last_login'] = (datetime.now() - df['last_login_at']).dt.days

        # User status categorization
        df['user_status_category'] = df['status'].map({
            'active': 'Active',
            'inactive': 'Inactive',
            'suspended': 'Suspended',
            'pending': 'Pending'
        })

        # Role hierarchy
        role_levels = {'guest': 1, 'user': 2, 'manager': 3, 'admin': 4, 'super_admin': 5}
        df['role_level'] = df['role'].map(role_levels).fillna(1)

        return df

    @staticmethod
    def transform_transaction_data(df: pd.DataFrame) -> pd.DataFrame:
        """Transform transaction data"""
        if df.empty:
            return df

        # Convert timestamps
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['updated_at'] = pd.to_datetime(df['updated_at'])

        # Extract date components
        df['transaction_date'] = df['created_at'].dt.date
        df['transaction_hour'] = df['created_at'].dt.hour
        df['transaction_day_of_week'] = df['created_at'].dt.day_name()

        # Transaction amount analysis
        df['amount_usd'] = df.apply(
            lambda row: row['amount'] * get_exchange_rate(row['currency'], 'USD'),
            axis=1
        )

        # Transaction status analysis
        df['is_successful'] = df['status'] == 'completed'
        df['is_pending'] = df['status'] == 'pending'
        df['is_failed'] = df['status'].isin(['failed', 'cancelled'])

        # Transaction type categorization
        df['transaction_category'] = df['type'].map({
            'deposit': 'Incoming',
            'withdrawal': 'Outgoing',
            'transfer': 'Transfer',
            'payment': 'Payment',
            'fee': 'Fee'
        })

        return df

    @staticmethod
    def transform_audit_data(df: pd.DataFrame) -> pd.DataFrame:
        """Transform audit log data"""
        if df.empty:
            return df

        # Convert timestamps
        df['created_at'] = pd.to_datetime(df['created_at'])

        # Extract metadata
        df['metadata'] = df['metadata'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)

        # Risk scoring based on actions
        risk_actions = {
            'login_failed': 3,
            'password_change': 1,
            'admin_access': 2,
            'data_export': 2,
            'user_delete': 4,
            'system_config_change': 5
        }

        df['risk_score'] = df['action'].map(risk_actions).fillna(1)

        # Time-based analysis
        df['hour_of_day'] = df['created_at'].dt.hour
        df['day_of_week'] = df['created_at'].dt.day_name()

        # Geographic analysis (if IP available)
        df['country'] = df['ip_address'].apply(lambda ip: get_country_from_ip(ip) if ip else 'Unknown')

        return df

    @staticmethod
    def transform_metrics_data(df: pd.DataFrame) -> pd.DataFrame:
        """Transform metrics data"""
        if df.empty:
            return df

        # Convert timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Calculate rates and percentages
        if 'response_time' in df.columns:
            df['response_time_ms'] = df['response_time'] * 1000

        if 'cpu_usage' in df.columns:
            df['cpu_usage_percent'] = df['cpu_usage'] * 100

        if 'memory_usage' in df.columns:
            df['memory_usage_mb'] = df['memory_usage'] / (1024 * 1024)

        # Performance categorization
        df['performance_category'] = pd.cut(
            df.get('response_time_ms', 0),
            bins=[0, 100, 500, 1000, float('inf')],
            labels=['Excellent', 'Good', 'Slow', 'Very Slow']
        )

        return df

class DataLoader:
    """Load transformed data into data warehouse"""

    def __init__(self, config: ETLConfig):
        self.config = config
        self.engine = create_engine(config.data_warehouse_url)

    def load_user_dimensions(self, df: pd.DataFrame):
        """Load user dimension data"""
        if df.empty:
            return

        # Upsert user dimension
        df.to_sql(
            'dim_users',
            self.engine,
            if_exists='replace',  # In production, use upsert logic
            index=False,
            chunksize=self.config.batch_size
        )

        logger.info(f"Loaded {len(df)} user dimension records")

    def load_transaction_facts(self, df: pd.DataFrame):
        """Load transaction fact data"""
        if df.empty:
            return

        # Load transaction facts
        df.to_sql(
            'fact_transactions',
            self.engine,
            if_exists='append',
            index=False,
            chunksize=self.config.batch_size
        )

        logger.info(f"Loaded {len(df)} transaction fact records")

    def load_audit_facts(self, df: pd.DataFrame):
        """Load audit fact data"""
        if df.empty:
            return

        # Load audit facts
        df.to_sql(
            'fact_audit_logs',
            self.engine,
            if_exists='append',
            index=False,
            chunksize=self.config.batch_size
        )

        logger.info(f"Loaded {len(df)} audit fact records")

    def load_metrics_facts(self, df: pd.DataFrame):
        """Load metrics fact data"""
        if df.empty:
            return

        # Load metrics facts
        df.to_sql(
            'fact_metrics',
            self.engine,
            if_exists='append',
            index=False,
            chunksize=self.config.batch_size
        )

        logger.info(f"Loaded {len(df)} metrics fact records")

class ETLOrchestrator:
    """Orchestrate ETL pipeline execution"""

    def __init__(self, config: ETLConfig):
        self.config = config
        self.extractor = DataExtractor(config)
        self.transformer = DataTransformer()
        self.loader = DataLoader(config)
        self.last_run_times = {}

    async def run_full_etl(self):
        """Run complete ETL pipeline"""
        logger.info("Starting full ETL pipeline")

        try:
            # Extract data
            users_df = await self.extractor.extract_user_data()
            transactions_df = await self.extractor.extract_transaction_data()
            audit_df = await self.extractor.extract_audit_logs()
            metrics_df = await self.extractor.extract_metrics_data()

            # Transform data
            users_transformed = self.transformer.transform_user_data(users_df)
            transactions_transformed = self.transformer.transform_transaction_data(transactions_df)
            audit_transformed = self.transformer.transform_audit_data(audit_df)
            metrics_transformed = self.transformer.transform_metrics_data(metrics_df)

            # Load data
            self.loader.load_user_dimensions(users_transformed)
            self.loader.load_transaction_facts(transactions_transformed)
            self.loader.load_audit_facts(audit_transformed)
            self.loader.load_metrics_facts(metrics_transformed)

            # Update last run time
            self.last_run_times['full_etl'] = datetime.now()

            logger.info("Full ETL pipeline completed successfully")

        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}")
            raise

    async def run_incremental_etl(self):
        """Run incremental ETL pipeline"""
        logger.info("Starting incremental ETL pipeline")

        last_run = self.last_run_times.get('incremental_etl')

        try:
            # Extract incremental data
            users_df = await self.extractor.extract_user_data(last_run)
            transactions_df = await self.extractor.extract_transaction_data(last_run)
            audit_df = await self.extractor.extract_audit_logs(last_run)
            metrics_df = await self.extractor.extract_metrics_data()

            # Transform data
            users_transformed = self.transformer.transform_user_data(users_df)
            transactions_transformed = self.transformer.transform_transaction_data(transactions_df)
            audit_transformed = self.transformer.transform_audit_data(audit_df)
            metrics_transformed = self.transformer.transform_metrics_data(metrics_df)

            # Load data
            if not users_transformed.empty:
                self.loader.load_user_dimensions(users_transformed)
            if not transactions_transformed.empty:
                self.loader.load_transaction_facts(transactions_transformed)
            if not audit_transformed.empty:
                self.loader.load_audit_facts(audit_transformed)
            if not metrics_transformed.empty:
                self.loader.load_metrics_facts(metrics_transformed)

            # Update last run time
            self.last_run_times['incremental_etl'] = datetime.now()

            logger.info("Incremental ETL pipeline completed successfully")

        except Exception as e:
            logger.error(f"Incremental ETL pipeline failed: {e}")
            raise

    async def run_scheduled_etl(self):
        """Run ETL on schedule"""
        while True:
            try:
                await self.run_incremental_etl()
            except Exception as e:
                logger.error(f"Scheduled ETL failed: {e}")

            await asyncio.sleep(self.config.etl_interval_minutes * 60)

# Utility functions
def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """Get exchange rate (simplified implementation)"""
    # In production, integrate with a real exchange rate API
    rates = {
        'USD': 1.0,
        'EUR': 1.1,
        'GBP': 1.3,
        'JPY': 0.009,
        'CAD': 0.8,
        'AUD': 0.7
    }
    return rates.get(from_currency.upper(), 1.0) / rates.get(to_currency.upper(), 1.0)

def get_country_from_ip(ip_address: str) -> str:
    """Get country from IP address (simplified implementation)"""
    # In production, use a GeoIP database or service
    return "Unknown"

# Global ETL orchestrator instance
etl_config = ETLConfig()
etl_orchestrator = ETLOrchestrator(etl_config)

# Export functions and classes
__all__ = [
    "ETLConfig",
    "DataExtractor",
    "DataTransformer",
    "DataLoader",
    "ETLOrchestrator",
    "etl_orchestrator"
]</content>
</xai:function_call"><xai:function_call name="write">
<parameter name="filePath">data/analytics_engine.py
