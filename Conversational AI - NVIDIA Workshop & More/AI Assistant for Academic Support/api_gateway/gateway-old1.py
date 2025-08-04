# api_gateway/gateway.py

from typing import Dict, Any, Optional, List, Union, Callable
import time
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('api_gateway')

class APIGateway:
    """
    A simple API Gateway that routes requests to appropriate services.
    Implements service discovery, request routing, and basic monitoring.
    """
    
    def __init__(self):
        # Registry of available services
        self._services = {}
        
        # Request metrics
        self._request_count = 0
        self._service_metrics = {}
        self._lock = threading.Lock()
        
        # Track the last metrics reporting time
        self._last_report_time = time.time()
        
        logger.info("API Gateway initialized")
    
    def register_service(self, service_name: str, service_instance: Any) -> None:
        """Register a service with the gateway"""
        self._services[service_name] = service_instance
        self._service_metrics[service_name] = {
            "requests": 0,
            "errors": 0,
            "avg_response_time": 0,
            "total_response_time": 0,  # Added to help calculate rolling average
            "last_activity": time.time()
        }
        logger.info(f"Registered service: {service_name}")
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get a service instance by name"""
        return self._services.get(service_name)
    
    def list_services(self) -> List[str]:
        """List all registered services"""
        return list(self._services.keys())
    
    def route_request(self, service_name: str, method_name: str, *args, **kwargs) -> Any:
        """
        Route a request to the appropriate service method
        Handles metrics collection and error handling
        """
        service = self.get_service(service_name)
        if not service:
            logger.error(f"Service not found: {service_name}")
            raise ValueError(f"Service '{service_name}' not found")
        
        method = getattr(service, method_name, None)
        if not method or not callable(method):
            logger.error(f"Method not found: {service_name}.{method_name}")
            raise ValueError(f"Method '{method_name}' not found in service '{service_name}'")
        
        # Track request metrics
        with self._lock:
            self._request_count += 1
            self._service_metrics[service_name]["requests"] += 1
            self._service_metrics[service_name]["last_activity"] = time.time()
        
        # Execute the request with timing
        start_time = time.time()
        try:
            result = method(*args, **kwargs)
            
            # Report metrics if it's been more than 60 seconds since the last report
            current_time = time.time()
            if current_time - self._last_report_time >= 60:
                self._report_metrics()
                self._last_report_time = current_time
            
            # Log metrics to W&B if the service exists
            wandb_tracker = self.get_service("wandb_tracker")
            if wandb_tracker:
                service_metrics = self._service_metrics[service_name]
                # Only log if there's a significant change (to avoid overloading W&B)
                if service_metrics["requests"] % 10 == 0:  # Log every 10 requests
                    try:
                        wandb_tracker.log_system_metrics({
                            f"service/{service_name}/requests": service_metrics["requests"],
                            f"service/{service_name}/errors": service_metrics["errors"],
                            f"service/{service_name}/avg_response_time": service_metrics["avg_response_time"]
                        })
                    except Exception as e:
                        logger.warning(f"Failed to log service metrics to W&B: {str(e)}")
            
            return result
        except Exception as e:
            logger.error(f"Error routing request to {service_name}.{method_name}: {str(e)}")
            with self._lock:
                self._service_metrics[service_name]["errors"] += 1
                
            # Log error to W&B if the service exists
            wandb_tracker = self.get_service("wandb_tracker")
            if wandb_tracker:
                try:
                    wandb_tracker.log_error(
                        error_type=f"{service_name}_error",
                        error_message=str(e),
                        query=f"Method: {method_name}, Args: {args}, Kwargs: {kwargs}"
                    )
                except Exception as log_err:
                    logger.warning(f"Failed to log error to W&B: {str(log_err)}")
                    
            raise
        finally:
            # Calculate response time
            response_time = time.time() - start_time
            
            # Update average response time
            with self._lock:
                metrics = self._service_metrics[service_name]
                metrics["total_response_time"] += response_time
                metrics["avg_response_time"] = metrics["total_response_time"] / metrics["requests"]
    
    def _report_metrics(self) -> None:
        """Report the current metrics"""
        with self._lock:
            logger.info(f"Total requests processed: {self._request_count}")
            for service, metrics in self._service_metrics.items():
                # Only log metrics for services that have had activity
                if metrics["requests"] > 0:
                    logger.info(f"Service: {service}, "
                               f"Requests: {metrics['requests']}, "
                               f"Errors: {metrics['errors']}, "
                               f"Avg Response Time: {metrics['avg_response_time']:.4f}s")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get the current metrics for all services"""
        with self._lock:
            metrics = {
                "total_requests": self._request_count,
                "services": {}
            }
            
            for service_name, service_metrics in self._service_metrics.items():
                metrics["services"][service_name] = {
                    "requests": service_metrics["requests"],
                    "errors": service_metrics["errors"],
                    "avg_response_time": service_metrics["avg_response_time"],
                    "last_activity": time.time() - service_metrics["last_activity"]
                }
            
            return metrics

# Create a singleton instance
gateway = APIGateway()

def register_service(service_name: str, service_instance: Any) -> None:
    """Register a service with the gateway"""
    gateway.register_service(service_name, service_instance)

def get_service(service_name: str) -> Optional[Any]:
    """Get a service instance by name"""
    return gateway.get_service(service_name)

def route_request(service_name: str, method_name: str, *args, **kwargs) -> Any:
    """Route a request to a service method"""
    return gateway.route_request(service_name, method_name, *args, **kwargs)

def get_gateway_metrics() -> Dict[str, Any]:
    """Get current metrics from the gateway"""
    return gateway.get_metrics()

# Add W&B integration functions
def register_wandb_service(config=None):
    """
    Register the W&B tracking service in the gateway.
    
    Args:
        config: Configuration dictionary to initialize W&B with
        
    Returns:
        The initialized W&B tracker instance
    """
    # Import here to avoid circular imports
    from services.wandb_service import WandbTracker
    
    wandb_tracker = WandbTracker(
        project_name="usiu-chatbot",
        # entity="your-username",  # Uncomment and add your W&B username
        # api_key="your-api-key",  # Uncomment and add your W&B API key if not set as env var
        tags=["production", "gradio-app"]
    )
    
    # Initialize with config if provided
    if config:
        wandb_tracker.initialize(config=config)
    
    # Register the service
    register_service("wandb_tracker", wandb_tracker)
    
    logger.info("Registered W&B tracking service")
    return wandb_tracker

def get_wandb_tracker():
    """Convenience function to get the W&B tracker service."""
    return get_service("wandb_tracker")