# services/wandb_service.py

import os
import time
import json
import wandb
from typing import Dict, List, Any, Optional, Union
import numpy as np

class WandbTracker:
    """Enhanced W&B integration for comprehensive chatbot monitoring matching Chapter 5 metrics."""
    
    def __init__(self, project_name: str = "usiu-chatbot", entity: Optional[str] = None, 
                 api_key: Optional[str] = None, tags: Optional[List[str]] = None):
        """Initialize the WandbTracker with enhanced metrics tracking."""
        self.project_name = project_name
        self.entity = entity
        self.tags = tags or ["gradio-chatbot", "production"]
        
        if api_key:
            os.environ["WANDB_API_KEY"] = api_key
            
        self.run = None
        self.is_initialized = False
        self.session_metrics = {}
        
        # Enhanced metrics for Chapter 5
        self.total_conversations = 0
        self.total_tokens = 0
        self.total_response_time = 0
        self.feedback_counts = {"positive": 0, "negative": 0, "neutral": 0}
        
        # New metrics for Chapter 5
        self.query_complexity_metrics = {
            "simple": {"count": 0, "total_time": 0, "total_accuracy": 0},
            "medium": {"count": 0, "total_time": 0, "total_accuracy": 0},
            "complex": {"count": 0, "total_time": 0, "total_accuracy": 0}
        }
        
        self.rag_metrics = {
            "with_rag": {"count": 0, "total_time": 0, "total_tokens": 0},
            "without_rag": {"count": 0, "total_time": 0, "total_tokens": 0},
            "retrieval_count": 0,
            "retrieval_errors": 0
        }
        
        self.model_performance = {
            "general": {"count": 0, "total_accuracy": 0, "errors": 0},
            "study": {"count": 0, "total_accuracy": 0, "errors": 0}
        }
        
        self.conversation_table = None
        self.metrics_table = None
        self.error_table = None
        self.file_table = None
        self.performance_table = None

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the W&B run with enhanced tables."""
        if self.is_initialized:
            return
            
        default_config = {
            "app_version": "1.0.0",
            "interface_type": "gradio",
            "retrieval_method": "vector_store",
            "max_context_length": 8000,
            "evaluation_metrics": ["accuracy", "response_time", "token_usage", "user_satisfaction"]
        }
        
        run_config = {**default_config, **(config or {})}
        
        self.run = wandb.init(
            project=self.project_name,
            entity=self.entity,
            config=run_config,
            tags=self.tags,
            job_type="chatbot",
            notes="Enhanced Gradio chatbot with Chapter 5 metrics",
            reinit="return_previous"
        )
        
        # Enhanced tables for Chapter 5 metrics
        self.conversation_table = wandb.Table(
            columns=["timestamp", "session_id", "user_id", "chat_type", 
                     "query", "response", "context_used", "tokens", 
                     "response_time", "feedback", "query_complexity", "accuracy_score"]
        )
        
        self.metrics_table = wandb.Table(
            columns=["timestamp", "metric_type", "metric_name", "value", "category"]
        )
        
        self.performance_table = wandb.Table(
            columns=["timestamp", "model", "query_type", "response_time", 
                     "accuracy", "tokens", "with_rag", "error_rate"]
        )
        
        self.is_initialized = True
        print(f"W&B initialized for project {self.project_name} with enhanced metrics")
        
    def log_conversation(self, 
                       session_id: str,
                       user_id: Optional[str],
                       chat_type: str,
                       query: str,
                       response: str,
                       context_used: Optional[List[str]] = None,
                       tokens: Optional[int] = None,
                       response_time: Optional[float] = None,
                       feedback: Optional[str] = None,
                       query_complexity: Optional[str] = None,
                       accuracy_score: Optional[float] = None) -> None:
        """Enhanced conversation logging with Chapter 5 metrics."""
        if not self.is_initialized:
            self.initialize()
            
        try:
            # Determine query complexity if not provided
            if not query_complexity:
                query_complexity = self._classify_query_complexity(query)
            
            # Estimate accuracy if not provided
            if accuracy_score is None:
                accuracy_score = self._estimate_accuracy(response, context_used)
            
            # Format context for JSON
            context_json = json.dumps(context_used) if context_used else "[]"
            
            # Add to conversation table
            self.conversation_table.add_data(
                time.time(),
                session_id,
                user_id or "anonymous",
                chat_type,
                query,
                response,
                context_json,
                tokens or 0,
                response_time or 0.0,
                feedback or "none",
                query_complexity,
                accuracy_score
            )
            
            # Update metrics
            self.total_conversations += 1
            if tokens:
                self.total_tokens += tokens
            if response_time:
                self.total_response_time += response_time
            
            # Update complexity metrics
            if query_complexity in self.query_complexity_metrics:
                self.query_complexity_metrics[query_complexity]["count"] += 1
                if response_time:
                    self.query_complexity_metrics[query_complexity]["total_time"] += response_time
                self.query_complexity_metrics[query_complexity]["total_accuracy"] += accuracy_score
            
            # Update RAG metrics
            if context_used and len(context_used) > 0:
                self.rag_metrics["with_rag"]["count"] += 1
                if response_time:
                    self.rag_metrics["with_rag"]["total_time"] += response_time
                if tokens:
                    self.rag_metrics["with_rag"]["total_tokens"] += tokens
            else:
                self.rag_metrics["without_rag"]["count"] += 1
                if response_time:
                    self.rag_metrics["without_rag"]["total_time"] += response_time
                if tokens:
                    self.rag_metrics["without_rag"]["total_tokens"] += tokens
            
            # Update model performance
            model_type = "general" if chat_type == "general" else "study"
            self.model_performance[model_type]["count"] += 1
            self.model_performance[model_type]["total_accuracy"] += accuracy_score
            
            # Update session metrics
            if session_id not in self.session_metrics:
                self.session_metrics[session_id] = {
                    "total_queries": 0,
                    "total_tokens": 0,
                    "avg_response_time": 0,
                    "total_time": 0,
                    "satisfaction_score": 0
                }
                
            self.session_metrics[session_id]["total_queries"] += 1
            if tokens:
                self.session_metrics[session_id]["total_tokens"] += tokens
            if response_time:
                total_time = self.session_metrics[session_id]["total_time"] + response_time
                self.session_metrics[session_id]["total_time"] = total_time
                self.session_metrics[session_id]["avg_response_time"] = (
                    total_time / self.session_metrics[session_id]["total_queries"]
                )
            
            # Update feedback counts
            if feedback:
                feedback_type = "neutral"
                if feedback.lower() in ["like", "positive", "thumbs up", "good"]:
                    feedback_type = "positive"
                elif feedback.lower() in ["dislike", "negative", "thumbs down", "bad"]:
                    feedback_type = "negative"
                
                self.feedback_counts[feedback_type] += 1
            
            # Calculate comprehensive metrics
            avg_response_time = self.total_response_time / self.total_conversations if self.total_conversations > 0 else 0
            
            # Log all metrics
            wandb.log({
                "conversations": self.conversation_table,
                "conversations/total": self.total_conversations,
                "conversations/tokens_used": self.total_tokens,
                "conversations/avg_response_time": avg_response_time,
                "conversations/active_sessions": len(self.session_metrics),
                "feedback/positive": self.feedback_counts["positive"],
                "feedback/negative": self.feedback_counts["negative"],
                "feedback/neutral": self.feedback_counts["neutral"],
                f"session/{session_id}/queries": self.session_metrics[session_id]["total_queries"],
                f"session/{session_id}/tokens": self.session_metrics[session_id]["total_tokens"],
                f"session/{session_id}/avg_response_time": self.session_metrics[session_id]["avg_response_time"]
            })
            
            # Log complexity-specific metrics
            for complexity, metrics in self.query_complexity_metrics.items():
                if metrics["count"] > 0:
                    avg_time = metrics["total_time"] / metrics["count"]
                    avg_accuracy = metrics["total_accuracy"] / metrics["count"]
                    wandb.log({
                        f"complexity/{complexity}/count": metrics["count"],
                        f"complexity/{complexity}/avg_response_time": avg_time,
                        f"complexity/{complexity}/avg_accuracy": avg_accuracy
                    })
            
            # Log RAG comparison metrics
            if self.rag_metrics["with_rag"]["count"] > 0:
                wandb.log({
                    "rag/with_rag_count": self.rag_metrics["with_rag"]["count"],
                    "rag/with_rag_avg_time": self.rag_metrics["with_rag"]["total_time"] / self.rag_metrics["with_rag"]["count"],
                    "rag/with_rag_avg_tokens": self.rag_metrics["with_rag"]["total_tokens"] / self.rag_metrics["with_rag"]["count"]
                })
            
            if self.rag_metrics["without_rag"]["count"] > 0:
                wandb.log({
                    "rag/without_rag_count": self.rag_metrics["without_rag"]["count"],
                    "rag/without_rag_avg_time": self.rag_metrics["without_rag"]["total_time"] / self.rag_metrics["without_rag"]["count"],
                    "rag/without_rag_avg_tokens": self.rag_metrics["without_rag"]["total_tokens"] / self.rag_metrics["without_rag"]["count"]
                })
            
            # Log model performance metrics
            for model, perf in self.model_performance.items():
                if perf["count"] > 0:
                    avg_accuracy = perf["total_accuracy"] / perf["count"]
                    error_rate = perf["errors"] / perf["count"]
                    wandb.log({
                        f"model/{model}/conversations": perf["count"],
                        f"model/{model}/avg_accuracy": avg_accuracy,
                        f"model/{model}/error_rate": error_rate
                    })
            
            # Calculate and log user satisfaction
            total_feedback = sum(self.feedback_counts.values())
            if total_feedback > 0:
                satisfaction = (self.feedback_counts["positive"] / total_feedback) * 100
                wandb.log({"feedback/satisfaction_percentage": satisfaction})
                
        except Exception as e:
            print(f"Error logging conversation to W&B: {e}")
    
    def _classify_query_complexity(self, query: str) -> str:
        """Classify query complexity based on content analysis."""
        word_count = len(query.split())
        
        # Simple heuristics for complexity
        if word_count < 10:
            return "simple"
        elif word_count < 25:
            return "medium"
        else:
            return "complex"
    
    def _estimate_accuracy(self, response: str, context_used: Optional[List[str]]) -> float:
        """Estimate accuracy score based on response characteristics."""
        # Basic heuristics for accuracy estimation
        score = 0.7  # Base score
        
        # Check response length
        if len(response) > 100:
            score += 0.1
        
        # Check if context was used
        if context_used and len(context_used) > 0:
            score += 0.1
        
        # Check for error indicators
        if "error" in response.lower() or "unable to" in response.lower():
            score -= 0.3
        
        return max(0.0, min(1.0, score))
    
    def log_error(self, error_type: str, error_message: str, session_id: Optional[str] = None,
                 query: Optional[str] = None) -> None:
        """Enhanced error logging."""
        if not self.is_initialized:
            self.initialize()
            
        try:
            # Update model error counts
            if "general" in error_type.lower():
                self.model_performance["general"]["errors"] += 1
            elif "study" in error_type.lower() or "claude" in error_type.lower():
                self.model_performance["study"]["errors"] += 1
            
            # Log error metrics
            wandb.log({
                "errors/count": 1,
                "errors/type": error_type,
                "errors/session_id": session_id or "unknown",
                "errors/query": query or "none"
            })
            
            # Add to error table
            error_info = {
                "type": error_type,
                "message": error_message,
                "session_id": session_id or "unknown",
                "query": query or "none",
                "timestamp": time.time()
            }
            
            if not hasattr(self, "error_table"):
                self.error_table = wandb.Table(columns=list(error_info.keys()))
            
            self.error_table.add_data(*error_info.values())
            wandb.log({"errors/details": self.error_table})
            
        except Exception as e:
            print(f"Error logging error to W&B: {e}")
    
    def log_system_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log system performance metrics."""
        if not self.is_initialized:
            self.initialize()
            
        try:
            # Add timestamp to metrics
            metrics["timestamp"] = time.time()
            
            # Log to metrics table for tracking
            for key, value in metrics.items():
                if key != "timestamp" and isinstance(value, (int, float)):
                    metric_type = key.split("/")[0]
                    metric_name = "/".join(key.split("/")[1:])
                    self.metrics_table.add_data(
                        metrics["timestamp"],
                        metric_type,
                        metric_name,
                        value,
                        "system"
                    )
            
            wandb.log(metrics)
            
        except Exception as e:
            print(f"Error logging system metrics to W&B: {e}")
    
    def log_file_upload(self, session_id: str, file_type: str, file_size: int, 
                         processing_time: float) -> None:
        """Log file upload and processing information."""
        if not self.is_initialized:
            self.initialize()
            
        try:
            # Log file metrics
            wandb.log({
                "files/upload_count": 1,
                "files/processing_time": processing_time,
                "files/size_kb": file_size / 1024,
                f"files/type_{file_type}": 1
            })
            
            # Add to file tracking table
            file_info = {
                "session_id": session_id,
                "file_type": file_type,
                "file_size": file_size,
                "processing_time": processing_time,
                "timestamp": time.time()
            }
            
            if not hasattr(self, "file_table"):
                self.file_table = wandb.Table(columns=list(file_info.keys()))
            
            self.file_table.add_data(*file_info.values())
            wandb.log({"files/details": self.file_table})
            
        except Exception as e:
            print(f"Error logging file upload to W&B: {e}")
    
    def log_performance_comparison(self, model: str, query_type: str, 
                                 response_time: float, accuracy: float, 
                                 tokens: int, with_rag: bool, 
                                 error_occurred: bool = False) -> None:
        """Log detailed performance comparison data."""
        if not self.is_initialized:
            self.initialize()
            
        try:
            # Add to performance table
            self.performance_table.add_data(
                time.time(),
                model,
                query_type,
                response_time,
                accuracy,
                tokens,
                with_rag,
                1.0 if error_occurred else 0.0
            )
            
            # Log the table
            wandb.log({"performance/comparison": self.performance_table})
            
            # Log specific metrics for easy visualization
            rag_suffix = "with_rag" if with_rag else "without_rag"
            wandb.log({
                f"performance/{model}/{rag_suffix}/response_time": response_time,
                f"performance/{model}/{rag_suffix}/accuracy": accuracy,
                f"performance/{model}/{rag_suffix}/tokens": tokens,
                f"performance/{model}/{query_type}/response_time": response_time,
                f"performance/{model}/{query_type}/accuracy": accuracy
            })
            
        except Exception as e:
            print(f"Error logging performance comparison to W&B: {e}")
    
    def create_summary_plots(self) -> None:
        """Create and log summary plots for Chapter 5 visualizations."""
        if not self.is_initialized:
            return
            
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Create performance comparison plot
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            
            # 1. Response time by complexity
            complexity_data = []
            for complexity, metrics in self.query_complexity_metrics.items():
                if metrics["count"] > 0:
                    avg_time = metrics["total_time"] / metrics["count"]
                    complexity_data.append({
                        "Complexity": complexity.capitalize(),
                        "Avg Response Time (s)": avg_time
                    })
            
            if complexity_data:
                import pandas as pd
                df = pd.DataFrame(complexity_data)
                sns.barplot(data=df, x="Complexity", y="Avg Response Time (s)", ax=axes[0, 0])
                axes[0, 0].set_title("Response Time by Query Complexity")
            
            # 2. Accuracy by model
            model_data = []
            for model, perf in self.model_performance.items():
                if perf["count"] > 0:
                    avg_accuracy = perf["total_accuracy"] / perf["count"]
                    model_data.append({
                        "Model": model.capitalize(),
                        "Avg Accuracy": avg_accuracy
                    })
            
            if model_data:
                df = pd.DataFrame(model_data)
                sns.barplot(data=df, x="Model", y="Avg Accuracy", ax=axes[0, 1])
                axes[0, 1].set_title("Average Accuracy by Model")
                axes[0, 1].set_ylim(0, 1)
            
            # 3. RAG comparison
            rag_data = []
            for rag_type in ["with_rag", "without_rag"]:
                if self.rag_metrics[rag_type]["count"] > 0:
                    avg_time = self.rag_metrics[rag_type]["total_time"] / self.rag_metrics[rag_type]["count"]
                    rag_data.append({
                        "RAG": rag_type.replace("_", " ").title(),
                        "Avg Response Time (s)": avg_time
                    })
            
            if rag_data:
                df = pd.DataFrame(rag_data)
                sns.barplot(data=df, x="RAG", y="Avg Response Time (s)", ax=axes[1, 0])
                axes[1, 0].set_title("Response Time: RAG vs No-RAG")
            
            # 4. User satisfaction
            total_feedback = sum(self.feedback_counts.values())
            if total_feedback > 0:
                feedback_data = []
                for feedback_type, count in self.feedback_counts.items():
                    percentage = (count / total_feedback) * 100
                    feedback_data.append({
                        "Feedback": feedback_type.capitalize(),
                        "Percentage": percentage
                    })
                
                df = pd.DataFrame(feedback_data)
                colors = ["#2ecc71", "#e74c3c", "#95a5a6"]
                axes[1, 1].pie(df["Percentage"], labels=df["Feedback"], colors=colors, autopct='%1.1f%%')
                axes[1, 1].set_title("User Satisfaction Distribution")
            
            plt.tight_layout()
            wandb.log({"performance_summary": wandb.Image(fig)})
            plt.close()
            
        except Exception as e:
            print(f"Error creating summary plots: {e}")
    
    def finish(self) -> None:
        """Finish the W&B run with comprehensive summary."""
        if self.is_initialized and self.run is not None:
            try:
                # Check if we're in a shutdown state
                import sys
                if sys.meta_path is None:
                    print("W&B: Interpreter shutting down, skipping summary plots")
                    return
                    
                # Try to create summary plots if possible
                try:
                    self.create_summary_plots()
                except Exception as e:
                    print(f"Could not create summary plots: {e}")
                
                # Calculate final metrics
                avg_response_time = self.total_response_time / self.total_conversations if self.total_conversations > 0 else 0
                
                # Calculate complexity-based averages
                complexity_summary = {}
                for complexity, metrics in self.query_complexity_metrics.items():
                    if metrics["count"] > 0:
                        complexity_summary[f"{complexity}_avg_time"] = metrics["total_time"] / metrics["count"]
                        complexity_summary[f"{complexity}_avg_accuracy"] = metrics["total_accuracy"] / metrics["count"]
                
                # Calculate model-based averages
                model_summary = {}
                for model, perf in self.model_performance.items():
                    if perf["count"] > 0:
                        model_summary[f"{model}_avg_accuracy"] = perf["total_accuracy"] / perf["count"]
                        model_summary[f"{model}_error_rate"] = perf["errors"] / perf["count"]
                
                # Try to update summary
                try:
                    wandb.summary.update({
                        "total_conversations": self.total_conversations,
                        "total_tokens": self.total_tokens,
                        "avg_response_time": avg_response_time,
                        "total_sessions": len(self.session_metrics),
                        "positive_feedback": self.feedback_counts["positive"],
                        "negative_feedback": self.feedback_counts["negative"],
                        "neutral_feedback": self.feedback_counts["neutral"],
                        **complexity_summary,
                        **model_summary
                    })
                except Exception as e:
                    print(f"Could not update W&B summary: {e}")
                
                # Try to log final tables
                try:
                    wandb.log({
                        "final_conversations": self.conversation_table,
                        "final_metrics": self.metrics_table,
                        "final_performance": self.performance_table
                    })
                except Exception as e:
                    print(f"Could not log final tables: {e}")
                
                # Finish the run
                try:
                    self.run.finish()
                except Exception as e:
                    print(f"Error finishing W&B run: {e}")
                    
                self.is_initialized = False
                print("W&B tracking finished")
                
            except Exception as e:
                print(f"Error in W&B finish: {e}")