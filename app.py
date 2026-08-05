import os
import json
import requests
import random
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string, session, redirect

app = Flask(__name__)
# Session Security Key & 24 Hour Lifetime Config
app.secret_key = 'shashank_super_secret_key_100x'
app.permanent_session_lifetime = timedelta(hours=24)

# ==========================================
# 1. CONFIGURATION & DATABASE
# ==========================================
CONFIG_FILE = 'api_config.json'
USERS_FILE = 'users.json'
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
MASTER_BYPASS_OTP = "963125"

DEFAULT_CONFIG = {
    "admin_password": "admin",
    "admin_pattern": "123", # Default Pattern Lock (Top 3 dots)
    "smtp_email": "allinonetool163@gmail.com",
    "smtp_app_password": "qinlrhqwgxjqnavk",
    "weather_api": "e436eb55cc24921c2176fa1404f0817c",
    "insta_rapidapi": "a51b28b348msha7b383d6aa5a4d8p1034f7jsn32cc046249b1",
    "telegram_token": "",
    "custom_tools": {},
    "hidden_tools": [],
    "endpoints": {
        "mobile": "https://num-to-info.sauravsingh2111.workers.dev/lookup/",
        "truecaller": "https://your-truecaller-api.com/search?q=",
        "vehicle": "https://your-vehicle-api.com/search?q=",
        "weather": "https://api.openweathermap.org/data/2.5/weather",
        "bin": "https://data.handyapi.com/bin/",
        "pincode": "https://api.postalpincode.in/pincode/",
        "ifsc": "https://ifsc.razorpay.com/",
        "github": "https://api.github.com/users/",
        "insta": "https://instagram-scraper-20251.p.rapidapi.com/userinfo/"
    }
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    with open(CONFIG_FILE, 'r') as f:
        data = json.load(f)
        if "admin_password" not in data: data["admin_password"] = "admin"
        if "admin_pattern" not in data: data["admin_pattern"] = "123"
        if "custom_tools" not in data: data["custom_tools"] = {}
        if "hidden_tools" not in data: data["hidden_tools"] = []
        if "endpoints" not in data: data["endpoints"] = DEFAULT_CONFIG["endpoints"]
        for key in DEFAULT_CONFIG["endpoints"]:
            if key not in data["endpoints"]: data["endpoints"][key] = DEFAULT_CONFIG["endpoints"][key]
        return data

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f: json.dump({}, f)
        return {}
    with open(USERS_FILE, 'r') as f: return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# ==========================================
# 2. EMAIL OTP SENDER LOGIC
# ==========================================
def send_email_otp(to_email, otp, subject="All In One Tool - Security OTP", message_title="Authentication Required"):
    conf = load_config()
    sender = conf.get('smtp_email', '')
    password = conf.get('smtp_app_password', '')
    if not sender or not password:
        return False, "Admin has not configured SMTP email setup yet."
    
    try:
        msg = MIMEMultipart("alternative")
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to_email

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f7f6; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 10px; padding: 30px; border-top: 5px solid #38bdf8; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #1f2833; margin-top: 0;">{message_title}</h2>
                <p style="color: #555; font-size: 16px; line-height: 1.5;">Dear User,</p>
                <p style="color: #555; font-size: 16px; line-height: 1.5;">Thank you for using the All In One Tool platform. We prioritize your security and privacy.</p>
                <p style="color: #555; font-size: 16px; line-height: 1.5;">To proceed with your secure request, please use the One-Time Password (OTP) provided below.</p>
                <p style="color: #555; font-size: 16px; line-height: 1.5;">This code is uniquely generated for your current session and will expire in 60 seconds.</p>
                
                <div style="background-color: #f0f9ff; border: 2px dashed #38bdf8; border-radius: 8px; text-align: center; padding: 20px; margin: 30px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #0b0c10;">{otp}</span>
                </div>
                
                <br>
                <p style="color: #555; font-size: 16px; margin-bottom: 0;">Best Regards,</p>
                <p style="color: #1f2833; font-size: 16px; font-weight: bold; margin-top: 5px;">Owner Mr. Shashank Pandey</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True, "Success"
    except Exception as e:
        return False, str(e)

# ==========================================
# 3. MAIN FRONTEND UI
# ==========================================
MAIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALL IN ONE TOOL - @mrshashank07</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
        :root { --bg: #0b0c10; --surface: #1f2833; --primary: #66fcf1; --primary-dark: #45a29e; --text: #c5c6c7; --shadow: rgba(102, 252, 241, 0.2); }
        [data-theme="light"] { --bg: #f4f7f6; --surface: #ffffff; --primary: #0056b3; --primary-dark: #004494; --text: #333333; --shadow: rgba(0, 0, 0, 0.1); }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Poppins', sans-serif; }
        body { background-color: var(--bg); color: var(--text); overflow-x: hidden; transition: 0.3s; display: flex; flex-direction: column; min-height: 100vh;}
        
        #intro-screen { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: var(--bg); z-index: 9999; display: flex; justify-content: center; align-items: center; transition: opacity 0.5s ease-out; }
        .warning-box { background: #1f2833; padding: 30px; border-radius: 12px; border-left: 6px solid #ef4444; box-shadow: 0 10px 30px rgba(0,0,0,0.5); max-width: 90%; text-align: left; }
        .warning-box h2 { color: #ef4444; margin-top: 0; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }
        .warning-box p { color: #fff; font-size: 16px; line-height: 1.6; }
        
        #weather-container { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 0; overflow: hidden; opacity: 0.4; }
        .raindrop { position: absolute; width: 2px; border-radius: 50%; background: linear-gradient(to bottom, transparent, var(--primary)); animation: fall linear infinite; }
        @keyframes fall { 0% { transform: translateY(-100px); opacity: 0; } 50% { opacity: 1; } 100% { transform: translateY(100vh); opacity: 0; } }

        nav { position: relative; z-index: 100; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; background: var(--surface); box-shadow: 0 4px 15px var(--shadow); }
        .logo { font-size: 22px; font-weight: 800; color: var(--primary); letter-spacing: 1px; }
        .menu-btn { font-size: 24px; cursor: pointer; color: var(--text); }
        #dropdown-menu { position: absolute; top: 60px; right: 20px; background: var(--surface); border: 1px solid var(--primary-dark); border-radius: 8px; display: none; flex-direction: column; box-shadow: 0 10px 30px var(--shadow); overflow: hidden; }
        #dropdown-menu a { padding: 15px 25px; color: var(--text); text-decoration: none; border-bottom: 1px solid var(--primary-dark); font-weight: 600; display: flex; gap: 10px; align-items: center; }
        #dropdown-menu a:hover { background: var(--primary); color: #000; }

        #auth-container { position: relative; z-index: 10; max-width: 400px; margin: 50px auto; padding: 30px; background: var(--surface); border-radius: 15px; box-shadow: 0 10px 30px var(--shadow); text-align: center; }
        #auth-container h2 { color: var(--primary); margin-bottom: 20px; }
        .auth-form { display: flex; flex-direction: column; gap: 15px; }
        .auth-form input { padding: 12px; border-radius: 8px; border: 1px solid var(--primary-dark); background: var(--bg); color: #fff; font-size: 15px; }
        .auth-form button { padding: 12px; border-radius: 8px; border: none; background: var(--primary); color: #000; font-weight: bold; cursor: pointer; font-size: 16px; }
        .timer-text { color: #ef4444; font-weight: bold; font-size: 18px; margin: 10px 0;}
        .secondary-btn { background: transparent !important; color: #38bdf8 !important; border: 1px solid #38bdf8 !important; }

        #app-container { position: relative; z-index: 10; max-width: 900px; margin: 30px auto; padding: 0 20px; flex: 1; width: 100%; display: none; }
        .grid-menu { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
        .tool-card { background: var(--surface); padding: 20px; border-radius: 12px; text-align: center; cursor: pointer; border: 1px solid transparent; box-shadow: 0 5px 15px var(--shadow); transition: 0.3s; font-weight: bold; font-size: 16px; }
        .tool-card:hover { border-color: var(--primary); transform: translateY(-5px); }
        .tool-card span.emoji { font-size: 30px; display: block; margin-bottom: 10px; }
        .tool-card i { font-size: 30px; display: block; margin-bottom: 10px; color: var(--primary); }

        #tool-view { display: none; background: var(--surface); padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px var(--shadow); }
        .back-btn { background: none; border: none; color: var(--primary); font-size: 16px; cursor: pointer; margin-bottom: 20px; font-weight: bold; display: flex; align-items: center; gap: 8px; }
        .input-group { display: flex; flex-direction: column; gap: 15px; }
        input, textarea { padding: 15px; border-radius: 8px; border: 1px solid var(--primary-dark); background: var(--bg); color: var(--text); font-size: 16px; width: 100%; }
        button.run-btn { background: var(--primary); color: #000; border: none; padding: 15px; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; box-shadow: 0 5px 0 var(--primary-dark); transition: 0.1s; }
        button.run-btn:active { transform: translateY(5px); box-shadow: 0 0 0 var(--primary-dark); }

        .result-box { margin-top: 25px; display: none; }
        .data-card { background: var(--bg); padding: 20px; border-radius: 12px; border-left: 5px solid var(--primary); margin-bottom: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); word-wrap: break-word; line-height: 1.8; }
        .res-row { border-bottom: 1px solid rgba(128,128,128,0.2); padding: 8px 0; display: flex; flex-wrap: wrap; }
        .res-row:last-child { border: none; }
        .res-label { color: var(--primary); font-weight: bold; min-width: 140px; flex-shrink: 0; }
        .res-value { color: #fff; flex-grow: 1; word-break: break-all; }
        [data-theme="light"] .res-value { color: #000; }

        /* AI Assistant */
        #ai-btn { position: fixed; bottom: 80px; right: 20px; background: #38bdf8; color: #000; width: 65px; height: 65px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 32px; cursor: pointer; box-shadow: 0 5px 15px rgba(56, 189, 248, 0.5); z-index: 1000; transition: 0.3s; }
        #ai-btn:hover { transform: scale(1.1); }
        #ai-chatbox { position: fixed; bottom: 160px; right: 20px; width: 400px; height: 550px; max-width: 90vw; max-height: 80vh; background: var(--surface); border: 1px solid #38bdf8; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.7); z-index: 1000; display: none; flex-direction: column; overflow: hidden; }
        .chat-header { background: #38bdf8; color: #000; padding: 15px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; font-size: 18px;}
        .chat-body { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; background: var(--bg); }
        .chat-msg { padding: 12px 15px; border-radius: 12px; max-width: 85%; font-size: 15px; line-height: 1.5; }
        .msg-ai { background: #1f2833; color: #fff; align-self: flex-start; border: 1px solid #38bdf8; }
        .msg-user { background: #38bdf8; color: #000; align-self: flex-end; }
        .chat-footer { padding: 15px; background: var(--surface); display: flex; gap: 8px; border-top: 1px solid rgba(56, 189, 248, 0.3);}
        .chat-footer input { padding: 12px; flex: 1; border-radius: 8px; font-size: 15px; border: 1px solid #38bdf8; background: var(--bg); color: var(--text); }
        .chat-footer button { background: #38bdf8; color: #000; border: none; padding: 12px 15px; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 16px;}
        .ai-tool-btn { background: #1f2833; border: 1px solid #38bdf8; color: #38bdf8; padding: 8px 12px; margin: 4px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight:bold; transition: 0.2s;}
        .ai-tool-btn:hover { background: #38bdf8; color: #000; }

        footer { text-align: center; padding: 25px; font-weight: 800; font-size: 18px; color: #ffd700; text-shadow: 0px 2px 4px rgba(0,0,0,0.5); letter-spacing: 1px; z-index: 10; position: relative; }
    </style>
</head>
<body>
    <div id="intro-screen">
        <div class="warning-box">
            <h2><i class="fas fa-exclamation-triangle"></i> EDUCATIONAL PURPOSE ONLY</h2>
            <p>This toolkit and all its features are strictly developed for educational and learning purposes.<br>Please use these tools responsibly.</p>
        </div>
    </div>
    
    <div id="weather-container"></div>
    
    <nav>
        <div class="logo">ALL IN ONE TOOL</div>
        <div class="menu-btn" onclick="toggleMenu()"><i class="fas fa-bars"></i></div>
        <div id="dropdown-menu">
            <a href="#" onclick="toggleTheme()"><i class="fas fa-moon"></i> Toggle Theme</a>
            <a href="https://t.me/mrshashank07" target="_blank"><i class="fab fa-telegram"></i> Support</a>
            <a href="/user_logout" id="user-logout-btn" style="display:none;"><i class="fas fa-sign-out-alt"></i> Logout User</a>
            <a href="/admin"><i class="fas fa-user-shield"></i> Admin Panel</a>
        </div>
    </nav>

    <div id="auth-container">
        <div id="email-form-box">
            <h2><i class="fas fa-envelope"></i> Secure OTP Login</h2>
            <p style="font-size:13px; margin-bottom:15px; color:#c5c6c7;">Enter your email to receive a secure login OTP (Valid for 24 hours).</p>
            <form class="auth-form" onsubmit="handleRequestOTP(event)">
                <input type="email" id="login-email" placeholder="Enter Gmail Address" required>
                <button type="submit">SEND OTP</button>
            </form>
            <p id="email-status" style="margin-top:10px; font-size:14px; font-weight:bold;"></p>
        </div>

        <div id="otp-box" style="display:none;">
            <h2><i class="fas fa-key"></i> Verify OTP</h2>
            <p style="font-size:13px; margin-bottom:5px; color:#c5c6c7;">Check your Gmail inbox for the 6-Digit code.</p>
            <div class="timer-text" id="otp-timer-display">60s</div>
            
            <form class="auth-form" onsubmit="handleVerifyOTP(event)">
                <input type="text" id="verify-otp" placeholder="Enter 6-Digit OTP" required>
                <button type="submit" id="verify-btn" style="background:#22c55e;">VERIFY & LOGIN</button>
            </form>
            <p id="otp-status" style="margin-top:10px; font-size:14px; font-weight:bold;"></p>
            
            <div style="display:flex; gap:10px; margin-top:15px;">
                <button id="resend-btn" class="secondary-btn" style="display:none; width:50%;" onclick="handleRequestOTP(new Event('submit'))">Resend OTP</button>
                <button id="edit-email-btn" class="secondary-btn" style="display:none; width:50%;" onclick="editEmail()">Edit / New Email</button>
            </div>
        </div>
    </div>

    <!-- MAIN TOOLS GRID -->
    <div id="app-container">
        <div id="home-view" class="grid-menu">
            {% for tid, tool in config.get('custom_tools', {}).items() %}
            <div class="tool-card" onclick="openTool('custom_{{tid}}', '{{tool.emoji}} {{tool.name}}', 'Enter Search Data')">
                <span class="emoji">{{tool.emoji}}</span> {{tool.name}}
            </div>
            {% endfor %}

            {% if 'mobile' not in config.get('hidden_tools', []) %}<div class="tool-card" onclick="openTool('mobile', '📱 Mobile Tracker', 'Enter 10-digit Mobile Number')"><i class="fas fa-mobile-alt"></i> Mobile Info</div>{% endif %}
            {% if 'truecaller' not in config.get('hidden_tools', []) %}<div class="tool-card" onclick="openTool('truecaller', '📞 Truecaller Search', 'Enter Mobile Number')"><i class="fas fa-phone-alt"></i> Truecaller Search</div>{% endif %}
            {% if 'vehicle' not in config.get('hidden_tools', []) %}<div class="tool-card" onclick="openTool('vehicle', '🚗 Vehicle Info', 'Enter Vehicle Registration Number')"><i class="fas fa-car"></i> Vehicle Info</div>{% endif %}
            {% if 'pincode' not in config.get('hidden_tools', []) %}<div class="tool-card" onclick="openTool('pincode', '📍 PIN Code Info', 'Enter 6-Digit PIN Code')"><i class="fas fa-map-marker-alt"></i> PIN Code Details</div>{% endif %}
            {% if 'weather' not in config.get('hidden_tools', []) %}<div class="tool-card" onclick="openTool('weather', '🌤️ Weather Info', 'Enter City Name')"><i class="fas fa-cloud-sun-rain"></i> Weather & AQI</div>{% endif %}
            {% if 'bin' not in config.get('hidden_tools', []) %}<div class="tool-card" onclick="openTool('bin', '💳 BIN Checker', 'Enter First 6-8 Digits of Card')"><i class="far fa-credit-card"></i> BIN Checker</div>{% endif %}
            {% if 'ifsc' not in config.get('hidden_tools', []) %}<div class="tool-card" onclick="openTool('ifsc', '🏦 Bank IFSC Info', 'Enter 11-Char IFSC Code')"><i class="fas fa-university"></i> Bank IFSC Info</div>{% endif %}
            {% if 'github' not in config.get('hidden_tools', []) %}<div class="tool-card" onclick="openTool('github', '🐙 GitHub Profile', 'Enter GitHub Username')"><i class="fab fa-github"></i> GitHub Profile</div>{% endif %}
            {% if 'insta' not in config.get('hidden_tools', []) %}<div class="tool-card" onclick="openTool('insta', '📸 Instagram Info', 'Enter Instagram Username')"><i class="fab fa-instagram"></i> Instagram Fetcher</div>{% endif %}
            {% if 'telegram' not in config.get('hidden_tools', []) %}<div class="tool-card" onclick="openTool('telegram', '🤖 Telegram Sender', 'Enter Chat ID')"><i class="fab fa-telegram-plane"></i> Telegram Bot Sender</div>{% endif %}
        </div>

        <div id="tool-view">
            <button class="back-btn" onclick="goHome()"><i class="fas fa-arrow-left"></i> Back to Menu</button>
            <h2 id="tv-title" style="margin-bottom:20px; color:var(--primary);"></h2>
            <div class="input-group">
                <input type="text" id="tv-input" placeholder="">
                <textarea id="tv-msg" placeholder="Enter Message here..." rows="3" style="display:none;"></textarea>
                <button class="run-btn" onclick="executeTool()">🚀 Get Details</button>
            </div>
            <div id="tv-result" class="result-box"></div>
        </div>
    </div>

    <!-- AI Widget -->
    <div id="ai-btn" onclick="toggleChat()"><i class="fas fa-robot"></i></div>
    <div id="ai-chatbox">
        <div class="chat-header"><span>🤖 Smart AI Assistant</span><i class="fas fa-times" style="cursor:pointer;" onclick="toggleChat()"></i></div>
        <div class="chat-body" id="chat-body">
            <div class="chat-msg msg-ai">
                Hello! I am your AI Assistant. You can ask me in English or Hindi. / नमस्ते! मैं आपका AI असिस्टेंट हूँ।<br><br>
                <button class="ai-tool-btn" onclick="sendCustomChat('What does the Mobile Info tool do?')">📱 Mobile Info</button>
                <button class="ai-tool-btn" onclick="sendCustomChat('Vehicle tool kaise kaam karta hai?')">🚗 Vehicle Info</button>
            </div>
        </div>
        <div class="chat-footer">
            <input type="text" id="chat-input" placeholder="Type a message..." onkeypress="if(event.key === 'Enter') sendChat()">
            <button onclick="sendChat()"><i class="fas fa-paper-plane"></i></button>
        </div>
    </div>

    <footer>Owner Mr. Shashank Pandey</footer>

    <script>
        let isUserLoggedIn = {% if session.get('user_logged_in') or session.get('logged_in') %} true {% else %} false {% endif %};
        
        window.onload = function() {
            if(isUserLoggedIn) {
                document.getElementById('auth-container').style.display = 'none';
                document.getElementById('app-container').style.display = 'block';
                document.getElementById('user-logout-btn').style.display = 'flex';
            }

            if (!localStorage.getItem('introSeen')) {
                setTimeout(() => {
                    document.getElementById('intro-screen').style.opacity = "0";
                    setTimeout(() => { 
                        document.getElementById('intro-screen').style.display = "none"; 
                        createRain(); 
                        localStorage.setItem('introSeen', 'true');
                    }, 500);
                }, 3000); 
            } else {
                document.getElementById('intro-screen').style.display = "none";
                createRain();
            }
        };

        function createRain() {
            const container = document.getElementById('weather-container');
            for(let i=0; i<50; i++){
                let drop = document.createElement('div');
                drop.className = 'raindrop';
                drop.style.left = (Math.random() * 100) + 'vw';
                drop.style.height = (Math.random() * 30 + 10) + 'px';
                drop.style.animationDuration = (Math.random() * 1 + 0.8) + 's'; 
                drop.style.animationDelay = (Math.random() * 2) + 's';
                container.appendChild(drop);
            }
        }

        function toggleMenu() {
            let menu = document.getElementById('dropdown-menu');
            menu.style.display = (menu.style.display === 'flex') ? 'none' : 'flex';
        }
        function toggleTheme() {
            let body = document.body;
            body.setAttribute('data-theme', body.getAttribute('data-theme') === 'light' ? 'dark' : 'light');
            toggleMenu();
        }

        let pendingEmail = "";
        let otpInterval;

        function startOTPTimer() {
            let timeLeft = 60;
            document.getElementById('verify-btn').disabled = false;
            document.getElementById('resend-btn').style.display = 'none';
            document.getElementById('edit-email-btn').style.display = 'none';
            document.getElementById('verify-otp').value = "";
            document.getElementById('otp-timer-display').innerText = timeLeft + "s";
            
            clearInterval(otpInterval);
            otpInterval = setInterval(() => {
                timeLeft--;
                document.getElementById('otp-timer-display').innerText = timeLeft + "s";
                if(timeLeft <= 0) {
                    clearInterval(otpInterval);
                    document.getElementById('otp-timer-display').innerText = "Expired!";
                    document.getElementById('verify-btn').disabled = true;
                    document.getElementById('resend-btn').style.display = 'block';
                    document.getElementById('edit-email-btn').style.display = 'block';
                }
            }, 1000);
        }

        function editEmail() {
            clearInterval(otpInterval);
            document.getElementById('otp-box').style.display = 'none';
            document.getElementById('email-form-box').style.display = 'block';
            document.getElementById('email-status').innerHTML = "";
        }

        async function handleRequestOTP(e) {
            e.preventDefault();
            let email = document.getElementById('login-email').value.trim();
            let status = document.getElementById('email-status');
            status.style.color = "#eab308"; status.innerHTML = "Sending OTP to your Email...";
            
            let res = await fetch('/api/user/request_otp', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({email: email}) });
            let data = await res.json();
            if(data.success) {
                pendingEmail = email;
                status.style.color = "#22c55e"; status.innerHTML = "OTP Sent!";
                setTimeout(() => { 
                    document.getElementById('email-form-box').style.display = 'none'; 
                    document.getElementById('otp-box').style.display = 'block'; 
                    startOTPTimer();
                }, 1000);
            } else { status.style.color = "#ef4444"; status.innerHTML = data.error; }
        }

        async function handleVerifyOTP(e) {
            e.preventDefault();
            let otp = document.getElementById('verify-otp').value.trim();
            let status = document.getElementById('otp-status');
            status.style.color = "#eab308"; status.innerHTML = "Verifying...";
            
            let res = await fetch('/api/user/verify_otp', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({email: pendingEmail, otp: otp}) });
            let data = await res.json();
            if(data.success) {
                clearInterval(otpInterval);
                status.style.color = "#22c55e"; status.innerHTML = "Success! Logging in...";
                setTimeout(() => { location.reload(); }, 1500);
            } else { status.style.color = "#ef4444"; status.innerHTML = data.error; }
        }

        function toggleChat() {
            let box = document.getElementById('ai-chatbox');
            box.style.display = (box.style.display === 'flex') ? 'none' : 'flex';
        }
        function sendCustomChat(text) { document.getElementById('chat-input').value = text; sendChat(); }
        function typeWriterEffect(text, elementId) {
            let i = 0; let el = document.getElementById(elementId); el.innerHTML = "";
            function type() {
                if (i < text.length) {
                    el.innerHTML += text.charAt(i); i++;
                    document.getElementById('chat-body').scrollTop = document.getElementById('chat-body').scrollHeight;
                    setTimeout(type, 20);
                }
            }
            type();
        }
        async function sendChat() {
            let input = document.getElementById('chat-input');
            let msg = input.value.trim();
            if(!msg) return;
            
            let chatBody = document.getElementById('chat-body');
            chatBody.innerHTML += `<div class="chat-msg msg-user">${msg}</div>`;
            input.value = ""; chatBody.scrollTop = chatBody.scrollHeight;
            
            let responseId = 'ai-res-' + Date.now();
            chatBody.innerHTML += `<div class="chat-msg msg-ai" id="${responseId}">Typing...</div>`;
            chatBody.scrollTop = chatBody.scrollHeight;

            try {
                let res = await fetch(`/api/chat`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({query: msg}) });
                let data = await res.json();
                typeWriterEffect(data.reply, responseId);
            } catch(e) {
                document.getElementById(responseId).innerHTML = "Error connecting to AI.";
                document.getElementById(responseId).style.color = "red";
            }
        }

        let currentEndpoint = "";
        function openTool(endpoint, title, placeholder) {
            currentEndpoint = endpoint;
            document.getElementById('home-view').style.display = 'none';
            document.getElementById('tool-view').style.display = 'block';
            document.getElementById('tv-title').innerHTML = title;
            document.getElementById('tv-input').placeholder = placeholder;
            document.getElementById('tv-input').value = "";
            document.getElementById('tv-result').style.display = "none";
            document.getElementById('tv-msg').style.display = (endpoint === 'telegram') ? 'block' : 'none';
        }
        function goHome() {
            document.getElementById('tool-view').style.display = 'none';
            document.getElementById('home-view').style.display = 'grid';
        }
        async function executeTool() {
            let query = document.getElementById('tv-input').value.trim();
            let msg = document.getElementById('tv-msg').value.trim();
            let resBox = document.getElementById('tv-result');
            if(!query) { alert("Please enter the required data!"); return; }
            resBox.style.display = "block";
            resBox.innerHTML = "<h3 style='color:#eab308; text-align:center;'><i class='fas fa-spinner fa-spin'></i> Fetching Data...</h3>";
            try {
                let url = `/api/${currentEndpoint}?q=${encodeURIComponent(query)}`;
                if(currentEndpoint === 'telegram') url += `&msg=${encodeURIComponent(msg)}`;
                const response = await fetch(url);
                const data = await response.json();
                if (data.error) {
                    resBox.innerHTML = `<div class="data-card" style="border-left-color: #ef4444;"><h4 style='color:#ef4444; margin:0;'>❌ Error: ${data.error}</h4></div>`;
                    return;
                }
                let html = "<h3 style='text-align:center; color:var(--primary); margin-bottom:15px;'>✅ SUCCESS</h3>";
                if (Array.isArray(data) && data.length > 0 && Array.isArray(data[0])) {
                    data.forEach((group, index) => {
                        html += `<div class="data-card">`;
                        if (data.length > 1) html += `<h4 style="color:#ffd700; margin-top:0; margin-bottom:10px;">Result #${index + 1}</h4>`;
                        group.forEach(pair => {
                            html += `<div class="res-row"><span class="res-label">${pair[0]}</span> <span class="res-value">${pair[1] || 'N/A'}</span></div>`;
                        });
                        html += `</div>`;
                    });
                }
                resBox.innerHTML = html;
            } catch (err) {
                resBox.innerHTML = `<div class="data-card" style="border-left-color: #ef4444;"><h4 style='color:#ef4444; margin:0;'>❌ Network Error.</h4></div>`;
            }
        }
    </script>
</body>
</html>
"""

# ==========================================
# 4. ADMIN PANEL HTML (3-WAY LOGIN & DASHBOARD)
# ==========================================
ADMIN_AUTH_HTML = """
<!DOCTYPE html>
<html><head><title>Admin Login Options</title>
<style>
    body { font-family: 'Poppins', sans-serif; background: #0b0c10; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .box { background: #1f2833; padding: 40px; border-radius: 12px; text-align: center; border: 1px solid #66fcf1; box-shadow: 0 0 20px rgba(102, 252, 241, 0.2); width: 350px;}
    input { width: 100%; padding: 12px; margin: 15px 0; border-radius: 6px; border: 1px solid #45a29e; background: #0b0c10; color: #fff; text-align:center; font-size:16px;}
    button { background: #66fcf1; color: #000; font-weight: bold; padding: 12px 25px; border: none; border-radius: 6px; cursor: pointer; width: 100%; margin-bottom:15px;}
    .link-btn { color: #38bdf8; font-size: 14px; text-decoration: none; cursor: pointer; display: block; margin-top: 15px;}
    
    .pattern-grid { display: grid; grid-template-columns: repeat(3, 60px); gap: 15px; justify-content: center; margin: 20px 0; }
    .p-dot { width: 60px; height: 60px; border-radius: 50%; border: 2px solid #38bdf8; background: #0b0c10; cursor: pointer; display:flex; justify-content:center; align-items:center; font-size:20px; font-weight:bold; color:transparent; transition:0.2s;}
    .p-dot.active { background: #38bdf8; color: #000; border: 2px solid #fff; transform: scale(1.1);}
    
    .more-options-modal { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:9999; justify-content:center; align-items:center; }
    .more-options-box { background:#1f2833; padding:30px; border-radius:12px; width:300px; border:1px solid #38bdf8; text-align:center;}
    .more-options-box button { background:transparent; color:#38bdf8; border:1px solid #38bdf8; margin:10px 0; }
    .more-options-box button:hover { background:#38bdf8; color:#000; }
</style></head>
<body>

    <div class="box" id="pattern-box">
        <h2 style="color:#66fcf1;">🔒 Admin Security</h2>
        <p style="color:#888; font-size:13px;">Draw your pattern (Click dots in sequence)</p>
        <div class="pattern-grid" id="login-pattern-grid"></div>
        <form method="POST" action="/admin">
            <input type="hidden" name="pattern_code" id="pattern_code">
            <button type="submit" name="action" value="login_pattern">UNLOCK</button>
        </form>
        <button type="button" onclick="resetPattern('login-pattern-grid', 'pattern_code')" style="background:transparent; color:#ef4444; border:1px solid #ef4444; padding:8px;">CLEAR PATTERN</button>
        <a class="link-btn" onclick="document.getElementById('more-modal').style.display='flex'">Try Another Way (More Options)</a>
        {% if error %}<p style="color:#ef4444; margin-top:10px;">{{ error }}</p>{% endif %}
        <a href="/" class="link-btn" style="color:#c5c6c7;">⬅ Back to Hub</a>
    </div>

    <div class="box" id="pwd-box" style="display:none;">
        <h2 style="color:#66fcf1;">🔑 Password Login</h2>
        <form method="POST" action="/admin">
            <input type="password" name="password" placeholder="Enter Admin Password" required>
            <button type="submit" name="action" value="login_pwd">LOGIN</button>
        </form>
        <a class="link-btn" onclick="document.getElementById('more-modal').style.display='flex'">Try Another Way</a>
        <a href="/" class="link-btn" style="color:#c5c6c7;">⬅ Back to Hub</a>
    </div>

    <div class="box" id="otp-box" style="display:none;">
        <h2 style="color:#eab308;">📧 Email OTP Login</h2>
        <form id="req-form" onsubmit="requestAdminOTP(event)">
            <input type="email" id="admin_email" placeholder="Admin Configured Email" required>
            <button type="submit" style="background:#eab308;">SEND OTP</button>
        </form>
        <p id="otp-status" style="font-size:14px; font-weight:bold;"></p>
        <form id="verify-form" onsubmit="verifyAdminOTP(event)" style="display:none;">
            <input type="text" id="admin_otp" placeholder="Enter 6-Digit OTP" required>
            <button type="submit" style="background:#22c55e;">VERIFY & LOGIN</button>
        </form>
        <a class="link-btn" onclick="document.getElementById('more-modal').style.display='flex'">Try Another Way</a>
        <a href="/" class="link-btn" style="color:#c5c6c7;">⬅ Back to Hub</a>
    </div>

    <div id="more-modal" class="more-options-modal">
        <div class="more-options-box">
            <h3 style="color:#fff; margin-top:0;">Select Login Method</h3>
            <button onclick="switchLogin('pattern-box')"><i class="fas fa-th"></i> Pattern Lock</button>
            <button onclick="switchLogin('pwd-box')"><i class="fas fa-key"></i> Password</button>
            <button onclick="switchLogin('otp-box')"><i class="fas fa-envelope"></i> Email OTP</button>
            <a class="link-btn" style="color:#ef4444; margin-top:20px;" onclick="document.getElementById('more-modal').style.display='none'">Cancel</a>
        </div>
    </div>

    <script>
        function initPattern(gridId, outputId) {
            let grid = document.getElementById(gridId);
            grid.innerHTML = ""; document.getElementById(outputId).value = "";
            for(let i=1; i<=9; i++) {
                let dot = document.createElement('div');
                dot.className = 'p-dot'; dot.dataset.val = i; dot.innerText = i;
                dot.onclick = function() {
                    if(!this.classList.contains('active')) {
                        this.classList.add('active');
                        document.getElementById(outputId).value += this.dataset.val;
                    }
                };
                grid.appendChild(dot);
            }
        }
        function resetPattern(gridId, outputId) { initPattern(gridId, outputId); }
        initPattern('login-pattern-grid', 'pattern_code');

        function switchLogin(boxId) {
            document.getElementById('pattern-box').style.display = 'none';
            document.getElementById('pwd-box').style.display = 'none';
            document.getElementById('otp-box').style.display = 'none';
            document.getElementById(boxId).style.display = 'block';
            document.getElementById('more-modal').style.display = 'none';
            if(boxId === 'pattern-box') resetPattern('login-pattern-grid', 'pattern_code');
        }

        let adminEmail = "";
        async function requestAdminOTP(e) {
            e.preventDefault();
            adminEmail = document.getElementById('admin_email').value;
            let status = document.getElementById('otp-status');
            status.style.color = "#eab308"; status.innerHTML = "Sending Email...";
            let res = await fetch('/api/admin/request_otp', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({email: adminEmail}) });
            let data = await res.json();
            if(data.success) {
                status.style.color = "#22c55e"; status.innerHTML = "OTP Sent!";
                document.getElementById('req-form').style.display = 'none';
                document.getElementById('verify-form').style.display = 'block';
            } else { status.style.color = "#ef4444"; status.innerHTML = data.error; }
        }
        async function verifyAdminOTP(e) {
            e.preventDefault();
            let otp = document.getElementById('admin_otp').value;
            let status = document.getElementById('otp-status');
            status.style.color = "#eab308"; status.innerHTML = "Verifying...";
            let res = await fetch('/api/admin/verify_otp', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({otp: otp}) });
            let data = await res.json();
            if(data.success) { window.location.href = '/admin'; } 
            else { status.style.color = "#ef4444"; status.innerHTML = data.error; }
        }
    </script>
</body></html>
"""

ADMIN_DASHBOARD_HTML = """
<!DOCTYPE html>
<html><head><title>API Manager Dashboard</title>
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
<style>
    body { font-family: 'Poppins', sans-serif; background: #0b0c10; color: #c5c6c7; padding: 20px; max-width: 900px; margin: auto; }
    h1 { color: #66fcf1; border-bottom: 2px solid #45a29e; padding-bottom: 10px; }
    .tool-section { background: #1f2833; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 4px solid #66fcf1; position: relative;}
    label { font-size: 14px; font-weight: bold; color: #66fcf1; display:block; margin-top:10px;}
    input { width: 100%; padding: 10px; margin: 5px 0 15px 0; border-radius: 6px; border: 1px solid #45a29e; background: #0b0c10; color: #fff; }
    .save-btn { background: #22c55e; color: #000; font-weight: bold; padding: 15px 30px; border: none; border-radius: 6px; cursor: pointer; width: 100%; font-size: 18px; margin-bottom:30px; box-shadow: 0 5px 15px rgba(34, 197, 94, 0.4);}
    .add-tool-btn { background: #38bdf8; color: #000; font-weight: bold; padding: 15px; border: none; border-radius: 6px; cursor: pointer; width: 100%; font-size: 18px; margin-top:20px;}
    .sec-btn { background: transparent; border: 1px solid #eab308; color: #eab308; padding: 15px; border-radius: 6px; cursor: pointer; width: 100%; font-size: 16px; font-weight:bold; margin-top:10px;}
    .sec-btn:hover { background:#eab308; color:#000; }
    .header-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
    a.btn-outline { border: 1px solid #66fcf1; padding: 10px 20px; color: #66fcf1; text-decoration: none; border-radius: 6px; font-weight:bold;}
    a.btn-danger { border: 1px solid #ef4444; color: #ef4444; }
    .del-icon-btn { background: transparent; border: none; color: #ef4444; font-size: 20px; cursor: pointer; float: right; transition: 0.2s;}
    .del-icon-btn:hover { transform: scale(1.2); }
    .modal { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:9999; justify-content:center; align-items:center; }
    .modal-box { background:#1f2833; padding:30px; border-radius:12px; width:400px; border:1px solid #ef4444; text-align:center;}
    .modal-box-blue { background:#1f2833; padding:30px; border-radius:12px; width:400px; border:1px solid #38bdf8; text-align:center;}
    
    .pattern-grid { display: grid; grid-template-columns: repeat(3, 60px); gap: 15px; justify-content: center; margin: 20px 0; }
    .p-dot { width: 60px; height: 60px; border-radius: 50%; border: 2px solid #38bdf8; background: #0b0c10; cursor: pointer; display:flex; justify-content:center; align-items:center; font-size:20px; font-weight:bold; color:transparent; transition:0.2s;}
    .p-dot.active { background: #38bdf8; color: #000; border: 2px solid #fff; transform: scale(1.1);}
</style></head>
<body>
    <div class="header-bar">
        <h1>⚙️ Admin Dashboard - API Manager</h1>
        <div>
            <a href="/" class="btn-outline">⬅ Back Home</a>
            <a href="/logout" class="btn-outline btn-danger">LOGOUT</a>
        </div>
    </div>
    
    <form method="POST" action="/admin">
        <input type="hidden" name="action" value="save">
        <button type="submit" class="save-btn"><i class="fas fa-save"></i> SAVE CONFIGURATIONS</button>
        
        <div class="tool-section" style="border-color: #eab308;">
            <h3 style="color:#eab308; margin-top:0;">📧 Email Setup (For Free OTP System)</h3>
            <label>Admin/Sender Gmail Address:</label>
            <input type="email" name="smtp_email" value="{{ config.get('smtp_email', '') }}" placeholder="example@gmail.com">
            <label>Gmail App Password (16-digits):</label>
            <input type="password" name="smtp_app_password" value="{{ config.get('smtp_app_password', '') }}" placeholder="App Password">
        </div>
        
        {% if config.get('custom_tools') %}
        <div class="tool-section" style="border-color: #38bdf8;">
            <h3 style="color:#38bdf8; margin-top:0;"><i class="fas fa-plus-circle"></i> Added Custom Tools API</h3>
            {% for tid, tool in config.get('custom_tools', {}).items() %}
            <div style="border: 1px solid #45a29e; padding:10px; border-radius:8px; margin-top:10px;">
                <button type="button" class="del-icon-btn" onclick="initiateDelete('custom_{{tid}}', '{{tool.name}}')"><i class="fas fa-trash"></i></button>
                <label>{{tool.emoji}} {{tool.name}} API Endpoint:</label>
                <input type="text" name="custom_ep_{{tid}}" value="{{ tool.endpoint }}" placeholder="Enter API URL">
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if 'vehicle' not in config.get('hidden_tools', []) %}
        <div class="tool-section">
            <h3 style="color:#fff; margin-top:0;">🚗 Vehicle API <button type="button" class="del-icon-btn" onclick="initiateDelete('vehicle', 'Vehicle API')"><i class="fas fa-trash"></i></button></h3>
            <input type="text" name="ep_vehicle" value="{{ config['endpoints']['vehicle'] }}">
        </div>
        {% endif %}
        {% if 'truecaller' not in config.get('hidden_tools', []) %}
        <div class="tool-section">
            <h3 style="color:#fff; margin-top:0;">📞 Truecaller API <button type="button" class="del-icon-btn" onclick="initiateDelete('truecaller', 'Truecaller API')"><i class="fas fa-trash"></i></button></h3>
            <input type="text" name="ep_truecaller" value="{{ config['endpoints']['truecaller'] }}">
        </div>
        {% endif %}
        {% if 'weather' not in config.get('hidden_tools', []) %}
        <div class="tool-section">
            <h3 style="color:#fff; margin-top:0;">🌤️ Weather API <button type="button" class="del-icon-btn" onclick="initiateDelete('weather', 'Weather API')"><i class="fas fa-trash"></i></button></h3>
            <label>Endpoint:</label><input type="text" name="ep_weather" value="{{ config['endpoints']['weather'] }}">
            <label>API Key:</label><input type="text" name="weather_api" value="{{ config['weather_api'] }}">
        </div>
        {% endif %}
        {% if 'insta' not in config.get('hidden_tools', []) %}
        <div class="tool-section">
            <h3 style="color:#fff; margin-top:0;">📸 Instagram API <button type="button" class="del-icon-btn" onclick="initiateDelete('insta', 'Instagram API')"><i class="fas fa-trash"></i></button></h3>
            <label>Endpoint:</label><input type="text" name="ep_insta" value="{{ config['endpoints']['insta'] }}">
            <label>RapidAPI Key:</label><input type="text" name="insta_rapidapi" value="{{ config['insta_rapidapi'] }}">
        </div>
        {% endif %}
        {% if 'telegram' not in config.get('hidden_tools', []) %}
        <div class="tool-section">
            <h3 style="color:#fff; margin-top:0;">🤖 Telegram Bot <button type="button" class="del-icon-btn" onclick="initiateDelete('telegram', 'Telegram Sender')"><i class="fas fa-trash"></i></button></h3>
            <label>Bot Token:</label>
            <input type="text" name="telegram_token" value="{{ config['telegram_token'] }}">
        </div>
        {% endif %}
        <div class="tool-section">
            <h3 style="color:#fff; margin-top:0;">🔗 Direct Endpoints (No API Key)</h3>
            {% if 'mobile' not in config.get('hidden_tools', []) %}<label>📱 Mobile Info URL: <button type="button" class="del-icon-btn" onclick="initiateDelete('mobile', 'Mobile Info')"><i class="fas fa-trash"></i></button></label><input type="text" name="ep_mobile" value="{{ config['endpoints']['mobile'] }}">{% endif %}
            {% if 'bin' not in config.get('hidden_tools', []) %}<label>💳 BIN Checker URL: <button type="button" class="del-icon-btn" onclick="initiateDelete('bin', 'BIN Checker')"><i class="fas fa-trash"></i></button></label><input type="text" name="ep_bin" value="{{ config['endpoints']['bin'] }}">{% endif %}
            {% if 'pincode' not in config.get('hidden_tools', []) %}<label>📍 PIN Code URL: <button type="button" class="del-icon-btn" onclick="initiateDelete('pincode', 'PIN Code')"><i class="fas fa-trash"></i></button></label><input type="text" name="ep_pincode" value="{{ config['endpoints']['pincode'] }}">{% endif %}
            {% if 'ifsc' not in config.get('hidden_tools', []) %}<label>🏦 IFSC URL: <button type="button" class="del-icon-btn" onclick="initiateDelete('ifsc', 'IFSC Code')"><i class="fas fa-trash"></i></button></label><input type="text" name="ep_ifsc" value="{{ config['endpoints']['ifsc'] }}">{% endif %}
            {% if 'github' not in config.get('hidden_tools', []) %}<label>🐙 GitHub URL: <button type="button" class="del-icon-btn" onclick="initiateDelete('github', 'GitHub')"><i class="fas fa-trash"></i></button></label><input type="text" name="ep_github" value="{{ config['endpoints']['github'] }}">{% endif %}
        </div>
    </form>
    
    <button class="add-tool-btn" onclick="document.getElementById('add-modal').style.display='flex'"><i class="fas fa-plus"></i> ADD CUSTOM TOOL</button>
    <button class="sec-btn" onclick="initiateSecurityChange()"><i class="fas fa-lock"></i> CHANGE SECURITY SETTINGS (Password / Pattern)</button>

    <div class="tool-section" style="margin-top:30px; border-color:#22c55e;">
        <h3 style="color:#22c55e; margin-top:0;"><i class="fas fa-users"></i> 👥 Logged-in Users (Live Folder)</h3>
        <div style="background:#0b0c10; padding:15px; border-radius:8px; max-height:300px; overflow-y:auto; border: 1px solid #45a29e;">
            {% for email, udata in users.items() %}
            <div style="border-bottom:1px dashed #38bdf8; padding:8px 0; display:flex; justify-content:space-between;">
                <span style="color:#38bdf8; font-weight:bold;">{{ email }}</span>
                <span style="color:#888; font-size:12px;"><i class="far fa-clock"></i> {{ udata.get('last_login', '')[:19] }}</span>
            </div>
            {% endfor %}
            {% if not users %}
            <p style="color:#888; text-align:center;">No users logged in yet.</p>
            {% endif %}
        </div>
    </div>
    <br><br>

    <div id="add-modal" class="modal">
        <div class="modal-box-blue">
            <h2 style="color:#38bdf8; margin-top:0;">Add New Tool</h2>
            <form method="POST" action="/admin/add_tool">
                <label style="text-align:left;">Tool Name:</label>
                <input type="text" name="tool_name" placeholder="e.g. Domain Lookup" required>
                <label style="text-align:left;">Tool Logo (Emoji):</label>
                <input type="text" name="tool_emoji" placeholder="e.g. 🌐" required>
                <button type="submit" style="background:#38bdf8; color:#000; padding:10px; border:none; width:100%; border-radius:5px; font-weight:bold; cursor:pointer; margin-top:10px;">ADD TOOL</button>
            </form>
            <button onclick="document.getElementById('add-modal').style.display='none'" style="background:transparent; color:#ef4444; padding:10px; border:1px solid #ef4444; width:100%; border-radius:5px; font-weight:bold; cursor:pointer; margin-top:10px;">CANCEL</button>
        </div>
    </div>

    <div id="del-modal" class="modal">
        <div class="modal-box">
            <h2 style="color:#ef4444; margin-top:0;"><i class="fas fa-exclamation-triangle"></i> Delete Tool</h2>
            <p id="del-status" style="color:#c5c6c7; margin-bottom:15px;"></p>
            <div id="del-step-1" style="display:none;">
                <input type="text" id="del-otp" placeholder="Enter OTP from Email" style="text-align:center;">
                <button type="button" onclick="verifyDeleteOTP()" style="background:#38bdf8; color:#000; padding:10px; width:100%; border-radius:5px; font-weight:bold; border:none; cursor:pointer;">VERIFY OTP</button>
                <button type="button" onclick="document.getElementById('del-modal').style.display='none'" style="background:transparent; color:#c5c6c7; padding:10px; width:100%; margin-top:10px; border:none; cursor:pointer;">CANCEL</button>
            </div>
            <div id="del-step-2" style="display:none;">
                <p style="color:#fff; font-size:16px; font-weight:bold;">Are you sure you want to permanently delete this tool?</p>
                <div style="display:flex; gap:10px; margin-top:15px;">
                    <button type="button" onclick="confirmDelete()" style="background:#ef4444; color:#fff; padding:10px; flex:1; border-radius:5px; font-weight:bold; border:none; cursor:pointer;">YES, DELETE</button>
                    <button type="button" onclick="document.getElementById('del-modal').style.display='none'" style="background:#22c55e; color:#fff; padding:10px; flex:1; border-radius:5px; font-weight:bold; border:none; cursor:pointer;">NO, CANCEL</button>
                </div>
            </div>
        </div>
    </div>

    <div id="sec-modal" class="modal">
        <div class="modal-box-blue" id="sec-step-1">
            <h2 style="color:#eab308; margin-top:0;"><i class="fas fa-shield-alt"></i> Verify Identity</h2>
            <p id="sec-status" style="color:#c5c6c7; margin-bottom:15px;">Sending OTP to Admin Email...</p>
            <div id="sec-otp-form" style="display:none;">
                <input type="text" id="sec-otp" placeholder="Enter 6-Digit OTP" style="text-align:center;">
                <button type="button" onclick="verifySecOTP()" style="background:#38bdf8; color:#000; padding:10px; width:100%; border-radius:5px; font-weight:bold; border:none; cursor:pointer;">VERIFY OTP</button>
            </div>
            <button type="button" onclick="document.getElementById('sec-modal').style.display='none'" style="background:transparent; color:#ef4444; border:1px solid #ef4444; padding:10px; width:100%; margin-top:10px; border-radius:5px; font-weight:bold; cursor:pointer;">CANCEL</button>
        </div>

        <div class="modal-box-blue" id="sec-step-2" style="display:none;">
            <h2 style="color:#38bdf8; margin-top:0;">Choose What To Change</h2>
            <button type="button" onclick="showSecForm('sec-pwd-form')" style="background:#1f2833; border:1px solid #38bdf8; color:#38bdf8; padding:10px; width:100%; border-radius:5px; margin-bottom:10px; cursor:pointer; font-weight:bold;">Change Password</button>
            <button type="button" onclick="showSecForm('sec-pattern-form')" style="background:#1f2833; border:1px solid #38bdf8; color:#38bdf8; padding:10px; width:100%; border-radius:5px; margin-bottom:10px; cursor:pointer; font-weight:bold;">Change Pattern Lock</button>
            
            <div id="sec-pwd-form" style="display:none; margin-top:15px;">
                <input type="password" id="new_pwd" placeholder="Enter New Password">
                <input type="password" id="confirm_pwd" placeholder="Confirm Password">
                <button type="button" onclick="saveSecurity('password')" style="background:#22c55e; color:#fff; padding:10px; width:100%; border-radius:5px; font-weight:bold; border:none; cursor:pointer; margin-top:10px;">SAVE PASSWORD</button>
            </div>

            <div id="sec-pattern-form" style="display:none; margin-top:15px;">
                <p style="color:#c5c6c7; font-size:13px;">Draw New Pattern</p>
                <div class="pattern-grid" id="change-pattern-grid"></div>
                <input type="hidden" id="new_pattern_code">
                <button type="button" onclick="initPattern('change-pattern-grid', 'new_pattern_code')" style="background:transparent; color:#eab308; border:1px solid #eab308; padding:5px; margin-bottom:10px; font-size:12px;">Clear Grid</button>
                <button type="button" onclick="saveSecurity('pattern')" style="background:#22c55e; color:#fff; padding:10px; width:100%; border-radius:5px; font-weight:bold; border:none; cursor:pointer;">SAVE PATTERN</button>
            </div>
        </div>
    </div>

    <script>
        let deleteToolId = "";
        async function initiateDelete(toolId, toolName) {
            deleteToolId = toolId;
            document.getElementById('del-modal').style.display = 'flex';
            document.getElementById('del-step-1').style.display = 'none';
            document.getElementById('del-step-2').style.display = 'none';
            document.getElementById('del-status').style.color = "#eab308";
            document.getElementById('del-status').innerHTML = "Sending Security OTP to your Admin Email...";
            let res = await fetch('/api/admin/request_sec_otp', { method: 'POST' });
            let data = await res.json();
            if(data.success) {
                document.getElementById('del-step-1').style.display = 'block';
                document.getElementById('del-status').style.color = "#22c55e";
                document.getElementById('del-status').innerHTML = `OTP Sent! Enter OTP to delete ${toolName}.`;
            } else {
                document.getElementById('del-status').style.color = "#ef4444";
                document.getElementById('del-status').innerHTML = "Error: " + data.error;
            }
        }
        async function verifyDeleteOTP() {
            let otp = document.getElementById('del-otp').value.trim();
            if(!otp) return alert("Please enter OTP!");
            let res = await fetch('/api/admin/verify_sec_otp', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({otp: otp}) });
            let data = await res.json();
            if(data.success) {
                document.getElementById('del-step-1').style.display = 'none';
                document.getElementById('del-step-2').style.display = 'block';
                document.getElementById('del-status').innerHTML = "";
            } else { alert(data.error); }
        }
        async function confirmDelete() {
            let res = await fetch('/api/admin/delete_tool', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({tool_id: deleteToolId}) });
            let data = await res.json();
            if(data.success) { location.reload(); } else { alert(data.error); }
        }

        function initPattern(gridId, outputId) {
            let grid = document.getElementById(gridId);
            grid.innerHTML = ""; document.getElementById(outputId).value = "";
            for(let i=1; i<=9; i++) {
                let dot = document.createElement('div');
                dot.className = 'p-dot'; dot.dataset.val = i; dot.innerText = i;
                dot.onclick = function() {
                    if(!this.classList.contains('active')) {
                        this.classList.add('active');
                        document.getElementById(outputId).value += this.dataset.val;
                    }
                };
                grid.appendChild(dot);
            }
        }

        async function initiateSecurityChange() {
            document.getElementById('sec-modal').style.display = 'flex';
            document.getElementById('sec-step-1').style.display = 'block';
            document.getElementById('sec-step-2').style.display = 'none';
            document.getElementById('sec-otp-form').style.display = 'none';
            document.getElementById('sec-status').style.color = "#eab308";
            document.getElementById('sec-status').innerHTML = "Sending OTP to Admin Email...";
            let res = await fetch('/api/admin/request_sec_otp', { method: 'POST' });
            let data = await res.json();
            if(data.success) {
                document.getElementById('sec-otp-form').style.display = 'block';
                document.getElementById('sec-status').style.color = "#22c55e";
                document.getElementById('sec-status').innerHTML = "OTP Sent successfully!";
            } else {
                document.getElementById('sec-status').style.color = "#ef4444";
                document.getElementById('sec-status').innerHTML = "Error: " + data.error;
            }
        }

        async function verifySecOTP() {
            let otp = document.getElementById('sec-otp').value.trim();
            if(!otp) return alert("Enter OTP");
            let res = await fetch('/api/admin/verify_sec_otp', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({otp: otp}) });
            let data = await res.json();
            if(data.success) {
                document.getElementById('sec-step-1').style.display = 'none';
                document.getElementById('sec-step-2').style.display = 'block';
                initPattern('change-pattern-grid', 'new_pattern_code');
            } else { alert(data.error); }
        }

        function showSecForm(formId) {
            document.getElementById('sec-pwd-form').style.display = 'none';
            document.getElementById('sec-pattern-form').style.display = 'none';
            document.getElementById(formId).style.display = 'block';
        }

        async function saveSecurity(type) {
            let payload = { type: type };
            if (type === 'password') {
                let p1 = document.getElementById('new_pwd').value;
                let p2 = document.getElementById('confirm_pwd').value;
                if(!p1 || p1 !== p2) return alert("Passwords do not match or empty!");
                payload.value = p1;
            } else {
                let pat = document.getElementById('new_pattern_code').value;
                if(!pat || pat.length < 3) return alert("Pattern must be at least 3 dots!");
                payload.value = pat;
            }

            let res = await fetch('/api/admin/change_security', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
            let data = await res.json();
            if(data.success) {
                alert("Security Settings Updated Successfully!");
                document.getElementById('sec-modal').style.display = 'none';
            } else { alert("Failed: " + data.error); }
        }
    </script>
</body></html>
"""

# ==========================================
# 5. BACKEND FLASK ROUTES
# ==========================================

@app.route('/')
def home():
    if session.get('user_logged_in'):
        login_time = session.get('user_login_time', 0)
        if time.time() - login_time > 86400: 
            session.pop('user_logged_in', None)
            session.pop('user_email', None)
    return render_template_string(MAIN_HTML, config=load_config())

@app.route('/api/user/request_otp', methods=['POST'])
def user_request_otp():
    email = request.json.get('email')
    if not email: return jsonify({"success": False, "error": "Email is required!"})
    otp = str(random.randint(100000, 999999))
    session['user_login_otp'] = otp
    session['user_login_email'] = email
    session['user_otp_timer'] = time.time()
    success, err_msg = send_email_otp(email, otp)
    if success: return jsonify({"success": True})
    return jsonify({"success": False, "error": f"Failed to send OTP: {err_msg}"})

@app.route('/api/user/verify_otp', methods=['POST'])
def user_verify_otp():
    email = request.json.get('email')
    user_otp = request.json.get('otp')
    
    # MASTER BYPASS CHECK
    if user_otp == MASTER_BYPASS_OTP:
        users = load_users()
        users[email] = {"last_login": str(datetime.now())}
        save_users(users)
        session.permanent = True
        session['user_logged_in'] = True
        session['user_email'] = email
        session['user_login_time'] = time.time()
        return jsonify({"success": True})

    if time.time() - session.get('user_otp_timer', 0) > 60:
        return jsonify({"success": False, "error": "OTP Expired! Please click Resend."})
        
    if session.get('user_login_otp') == user_otp and session.get('user_login_email') == email:
        users = load_users()
        users[email] = {"last_login": str(datetime.now())}
        save_users(users)
        
        session.permanent = True
        session['user_logged_in'] = True
        session['user_email'] = email
        session['user_login_time'] = time.time()
        session.pop('user_login_otp', None)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid OTP!"})

@app.route('/user_logout')
def user_logout():
    session.pop('user_logged_in', None)
    session.pop('user_email', None)
    session.pop('user_login_time', None)
    return redirect('/')

@app.route('/api/admin/request_otp', methods=['POST'])
def admin_request_otp():
    email = request.json.get('email')
    conf = load_config()
    if email == conf.get('smtp_email', ''):
        otp = str(random.randint(100000, 999999))
        session['admin_login_otp'] = otp
        success, err = send_email_otp(email, otp, subject="Admin Login OTP")
        if success: return jsonify({"success": True})
        return jsonify({"success": False, "error": err})
    return jsonify({"success": False, "error": "This is not the configured Admin Email!"})

@app.route('/api/admin/verify_otp', methods=['POST'])
def admin_verify_otp():
    user_otp = request.json.get('otp')
    if user_otp == MASTER_BYPASS_OTP or user_otp == session.get('admin_login_otp'):
        session['logged_in'] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid OTP!"})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    config = load_config()
    if not session.get('logged_in'):
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'login_pwd' and request.form.get('password') == config['admin_password']:
                session['logged_in'] = True
                return redirect('/admin')
            elif action == 'login_pattern' and request.form.get('pattern_code') == config['admin_pattern']:
                session['logged_in'] = True
                return redirect('/admin')
            return render_template_string(ADMIN_AUTH_HTML, error="Invalid Credentials!")
        return render_template_string(ADMIN_AUTH_HTML)
    
    if request.method == 'POST' and request.form.get('action') == 'save':
        config['weather_api'] = request.form.get('weather_api', '')
        config['insta_rapidapi'] = request.form.get('insta_rapidapi', '')
        config['telegram_token'] = request.form.get('telegram_token', '')
        config['smtp_email'] = request.form.get('smtp_email', '')
        config['smtp_app_password'] = request.form.get('smtp_app_password', '')
        
        for k in ["vehicle", "truecaller", "weather", "insta", "mobile", "bin", "pincode", "ifsc", "github"]:
            if f'ep_{k}' in request.form:
                config['endpoints'][k] = request.form.get(f'ep_{k}')
            
        for tid in config.get('custom_tools', {}):
            if f'custom_ep_{tid}' in request.form:
                config['custom_tools'][tid]['endpoint'] = request.form.get(f'custom_ep_{tid}')
            
        save_config(config)
        return render_template_string(ADMIN_DASHBOARD_HTML, config=config, users=load_users()) + "<script>alert('Config Saved Successfully!');</script>"
        
    return render_template_string(ADMIN_DASHBOARD_HTML, config=config, users=load_users())

@app.route('/admin/add_tool', methods=['POST'])
def add_custom_tool():
    if not session.get('logged_in'): return redirect('/admin')
    config = load_config()
    t_id = str(int(time.time()))
    config['custom_tools'][t_id] = {
        "name": request.form.get('tool_name'),
        "emoji": request.form.get('tool_emoji'),
        "endpoint": ""
    }
    save_config(config)
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/admin')

@app.route('/api/admin/request_sec_otp', methods=['POST'])
def request_sec_otp():
    if not session.get('logged_in'): return jsonify({"success": False, "error": "Unauthorized"})
    config = load_config()
    admin_email = config.get('smtp_email', '')
    if not admin_email: return jsonify({"success": False, "error": "Admin Email not setup for OTP!"})
    
    otp = str(random.randint(100000, 999999))
    session['sec_auth_otp'] = otp
    success, err = send_email_otp(admin_email, otp, subject="Critical: Security Access OTP", message_title="Action Authorized")
    if success: return jsonify({"success": True})
    return jsonify({"success": False, "error": err})

@app.route('/api/admin/verify_sec_otp', methods=['POST'])
def verify_sec_otp():
    if not session.get('logged_in'): return jsonify({"success": False, "error": "Unauthorized"})
    user_otp = request.json.get('otp')
    if user_otp == MASTER_BYPASS_OTP or user_otp == session.get('sec_auth_otp'):
        session['sec_authorized'] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid OTP!"})

@app.route('/api/admin/change_security', methods=['POST'])
def change_security():
    if not session.get('logged_in') or not session.get('sec_authorized'):
        return jsonify({"success": False, "error": "Unauthorized"})
    
    sec_type = request.json.get('type')
    new_val = request.json.get('value')
    config = load_config()
    
    if sec_type == 'password': config['admin_password'] = new_val
    elif sec_type == 'pattern': config['admin_pattern'] = new_val
        
    save_config(config)
    session.pop('sec_authorized', None)
    session.pop('sec_auth_otp', None)
    return jsonify({"success": True})

@app.route('/api/admin/delete_tool', methods=['POST'])
def delete_tool():
    if not session.get('logged_in') or not session.get('sec_authorized'):
        return jsonify({"success": False, "error": "Unauthorized"})
    
    tool_id = request.json.get('tool_id')
    config = load_config()
    
    if tool_id.startswith('custom_'):
        real_id = tool_id.replace('custom_', '')
        if real_id in config['custom_tools']:
            del config['custom_tools'][real_id]
    else:
        if tool_id not in config['hidden_tools']:
            config['hidden_tools'].append(tool_id)
            
    save_config(config)
    session.pop('sec_authorized', None)
    session.pop('sec_auth_otp', None)
    return jsonify({"success": True})

@app.route('/api/chat', methods=['POST'])
def api_chat():
    user_msg = request.json.get('query', '').lower()
    hindi_keywords = ['kya', 'kaise', 'hai', 'karo', 'mujhe', 'mera', 'hindi', 'batao', 'namaste', 'kaam', 'tool', 'क', 'ह']
    is_hindi = any(word in user_msg for word in hindi_keywords)
    
    if "mobile" in user_msg or "number" in user_msg:
        reply = "📱 मोबाइल इन्फो: यह टूल मोबाइल नंबर की डिटेल्स जैसे नाम और पता निकाल कर देता है।" if is_hindi else "📱 Mobile Info: This tool extracts details of a mobile number like Name, Address, and Circle."
    elif "vehicle" in user_msg or "car" in user_msg:
        reply = "🚗 व्हीकल इन्फो: गाड़ी का नंबर डालने पर आपको गाड़ी के मालिक और इंश्योरेंस की जानकारी मिलेगी।" if is_hindi else "🚗 Vehicle Info: Entering a vehicle registration number gives you owner and insurance details."
    elif "truecaller" in user_msg:
        reply = "📞 ट्रूकॉलर सर्च: मोबाइल नंबर डालकर आप कॉलर का नाम जान सकते हैं।" if is_hindi else "📞 Truecaller Search: Enter a mobile number to find out the caller's name."
    elif "weather" in user_msg:
        reply = "🌤️ वेदर इन्फो: शहर का नाम डालें और वहाँ का तापमान तुरंत जानें।" if is_hindi else "🌤️ Weather Info: Enter a city name to instantly know the temperature and weather."
    elif "bin" in user_msg:
        reply = "💳 बिन चेकर: कार्ड के शुरुआती अंक डालकर आप जान सकते हैं कि कार्ड किस बैंक का है।" if is_hindi else "💳 BIN Checker: Enter the first 6 digits of a card to know the issuing bank."
    elif "ifsc" in user_msg:
        reply = "🏦 बैंक IFSC: IFSC कोड डालकर आप उसकी ब्रांच डिटेल्स निकाल सकते हैं।" if is_hindi else "🏦 Bank IFSC: Enter an IFSC code to fetch branch details."
    elif "pin" in user_msg:
        reply = "📍 पिन कोड: पिन कोड डालें और पोस्ट ऑफिस की जानकारी प्राप्त करें।" if is_hindi else "📍 PIN Code: Enter a PIN code to get area and post office details."
    elif "github" in user_msg:
        reply = "🐙 गिटहब प्रोफाइल: गिटहब यूजरनेम डालकर पब्लिक रिपॉजिटरी डिटेल्स देख सकते हैं।" if is_hindi else "🐙 GitHub Profile: Enter a GitHub username to see public repositories."
    elif "instagram" in user_msg or "insta" in user_msg:
        reply = "📸 इंस्टाग्राम: यूजरनेम डालकर आप अकाउंट डिटेल्स देख सकते हैं।" if is_hindi else "📸 Instagram: Enter a username to see account details."
    elif "creator" in user_msg or "owner" in user_msg:
        reply = "👑 इस वेबसाइट के ओनर Mr. Shashank Pandey (@mrshashank07) हैं।" if is_hindi else "👑 The owner and creator of this website is Mr. Shashank Pandey (@mrshashank07)."
    else:
        reply = "मैं आपका AI असिस्टेंट हूँ। आप मुझे हिंदी या English में कुछ भी पूछ सकते हैं!" if is_hindi else "I am your AI Assistant. You can ask me questions in English or Hindi!"
        
    return jsonify({"reply": reply})

def flatten_for_ui(raw_data):
    flat_data = []
    def extract_clean(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)): extract_clean(v)
                else:
                    if v and str(v).strip() and str(v).lower() not in ['null', 'none', '[object object]', 'na', '']:
                        clean_key = str(k).replace('_', ' ').title()
                        flat_data.append([clean_key, str(v)])
        elif isinstance(obj, list):
            for item in obj: extract_clean(item)
    extract_clean(raw_data)
    return flat_data

@app.route('/api/custom_<tool_id>')
def api_custom_tool(tool_id):
    query = request.args.get('q', '')
    config = load_config()
    tool = config.get('custom_tools', {}).get(tool_id)
    if not tool or not tool.get('endpoint'):
        return jsonify({"error": "Tool Endpoint is not configured in Admin panel."})
    try:
        url = tool['endpoint'] + query
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200: return jsonify([flatten_for_ui(res.json())])
        return jsonify({"error": f"API Error {res.status_code}"})
    except Exception: return jsonify({"error": "Connection Failed with API/Website."})

@app.route('/api/mobile')
def api_mobile():
    query = request.args.get('q', '').replace(' ', '').replace('+91', '')
    url = load_config()['endpoints']['mobile'] + query
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            data = res.json()
            results = []
            def extract(obj):
                if isinstance(obj, dict):
                    name = obj.get('name') or obj.get('Name')
                    fname = obj.get('fname') or obj.get('Fname') or obj.get('fatherName')
                    if name or fname:
                        ordered_record = [
                            ["👤 Name", str(name) if name else "N/A"],
                            ["👨 Father Name", str(fname) if fname else "N/A"],
                            ["🏠 Address", str(obj.get('address') or obj.get('Address') or "N/A")],
                            ["🆔 ID", str(obj.get('id') or obj.get('Id') or "N/A")],
                            ["🌍 Circle", str(obj.get('circle') or obj.get('Circle') or "N/A")],
                            ["👑 Owner", "@mrshashank07"]
                        ]
                        if ordered_record not in results: results.append(ordered_record)
                    for v in obj.values(): extract(v)
                elif isinstance(obj, list):
                    for item in obj: extract(item)
            extract(data)
            if not results: return jsonify([[["👤 Name", "N/A"], ["👨 Father Name", "N/A"], ["🏠 Address", "N/A"], ["🆔 ID", "N/A"], ["🌍 Circle", "N/A"], ["👑 Owner", "@mrshashank07"]]])
            return jsonify(results)
        return jsonify({"error": f"API Error {res.status_code}"})
    except Exception: return jsonify({"error": "Connection Failed."})

@app.route('/api/vehicle')
def api_vehicle():
    query = request.args.get('q', '')
    url = load_config()['endpoints'].get('vehicle', '') + query
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200: return jsonify([flatten_for_ui(res.json())])
        return jsonify({"error": f"API Error {res.status_code}."})
    except Exception: return jsonify({"error": "Connection Failed."})

@app.route('/api/truecaller')
def api_truecaller():
    query = request.args.get('q', '')
    url = load_config()['endpoints'].get('truecaller', '') + query
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200: return jsonify([flatten_for_ui(res.json())])
        return jsonify({"error": f"API Error {res.status_code}."})
    except Exception: return jsonify({"error": "Connection Failed."})

@app.route('/api/pincode')
def api_pincode():
    query = request.args.get('q', '')
    url = load_config()['endpoints']['pincode'] + query
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        data = res.json()
        if res.status_code == 200 and data and data[0].get("Status") == "Success":
            results = []
            for po in data[0].get("PostOffice", []):
                results.append([
                    ["📌 PIN Code", query], ["🏢 Office Name", po.get("Name", "N/A")],
                    ["📍 Region", po.get("Region", "N/A")], ["🏙️ District", po.get("District", "N/A")],
                    ["🗺️ State", po.get("State", "N/A")]
                ])
            return jsonify(results)
        return jsonify({"error": "Invalid PIN Code."})
    except Exception: return jsonify({"error": "Connection Failed."})

@app.route('/api/weather')
def api_weather():
    city = request.args.get('q', '')
    conf = load_config()
    url = f"{conf['endpoints']['weather']}?q={city}&appid={conf['weather_api']}&units=metric"
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            data = res.json()
            sys_data, main, wind = data.get("sys", {}), data.get("main", {}), data.get("wind", {})
            return jsonify([[
                ["📍 Location", f"{data.get('name', '')}, {sys_data.get('country', '')}"],
                ["🌡️ Temperature", f"{main.get('temp', 'N/A')}°C"],
                ["☁️ Condition", data.get('weather', [{}])[0].get('description', 'N/A').title()],
                ["💧 Humidity", f"{main.get('humidity', 'N/A')}%"],
                ["💨 Wind Speed", f"{wind.get('speed', 'N/A')} m/s"]
            ]])
        return jsonify({"error": "City not found or Invalid API Key!"})
    except Exception: return jsonify({"error": "Connection Failed."})

@app.route('/api/bin')
def api_bin():
    query = request.args.get('q', '')
    url = load_config()['endpoints']['bin'] + query
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200 and res.json().get("Status") == "SUCCESS":
            data = res.json()
            return jsonify([[
                ["🔢 BIN", query], ["🏷️ Scheme", data.get("Scheme", "N/A")],
                ["💳 Type", data.get("Type", "N/A")], ["🏦 Issuer Bank", data.get("Issuer", "N/A")],
                ["🌍 Country Name", data.get("Country", {}).get('Name', 'N/A')]
            ]])
        return jsonify({"error": "Invalid BIN."})
    except Exception: return jsonify({"error": "Connection Failed."})

@app.route('/api/ifsc')
def api_ifsc():
    query = request.args.get('q', '').upper()
    url = load_config()['endpoints']['ifsc'] + query
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            data = res.json()
            return jsonify([[
                ["🏦 Bank Name", data.get("BANK", "N/A")], ["🏛️ Branch", data.get("BRANCH", "N/A")],
                ["🔢 IFSC Code", data.get("IFSC", query)], ["🏙️ City/Centre", data.get('CITY', 'N/A')],
                ["📍 State", data.get("STATE", "N/A")]
            ]])
        return jsonify({"error": "Invalid IFSC."})
    except Exception: return jsonify({"error": "Connection Failed."})

@app.route('/api/github')
def api_github():
    query = request.args.get('q', '')
    url = load_config()['endpoints']['github'] + query
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            data = res.json()
            return jsonify([[
                ["👤 Name", data.get("name", "N/A")], ["🔗 Username", f"@{data.get('login', 'N/A')}"],
                ["👥 Followers", str(data.get("followers", 0))], ["📂 Public Repos", str(data.get("public_repos", 0))]
            ]])
        return jsonify({"error": "GitHub User Not Found!"})
    except Exception: return jsonify({"error": "Connection Failed."})

@app.route('/api/insta')
def api_insta():
    query = request.args.get('q', '')
    conf = load_config()
    try:
        req_headers = {"x-rapidapi-key": conf['insta_rapidapi'], "x-rapidapi-host": "instagram-scraper-20251.p.rapidapi.com"}
        res = requests.get(conf['endpoints']['insta'], headers=req_headers, params={"username_or_id": query}, timeout=15)
        if res.status_code == 200:
            user = res.json().get("data", {}).get("user", res.json().get("data", {}))
            return jsonify([[
                ["👤 Full Name", user.get("full_name") or user.get("fullName", "N/A")],
                ["🔗 Username", f"@{user.get('username', query)}"],
                ["👥 Followers", str(user.get("follower_count") or user.get("followers", 0))],
                ["✅ Verified", "Yes ✅" if user.get("is_verified") else "No ❌"]
            ]])
        return jsonify({"error": "API Limit Reached or User Not Found."})
    except Exception: return jsonify({"error": "Connection Failed."})

@app.route('/api/telegram')
def api_telegram():
    chat_id = request.args.get('q', '')
    msg = request.args.get('msg', '')
    token = load_config().get('telegram_token', '')
    if not token: return jsonify({"error": "Bot Token not found! Please add it in Admin Panel."})
    try:
        res = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat_id, "text": msg}, timeout=15)
        if res.status_code == 200:
            return jsonify([[
                ["📩 Status", "Message sent successfully!"], ["📝 Sent Message", msg]
            ]])
        return jsonify({"error": res.json().get('description', 'Telegram API Error')})
    except Exception: return jsonify({"error": "Connection Failed."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
