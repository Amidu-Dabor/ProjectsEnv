# services/wandb_service.py

import os
import time
import json
import wandb
from typing import Dict, List, Any, Optional, Union

class WandbTracker:
    """Class to handle Weights & Biases integration for chatbot monitoring and evaluation."""
    
    def __init__(self, project_name: str = "usiu-chatbot", entity: Optional[str] = None, 
                 api_key: Optional[str] = None, tags: Optional[List[str]] = None):
        """
        Initialize the WandbTracker.
        
        Args:
            project_name: The name of the W&B project
            entity: The W&B entity (username or team name)
            api_key: Optional W&B API key (can also be set via WANDB_API_KEY env var)
            tags: Optional tags for the run
        """
        self.project_name = project_name
        self.entity = entity
        self.tags = tags or ["gradio-chatbot", "production"]
        
        # Set API key if provided (otherwise, wandb will look for WANDB_API_KEY env var)
        if api_key:
            os.environ["WANDB_API_KEY"] = api_key
            
        # Initialize W&B run
        self.run = None
        self.is_initialized = False
        self.session_metrics = {}
        
        # Chat metrics
        self.total_conversations = 0
        self.total_tokens = 0
        self.total_response_time = 0
        self.feedback_counts = {"positive": 0, "negative": 0, "neutral": 0}
        
        # Create metrics table structure for logging conversations
        self.conversation_table = None

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the W&B run."""
        if self.is_initialized:
            return
            
        default_config = {
            "app_version": "1.0.0",
            "interface_type": "gradio",
            "retrieval_method": "vector_store",
            "max_context_length": 8000
        }
        
        # Merge default config with provided config
        run_config = {**default_config, **(config or {})}
        
        # Initialize W&B run
        self.run = wandb.init(
            project=self.project_name,
            entity=self.entity,
            config=run_config,
            tags=self.tags,
            job_type="chatbot",
            notes="Gradio chatbot monitoring with W&B integration",
            reinit="return_previous"
        )
        
        # Create table for tracking conversations
        self.conversation_table = wandb.Table(
            columns=["timestamp", "session_id", "user_id", "chat_type", 
                     "query", "response", "context_used", "tokens", 
                     "response_time", "feedback"]
        )
        
        self.is_initialized = True
        print(f"W&B initialized for project {self.project_name}")
        
    def log_conversation(self, 
                       session_id: str,
                       user_id: Optional[str],
                       chat_type: str,
                       query: str,
                       response: str,
                       context_used: Optional[List[str]] = None,
                       tokens: Optional[int] = None,
                       response_time: Optional[float] = None,
                       feedback: Optional[str] = None) -> None:
        """
        Log a conversation exchange to W&B.
        
        Args:
            session_id: Unique identifier for the user session
            user_id: User identifier (email or anonymous ID)
            chat_type: Type of chat (e.g., 'general', 'study_support')
            query: User's query text
            response: Model's response text
            context_used: Optional list of context snippets used for RAG
            tokens: Optional count of tokens used
            response_time: Optional time taken to generate response
            feedback: Optional user feedback on the response
        """
        if not self.is_initialized:
            self.initialize()
            
        try:
            # Format context for JSON serialization
            context_json = json.dumps(context_used) if context_used else "[]"
            
            # Add row to conversation table
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
                feedback or "none"
            )
            
            # Log the updated table
            wandb.log({"conversations": self.conversation_table})
            
            # Update global metrics
            self.total_conversations += 1
            if tokens:
                self.total_tokens += tokens
            if response_time:
                self.total_response_time += response_time
            
            # Track session-level metrics
            if session_id not in self.session_metrics:
                self.session_metrics[session_id] = {
                    "total_queries": 0,
                    "total_tokens": 0,
                    "avg_response_time": 0,
                    "total_time": 0
                }
                
            # Update session metrics
            self.session_metrics[session_id]["total_queries"] += 1
            if tokens:
                self.session_metrics[session_id]["total_tokens"] += tokens
            if response_time:
                total_time = self.session_metrics[session_id]["total_time"] + response_time
                self.session_metrics[session_id]["total_time"] = total_time
                self.session_metrics[session_id]["avg_response_time"] = (
                    total_time / self.session_metrics[session_id]["total_queries"]
                )
                
            # Update feedback counts if provided
            if feedback:
                feedback_type = "neutral"
                if feedback.lower() in ["like", "positive", "thumbs up", "good"]:
                    feedback_type = "positive"
                elif feedback.lower() in ["dislike", "negative", "thumbs down", "bad"]:
                    feedback_type = "negative"
                
                self.feedback_counts[feedback_type] += 1
                
            # Calculate average response time
            avg_response_time = self.total_response_time / self.total_conversations if self.total_conversations > 0 else 0
                
            # Log session metrics
            wandb.log({
                f"session_{session_id}_queries": self.session_metrics[session_id]["total_queries"],
                f"session_{session_id}_tokens": self.session_metrics[session_id]["total_tokens"],
                f"session_{session_id}_avg_response_time": self.session_metrics[session_id]["avg_response_time"]
            })
            
            # Log global metrics
            wandb.log({
                "conversations/total": self.total_conversations,
                "conversations/tokens_used": self.total_tokens,
                "conversations/avg_response_time": avg_response_time,
                "conversations/active_sessions": len(self.session_metrics),
                "feedback/positive": self.feedback_counts["positive"],
                "feedback/negative": self.feedback_counts["negative"],
                "feedback/neutral": self.feedback_counts["neutral"]
            })
            
            # Calculate and log user satisfaction percentage
            total_feedback = sum(self.feedback_counts.values())
            if total_feedback > 0:
                satisfaction = (self.feedback_counts["positive"] / total_feedback) * 100
                wandb.log({"feedback/satisfaction_percentage": satisfaction})
                
        except Exception as e:
            print(f"Error logging conversation to W&B: {e}")
    
    def log_error(self, error_type: str, error_message: str, session_id: Optional[str] = None,
                 query: Optional[str] = None) -> None:
        """Log an error to W&B."""
        if not self.is_initialized:
            self.initialize()
            
        try:
            # Log error event
            wandb.log({
                "errors/count": 1,
                "errors/type": error_type,
                "errors/session_id": session_id or "unknown",
                "errors/query": query or "none"
            })
            
            # Add to error table if we want to track details
            error_info = {
                "type": error_type,
                "message": error_message,
                "session_id": session_id or "unknown",
                "query": query or "none",
                "timestamp": time.time()
            }
            
            # Log as a separate artifact for detailed error tracking
            if not hasattr(self, "error_table"):
                self.error_table = wandb.Table(columns=list(error_info.keys()))
            
            self.error_table.add_data(*error_info.values())
            wandb.log({"errors/details": self.error_table})
            
        except Exception as e:
            print(f"Error logging error to W&B: {e}")
    
    def log_system_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log system performance metrics to W&B."""
        if not self.is_initialized:
            self.initialize()
            
        try:
            wandb.log(metrics)
        except Exception as e:
            print(f"Error logging system metrics to W&B: {e}")
    
    def log_file_upload(self, session_id: str, file_type: str, file_size: int, 
                         processing_time: float) -> None:
        """Log file upload and processing information."""
        if not self.is_initialized:
            self.initialize()
            
        try:
            # Log file upload metrics
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
    
    def finish(self) -> None:
        """Finish the W&B run gracefully."""
        if self.is_initialized and self.run is not None:
            try:
                # Log final summary metrics
                wandb.summary.update({
                    "total_conversations": self.total_conversations,
                    "total_tokens": self.total_tokens,
                    "avg_response_time": self.total_response_time / self.total_conversations if self.total_conversations > 0 else 0,
                    "total_sessions": len(self.session_metrics),
                    "positive_feedback": self.feedback_counts["positive"],
                    "negative_feedback": self.feedback_counts["negative"],
                    "neutral_feedback": self.feedback_counts["neutral"]
                })
                
                self.run.finish()
                self.is_initialized = False
                print("W&B tracking finished")
                
            except Exception as e:
                print(f"Error finishing W&B run: {e}")