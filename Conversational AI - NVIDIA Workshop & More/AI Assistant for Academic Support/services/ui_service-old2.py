# services/ui_service.py

import re
import os
import time
import json
import openai
import anthropic
import gradio as gr
import threading
import concurrent.futures
import asyncio
from typing import List, Dict, Any, Tuple, Optional, Generator, Union
from hume.legacy import HumeVoiceClient, MicrophoneInterface, VoiceConfig

from configs.config import GPT4O_MODEL, HUMEAI_API_KEY, HUMEAI_CONFIG_ID
from services.auth_service import (
    authenticate, create_session, get_session, update_session_activity, 
    end_session, is_session_active, get_session_remaining_time, should_show_warning,
    INACTIVITY_TIMEOUT, WARNING_TIMEOUT
)
from services.file_service import FileProcessor
from api_gateway.gateway import route_request

claude_client = anthropic.Anthropic()

# Will be set when dashboard_ui is called (during runtime)
GLOBAL_RETRIEVER = None


def custom_css():
    css = """
    /* Professional custom CSS with transitions, hover effects, and responsive design */
    body { 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        background-color: #f8f9fa; 
        margin: 0; 
        padding: 0;
        width: 100%;
        overflow-x: hidden; /* Prevent horizontal scrolling */
    }
    h1, h2, h3 { 
        text-align: center; 
        color: #495057;
    }
    .gr-button:not(.secondary-button):not([aria-label="Clear"]):not([aria-label="Retry"]):not([aria-label="Undo"]):not(.chat-buttons button) { 
        transition: background-color 0.3s ease, transform 0.3s ease; 
        border-radius: 4px;
        /* USIU-Africa theme color for buttons */
        background-color: #1F2E8C !important;
        color: white !important;
    }
    .gr-button:not(.secondary-button):not([aria-label="Clear"]):not([aria-label="Retry"]):not([aria-label="Undo"]):not(.chat-buttons button):hover { 
        background-color: #000066 !important; 
        color: #fff !important; 
        transform: scale(1.03);
    }
    .container { 
        transition: opacity 0.5s ease-in-out;
        padding: 4px;
    }

    /* Style the "+ New chat" button to match USIU-Africa theme */
    button.primary, .gradio-container button.gr-button.gr-button-lg.primary {
        background-color: #1F2E8C !important; /* USIU-Africa navy blue */
        color: white !important;
        border: none !important;
        transition: background-color 0.3s ease, transform 0.2s ease !important;
    }

    /* Styling the submit button and the file upload button accordion button */
    button.submit-button.svelte-173056l svg g#SVGRepo_iconCarrier,
    button.label-wrap.svelte-1w6vloh span {
        color: #1F2E8C;
    }

    button.secondary-button:hover, .gradio-container button.gr-button.gr-button-lg.secondary-button:hover {
        background-color: #000066 !important; /* Slightly darker on hover */
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }

    /* ENHANCED: All chat action buttons should have the USIU-Africa theme */
    .chat-buttons button, .gradio-container .chat-buttons button {
        background-color: #1F2E8C !important;
        color: white !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }

    .chat-buttons button:hover, .gradio-container .chat-buttons button:hover {
        background-color: #000066 !important;
        transform: translateY(-2px) !important;
    }

    /* Glassmorphism effect for floating cards */
    .floating-card {
        background: rgba(255, 255, 255, 0.85);
        border-radius: 12px;
        box-shadow: 
            0 10px 25px rgba(0,0,0,0.08),
            0 6px 10px rgba(0,0,0,0.12),
            0 3px 3px rgba(0,0,0,0.15);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        padding: 25px;
        margin: 15px auto; /* Reduced margin */
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.25);
        width: 95%; /* Increased width */
        max-width: 98%; /* Increased max-width */
    }

    # .floating-card:hover {
    #     box-shadow: 
    #         0 15px 30px rgba(0,0,0,0.15),
    #         0 10px 10px rgba(0,0,0,0.18);
    #     transform: translateY(-5px);
    #     background: rgba(255, 255, 255, 0.9);
    # }

    div.html-container {
        padding: 0px;
    }

    /* ENHANCED: Chat UI container with increased dimensions and floating card effect */
    .chat-container {
        max-width: 1200px; /* INCREASED: from 1000px */
        width: 98%;
        margin: auto auto 20px auto !important; /* INCREASED top margin to give space from header */
        opacity: 0;
        transform: translateY(20px);
        animation: fadeInUp 0.7s forwards;
    }

    div.wrapper.svelte-g3p8na label {
        color: #1F2E8C;
    }

    /* ENHANCED: Increase chat window height/width & add floating + inset 3D effect */
    .chatbot-container, .gradio-container .chat {
        height: 600px !important;                /* FIXED HEIGHT SETTING */
        max-height: 1500px !important;          /* INCREASED: from 1000px */
        width: 100% !important;                /* INCREASED: from 98% */
        margin: 0 auto !important;
        background: rgba(255, 255, 255, 0.85) !important;
        border-radius: 16px !important;
        box-shadow:
            /* existing floating "lift" */
            0 15px 35px rgba(0, 0, 0, 0.10),
            0 10px 15px rgba(0, 0, 0, 0.07),
            0 5px 10px rgba(0, 0, 0, 0.05),
            /* new inset 3D "pressed‑in" effect */
            inset 0 4px 12px rgba(0, 0, 0, 0.12),
            inset 0 -4px 12px rgba(0, 0, 0, 0.06) !important;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-top: 3px solid #1F2E8C !important;
        overflow: hidden !important;
    }

    /* FIXED: Chat interfaces and window heights */
    .chat-interface-container {
        min-height: 600px !important;
        height: 75vh !important;
    }
    
    .chat-interface-container .chat, 
    .chat-interface-container .chatbot-container {
        min-height: 600px !important;
        height: 75vh !important;
    }
    
    /* Fix chat window scrollable height */
    .chat-interface-container .chat-window,
    .chat-interface-container .chat-window-content {
        min-height: 450px !important;
        height: calc(75vh - 150px) !important;
        overflow-y: auto !important;
    }

    .bubble-wrap {
        position: relative;
        box-shadow:
            inset 0 4px 12px rgba(0, 0, 0, 0.12),
            inset 0 -4px 12px rgba(0, 0, 0, 0.06);
    }

    /* Ensure chat message container has enough height */
    .gradio-container .chat-window, .gradio-container .chat-window-content {
        height: calc(90vh - 120px) !important; /* Adjust height to accommodate header and input area */
        overflow-y: auto !important;
    }

    /* Add hover effect to chat container for professional floating appearance */
    .chatbot-container:hover, .gradio-container .chat:hover {
        box-shadow: 
            0 20px 40px rgba(0,0,0,0.12),
            0 15px 20px rgba(0,0,0,0.08),
            0 8px 15px rgba(0,0,0,0.06) !important;
        transform: translateY(-8px) !important;
        # cursor: pointer;
        pointer-events: auto !important;
    }
    
    /* Make Gradio container take full width on mobile */
    .gradio-container {
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Login form styling with responsiveness */
    .login-form-container {
        width: 98% !important; /* Increased width for mobile */
        max-width: 500px !important;
        margin: 30px auto 30px auto !important; /* Increased top margin to give space from header */
        background: rgba(255, 255, 255, 0.88) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-top: 3px solid #1F2E8C !important;
        padding: 20px 15px !important; /* Added horizontal padding */
    }

    /* Dashboard container styling with responsiveness */
    .dashboard-card {
        width: 98% !important; /* Take almost full width on mobile */
        max-width: 700px !important;
        margin: 30px auto 20px auto !important; /* Increased top margin to give space from header */
        background: rgba(255, 255, 255, 0.88) !important;
        backdrop-filter: blur(12px) !important;
        height: auto !important;
        min-height: 500px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-top: 3px solid #1F2E8C !important;
        opacity: 0;
        animation: dashboardFadeIn 1.5s forwards ease-in-out;
        padding: 20px 10px !important; /* Reduced horizontal padding */
    }

    /* A subtle gradient background to the cards */
    .dashboard-card, .login-form-container {
        background: linear-gradient(
            135deg, 
            rgba(255, 255, 255, 0.9) 0%, 
            rgba(255, 255, 255, 0.8) 100%
        ) !important;
    }

    /* ENHANCED: App header with USIU-Africa theme */
    .app-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 70px;
        background-color: #1F2E8C !important; /* USIU-Africa navy blue */
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        z-index: 1000;
        padding: 0 15px;
        color: white !important;
    }

    /* Logo container styling with responsive adjustments */
    .logo-container {
        text-align: center;
        margin-bottom: 25px;
        position: relative;
        width: 100%;
    }

    .logo {
        max-height: 80px;
        max-width: 90%; /* Increased max-width */
        margin: 0 auto;
        display: block;
    }

    .logo-dashboard {
        max-height: 60px;
        max-width: 180px;
        margin-left: 15px;
        color: white;
    }

    /* Add padding to account for fixed header */
    .content-area {
        padding-top: 60px;
    }

    .with-logo {
        margin-top: 10px;
    }

    /* Professional Logout Icon Styling */
    .logout-icon-container {
        position: absolute;
        right: 15px;
        top: 50%;
        transform: translateY(-50%);
        display: flex;
        align-items: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .user-email {
        margin-right: 8px;
        font-size: 14px;
        color: white;
        font-weight: 500;
    }
    
    .logout-icon {
        position: relative;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: all 0.3s ease;
    }
    
    .logout-icon svg {
        transition: transform 0.3s ease;
        fill: white; /* Make icon white */
    }
    
    .logout-icon:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
    
    .logout-icon:hover svg {
        transform: scale(1.1);
    }
    
    /* Tooltip styling */
    .logout-icon .tooltip {
        position: absolute;
        bottom: -30px;
        left: 50%;
        transform: translateX(-50%);
        background-color: #333;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 12px;
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.3s, visibility 0.3s;
        white-space: nowrap;
    }
    
    .logout-icon .tooltip:after {
        content: '';
        position: absolute;
        top: -5px;
        left: 50%;
        transform: translateX(-50%);
        border-width: 5px;
        border-style: solid;
        border-color: transparent transparent #333 transparent;
    }
    
    .logout-icon:hover .tooltip {
        opacity: 1;
        visibility: visible;
    }

    /* Inactivity warning modal */
    .inactive-warning {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: white;
        border: 1px solid #ccc;
        border-radius: 8px;
        padding: 25px;
        z-index: 1001;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        max-width: 400px;
        width: 90%;
        text-align: center;
        display: none;
        animation: fadeIn 0.3s ease;
    }

    .inactive-warning h3 {
        margin-top: 0;
        color: #c62828;
        font-size: 20px;
    }

    .inactive-warning p {
        font-size: 16px;
        margin: 15px 0;
    }

    .inactive-warning #countdown {
        font-weight: bold;
        color: #c62828;
    }

    .inactive-warning button {
        margin-top: 20px;
        background-color: #1F2E8C;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
        transition: background-color 0.2s;
    }

    .inactive-warning button:hover {
        background-color: #000066;
    }

    .overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0,0,0,0.6);
        z-index: 1000;
        display: none;
        animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* Dashboard menu buttons styling with responsiveness */
    .dashboard-menu {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 60vh;
        gap: 8px;
        opacity: 0;
        animation: menuFadeIn 3s forwards ease-in-out;
        animation-delay: 0.5s;
        padding: 15px 0; /* Reduced padding */
        width: 100%; /* Full width */
    }

    .menu-button {
        width: 95% !important;               /* Increased width for mobile */
        max-width: 300px !important;
        height: auto !important;
        min-height: 60px !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        margin: 6px auto !important;         /* Reduced margin */
        border-radius: 8px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        
        /* Sliding gradient background */
        background-image: linear-gradient(135deg, #1F2E8C 0%, #FCC707 100%) !important;
        background-size: 200% 200% !important;
        background-position: 0% 50% !important;
        
        color: white !important;
        opacity: 0;
        padding: 10px 15px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        word-wrap: break-word !important;
        
        animation: buttonsFadeIn 0.5s forwards ease-in-out;
        animation-delay: calc(var(--button-index, 0) * 0.3s + 1s);
        
        transition:
        transform 0.3s ease,
        box-shadow 0.3s ease !important,
        background-position 0.5s ease !important;
    }

    .menu-button:hover {
        transform: scale(1.02) !important;
        background-position: 100% 50% !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }


    /* ENHANCED: Style the chat message containers */
    .message-wrap {
        border-radius: 10px !important;
        margin: 12px 0 !important;
        transition: all 0.3s ease !important;
    }

    .message-wrap:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05) !important;
    }

    /* Style user messages */
    .user-message {
        background-color: #f0f7ff !important; 
        border-left: 3px solid #1F2E8C !important;
    }

    /* Style bot messages */
    .bot-message {
        background-color: #f9f9f9 !important;
        border-left: 3px solid #505050 !important;
    }

    /* Style the chat input area */
    .chat-input-container {
        padding: 15px !important;
        background: rgba(255, 255, 255, 0.9) !important;
        border-top: 1px solid rgba(0, 0, 128, 0.2) !important;
        border-radius: 0 0 16px 16px !important;
    }

    .chat-input {
        border-radius: 25px !important;
        border: 2px solid rgba(0, 0, 128, 0.3) !important;
        padding: 12px 20px !important;
        transition: all 0.3s ease !important;
    }

    .chat-input:focus {
        border-color: #1F2E8C !important;
        box-shadow: 0 0 0 3px rgba(0, 0, 128, 0.2) !important;
    }

    /* 3D Loader CSS with responsive sizing */
    .loader {
        width: 40px; /* Reduced size */
        height: 40px; /* Reduced size */
        perspective: 100px;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 9999;
        display: none;
    }
    .cube {
        width: 100%;
        height: 100%;
        background: #1F2E8C;
        transform: rotateX(0deg) rotateY(0deg);
        animation: spinCube 1.5s infinite ease-in-out;
    }
    @keyframes spinCube {
        0%   { transform: rotateX(0deg) rotateY(0deg); }
        25%  { transform: rotateX(90deg) rotateY(0deg); }
        50%  { transform: rotateX(90deg) rotateY(90deg); }
        75%  { transform: rotateX(0deg) rotateY(90deg); }
        100% { transform: rotateX(0deg) rotateY(0deg); }
    }
    
    /* Dashboard specific fade-in animations */
    @keyframes dashboardFadeIn {
        0% {
            opacity: 0;
            transform: translateY(30px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes menuFadeIn {
        0% {
            opacity: 0;
            transform: scale(0.95);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes buttonsFadeIn {
        0% {
            opacity: 0;
            transform: translateX(-15px);
        }
        100% {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* Adding transition effects for interfaces */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes fadeInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* Container animation classes that can be dynamically applied */
    .animate-fadeInUp {
        animation: fadeInUp 0.7s forwards;
    }

    .animate-fadeInRight {
        animation: fadeInRight 0.7s forwards;
    }

    .animate-fadeInLeft {
        animation: fadeInLeft 0.7s forwards;
    }

    /* Initial state for containers to be animated */
    .pre-animation {
        opacity: 0;
    }

    /* Specifically target Gradio elements to make them more mobile-friendly */
    .gradio-container {
        margin-left: 0 !important;
        margin-right: 0 !important;
    }
    
    /* Adjust textbox and button widths for mobile */
    .gr-textbox {
        width: 100% !important;
    }
    
    .gr-button-primary {
        width: 100% !important;
        margin: 5px 0 !important;
    }
    
    /* Make all interface elements take more width on mobile */
    .interface-elements {
        width: 98% !important;
        max-width: 100% !important;
        margin: 0 auto !important;
    }
    
    /* Fix padding for form elements */
    input, select, textarea, button {
        box-sizing: border-box !important;
    }

    /* Ensure minimum touch target size for all clickable elements 
       BUT exclude accordion, file input, and chat action buttons */
    button:not([aria-label="Clear"]):not([aria-label="Retry"]):not([aria-label="Undo"]):not([aria-label="Edit"]):not(.chat-buttons button), 
    .gr-button:not(.file-upload .gr-button button):not(.chat-buttons .gr-button), 
    a,
    input[type="submit"], 
    input[type="button"] {
        min-height: 44px !important; /* Apple's recommended minimum touch target size */
        min-width: 44px !important;
    }
    
    /* Remove any unnecessary margins from Gradio components */
    .gradio-container .gr-form > *, .gradio-container .gr-group > * {
        margin-bottom: 8px !important;
    }
    
    /* Ensure Gradio container does not exceed viewport width and height */
    div#component-0, div#component-1, div#component-2, div#component-3, div#component-4, div#component-5,
    div#component-6, div#component-7, div#component-8, div#component-9, div#component-10 {
        max-width: 100vw !important;
        overflow-x: hidden !important;
    }

    /* FIXED: Direct height setting for chat components by ID
       But also use classes for more flexible targeting */
    #general-chat-interface, #study-chat-interface {
        min-height: 600px !important;
        height: 75vh !important;
    }

    /* File upload accordion width fix */
    .additional-inputs-accordion {
        width: 86% !important;
        max-width: 1100px !important;
        margin: 0 auto !important;
    }

    /* File input width fix */
    .additional-inputs-accordion .file-container {
        width: 100% !important;
        max-width: 100% !important;
    }

    /* Voice chat button styling */
    .mic-button {
        position: absolute;
        right: 70px;
        bottom: 18px;
        width: 40px !important;
        height: 40px !important;
        border-radius: 50% !important;
        background-color: #1F2E8C !important;
        color: white !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        border: none !important;
        z-index: 100;
        padding: 0 !important;
        min-width: 40px !important;
    }

    .mic-button:hover {
        transform: scale(1.1) !important;
        background-color: #000066 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }

    .mic-button svg {
        width: 20px;
        height: 20px;
        fill: white;
    }

    /* Voice chat modal styling */
    .voice-chat-modal {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 400px;
        max-width: 90vw;
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
        z-index: 2000;
        padding: 24px;
        display: none;
        animation: fadeIn 0.3s ease;
    }

    .voice-chat-modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }

    .voice-chat-modal-title {
        font-size: 18px;
        font-weight: 600;
        color: #1F2E8C;
    }

    .voice-chat-modal-close {
        background: none;
        border: none;
        color: #666;
        font-size: 20px;
        cursor: pointer;
        padding: 5px;
        border-radius: 50%;
        transition: all 0.2s ease;
    }

    .voice-chat-modal-close:hover {
        background-color: #f0f0f0;
    }

    .voice-visualizer {
        height: 120px;
        width: 100%;
        background-color: #f8f9fa;
        border-radius: 8px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    .visualization-bars {
        display: flex;
        align-items: flex-end;
        height: 100px;
        width: 100%;
        padding: 0 20px;
    }

    .bar {
        background-color: #1F2E8C;
        margin: 0 2px;
        width: 5px;
        height: 10px;
        border-radius: 2px;
        animation: barAnimation 0.5s infinite alternate;
    }

    @keyframes barAnimation {
        0% {
            height: 10px;
        }
        100% {
            height: var(--bar-height, 50px);
        }
    }

    .voice-chat-buttons {
        display: flex;
        justify-content: center;
        gap: 16px;
    }

    .voice-chat-button {
        padding: 10px 20px;
        border-radius: 6px;
        border: none;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .stop-button {
        background-color: #c62828;
        color: white;
    }

    .pause-button {
        background-color: #ffab00;
        color: white;
    }

    .status-indicator {
        text-align: center;
        margin-top: 15px;
        font-size: 14px;
        color: #666;
    }

    /* Media Queries for better responsiveness */
    @media screen and (max-width: 768px) {
        body {
            padding: 0 !important; /* Remove body padding on mobile */
        }
        
        .dashboard-card {
            width: 100% !important; /* Full width */
            padding: 15px 8px !important; /* Reduced padding */
            margin: 60px auto 10px auto !important; /* Adjusted margin for mobile */
            border-radius: 0 !important; /* Optional: Remove border radius for full-width look */
        }
        
        .login-form-container {
            width: 100% !important; /* Full width */
            padding: 15px 10px !important; /* Reduced padding */
            margin: 60px auto 10px auto !important; /* Adjusted margin for mobile */
            border-radius: 0 !important; /* Optional: Remove border radius for full-width look */
        }
        
        .menu-button {
            width: 98% !important; /* Almost full width */
            font-size: 14px !important;
            min-height: 50px !important;
        }
        
        .logo-dashboard {
            max-height: 40px;
            margin-left: 5px;
        }
        
        h1 {
            font-size: 1.5rem !important;
            margin-top: 10px !important;
            margin-bottom: 15px !important;
        }
        
        h2 {
            font-size: 1.3rem !important;
            margin-top: 8px !important;
            margin-bottom: 12px !important;
        }
        
        h3 {
            font-size: 1.1rem !important;
            margin-top: 6px !important;
            margin-bottom: 10px !important;
        }
        
        /* Make chat interface take full width with adjusted margin */
        .chat-container {
            width: 100% !important;
            margin: 60px auto 0 auto !important;
            padding: 0 5px !important;
        }
        
        /* Adjust Gradio containers */
        .gradio-container {
            padding: 0 !important;
        }
        
        /* Adjust logout icon for mobile */
        .user-email {
            font-size: 12px;
            max-width: 120px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .logout-icon {
            width: 32px;
            height: 32px;
        }
        
        .logout-icon svg {
            width: 20px;
            height: 20px;
        }
        
        /* Adjust fixed header for mobile */
        .app-header {
            height: 60px;
            padding: 0 10px;
        }
        
        /* Adjust content padding for mobile header */
        .content-area {
            padding-top: 60px;
        }
        
        /* Adjust chat container height for mobile */
        .chatbot-container, .gradio-container .chat {
            height: 85vh !important; /* Slightly reduced height on mobile */
        }
        
        .gradio-container .chat-window, .gradio-container .chat-window-content {
            height: calc(85vh - 110px) !important; /* Adjusted for mobile */
        }
        
        /* FIXED: Adjust specific interfaces on mobile */
        #general-chat-interface, #study-chat-interface {
            min-height: 500px !important;
            height: 70vh !important;
        }
        
        /* Voice chat adjustments for mobile */
        .voice-chat-modal {
            width: 320px;
            padding: 15px;
        }
        
        .mic-button {
            right: 55px;
            bottom: 16px;
            width: 36px !important;
            height: 36px !important;
            min-width: 36px !important;
        }
        
        .voice-visualizer {
            height: 80px;
        }
    }

    @media screen and (max-width: 480px) {
        .dashboard-card {
            padding: 10px 5px !important; /* Further reduced padding */
            margin: 30px auto 0 auto !important; /* Adjusted for very small screens */
            border-radius: 0 !important; /* Remove border radius */
            width: 100% !important; /* Full width */
        }
        
        .login-form-container {
            padding: 10px 5px !important; /* Further reduced padding */
            margin: 10px auto 0 auto !important; /* Adjusted for very small screens */
            border-radius: 0 !important; /* Remove border radius */
            width: 100% !important; /* Full width */
        }
        
        .menu-button {
            font-size: 13px !important;
            min-height: 45px !important;
            margin: 5px auto !important;
            width: 100% !important; /* Full width */
            border-radius: 6px !important; /* Slightly reduced border radius */
        }
        
        .logo-dashboard {
            max-height: 35px;
        }
        
        /* Adjust spacing in forms for mobile */
        input, select, textarea {
            margin-bottom: 8px !important;
            padding: 8px !important;
            width: 100% !important;
        }
        
        /* Reduce padding and margins for all content */
        .floating-card, .gr-box, .gr-panel {
            padding: 10px 5px !important;
            margin: 5px 0 !important;
            width: 100% !important;
        }
        
        /* Full width for all UI components */
        .gr-form, .gr-input, .gr-button, .gr-box {
            width: 100% !important;
            margin-left: 0 !important;
            margin-right: 0 !important;
        }
        
        /* Hide user email on small screens */
        .user-email {
            display: none; /* Hide email on very small screens */
        }
        
        /* Adjust chat container for smaller screens */
        .chatbot-container, .gradio-container .chat {
            height: 80vh !important; /* Slightly reduce height on small screens */
            border-radius: 10px !important; /* Smaller border radius */
        }
        
        .chat-container {
            margin: 30px auto 0 auto !important; /* Adjusted for very small screens */
        }
        
        .gradio-container .chat-window, .gradio-container .chat-window-content {
            height: calc(80vh - 100px) !important; /* Adjusted for very small screens */
        }
        
        /* Voice chat adjustments for very small screens */
        .voice-chat-modal {
            width: 280px;
            padding: 10px;
        }
        
        .voice-chat-modal-title {
            font-size: 16px;
        }
        
        .mic-button {
            right: 45px;
            bottom: 15px;
            width: 32px !important;
            height: 32px !important;
            min-width: 32px !important;
        }
        
        .mic-button svg {
            width: 16px;
            height: 16px;
        }
    }

    /* Additional responsive handling for extreme screen sizes */
    @media screen and (max-width: 320px) {
        /* For very small screens like older iPhones */
        .menu-button {
            font-size: 11px !important;
            min-height: 40px !important;
            padding: 6px 5px !important;
        }
        
        .dashboard-card {
            padding: 5px 3px !important;
            margin: 6px auto 0 auto !important; /* Adjusted for extremely small screens */
        }
        
        .login-form-container {
            margin: 6px auto 0 auto !important; /* Adjusted for extremely small screens */
        }
        
        .chat-container {
            margin: 6px auto 0 auto !important; /* Adjusted for extremely small screens */
        }
        
        h1 {
            font-size: 1.3rem !important;
        }
        
        h2 {
            font-size: 1.1rem !important;
        }
        
        h3 {
            font-size: 1rem !important;
        }
        
        /* Adjust chat container height for very small screens */
        .chatbot-container, .gradio-container .chat {
            height: 75vh !important;
        }
        
        /* Voice chat adjustments for extremely small screens */
        .voice-chat-modal {
            width: 250px;
            padding: 8px;
        }
        
        .voice-visualizer {
            height: 60px;
        }
        
        .voice-chat-button {
            padding: 8px 12px;
            font-size: 12px;
        }
    }

    @media screen and (min-width: 1600px) {
        /* For very large screens */
        .dashboard-card {
            max-width: 1000px !important;
            margin: 70px auto 30px auto !important; /* Increased margin for large screens */
        }
        
        .login-form-container {
            margin: 70px auto 30px auto !important; /* Increased margin for large screens */
        }
        
        .menu-button {
            max-width: 400px !important;
        }
        
        /* ENHANCED: Make chat container even larger on big screens */
        .chat-container {
            max-width: 1400px !important;
            margin: 100px auto 30px auto !important; /* Increased margin for large screens */
        }
        
        .chatbot-container, .gradio-container .chat {
            max-height: 1200px !important;
            height: 92vh !important; /* Increased height for large screens */
        }
        
        .gradio-container .chat-window, .gradio-container .chat-window-content {
            height: calc(92vh - 130px) !important; /* Adjusted for large screens */
        }
        
        /* FIXED: Larger interfaces on big screens */
        #general-chat-interface, #study-chat-interface {
            min-height: 800px !important;
            height: 85vh !important;
        }
    }

    /* For landscape orientation on mobile */
    @media screen and (max-height: 500px) and (orientation: landscape) {
        .dashboard-menu {
            min-height: auto;
            padding: 5px 0;
        }
        
        .dashboard-card {
            min-height: 300px !important;
            margin: 8px auto 10px auto !important; /* Adjusted for landscape */
        }
        
        .login-form-container {
            margin: 8px auto 10px auto !important; /* Adjusted for landscape */
        }
        
        .chat-container {
            margin: 8px auto 10px auto !important; /* Adjusted for landscape */
        }
        
        .menu-button {
            min-height: 40px !important;
            margin: 4px auto !important;
        }
        
        /* Adjust header height for landscape */
        .app-header {
            height: 50px;
        }
        
        /* Adjust content padding for landscape header */
        .content-area {
            padding-top: 50px;
        }
        
        /* Adjust chat container height for landscape */
        .chatbot-container, .gradio-container .chat {
            height: 80vh !important;
        }
        
        .gradio-container .chat-window, .gradio-container .chat-window-content {
            height: calc(70vh - 80px) !important;
        }
    }
    
    /* Fixed positions for mobile views */
    .fixed-top {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
    }
    
    .fixed-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 1000;
    }

    .message-row.bubble.user-row.svelte-yaaj3 .flex-wrap.svelte-yaaj3 .user,
    .message-row.bubble.bot-row.svelte-yaaj3 .flex-wrap.svelte-yaaj3 .bot {
        background-color: #FAFAFA !important;
        border-radius: 16px 16px 0 16px !important;
        box-shadow:
            0 8px 16px rgba(0,0,0,0.10) !important,     /* big, soft shadow */
            0 4px  8px rgba(0,0,0,0.08) !important;     /* smaller, darker falloff */
        pointer-events: auto !important;
    }

    .message-row.bubble.bot-row.svelte-yaaj3 .flex-wrap.svelte-yaaj3 .bot {
        background-color: #F7FCFF !important; /* #F7F9FF, FDFEFF */
        border-radius: 16px 16px 16px 0 !important;
    }

    .message-row {
        max-width: 86% !important;
    }
    """
    return css

# ----------------- Session Management Functions -----------------
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


# ----------------- Summarization Helper -----------------
def summarize_context(text: str, summarization_model: str = GPT4O_MODEL) -> str:
    """
    Summarize the given text concisely while preserving key details.
    Uses the provided summarization model (e.g., GPT-4o or llama-3-8b).
    """
    summarization_prompt = (
        "Summarize the following text concisely while preserving the essential details:\n\n"
        f"{text}\n\nSummary:"
    )
    try:
        # Non-streaming call to get the summary
        response = openai.chat.completions.create(
            model=summarization_model,
            messages=[{"role": "system", "content": summarization_prompt}],
            max_tokens=150,
            temperature=0.5,
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print("Summarization failed:", e)
        # Fallback: return a truncated version if summarization fails
        return text[:500]

# ----------------- Notification Helpers -----------------

def show_success(message: str, duration: float = 8, visible: bool = True, title: str = "Success") -> None:
    """Display a success notification"""
    styled_message = (
        f'<span style="color: #2e7d32; background-color: #c8e6c9; padding: 10px; '
        f'border-radius: 4px; display: block;">{message}</span>'
    )
    gr.Success(styled_message, duration=duration, visible=visible, title=title)
    # Add a small delay to help the modal appear
    time.sleep(0.1)

def show_error(message: str, duration: float = 10, visible: bool = True, title: str = "Error") -> None:
    """Display an error notification"""
    styled_message = (
        f'<span style="color: #c62828; background-color: #ffcdd2; padding: 10px; '
        f'border-radius: 4px; display: block;">{message}</span>'
    )
    gr.Error(styled_message, duration=duration, visible=visible, title=title)
    # Add a small delay to help the modal appear
    time.sleep(0.1)

# ----------------- Voice Chat Implementation -----------------

def voice_chat_html():
    """Create HTML for voice chat modal and microphone button"""
    modal_html = """
    <div class="voice-chat-modal" id="voice-chat-modal">
        <div class="voice-chat-modal-header">
            <div class="voice-chat-modal-title">Voice Conversation</div>
            <button class="voice-chat-modal-close" id="voice-chat-modal-close">&times;</button>
        </div>
        <div class="voice-visualizer" id="voice-visualizer">
            <div class="visualization-bars" id="visualization-bars"></div>
        </div>
        <div class="voice-chat-buttons">
            <button class="voice-chat-button stop-button" id="stop-voice-chat">Stop Conversation</button>
        </div>
        <div class="status-indicator" id="voice-status">Listening...</div>
    </div>
    """
    
    mic_button_html = """
    <button class="mic-button" id="mic-button">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" fill="white"/>
        </svg>
    </button>
    """
    
    return modal_html, mic_button_html

def voice_chat_js():
    """Create JavaScript for voice chat functionality"""
    return """
    <script>
    // Will be initialized after DOM is loaded
    let voiceChatActive = false;
    let humeVoiceSocket = null;
    let currentChatComponent = null;
    
    document.addEventListener('DOMContentLoaded', function() {
        // Create the voice chat modal
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = `
            <div class="voice-chat-modal" id="voice-chat-modal">
                <div class="voice-chat-modal-header">
                    <div class="voice-chat-modal-title">Voice Conversation</div>
                    <button class="voice-chat-modal-close" id="voice-chat-modal-close">&times;</button>
                </div>
                <div class="voice-visualizer" id="voice-visualizer">
                    <div class="visualization-bars" id="visualization-bars"></div>
                </div>
                <div class="voice-chat-buttons">
                    <button class="voice-chat-button stop-button" id="stop-voice-chat">Stop Conversation</button>
                </div>
                <div class="status-indicator" id="voice-status">Listening...</div>
            </div>
        `;
        document.body.appendChild(modalContainer);
        
        // Create the voice visualization bars
        const barsContainer = document.getElementById('visualization-bars');
        if (barsContainer) {
            for (let i = 0; i < 30; i++) {
                const bar = document.createElement('div');
                bar.className = 'bar';
                bar.style.setProperty('--bar-height', Math.floor(Math.random() * 80 + 10) + 'px');
                bar.style.animationDelay = (i * 0.05) + 's';
                barsContainer.appendChild(bar);
            }
        }
        
        // Add event listeners for modal controls
        const closeButton = document.getElementById('voice-chat-modal-close');
        if (closeButton) {
            closeButton.addEventListener('click', stopVoiceChat);
        }
        
        const stopButton = document.getElementById('stop-voice-chat');
        if (stopButton) {
            stopButton.addEventListener('click', stopVoiceChat);
        }
        
        // Observe DOM changes to attach mic buttons to chat interfaces
        const observer = new MutationObserver(function(mutations) {
            attachMicButtons();
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Initial attempt to attach buttons
        setTimeout(attachMicButtons, 1000);
    });
    
    // Function to attach mic buttons to all chat interfaces
    function attachMicButtons() {
        // Find all chat interfaces that don't already have a mic button
        const chatInterfaces = document.querySelectorAll('.chat-interface-container');
        
        chatInterfaces.forEach(function(chat) {
            // Check if this chat already has a mic button
            if (!chat.querySelector('.mic-button')) {
                // Find the textbox within this chat
                const textbox = chat.querySelector('textarea');
                if (textbox) {
                    const textboxParent = textbox.parentElement;
                    
                    // Create mic button
                    const micButton = document.createElement('button');
                    micButton.className = 'mic-button';
                    micButton.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" fill="white"/>
                        </svg>
                    `;
                    
                    // Position the button relative to the textbox's parent
                    if (textboxParent && textboxParent.style) {
                        textboxParent.style.position = 'relative';
                        textboxParent.appendChild(micButton);
                        
                        // Add click handler to the mic button
                        micButton.addEventListener('click', function() {
                            startVoiceChat(chat);
                        });
                    }
                }
            }
        });
    }
    
    // Start voice conversation
    function startVoiceChat(chatElement) {
        if (voiceChatActive) return;
        
        voiceChatActive = true;
        currentChatComponent = chatElement;
        
        // Find the submit button and textbox in this chat
        const submitButton = chatElement.querySelector('button[type="submit"]') || 
                              chatElement.querySelector('button.submit-button') ||
                              chatElement.querySelector('button').find(btn => btn.textContent.includes('Submit') || btn.textContent.includes('Send'));
        
        const textbox = chatElement.querySelector('textarea');
        
        // Show the voice chat modal
        const modal = document.getElementById('voice-chat-modal');
        if (modal) {
            modal.style.display = 'block';
            
            // Update status
            const status = document.getElementById('voice-status');
            if (status) {
                status.textContent = 'Initializing voice connection...';
            }
            
            // Animate the visualization bars
            animateVoiceBars(true);
            
            // Here we would normally connect to Hume Voice API
            // Since we can't directly call Python from JavaScript, we'll simulate it
            setTimeout(function() {
                if (status) {
                    status.textContent = 'Listening... Speak now';
                }
                
                // Simulate receiving voice input after a few seconds
                setTimeout(function() {
                    if (voiceChatActive) {
                        const sampleQuestion = "What are the main campus resources available to students?";
                        
                        if (status) {
                            status.textContent = 'Processing: "' + sampleQuestion + '"';
                        }
                        
                        // Fill in the textbox with the transcript
                        if (textbox) {
                            textbox.value = sampleQuestion;
                            
                            // Trigger the submit button after a short delay
                            setTimeout(function() {
                                if (submitButton) {
                                    submitButton.click();
                                    
                                    if (status) {
                                        status.textContent = 'AI is responding...';
                                    }
                                    
                                    // Simulate AI response time
                                    setTimeout(function() {
                                        if (voiceChatActive) {
                                            if (status) {
                                                status.textContent = 'Response complete. Listening again...';
                                            }
                                        }
                                    }, 5000);
                                }
                            }, 1000);
                        }
                    }
                }, 3000);
            }, 2000);
        }
    }
    
    // Stop voice conversation
    function stopVoiceChat() {
        voiceChatActive = false;
        
        // Hide the modal
        const modal = document.getElementById('voice-chat-modal');
        if (modal) {
            modal.style.display = 'none';
        }
        
        // Stop the visualization animation
        animateVoiceBars(false);
        
        // Reset the current chat component
        currentChatComponent = null;
    }
    
    // Animate the voice visualization bars
    function animateVoiceBars(isActive) {
        const bars = document.querySelectorAll('.bar');
        if (bars) {
            bars.forEach(function(bar, index) {
                if (isActive) {
                    // Random height animation when active
                    setInterval(function() {
                        if (voiceChatActive) {
                            const height = Math.floor(Math.random() * 80 + 10);
                            bar.style.setProperty('--bar-height', height + 'px');
                        }
                    }, 500);
                } else {
                    // Reset to minimal height when inactive
                    bar.style.setProperty('--bar-height', '10px');
                }
            });
        }
    }
    </script>
    """

# ----------------- Login Form UI -----------------

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
        # Error message for invalid user ID
        user_id_error = gr.Markdown("", visible=True)
        
        password_input = gr.Textbox(
            placeholder="Enter your Password", 
            label="Password", 
            type="password"
        )
        # Error message for invalid password
        password_error = gr.Markdown("", visible=True)
        
        login_btn = gr.Button("Login")
        # Error message for invalid credentials
        login_msg = gr.Markdown("")
        proceed_btn = gr.Button("Proceed", visible=False)
        back_btn = gr.Button("Back to Dashboard")
        
        # Hidden field to store session ID
        session_id = gr.Textbox(visible=False)
    # Return the login form along with the necessary components in order.
    return login_form, user_id_input, user_id_error, password_input, password_error, login_btn, login_msg, proceed_btn, back_btn, session_id

# ----------------- Authentication Logic -----------------

def handle_login(user_id, password):
    """
    Validates login fields and the User ID (which must end with '@usiu.ac.ke').
    Returns appropriate error messages and updates UI components.
    """
    try:
        user_id = user_id.strip() if user_id else ""
        password = password.strip() if password else ""

        # Both fields empty:
        if user_id == "" and password == "":
            show_error("Please enter your User ID and Password.")
            return (
                "<span style='color:#c62828;'>Please enter your User ID and Password.</span>",
                "",   # No field-specific error for User ID.
                "",   # No field-specific error for Password.
                gr.update(visible=False),
                gr.update(visible=True),
                ""    # No session ID since login failed
            )
        # User ID is empty:
        elif user_id == "":
            show_error("User ID is required.")
            return (
                "", 
                "<span style='color:#c62828;'>User ID is required.</span>",
                "",
                gr.update(visible=False),
                gr.update(visible=True),
                ""    # No session ID since login failed
            )
        # Password is empty:
        elif password == "":
            show_error("Password is required.")
            return (
                "",
                "",
                "<span style='color:#c62828;'>Password is required.</span>",
                gr.update(visible=False),
                gr.update(visible=True),
                ""    # No session ID since login failed
            )
        else:
            # Validate the User ID: must end with "@usiu.ac.ke"
            email_regex = r'^[\w\.-]+@usiu\.ac\.ke$'
            if not re.match(email_regex, user_id):
                show_error("User ID must be a valid \"@usiu.ac.ke\" email address.")
                return (
                    "",
                    "<span style='color:#c62828;'>User ID must be a valid @usiu.ac.ke email address.</span>",
                    "",
                    gr.update(visible=False),
                    gr.update(visible=True),
                    ""    # No session ID since login failed
                )
            # Attempt authentication.
            if authenticate(user_id, password):
                # Create a session for the authenticated user
                session_id = create_session(user_id)
                
                show_success("Login successful! Click 'Proceed' to continue!", duration=10)
                return (
                    "", 
                    "",
                    "",
                    gr.update(visible=True), # Show Proceed button.
                    gr.update(visible=False), # Hide Login button.
                    session_id   # Return the session ID for the new session
                )
            else:
                show_error("Invalid credentials. Please try again.")
                return (
                    "<span style='color:#c62828;'>Invalid credentials. Please try again.</span>",
                    "",
                    "",
                    gr.update(visible=False),
                    gr.update(visible=True),
                    ""    # No session ID since login failed
                )
    except Exception as e:
        show_error(f"System error: {str(e)}. Please ensure required modules are imported.")
        return (
            "<span style='color:#c62828;'>System error encountered.</span>",
            "",
            "",
            gr.update(visible=False),
            gr.update(visible=True),
            ""    # No session ID since login failed
        )

def generate_initial_greeting_general(system_prompt: str, model: str) -> str:
    """Ask the LLM to craft a friendly, creative greeting."""
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role":"system",  "content": system_prompt},
                {"role":"user",    "content": "Please write a warm, engaging opening message for your next chat session as an AI assistant for USIU students and faculty."}
            ],
            max_tokens=60,
            temperature=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Warning] could not generate dynamic greeting: {e}")
        return "Hello there! How can I assist you today?"
    
def generate_initial_greeting_study(system_prompt: str, model: str) -> str:
    """Ask Claude to craft a friendly, creative greeting."""
    try:
        response = claude_client.messages.create(
            model=model,
            system=system_prompt,
            messages=[
                {"role": "user", "content": "Please write a warm, engaging opening message for your next chat session as an AI assistant for USIU students and faculty."}
            ],
            max_tokens=250,
            temperature=0.9
        )
        
        return response.content[0].text.strip()
    except Exception as e:
        print(f"[Warning] could not generate dynamic greeting with Claude: {e}")
        return "Hello there! How can I assist you today?"

# ----------------- Voice Chat Functions -----------------

async def start_voice_chat(message_placeholder, chat_history):
    """Start a voice chat session using Hume Voice API"""
    try:
        client = HumeVoiceClient(api_key=HUMEAI_API_KEY)
        
        async with client.connect(config_id=HUMEAI_CONFIG_ID) as socket:
            # Start the microphone interface
            await MicrophoneInterface.start(socket)
            
            # Get the transcript from the voice input
            transcript = await socket.receive_transcript()
            
            # Update the message placeholder with the transcript
            return transcript, chat_history
    except Exception as e:
        print(f"Error in voice chat: {e}")
        return f"Voice chat error: {str(e)}", chat_history

def process_voice_response(response_text, chat_history):
    """Add the voice response to chat history and send to client"""
    if chat_history is None:
        chat_history = []
    chat_history.append((None, response_text))
    return chat_history

# ----------------- Chat Interfaces -----------------

def general_chat_ui(system_prompt: str, model: str):
    """Creates a Gradio ChatInterface for general academic chat with RAG."""

    def general_chat(message: str, chat_history, file) -> str:
        # Ensure chat_history is a list and filter out any None items.
        if chat_history is None:
            chat_history = []
        else:
            chat_history = [msg for msg in chat_history if msg is not None]

        # If a file is uploaded and the message is empty, replace the empty message with the file name.
        if not message.strip() and file is not None:
            message = f"Uploaded file: {os.path.basename(file.name)}"

        # If this is a new conversation, insert a conversation header.
        if not chat_history:
            date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime())
            conv_header = {
                "role": "header",
                "content": (
                    f"<div style='text-align: center; font-weight: bold; font-size: 16px; color: #000;'>"
                    f"Conversation started on {date_str}"
                    f"</div>"
                ),
                "files": []
            }
            chat_history.insert(0, conv_header)  # Insert at the beginning

        # Start with the initial system prompt.
        messages = [{"role": "system", "content": system_prompt, "files": []}]

        # Add chat history to messages (all messages, including header).
        if chat_history:
            # If the first element is a tuple/list with two elements, assume pair format.
            if isinstance(chat_history[0], (tuple, list)) and len(chat_history[0]) == 2:
                for human, assistant in chat_history:
                    messages.append({"role": "user", "content": human, "files": []})
                    messages.append({"role": "assistant", "content": assistant, "files": []})
            # Otherwise, if they are dicts, ensure each has a 'files' field.
            elif isinstance(chat_history[0], dict):
                for msg in chat_history:
                    # Skip header messages.
                    if msg.get("role") == "header":
                        continue
                    msg_to_send = dict(msg)
                    if "files" not in msg_to_send or msg_to_send["files"] is None:
                        msg_to_send["files"] = []
                    messages.append(msg_to_send)

        # If a file is uploaded, add its content to the messages.
        if file is not None:
            try:
                file_content = FileProcessor.read_file(file)
                messages.append({
                    "role": "user",
                    "content": f"Here's the content of the uploaded file:\n\n{file_content}",
                    "files": []
                })
            except Exception as e:
                messages.append({
                    "role": "user",
                    "content": f"Error reading file: {str(e)}",
                    "files": []
                })

        # Optimized RAG Retrieval and Summarization Implementation:
        if GLOBAL_RETRIEVER is not None:
            try:
                # Retrieve relevant documents.
                docs = GLOBAL_RETRIEVER.invoke(message)
                if docs:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(docs), 5)) as executor:
                        futures = [executor.submit(summarize_context, doc.page_content, GPT4O_MODEL)
                                   for doc in docs]
                        summarized_texts = []
                        for future in concurrent.futures.as_completed(futures):
                            result = future.result()
                            if result and result.strip():
                                summarized_texts.append(result.strip())
                    if summarized_texts:
                        context_text = "\n\n".join(summarized_texts)
                        messages.insert(1, {
                            "role": "system",
                            "content": f"Additional Context Summaries:\n{context_text}",
                            "files": []
                        })
                    else:
                        print("No valid summaries were generated.")
            except Exception as e:
                print("RAG retrieval failed:", e)

        # Append the user's current message.
        chat_history.append({"role": "user", "content": message, "files": []})
        messages.append({"role": "user", "content": message, "files": []})

        # Call OpenAI's ChatCompletion with streaming enabled.
        completion = openai.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=600,
            temperature=0.7,
            stream=True,
        )

        response = ""
        for chunk in completion:
            token = chunk.choices[0].delta.content or ""
            response += token
            yield response

    # A zero‑arg function for value that calls a greeting generator:
    def initial_value_general():
        return [{"role":"assistant", "content": generate_initial_greeting_general(system_prompt, model)}]

    # Instantiate a Chatbot with additional components.
    chatbot_comp = gr.Chatbot(
        value=initial_value_general,
        type="messages",
        show_copy_button=True,
        avatar_images=("👤", "🤖"),
        sanitize_html=True,
        allow_tags=["thinking"],
        height=600,
        group_consecutive_messages=False
    )

    # Create a new wrapper function that will be called by the ChatInterface
    def chat_wrapper(message, history):
        # This function doesn't handle file uploads yet
        # It will be replaced by our custom event handlers
        return general_chat(message, history, None)

    # Create the chat interface with a custom chatbot component
    with gr.Blocks(elem_id="general-chat-interface", elem_classes="chat-interface-container") as interface:
        # Create the chat interface
        chat_interface = gr.ChatInterface(
            fn=general_chat,
            chatbot=chatbot_comp,
            editable=True,
            save_history=True,
            title="General Enquiries",
            description="<div style='display:flex; justify-content:center;'>Hi there! I'm your AI assistant, here to help you with queries related to USIU. Feel free to ask any questions or seek assistance.</div>",
            type="messages",
            cache_mode="eager",
            flagging_mode="manual",
            flagging_options=("Like","Dislike","Neutral"),
            flagging_dir="user_feedback_enquiry",
        )

        # Add file input at the bottom
        with gr.Accordion("File Upload", open=False, elem_classes="additional-inputs-accordion"):
            file_input = gr.File(label="Upload a file (optional)", elem_classes="file-container")

        # Integrate voice chat HTML
        gr.HTML(voice_chat_js())

        # Now handle file input separately by extracting the components
        # Get textbox and attach our custom function to it
        textbox = None
        submit_button = None
        
        # Find the textbox and submit button
        for component in interface.blocks.values():
            if isinstance(component, gr.Textbox) and not component.visible == False:
                textbox = component
            elif isinstance(component, gr.Button) and (component.value == "Submit" or component.value == "Send"):
                submit_button = component
        
        # If we found the components, attach new event handlers
        if textbox and submit_button:
            # Add event handlers that will override the default ones
            # These new handlers will run AFTER the default ones
            textbox.submit(
                fn=lambda msg, history: general_chat(msg, history, file_input.value),
                inputs=[textbox, chat_interface.chatbot],
                outputs=[chat_interface.chatbot],
                api_name=False,
                queue=True,
            )
            
            submit_button.click(
                fn=lambda msg, history: general_chat(msg, history, file_input.value),
                inputs=[textbox, chat_interface.chatbot],
                outputs=[chat_interface.chatbot],
                api_name=False,
                queue=True,
            )
    
    # Return the blocks interface instead of launching it
    return interface.queue(default_concurrency_limit=2000)

# --------------  STUDY SUPPORT CHAT UI  ------------------------------------------

def study_support_ui(system_prompt: str, model: str):
    """
    Returns a queued gr.Blocks object that hosts the Study‑Support chat.
    The file‑upload accordion sits *under* the chat input.
    """

    # ===================== 1) STREAM HANDLER ==================================== #
    def study_support_chat(
        message: str,
        chat_history: list,
        file_path_or_handle: Optional[Union[str, os.PathLike, Any]],
        session_id: str,
    ):
        """Streams a reply from Claude; embeds the uploaded file if present."""

        # ---- Session alive? --------------------------------------------------
        if session_id:
            update_session_activity(session_id)
            sess = get_session(session_id)
            if not sess or not sess.get("logged_in", False):
                yield "Your session has expired. Please log in again."
                return

        chat_history = chat_history or []

        # ---- Header on first exchange ---------------------------------------
        if not chat_history:
            chat_history.insert(
                0,
                {
                    "role": "header",
                    "content": f"<div style='text-align:center;font-weight:bold;'>"
                    f"Conversation started on {time.strftime('%Y-%m-%d %H:%M')}</div>",
                },
            )

        # ---- Rebuild prompt for Claude --------------------------------------
        msgs: list[dict[str, str]] = []
        for entry in chat_history:
            if isinstance(entry, dict) and entry.get("role") != "header":
                msgs.append({"role": entry["role"], "content": entry["content"]})
            elif isinstance(entry, (list, tuple)) and len(entry) == 2:
                human, assistant = entry
                msgs.extend(
                    [
                        {"role": "user", "content": human},
                        {"role": "assistant", "content": assistant},
                    ]
                )

        msgs.append({"role": "user", "content": message})

        # ---- If a file was supplied, read it ---------------------------------
        if file_path_or_handle:
            try:
                file_text = FileProcessor.read_file(file_path_or_handle)
                meta = FileProcessor.get_file_metadata(file_path_or_handle)
                compact_meta = ", ".join(
                    f"{k}: {v}"
                    for k, v in meta.items()
                    if k in ("filename", "extension", "size_formatted", "pages", "rows", "columns", "dimensions")
                )
                file_msg = (
                    f"I've uploaded a file ({compact_meta}) with the following content:\n\n"
                    f"{file_text[:50000]}{'…[truncated]' if len(file_text) > 50000 else ''}"
                )
                msgs.append({"role": "user", "content": file_msg})
            except Exception as e:
                msgs.append({"role": "user", "content": f"[Error processing file: {e}]"})

        # ---- Stream from Claude ---------------------------------------------
        attempts, delay, max_retry = 0, 3, 7
        while attempts < max_retry:
            try:
                stream = claude_client.messages.stream(
                    model=model,
                    system=system_prompt,
                    messages=msgs,
                    max_tokens=63_500,
                    extra_query={"extended_thinking": True},
                )
                response = ""
                with stream as s:
                    for chunk in s.text_stream:
                        response += chunk
                        yield response
                break
            except Exception as e:
                if "overloaded" in str(e).lower():
                    attempts += 1
                    yield f"(Service busy – retrying in {delay}s, {attempts}/{max_retry})"
                    time.sleep(delay)
                else:
                    yield f"Error: {e}"
                    break

    # ===================== 2) INITIAL GREETING ================================= #
    def initial_value_study():
        return [
            {
                "role": "assistant",
                "content": generate_initial_greeting_study(system_prompt, model),
            }
        ]

    # ===================== 3) BUILD THE UI ===================================== #
    with gr.Blocks(elem_id="study-chat-interface") as interface:

        session_id_box = gr.Textbox(visible=False)

        chatbot = gr.Chatbot(
            value=initial_value_study,
            type="messages",
            show_copy_button=True,
            avatar_images=("👤", "🤖"),
            sanitize_html=True,
            allow_tags=["thinking"],
            height=600,
            group_consecutive_messages=False,
        )

        # -------- inner wrapper so we can capture the file value ---------------
        def chat_wrapper(user_msg, history):
            current_file = file_input.value or None
            yield from study_support_chat(
                user_msg, history, current_file, session_id_box.value
            )
            # auto‑clear if ticked
            if auto_clear_files.value and current_file:
                file_input.clear()
                file_status.value = "File cleared"

        gr.ChatInterface(
            fn=chat_wrapper,
            chatbot=chatbot,
            editable=True,
            save_history=True,
            title="Study Bud",
            description=(
                "<div style='display:flex;justify-content:center;'>"
                "Hi there! I'm your AI study bud, here to assist you with your study journey.</div>"
            ),
            type="messages",
            cache_mode="eager",
            flagging_mode="manual",
            flagging_options=("Like", "Dislike", "Neutral"),
            flagging_dir="user_feedback_study",
        )

        # Integrate voice chat HTML
        gr.HTML(voice_chat_js())

        # ---------------- FILE‑UPLOAD ACCORDION (bottom) -----------------------
        with gr.Accordion(
            "File Upload & Settings", open=False, elem_classes="additional-inputs-accordion"
        ):

            with gr.Row():
                with gr.Column(scale=3):
                    file_input = gr.File(
                        label="Upload a file (PDF, Word, Excel, CSV, TXT, etc.)",
                        file_types=[
                            ".txt",
                            ".pdf",
                            ".docx",
                            ".doc",
                            ".xlsx",
                            ".xls",
                            ".csv",
                            ".pptx",
                            ".ppt",
                            ".png",
                            ".jpg",
                            ".jpeg",
                            ".gif",
                        ],
                        type="filepath",
                        elem_classes="file-container"
                    )
                with gr.Column(scale=2):
                    file_status = gr.Textbox(
                        label="File Status", value="No file uploaded", interactive=False
                    )

            with gr.Row():
                auto_clear_files = gr.Checkbox(
                    label="Auto‑clear files after processing", value=True
                )
                test_button = gr.Button("Test File Processing")

            test_output = gr.Textbox(
                label="File Test Results",
                visible=True,
                interactive=False,
                max_lines=10,
            )

            # ---------- helper fns for status + test ---------------------------
            def update_file_status(f):
                if not f:
                    return "No file uploaded"
                if isinstance(f, (str, os.PathLike)):
                    try:
                        size = os.path.getsize(f)
                        return f"{os.path.basename(f)} • {FileProcessor._format_file_size(size)}"
                    except Exception as e:
                        return f"File received but size unknown ({e})"
                # fallback for BytesIO etc.
                name = getattr(f, "name", "unknown")
                return f"{name} ready"

            def test_file_processing(f):
                if not f:
                    return "No file selected. Please upload a file first."
                try:
                    content_preview = FileProcessor.read_file(f)[:1000]
                    meta = FileProcessor.get_file_metadata(f)
                    meta_str = "\n".join(f"- {k}: {v}" for k, v in meta.items())
                    return f"✅ **Metadata:**\n{meta_str}\n\n📄 **Preview:**\n{content_preview}"
                except Exception as e:
                    return f"❌ Error testing file: {e}"

            file_input.change(update_file_status, file_input, file_status)
            test_button.click(test_file_processing, file_input, test_output)

    return interface.queue(default_concurrency_limit=2000)

# ---------- Dashboard UI ----------

def dashboard_ui(general_chat_prompt: str, general_model: str, 
                 study_prompt: str, study_model: str, retriever=None):
    """
    Creates a dashboard with professional styling, two main menus (General Chat and Study Support),
    and smooth transitions between views. For Study Support, a login form (with authentication)
    is shown before revealing the chat interface.
    
    Args:
        general_chat_prompt: System prompt for general enquiries
        general_model: Model ID for general chat (e.g., GPT4O_MODEL)
        study_prompt: System prompt for study support
        study_model: Model ID for study support (e.g., CLAUDE_MODEL)
        retriever: The retriever to use for RAG in general chat
    """
    global GLOBAL_RETRIEVER
    GLOBAL_RETRIEVER = retriever
    
    # Retrieve the existing chat interfaces.
    general_chat_component = general_chat_ui(general_chat_prompt, general_model)
    study_support_component = study_support_ui(study_prompt, study_model)
    # Retrieve the login form.
    (login_form_component, user_id_input, user_id_error, password_input, password_error,
     login_btn, login_msg, proceed_btn, login_back_btn, session_id) = login_form_ui()
    
    # Create the inactivity warning modal HTML
    inactivity_warning_html = """
    <div class="overlay" id="inactivity-overlay"></div>
    <div class="inactive-warning" id="inactivity-warning">
        <h3>Session Timeout Warning</h3>
        <p>Your session will expire due to inactivity in <span id="countdown">0</span> seconds.</p>
        <p>Would you like to continue your session?</p>
        <button id="stay-active-btn">Stay Active</button>
    </div>
    """
    
    with gr.Blocks(css=custom_css()) as dashboard:
        # Header component
        header_component = gr.HTML('''
        <div class="app-header">
            <!-- USIU Logo on the left -->
            <img src="/static/images/usiu-logo.png" alt="USIU Logo" class="logo-dashboard" />
            <!-- The logout button will be added programmatically -->
        </div>
        <div class="content-area"></div>
        ''', elem_id="header-container"
        )

        # Define containers for different views with initial animation state
        # Add content-area class to ensure proper spacing below fixed header
        dashboard_container = gr.Column(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInUp content-area")
        general_container = gr.Column(visible=False, elem_classes="chat-container pre-animation content-area")
        login_container = gr.Column(visible=False, elem_classes="container floating-card login-form-container pre-animation content-area")
        study_container = gr.Column(visible=False, elem_classes="chat-container pre-animation content-area")
        
        # Add the inactivity warning modal to the UI
        gr.HTML(inactivity_warning_html)
        
        # Logout Button Component (hidden by default, will be shown after login)
        with gr.Row(visible=False, elem_id="logout-row") as logout_component:
            # Hidden email for user info
            current_user = gr.Textbox(visible=False, elem_id="user-email")
            
            # Actual logout button - will be triggered via the icon in the header
            logout_btn = gr.Button("Logout", elem_id="logout-btn", visible=False)
        
        # ------------- Dashboard View -------------
        with dashboard_container:
            gr.Markdown("<h1 class='with-logo'>AI Assistance Dashboard</h1>")
            with gr.Column(elem_classes="dashboard-menu"):
                gen_button = gr.Button("General Enquiries", elem_classes="menu-button")
                study_button = gr.Button("Study with AI", elem_classes="menu-button")
        
        # ------------- General Academic Chat View -------------
        with general_container:
            back_gen = gr.Button("Back to Dashboard")
            # Render the general chat component directly in the container
            general_chat_component.render()
        
        # ------------- Login Form (for Study Support) View -------------
        with login_container:
            login_form_component.render()
        
        # ------------- Study Support Chat View -------------
        with study_container:
            back_study = gr.Button("Back to Dashboard")
            # Render the study support component directly in the container
            study_support_component.render()
            
            # Set session ID for the study chat interface
            # This ensures the session is refreshed on user interaction
            session_id_for_study = gr.Textbox(visible=False)
        
        # Hidden components for session management
        with gr.Row(visible=False):
            check_session_fn = gr.Button("check_session", elem_id="check_session_status")
            keep_alive_fn = gr.Button("keep_alive", elem_id="keep_session_alive")
            session_status_output = gr.JSON(elem_id="session_status_output")
            keep_alive_output = gr.JSON(elem_id="keep_alive_output")
        
        # Function calls for session management
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
        
        # JavaScript for session management and chat container resizing
        gr.HTML("""
        <script>
        // Session management with server synchronization
        let sessionId = "";
        let sessionCheckInterval;
        let warningDisplayed = false;
        
        // Function to start session monitoring
        function startSessionMonitoring(sid) {
            sessionId = sid;
            console.log("Starting session monitoring for session ID:", sid);
            
            // Clear any existing interval
            if (sessionCheckInterval) {
                clearInterval(sessionCheckInterval);
            }
            
            // Check session status every 5 seconds
            sessionCheckInterval = setInterval(checkSessionStatus, 5000);
            
            // Setup activity tracking
            setupActivityTracking();
        }
        
        // Function to check session status with the server
        function checkSessionStatus() {
            if (!sessionId) return;
            
            // Find the check session status button and click it
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
                // Session expired - force logout
                performLogout();
                return;
            }
            
            // Handle warning display
            if (status.show_warning && !warningDisplayed) {
                showSessionWarning(status.remaining);
                warningDisplayed = true;
            } else if (!status.show_warning && warningDisplayed) {
                hideSessionWarning();
                warningDisplayed = false;
            }
            
            // Update countdown if warning is displayed
            if (warningDisplayed) {
                updateCountdown(status.remaining);
            }
        }
        
        // Function to keep session alive
        function keepSessionAlive() {
            if (!sessionId) return;
            
            // Find the keep session alive button and click it
            const buttons = document.querySelectorAll('button');
            for (const button of buttons) {
                if (button.textContent === 'keep_alive') {
                    button.click();
                    break;
                }
            }
            
            // Hide warning if displayed
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
            // Find and click logout button
            const logoutBtn = document.getElementById('logout-btn');
            if (logoutBtn) {
                logoutBtn.click();
            } else {
                // Fallback: redirect to dashboard
                window.location.href = window.location.pathname;
            }
        }
        
        // Function to setup activity tracking
        function setupActivityTracking() {
            // Track user activity events that should reset timer
            ["mousemove", "keydown", "click", "scroll", "touchstart"].forEach(function(event) {
                document.addEventListener(event, function() {
                    // Only reset if warning is not displayed
                    if (!warningDisplayed) {
                        keepSessionAlive();
                    }
                });
            });
            
            // Setup the stay active button
            const stayActiveBtn = document.getElementById('stay-active-btn');
            if (stayActiveBtn) {
                stayActiveBtn.addEventListener('click', keepSessionAlive);
            }
        }
        
        // Function to fix chat interface heights
        function adjustChatInterfaceHeights() {
            // Wait for DOM to be fully rendered
            setTimeout(function() {
                // Target the chat interfaces specifically
                const chatInterfaces = document.querySelectorAll('.chat-interface-container');
                
                chatInterfaces.forEach(function(chatInterface) {
                    // Set minimum height
                    chatInterface.style.minHeight = '600px';
                    chatInterface.style.height = '75vh';
                    
                    // Find the chat element inside
                    const chatElement = chatInterface.querySelector('.chat');
                    if (chatElement) {
                        chatElement.style.minHeight = '600px';
                        chatElement.style.height = '75vh';
                        
                        // Find the chat window inside
                        const chatWindow = chatElement.querySelector('.chat-window');
                        if (chatWindow) {
                            chatWindow.style.minHeight = '450px';
                            chatWindow.style.height = 'calc(75vh - 150px)';
                            chatWindow.style.overflowY = 'auto';
                            
                            // Also target the content container
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
        
        // Watch for session status updates
        document.addEventListener('DOMContentLoaded', function() {
            // Run height adjustment when page loads
            adjustChatInterfaceHeights();
            
            // Monitor for view changes and adjust heights again
            const observer = new MutationObserver(function(mutations) {
                adjustChatInterfaceHeights();
                
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'childList') {
                        // Look for the session status output element
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
            
            // Observe the entire document for changes
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            // Run height adjustment periodically to ensure it's applied
            setInterval(adjustChatInterfaceHeights, 2000);
        });
        
        // Add event listeners for the menu buttons to adjust heights when views change
        window.addEventListener('load', function() {
            // Find button elements
            const buttons = document.querySelectorAll('button');
            
            buttons.forEach(function(button) {
                button.addEventListener('click', function() {
                    // Delay to allow DOM updates
                    setTimeout(adjustChatInterfaceHeights, 300);
                });
            });
        });
        </script>
        """
        )
        
        # ------------- Navigation Callbacks -------------
        # When "General Academic Chat" is selected from the dashboard.
        gen_button.click(
            lambda: [
                gr.update(visible=False),
                gr.update(visible=True, elem_classes="chat-container animate-fadeInRight"),
                gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
                gr.update(visible=False, elem_classes="chat-container pre-animation")
            ],
            outputs=[dashboard_container, general_container, login_container, study_container]
        )
        
        # When "Study Support Chat" is selected from the dashboard, show the login view with animation.
        study_button.click(
            lambda: [
                gr.update(visible=False),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=True, elem_classes="container floating-card login-form-container animate-fadeInRight"),
                gr.update(visible=False, elem_classes="chat-container pre-animation")
            ],
            outputs=[dashboard_container, general_container, login_container, study_container]
        )
        
        # "Back to Dashboard" buttons with animation.
        back_gen.click(
            lambda: [
                gr.update(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInLeft"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
                gr.update(visible=False, elem_classes="chat-container pre-animation")
            ],
            outputs=[dashboard_container, general_container, login_container, study_container]
        )
        
        # Add the header_component to the outputs
        back_study.click(
            lambda: [
                gr.update(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInLeft"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                "", # Clear the current user
                gr.update(visible=False), # Hide logout component
                '''
                <div class="app-header">
                    <!-- USIU Logo on the left -->
                    <img src="/static/images/usiu-logo.png" alt="USIU Logo" class="logo-dashboard" />
                </div>
                <div class="content-area"></div>
                '''  # Reset header to original state
            ],
            outputs=[dashboard_container, general_container, login_container, study_container, current_user, logout_component, header_component]
        )
        
        login_back_btn.click(
            lambda: [
                gr.update(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInLeft"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
                gr.update(visible=False, elem_classes="chat-container pre-animation")
            ],
            outputs=[dashboard_container, general_container, login_container, study_container]
        )
        
        # ------------- Authentication Logic -------------
        login_btn.click(
            handle_login,
            inputs=[user_id_input, password_input],
            outputs=[login_msg, user_id_error, password_error, proceed_btn, login_btn, session_id]
        )
        
        # When "Proceed" is clicked after successful authentication
        def proceed_to_study(session_id_value):
            # Get user info from the session
            session = get_session(session_id_value)
            user_email = session["user_id"] if session and "user_id" in session else "Guest"
            
            # Create HTML that includes the logout icon directly in the header
            updated_header_html = f'''
            <div class="app-header">
                <!-- USIU Logo on the left -->
                <img src="/static/images/usiu-logo.png" alt="USIU Logo" class="logo-dashboard" />
                
                <!-- Logout icon directly embedded -->
                <div class="logout-icon-container">
                    <span class="user-email">{user_email}</span>
                    <div class="logout-icon" onclick="document.getElementById('logout-btn').click();">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
                            <path d="M5 5h7V3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h7v-2H5V5zm16 7l-4-4v3H9v2h8v3l4-4z" fill="#ffffff"/>
                        </svg>
                        <span class="tooltip">Logout</span>
                    </div>
                </div>
            </div>
            <div class="content-area"></div>

            <script>
                // Initialize session monitoring with the current session ID
                setTimeout(function() {{
                    if (typeof startSessionMonitoring === 'function') {{
                        startSessionMonitoring('{session_id_value}');
                    }}
                    
                    // Adjust chat heights after view change
                    if (typeof adjustChatInterfaceHeights === 'function') {{
                        adjustChatInterfaceHeights();
                    }}
                }}, 1000);
            </script>
            '''
            
            # Start tracking activity for this session
            update_session_activity(session_id_value)
            
            return [
                gr.update(visible=False),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
                gr.update(visible=True, elem_classes="chat-container animate-fadeInRight"),
                user_email,              # Set current user
                session_id_value,        # Pass session ID to study interface
                gr.update(visible=True), # Show logout component
                updated_header_html      # Replace entire header HTML
            ]
        
        proceed_btn.click(
            proceed_to_study,
            inputs=[session_id],
            outputs=[
                dashboard_container, 
                general_container, 
                login_container, 
                study_container, 
                current_user,
                session_id_for_study,
                logout_component,
                header_component
            ]
        )
        
        def enhanced_logout(session_id_value):
            # End the session in the backend
            end_session(session_id_value)
            
            # Reset the header to the original state without the logout icon
            original_header_html = '''
            <div class="app-header">
                <!-- USIU Logo on the left -->
                <img src="/static/images/usiu-logo.png" alt="USIU Logo" class="logo-dashboard" />
            </div>
            <div class="content-area"></div>
            '''
            
            # Return updates for UI components
            return [
                gr.update(visible=True, elem_classes="container floating-card dashboard-card animate-fadeInLeft"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                gr.update(visible=False, elem_classes="container floating-card login-form-container pre-animation"),
                gr.update(visible=False, elem_classes="chat-container pre-animation"),
                "",  # Clear user_id_input
                "",  # Clear password_input
                "",  # Clear any login errors
                "",  # Clear any field errors
                "",  # Clear any field errors
                gr.update(visible=True),  # Show login button
                gr.update(visible=False),  # Hide proceed button
                gr.update(visible=False),  # Hide logout component
                original_header_html  # Reset header to original state
            ]
        
        logout_btn.click(
            enhanced_logout,
            inputs=[session_id_for_study],
            outputs=[
                dashboard_container, 
                general_container, 
                login_container, 
                study_container,
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