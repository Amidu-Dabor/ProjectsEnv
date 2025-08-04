# services/ui_service.py

import re
import time
import json
import gradio as gr
from typing import Optional

from configs.config import GPT4O_MODEL, CLAUDE_MODEL
from services.auth_service import (
    authenticate, create_session, get_session, update_session_activity, 
    end_session, is_session_active, get_session_remaining_time, should_show_warning,
    INACTIVITY_TIMEOUT, WARNING_TIMEOUT
)
from services.general_chat_service import GeneralChatService
from services.study_support_service import StudySupportService
from api_gateway.gateway import get_service
from .custom_css import custom_css

# Session Management Functions
def check_session_status(session_id):
    """Check session status and return relevant information."""
    if not session_id:
        return json.dumps({"valid": False, "remaining": 0, "show_warning": False})
    
    session = get_session(session_id)
    if not session:
        return json.dumps({"valid": False, "remaining": 0, "show_warning": False})
    
    remaining = get_session_remaining_time(session_id)
    show_warning = should_show_warning(session_id)
    
    return json.dumps({
        "valid": remaining > 0,
        "remaining": remaining,
        "show_warning": show_warning,
        "user_id": session.get("user_id", "")
    })

def keep_session_alive(session_id):
    """Update session activity and return new status."""
    success = update_session_activity(session_id)
    
    if success:
        status = check_session_status(session_id)
    else:
        status = json.dumps({"valid": False})
        
    return json.dumps({
        "success": success,
        "status": status
    })

# Notification Helpers
def show_success(message: str, duration: float = 8, visible: bool = True, title: str = "Success") -> None:
    """Display a success notification"""
    styled_message = (
        f'<span style="color: #2e7d32; background-color: #c8e6c9; padding: 10px; '
        f'border-radius: 4px; display: block;">{message}</span>'
    )
    gr.Success(styled_message, duration=duration, visible=visible, title=title)
    time.sleep(0.1)

def show_error(message: str, duration: float = 10, visible: bool = True, title: str = "Error") -> None:
    """Display an error notification"""
    styled_message = (
        f'<span style="color: #c62828; background-color: #ffcdd2; padding: 10px; '
        f'border-radius: 4px; display: block;">{message}</span>'
    )
    gr.Error(styled_message, duration=duration, visible=visible, title=title)
    time.sleep(0.1)

# Login Form UI
def login_form_ui():
    """Create and return the login form interface"""
    with gr.Blocks() as login_form:
        gr.Markdown("## Please Login")
        user_id_input = gr.Textbox(
            placeholder="Enter your User ID", 
            label="User ID", 
            type="email", 
            autofocus=True
        )
        user_id_error = gr.Markdown("", visible=True)
        
        password_input = gr.Textbox(
            placeholder="Enter your Password", 
            label="Password", 
            type="password"
        )
        password_error = gr.Markdown("", visible=True)
        
        login_btn = gr.Button("Login")
        login_msg = gr.Markdown("")
        proceed_btn = gr.Button("Proceed", visible=False)
        back_btn = gr.Button("Back to Dashboard")
        
        session_id = gr.Textbox(visible=False)
    
    return login_form, user_id_input, user_id_error, password_input, password_error, login_btn, login_msg, proceed_btn, back_btn, session_id

# Authentication Logic
def handle_login(user_id, password):
    """Validates login fields and the User ID."""
    try:
        user_id = user_id.strip() if user_id else ""
        password = password.strip() if password else ""

        # Validation logic
        if user_id == "" and password == "":
            show_error("Please enter your User ID and Password.")
            return (
                "<span style='color:#c62828;'>Please enter your User ID and Password.</span>",
                "", "", gr.update(visible=False), gr.update(visible=True), ""
            )
        elif user_id == "":
            show_error("User ID is required.")
            return (
                "", 
                "<span style='color:#c62828;'>User ID is required.</span>",
                "", gr.update(visible=False), gr.update(visible=True), ""
            )
        elif password == "":
            show_error("Password is required.")
            return (
                "",
                "",
                "<span style='color:#c62828;'>Password is required.</span>",
                gr.update(visible=False), gr.update(visible=True), ""
            )
        else:
           # Validate email format
           email_regex = r'^[\w\.-]+@usiu\.ac\.ke$'
           if not re.match(email_regex, user_id):
               show_error("User ID must be a valid \"@usiu.ac.ke\" email address.")
               return (
                   "",
                   "<span style='color:#c62828;'>User ID must be a valid @usiu.ac.ke email address.</span>",
                   "", gr.update(visible=False), gr.update(visible=True), ""
               )
           
           # Attempt authentication
           if authenticate(user_id, password):
               session_id = create_session(user_id)
               show_success("Login successful! Click 'Proceed' to continue!", duration=10)
               return (
                   "", "", "",
                   gr.update(visible=True),  # Show Proceed button
                   gr.update(visible=False),  # Hide Login button
                   session_id
               )
           else:
               show_error("Invalid credentials. Please try again.")
               return (
                   "<span style='color:#c62828;'>Invalid credentials. Please try again.</span>",
                   "", "", gr.update(visible=False), gr.update(visible=True), ""
               )
    except Exception as e:
       show_error(f"System error: {str(e)}. Please ensure required modules are imported.")
       return (
           "<span style='color:#c62828;'>System error encountered.</span>",
           "", "", gr.update(visible=False), gr.update(visible=True), ""
       )

# Main Dashboard UI
def dashboard_ui(general_chat_prompt: str, general_model: str, 
                study_prompt: str, study_model: str, retriever=None):
   """Creates a dashboard with professional styling and smooth transitions."""
   
   # Initialize chat services
   general_chat_service = GeneralChatService(general_chat_prompt, general_model, retriever)
   study_support_service = StudySupportService(study_prompt, study_model)
   
   # Get chat interfaces
   general_chat_component = general_chat_service.create_interface()
   study_support_component = study_support_service.create_interface()
   
   # Get login form
   (login_form_component, user_id_input, user_id_error, password_input, password_error,
    login_btn, login_msg, proceed_btn, login_back_btn, session_id) = login_form_ui()
   
   # Inactivity warning modal HTML
   inactivity_warning_html = """
   <div class="overlay" id="inactivity-overlay"></div>
   <div class="inactive-warning" id="inactivity-warning">
       <h3>Session Timeout Warning</h3>
       <p>Your session will expire due to inactivity in <span id="countdown">0</span> seconds.</p>
       <p>Would you like to continue your session?</p>
       <button id="stay-active-btn">Stay Active</button>
   </div>
   """
   
   # W&B dashboard setup
   default_entity = "daboramidu93-united-states-international-university-africa"
   default_project = "usiu-chatbot"
   
   entity = default_entity
   project = default_project
   
   try:
       wandb_tracker = get_service("wandb_tracker")
       if wandb_tracker:
           if hasattr(wandb_tracker, 'entity') and wandb_tracker.entity:
               entity = wandb_tracker.entity
           if hasattr(wandb_tracker, 'project_name') and wandb_tracker.project_name:
               project = wandb_tracker.project_name
   except Exception as e:
       print(f"Error getting W&B tracker: {e}")
   
   dashboard_url = f"https://wandb.ai/{entity}/{project}"
   
   # W&B dashboard HTML
   wandb_dashboard_html = f"""
   <div style="display: flex; flex-direction: column; height: 66vh; padding: 20px; text-align: center;">
       <h2 style="margin-bottom: 20px;">Chatbot Analytics</h2>
       <div style="margin: 10px 0; padding: 10px; background-color: #f8f9fa; border-radius: 5px; font-size: 14px; color: #666;">
           <p>
               Full analytics and visualizations are available in the Weights & Biases dashboard.
               Click the button below to open the dashboard in a new tab.
           </p>
       </div>
       
       <div style="margin: 0 auto;">
           <a href="{dashboard_url}" target="_blank" 
              style="background-color: #FFBE00; color: black; text-decoration: none; 
                     padding: 15px 30px; border-radius: 5px; font-weight: bold; 
                     display: inline-block; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                     transition: all 0.3s ease;">
               Open W&B Dashboard
           </a>
       </div>
       <div style="margin-top: 40px; padding: 20px; background: #f5f5f5; border-radius: 10px;">
           <h3>What's tracked in the dashboard?</h3>
           <ul style="text-align: left; margin: 20px auto; max-width: 600px;">
               <li><strong>Conversation metrics</strong>: Number of conversations, response times, token usage</li>
               <li><strong>User feedback</strong>: Likes, dislikes, and neutral ratings</li>
               <li><strong>File uploads</strong>: Types, sizes, and processing times</li>
               <li><strong>System performance</strong>: CPU, memory, and API usage</li>
               <li><strong>Error tracking</strong>: Occurred errors and their frequency</li>
               <li><strong>RAG performance</strong>: Document retrieval effectiveness</li>
               <li><strong>Model comparison</strong>: Response quality metrics</li>
           </ul>
       </div>
   </div>
   """
   
   # Theme toggle JavaScript
   theme_toggle_js = """
   <script>
   // Theme handling functionality
   document.addEventListener('DOMContentLoaded', function() {
       // Theme detection and initialization
       function initTheme() {
           const savedTheme = localStorage.getItem('theme');
           if (savedTheme) {
               document.documentElement.setAttribute('data-theme', savedTheme);
               updateThemeIcon(savedTheme);
           } else {
               const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
               const theme = prefersDark ? 'dark' : 'light';
               document.documentElement.setAttribute('data-theme', theme);
               updateThemeIcon(theme);
           }
       }

       // Update the theme toggle icon based on current theme
       function updateThemeIcon(theme) {
           const themeToggles = document.querySelectorAll('.theme-toggle');
           themeToggles.forEach(toggle => {
               if (theme === 'dark') {
                   toggle.innerHTML = `
                       <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                           <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41.39.39 1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41.39.39 1.03.39 1.41 0l1.06-1.06z" />
                       </svg>
                       <span class="tooltip">Switch to Light Mode</span>
                   `;
               } else {
                   toggle.innerHTML = `
                       <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                           <path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-2.98 0-5.4-2.42-5.4-5.4 0-1.81.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z" />
                       </svg>
                       <span class="tooltip">Switch to Dark Mode</span>
                   `;
               }
           });
       }

       // Toggle between light and dark theme
       function toggleTheme() {
           const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
           const newTheme = currentTheme === 'light' ? 'dark' : 'light';
           
           document.documentElement.setAttribute('data-theme', newTheme);
           localStorage.setItem('theme', newTheme);
           updateThemeIcon(newTheme);
       }

       // Initialize theme when page loads
       initTheme();

       // Set up listeners for theme toggle buttons
       document.addEventListener('click', function(e) {
           if (e.target.closest('.theme-toggle')) {
               toggleTheme();
           }
       });

       // Listen for system theme changes
       window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
           if (!localStorage.getItem('theme')) {
               const theme = e.matches ? 'dark' : 'light';
               document.documentElement.setAttribute('data-theme', theme);
               updateThemeIcon(theme);
           }
       });
   });
   </script>
   """
   
   # Build the dashboard
   with gr.Blocks(css=custom_css()) as dashboard:
       # Header component
       header_component = gr.HTML('''
       <div class="app-header">
           <img src="/Users/apple/Desktop/chatbot_prototype/images/usiu-logo.png" alt="Logo" class="logo-dashboard" />
           <div class="header-controls">
               <button class="theme-toggle" aria-label="Toggle theme"></button>
           </div>
       </div>
       <div class="content-area"></div>
       ''', elem_id="header-container")

       # Define containers
       dashboard_container = gr.Column(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInUp content-area")
       general_container = gr.Column(visible=False, elem_classes="chat-container pre-animation content-area")
       login_container = gr.Column(visible=False, elem_classes="container floating-card login-form-container pre-animation content-area")
       study_container = gr.Column(visible=False, elem_classes="chat-container pre-animation content-area")
       analytics_container = gr.Column(visible=False, elem_classes="container floating-card dashboard-card pre-animation content-area")
       
       # Add inactivity warning modal
       gr.HTML(inactivity_warning_html)
       
       # Logout components
       with gr.Row(visible=False, elem_id="logout-row") as logout_component:
           current_user = gr.Textbox(visible=False, elem_id="user-email")
           logout_btn = gr.Button("Logout", elem_id="logout-btn", visible=False)
       
       # Dashboard View
       with dashboard_container:
           gr.Markdown("<h1 class='with-logo'>Academic AI Assistant</h1>")
           with gr.Column(elem_classes="dashboard-menu"):
               gen_button = gr.Button("General Enquiries", elem_classes="menu-button")
               study_button = gr.Button("Study with AI", elem_classes="menu-button")
               analytics_button = gr.Button("Analytics Dashboard", elem_classes="menu-button")
       
       # General Chat View
       with general_container:
           back_gen = gr.Button("Back to Dashboard")
           general_chat_component.render()
       
       # Login Form View
       with login_container:
           login_form_component.render()
       
       # Study Support View
       with study_container:
           back_study = gr.Button("Back to Dashboard")
           study_support_component.render()
           session_id_for_study = gr.Textbox(visible=False)
           
       # Analytics Dashboard View
       with analytics_container:
           back_analytics = gr.Button("Back to Dashboard")
           gr.Markdown("## Weights & Biases Analytics Dashboard")
           gr.HTML(wandb_dashboard_html)
       
       # Hidden session management components
       with gr.Row(visible=False):
           check_session_fn = gr.Button("check_session", elem_id="check_session_status")
           keep_alive_fn = gr.Button("keep_alive", elem_id="keep_session_alive")
           session_status_output = gr.JSON(elem_id="session_status_output")
           keep_alive_output = gr.JSON(elem_id="keep_alive_output")
       
       # Session management functions
       check_session_fn.click(
           check_session_status,
           inputs=[session_id_for_study],
           outputs=[session_status_output]
       )
       
       keep_alive_fn.click(
           keep_session_alive,
           inputs=[session_id_for_study],
           outputs=[keep_alive_output]
       )
       
       # Add JavaScript for session management and height adjustments
       gr.HTML(theme_toggle_js + """
       <script>
       // Session management with server synchronization
       let sessionId = "";
       let sessionCheckInterval;
       let warningDisplayed = false;
       
       // Function to start session monitoring
       function startSessionMonitoring(sid) {
           sessionId = sid;
           console.log("Starting session monitoring for session ID:", sid);
           
           if (sessionCheckInterval) {
               clearInterval(sessionCheckInterval);
           }
           
           sessionCheckInterval = setInterval(checkSessionStatus, 5000);
           setupActivityTracking();
       }
       
       // Function to check session status with the server
       function checkSessionStatus() {
           if (!sessionId) return;
           
           const buttons = document.querySelectorAll('button');
           for (const button of buttons) {
               if (button.textContent === 'check_session') {
                   button.click();
                   break;
               }
           }
       }
       
       // Function to handle session status updates
       function handleSessionStatus(status) {
           if (!status) return;
           
           if (!status.valid) {
               performLogout();
               return;
           }
           
           if (status.show_warning && !warningDisplayed) {
               showSessionWarning(status.remaining);
               warningDisplayed = true;
           } else if (!status.show_warning && warningDisplayed) {
               hideSessionWarning();
               warningDisplayed = false;
           }
           
           if (warningDisplayed) {
               updateCountdown(status.remaining);
           }
       }
       
       // Function to keep session alive
       function keepSessionAlive() {
           if (!sessionId) return;
           
           const buttons = document.querySelectorAll('button');
           for (const button of buttons) {
               if (button.textContent === 'keep_alive') {
                   button.click();
                   break;
               }
           }
           
           hideSessionWarning();
           warningDisplayed = false;
       }
       
       // Function to show session warning
       function showSessionWarning(remaining) {
           const overlay = document.getElementById('inactivity-overlay');
           const warning = document.getElementById('inactivity-warning');
           
           if (overlay && warning) {
               updateCountdown(remaining);
               overlay.style.display = "block";
               warning.style.display = "block";
           }
       }
       
       // Function to hide session warning
       function hideSessionWarning() {
           const overlay = document.getElementById('inactivity-overlay');
           const warning = document.getElementById('inactivity-warning');
           
           if (overlay && warning) {
               overlay.style.display = "none";
               warning.style.display = "none";
           }
       }
       
       // Function to update countdown display
       function updateCountdown(seconds) {
           const countdownEl = document.getElementById('countdown');
           if (countdownEl) {
               countdownEl.textContent = Math.max(0, seconds);
           }
       }
       
       // Function to perform logout
       function performLogout() {
           const logoutBtn = document.getElementById('logout-btn');
           if (logoutBtn) {
               logoutBtn.click();
           } else {
               window.location.href = window.location.pathname;
           }
       }
       
       // Function to setup activity tracking
       function setupActivityTracking() {
           ["mousemove", "keydown", "click", "scroll", "touchstart"].forEach(function(event) {
               document.addEventListener(event, function() {
                   if (!warningDisplayed) {
                       keepSessionAlive();
                   }
               });
           });
           
           const stayActiveBtn = document.getElementById('stay-active-btn');
           if (stayActiveBtn) {
               stayActiveBtn.addEventListener('click', keepSessionAlive);
           }
       }
       
       // Function to fix chat interface heights
       function adjustChatInterfaceHeights() {
           setTimeout(function() {
               const chatInterfaces = document.querySelectorAll('.chat-interface-container');
               
               chatInterfaces.forEach(function(chatInterface) {
                   chatInterface.style.minHeight = '600px';
                   chatInterface.style.height = '75vh';
                   
                   const chatElement = chatInterface.querySelector('.chat');
                   if (chatElement) {
                       chatElement.style.minHeight = '600px';
                       chatElement.style.height = '75vh';
                       
                       const chatWindow = chatElement.querySelector('.chat-window');
                       if (chatWindow) {
                           chatWindow.style.minHeight = '450px';
                           chatWindow.style.height = 'calc(75vh - 150px)';
                           chatWindow.style.overflowY = 'auto';
                           
                           const chatContent = chatWindow.querySelector('.chat-window-content');
                           if (chatContent) {
                               chatContent.style.minHeight = '450px';
                               chatContent.style.height = 'calc(75vh - 150px)';
                               chatContent.style.overflowY = 'auto';
                           }
                       }
                   }
               });
           }, 500);
       }
       
       // Watch for session status updates and DOM changes
       document.addEventListener('DOMContentLoaded', function() {
           adjustChatInterfaceHeights();
           
           const observer = new MutationObserver(function(mutations) {
               adjustChatInterfaceHeights();
               
               mutations.forEach(function(mutation) {
                   if (mutation.type === 'childList') {
                       const statusElements = document.querySelectorAll('[id$="session_status_output"]');
                       for (const element of statusElements) {
                           if (element.textContent.trim()) {
                               try {
                                   const status = JSON.parse(element.textContent);
                                   handleSessionStatus(status);
                               } catch (e) {
                                   console.error("Error parsing session status:", e);
                               }
                           }
                       }
                   }
               });
           });
           
           observer.observe(document.body, {
               childList: true,
               subtree: true
           });
           
           setInterval(adjustChatInterfaceHeights, 2000);
       });
       
       // Add event listeners for menu buttons
       window.addEventListener('load', function() {
           const buttons = document.querySelectorAll('button');
           
           buttons.forEach(function(button) {
               button.addEventListener('click', function() {
                   setTimeout(adjustChatInterfaceHeights, 300);
               });
           });
       });
       </script>
       """)
       
       # Navigation Callbacks
       gen_button.click(
           lambda: [
               gr.update(visible=False),
               gr.update(visible=True, elem_classes="chat-container animate-fadeInRight"),
               gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
               gr.update(visible=False, elem_classes="chat-container pre-animation"),
               gr.update(visible=False, elem_classes="container floating-card dashboard-card pre-animation")
           ],
           outputs=[dashboard_container, general_container, login_container, study_container, analytics_container]
       )
       
       study_button.click(
           lambda: [
               gr.update(visible=False),
               gr.update(visible=False, elem_classes="chat-container pre-animation"),
               gr.update(visible=True, elem_classes="container floating-card login-form-container animate-fadeInRight"),
               gr.update(visible=False, elem_classes="chat-container pre-animation"),
               gr.update(visible=False, elem_classes="container floating-card dashboard-card pre-animation")
           ],
           outputs=[dashboard_container, general_container, login_container, study_container, analytics_container]
       )
       
       analytics_button.click(
           lambda: [
               gr.update(visible=False),
               gr.update(visible=False, elem_classes="chat-container pre-animation"),
               gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
               gr.update(visible=False, elem_classes="chat-container pre-animation"),
               gr.update(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInRight")
           ],
           outputs=[dashboard_container, general_container, login_container, study_container, analytics_container]
       )
       
       # Back buttons
       back_gen.click(
           lambda: [
               gr.update(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInLeft"),
               gr.update(visible=False, elem_classes="chat-container pre-animation"),
               gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
               gr.update(visible=False, elem_classes="chat-container pre-animation"),
               gr.update(visible=False, elem_classes="container floating-card dashboard-card pre-animation")
           ],
           outputs=[dashboard_container, general_container, login_container, study_container, analytics_container]
       )
       
       back_study.click(
           lambda: [
               gr.update(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInLeft"),
               gr.update(visible=False, elem_classes="chat-container pre-animation"),
               gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
               gr.update(visible=False, elem_classes="chat-container pre-animation"),
               gr.update(visible=False, elem_classes="container floating-card dashboard-card pre-animation"),
               "",
               gr.update(visible=False),
               '''
               <div class="app-header">
                   <img src="/Users/apple/Desktop/chatbot_prototype/images/usiu-logo.png" alt="Logo" class="logo-dashboard" />
                   <div class="header-controls">
                       <button class="theme-toggle" aria-label="Toggle theme"></button>
                   </div>
               </div>
               <div class="content-area"></div>
               '''
           ],
           outputs=[dashboard_container, general_container, login_container, study_container, analytics_container, current_user, logout_component, header_component]
       )
       
       back_analytics.click(
           lambda: [
               gr.update(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInLeft"),
               gr.update(visible=False, elem_classes="chat-container pre-animation"),
               gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
               gr.update(visible=False, elem_classes="chat-container pre-animation"),
               gr.update(visible=False, elem_classes="container floating-card dashboard-card pre-animation")
           ],
           outputs=[dashboard_container, general_container, login_container, study_container, analytics_container]
       )
       
       login_back_btn.click(
           lambda: [
               gr.update(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInLeft"),
               gr.update(visible=False, elem_classes="chat-container pre-animation"),
               gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
               gr.update(visible=False, elem_classes="chat-container pre-animation"),
               gr.update(visible=False, elem_classes="container floating-card dashboard-card pre-animation")
           ],
           outputs=[dashboard_container, general_container, login_container, study_container, analytics_container]
       )
       
       # Authentication logic
       login_btn.click(
           handle_login,
           inputs=[user_id_input, password_input],
           outputs=[login_msg, user_id_error, password_error, proceed_btn, login_btn, session_id]
       )
       
       # Proceed to study after login
       def proceed_to_study(session_id_value):
           session = get_session(session_id_value)
           user_email = session["user_id"] if session and "user_id" in session else "Guest"
           
           updated_header_html = f'''
           <div class="app-header">
               <img src="images/usiu-logo.png" alt="USIU Logo" class="logo-dashboard" />
               <div class="header-controls">
                   <button class="theme-toggle" aria-label="Toggle theme"></button>
                   <div class="logout-icon-container">
                       <span class="user-email">{user_email}</span>
                       <div class="logout-icon" onclick="document.getElementById('logout-btn').click();">
                           <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
                               <path d="M5 5h7V3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h7v-2H5V5zm16 7l-4-4v3H9v2h8v3l4-4z" fill="white"/>
                           </svg>
                           <span class="tooltip">Logout</span>
                       </div>
                   </div>
               </div>
           </div>
           <div class="content-area"></div>

           <script>
               setTimeout(function() {{
                   if (typeof startSessionMonitoring === 'function') {{
                       startSessionMonitoring('{session_id_value}');
                   }}
                   
                   if (typeof adjustChatInterfaceHeights === 'function') {{
                       adjustChatInterfaceHeights();
                   }}
               }}, 1000);
           </script>
           '''
           
           update_session_activity(session_id_value)
           
           # Log login event
           wandb_tracker = get_service("wandb_tracker")
           if wandb_tracker:
               try:
                   wandb_tracker.log_system_metrics({
                       "login/success": 1,
                       "login/user": user_email
                   })
               except Exception as e:
                   print(f"Failed to log login event to W&B: {e}")
           
           return [
               gr.update(visible=False),
               gr.update(visible=False, elem_classes="chat-container pre-animation"),
               gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
               gr.update(visible=True, elem_classes="chat-container animate-fadeInRight"),
               gr.update(visible=False, elem_classes="container floating-card dashboard-card pre-animation"),
               user_email,
               session_id_value,
               gr.update(visible=True),
               updated_header_html
           ]
       
       proceed_btn.click(
           proceed_to_study,
           inputs=[session_id],
           outputs=[
               dashboard_container, 
               general_container, 
               login_container, 
               study_container,
               analytics_container,
               current_user,
               session_id_for_study,
               logout_component,
               header_component
           ]
       )
       
       # Enhanced logout
       def enhanced_logout(session_id_value):
           end_session(session_id_value)
           
           # Log logout event
           wandb_tracker = get_service("wandb_tracker")
           if wandb_tracker:
               try:
                   session = get_session(session_id_value)
                   user_email = session.get("user_id", "anonymous") if session else "anonymous"
                   
                   wandb_tracker.log_system_metrics({
                       "logout/event": 1,
                       "logout/user": user_email
                   })
               except Exception as e:
                   print(f"Failed to log logout event to W&B: {e}")
           
           original_header_html = '''
           <div class="app-header">
               <img src="images/usiu-logo.png" alt="USIU Logo" class="logo-dashboard" />
               <div class="header-controls">
                   <button class="theme-toggle" aria-label="Toggle theme"></button>
               </div>
           </div>
           <div class="content-area"></div>
           '''
           
           return [
               gr.update(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInLeft"),
               gr.update(visible=False, elem_classes="chat-container pre-animation"),
               gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
               gr.update(visible=False, elem_classes="chat-container pre-animation"),
               gr.update(visible=False, elem_classes="container floating-card dashboard-card pre-animation"),
               "",  # Clear user_id_input
               "",  # Clear password_input
               "",  # Clear login_msg
               "",  # Clear user_id_error
               "",  # Clear password_error
               gr.update(visible=True),  # Show login button
               gr.update(visible=False),  # Hide proceed button
               gr.update(visible=False),  # Hide logout component
               original_header_html  # Reset header
           ]
       
       logout_btn.click(
           enhanced_logout,
           inputs=[session_id_for_study],
           outputs=[
               dashboard_container, 
               general_container, 
               login_container, 
               study_container,
               analytics_container,
               user_id_input,
               password_input,
               login_msg,
               user_id_error,
               password_error,
               login_btn,
               proceed_btn,
               logout_component,
               header_component
           ]
       )
   
   return dashboard.queue()