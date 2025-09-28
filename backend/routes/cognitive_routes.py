#!/usr/bin/env python3
"""
NEXUS Platform - Cognitive Services API Routes
REST API endpoints for cognitive services platform
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import json
import base64
from datetime import datetime
from ..services.cognitive_services import (
    cognitive_services_platform, 
    ServiceType, 
    ProcessingStatus
)

router = APIRouter(prefix="/api/v1/cognitive", tags=["cognitive"])

@router.post("/nlp/sentiment")
async def analyze_sentiment(text: str = Form(...)):
    """Analyze sentiment of text"""
    try:
        request_id = await cognitive_services_platform.submit_request(
            ServiceType.NLP, 
            text, 
            {"sentiment": True}
        )
        return {"request_id": request_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/nlp/classify")
async def classify_text(
    text: str = Form(...),
    categories: str = Form(...)
):
    """Classify text into categories"""
    try:
        categories_list = json.loads(categories)
        request_id = await cognitive_services_platform.submit_request(
            ServiceType.NLP, 
            text, 
            {"classification": True, "categories": categories_list}
        )
        return {"request_id": request_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/nlp/entities")
async def extract_entities(text: str = Form(...)):
    """Extract named entities from text"""
    try:
        request_id = await cognitive_services_platform.submit_request(
            ServiceType.NLP, 
            text, 
            {"entities": True}
        )
        return {"request_id": request_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/nlp/summarize")
async def summarize_text(
    text: str = Form(...),
    max_length: int = Form(150)
):
    """Summarize text"""
    try:
        request_id = await cognitive_services_platform.submit_request(
            ServiceType.NLP, 
            text, 
            {"summarize": True, "max_length": max_length}
        )
        return {"request_id": request_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vision/detect")
async def detect_objects(file: UploadFile = File(...)):
    """Detect objects in image"""
    try:
        image_data = await file.read()
        request_id = await cognitive_services_platform.submit_request(
            ServiceType.VISION, 
            image_data, 
            {"detect": True}
        )
        return {"request_id": request_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vision/classify")
async def classify_image(file: UploadFile = File(...)):
    """Classify image"""
    try:
        image_data = await file.read()
        request_id = await cognitive_services_platform.submit_request(
            ServiceType.VISION, 
            image_data, 
            {"classify": True}
        )
        return {"request_id": request_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vision/ocr")
async def extract_text_from_image(file: UploadFile = File(...)):
    """Extract text from image using OCR"""
    try:
        image_data = await file.read()
        request_id = await cognitive_services_platform.submit_request(
            ServiceType.VISION, 
            image_data, 
            {"ocr": True}
        )
        return {"request_id": request_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/speech/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe audio to text"""
    try:
        audio_data = await file.read()
        request_id = await cognitive_services_platform.submit_request(
            ServiceType.SPEECH, 
            audio_data, 
            {"transcribe": True}
        )
        return {"request_id": request_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/speech/emotion")
async def analyze_audio_emotion(file: UploadFile = File(...)):
    """Analyze emotion from audio"""
    try:
        audio_data = await file.read()
        request_id = await cognitive_services_platform.submit_request(
            ServiceType.SPEECH, 
            audio_data, 
            {"emotion": True}
        )
        return {"request_id": request_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/response/{request_id}")
async def get_response(request_id: str):
    """Get processing response by request ID"""
    try:
        response = await cognitive_services_platform.get_response(request_id)
        if not response:
            raise HTTPException(status_code=404, detail="Response not found")
        
        return {
            "request_id": response.request_id,
            "service_type": response.service_type.value,
            "result": response.result,
            "confidence": response.confidence,
            "processing_time": response.processing_time,
            "status": response.status.value,
            "created_at": response.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_platform_status():
    """Get cognitive services platform status"""
    try:
        status = await cognitive_services_platform.get_platform_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services")
async def get_available_services():
    """Get list of available cognitive services"""
    return {
        "nlp": {
            "sentiment_analysis": "Analyze text sentiment",
            "text_classification": "Classify text into categories",
            "entity_extraction": "Extract named entities",
            "text_summarization": "Summarize long text"
        },
        "vision": {
            "object_detection": "Detect objects in images",
            "image_classification": "Classify images",
            "ocr": "Extract text from images"
        },
        "speech": {
            "speech_recognition": "Transcribe audio to text",
            "emotion_analysis": "Analyze emotion from audio"
        }
    }

@router.post("/batch/nlp")
async def batch_nlp_processing(
    texts: str = Form(...),
    operations: str = Form(...)
):
    """Process multiple texts with multiple NLP operations"""
    try:
        texts_list = json.loads(texts)
        operations_list = json.loads(operations)
        
        request_ids = []
        for text in texts_list:
            for operation in operations_list:
                request_id = await cognitive_services_platform.submit_request(
                    ServiceType.NLP, 
                    text, 
                    {operation: True}
                )
                request_ids.append(request_id)
        
        return {
            "batch_id": f"batch_{int(datetime.now().timestamp())}",
            "request_ids": request_ids,
            "total_requests": len(request_ids)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_cognitive_metrics():
    """Get cognitive services performance metrics"""
    try:
        status = await cognitive_services_platform.get_platform_status()
        
        return {
            "platform_uptime": "active",
            "total_requests_processed": status["total_requests"],
            "success_rate": status["success_rate"],
            "average_processing_time": 2.5,
            "services_status": status["services"],
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
