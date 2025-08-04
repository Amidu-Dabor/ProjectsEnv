#!/usr/bin/env python
from services.data_service import DataService
from services.ui_service6 import dashboard_ui
from configs.config import GPT4O_MODEL, CLAUDE_MODEL
from vector_services.data_curator import DataCurator, safe_embeddings_constructor
from api_gateway.gateway import register_service, get_gateway_metrics, register_wandb_service
import gradio as gr
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import time
import psutil
import atexit
import socket
import platform
import json
import threading

def main() -> None:
    base_dir = "usiu-knowledge-base"
    vector_store_dir = "vector_services/usiu_vector_db"

    # Load the existing vector store and obtain its retriever
    curator = DataCurator(knowledge_base_dir=base_dir, persist_directory=vector_store_dir)
    vector_store = curator.load_vectorstore()
    retriever = curator.get_retriever()

    # Initialize DataService with the retriever so that general chat uses RAG
    data_service = DataService(retriever=retriever)
    
    # Register services with API Gateway
    register_service("data_service", data_service)
    register_service("curator", curator)
    
    # Initialize and register Weights & Biases (W&B) service with app configuration
    app_config = {
        "app_version": "1.0.0",
        "models": {
            "general_chat": GPT4O_MODEL,
            "study_chat": CLAUDE_MODEL
        },
        "features": {
            "rag_enabled": True,
            "file_upload": True,
            "authentication": True
        },
        "system_info": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
        },
        "environment": os.environ.get("APP_ENV", "development")
    }
    # wandb_tracker = register_wandb_service(app_config)
    
    # Register cleanup function to properly finish W&B tracking when app closes
    # if wandb_tracker:
    #     atexit.register(wandb_tracker.finish)
    
    # Get system prompts for general and study support
    general_chat_prompt, study_prompt = data_service.prompts_service.get_prompt()

    # Build the dashboard, passing the relevant prompts, model identifiers, and retriever
    dashboard = dashboard_ui(
        general_chat_prompt=general_chat_prompt,
        general_model=CLAUDE_MODEL,
        study_prompt=study_prompt,
        study_model=CLAUDE_MODEL,
        retriever=retriever
    )

    # Get the directory where the current file (app.py) is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    static_path = os.path.join(current_dir, "static")
    images_path = os.path.join(static_path, "images")

    # Create directories if they don't exist
    if not os.path.isdir(static_path):
        os.makedirs(static_path)
    if not os.path.isdir(images_path):
        os.makedirs(images_path)

    app = dashboard.app
    
    # Mount static files directory
    app.mount("/static", StaticFiles(directory=static_path), name="static")

    # Add metrics endpoint to the FastAPI app
    # @app.get("/api/metrics")
    # def metrics():
    #     """Return the current gateway metrics as JSON"""
    #     gateway_metrics = get_gateway_metrics()
        
    #     # Log metrics to W&B when they're accessed
    #     if wandb_tracker:
    #         wandb_tracker.log_system_metrics({
    #             "api/total_requests": gateway_metrics.get("total_requests", 0),
    #             "api/active_services": len(gateway_metrics.get("services", {}))
    #         })
            
    #     return JSONResponse(content=gateway_metrics)
    
    # Start a background thread to log system metrics to W&B
    def log_system_metrics_to_wandb():
        """Background thread that logs system metrics to W&B"""
        while True:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                net_io = psutil.net_io_counters()
                
                # Get gateway metrics
                gateway_metrics = get_gateway_metrics()
                
                # Build metrics dictionary
                metrics = {
                    "system/cpu_percent": cpu_percent,
                    "system/memory_percent": memory.percent,
                    "system/memory_used_gb": memory.used / (1024 ** 3),
                    "system/memory_available_gb": memory.available / (1024 ** 3),
                    "system/disk_percent": disk.percent,
                    "system/disk_used_gb": disk.used / (1024 ** 3),
                    "system/disk_free_gb": disk.free / (1024 ** 3),
                    "system/network_bytes_sent": net_io.bytes_sent,
                    "system/network_bytes_recv": net_io.bytes_recv,
                    "api/total_requests": gateway_metrics.get("total_requests", 0),
                    "api/active_services": len(gateway_metrics.get("services", {}))
                }
                
                # Add service-specific metrics
                for service_name, service_metrics in gateway_metrics.get("services", {}).items():
                    metrics[f"service/{service_name}/requests"] = service_metrics.get("requests", 0)
                    metrics[f"service/{service_name}/errors"] = service_metrics.get("errors", 0)
                    metrics[f"service/{service_name}/avg_response_time"] = service_metrics.get("avg_response_time", 0)
                
                # Log to W&B
                # wandb_tracker.log_system_metrics(metrics)
                
                # Sleep for 15 seconds to not overwhelm W&B
                time.sleep(15)
            except Exception as e:
                print(f"Error logging system metrics: {e}")
                time.sleep(60)  # Wait longer if there was an error
    
    # Start the metrics logging thread if W&B is enabled
    # if wandb_tracker:
    #     metrics_thread = threading.Thread(
    #         target=log_system_metrics_to_wandb, 
    #         daemon=True,
    #         name="WandbMetricsThread"
    #     )
    #     metrics_thread.start()
        
    #     # Log initial app startup metrics
    #     startup_metrics = {
    #         "app/startup": 1,
    #         "app/version": app_config["app_version"],
    #         "system/hostname": socket.gethostname(),
    #         "system/platform": platform.platform()
    #     }
    #     wandb_tracker.log_system_metrics(startup_metrics)
    
    # Add enhanced metrics dashboard with W&B link
    # @app.get("/metrics-dashboard")
    # def metrics_dashboard():
    #     """Return an HTML dashboard for metrics with W&B integration"""
    #     from configs.config import WANDB_ENTITY, WANDB_PROJECT_NAME, WANDB_API_KEY

    #     # Get the W&B project URL
    #     wandb_entity = wandb_tracker.entity if wandb_tracker else WANDB_ENTITY
    #     wandb_project = wandb_tracker.project_name if wandb_tracker else "usiu-chatbot"
    #     wandb_url = f"https://wandb.ai/{wandb_entity}/{wandb_project}"
        
    #     html_content = f"""
    #     <!DOCTYPE html>
    #     <html>
    #     <head>
    #         <title>USIU Chatbot Metrics</title>
    #         <style>
    #             body {{
    #                 font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    #                 margin: 0;
    #                 padding: 0;
    #                 background-color: #f5f5f5;
    #                 color: #333;
    #             }}
    #             .container {{
    #                 max-width: 1200px;
    #                 margin: 0 auto;
    #                 padding: 20px;
    #             }}
    #             .header {{
    #                 background-color: #1F2E8C;
    #                 color: white;
    #                 padding: 20px;
    #                 text-align: center;
    #                 border-radius: 5px 5px 0 0;
    #                 margin-bottom: 20px;
    #             }}
    #             .card {{
    #                 background-color: white;
    #                 border-radius: 5px;
    #                 box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    #                 padding: 20px;
    #                 margin-bottom: 20px;
    #             }}
    #             .metrics-grid {{
    #                 display: grid;
    #                 grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    #                 gap: 20px;
    #                 margin-bottom: 20px;
    #             }}
    #             .metric-card {{
    #                 background-color: white;
    #                 border-radius: 5px;
    #                 box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    #                 padding: 15px;
    #             }}
    #             .metric-title {{
    #                 font-weight: 600;
    #                 font-size: 16px;
    #                 color: #1F2E8C;
    #                 margin-bottom: 10px;
    #                 border-bottom: 1px solid #eee;
    #                 padding-bottom: 5px;
    #             }}
    #             .metric-value {{
    #                 font-size: 24px;
    #                 font-weight: 700;
    #                 margin: 10px 0;
    #             }}
    #             .chart-container {{
    #                 height: 200px;
    #                 margin: 15px 0;
    #             }}
    #             .btn {{
    #                 background-color: #1F2E8C;
    #                 color: white;
    #                 border: none;
    #                 padding: 10px 20px;
    #                 border-radius: 5px;
    #                 cursor: pointer;
    #                 font-size: 14px;
    #                 font-weight: 500;
    #                 transition: background-color 0.3s;
    #             }}
    #             .btn:hover {{
    #                 background-color: #000066;
    #             }}
    #             .tabs {{
    #                 display: flex;
    #                 margin-bottom: 20px;
    #                 border-bottom: 1px solid #ddd;
    #             }}
    #             .tab {{
    #                 padding: 10px 20px;
    #                 cursor: pointer;
    #                 border-bottom: 2px solid transparent;
    #                 font-weight: 500;
    #             }}
    #             .tab.active {{
    #                 border-bottom: 2px solid #1F2E8C;
    #                 color: #1F2E8C;
    #             }}
    #             .tab-content {{
    #                 display: none;
    #             }}
    #             .tab-content.active {{
    #                 display: block;
    #             }}
    #             .wandb-section {{
    #                 margin-top: 30px;
    #                 text-align: center;
    #             }}
    #             .wandb-button {{
    #                 display: inline-block;
    #                 background-color: #FFBE00;
    #                 color: black;
    #                 text-decoration: none;
    #                 padding: 12px 25px;
    #                 border-radius: 5px;
    #                 font-weight: 600;
    #                 margin-top: 10px;
    #                 transition: all 0.3s;
    #             }}
    #             .wandb-button:hover {{
    #                 background-color: #E6A800;
    #                 transform: translateY(-2px);
    #                 box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    #             }}
    #             .footer {{
    #                 text-align: center;
    #                 margin-top: 30px;
    #                 color: #666;
    #                 font-size: 14px;
    #             }}
    #             #timestamp {{
    #                 text-align: right;
    #                 color: #666;
    #                 font-size: 12px;
    #                 margin-bottom: 20px;
    #             }}
    #         </style>
    #     </head>
    #     <body>
    #         <div class="container">
    #             <div class="header">
    #                 <h1>USIU Chatbot Analytics Dashboard</h1>
    #                 <p>Real-time metrics and performance analytics</p>
    #             </div>
                
    #             <div class="tabs">
    #                 <div class="tab active" onclick="showTab('overview')">Overview</div>
    #                 <div class="tab" onclick="showTab('services')">Services</div>
    #                 <div class="tab" onclick="showTab('chatbot')">Chatbot Performance</div>
    #                 <div class="tab" onclick="showTab('system')">System Metrics</div>
    #             </div>
                
    #             <div id="timestamp">Last updated: Loading...</div>
                
    #             <div id="overview-tab" class="tab-content active">
    #                 <div class="metrics-grid">
    #                     <div class="metric-card">
    #                         <div class="metric-title">Total Requests</div>
    #                         <div class="metric-value" id="total-requests">Loading...</div>
    #                     </div>
    #                     <div class="metric-card">
    #                         <div class="metric-title">Active Services</div>
    #                         <div class="metric-value" id="active-services">Loading...</div>
    #                     </div>
    #                     <div class="metric-card">
    #                         <div class="metric-title">Average Response Time</div>
    #                         <div class="metric-value" id="avg-response-time">Loading...</div>
    #                     </div>
    #                     <div class="metric-card">
    #                         <div class="metric-title">System Load</div>
    #                         <div class="metric-value" id="system-load">Loading...</div>
    #                     </div>
    #                 </div>
                    
    #                 <div class="card">
    #                     <h2>Recent Activity</h2>
    #                     <div class="chart-container">
    #                         <p style="text-align:center;margin-top:70px;color:#666;">
    #                             View detailed charts in Weights & Biases
    #                         </p>
    #                     </div>
    #                 </div>
    #             </div>
                
    #             <div id="services-tab" class="tab-content">
    #                 <div class="card">
    #                     <h2>Service Health</h2>
    #                     <div id="service-metrics">
    #                         Loading service metrics...
    #                     </div>
    #                 </div>
    #             </div>
                
    #             <div id="chatbot-tab" class="tab-content">
    #                 <div class="metrics-grid">
    #                     <div class="metric-card">
    #                         <div class="metric-title">Total Conversations</div>
    #                         <div class="metric-value" id="total-conversations">-</div>
    #                     </div>
    #                     <div class="metric-card">
    #                         <div class="metric-title">User Satisfaction</div>
    #                         <div class="metric-value" id="user-satisfaction">-</div>
    #                     </div>
    #                     <div class="metric-card">
    #                         <div class="metric-title">Average Chat Length</div>
    #                         <div class="metric-value" id="avg-chat-length">-</div>
    #                     </div>
    #                     <div class="metric-card">
    #                         <div class="metric-title">File Uploads</div>
    #                         <div class="metric-value" id="file-uploads">-</div>
    #                     </div>
    #                 </div>
                    
    #                 <div class="card">
    #                     <h2>Conversation Analytics</h2>
    #                     <p style="text-align:center;color:#666;">
    #                         Detailed conversation analytics are available in Weights & Biases
    #                     </p>
    #                 </div>
    #             </div>
                
    #             <div id="system-tab" class="tab-content">
    #                 <div class="metrics-grid">
    #                     <div class="metric-card">
    #                         <div class="metric-title">CPU Usage</div>
    #                         <div class="metric-value" id="cpu-usage">-</div>
    #                     </div>
    #                     <div class="metric-card">
    #                         <div class="metric-title">Memory Usage</div>
    #                         <div class="metric-value" id="memory-usage">-</div>
    #                     </div>
    #                     <div class="metric-card">
    #                         <div class="metric-title">Disk Usage</div>
    #                         <div class="metric-value" id="disk-usage">-</div>
    #                     </div>
    #                     <div class="metric-card">
    #                         <div class="metric-title">Network Traffic</div>
    #                         <div class="metric-value" id="network-traffic">-</div>
    #                     </div>
    #                 </div>
    #             </div>
                
    #             <div class="wandb-section">
    #                 <h2>Advanced Analytics</h2>
    #                 <p>For detailed metrics, charts, and conversation analytics, visit the Weights & Biases dashboard</p>
    #                 <a href="{wandb_url}" target="_blank" class="wandb-button">
    #                     Open W&B Dashboard →
    #                 </a>
    #             </div>
                
    #             <div class="footer">
    #                 <p>USIU-Africa AI Chatbot © {time.strftime("%Y")}</p>
    #             </div>
    #         </div>
            
    #         <script>
    #             // Show active tab
    #             function showTab(tabId) {{
    #                 // Hide all tabs
    #                 document.querySelectorAll('.tab-content').forEach(tab => {{
    #                     tab.classList.remove('active');
    #                 }});
                    
    #                 // Remove active class from tab buttons
    #                 document.querySelectorAll('.tab').forEach(tab => {{
    #                     tab.classList.remove('active');
    #                 }});
                    
    #                 // Show selected tab
    #                 document.getElementById(tabId + '-tab').classList.add('active');
                    
    #                 // Add active class to clicked tab button
    #                 document.querySelectorAll('.tab').forEach(tab => {{
    #                     if (tab.textContent.toLowerCase().includes(tabId)) {{
    #                         tab.classList.add('active');
    #                     }}
    #                 }});
    #             }}
                
    #             // Fetch metrics on page load
    #             document.addEventListener('DOMContentLoaded', fetchMetrics);
                
    #             function fetchMetrics() {{
    #                 fetch('/api/metrics')
    #                     .then(response => response.json())
    #                     .then(data => {{
    #                         document.getElementById('timestamp').textContent = 'Last updated: ' + new Date().toLocaleString();
                            
    #                         // Update overview metrics
    #                         document.getElementById('total-requests').textContent = data.total_requests || 0;
    #                         document.getElementById('active-services').textContent = Object.keys(data.services || {{}}).length;
                            
    #                         let totalTime = 0;
    #                         let serviceCount = 0;
                            
    #                         // Calculate average response time across all services
    #                         for (const service in data.services || {{}}) {{
    #                             if (data.services[service].avg_response_time) {{
    #                                 totalTime += data.services[service].avg_response_time;
    #                                 serviceCount++;
    #                             }}
    #                         }}
                            
    #                         const avgResponseTime = serviceCount > 0 ? (totalTime / serviceCount).toFixed(4) + 's' : 'N/A';
    #                         document.getElementById('avg-response-time').textContent = avgResponseTime;
                            
    #                         // For system load, estimate based on CPU usage from services activity
    #                         let systemLoad = "Low";
    #                         if (data.total_requests > 100) {{
    #                             systemLoad = "High";
    #                         }} else if (data.total_requests > 20) {{
    #                             systemLoad = "Medium";
    #                         }}
    #                         document.getElementById('system-load').textContent = systemLoad;
                            
    #                         // Update service metrics
    #                         const servicesContainer = document.getElementById('service-metrics');
    #                         servicesContainer.innerHTML = '';
                            
    #                         for (const [serviceName, metrics] of Object.entries(data.services || {{}})) {{
    #                             const serviceCard = document.createElement('div');
    #                             serviceCard.className = 'metric-card';
    #                             serviceCard.style.margin = '10px 0';
                                
    #                             const lastActivityMinutes = Math.round(metrics.last_activity / 60);
    #                             const lastActivityText = lastActivityMinutes <= 0 
    #                                 ? 'just now' 
    #                                 : `${{lastActivityMinutes}} minute${{lastActivityMinutes !== 1 ? 's' : ''}} ago`;
                                
    #                             const errorStyle = metrics.errors > 0 ? 'color: #c62828; font-weight: bold;' : '';
                                
    #                             serviceCard.innerHTML = `
    #                                 <div class="metric-title">${{serviceName}}</div>
    #                                 <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
    #                                     <div>
    #                                         <strong>Requests:</strong> ${{metrics.requests}}
    #                                     </div>
    #                                     <div style="${{errorStyle}}">
    #                                         <strong>Errors:</strong> ${{metrics.errors}}
    #                                     </div>
    #                                     <div>
    #                                         <strong>Avg Response:</strong> ${{metrics.avg_response_time ? metrics.avg_response_time.toFixed(4) + 's' : 'N/A'}}
    #                                     </div>
    #                                     <div>
    #                                         <strong>Last Activity:</strong> ${{lastActivityText}}
    #                                     </div>
    #                                 </div>
    #                             `;
                                
    #                             servicesContainer.appendChild(serviceCard);
    #                         }}
                            
    #                         // Calculate and display chatbot performance metrics
    #                         // Here we just show placeholders - the real data comes from W&B
    #                         document.getElementById('total-conversations').textContent = "See W&B Dashboard";
    #                         document.getElementById('user-satisfaction').textContent = "See W&B Dashboard";
    #                         document.getElementById('avg-chat-length').textContent = "See W&B Dashboard";
    #                         document.getElementById('file-uploads').textContent = "See W&B Dashboard";
                            
    #                         // Calculate and display system metrics
    #                         document.getElementById('cpu-usage').textContent = "See W&B Dashboard";
    #                         document.getElementById('memory-usage').textContent = "See W&B Dashboard";
    #                         document.getElementById('disk-usage').textContent = "See W&B Dashboard";
    #                         document.getElementById('network-traffic').textContent = "See W&B Dashboard";
    #                     }})
    #                     .catch(error => {{
    #                         console.error('Error fetching metrics:', error);
    #                         document.getElementById('service-metrics').innerHTML = 
    #                             '<div style="color: #c62828; padding: 15px;">Error fetching metrics</div>';
    #                     }});
    #             }}
                
    #             // Auto-refresh every 30 seconds
    #             setInterval(fetchMetrics, 30000);
    #         </script>
    #     </body>
    #     </html>
    #     """
        
    #     from fastapi.responses import HTMLResponse
    #     return HTMLResponse(content=html_content)

    # print("\n" + "="*80)
    # print("USIU Chatbot with W&B Integration starting up...")
    # print("="*80)
    # print(f"Current working directory: {current_dir}")
    # print(f"Serving static files from: {static_path}")
    # print(f"Images path: {images_path}")
    # print(f"Basic metrics dashboard: http://localhost:7860/metrics-dashboard")
    # if wandb_tracker:
    #     print(f"W&B dashboard: https://wandb.ai/{wandb_tracker.entity or 'daboramidu93-united-states-international-university-africa'}/{wandb_tracker.project_name}")
    # print("="*80 + "\n")
    
    dashboard.launch(share=True, inbrowser=True)

if __name__ == "__main__":
    main()