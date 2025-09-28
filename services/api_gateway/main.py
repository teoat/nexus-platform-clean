from typing import Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="NEXUS API Registry",
    description="Service discovery and API registry for NEXUS platform",
)

# In-memory registry (in production, use Redis or database)
service_registry = {}


class ServiceRegistration(BaseModel):
    name: str
    version: str
    host: str
    port: int
    health_check_url: str
    metadata: Optional[Dict] = {}


@app.post("/register")
async def register_service(service: ServiceRegistration):
    """Register a new service in the registry"""
    service_key = f"{service.name}:{service.version}"
    service_registry[service_key] = {
        "name": service.name,
        "version": service.version,
        "host": service.host,
        "port": service.port,
        "health_check_url": service.health_check_url,
        "metadata": service.metadata or {},
        "registered_at": "2025-09-26T00:00:00Z",  # Use actual timestamp
    }
    return {"message": "Service registered successfully", "service_key": service_key}


@app.get("/services")
async def get_services():
    """Get all registered services"""
    return {"services": list(service_registry.values())}


@app.get("/services/{name}")
async def get_service(name: str, version: Optional[str] = None):
    """Get a specific service by name and optional version"""
    if version:
        service_key = f"{name}:{version}"
        if service_key not in service_registry:
            raise HTTPException(status_code=404, detail="Service not found")
        return service_registry[service_key]
    else:
        # Return latest version
        matching_services = [s for s in service_registry.values() if s["name"] == name]
        if not matching_services:
            raise HTTPException(status_code=404, detail="Service not found")
        return max(matching_services, key=lambda x: x["version"])


@app.delete("/services/{name}")
async def unregister_service(name: str, version: str):
    """Unregister a service"""
    service_key = f"{name}:{version}"
    if service_key not in service_registry:
        raise HTTPException(status_code=404, detail="Service not found")
    del service_registry[service_key]
    return {"message": "Service unregistered successfully"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "services_registered": len(service_registry)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
