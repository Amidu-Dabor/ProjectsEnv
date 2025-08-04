# api_gateway/gateway.py

from typing import Dict, Any, Optional, List, Union, Callable
import time
import threading
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('api_gateway')

class APIGateway:
    """
    Enhanced API Gateway with comprehensive metrics tracking for Chapter 5.
    """
    
    def __init__(self):
        # Registry of available services
        self._services = {}
        
        # Enhanced metrics for Chapter 5
        self._request_count = 0
        self._service_metrics = {}
        self._performance_metrics = {
            "response_times": [],
            "token_counts": [],
            "accuracy_scores": [],
            "query_complexities": {"simple": 0, "medium": 0, "complex": 0}
        }
        self._lock = threading.Lock()
        
        # Track the last metrics reporting time
        self._last_report_time = time.time()
        self._metrics_buffer = []
        
        logger.info("Enhanced API Gateway initialized with Chapter 5 metrics")
    
    def register_service(self, service_name: str, service_instance: Any) -> None:
        """Register a service with the gateway"""
        self._services[service_name] = service_instance
        self._service_metrics[service_name] = {
            "requests": 0,
            "errors": 0,
            "avg_response_time": 0,
            "total_response_time": 0,
            "last_activity": time.time(),
            "token_usage": 0,
            "accuracy_sum": 0
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
        Enhanced request routing with comprehensive metrics collection.
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
        tokens_used = 0
        accuracy_score = 0
        query_complexity = "medium"
        
        try:
            result = method(*args, **kwargs)
            
            # Extract metrics from result if available
            if isinstance(result, dict):
                tokens_used = result.get("tokens", 0)
                accuracy_score = result.get("accuracy", 0)
                query_complexity = result.get("complexity", "medium")
            
            # Report metrics periodically
            current_time = time.time()
            if current_time - self._last_report_time >= 60:
                self._report_metrics()
                self._last_report_time = current_time
            
            # Log to W&B if available
            wandb_tracker = self.get_service("wandb_tracker")
            if wandb_tracker:
                response_time = time.time() - start_time
                service_metrics = self._service_metrics[service_name]
                
                # Log detailed metrics
                if service_name in ["general_chat", "study_support"]:
                    wandb_tracker.log_performance_comparison(
                        model=service_name,
                        query_type=query_complexity,
                        response_time=response_time,
                        accuracy=accuracy_score,
                        tokens=tokens_used,
                        with_rag=kwargs.get("with_rag", False),
                        error_occurred=False
                    )
                
                # Log service metrics
                if service_metrics["requests"] % 10 == 0:  # Log every 10 requests
                    try:
                        wandb_tracker.log_system_metrics({
                            f"service/{service_name}/requests": service_metrics["requests"],
                            f"service/{service_name}/errors": service_metrics["errors"],
                            f"service/{service_name}/avg_response_time": service_metrics["avg_response_time"],
                            f"service/{service_name}/total_tokens": service_metrics["token_usage"]
                        })
                    except Exception as e:
                        logger.warning(f"Failed to log service metrics to W&B: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error routing request to {service_name}.{method_name}: {str(e)}")
            with self._lock:
                self._service_metrics[service_name]["errors"] += 1
                
            # Log error to W&B
            wandb_tracker = self.get_service("wandb_tracker")
            if wandb_tracker:
                try:
                    wandb_tracker.log_error(
                        error_type=f"{service_name}_error",
                        error_message=str(e),
                        query=f"Method: {method_name}"
                    )
                    
                    # Log error in performance comparison
                    wandb_tracker.log_performance_comparison(
                        model=service_name,
                        query_type=query_complexity,
                       response_time=time.time() - start_time,
                       accuracy=0,
                       tokens=0,
                       with_rag=kwargs.get("with_rag", False),
                       error_occurred=True
                   )
                except Exception as log_err:
                   logger.warning(f"Failed to log error to W&B: {str(log_err)}")
                   
            raise
        finally:
           # Calculate response time and update metrics
           response_time = time.time() - start_time
           
           # Update comprehensive metrics
           with self._lock:
               metrics = self._service_metrics[service_name]
               metrics["total_response_time"] += response_time
               metrics["avg_response_time"] = metrics["total_response_time"] / metrics["requests"]
               metrics["token_usage"] += tokens_used
               metrics["accuracy_sum"] += accuracy_score
               
               # Update performance metrics
               self._performance_metrics["response_times"].append(response_time)
               self._performance_metrics["token_counts"].append(tokens_used)
               self._performance_metrics["accuracy_scores"].append(accuracy_score)
               self._performance_metrics["query_complexities"][query_complexity] += 1
               
               # Buffer metrics for batch processing
               self._metrics_buffer.append({
                   "timestamp": time.time(),
                   "service": service_name,
                   "method": method_name,
                   "response_time": response_time,
                   "tokens": tokens_used,
                   "accuracy": accuracy_score,
                   "complexity": query_complexity
               })
   
    def _report_metrics(self) -> None:
       """Report comprehensive metrics including Chapter 5 requirements."""
       with self._lock:
           logger.info(f"Total requests processed: {self._request_count}")
           
           # Calculate aggregate performance metrics
           if self._performance_metrics["response_times"]:
               avg_response_time = sum(self._performance_metrics["response_times"]) / len(self._performance_metrics["response_times"])
               avg_tokens = sum(self._performance_metrics["token_counts"]) / len(self._performance_metrics["token_counts"]) if self._performance_metrics["token_counts"] else 0
               avg_accuracy = sum(self._performance_metrics["accuracy_scores"]) / len(self._performance_metrics["accuracy_scores"]) if self._performance_metrics["accuracy_scores"] else 0
               
               logger.info(f"Average response time: {avg_response_time:.4f}s")
               logger.info(f"Average tokens used: {avg_tokens:.0f}")
               logger.info(f"Average accuracy: {avg_accuracy:.4f}")
           
           # Report service-specific metrics
           for service, metrics in self._service_metrics.items():
               if metrics["requests"] > 0:
                   avg_accuracy = metrics["accuracy_sum"] / metrics["requests"]
                   logger.info(f"Service: {service}, "
                              f"Requests: {metrics['requests']}, "
                              f"Errors: {metrics['errors']}, "
                              f"Avg Response Time: {metrics['avg_response_time']:.4f}s, "
                              f"Avg Accuracy: {avg_accuracy:.4f}, "
                              f"Total Tokens: {metrics['token_usage']}")
           
           # Report complexity distribution
           total_complexity = sum(self._performance_metrics["query_complexities"].values())
           if total_complexity > 0:
               logger.info("Query complexity distribution:")
               for complexity, count in self._performance_metrics["query_complexities"].items():
                   percentage = (count / total_complexity) * 100
                   logger.info(f"  {complexity}: {count} ({percentage:.1f}%)")
   
    def get_metrics(self) -> Dict[str, Any]:
       """Get comprehensive metrics for all services including Chapter 5 data."""
       with self._lock:
           # Calculate aggregate metrics
           total_tokens = sum(m["token_usage"] for m in self._service_metrics.values())
           total_errors = sum(m["errors"] for m in self._service_metrics.values())
           
           # Calculate average accuracy across all services
           total_accuracy_sum = sum(m["accuracy_sum"] for m in self._service_metrics.values())
           total_requests = sum(m["requests"] for m in self._service_metrics.values())
           avg_accuracy = total_accuracy_sum / total_requests if total_requests > 0 else 0
           
           metrics = {
               "total_requests": self._request_count,
               "total_tokens": total_tokens,
               "total_errors": total_errors,
               "average_accuracy": avg_accuracy,
               "services": {}
           }
           
           # Add service-specific metrics
           for service_name, service_metrics in self._service_metrics.items():
               service_avg_accuracy = service_metrics["accuracy_sum"] / service_metrics["requests"] if service_metrics["requests"] > 0 else 0
               
               metrics["services"][service_name] = {
                   "requests": service_metrics["requests"],
                   "errors": service_metrics["errors"],
                   "avg_response_time": service_metrics["avg_response_time"],
                   "total_tokens": service_metrics["token_usage"],
                   "avg_accuracy": service_avg_accuracy,
                   "last_activity": time.time() - service_metrics["last_activity"]
               }
           
           # Add performance distribution metrics
           if self._performance_metrics["response_times"]:
               metrics["performance"] = {
                   "avg_response_time": sum(self._performance_metrics["response_times"]) / len(self._performance_metrics["response_times"]),
                   "min_response_time": min(self._performance_metrics["response_times"]),
                   "max_response_time": max(self._performance_metrics["response_times"]),
                   "query_complexity_distribution": self._performance_metrics["query_complexities"]
               }
           
           return metrics
   
    def get_performance_summary(self) -> Dict[str, Any]:
       """Get a performance summary matching Chapter 5 requirements."""
       with self._lock:
           if not self._metrics_buffer:
               return {"message": "No performance data available yet"}
           
           # Group metrics by service and complexity
           service_performance = {}
           complexity_performance = {}
           
           for metric in self._metrics_buffer:
               service = metric["service"]
               complexity = metric["complexity"]
               
               # Initialize service metrics
               if service not in service_performance:
                   service_performance[service] = {
                       "count": 0,
                       "total_time": 0,
                       "total_tokens": 0,
                       "total_accuracy": 0
                   }
               
               # Initialize complexity metrics
               if complexity not in complexity_performance:
                   complexity_performance[complexity] = {
                       "count": 0,
                       "total_time": 0,
                       "total_accuracy": 0
                   }
               
               # Update metrics
               service_performance[service]["count"] += 1
               service_performance[service]["total_time"] += metric["response_time"]
               service_performance[service]["total_tokens"] += metric["tokens"]
               service_performance[service]["total_accuracy"] += metric["accuracy"]
               
               complexity_performance[complexity]["count"] += 1
               complexity_performance[complexity]["total_time"] += metric["response_time"]
               complexity_performance[complexity]["total_accuracy"] += metric["accuracy"]
           
           # Calculate averages
           summary = {
               "by_service": {},
               "by_complexity": {},
               "overall": {
                   "total_requests": len(self._metrics_buffer),
                   "avg_response_time": sum(m["response_time"] for m in self._metrics_buffer) / len(self._metrics_buffer),
                   "avg_tokens": sum(m["tokens"] for m in self._metrics_buffer) / len(self._metrics_buffer),
                   "avg_accuracy": sum(m["accuracy"] for m in self._metrics_buffer) / len(self._metrics_buffer)
               }
           }
           
           # Service averages
           for service, perf in service_performance.items():
               if perf["count"] > 0:
                   summary["by_service"][service] = {
                       "requests": perf["count"],
                       "avg_response_time": perf["total_time"] / perf["count"],
                       "avg_tokens": perf["total_tokens"] / perf["count"],
                       "avg_accuracy": perf["total_accuracy"] / perf["count"]
                   }
           
           # Complexity averages
           for complexity, perf in complexity_performance.items():
               if perf["count"] > 0:
                   summary["by_complexity"][complexity] = {
                       "requests": perf["count"],
                       "avg_response_time": perf["total_time"] / perf["count"],
                       "avg_accuracy": perf["total_accuracy"] / perf["count"]
                   }
           
           return summary

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

def get_performance_summary() -> Dict[str, Any]:
   """Get performance summary for Chapter 5 analysis"""
   return gateway.get_performance_summary()

# Enhanced W&B integration functions
def register_wandb_service(config=None):
   """
   Register the enhanced W&B tracking service with Chapter 5 metrics.
   """
   from services.wandb_service import WandbTracker
   
   wandb_tracker = WandbTracker(
       project_name="usiu-chatbot",
       tags=["production", "gradio-app", "chapter5-metrics"]
   )
   
   # Initialize with enhanced config
   enhanced_config = {
       "metrics_tracking": {
           "response_time": True,
           "accuracy": True,
           "token_usage": True,
           "query_complexity": True,
           "rag_comparison": True,
           "user_satisfaction": True
       },
       "performance_goals": {
           "target_response_time": 3.0,  # seconds
           "target_accuracy": 0.93,      # 93% as per Chapter 5
           "target_satisfaction": 0.80   # 80% positive feedback
       }
   }
   
   if config:
       enhanced_config.update(config)
   
   wandb_tracker.initialize(config=enhanced_config)
   
   # Register the service
   register_service("wandb_tracker", wandb_tracker)
   
   logger.info("Registered enhanced W&B tracking service with Chapter 5 metrics")
   return wandb_tracker

def get_wandb_tracker():
   """Convenience function to get the W&B tracker service."""
   return get_service("wandb_tracker")