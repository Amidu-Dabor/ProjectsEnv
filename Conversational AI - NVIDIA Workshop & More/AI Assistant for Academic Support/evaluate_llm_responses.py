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

# Test queries matching Chapter 5 complexity levels
TEST_QUERIES = {
    "general": {
        "simple": [
            {"query": "What time does the library close?", "expected_elements": ["library hours", "closing time"], "category": "campus"},
            {"query": "List available computer science programs", "expected_elements": ["programs", "computer science", "degrees"], "category": "academics"},
            {"query": "What is the main campus address?", "expected_elements": ["address", "location"], "category": "contact"}
        ],
        "medium": [
            {"query": "What are the admission requirements for international students?", "expected_elements": ["requirements", "international", "documents", "qualifications"], "category": "admissions"},
            {"query": "Tell me about financial aid options and application deadlines", "expected_elements": ["financial aid", "scholarships", "deadlines", "application process"], "category": "financial"},
            {"query": "What student support services are available on campus?", "expected_elements": ["support services", "counseling", "academic support", "health"], "category": "student_support"}
        ],
        "complex": [
            {"query": "Compare undergraduate vs graduate tuition fees and available payment plans for international students", "expected_elements": ["tuition", "undergraduate", "graduate", "payment plans", "international"], "category": "financial"},
            {"query": "Explain the process for transferring credits from another university and how it affects graduation requirements", "expected_elements": ["transfer credits", "process", "requirements", "graduation", "evaluation"], "category": "academics"},
            {"query": "What are all the steps involved in applying for on-campus housing, including deadlines, costs, and meal plan options?", "expected_elements": ["housing application", "deadlines", "costs", "meal plans", "process"], "category": "campus"}
        ]
    },
    "study": {
        "simple": [
            {"query": "Help me understand recursion in programming", "expected_elements": ["recursion", "base case", "recursive call", "examples"], "category": "programming"},
            {"query": "Explain the Pythagorean theorem", "expected_elements": ["a² + b² = c²", "right triangle", "hypotenuse"], "category": "math"},
            {"query": "What is photosynthesis?", "expected_elements": ["light", "chlorophyll", "glucose", "oxygen"], "category": "science"}
        ],
        "medium": [
            {"query": "Debug this Python code: def factorial(n): return n * factorial(n-1)", "expected_elements": ["base case missing", "if n <= 1: return 1", "recursion", "fix"], "category": "programming"},
            {"query": "Help me write an introduction paragraph for an essay on climate change", "expected_elements": ["hook", "thesis statement", "overview", "structure"], "category": "writing"},
            {"query": "Explain the difference between mean, median, and mode with examples", "expected_elements": ["average", "middle value", "most frequent", "examples"], "category": "math"}
        ],
        "complex": [
            {"query": "Convert this recursive Fibonacci function to an iterative one in C++ and analyze time complexity", "expected_elements": ["iterative implementation", "C++ syntax", "O(n) time", "O(1) space"], "category": "programming"},
            {"query": "Design a research methodology for studying the impact of social media on teenage mental health", "expected_elements": ["research design", "data collection", "ethical considerations", "analysis methods"], "category": "research"},
            {"query": "Create a comprehensive study plan for preparing for calculus finals covering derivatives, integrals, and applications", "expected_elements": ["study schedule", "topics breakdown", "practice problems", "review strategy"], "category": "math"}
        ]
    }
}

class EnhancedLLMEvaluator:
    """Enhanced evaluator matching Chapter 5 requirements exactly."""
    
    def __init__(
        self, 
        general_model: str = CLAUDE_MODEL, 
        study_model: str = CLAUDE_MODEL,
        retriever = None,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        wandb_tracking: bool = True
    ):
        self.general_model = general_model
        self.study_model = study_model
        self.retriever = retriever
        self.output_dir = output_dir
        self.wandb_tracking = wandb_tracking
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize clients
        self.openai_client = openai.OpenAI()
        self.claude_client = anthropic.Anthropic()
        
        # Initialize data service
        self.data_service = DataService(retriever=retriever)
        self.general_prompt, self.study_prompt = self.data_service.prompts_service.get_prompt()
        
        # Initialize W&B with Chapter 5 config
        if wandb_tracking:
            config = {
                "general_model": general_model,
                "study_model": study_model,
                "evaluation_type": "chapter5_metrics",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "test_categories": ["simple", "medium", "complex"],
                "metrics_tracked": ["response_time", "accuracy", "tokens", "rag_effectiveness"]
            }
            self.wandb_tracker = register_wandb_service(config)
            if not self.wandb_tracker:
                print("Warning: Could not initialize W&B tracking.")
                self.wandb_tracking = False
        
        # Results storage matching Chapter 5 structure
        self.results = {
            "general": [],
            "study": []
        }
        
        # Chapter 5 specific metrics
        self.chapter5_metrics = {
            "overall": {"response_time": [], "accuracy": [], "tokens": []},
            "by_complexity": {
                "simple": {"response_time": [], "accuracy": [], "tokens": []},
                "medium": {"response_time": [], "accuracy": [], "tokens": []},
                "complex": {"response_time": [], "accuracy": [], "tokens": []}
            },
            "rag_comparison": {
                "with_rag": {"response_time": [], "accuracy": [], "tokens": []},
                "without_rag": {"response_time": [], "accuracy": [], "tokens": []}
            }
        }
    
    def _generate_response(
        self, 
        query: str, 
        model_type: str, 
        with_rag: bool = True
    ) -> Tuple[str, float, Dict[str, Any]]:
        """Generate response with detailed metrics tracking."""
        start_time = time.time()
        response_text = ""
        metadata = {
            "token_count": 0,
            "retrieved_docs": [],
            "error": None
        }
        
        try:
            if model_type == "general":
                # Use OpenAI for general queries
                messages = [{"role": "system", "content": self.general_prompt}]
                
                # Add RAG context if enabled
                if with_rag and self.retriever:
                    try:
                        docs = self.retriever.invoke(query)
                        if docs:
                            metadata["retrieved_docs"] = [doc.page_content[:200] + "..." for doc in docs]
                            context_text = "\n\n".join([doc.page_content for doc in docs])
                            messages.insert(1, {
                                "role": "system",
                                "content": f"Additional Context:\n{context_text}"
                            })
                    except Exception as e:
                        print(f"RAG retrieval error: {e}")
                        metadata["error"] = f"RAG error: {str(e)}"
                
                messages.append({"role": "user", "content": query})
                
                # Generate response
                response = self.openai_client.chat.completions.create(
                    model=self.general_model,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
                
                response_text = response.choices[0].message.content
                metadata["token_count"] = response.usage.total_tokens
                
            elif model_type == "study":
                # Use Claude for study queries
                response = self.claude_client.messages.create(
                    model=self.study_model,
                    system=self.study_prompt,
                    messages=[{"role": "user", "content": query}],
                    max_tokens=1000,
                    temperature=0.7
                )
                
                response_text = response.content[0].text
                # Estimate tokens for Claude
                metadata["token_count"] = int(len(query.split()) + len(response_text.split()) * 1.3)
        
        except Exception as e:
            print(f"Error generating response: {e}")
            response_text = f"Error: {str(e)}"
            metadata["error"] = str(e)
        
        response_time = time.time() - start_time
        return response_text, response_time, metadata
    
    def _evaluate_response_quality(
        self, 
        query_data: Dict[str, Any], 
        response: str
    ) -> float:
        """Evaluate response quality based on expected elements."""
        expected_elements = query_data.get("expected_elements", [])
        if not expected_elements:
            return 0.7  # Default score
        
        # Count how many expected elements are present
        elements_found = 0
        for element in expected_elements:
            if element.lower() in response.lower():
                elements_found += 1
        
        # Calculate base accuracy
        accuracy = elements_found / len(expected_elements)
        
        # Adjust for response quality indicators
        if len(response) < 50:  # Too short
            accuracy *= 0.5
        elif len(response) > 2000:  # Very comprehensive
            accuracy = min(1.0, accuracy * 1.1)
        
        # Check for errors
        if "error" in response.lower() or "unable to" in response.lower():
            accuracy *= 0.7
        
        return min(1.0, max(0.0, accuracy))
    
    def run_chapter5_evaluation(self, iterations_per_complexity: int = 5):
        """Run evaluation matching Chapter 5 test structure."""
        print(f"\nStarting Chapter 5 LLM Evaluation")
        print(f"Models: General={self.general_model}, Study={self.study_model}")
        print(f"Iterations per complexity level: {iterations_per_complexity}")
        print("="*60)
        
        # Test general queries
        print("\n📚 Testing General Enquiries...")
        for complexity in ["simple", "medium", "complex"]:
            print(f"\n  Testing {complexity.upper()} queries:")
            queries = TEST_QUERIES["general"][complexity]
            
            for i in range(min(iterations_per_complexity, len(queries))):
                query_data = queries[i % len(queries)]
                query_text = query_data["query"]
                print(f"    - {query_text[:60]}...")
                
                # Test with RAG (if available)
                if self.retriever:
                    response, time_taken, metadata = self._generate_response(
                        query_text, "general", with_rag=True
                    )
                    accuracy = self._evaluate_response_quality(query_data, response)
                    
                    # Store results
                    result = {
                        "query_id": f"GE{i+1}",
                        "query_text": query_text,
                        "query_complexity": complexity,
                        "query_category": query_data["category"],
                        "response_time": round(time_taken, 4),
                        "accuracy": round(accuracy, 4),
                        "tokens": metadata["token_count"],
                        "with_rag": True,
                        "error": metadata.get("error")
                    }
                    self.results["general"].append(result)
                    
                    # Update Chapter 5 metrics
                    self.chapter5_metrics["overall"]["response_time"].append(time_taken)
                    self.chapter5_metrics["overall"]["accuracy"].append(accuracy)
                    self.chapter5_metrics["overall"]["tokens"].append(metadata["token_count"])
                    
                    self.chapter5_metrics["by_complexity"][complexity]["response_time"].append(time_taken)
                    self.chapter5_metrics["by_complexity"][complexity]["accuracy"].append(accuracy)
                    self.chapter5_metrics["by_complexity"][complexity]["tokens"].append(metadata["token_count"])
                    
                    self.chapter5_metrics["rag_comparison"]["with_rag"]["response_time"].append(time_taken)
                    self.chapter5_metrics["rag_comparison"]["with_rag"]["accuracy"].append(accuracy)
                    self.chapter5_metrics["rag_comparison"]["with_rag"]["tokens"].append(metadata["token_count"])
                    
                    # Log to W&B
                    if self.wandb_tracking and self.wandb_tracker:
                        self.wandb_tracker.log_conversation(
                            session_id=f"eval_general_{complexity}_{i}",
                            user_id="evaluator",
                            chat_type="general",
                            query=query_text,
                            response=response,
                            context_used=metadata["retrieved_docs"],
                            tokens=metadata["token_count"],
                            response_time=time_taken,
                            feedback=None,
                            query_complexity=complexity,
                            accuracy_score=accuracy
                        )
                
                # Test without RAG
                response, time_taken, metadata = self._generate_response(
                    query_text, "general", with_rag=False
                )
                accuracy = self._evaluate_response_quality(query_data, response)
                
                # Store results
                result = {
                    "query_id": f"GE{i+1}_no_rag",
                    "query_text": query_text,
                    "query_complexity": complexity,
                    "query_category": query_data["category"],
                    "response_time": round(time_taken, 4),
                    "accuracy": round(accuracy, 4),
                    "tokens": metadata["token_count"],
                    "with_rag": False,
                    "error": metadata.get("error")
                }
                self.results["general"].append(result)
                
                self.chapter5_metrics["rag_comparison"]["without_rag"]["response_time"].append(time_taken)
                self.chapter5_metrics["rag_comparison"]["without_rag"]["accuracy"].append(accuracy)
                self.chapter5_metrics["rag_comparison"]["without_rag"]["tokens"].append(metadata["token_count"])
        
        # Test study support queries
        print("\n\n🎓 Testing Study Support...")
        for complexity in ["simple", "medium", "complex"]:
            print(f"\n  Testing {complexity.upper()} queries:")
            queries = TEST_QUERIES["study"][complexity]
            
            for i in range(min(iterations_per_complexity, len(queries))):
                query_data = queries[i % len(queries)]
                query_text = query_data["query"]
                print(f"    - {query_text[:60]}...")
                
                response, time_taken, metadata = self._generate_response(
                    query_text, "study", with_rag=False
                )
                accuracy = self._evaluate_response_quality(query_data, response)
                
                # Store results
                result = {
                    "query_id": f"SS{i+1}",
                    "query_text": query_text,
                    "query_complexity": complexity,
                    "query_category": query_data["category"],
                    "response_time": round(time_taken, 4),
                    "accuracy": round(accuracy, 4),
                    "tokens": metadata["token_count"],
                    "with_rag": False,
                    "error": metadata.get("error")
                }
                self.results["study"].append(result)
                
                # Update Chapter 5 metrics
                self.chapter5_metrics["overall"]["response_time"].append(time_taken)
                self.chapter5_metrics["overall"]["accuracy"].append(accuracy)
                self.chapter5_metrics["overall"]["tokens"].append(metadata["token_count"])
                
                self.chapter5_metrics["by_complexity"][complexity]["response_time"].append(time_taken)
                self.chapter5_metrics["by_complexity"][complexity]["accuracy"].append(accuracy)
                self.chapter5_metrics["by_complexity"][complexity]["tokens"].append(metadata["token_count"])
                
                # Log to W&B
                if self.wandb_tracking and self.wandb_tracker:
                    self.wandb_tracker.log_conversation(
                        session_id=f"eval_study_{complexity}_{i}",
                        user_id="evaluator",
                        chat_type="study_support",
                        query=query_text,
                        response=response,
                        context_used=[],
                        tokens=metadata["token_count"],
                        response_time=time_taken,
                        feedback=None,
                        query_complexity=complexity,
                        accuracy_score=accuracy
                    )
        
        # Generate Chapter 5 specific outputs
        self._generate_chapter5_report()
        self._create_chapter5_visualizations()
        
        print("\n✅ Evaluation Complete!")
        print(f"Results saved to: {self.output_dir}")
    
    def _generate_chapter5_report(self):
        """Generate report matching Chapter 5 format."""
        
        # Calculate overall metrics
        overall_metrics = {
            "avg_response_time": np.mean(self.chapter5_metrics["overall"]["response_time"]),
            "avg_accuracy": np.mean(self.chapter5_metrics["overall"]["accuracy"]),
            "avg_tokens": np.mean(self.chapter5_metrics["overall"]["tokens"]),
            "total_queries": len(self.chapter5_metrics["overall"]["response_time"])
        }
        
        # Calculate metrics by complexity
        complexity_metrics = {}
        for complexity in ["simple", "medium", "complex"]:
            if self.chapter5_metrics["by_complexity"][complexity]["response_time"]:
                complexity_metrics[complexity] = {
                    "avg_response_time": np.mean(self.chapter5_metrics["by_complexity"][complexity]["response_time"]),
                    "avg_accuracy": np.mean(self.chapter5_metrics["by_complexity"][complexity]["accuracy"]),
                    "avg_tokens": np.mean(self.chapter5_metrics["by_complexity"][complexity]["tokens"]),
                    "count": len(self.chapter5_metrics["by_complexity"][complexity]["response_time"])
                }
        
        # Calculate RAG comparison
        rag_metrics = {}
        for rag_type in ["with_rag", "without_rag"]:
            if self.chapter5_metrics["rag_comparison"][rag_type]["response_time"]:
                rag_metrics[rag_type] = {
                    "avg_response_time": np.mean(self.chapter5_metrics["rag_comparison"][rag_type]["response_time"]),
                    "avg_accuracy": np.mean(self.chapter5_metrics["rag_comparison"][rag_type]["accuracy"]),
                    "avg_tokens": np.mean(self.chapter5_metrics["rag_comparison"][rag_type]["tokens"]),
                    "count": len(self.chapter5_metrics["rag_comparison"][rag_type]["response_time"])
                }
        
        # Create summary report
        report = {
            "evaluation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "models": {
                "general": self.general_model,
                "study": self.study_model
            },
            "overall_performance": overall_metrics,
            "performance_by_complexity": complexity_metrics,
            "rag_comparison": rag_metrics,
            "chapter5_targets": {
                "target_avg_response_time": 3.26,
                "target_accuracy": 0.935,
                "target_avg_tokens": 783
            },
            "target_achievement": {
                "response_time_achieved": overall_metrics["avg_response_time"] <= 3.26,
                "accuracy_achieved": overall_metrics["avg_accuracy"] >= 0.935,
                "token_efficiency_achieved": overall_metrics["avg_tokens"] <= 783
            }
        }
        
        # Save report
        with open(os.path.join(self.output_dir, "chapter5_evaluation_summary.json"), 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save detailed results as CSV
        for query_type in ["general", "study"]:
            if self.results[query_type]:
                df = pd.DataFrame(self.results[query_type])
                df.to_csv(os.path.join(self.output_dir, f"chapter5_{query_type}_results.csv"), index=False)
        
        # Print summary
        print("\n" + "="*60)
        print("CHAPTER 5 EVALUATION SUMMARY")
        print("="*60)
        print(f"Overall Performance:")
        print(f"  - Average Response Time: {overall_metrics['avg_response_time']:.4f}s (Target: 3.26s)")
        print(f"  - Average Accuracy: {overall_metrics['avg_accuracy']*100:.1f}% (Target: 93.5%)")
        print(f"  - Average Tokens: {overall_metrics['avg_tokens']:.0f} (Target: 783)")
        
        if rag_metrics.get("with_rag") and rag_metrics.get("without_rag"):
            print(f"\nRAG Comparison:")
            print(f"  With RAG:")
            print(f"    - Response Time: {rag_metrics['with_rag']['avg_response_time']:.4f}s")
            print(f"    - Accuracy: {rag_metrics['with_rag']['avg_accuracy']*100:.1f}%")
            print(f"  Without RAG:")
            print(f"    - Response Time: {rag_metrics['without_rag']['avg_response_time']:.4f}s")
            print(f"    - Accuracy: {rag_metrics['without_rag']['avg_accuracy']*100:.1f}%")
            print(f"  RAG Improvement: {(rag_metrics['with_rag']['avg_accuracy'] - rag_metrics['without_rag']['avg_accuracy'])*100:.1f}%")
    
    def _create_chapter5_visualizations(self):
        """Create visualizations matching Chapter 5 figures."""
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # Create figure with subplots matching Chapter 5
        fig = plt.figure(figsize=(16, 12))
        
        # 1. Response Time by Complexity (Figure 5.1 equivalent)
        ax1 = plt.subplot(2, 3, 1)
        complexity_data = []
        for complexity in ["simple", "medium", "complex"]:
            times = self.chapter5_metrics["by_complexity"][complexity]["response_time"]
            if times:
                complexity_data.append({
                    "Complexity": complexity.capitalize(),
                    "Response Time": times
                })
        
        if complexity_data:
            data_list = []
            for item in complexity_data:
                for time_val in item["Response Time"]:
                    data_list.append({"Complexity": item["Complexity"], "Response Time (s)": time_val})
            df = pd.DataFrame(data_list)
            sns.boxplot(x="Complexity", y="Response Time (s)", data=df, ax=ax1)
            ax1.axhline(y=3.26, color='r', linestyle='--', label='Target (3.26s)')
            ax1.set_title("Response Time by Query Complexity")
            ax1.legend()
        
        # 2. Accuracy by Complexity (Figure 5.2 equivalent)
        ax2 = plt.subplot(2, 3, 2)
        accuracy_by_complexity = []
        for complexity in ["simple", "medium", "complex"]:
            acc_values = self.chapter5_metrics["by_complexity"][complexity]["accuracy"]
            if acc_values:
                accuracy_by_complexity.append({
                    "Complexity": complexity.capitalize(),
                    "Accuracy": np.mean(acc_values) * 100
                })
        
        if accuracy_by_complexity:
            df = pd.DataFrame(accuracy_by_complexity)
            sns.barplot(x="Complexity", y="Accuracy", data=df, ax=ax2)
            ax2.axhline(y=93.5, color='r', linestyle='--', label='Target (93.5%)')
            ax2.set_ylim(0, 105)
            ax2.set_ylabel("Accuracy (%)")
            ax2.set_title("Accuracy by Query Complexity")
            ax2.legend()
        
        # 3. RAG Comparison (Enhanced)
        ax3 = plt.subplot(2, 3, 3)
        rag_comparison = []
        for rag_type, label in [("with_rag", "With RAG"), ("without_rag", "Without RAG")]:
            if self.chapter5_metrics["rag_comparison"][rag_type]["accuracy"]:
                rag_comparison.append({
                    "Configuration": label,
                    "Accuracy": np.mean(self.chapter5_metrics["rag_comparison"][rag_type]["accuracy"]) * 100,
                    "Response Time": np.mean(self.chapter5_metrics["rag_comparison"][rag_type]["response_time"])
                })
        
        if rag_comparison:
            df = pd.DataFrame(rag_comparison)
            x = np.arange(len(df))
            width = 0.35
            
            ax3_twin = ax3.twinx()
            bars1 = ax3.bar(x - width/2, df["Accuracy"], width, label='Accuracy (%)', color='skyblue')
            bars2 = ax3_twin.bar(x + width/2, df["Response Time"], width, label='Response Time (s)', color='lightcoral')
            
            ax3.set_xlabel('Configuration')
            ax3.set_ylabel('Accuracy (%)', color='skyblue')
            ax3_twin.set_ylabel('Response Time (s)', color='lightcoral')
            ax3.set_title('RAG vs No-RAG Comparison')
            ax3.set_xticks(x)
            ax3.set_xticklabels(df["Configuration"])
            ax3.tick_params(axis='y', labelcolor='skyblue')
            ax3_twin.tick_params(axis='y', labelcolor='lightcoral')
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}%', ha='center', va='bottom')
            
            for bar in bars2:
                height = bar.get_height()
                ax3_twin.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.2f}s', ha='center', va='bottom')
        
        # 4. Token Usage Distribution
        ax4 = plt.subplot(2, 3, 4)
        token_data = self.chapter5_metrics["overall"]["tokens"]
        if token_data:
            sns.histplot(token_data, kde=True, ax=ax4)
            ax4.axvline(x=783, color='r', linestyle='--', label='Target (783)')
            ax4.set_xlabel("Token Count")
            ax4.set_ylabel("Frequency")
            ax4.set_title("Token Usage Distribution")
            ax4.legend()
        
        # 5. Performance Over Time (simulated)
        ax5 = plt.subplot(2, 3, 5)
        if self.chapter5_metrics["overall"]["accuracy"]:
            x = range(len(self.chapter5_metrics["overall"]["accuracy"]))
            accuracy_values = [acc * 100 for acc in self.chapter5_metrics["overall"]["accuracy"]]
            ax5.plot(x, accuracy_values, marker='o', linestyle='-', alpha=0.7)
            ax5.axhline(y=93.5, color='r', linestyle='--', label='Target (93.5%)')
            ax5.set_xlabel("Query Number")
            ax5.set_ylabel("Accuracy (%)")
            ax5.set_title("Accuracy Trend Over Evaluation")
            ax5.set_ylim(0, 105)
            ax5.legend()
        
        # 6. Overall Performance Summary
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        # Calculate summary statistics
        overall_stats = {
            "Metric": ["Avg Response Time", "Avg Accuracy", "Avg Tokens", "Error Rate"],
            "Value": [
                f"{np.mean(self.chapter5_metrics['overall']['response_time']):.3f}s",
                f"{np.mean(self.chapter5_metrics['overall']['accuracy'])*100:.1f}%",
                f"{np.mean(self.chapter5_metrics['overall']['tokens']):.0f}",
                f"{sum(1 for r in self.results['general'] + self.results['study'] if r.get('error')) / len(self.results['general'] + self.results['study']) * 100:.1f}%"
            ],
            "Target": ["3.26s", "93.5%", "783", "<1%"],
            "Status": ["✅" if np.mean(self.chapter5_metrics['overall']['response_time']) <= 3.26 else "❌",
                      "✅" if np.mean(self.chapter5_metrics['overall']['accuracy']) >= 0.935 else "❌",
                      "✅" if np.mean(self.chapter5_metrics['overall']['tokens']) <= 783 else "❌",
                      "✅" if sum(1 for r in self.results['general'] + self.results['study'] if r.get('error')) / max(len(self.results['general'] + self.results['study']), 1) < 0.01 else "❌"]
       }
       
        # Create table
        table_data = []
        for i in range(len(overall_stats["Metric"])):
            table_data.append([
                overall_stats["Metric"][i],
                overall_stats["Value"][i],
                overall_stats["Target"][i],
                overall_stats["Status"][i]
            ])
       
        table = ax6.table(cellText=table_data,
                            colLabels=["Metric", "Actual", "Target", "Status"],
                            cellLoc='center',
                            loc='center',
                            colWidths=[0.3, 0.25, 0.25, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.8)
        
        # Style the table
        for i in range(len(table_data) + 1):
            for j in range(4):
                cell = table[(i, j)]
                if i == 0:  # Header row
                    cell.set_facecolor('#1F2E8C')
                    cell.set_text_props(weight='bold', color='white')
                else:
                    if j == 3:  # Status column
                        if table_data[i-1][3] == "✅":
                            cell.set_facecolor('#E8F5E9')
                        else:
                            cell.set_facecolor('#FFEBEE')
        
        ax6.set_title("Overall Performance Summary", pad=20, fontsize=12, weight='bold')
        
        plt.suptitle("Chapter 5: LLM Evaluation Results", fontsize=16, y=0.98)
        plt.tight_layout()
        
        # Save figure
        plt.savefig(os.path.join(self.output_dir, "chapter5_evaluation_results.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create additional specialized plots
        self._create_rag_effectiveness_plot()
        self._create_complexity_comparison_plot()
        
        # Log final visualization to W&B
        if self.wandb_tracking and self.wandb_tracker:
            try:
                self.wandb_tracker.run.log({
                    "chapter5_evaluation_results": wandb.Image(
                        os.path.join(self.output_dir, "chapter5_evaluation_results.png")
                    )
                })
                
                # Create and log summary metrics
                self.wandb_tracker.create_summary_plots()
                
            except Exception as e:
                print(f"Error logging to W&B: {e}")
    
    def _create_rag_effectiveness_plot(self):
        """Create a detailed RAG effectiveness visualization."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # RAG Impact on Accuracy
        rag_data = []
        for result in self.results["general"]:
            if "with_rag" in result:
                rag_data.append({
                    "RAG": "With RAG" if result["with_rag"] else "Without RAG",
                    "Accuracy": result["accuracy"] * 100,
                    "Complexity": result["query_complexity"]
                })
        
        if rag_data:
            df = pd.DataFrame(rag_data)
            
            # Box plot by RAG status
            sns.boxplot(x="RAG", y="Accuracy", data=df, ax=ax1)
            ax1.set_ylabel("Accuracy (%)")
            ax1.set_title("RAG Impact on Accuracy")
            ax1.set_ylim(0, 105)
            
            # Grouped bar plot by complexity
            pivot_df = df.groupby(['Complexity', 'RAG'])['Accuracy'].mean().reset_index()
            sns.barplot(x="Complexity", y="Accuracy", hue="RAG", data=pivot_df, ax=ax2)
            ax2.set_ylabel("Average Accuracy (%)")
            ax2.set_title("RAG Effectiveness by Query Complexity")
            ax2.set_ylim(0, 105)
        
        plt.suptitle("RAG (Retrieval-Augmented Generation) Effectiveness Analysis", fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "rag_effectiveness_analysis.png"), dpi=300, bbox_inches='tight')
        plt.close()
   
    def _create_complexity_comparison_plot(self):
        """Create a comprehensive complexity comparison visualization."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Prepare data
        all_results = self.results["general"] + self.results["study"]
        df = pd.DataFrame(all_results)
        
        # 1. Response Time Heatmap
        ax1 = axes[0, 0]
        pivot_time = df.pivot_table(
            values='response_time', 
            index='query_complexity', 
            columns='query_category', 
            aggfunc='mean'
        )
        if not pivot_time.empty:
            sns.heatmap(pivot_time, annot=True, fmt='.3f', cmap='YlOrRd', ax=ax1)
            ax1.set_title("Avg Response Time by Complexity & Category")
            ax1.set_xlabel("Category")
            ax1.set_ylabel("Complexity")
        
        # 2. Accuracy Heatmap
        ax2 = axes[0, 1]
        pivot_acc = df.pivot_table(
            values='accuracy', 
            index='query_complexity', 
            columns='query_category', 
            aggfunc='mean'
        )
        if not pivot_acc.empty:
            sns.heatmap(pivot_acc * 100, annot=True, fmt='.1f', cmap='RdYlGn', ax=ax2)
            ax2.set_title("Avg Accuracy (%) by Complexity & Category")
            ax2.set_xlabel("Category")
            ax2.set_ylabel("Complexity")
        
        # 3. Token Usage by Complexity
        ax3 = axes[1, 0]
        sns.violinplot(x='query_complexity', y='tokens', data=df, ax=ax3)
        ax3.axhline(y=783, color='r', linestyle='--', alpha=0.7, label='Target (783)')
        ax3.set_title("Token Distribution by Complexity")
        ax3.set_xlabel("Complexity")
        ax3.set_ylabel("Tokens Used")
        ax3.legend()
        
        # 4. Performance Radar Chart (if possible)
        ax4 = axes[1, 1]
        complexity_levels = ['simple', 'medium', 'complex']
        metrics = ['Accuracy', 'Speed', 'Efficiency']
        
        radar_data = []
        for complexity in complexity_levels:
            complexity_df = df[df['query_complexity'] == complexity]
            if not complexity_df.empty:
                accuracy = complexity_df['accuracy'].mean()
                speed = 1 - (complexity_df['response_time'].mean() / df['response_time'].max())
                efficiency = 1 - (complexity_df['tokens'].mean() / df['tokens'].max())
                radar_data.append([accuracy, speed, efficiency])
        
        if radar_data:
            angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
            angles += angles[:1]
            
            for i, (complexity, data) in enumerate(zip(complexity_levels, radar_data)):
                values = data + data[:1]
                ax4.plot(angles, values, 'o-', linewidth=2, label=complexity.capitalize())
                ax4.fill(angles, values, alpha=0.25)
            
            ax4.set_theta_offset(np.pi / 2)
            ax4.set_theta_direction(-1)
            ax4.set_xticks(angles[:-1])
            ax4.set_xticklabels(metrics)
            ax4.set_ylim(0, 1)
            ax4.set_title("Performance Profile by Complexity")
            ax4.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
            ax4.grid(True)
        
        plt.suptitle("Complexity-Based Performance Analysis", fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "complexity_performance_analysis.png"), dpi=300, bbox_inches='tight')
        plt.close()


def main():
    parser = argparse.ArgumentParser(description="Chapter 5 LLM Evaluation")
    parser.add_argument("--iterations", type=int, default=5,
                        help="Number of iterations per complexity level (default: 5)")
    parser.add_argument("--output-dir", type=str, default=DEFAULT_OUTPUT_DIR,
                        help=f"Directory to save evaluation results (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--disable-wandb", action="store_true",
                        help="Disable W&B tracking during evaluation")
    parser.add_argument("--disable-rag", action="store_true",
                        help="Disable RAG for testing")
    args = parser.parse_args()
    
    # Load retriever for RAG
    retriever = None
    if not args.disable_rag:
        try:
            base_dir = "usiu-knowledge-base"
            vector_store_dir = "vector_services/usiu_vector_db"
            curator = DataCurator(knowledge_base_dir=base_dir, persist_directory=vector_store_dir)
            vector_store = curator.load_vectorstore()
            retriever = curator.get_retriever()
            print("✅ Successfully loaded vector store retriever for RAG")
        except Exception as e:
            print(f"⚠️  Error loading retriever: {e}")
            print("Continuing evaluation without RAG capabilities")
    
    # Create and run the evaluator
    evaluator = EnhancedLLMEvaluator(
        general_model=CLAUDE_MODEL,
        study_model=CLAUDE_MODEL,
        retriever=retriever,
        output_dir=args.output_dir,
        wandb_tracking=not args.disable_wandb
    )
    
    # Run Chapter 5 specific evaluation
    evaluator.run_chapter5_evaluation(iterations_per_complexity=args.iterations)
    
    # Generate final HTML report
    generate_html_report(args.output_dir)


def generate_html_report(output_dir: str):
    """Generate a comprehensive HTML report for Chapter 5 results."""
    
    # Load the summary data
    with open(os.path.join(output_dir, "chapter5_evaluation_summary.json"), 'r') as f:
        summary = json.load(f)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chapter 5: LLM Evaluation Results</title>
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .header {{
                background-color: #1F2E8C;
                color: white;
                padding: 30px;
                border-radius: 8px;
                text-align: center;
                margin-bottom: 30px;
            }}
            .summary-card {{
                background-color: white;
                border-radius: 8px;
                padding: 25px;
                margin-bottom: 25px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .metric-card {{
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                border: 1px solid #e9ecef;
            }}
            .metric-value {{
                font-size: 36px;
                font-weight: bold;
                color: #1F2E8C;
                margin: 10px 0;
            }}
            .metric-label {{
                font-size: 14px;
                color: #6c757d;
                text-transform: uppercase;
            }}
            .target {{
                font-size: 12px;
                color: #999;
            }}
            .achieved {{ color: #28a745; }}
            .not-achieved {{ color: #dc3545; }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #dee2e6;
            }}
            th {{
                background-color: #f8f9fa;
                font-weight: 600;
            }}
            .visualization {{
                margin: 30px 0;
                text-align: center;
            }}
            .visualization img {{
                max-width: 100%;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .conclusion {{
                background-color: #e3f2fd;
                border-left: 4px solid #1F2E8C;
                padding: 20px;
                margin: 30px 0;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Chapter 5: LLM Response Evaluation Results</h1>
            <p>Comprehensive evaluation of AI Assistant performance</p>
            <p>{summary['evaluation_date']}</p>
        </div>
        
        <div class="summary-card">
            <h2>Executive Summary</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Average Response Time</div>
                    <div class="metric-value {('achieved' if summary['target_achievement']['response_time_achieved'] else 'not-achieved')}">
                        {summary['overall_performance']['avg_response_time']:.3f}s
                    </div>
                    <div class="target">Target: {summary['chapter5_targets']['target_avg_response_time']}s</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Average Accuracy</div>
                    <div class="metric-value {('achieved' if summary['target_achievement']['accuracy_achieved'] else 'not-achieved')}">
                        {summary['overall_performance']['avg_accuracy']*100:.1f}%
                    </div>
                    <div class="target">Target: {summary['chapter5_targets']['target_accuracy']*100:.1f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Average Tokens</div>
                    <div class="metric-value {('achieved' if summary['target_achievement']['token_efficiency_achieved'] else 'not-achieved')}">
                        {summary['overall_performance']['avg_tokens']:.0f}
                    </div>
                    <div class="target">Target: {summary['chapter5_targets']['target_avg_tokens']}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Total Queries</div>
                    <div class="metric-value">
                        {summary['overall_performance']['total_queries']}
                    </div>
                    <div class="target">Evaluated</div>
                </div>
            </div>
        </div>
        
        <div class="summary-card">
            <h2>Performance by Complexity</h2>
            <table>
                <thead>
                    <tr>
                        <th>Complexity</th>
                        <th>Count</th>
                        <th>Avg Response Time</th>
                        <th>Avg Accuracy</th>
                        <th>Avg Tokens</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add complexity data
    for complexity, metrics in summary.get('performance_by_complexity', {}).items():
        html_content += f"""
                    <tr>
                        <td><strong>{complexity.capitalize()}</strong></td>
                        <td>{metrics['count']}</td>
                        <td>{metrics['avg_response_time']:.3f}s</td>
                        <td>{metrics['avg_accuracy']*100:.1f}%</td>
                        <td>{metrics['avg_tokens']:.0f}</td>
                    </tr>
        """
    
    html_content += """
                </tbody>
            </table>
        </div>
    """
    
    # Add RAG comparison if available
    if summary.get('rag_comparison'):
        html_content += """
        <div class="summary-card">
            <h2>RAG (Retrieval-Augmented Generation) Comparison</h2>
            <table>
                <thead>
                    <tr>
                        <th>Configuration</th>
                        <th>Count</th>
                        <th>Avg Response Time</th>
                        <th>Avg Accuracy</th>
                        <th>Avg Tokens</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for rag_type, metrics in summary['rag_comparison'].items():
            label = "With RAG" if rag_type == "with_rag" else "Without RAG"
            html_content += f"""
                    <tr>
                        <td><strong>{label}</strong></td>
                        <td>{metrics['count']}</td>
                        <td>{metrics['avg_response_time']:.3f}s</td>
                        <td>{metrics['avg_accuracy']*100:.1f}%</td>
                        <td>{metrics['avg_tokens']:.0f}</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </div>
        """
    
    # Add visualizations
    html_content += """
        <div class="summary-card">
            <h2>Performance Visualizations</h2>
            <div class="visualization">
                <h3>Overall Evaluation Results</h3>
                <img src="chapter5_evaluation_results.png" alt="Chapter 5 Evaluation Results">
            </div>
            <div class="visualization">
                <h3>RAG Effectiveness Analysis</h3>
                <img src="rag_effectiveness_analysis.png" alt="RAG Effectiveness Analysis">
            </div>
            <div class="visualization">
                <h3>Complexity-Based Performance</h3>
                <img src="complexity_performance_analysis.png" alt="Complexity Performance Analysis">
            </div>
        </div>
        
        <div class="conclusion">
            <h2>Conclusion</h2>
            <p>
                The evaluation demonstrates that the AI Assistant system has achieved the following:
            </p>
            <ul>
    """
    
    # Add achievement summary
    achievements = []
    if summary['target_achievement']['response_time_achieved']:
        achievements.append(f"✅ Response time target met ({summary['overall_performance']['avg_response_time']:.3f}s vs target {summary['chapter5_targets']['target_avg_response_time']}s)")
    else:
        achievements.append(f"❌ Response time target not met ({summary['overall_performance']['avg_response_time']:.3f}s vs target {summary['chapter5_targets']['target_avg_response_time']}s)")
    
    if summary['target_achievement']['accuracy_achieved']:
        achievements.append(f"✅ Accuracy target met ({summary['overall_performance']['avg_accuracy']*100:.1f}% vs target {summary['chapter5_targets']['target_accuracy']*100:.1f}%)")
    else:
        achievements.append(f"❌ Accuracy target not met ({summary['overall_performance']['avg_accuracy']*100:.1f}% vs target {summary['chapter5_targets']['target_accuracy']*100:.1f}%)")
    
    if summary['target_achievement']['token_efficiency_achieved']:
        achievements.append(f"✅ Token efficiency target met ({summary['overall_performance']['avg_tokens']:.0f} vs target {summary['chapter5_targets']['target_avg_tokens']})")
    else:
        achievements.append(f"❌ Token efficiency target not met ({summary['overall_performance']['avg_tokens']:.0f} vs target {summary['chapter5_targets']['target_avg_tokens']})")
    
    for achievement in achievements:
        html_content += f"<li>{achievement}</li>\n"
    
    html_content += f"""
            </ul>
            <p>
                <strong>Models Evaluated:</strong><br>
                General Enquiries: {summary['models']['general']}<br>
                Study Support: {summary['models']['study']}
            </p>
        </div>
    </body>
    </html>
    """
    
    # Save HTML report
    with open(os.path.join(output_dir, "chapter5_evaluation_report.html"), 'w') as f:
        f.write(html_content)
    
    print(f"\n📄 HTML report generated: {os.path.join(output_dir, 'chapter5_evaluation_report.html')}")


if __name__ == "__main__":
   main()