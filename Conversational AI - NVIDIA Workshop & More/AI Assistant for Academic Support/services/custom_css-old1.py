def custom_css():
    css = """
    /* Theme variables for light/dark mode */
    :root {
        /* Light theme (default) */
        --bg-color: #f8f9fa;
        --text-color: #495057;
        --primary-color: #1F2E8C;
        --primary-hover: #000066;
        --header-bg: #1F2E8C;
        --header-text: white;
        --card-bg: rgba(255, 255, 255, 0.85);
        --card-bg-gradient-start: rgba(255, 255, 255, 0.9);
        --card-bg-gradient-end: rgba(255, 255, 255, 0.8);
        --card-border: 1px solid rgba(255, 255, 255, 0.3);
        --chatbot-bg: rgba(255, 255, 255, 0.85);
        --user-message-bg: #f0f7ff;
        --bot-message-bg: #f9f9f9;
        --chat-input-bg: rgba(255, 255, 255, 0.9);
        --chat-user-bubble-bg: #FAFAFA;
        --chat-bot-bubble-bg: #F7FCFF;
        --inactive-warning-bg: white;
        --inactive-warning-border: 1px solid #ccc;
        --inactive-warning-color: #c62828;
    }
    
    [data-theme="dark"] {
        /* Dark theme */
        --bg-color: #121212;
        --text-color: #E1E1E1;
        --primary-color: #4D5BBD;
        --primary-hover: #5F6DC9;
        --header-bg: #0F1A63;
        --header-text: white;
        --card-bg: rgba(40, 40, 40, 0.85);
        --card-bg-gradient-start: rgba(40, 40, 40, 0.9);
        --card-bg-gradient-end: rgba(30, 30, 30, 0.8);
        --card-border: 1px solid rgba(70, 70, 70, 0.3);
        --chatbot-bg: rgba(40, 40, 40, 0.85);
        --user-message-bg: #212B45;
        --bot-message-bg: #2A2A2A;
        --chat-input-bg: rgba(40, 40, 40, 0.9);
        --chat-user-bubble-bg: #2A2A2A;
        --chat-bot-bubble-bg: #212B45;
        --inactive-warning-bg: #2A2A2A;
        --inactive-warning-border: 1px solid #444;
        --inactive-warning-color: #ef5350;
    }

    /* Professional custom CSS with transitions, hover effects, and responsive design */
    body { 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        background-color: var(--bg-color); 
        margin: 0; 
        padding: 0;
        width: 100%;
        overflow-x: hidden; /* Prevent horizontal scrolling */
        color: var(--text-color);
        transition: background-color 0.3s ease, color 0.3s ease;
    }
    h1, h2, h3 { 
        text-align: center; 
        color: var(--text-color);
    }
    .gr-button:not(.secondary-button):not([aria-label="Clear"]):not([aria-label="Retry"]):not([aria-label="Undo"]):not(.chat-buttons button) { 
        transition: background-color 0.3s ease, transform 0.3s ease; 
        border-radius: 4px;
        /* USIU-Africa theme color for buttons */
        background-color: var(--primary-color) !important;
        color: white !important;
    }
    .gr-button:not(.secondary-button):not([aria-label="Clear"]):not([aria-label="Retry"]):not([aria-label="Undo"]):not(.chat-buttons button):hover { 
        background-color: var(--primary-hover) !important; 
        color: #fff !important; 
        transform: scale(1.03);
    }
    .container { 
        transition: opacity 0.5s ease-in-out;
        padding: 4px;
    }

    /* Style the "+ New chat" button to match USIU-Africa theme */
    button.primary, .gradio-container button.gr-button.gr-button-lg.primary {
        background-color: var(--primary-color) !important; /* USIU-Africa navy blue */
        color: white !important;
        border: none !important;
        transition: background-color 0.3s ease, transform 0.2s ease !important;
    }

    /* Styling the submit button and the file upload button accordion button */
    button.submit-button.svelte-173056l svg g#SVGRepo_iconCarrier,
    button.label-wrap.svelte-1w6vloh span, .message-buttons-left, .message-buttons-right {
        color: var(--primary-color);
    }

    button.secondary-button:hover, .gradio-container button.gr-button.gr-button-lg.secondary-button:hover {
        background-color: var(--primary-hover) !important; /* Slightly darker on hover */
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }

    /* ENHANCED: All chat action buttons should have the USIU-Africa theme */
    .chat-buttons button, .gradio-container .chat-buttons button {
        background-color: var(--primary-color) !important;
        color: white !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }

    .chat-buttons button:hover, .gradio-container .chat-buttons button:hover {
        background-color: var(--primary-hover) !important;
        transform: translateY(-2px) !important;
    }

    /* CRITICAL FIX: Make study support submit button visible exactly like general chat */
    #study-chat-interface button[data-testid="submit-button"],
    #study-chat-interface .submit-button,
    #study-chat-interface .input-row button[aria-label],
    button[aria-label="Submit"] {
        background-color: var(--primary-color) !important;
        color: var(--primary-color) !important;
        opacity: 1 !important;
        visibility: visible !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-width: 44px !important;
        min-height: 44px !important;
        border-radius: 4px !important;
        border: none !important;
        position: relative !important;
        transform: none !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        z-index: 20 !important;
    }

    /* Make the send icon white for better visibility */
    button[data-testid="submit-button"] svg path,
    button.submit-button svg path,
    button[aria-label="Submit"] svg path {
        fill: var(--primary-color) !important;
    }

    /* FIX: Ensure the submit button container is properly displayed */
    .wrap.svelte-tw2q7x.svelte-tw2q7x,
    .submit-container,
    .input-container button,
    .chat-input-container button {
        opacity: 1 !important;
        visibility: visible !important;
        display: flex !important;
        position: static !important;
    }

    /* Glassmorphism effect for floating cards */
    .floating-card {
        background: var(--card-bg);
        border-radius: 12px;
        box-shadow: 
            0 10px 25px rgba(0,0,0,0.08),
            0 6px 10px rgba(0,0,0,0.12),
            0 3px 3px rgba(0,0,0,0.15);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        padding: 25px;
        margin: 15px auto; /* Reduced margin */
        backdrop-filter: blur(10px);
        border: var(--card-border);
        border-top: 3px solid var(--primary-color);
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
        color: var(--primary-color);
    }

    /* ENHANCED: Increase chat window height/width & add floating + inset 3D effect */
    .chatbot-container, .gradio-container .chat {
        height: 600px !important;                /* FIXED HEIGHT SETTING */
        max-height: 1500px !important;          /* INCREASED: from 1000px */
        width: 100% !important;                /* INCREASED: from 98% */
        margin: 0 auto !important;
        background: var(--chatbot-bg) !important;
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
        border: var(--card-border) !important;
        border-top: 3px solid var(--primary-color) !important;
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
        background: var(--card-bg) !important;
        backdrop-filter: blur(12px) !important;
        border: var(--card-border) !important;
        border-top: 3px solid var(--primary-color) !important;
        padding: 20px 15px !important; /* Added horizontal padding */
    }

    /* Dashboard container styling with responsiveness */
    .dashboard-card {
        width: 98% !important; /* Take almost full width on mobile */
        max-width: 700px !important;
        margin: 30px auto 20px auto !important; /* Increased top margin to give space from header */
        background: var(--card-bg) !important;
        backdrop-filter: blur(12px) !important;
        height: auto !important;
        min-height: 500px !important;
        border: var(--card-border) !important;
        border-top: 3px solid var(--primary-color) !important;
        opacity: 0;
        animation: dashboardFadeIn 1.5s forwards ease-in-out;
        padding: 20px 10px !important; /* Reduced horizontal padding */
    }

    /* A subtle gradient background to the cards */
    .dashboard-card, .login-form-container {
        background: linear-gradient(
            135deg, 
            var(--card-bg-gradient-start) 0%, 
            var(--card-bg-gradient-end) 100%
        ) !important;
    }

    /* ENHANCED: App header with USIU-Africa theme */
    .app-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 70px;
        background-color: var(--header-bg) !important; /* USIU-Africa navy blue */
        box-shadow: 0 3px 15px rgba(0,0,0,0.45);
        display: flex;
        align-items: center;
        justify-content: space-between;
        z-index: 1000;
        padding: 0 15px;
        color: var(--header-text) !important;
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
        color: var(--header-text);
    }

    /* Add padding to account for fixed header */
    .content-area {
        padding-top: 60px;
    }

    .with-logo {
        margin-top: 10px;
    }

    /* Theme toggle button styling */
    .header-controls {
        display: flex;
        align-items: center;
    }

    .theme-toggle {
        position: relative;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: transparent;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 15px;
        transition: background-color 0.3s ease;
    }

    .theme-toggle:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }

    .theme-toggle svg {
        width: 22px;
        height: 22px;
        fill: var(--header-text);
        transition: transform 0.3s ease;
    }

    .theme-toggle:hover svg {
        transform: scale(1.1);
    }

    .theme-toggle .tooltip {
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

    .theme-toggle .tooltip:after {
        content: '';
        position: absolute;
        top: -5px;
        left: 50%;
        transform: translateX(-50%);
        border-width: 5px;
        border-style: solid;
        border-color: transparent transparent #333 transparent;
    }

    .theme-toggle:hover .tooltip {
        opacity: 1;
        visibility: visible;
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
        color: var(--header-text);
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
        fill: var(--header-text); /* Make icon match text color */
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
        background-color: var(--inactive-warning-bg);
        border: var(--inactive-warning-border);
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
        color: var(--inactive-warning-color);
        font-size: 20px;
    }

    .inactive-warning p {
        font-size: 16px;
        margin: 15px 0;
        color: var(--text-color);
    }

    .inactive-warning #countdown {
        font-weight: bold;
        color: var(--inactive-warning-color);
    }

    .inactive-warning button {
        margin-top: 20px;
        background-color: var(--primary-color);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
        transition: background-color 0.2s;
    }

    .inactive-warning button:hover {
        background-color: var(--primary-hover);
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
        # box-shadow: 0 5px 15px rgba(0,0,0,0.05) !important;
    }

    /* Style user messages */
    .user-message {
        background-color: var(--user-message-bg) !important; 
        border-left: 3px solid var(--primary-color) !important;
    }

    /* Style bot messages */
    .bot-message {
        background-color: var(--bot-message-bg) !important;
        border-left: 3px solid #505050 !important;
    }

    /* Style the chat input area */
    .chat-input-container {
        padding: 15px !important;
        background: var(--chat-input-bg) !important;
        border-top: 1px solid rgba(0, 0, 128, 0.2) !important;
        border-radius: 0 0 16px 16px !important;
    }

    .chat-input {
        border-radius: 25px !important;
        border: 2px solid rgba(0, 0, 128, 0.3) !important;
        padding: 12px 20px !important;
        transition: all 0.3s ease !important;
        background-color: var(--card-bg) !important;
        color: var(--text-color) !important;
    }

    .chat-input:focus {
        border-color: var(--primary-color) !important;
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
        background: var(--primary-color);
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

    # not(.file-upload button)
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

    /* Make the "File Upload" accordion span the full chat width - EXACTLY match the inset box-shadow element */
    .additional-inputs-accordion{
        width: 100% !important;
        max-width: 100% !important; 
        margin: 0 auto !important;
        box-sizing: border-box !important;
    }

    /* Ensure the file picker itself stretches the full width, too */
    .additional-inputs-accordion input[type="file"]{
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }

    /* Media Queries for better responsiveness */
    @media screen and (max-width: 768px) {
        body {
            padding: 0 !important; /* Remove body padding on mobile */
        }
        
        /* Force full width on mobile for chat interfaces */
        .gradio-container .tab-nav + div > div,
        .gradio-container [id^="component"] > div > div,
        .gradio-container [id^="component"] > div,
        .chat-container, .chat-interface-container,
        #general-chat-interface, #study-chat-interface,
        .chatbot-container, .gradio-container .chat {
            width: 100vw !important;
            max-width: 100vw !important;
            margin-left: 0 !important;
            margin-right: 0 !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            border-radius: 0 !important;
        }

        .user-message, .bot-message {
            font-size: 12px !important;
        }
        
        /* Match file upload accordion to chat container on mobile */
        # .additional-inputs-accordion {
        #     width: 100vw !important;
        #     max-width: 100vw !important;
        #     margin: 0 !important;
        #     padding: 0 !important;
        #     border-radius: 0 !important;
        # }
        
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
            padding: 0 !important;
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
        
        /* Adjust theme toggle for mobile */
        .theme-toggle {
            width: 32px;
            height: 32px;
            margin-right: 10px;
        }
        
        .theme-toggle svg {
            width: 18px;
            height: 18px;
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
        input:not(input[type="checkbox"]), select, textarea {
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
        
        .gradio-container .chat-window, .gradio-container .chat-window-content {
            # height: calc(75vh - 90px) !important;
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

        /* Match file-inputs-accordion width to chatbot container on large screens */
        .additional-inputs-accordion {
            max-width: 1400px !important;
            width: 100% !important;
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
        background-color: var(--chat-user-bubble-bg) !important;
        box-shadow:
            0 8px 16px rgba(0,0,0,0.10) !important,     /* big, soft shadow */
            0 4px  8px rgba(0,0,0,0.08) !important;     /* smaller, darker falloff */
        border-radius: 16px 16px 0 16px !important;
        pointer-events: auto !important;
    }

    .message-row.bubble.bot-row.svelte-yaaj3 .flex-wrap.svelte-yaaj3 .bot {
        background-color: var(--chat-bot-bubble-bg) !important; /* #F7F9FF, FDFEFF */
        border-radius: 16px 16px 16px 0 !important;
    }

    .flex-wrap .svelte-yaaj3 .message, .avatar-container.svelte-yaaj3, 
    .icon-button-wrapper, #component-14 {
        # box-shadow: 2px 5px 15px rgba(0,0,0,0.10) !important;
        /* top shadow | bottom shadows */
        box-shadow:
            /* subtle top lift */
            0 -3px 5px rgba(0, 0, 0, 0.03),
            /* main bottom spread */
            0  3px 10px rgba(0, 0, 0, 0.09),
            /* secondary crisp shadow */
            0  2px 5px rgba(0, 0, 0, 0.07);
    }

    .message-row {
        max-width: 86% !important;
    }
    """
    return css