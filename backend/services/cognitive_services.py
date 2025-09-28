#!/usr/bin/env python3
"""
NEXUS Platform - Cognitive Services Platform
Advanced AI services: NLP, Computer Vision, Speech Processing
"""
import asyncio
import logging
import json
import base64
import io
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from PIL import Image
import cv2
import librosa
import torch
from transformers import pipeline, AutoTokenizer, AutoModel

logger = logging.getLogger(__name__)

class ServiceType(Enum):
    NLP = "nlp"
    VISION = "vision"
    SPEECH = "speech"

class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class CognitiveRequest:
    request_id: str
    service_type: ServiceType
    input_data: Union[str, bytes, Dict]
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class CognitiveResponse:
    request_id: str
    service_type: ServiceType
    result: Dict[str, Any]
    confidence: float
    processing_time: float
    status: ProcessingStatus
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class NLPService:
    def __init__(self):
        self.sentiment_analyzer = None
        self.text_classifier = None
        self.ner_pipeline = None
        self.summarizer = None
        self._initialize_models()
    
    def _initialize_models(self):
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            self.text_classifier = pipeline("zero-shot-classification")
            self.ner_pipeline = pipeline("ner")
            self.summarizer = pipeline("summarization")
            logger.info("NLP models initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize NLP models: {e}")
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        try:
            result = self.sentiment_analyzer(text)
            return {
                "sentiment": result[0]["label"],
                "confidence": result[0]["score"],
                "text": text
            }
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"error": str(e)}
    
    async def classify_text(self, text: str, categories: List[str]) -> Dict[str, Any]:
        try:
            result = self.text_classifier(text, categories)
            return {
                "classification": result["labels"][0],
                "confidence": result["scores"][0],
                "categories": result["labels"],
                "scores": result["scores"]
            }
        except Exception as e:
            logger.error(f"Text classification failed: {e}")
            return {"error": str(e)}
    
    async def extract_entities(self, text: str) -> Dict[str, Any]:
        try:
            entities = self.ner_pipeline(text)
            return {
                "entities": entities,
                "text": text
            }
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {"error": str(e)}
    
    async def summarize_text(self, text: str, max_length: int = 150) -> Dict[str, Any]:
        try:
            summary = self.summarizer(text, max_length=max_length, min_length=30)
            return {
                "summary": summary[0]["summary_text"],
                "original_length": len(text),
                "summary_length": len(summary[0]["summary_text"])
            }
        except Exception as e:
            logger.error(f"Text summarization failed: {e}")
            return {"error": str(e)}

class VisionService:
    def __init__(self):
        self.object_detector = None
        self.image_classifier = None
        self.ocr_pipeline = None
        self._initialize_models()
    
    def _initialize_models(self):
        try:
            self.object_detector = pipeline("object-detection")
            self.image_classifier = pipeline("image-classification")
            self.ocr_pipeline = pipeline("image-to-text")
            logger.info("Vision models initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Vision models: {e}")
    
    async def detect_objects(self, image_data: bytes) -> Dict[str, Any]:
        try:
            image = Image.open(io.BytesIO(image_data))
            result = self.object_detector(image)
            return {
                "objects": result,
                "image_size": image.size,
                "detection_count": len(result)
            }
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return {"error": str(e)}
    
    async def classify_image(self, image_data: bytes) -> Dict[str, Any]:
        try:
            image = Image.open(io.BytesIO(image_data))
            result = self.image_classifier(image)
            return {
                "classification": result[0]["label"],
                "confidence": result[0]["score"],
                "all_predictions": result
            }
        except Exception as e:
            logger.error(f"Image classification failed: {e}")
            return {"error": str(e)}
    
    async def extract_text(self, image_data: bytes) -> Dict[str, Any]:
        try:
            image = Image.open(io.BytesIO(image_data))
            result = self.ocr_pipeline(image)
            return {
                "extracted_text": result,
                "image_size": image.size
            }
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return {"error": str(e)}

class SpeechService:
    def __init__(self):
        self.speech_recognizer = None
        self.text_to_speech = None
        self._initialize_models()
    
    def _initialize_models(self):
        try:
            self.speech_recognizer = pipeline("automatic-speech-recognition")
            logger.info("Speech models initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Speech models: {e}")
    
    async def transcribe_audio(self, audio_data: bytes) -> Dict[str, Any]:
        try:
            result = self.speech_recognizer(audio_data)
            return {
                "transcription": result["text"],
                "confidence": result.get("confidence", 0.0),
                "language": result.get("language", "unknown")
            }
        except Exception as e:
            logger.error(f"Speech recognition failed: {e}")
            return {"error": str(e)}
    
    async def analyze_emotion(self, audio_data: bytes) -> Dict[str, Any]:
        try:
            y, sr = librosa.load(io.BytesIO(audio_data))
            features = {
                "tempo": librosa.beat.tempo(y=y, sr=sr)[0],
                "spectral_centroid": np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)),
                "zero_crossing_rate": np.mean(librosa.feature.zero_crossing_rate(y)),
                "mfcc": np.mean(librosa.feature.mfcc(y=y, sr=sr), axis=1).tolist()
            }
            return {
                "audio_features": features,
                "duration": len(y) / sr,
                "sample_rate": sr
            }
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return {"error": str(e)}

class CognitiveServicesPlatform:
    def __init__(self):
        self.nlp_service = NLPService()
        self.vision_service = VisionService()
        self.speech_service = SpeechService()
        self.active_requests: Dict[str, CognitiveRequest] = {}
        self.completed_responses: Dict[str, CognitiveResponse] = {}
        self.is_running = False
    
    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        logger.info("Cognitive Services Platform started")
        asyncio.create_task(self._process_requests())
    
    async def stop(self):
        self.is_running = False
        logger.info("Cognitive Services Platform stopped")
    
    async def _process_requests(self):
        while self.is_running:
            try:
                pending_requests = [req for req in self.active_requests.values() 
                                 if req.request_id not in self.completed_responses]
                
                for request in pending_requests[:5]:
                    asyncio.create_task(self._process_request(request))
                
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error processing requests: {e}")
                await asyncio.sleep(5)
    
    async def _process_request(self, request: CognitiveRequest):
        try:
            start_time = datetime.now()
            
            if request.service_type == ServiceType.NLP:
                if "sentiment" in request.parameters:
                    result = await self.nlp_service.analyze_sentiment(request.input_data)
                elif "classification" in request.parameters:
                    result = await self.nlp_service.classify_text(
                        request.input_data, 
                        request.parameters.get("categories", [])
                    )
                elif "entities" in request.parameters:
                    result = await self.nlp_service.extract_entities(request.input_data)
                elif "summarize" in request.parameters:
                    result = await self.nlp_service.summarize_text(
                        request.input_data,
                        request.parameters.get("max_length", 150)
                    )
                else:
                    result = {"error": "Unknown NLP operation"}
            
            elif request.service_type == ServiceType.VISION:
                if "detect" in request.parameters:
                    result = await self.vision_service.detect_objects(request.input_data)
                elif "classify" in request.parameters:
                    result = await self.vision_service.classify_image(request.input_data)
                elif "ocr" in request.parameters:
                    result = await self.vision_service.extract_text(request.input_data)
                else:
                    result = {"error": "Unknown Vision operation"}
            
            elif request.service_type == ServiceType.SPEECH:
                if "transcribe" in request.parameters:
                    result = await self.speech_service.transcribe_audio(request.input_data)
                elif "emotion" in request.parameters:
                    result = await self.speech_service.analyze_emotion(request.input_data)
                else:
                    result = {"error": "Unknown Speech operation"}
            
            else:
                result = {"error": "Unknown service type"}
            
            processing_time = (datetime.now() - start_time).total_seconds()
            confidence = result.get("confidence", 0.0) if isinstance(result, dict) else 0.0
            
            response = CognitiveResponse(
                request_id=request.request_id,
                service_type=request.service_type,
                result=result,
                confidence=confidence,
                processing_time=processing_time,
                status=ProcessingStatus.COMPLETED
            )
            
            self.completed_responses[request.request_id] = response
            logger.info(f"Request {request.request_id} processed successfully")
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            response = CognitiveResponse(
                request_id=request.request_id,
                service_type=request.service_type,
                result={"error": str(e)},
                confidence=0.0,
                processing_time=processing_time,
                status=ProcessingStatus.FAILED
            )
            self.completed_responses[request.request_id] = response
            logger.error(f"Request {request.request_id} failed: {e}")
    
    async def submit_request(self, service_type: ServiceType, input_data: Union[str, bytes, Dict], 
                           parameters: Dict[str, Any] = None) -> str:
        request_id = f"req_{int(datetime.now().timestamp())}"
        
        request = CognitiveRequest(
            request_id=request_id,
            service_type=service_type,
            input_data=input_data,
            parameters=parameters or {}
        )
        
        self.active_requests[request_id] = request
        logger.info(f"Request {request_id} submitted for {service_type.value} service")
        return request_id
    
    async def get_response(self, request_id: str) -> Optional[CognitiveResponse]:
        return self.completed_responses.get(request_id)
    
    async def get_platform_status(self) -> Dict[str, Any]:
        total_requests = len(self.active_requests)
        completed_requests = len(self.completed_responses)
        failed_requests = len([r for r in self.completed_responses.values() 
                            if r.status == ProcessingStatus.FAILED])
        
        return {
            "platform_running": self.is_running,
            "total_requests": total_requests,
            "completed_requests": completed_requests,
            "failed_requests": failed_requests,
            "success_rate": completed_requests / total_requests if total_requests > 0 else 0,
            "services": {
                "nlp": "active" if self.nlp_service.sentiment_analyzer else "inactive",
                "vision": "active" if self.vision_service.object_detector else "inactive",
                "speech": "active" if self.speech_service.speech_recognizer else "inactive"
            }
        }

cognitive_services_platform = CognitiveServicesPlatform()
