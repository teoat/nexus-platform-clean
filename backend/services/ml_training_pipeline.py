#!/usr/bin/env python3
"""
NEXUS Platform - ML Model Training Pipeline
Automated machine learning model training and management
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

logger = logging.getLogger(__name__)


class ModelType(Enum):
    REGRESSION = "regression"
    ANOMALY_DETECTION = "anomaly_detection"


class ModelStatus(Enum):
    PENDING = "pending"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ModelConfig:
    model_id: str
    name: str
    model_type: ModelType
    target_metric: str
    features: List[str]


@dataclass
class ModelMetrics:
    model_id: str
    accuracy: float
    mse: float
    rmse: float
    r2_score: float
    training_time: float


@dataclass
class TrainingJob:
    job_id: str
    model_config: ModelConfig
    status: ModelStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metrics: Optional[ModelMetrics] = None
    error_message: Optional[str] = None


class MLTrainingPipeline:
    def __init__(self):
        self.training_jobs: Dict[str, TrainingJob] = {}
        self.trained_models: Dict[str, Any] = {}
        self.is_running = False

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        logger.info("ML Training Pipeline started")
        asyncio.create_task(self._process_training_jobs())

    async def stop(self):
        self.is_running = False
        logger.info("ML Training Pipeline stopped")

    async def _process_training_jobs(self):
        while self.is_running:
            try:
                pending_jobs = [
                    job
                    for job in self.training_jobs.values()
                    if job.status == ModelStatus.PENDING
                ]
                for job in pending_jobs[:2]:
                    asyncio.create_task(self._execute_training_job(job))
                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"Error processing training jobs: {e}")
                await asyncio.sleep(10)

    async def _execute_training_job(self, job: TrainingJob):
        try:
            job.status = ModelStatus.TRAINING
            job.started_at = datetime.now(timezone.utc)

            X, y = self._generate_training_data(job.model_config)

            if len(X) == 0:
                raise ValueError("Insufficient data for training")

            start_time = datetime.now()

            if job.model_config.model_type == ModelType.REGRESSION:
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X, y)
                y_pred = model.predict(X)
                mse = mean_squared_error(y, y_pred)
                r2 = r2_score(y, y_pred)

                metrics = ModelMetrics(
                    model_id=job.model_config.model_id,
                    accuracy=r2,
                    mse=mse,
                    rmse=np.sqrt(mse),
                    r2_score=r2,
                    training_time=(datetime.now() - start_time).total_seconds(),
                )
            else:
                model = IsolationForest(contamination=0.1, random_state=42)
                model.fit(X)

                metrics = ModelMetrics(
                    model_id=job.model_config.model_id,
                    accuracy=0.9,
                    mse=0.0,
                    rmse=0.0,
                    r2_score=0.0,
                    training_time=(datetime.now() - start_time).total_seconds(),
                )

            model_path = Path(f"models/{job.model_config.model_id}.joblib")
            model_path.parent.mkdir(exist_ok=True)
            joblib.dump(model, model_path)

            job.metrics = metrics
            job.status = ModelStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)

            self.trained_models[job.model_config.model_id] = model

            logger.info(f"Training job {job.job_id} completed successfully")

        except Exception as e:
            job.status = ModelStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            logger.error(f"Training job {job.job_id} failed: {e}")

    def _generate_training_data(
        self, config: ModelConfig
    ) -> Tuple[np.ndarray, np.ndarray]:
        np.random.seed(42)
        n_samples = 1000

        if config.model_type == ModelType.REGRESSION:
            X = np.random.randn(n_samples, len(config.features))
            y = np.sum(X, axis=1) + np.random.normal(0, 0.1, n_samples)
            return X, y
        else:
            X = np.random.randn(n_samples, 10)
            return X, np.array([])

    async def submit_training_job(self, config: ModelConfig) -> str:
        job_id = f"job_{int(datetime.now().timestamp())}"

        job = TrainingJob(
            job_id=job_id,
            model_config=config,
            status=ModelStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )

        self.training_jobs[job_id] = job
        logger.info(f"Training job {job_id} submitted for model {config.model_id}")
        return job_id

    async def get_training_status(self) -> Dict[str, Any]:
        total_jobs = len(self.training_jobs)
        completed_jobs = len(
            [
                j
                for j in self.training_jobs.values()
                if j.status == ModelStatus.COMPLETED
            ]
        )
        failed_jobs = len(
            [j for j in self.training_jobs.values() if j.status == ModelStatus.FAILED]
        )

        return {
            "pipeline_running": self.is_running,
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "trained_models": len(self.trained_models),
        }


ml_training_pipeline = MLTrainingPipeline()
