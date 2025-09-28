#!/usr/bin/env python3
"""
NEXUS Platform - Comprehensive System Validation
Validates all components and integrations
"""

import asyncio
import sys
import time
import json
import requests
import yaml
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemValidator:
    def __init__(self):
        self.results = {
            "timestamp": time.time(),
            "overall_status": "unknown",
            "components": {},
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        self.config = self._load_config()
        self.base_url = self.config["api_urls"]["backend"]
    
    def _load_config(self) -> Dict[str, Any]:
        config_path = Path("config/app_settings.yaml")
        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    async def validate_backend(self) -> Dict[str, Any]:
        """Validate backend services"""
        logger.info("🔍 Validating backend services...")
        
        backend_status = {
            "status": "unknown",
            "endpoints": {},
            "errors": [],
            "performance": {}
        }
        
        try:
            # Test health endpoint
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                backend_status["status"] = "healthy"
                backend_status["performance"]["health_check_ms"] = round(response_time * 1000, 2)
            else:
                backend_status["status"] = "unhealthy"
                backend_status["errors"].append(f"Health check failed: {response.status_code}")
            
            # Test SSOT endpoints
            ssot_endpoints = [
                "/api/v1/ssot/aliases",
                "/api/v1/ssot/resolve/user-management",
                "/api/v1/ssot/aliases/user-management"
            ]
            
            for endpoint in ssot_endpoints:
                try:
                    start_time = time.time()
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    response_time = time.time() - start_time
                    
                    backend_status["endpoints"][endpoint] = {
                        "status": "healthy" if response.status_code in [200, 404] else "error",
                        "response_time_ms": round(response_time * 1000, 2),
                        "status_code": response.status_code
                    }
                except Exception as e:
                    backend_status["endpoints"][endpoint] = {
                        "status": "error",
                        "error": str(e)
                    }
                    backend_status["errors"].append(f"Endpoint {endpoint}: {str(e)}")
            
        except Exception as e:
            backend_status["status"] = "error"
            backend_status["errors"].append(f"Backend validation failed: {str(e)}")
        
        return backend_status
    
    async def validate_ssot_system(self) -> Dict[str, Any]:
        """Validate SSOT system functionality"""
        logger.info("🔍 Validating SSOT system...")
        
        ssot_status = {
            "status": "unknown",
            "registry": {},
            "aliases": {},
            "performance": {},
            "errors": []
        }
        
        try:
            # Test alias creation
            test_alias = {
                "alias": "test-validation",
                "canonical": "/api/v1/test",
                "context": "frontend",
                "description": "Test alias for validation",
                "type": "application"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/v1/ssot/aliases",
                json=test_alias,
                timeout=5
            )
            creation_time = time.time() - start_time
            
            if response.status_code in [200, 201]:
                ssot_status["aliases"]["creation"] = {
                    "status": "success",
                    "response_time_ms": round(creation_time * 1000, 2)
                }
                
                # Test alias resolution
                start_time = time.time()
                resolve_response = requests.get(
                    f"{self.base_url}/api/v1/ssot/resolve/test-validation",
                    params={"context": "frontend"},
                    timeout=5
                )
                resolve_time = time.time() - start_time
                
                ssot_status["aliases"]["resolution"] = {
                    "status": "success" if resolve_response.status_code == 200 else "error",
                    "response_time_ms": round(resolve_time * 1000, 2),
                    "status_code": resolve_response.status_code
                }
                
                # Test alias listing
                start_time = time.time()
                list_response = requests.get(
                    f"{self.base_url}/api/v1/ssot/aliases",
                    params={"context": "frontend"},
                    timeout=5
                )
                list_time = time.time() - start_time
                
                ssot_status["aliases"]["listing"] = {
                    "status": "success" if list_response.status_code == 200 else "error",
                    "response_time_ms": round(list_time * 1000, 2),
                    "status_code": list_response.status_code
                }
                
                # Clean up test alias
                try:
                    requests.delete(
                        f"{self.base_url}/api/v1/ssot/aliases/test-validation",
                        params={"context": "frontend"},
                        timeout=5
                    )
                except:
                    pass
                
                ssot_status["status"] = "healthy"
            else:
                ssot_status["status"] = "error"
                ssot_status["errors"].append(f"Alias creation failed: {response.status_code}")
                
        except Exception as e:
            ssot_status["status"] = "error"
            ssot_status["errors"].append(f"SSOT validation failed: {str(e)}")
        
        return ssot_status
    
    async def validate_frontend(self) -> Dict[str, Any]:
        """Validate frontend components"""
        logger.info("🔍 Validating frontend components...")
        
        frontend_status = {
            "status": "unknown",
            "components": {},
            "build_status": "unknown",
            "errors": []
        }
        
        try:
            # Check if frontend build files exist
            frontend_path = Path("frontend/web/build")
            if frontend_path.exists():
                frontend_status["build_status"] = "built"
                
                # Check for key files
                key_files = [
                    "index.html",
                    "static/js/main.js",
                    "static/css/main.css"
                ]
                
                for file_path in key_files:
                    full_path = frontend_path / file_path
                    if full_path.exists():
                        frontend_status["components"][file_path] = "present"
                    else:
                        frontend_status["components"][file_path] = "missing"
                        frontend_status["errors"].append(f"Missing file: {file_path}")
                
                frontend_status["status"] = "healthy" if not frontend_status["errors"] else "warning"
            else:
                frontend_status["build_status"] = "not_built"
                frontend_status["status"] = "warning"
                frontend_status["errors"].append("Frontend not built - run 'npm run build'")
                
        except Exception as e:
            frontend_status["status"] = "error"
            frontend_status["errors"].append(f"Frontend validation failed: {str(e)}")
        
        return frontend_status
    
    async def validate_performance(self) -> Dict[str, Any]:
        """Validate system performance"""
        logger.info("🔍 Validating system performance...")
        
        performance_status = {
            "status": "unknown",
            "metrics": {},
            "thresholds": self.config["performance_thresholds"],
            "errors": []
        }
        
        try:
            # Test multiple endpoints for performance
            test_endpoints = [
                "/health",
                "/api/v1/ssot/aliases",
                "/api/status"
            ]
            
            response_times = []
            success_count = 0
            total_requests = len(test_endpoints) * 5  # 5 requests per endpoint
            
            for endpoint in test_endpoints:
                for _ in range(5):
                    try:
                        start_time = time.time()
                        response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                        response_time = time.time() - start_time
                        
                        response_times.append(response_time * 1000)  # Convert to ms
                        
                        if response.status_code in [200, 404]:  # 404 is acceptable for some endpoints
                            success_count += 1
                            
                    except Exception as e:
                        performance_status["errors"].append(f"Performance test failed for {endpoint}: {str(e)}")
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                success_rate = (success_count / total_requests) * 100
                
                performance_status["metrics"] = {
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "max_response_time_ms": round(max_response_time, 2),
                    "success_rate_percent": round(success_rate, 2),
                    "total_requests": total_requests
                }
                
                # Check against thresholds
                if avg_response_time > performance_status["thresholds"]["max_response_time_ms"]:
                    performance_status["errors"].append(f"Average response time {avg_response_time:.2f}ms exceeds threshold")
                
                if success_rate < performance_status["thresholds"]["min_success_rate"]:
                    performance_status["errors"].append(f"Success rate {success_rate:.2f}% below threshold")
                
                performance_status["status"] = "healthy" if not performance_status["errors"] else "warning"
            else:
                performance_status["status"] = "error"
                performance_status["errors"].append("No successful performance tests")
                
        except Exception as e:
            performance_status["status"] = "error"
            performance_status["errors"].append(f"Performance validation failed: {str(e)}")
        
        return performance_status
    
    async def generate_recommendations(self) -> List[str]:
        """Generate system recommendations"""
        recommendations = []
        
        # Analyze results and generate recommendations
        if self.results["components"].get("backend", {}).get("status") == "healthy":
            recommendations.append("✅ Backend is healthy and operational")
        else:
            recommendations.append("🔧 Fix backend issues before proceeding")
        
        if self.results["components"].get("ssot", {}).get("status") == "healthy":
            recommendations.append("✅ SSOT system is fully functional")
        else:
            recommendations.append("🔧 SSOT system needs attention")
        
        if self.results["components"].get("frontend", {}).get("build_status") == "built":
            recommendations.append("✅ Frontend is built and ready")
        else:
            recommendations.append("🔧 Build frontend with 'npm run build'")
        
        if self.results["components"].get("performance", {}).get("status") == "healthy":
            recommendations.append("✅ Performance metrics are within acceptable ranges")
        else:
            recommendations.append("🔧 Performance optimization needed")
        
        # Add specific recommendations based on errors
        all_errors = []
        for component, data in self.results["components"].items():
            if isinstance(data, dict) and "errors" in data:
                all_errors.extend(data["errors"])
        
        if len(all_errors) == 0:
            recommendations.append("🎉 System is ready for production deployment!")
        elif len(all_errors) < 5:
            recommendations.append("⚠️ Minor issues detected - system is mostly ready")
        else:
            recommendations.append("🚨 Multiple issues detected - system needs attention")
        
        return recommendations
    
    async def run_validation(self) -> Dict[str, Any]:
        """Run complete system validation"""
        logger.info("🚀 Starting NEXUS Platform validation...")
        
        start_time = time.time()
        
        # Run all validations
        self.results["components"]["backend"] = await self.validate_backend()
        self.results["components"]["ssot"] = await self.validate_ssot_system()
        self.results["components"]["frontend"] = await self.validate_frontend()
        self.results["components"]["performance"] = await self.validate_performance()
        
        # Generate recommendations
        self.results["recommendations"] = await self.generate_recommendations()
        
        # Determine overall status
        component_statuses = [comp.get("status", "unknown") for comp in self.results["components"].values()]
        
        if all(status == "healthy" for status in component_statuses):
            self.results["overall_status"] = "healthy"
        elif any(status == "error" for status in component_statuses):
            self.results["overall_status"] = "error"
        else:
            self.results["overall_status"] = "warning"
        
        validation_time = time.time() - start_time
        self.results["validation_time_seconds"] = round(validation_time, 2)
        
        logger.info(f"✅ Validation complete in {validation_time:.2f} seconds")
        logger.info(f"Overall status: {self.results['overall_status']}")
        
        return self.results

async def main():
    """Main validation function"""
    validator = SystemValidator()
    results = await validator.run_validation()
    
    # Print results
    print("\n" + "="*60)
    print("🎯 NEXUS PLATFORM VALIDATION RESULTS")
    print("="*60)
    
    print(f"\n📊 Overall Status: {results['overall_status'].upper()}")
    print(f"⏱️  Validation Time: {results['validation_time_seconds']}s")
    
    print("\n🔍 Component Status:")
    for component, data in results["components"].items():
        status = data.get("status", "unknown")
        status_icon = "✅" if status == "healthy" else "⚠️" if status == "warning" else "❌"
        print(f"  {status_icon} {component.title()}: {status}")
    
    if results["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in results["recommendations"]:
            print(f"  {rec}")
    
    # Save results to file
    results_file = Path("validation_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    # Exit with appropriate code
    if results["overall_status"] == "healthy":
        sys.exit(0)
    elif results["overall_status"] == "warning":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    asyncio.run(main())
