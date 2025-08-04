#!/usr/bin/env python
import time
import json
import random
import argparse
import os
import csv
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import numpy as np
import openai
import anthropic
import wandb

# Import your services
from api_gateway.gateway import register_service, get_gateway_metrics, get_service, register_wandb_service
from vector_services.data_curator import DataCurator
from services.data_service import DataService
from configs.config import GPT4O_MODEL, CLAUDE_MODEL

# Constants for test configuration
DEFAULT_TEST_ITERATIONS = 20
DEFAULT_OUTPUT_DIR = "evaluation_results"


class LLMEvaluator:
    """
    Comprehensive evaluator for LLM responses that assesses response time, 
    accuracy, and system performance across different models.
    """
    
    def __init__(
        self, 
        general_model: str = GPT4O_MODEL, 
        study_model: str = CLAUDE_MODEL,
        retriever = None,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        wandb_tracking: bool = True
    ):
        """
        Initialize the evaluator with the models to test and retriever for RAG.
        
        Args:
            general_model: Model ID for OpenAI model (general enquiries)
            study_model: Model ID for Claude model (study support)
            retriever: Vector store retriever for RAG
            output_dir: Directory to save evaluation results
            wandb_tracking: Whether to log results to W&B
        """
        self.general_model = general_model
        self.study_model = study_model
        self.retriever = retriever
        self.output_dir = output_dir
        self.wandb_tracking = wandb_tracking
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Initialize clients
        self.openai_client = openai.OpenAI()
        self.claude_client = anthropic.Anthropic()
        
        # Initialize data service to get prompts
        self.data_service = DataService(retriever=retriever)
        self.general_prompt, self.study_prompt = self.data_service.prompts_service.get_prompt()
        
        # Initialize W&B
        if wandb_tracking:
            config = {
                "general_model": general_model,
                "study_model": study_model,
                "evaluation_type": "response_quality",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            self.wandb_tracker = register_wandb_service(config)
            if not self.wandb_tracker:
                print("Warning: Could not initialize W&B tracking. Continuing without it.")
                self.wandb_tracking = False
        
        # Load or generate test queries
        self.general_queries = self._load_test_queries("general")
        self.study_queries = self._load_test_queries("study")
        
        # Prepare result storage
        self.results = {
            "general": [],
            "study": []
        }
        
    def _load_test_queries(self, query_type: str) -> List[Dict[str, Any]]:
        """
        Load test queries from file or generate new ones if file doesn't exist.
        
        Args:
            query_type: Type of queries to load ('general' or 'study')
            
        Returns:
            List of query dictionaries
        """
        filename = os.path.join(self.output_dir, f"{query_type}_test_queries.json")
        
        # Check if file exists
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        
        # Generate new test queries
        print(f"Generating new {query_type} test queries...")
        queries = self._generate_test_queries(query_type)
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(queries, f, indent=2)
            
        return queries
    
    def _generate_test_queries(self, query_type: str, num_queries: int = 20) -> List[Dict[str, Any]]:
        """
        Generate test queries for evaluation using the LLM itself.
        
        Args:
            query_type: Type of queries to generate ('general' or 'study')
            num_queries: Number of queries to generate
            
        Returns:
            List of query dictionaries
        """
        # Prompts for generating different types of test queries
        generation_prompts = {
            "general": """
            You are tasked with creating a diverse set of test queries that a university student might ask an AI assistant.
            Generate {num_queries} different queries related to university information, admissions, academic policies, campus services,
            and general information. Include some simple questions and some complex multi-part questions.
            
            For each query, include:
            1. The query text
            2. Expected response elements (key points that should be included in a good response)
            3. Complexity level (simple, moderate, complex)
            4. Category (e.g., admissions, academics, campus life)
            
            Format your response as a JSON array with objects containing "query", "expected_elements", "complexity", and "category" fields.
            """,
            "study": """
            You are tasked with creating a diverse set of test queries that a university student might ask an AI study assistant.
            Generate {num_queries} different queries related to academic support, writing assistance, research help, 
            programming problems, math questions, and subject-specific help. Include some simple questions and some that require step-by-step guidance.
            
            For each query, include:
            1. The query text
            2. Expected response elements (key points that should be included in a good response)
            3. Complexity level (simple, moderate, complex)
            4. Category (e.g., programming, writing, research, math, science)
            
            Format your response as a JSON array with objects containing "query", "expected_elements", "complexity", and "category" fields.
            """
        }
        
        # Choose the appropriate prompt
        prompt = generation_prompts[query_type].format(num_queries=num_queries)
        
        # Generate queries using OpenAI
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            # Parse the JSON from the content string
            data = json.loads(content)
            
            # Extract the array of queries (assumes the response has a top-level array)
            if "queries" in data:
                return data["queries"]
            else:
                # If the JSON structure is different, find the first array in the response
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 0:
                        return value
                        
            # Fallback: Return an empty list
            return []
            
        except Exception as e:
            print(f"Error generating test queries: {e}")
            # Return a small set of default queries
            return [
                {
                    "query": "What are the admission requirements?",
                    "expected_elements": ["GPA", "test scores", "application process"],
                    "complexity": "simple",
                    "category": "admissions"
                },
                {
                    "query": "How do I register for classes?",
                    "expected_elements": ["registration dates", "course catalog", "advisor"],
                    "complexity": "simple", 
                    "category": "academics"
                }
            ]
    
    def _generate_response(
        self, 
        query: str, 
        model_type: str, 
        with_rag: bool = True
    ) -> Tuple[str, float, Dict[str, Any]]:
        """
        Generate a response using the specified model with timing and metadata.
        
        Args:
            query: The query text to send to the model
            model_type: 'general' (OpenAI) or 'study' (Claude)
            with_rag: Whether to use RAG for this query
            
        Returns:
            Tuple of (response_text, response_time, metadata)
        """
        start_time = time.time()
        response_text = ""
        metadata = {
            "token_count": 0,
            "retrieved_docs": [],
            "error": None
        }
        
        try:
            # Use the appropriate model and prompt based on type
            if model_type == "general":
                model = self.general_model
                system_prompt = self.general_prompt
                
                # Prepare messages for OpenAI
                messages = [{"role": "system", "content": system_prompt}]
                
                # Add RAG context if requested
                if with_rag and self.retriever:
                    try:
                        # Retrieve relevant documents
                        docs = self.retriever.invoke(query)
                        if docs:
                            # Store document content for logging
                            metadata["retrieved_docs"] = [doc.page_content[:200] + "..." for doc in docs]
                            
                            # Add context to the prompt
                            context_text = "\n\n".join([doc.page_content for doc in docs])
                            messages.insert(1, {
                                "role": "system",
                                "content": f"Additional Context:\n{context_text}"
                            })
                    except Exception as e:
                        print(f"RAG retrieval error: {e}")
                        metadata["error"] = f"RAG error: {str(e)}"
                
                # Add the user query
                messages.append({"role": "user", "content": query})
                
                # Generate response with OpenAI
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
                
                response_text = response.choices[0].message.content
                metadata["token_count"] = response.usage.total_tokens
                
            elif model_type == "study":
                model = self.study_model
                system_prompt = self.study_prompt
                
                # Generate response with Claude
                response = self.claude_client.messages.create(
                    model=model,
                    system=system_prompt,
                    messages=[{"role": "user", "content": query}],
                    max_tokens=1000,
                    temperature=0.7
                )
                
                response_text = response.content[0].text
                # Claude doesn't provide token count directly, estimate it
                metadata["token_count"] = len(query.split()) + len(response_text.split()) * 1.3
        
        except Exception as e:
            print(f"Error generating response: {e}")
            response_text = f"Error: {str(e)}"
            metadata["error"] = str(e)
        
        response_time = time.time() - start_time
        return response_text, response_time, metadata
    
    def _evaluate_response(
        self, 
        query: Dict[str, Any], 
        response: str, 
        model_type: str
    ) -> Dict[str, Any]:
        """
        Evaluate the quality of a response against expected elements.
        
        Args:
            query: Query dictionary with expected elements
            response: Response text to evaluate
            model_type: 'general' or 'study'
            
        Returns:
            Dictionary with evaluation metrics
        """
        # First, do basic checks that don't require LLM evaluation
        expected_elements = query.get("expected_elements", [])
        
        # Check presence of expected elements
        element_presence = 0
        for element in expected_elements:
            if element.lower() in response.lower():
                element_presence += 1
        
        elements_score = element_presence / len(expected_elements) if expected_elements else 0
        
        # Check for error messages
        has_error = "error" in response.lower() or "unable to" in response.lower()
        
        # Check response length (as a rough quality metric)
        length_score = min(1.0, len(response) / 1000)  # Max score at 1000 chars
        
        # Calculate basic accuracy score based on these simple metrics
        basic_accuracy = (elements_score * 0.7 + length_score * 0.3) * (0.2 if has_error else 1.0)
        
        # Perform LLM-based evaluation for more nuanced scoring
        evaluation_result = self._llm_evaluate_response(query, response, model_type)
        
        # Combine the scores
        final_accuracy = 0.3 * basic_accuracy + 0.7 * evaluation_result["accuracy"]
        
        return {
            "accuracy": final_accuracy,
            "relevance": evaluation_result["relevance"],
            "completeness": evaluation_result["completeness"],
            "coherence": evaluation_result["coherence"],
            "elements_covered": element_presence,
            "total_elements": len(expected_elements),
            "has_error": has_error,
            "evaluation_comment": evaluation_result["comment"]
        }
    
    def _llm_evaluate_response(
        self, 
        query: Dict[str, Any], 
        response: str, 
        model_type: str
    ) -> Dict[str, Any]:
        """
        Use an LLM to evaluate response quality based on multiple dimensions.
        
        Args:
            query: Original query with expected elements
            response: Response text to evaluate
            model_type: Type of query ('general' or 'study')
            
        Returns:
            Dictionary with evaluation metrics
        """
        evaluation_prompt = f"""
        You are an expert evaluator of AI assistant responses. Assess the following response to a user query.
        
        USER QUERY: {query['query']}
        
        EXPECTED ELEMENTS: {', '.join(query.get('expected_elements', []))}
        
        QUERY COMPLEXITY: {query.get('complexity', 'unknown')}
        
        QUERY CATEGORY: {query.get('category', 'unknown')}
        
        AI RESPONSE TO EVALUATE:
        {response}
        
        Evaluate the response on the following dimensions (score from 0.0 to 1.0):
        
        1. Accuracy: Does the response provide factually correct information?
        2. Relevance: How relevant is the response to the query?
        3. Completeness: Does the response address all aspects of the query?
        4. Coherence: Is the response well-structured, logical, and easy to follow?
        
        Also provide a brief comment explaining your evaluation.
        
        Format your response as a JSON object with the following fields:
        {{"accuracy": float, "relevance": float, "completeness": float, "coherence": float, "comment": string}}
        """
        
        try:
            # Use a different model from what we're evaluating to avoid bias
            evaluation_model = "gpt-4o-mini"  # Use a smaller model for evaluation to save costs
            
            response = self.openai_client.chat.completions.create(
                model=evaluation_model,
                messages=[{"role": "system", "content": evaluation_prompt}],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Error in LLM evaluation: {e}")
            # Return default values if evaluation fails
            return {
                "accuracy": 0.5,
                "relevance": 0.5,
                "completeness": 0.5,
                "coherence": 0.5,
                "comment": f"Evaluation failed: {str(e)}"
            }
    
    def run_evaluation(self, iterations: int = DEFAULT_TEST_ITERATIONS):
        """
        Run a comprehensive evaluation with the specified number of iterations.
        Tests both general and study-related queries with various configurations.
        
        Args:
            iterations: Number of test iterations to run
        """
        print(f"Starting LLM evaluation with {iterations} iterations...")
        
        # Track system metrics at the start
        self._log_system_metrics("start")
        
        # Process general queries
        print("\nEvaluating general queries (OpenAI model)...")
        self._evaluate_query_batch("general", iterations)
        
        # Process study support queries
        print("\nEvaluating study support queries (Claude model)...")
        self._evaluate_query_batch("study", iterations)
        
        # Track system metrics at the end
        self._log_system_metrics("end")
        
        # Save and analyze results
        self._save_results()
        self._generate_report()
        
        print(f"\nEvaluation complete. Results saved to {self.output_dir}")
    
    def _evaluate_query_batch(self, query_type: str, iterations: int):
        """
        Evaluate a batch of queries of the specified type.
        
        Args:
            query_type: Type of queries to evaluate ('general' or 'study')
            iterations: Number of iterations to run
        """
        # Get the appropriate query list
        queries = self.general_queries if query_type == "general" else self.study_queries
        
        # Use a subset of queries based on the iterations requested
        test_queries = []
        for _ in range(iterations):
            test_queries.append(random.choice(queries))
        
        # Run evaluation for each query
        for i, query in enumerate(tqdm(test_queries, desc=f"{query_type.capitalize()} Queries")):
            query_text = query["query"]
            
            # For general queries, test both with and without RAG if a retriever is available
            if query_type == "general" and self.retriever:
                # Test with RAG
                rag_response, rag_time, rag_metadata = self._generate_response(
                    query_text, query_type, with_rag=True
                )
                rag_evaluation = self._evaluate_response(query, rag_response, query_type)
                
                # Save result
                self.results[query_type].append({
                    "query_id": f"{query_type}_{i}_rag",
                    "query_text": query_text,
                    "query_category": query.get("category", "unknown"),
                    "query_complexity": query.get("complexity", "unknown"),
                    "response": rag_response,
                    "response_time": rag_time,
                    "with_rag": True,
                    "token_count": rag_metadata["token_count"],
                    "retrieved_docs": rag_metadata["retrieved_docs"],
                    "error": rag_metadata["error"],
                    **rag_evaluation  # Include all evaluation metrics
                })
                
                # Log to W&B
                if self.wandb_tracking and self.wandb_tracker:
                    self.wandb_tracker.log_conversation(
                        session_id=f"eval_{query_type}_rag",
                        user_id="evaluator",
                        chat_type=f"{query_type}_with_rag",
                        query=query_text,
                        response=rag_response,
                        context_used=rag_metadata["retrieved_docs"],
                        tokens=rag_metadata["token_count"],
                        response_time=rag_time,
                        feedback=None
                    )
                    
                    # Log evaluation metrics
                    self.wandb_tracker.log_system_metrics({
                        f"eval/{query_type}_rag/accuracy": rag_evaluation["accuracy"],
                        f"eval/{query_type}_rag/relevance": rag_evaluation["relevance"],
                        f"eval/{query_type}_rag/completeness": rag_evaluation["completeness"],
                        f"eval/{query_type}_rag/coherence": rag_evaluation["coherence"],
                        f"eval/{query_type}_rag/response_time": rag_time
                    })
                
                # Test without RAG
                no_rag_response, no_rag_time, no_rag_metadata = self._generate_response(
                    query_text, query_type, with_rag=False
                )
                no_rag_evaluation = self._evaluate_response(query, no_rag_response, query_type)
                
                # Save result
                self.results[query_type].append({
                    "query_id": f"{query_type}_{i}_no_rag",
                    "query_text": query_text,
                    "query_category": query.get("category", "unknown"),
                    "query_complexity": query.get("complexity", "unknown"),
                    "response": no_rag_response,
                    "response_time": no_rag_time,
                    "with_rag": False,
                    "token_count": no_rag_metadata["token_count"],
                    "retrieved_docs": [],
                    "error": no_rag_metadata["error"],
                    **no_rag_evaluation  # Include all evaluation metrics
                })
                
                # Log to W&B
                if self.wandb_tracking and self.wandb_tracker:
                    self.wandb_tracker.log_conversation(
                        session_id=f"eval_{query_type}_no_rag",
                        user_id="evaluator",
                        chat_type=f"{query_type}_without_rag",
                        query=query_text,
                        response=no_rag_response,
                        context_used=[],
                        tokens=no_rag_metadata["token_count"],
                        response_time=no_rag_time,
                        feedback=None
                    )
                    
                    # Log evaluation metrics
                    self.wandb_tracker.log_system_metrics({
                        f"eval/{query_type}_no_rag/accuracy": no_rag_evaluation["accuracy"],
                        f"eval/{query_type}_no_rag/relevance": no_rag_evaluation["relevance"],
                        f"eval/{query_type}_no_rag/completeness": no_rag_evaluation["completeness"],
                        f"eval/{query_type}_no_rag/coherence": no_rag_evaluation["coherence"],
                        f"eval/{query_type}_no_rag/response_time": no_rag_time
                    })
                
            else:
                # For study queries or when no retriever is available, just test normally
                response, time_taken, metadata = self._generate_response(
                    query_text, query_type, with_rag=False
                )
                evaluation = self._evaluate_response(query, response, query_type)
                
                # Save result
                self.results[query_type].append({
                    "query_id": f"{query_type}_{i}",
                    "query_text": query_text,
                    "query_category": query.get("category", "unknown"),
                    "query_complexity": query.get("complexity", "unknown"),
                    "response": response,
                    "response_time": time_taken,
                    "with_rag": False,
                    "token_count": metadata["token_count"],
                    "retrieved_docs": [],
                    "error": metadata["error"],
                    **evaluation  # Include all evaluation metrics
                })
                
                # Log to W&B
                if self.wandb_tracking and self.wandb_tracker:
                    self.wandb_tracker.log_conversation(
                        session_id=f"eval_{query_type}",
                        user_id="evaluator",
                        chat_type=query_type,
                        query=query_text,
                        response=response,
                        context_used=[],
                        tokens=metadata["token_count"],
                        response_time=time_taken,
                        feedback=None
                    )
                    
                    # Log evaluation metrics
                    self.wandb_tracker.log_system_metrics({
                        f"eval/{query_type}/accuracy": evaluation["accuracy"],
                        f"eval/{query_type}/relevance": evaluation["relevance"],
                        f"eval/{query_type}/completeness": evaluation["completeness"],
                        f"eval/{query_type}/coherence": evaluation["coherence"],
                        f"eval/{query_type}/response_time": time_taken
                    })
    
    def _log_system_metrics(self, stage: str):
        """
        Log system performance metrics to W&B.
        
        Args:
            stage: Stage of evaluation ('start' or 'end')
        """
        if not self.wandb_tracking or not self.wandb_tracker:
            return
            
        try:
            import psutil
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Log to W&B
            self.wandb_tracker.log_system_metrics({
                f"system/{stage}/cpu_percent": cpu_percent,
                f"system/{stage}/memory_percent": memory.percent,
                f"system/{stage}/memory_used_gb": memory.used / (1024 ** 3)
            })
            
            # Also log to terminal
            print(f"\nSystem metrics ({stage}):")
            print(f"  CPU usage: {cpu_percent}%")
            print(f"  Memory usage: {memory.percent}%")
            
        except Exception as e:
            print(f"Error logging system metrics: {e}")
    
    def _save_results(self):
        """Save evaluation results to files."""
        # Save detailed JSON results
        for query_type in ["general", "study"]:
            filename = os.path.join(self.output_dir, f"{query_type}_results.json")
            with open(filename, 'w') as f:
                json.dump(self.results[query_type], f, indent=2)
                
            # Also save a CSV version for easier analysis
            csv_filename = os.path.join(self.output_dir, f"{query_type}_results.csv")
            if self.results[query_type]:
                # Extract the fields we want in the CSV
                csv_data = []
                for result in self.results[query_type]:
                    csv_data.append({
                        "query_id": result["query_id"],
                        "query_text": result["query_text"],
                        "query_category": result["query_category"],
                        "query_complexity": result["query_complexity"],
                        "response_time": result["response_time"],
                        "token_count": result["token_count"],
                        "with_rag": result["with_rag"],
                        "accuracy": result["accuracy"],
                        "relevance": result["relevance"],
                        "completeness": result["completeness"],
                        "coherence": result["coherence"],
                        "elements_covered": result["elements_covered"],
                        "total_elements": result["total_elements"],
                        "has_error": result["has_error"]
                    })
                
                # Write to CSV
                with open(csv_filename, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                    writer.writeheader()
                    writer.writerows(csv_data)
    
    def _generate_report(self):
        """Generate evaluation report with visualizations."""
        print("\nGenerating evaluation report...")
        
        # Prepare dataframes for analysis
        dfs = {}
        for query_type in ["general", "study"]:
            if not self.results[query_type]:
                continue
                
            # Convert results to dataframe
            df = pd.DataFrame(self.results[query_type])
            dfs[query_type] = df
            
            # Calculate aggregate metrics
            print(f"\n{query_type.capitalize()} Queries:")
            print(f"  Total queries: {len(df)}")
            print(f"  Average response time: {df['response_time'].mean():.4f}s")
            print(f"  Average accuracy: {df['accuracy'].mean():.4f}")
            print(f"  Average relevance: {df['relevance'].mean():.4f}")
            print(f"  Average completeness: {df['completeness'].mean():.4f}")
            print(f"  Average coherence: {df['coherence'].mean():.4f}")
            
            # If we have both RAG and no-RAG results, compare them
            if 'with_rag' in df.columns and df['with_rag'].nunique() > 1:
                rag_df = df[df['with_rag'] == True]
                no_rag_df = df[df['with_rag'] == False]
                
                print("\n  RAG vs. No-RAG Comparison:")
                print(f"    RAG average response time: {rag_df['response_time'].mean():.4f}s")
                print(f"    No-RAG average response time: {no_rag_df['response_time'].mean():.4f}s")
                print(f"    RAG average accuracy: {rag_df['accuracy'].mean():.4f}")
                print(f"    No-RAG average accuracy: {no_rag_df['accuracy'].mean():.4f}")
        
        # Generate visualizations
        self._generate_visualizations(dfs)
        
        # Create a combined summary report
        self._create_summary_report(dfs)
    
    def _generate_visualizations(self, dfs: Dict[str, pd.DataFrame]):
        """
        Generate visualizations from evaluation results.
        
        Args:
            dfs: Dictionary of dataframes with results
        """
        for query_type, df in dfs.items():
            # Set up the figure
            plt.figure(figsize=(16, 12))
            plt.suptitle(f"{query_type.capitalize()} Query Evaluation Results", fontsize=16)
            
            # 1. Response time distribution
            plt.subplot(2, 3, 1)
            sns.histplot(df['response_time'], kde=True)
            plt.title("Response Time Distribution")
            plt.xlabel("Response Time (s)")
            plt.ylabel("Count")
            
            # 2. Accuracy by complexity
            plt.subplot(2, 3, 2)
            if 'query_complexity' in df.columns:
                sns.boxplot(x='query_complexity', y='accuracy', data=df)
                plt.title("Accuracy by Query Complexity")
                plt.xlabel("Complexity")
                plt.ylabel("Accuracy Score")
            
            # 3. Quality metrics comparison
            plt.subplot(2, 3, 3)
            quality_metrics = ['accuracy', 'relevance', 'completeness', 'coherence']
            avg_metrics = [df[metric].mean() for metric in quality_metrics]
            sns.barplot(x=quality_metrics, y=avg_metrics)
            plt.title("Average Quality Metrics")
            plt.ylim(0, 1)
            plt.xticks(rotation=45)
            
            # 4. RAG vs No-RAG comparison (if applicable)
            plt.subplot(2, 3, 4)
            if 'with_rag' in df.columns and df['with_rag'].nunique() > 1:
                metrics_by_rag = df.groupby('with_rag')[quality_metrics].mean().reset_index()
                metrics_by_rag = pd.melt(metrics_by_rag, 
                                        id_vars=['with_rag'], 
                                        value_vars=quality_metrics,
                                        var_name='metric', 
                                        value_name='score')
                sns.barplot(x='metric', y='score', hue='with_rag', data=metrics_by_rag)
                plt.title("RAG vs No-RAG Comparison")
                plt.xlabel("Metric")
                plt.ylabel("Score")
                plt.ylim(0, 1)
                plt.xticks(rotation=45)
                plt.legend(title='RAG Used')
            
            # 5. Response time by complexity
            plt.subplot(2, 3, 5)
            if 'query_complexity' in df.columns:
                sns.boxplot(x='query_complexity', y='response_time', data=df)
                plt.title("Response Time by Query Complexity")
                plt.xlabel("Complexity")
                plt.ylabel("Response Time (s)")
            
            # 6. Token count distribution
            plt.subplot(2, 3, 6)
            sns.histplot(df['token_count'], kde=True)
            plt.title("Token Count Distribution")
            plt.xlabel("Token Count")
            plt.ylabel("Count")
            
            plt.tight_layout()
            
            # Save the figure
            plt.savefig(os.path.join(self.output_dir, f"{query_type}_visualizations.png"))
            plt.close()
            
            # Log visualizations to W&B
            if self.wandb_tracking and self.wandb_tracker:
                try:
                    visualization_path = os.path.join(self.output_dir, f"{query_type}_visualizations.png")
                    self.wandb_tracker.run.log({f"{query_type}_visualizations": wandb.Image(visualization_path)})
                except Exception as e:
                    print(f"Error logging visualizations to W&B: {e}")
    
    def _create_summary_report(self, dfs: Dict[str, pd.DataFrame]):
        """
        Create a summary report with key findings.
        
        Args:
            dfs: Dictionary of dataframes with results
        """
        summary = {
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "general_model": self.general_model,
            "study_model": self.study_model,
            "metrics": {}
        }
        
        for query_type, df in dfs.items():
            summary["metrics"][query_type] = {
                "query_count": len(df),
                "avg_response_time": round(df['response_time'].mean(), 4),
                "avg_accuracy": round(df['accuracy'].mean(), 4),
                "avg_relevance": round(df['relevance'].mean(), 4),
                "avg_completeness": round(df['completeness'].mean(), 4),
                "avg_coherence": round(df['coherence'].mean(), 4)
            }
            
            # Add RAG comparison if available
            if 'with_rag' in df.columns and df['with_rag'].nunique() > 1:
                rag_df = df[df['with_rag'] == True]
                no_rag_df = df[df['with_rag'] == False]
                
                summary["metrics"][query_type]["rag_comparison"] = {
                    "rag_response_time": round(rag_df['response_time'].mean(), 4),
                    "no_rag_response_time": round(no_rag_df['response_time'].mean(), 4),
                    "rag_accuracy": round(rag_df['accuracy'].mean(), 4),
                    "no_rag_accuracy": round(no_rag_df['accuracy'].mean(), 4),
                    "rag_vs_no_rag_accuracy_diff": round(rag_df['accuracy'].mean() - no_rag_df['accuracy'].mean(), 4)
                }
        
        # Save summary to file
        with open(os.path.join(self.output_dir, "evaluation_summary.json"), 'w') as f:
            json.dump(summary, f, indent=2)
            
        # Generate an HTML report
        self._generate_html_report(summary, dfs)
    
    def _generate_html_report(self, summary: Dict[str, Any], dfs: Dict[str, pd.DataFrame]):
        """
        Generate an HTML report with evaluation results.
        
        Args:
            summary: Summary metrics dictionary
            dfs: Dictionary of dataframes with results
        """
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>LLM Response Evaluation Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                }}
                th {{
                    background-color: #f2f2f2;
                    text-align: left;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .summary-card {{
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    padding: 15px;
                    margin-bottom: 20px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                .visualization {{
                    margin: 30px 0;
                    text-align: center;
                }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .metric-card {{
                    background-color: #fff;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                }}
                .metric-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin: 10px 0;
                }}
                .metric-title {{
                    font-size: 14px;
                    color: #7f8c8d;
                }}
                .rag-comparison {{
                    display: flex;
                    justify-content: space-between;
                    background-color: #fff;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .rag-column {{
                    flex: 1;
                    padding: 0 10px;
                }}
                .highlight {{
                    color: #27ae60;
                    font-weight: bold;
                }}
                .lowlight {{
                    color: #e74c3c;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <h1>LLM Response Evaluation Report</h1>
            <p>Generated on: {summary['date']}</p>
            
            <div class="summary-card">
                <h2>Evaluation Summary</h2>
                <p>
                    <strong>General Enquiries Model:</strong> {summary['general_model']}<br>
                    <strong>Study Support Model:</strong> {summary['study_model']}
                </p>
            </div>
        """
        
        # Add sections for each query type
        for query_type in dfs.keys():
            metrics = summary["metrics"][query_type]
            
            html_content += f"""
            <h2>{query_type.capitalize()} Queries Evaluation</h2>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">Queries Evaluated</div>
                    <div class="metric-value">{metrics['query_count']}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Average Response Time</div>
                    <div class="metric-value">{metrics['avg_response_time']}s</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Average Accuracy</div>
                    <div class="metric-value">{metrics['avg_accuracy']}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Average Relevance</div>
                    <div class="metric-value">{metrics['avg_relevance']}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Average Completeness</div>
                    <div class="metric-value">{metrics['avg_completeness']}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Average Coherence</div>
                    <div class="metric-value">{metrics['avg_coherence']}</div>
                </div>
            </div>
            """
            
            # Add RAG comparison if available
            if "rag_comparison" in metrics:
                rag_comp = metrics["rag_comparison"]
                accuracy_diff = rag_comp["rag_accuracy"] - rag_comp["no_rag_accuracy"]
                time_diff = rag_comp["rag_response_time"] - rag_comp["no_rag_response_time"]
                
                # Determine which is better for highlighting
                rag_acc_class = "highlight" if accuracy_diff > 0 else "lowlight"
                no_rag_acc_class = "highlight" if accuracy_diff < 0 else "lowlight"
                rag_time_class = "lowlight" if time_diff > 0 else "highlight"
                no_rag_time_class = "lowlight" if time_diff < 0 else "highlight"
                
                html_content += f"""
                <h3>RAG vs. No-RAG Comparison</h3>
                
                <div class="rag-comparison">
                    <div class="rag-column">
                        <h4>With RAG</h4>
                        <p>
                            <strong>Accuracy:</strong> <span class="{rag_acc_class}">{rag_comp['rag_accuracy']}</span><br>
                            <strong>Response Time:</strong> <span class="{rag_time_class}">{rag_comp['rag_response_time']}s</span>
                        </p>
                    </div>
                    <div class="rag-column">
                        <h4>Without RAG</h4>
                        <p>
                            <strong>Accuracy:</strong> <span class="{no_rag_acc_class}">{rag_comp['no_rag_accuracy']}</span><br>
                            <strong>Response Time:</strong> <span class="{no_rag_time_class}">{rag_comp['no_rag_response_time']}s</span>
                        </p>
                    </div>
                    <div class="rag-column">
                        <h4>Difference</h4>
                        <p>
                            <strong>Accuracy Difference:</strong> {accuracy_diff:.4f}<br>
                            <strong>Response Time Difference:</strong> {time_diff:.4f}s
                        </p>
                    </div>
                </div>
                """
            
            # Add visualizations
            html_content += f"""
            <div class="visualization">
                <h3>Visualizations</h3>
                <img src="{query_type}_visualizations.png" alt="{query_type} Visualizations" style="max-width:100%;">
            </div>
            """
            
            # Add sample queries and responses
            html_content += f"""
            <h3>Sample Queries and Responses</h3>
            <table>
                <tr>
                    <th>Query</th>
                    <th>Response</th>
                    <th>Response Time</th>
                    <th>Accuracy</th>
                    <th>Evaluation Comment</th>
                </tr>
            """
            
            # Add a few sample results
            sample_size = min(5, len(dfs[query_type]))
            samples = dfs[query_type].sample(sample_size) if sample_size > 0 else dfs[query_type]
            
            for _, row in samples.iterrows():
                # Truncate response for readability
                response = row['response']
                if len(response) > 300:
                    response = response[:300] + "..."
                
                html_content += f"""
                <tr>
                    <td>{row['query_text']}</td>
                    <td>{response}</td>
                    <td>{row['response_time']:.4f}s</td>
                    <td>{row['accuracy']:.4f}</td>
                    <td>{row['evaluation_comment']}</td>
                </tr>
                """
            
            html_content += "</table>"
        
        # Close the HTML document
        html_content += """
            <div class="summary-card">
                <h2>Conclusion</h2>
                <p>
                    This report presents a comprehensive evaluation of the LLM responses for both general enquiries and study support queries.
                    The metrics provide insights into the performance, accuracy, and efficiency of the models used in the chatbot system.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Save the HTML report
        with open(os.path.join(self.output_dir, "evaluation_report.html"), 'w') as f:
            f.write(html_content)


def main():
    parser = argparse.ArgumentParser(description="Evaluate LLM responses for the AI chatbot")
    parser.add_argument("--iterations", type=int, default=DEFAULT_TEST_ITERATIONS,
                        help=f"Number of test iterations to run (default: {DEFAULT_TEST_ITERATIONS})")
    parser.add_argument("--output-dir", type=str, default=DEFAULT_OUTPUT_DIR,
                        help=f"Directory to save evaluation results (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--disable-wandb", action="store_true",
                        help="Disable W&B tracking during evaluation")
    args = parser.parse_args()
    
    # Load retriever for RAG
    try:
        # Get the data curator service to access the retriever
        base_dir = "usiu-knowledge-base"
        vector_store_dir = "vector_services/usiu_vector_db"
        curator = DataCurator(knowledge_base_dir=base_dir, persist_directory=vector_store_dir)
        vector_store = curator.load_vectorstore()
        retriever = curator.get_retriever()
        print("Successfully loaded vector store retriever for RAG")
    except Exception as e:
        print(f"Error loading retriever: {e}")
        print("Continuing evaluation without RAG capabilities")
        retriever = None
    
    # Create and run the evaluator
    evaluator = LLMEvaluator(
        general_model=GPT4O_MODEL,
        study_model=CLAUDE_MODEL,
        retriever=retriever,
        output_dir=args.output_dir,
        wandb_tracking=not args.disable_wandb
    )
    
    # Run the evaluation
    evaluator.run_evaluation(iterations=args.iterations)


if __name__ == "__main__":
    main()