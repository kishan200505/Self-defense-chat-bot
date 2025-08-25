import nltk
import random
import string
import tkinter as tk
from tkinter import ttk, font, messagebox
import tkinter.font as tkfont
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pyttsx3
import speech_recognition as sr
import threading
import re
import time
import os
import sys
import requests
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
from PIL import Image, ImageTk

# Check dependencies and install if missing
def check_dependencies():
    try:
        import nltk
        import sklearn
        import pyttsx3
        import speech_recognition
        import requests
        import twilio
        from PIL import Image, ImageTk
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required packages with: pip install nltk sklearn pyttsx3 SpeechRecognition pillow requests twilio")
        input("Press Enter to exit...")
        sys.exit(1)

# Download required NLTK data if not already present
def download_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("Downloading required NLTK data...")
        nltk.download('punkt')
        nltk.download('stopwords')

# Initialize resources
check_dependencies()
download_nltk_data()

# Initialize stemmer
stemmer = LancasterStemmer()

# Initialize text-to-speech engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)
tts_engine.setProperty('volume', 0.9)

# Get available voices
voices = tts_engine.getProperty('voices')
if len(voices) > 1:
    tts_engine.setProperty('voice', voices[1].id)  # Use female voice if available

# Initialize speech recognizer
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True
recognizer.energy_threshold = 4000

# Twilio credentials (replace with your own from twilio.com)
TWILIO_SID = "your_account_sid"
TWILIO_AUTH_TOKEN = "your_auth_token"
TWILIO_PHONE = "your_twilio_number"

# Gmail credentials (use an App Password if 2FA is on)
GMAIL_USER = "your_email@gmail.com"
GMAIL_PASS = "your_app_password"

# Emergency contacts (initially empty, updated by user)
CONTACTS = {
    "phone": [],
    "email": []
}

# Enhanced Self-defense knowledge base
knowledge_base = {
    'general': [
        "Always trust your instincts. If a situation feels wrong, it probably is.",
        "Stay aware of your surroundings and avoid distractions like looking at your phone while walking alone.",
        "Walk confidently and keep your head up to appear less vulnerable.",
        "Focus on de-escalation and escape rather than confrontation when possible.",
        "Self-defense is about protecting yourself, not winning a fight."
    ],
    'physical_techniques': [
        "If someone grabs your wrist, rotate your arm toward their thumb (the weakest point) and pull away quickly.",
        "For a front chokehold, tuck your chin to protect your airway, then strike the attacker's arms upward while stepping back to break their grip.",
        "If you're pushed, lower your center of gravity by bending your knees to maintain balance, then move laterally away from the attacker.",
        "Use the heel of your palm for strikes instead of closed fists to avoid injuring your knuckles.",
        "Target vulnerable areas such as eyes, nose, throat, and groin when necessary for self-defense."
    ],
    'pressure_points': [
        "The philtrum (area between nose and upper lip) is sensitive - a sharp upward strike can cause momentary disorientation.",
        "The throat/windpipe (trachea) is very vulnerable - even light pressure can cause significant distress.",
        "The eyes are extremely sensitive - even light contact may create a reflexive response.",
        "The temples (sides of the head) are vulnerable points that can cause disorientation when struck.",
        "The groin area is highly sensitive for all genders and causes reflexive bending forward when struck.",
        "The solar plexus (diaphragm area below sternum) can cause temporary breathing difficulty when struck.",
        "The knees have limited lateral stability and can be target points to disrupt an attacker's mobility.",
        "The top of the foot contains many small bones that are sensitive to stomping motions."
    ],
    'choking_defense': [
        "For front chokeholds: Tuck your chin to protect your airway, raise your shoulders, and immediately strike upward between the attacker's arms to break their grip.",
        "For rear chokeholds: Drop your weight while tucking your chin, then grab one of the attacker's hands/arms while turning into their weakest point (usually the thumb side) and striking with your other arm.",
        "If on the ground being choked, trap one of the attacker's arms, bridge your hips upward forcefully and roll them to the trapped-arm side.",
        "When possible, use both hands to grab just one of the attacker's hands/wrists and pull while turning to break their grip.",
        "Remember that making noise is difficult during choking - focus first on breaking the grip to restore breathing."
    ],
    'weapon_defense': [
        "Against a weapon, creating distance and escaping should always be your first priority if possible.",
        "For knife threats, maintain distance and use improvised barriers (furniture, backpacks, etc.) between you and the attacker.",
        "If approached by someone with a knife, remember the saying 'run if you can, fight if you must'.",
        "With gun threats, follow instructions if the goal appears to be robbery, as possessions aren't worth your life.",
        "If you must defend against a weapon, focus on controlling the weapon hand/arm first before attempting other techniques."
    ],
    'escape': [
        "Create distance between you and an attacker when possible, then run to a public place.",
        "If being followed, change direction and head toward a populated area or business.",
        "Use your voice loudly - yell specific commands like 'Back off!' or 'Call 911!'",
        "If grabbed from behind, drop your weight suddenly while striking backward with elbows or heels.",
        "When escaping, run toward light and other people, not into isolated areas."
    ],
    'ground_defense': [
        "If taken to the ground, protect your head and try to maintain a guard position with your legs between you and the attacker.",
        "Bridge and roll techniques can help you escape when pinned on your back - thrust your hips upward while turning.",
        "From a ground position, use your stronger leg muscles to create space and escape rather than upper body strength.",
        "If straddled (mounted), trap one of the attacker's arms, bridge your hips up forcefully, and roll them to the trapped-arm side.",
        "When on the ground, look for opportunities to strike vulnerable areas to create a chance to escape."
    ],
    'emergency': [
        "Call 911 immediately in an emergency situation.",
        "If possible, tell the dispatcher your location first in case you're disconnected.",
        "Many campuses have emergency blue light phones or campus security numbers you can program into your phone.",
        "If injured, prioritize getting to safety before assessing injuries unless movement would cause greater harm.",
        "Trust your instincts - it's better to call for help unnecessarily than to wait until it's too late."
    ],
    'reporting': [
        "Report incidents to local police or campus security.",
        "Document what happened as soon as possible while details are fresh.",
        "Consider contacting victim advocacy services for support and guidance.",
        "Take photos of any injuries or damaged property for documentation.",
        "Preserve any evidence such as torn clothing or communications from the attacker."
    ],
    'prevention': [
        "Travel with friends whenever possible, especially at night.",
        "Let someone know your whereabouts and when to expect you.",
        "Keep doors and windows locked in your home and car.",
        "Consider taking a comprehensive self-defense course.",
        "Trust your instincts - if something feels wrong, remove yourself from the situation.",
        "Have your keys ready before approaching your door or car.",
        "Vary your routine if you notice suspicious patterns or feel you're being observed."
    ],
    'verbal_defense': [
        "Use assertive body language and a confident tone of voice when setting boundaries.",
        "Clear commands like 'Stop!' or 'Back away!' can be effective in some confrontations.",
        "De-escalation techniques include speaking calmly, avoiding threats, and creating psychological distance.",
        "Creating witnesses can deter an attacker - loudly addressing nearby people can help.",
        "In harassment situations, being direct and leaving the area is often more effective than engaging in argument."
    ]
}

# Process text
def process_text(text):
    tokens = nltk.word_tokenize(text.lower())
    tokens = [stemmer.stem(token) for token in tokens if token not in string.punctuation]
    return tokens

# Create corpus from knowledge base
corpus = []
categories = []
for category, responses in knowledge_base.items():
    for response in responses:
        corpus.append(response)
        categories.append(category)

# Initialize TF-IDF vectorizer
vectorizer = TfidfVectorizer(tokenizer=process_text, stop_words=stopwords.words('english'))
tfidf_matrix = vectorizer.fit_transform(corpus)

# Key term dictionary for specific matching
key_terms = {
    'pressure points': 'pressure_points',
    'pressure point': 'pressure_points',
    'vulnerable points': 'pressure_points',
    'vulnerable areas': 'pressure_points',
    'sensitive areas': 'pressure_points',
    'weak spots': 'pressure_points',
    'weak points': 'pressure_points',
    'choke': 'choking_defense',
    'choking': 'choking_defense',
    'choked': 'choking_defense',
    'chokehold': 'choking_defense',
    'strangled': 'choking_defense',
    'strangling': 'choking_defense',
    'neck grab': 'choking_defense',
    'knife': 'weapon_defense',
    'gun': 'weapon_defense',
    'weapon': 'weapon_defense',
    'armed': 'weapon_defense',
    'ground': 'ground_defense',
    'floor': 'ground_defense',
    'pinned': 'ground_defense',
    'mounted': 'ground_defense',
    'pinned down': 'ground_defense',
    'wrist grab': 'physical_techniques',
    'grabbed': 'physical_techniques',
    'strike': 'physical_techniques',
    'hit': 'physical_techniques',
    'punch': 'physical_techniques',
    'kick': 'physical_techniques',
    'defend': 'physical_techniques',
    'technique': 'physical_techniques',
    'move': 'physical_techniques',
    'run': 'escape',
    'escape': 'escape',
    'flee': 'escape',
    'get away': 'escape',
    'followed': 'escape',
    'following': 'escape',
    'stalked': 'escape',
    'yell': 'verbal_defense',
    'scream': 'verbal_defense',
    'verbal': 'verbal_defense',
    'say': 'verbal_defense',
    'shout': 'verbal_defense',
    'de-escalate': 'verbal_defense',
    'talk': 'verbal_defense',
    'report': 'reporting',
    'police': 'reporting',
    'document': 'reporting',
    'evidence': 'reporting',
    'record': 'reporting',
    'prevent': 'prevention',
    'avoid': 'prevention',
    'safety': 'prevention',
    'safe': 'prevention',
    'precaution': 'prevention',
    'call 911': 'emergency',
    'emergency': 'emergency',
    'help': 'emergency',
    'injured': 'emergency',
    'injury': 'emergency',
    'hurt': 'emergency',
}

# Get response based on user input
def get_response(user_input):
    lower_input = user_input.lower()
    for term, category in key_terms.items():
        if term in lower_input:
            return random.choice(knowledge_base[category])
    user_vector = vectorizer.transform([user_input])
    similarity_scores = cosine_similarity(user_vector, tfidf_matrix)[0]
    if max(similarity_scores) > 0.1:
        best_match_index = similarity_scores.argmax()
        category = categories[best_match_index]
        return random.choice(knowledge_base[category])
    else:
        safety_tips = [
            "I'm not sure about that specific situation, but remember to always be aware of your surroundings and prioritize your safety.",
            "That's a good question for your instructor. In general, focus on strategies that create distance and allow you to escape.",
            "I don't have specific information on that, but a key principle of self-defense is to use the minimum force necessary to ensure your safety.",
            "While I don't have details on that specific scenario, remember that the goal of self-defense is to get to safety, not to win a confrontation."
        ]
        return random.choice(safety_tips)

# SOS Functions
def get_gps_coordinates():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        loc = data["loc"].split(",")
        return {"lat": loc[0], "lon": loc[1], "city": data.get("city", "Unknown")}
    except Exception as e:
        return {"lat": "N/A", "lon": "N/A", "city": "Error: " + str(e)}

def send_sms(coords):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    message_body = f"Emergency! My location: Lat {coords['lat']}, Lon {coords['lon']} ({coords['city']}). Google Maps: https://maps.google.com/?q={coords['lat']},{coords['lon']}"
    for phone in CONTACTS["phone"]:
        client.messages.create(body=message_body, from_=TWILIO_PHONE, to=phone)

def send_email(coords):
    message_body = f"Emergency! My location: Lat {coords['lat']}, Lon {coords['lon']} ({coords['city']}). Google Maps: https://maps.google.com/?q={coords['lat']},{coords['lon']}"
    msg = MIMEText(message_body)
    msg["Subject"] = "Emergency Location Alert"
    msg["From"] = GMAIL_USER
    msg["To"] = ", ".join(CONTACTS["email"])
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, CONTACTS["email"], msg.as_string())

class SafetyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Global variables
        self.speech_enabled = True
        self.listening_mode = False
        self.wake_word = "hey defender"
        self.is_listening = False
        
        # Configure window
        self.title("Safety Assistant")
        self.geometry("800x900")
        self.minsize(700, 800)
        self.configure(bg="#E8ECEF")  # Light modern background
        
        # Load icon images
        try:
            self.icon_images = {
                'logo': self.load_image("shield.png", 50, 50) if os.path.exists("shield.png") else None,
                'mic_on': self.load_image("mic_on.png", 35, 35) if os.path.exists("mic_on.png") else None,
                'mic_off': self.load_image("mic_off.png", 35, 35) if os.path.exists("mic_off.png") else None,
                'speaker_on': self.load_image("speaker_on.png", 35, 35) if os.path.exists("speaker_on.png") else None,
                'speaker_off': self.load_image("speaker_off.png", 35, 35) if os.path.exists("speaker_off.png") else None,
                'send': self.load_image("send.png", 35, 35) if os.path.exists("send.png") else None,
                'background': self.load_image("background.jpg", 800, 900) if os.path.exists("background.jpg") else None
            }
        except Exception as e:
            print(f"Error loading images: {e}")
            self.icon_images = {key: None for key in ['logo', 'mic_on', 'mic_off', 'speaker_on', 'speaker_off', 'send', 'background']}
        
        # Set app icon if available
        if self.icon_images['logo']:
            self.iconphoto(True, self.icon_images['logo'])
        
        # Modern color scheme
        self.colors = {
            'primary': "#007BFF",    # Vibrant blue
            'secondary': "#6C757D",  # Cool gray
            'accent': "#28A745",     # Fresh green
            'background': "#E8ECEF", # Light gray
            'card': "#FFFFFF",      # White for cards
            'text': "#212529",      # Dark text
            'highlight': "#FFD700"   # Gold highlight
        }
        
        # Configure fonts
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Poppins", size=12)
        self.header_font = font.Font(family="Poppins", size=20, weight="bold")
        self.title_font = font.Font(family="Poppins", size=16, weight="bold")
        self.body_font = font.Font(family="Poppins", size=12)
        self.small_font = font.Font(family="Poppins", size=10)
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("TButton", font=self.body_font, padding=5, borderwidth=0)
        self.style.configure("TLabel", font=self.body_font)
        self.style.configure("TEntry", font=self.body_font)
        
        # Add background image if available
        if self.icon_images['background']:
            self.bg_label = tk.Label(self, image=self.icon_images['background'])
            self.bg_label.place(relwidth=1, relheight=1)
        
        # Create UI components
        self.create_header()
        self.create_chat_area()
        self.create_status_bar()
        self.create_input_area()
        self.create_sos_button()
        self.create_contact_settings()
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Initialize microphone in a separate thread
        threading.Thread(target=self.initialize_microphone, daemon=True).start()
        
        # Add welcome message
        self.display_welcome()
    
    def load_image(self, filename, width, height):
        """Load and resize image with error handling"""
        try:
            img = Image.open(filename)
            img = img.resize((width, height), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image {filename}: {e}")
            return None
    
    def create_header(self):
        """Create modern header with logo and title"""
        header_frame = tk.Frame(self, bg=self.colors['primary'], pady=15, padx=20, relief="raised", bd=2)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        if self.icon_images['logo']:
            logo_label = tk.Label(header_frame, image=self.icon_images['logo'], bg=self.colors['primary'])
            logo_label.pack(side=tk.LEFT, padx=15)
        
        title_label = tk.Label(header_frame, text="Safety Assistant", 
                              font=self.header_font, bg=self.colors['primary'], 
                              fg=self.colors['card'], pady=5)
        title_label.pack(side=tk.LEFT)
    
    def create_chat_area(self):
        """Create modern chat display area with card-like design"""
        chat_frame = tk.Frame(self, bg=self.colors['background'], padx=20, pady=15)
        chat_frame.grid(row=1, column=0, sticky="nsew", padx=10)
        chat_frame.grid_columnconfigure(0, weight=1)
        chat_frame.grid_rowconfigure(0, weight=1)
        
        chat_container = tk.Frame(chat_frame, bg=self.colors['card'], bd=0, 
                                 relief="solid", pady=10, padx=10, 
                                 highlightbackground=self.colors['secondary'], 
                                 highlightthickness=1, borderwidth=2)
        chat_container.grid(row=0, column=0, sticky="nsew")
        chat_container.grid_columnconfigure(0, weight=1)
        chat_container.grid_rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(chat_container, style="Vertical.TScrollbar")
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 5))
        
        self.chat_history = tk.Text(chat_container, wrap=tk.WORD, 
                                   yscrollcommand=scrollbar.set, 
                                   font=self.body_font, 
                                   bg=self.colors['card'],
                                   fg=self.colors['text'],
                                   padx=15, pady=15,
                                   bd=0, highlightthickness=0,
                                   relief="flat")
        self.chat_history.grid(row=0, column=0, sticky="nsew")
        self.chat_history.config(state=tk.DISABLED)
        
        scrollbar.config(command=self.chat_history.yview)
        
        self.chat_history.tag_configure("user", foreground=self.colors['primary'], 
                                        font=("Poppins", 12, "bold"))
        self.chat_history.tag_configure("bot", foreground=self.colors['accent'], 
                                        font=("Poppins", 12))
        self.chat_history.tag_configure("system", foreground=self.colors['secondary'], 
                                        font=("Poppins", 10, "italic"))
    
    def create_status_bar(self):
        """Create modern status bar with indicators"""
        status_frame = tk.Frame(self, bg=self.colors['card'], padx=20, pady=10, 
                               relief="raised", bd=1, highlightbackground=self.colors['secondary'], 
                               highlightthickness=1)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Status: Ready", 
                                    font=self.small_font, 
                                    fg=self.colors['secondary'], bg=self.colors['card'])
        self.status_label.pack(side=tk.LEFT)
        
        controls_frame = tk.Frame(status_frame, bg=self.colors['card'])
        controls_frame.pack(side=tk.RIGHT)
        
        self.speech_button = ttk.Button(controls_frame, 
                                       text="Speech: ON", 
                                       command=self.toggle_speech,
                                       style="Accent.TButton")
        if self.icon_images['speaker_on']:
            self.speech_button.config(image=self.icon_images['speaker_on'], compound=tk.LEFT)
        self.speech_button.pack(side=tk.LEFT, padx=10)
        
        self.voice_button = ttk.Button(controls_frame, 
                                      text="Voice: OFF", 
                                      command=self.toggle_listening_mode,
                                      style="Accent.TButton")
        if self.icon_images['mic_off']:
            self.voice_button.config(image=self.icon_images['mic_off'], compound=tk.LEFT)
        self.voice_button.pack(side=tk.LEFT, padx=10)
        
        self.indicator_canvas = tk.Canvas(controls_frame, width=25, height=25, 
                                        bg=self.colors['card'], 
                                        highlightthickness=0)
        self.indicator = self.indicator_canvas.create_oval(5, 5, 20, 20, 
                                                         fill=self.colors['secondary'], 
                                                         outline=self.colors['secondary'])
        self.indicator_canvas.pack(side=tk.LEFT, padx=10)
    
    def create_input_area(self):
        """Create modern user input area with send button"""
        input_frame = tk.Frame(self, bg=self.colors['background'], padx=20, pady=20)
        input_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        
        wake_frame = tk.Frame(input_frame, bg=self.colors['background'])
        wake_frame.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        wake_label = tk.Label(wake_frame, text="Wake Word:", font=self.small_font, 
                             bg=self.colors['background'], fg=self.colors['text'])
        wake_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.wake_word_entry = ttk.Entry(wake_frame, width=20, font=self.body_font, 
                                        style="Modern.TEntry")
        self.wake_word_entry.insert(0, self.wake_word)
        self.wake_word_entry.pack(side=tk.LEFT)
        
        wake_button = ttk.Button(wake_frame, text="Set", 
                                command=self.set_wake_word, 
                                style="Accent.TButton", width=6)
        wake_button.pack(side=tk.LEFT, padx=10)
        
        input_container = tk.Frame(input_frame, bg=self.colors['card'], bd=0, 
                                  relief="solid", pady=10, padx=10, 
                                  highlightbackground=self.colors['secondary'], 
                                  highlightthickness=1)
        input_container.grid(row=1, column=0, sticky="ew")
        input_container.grid_columnconfigure(0, weight=1)
        
        self.entry = tk.Text(input_container, height=3, 
                            font=self.body_font, 
                            bg=self.colors['card'], fg=self.colors['text'],
                            padx=15, pady=10,
                            bd=0, highlightthickness=0,
                            wrap=tk.WORD, relief="flat")
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<Return>", self.send_on_enter)
        self.entry.bind("<Shift-Return>", lambda e: None)
        
        send_button = ttk.Button(input_container, 
                                text="Send", 
                                command=self.send_message,
                                style="Accent.TButton", width=10)
        if self.icon_images['send']:
            send_button.config(image=self.icon_images['send'], compound=tk.LEFT)
        send_button.grid(row=0, column=1, padx=10, pady=5)  # Fixed column syntax
    
    def create_sos_button(self):
        """Create SOS button below input area"""
        sos_frame = tk.Frame(self, bg=self.colors['background'])
        sos_frame.grid(row=4, column=0, pady=20)
        self.sos_button = tk.Button(sos_frame, text="SOS", font=("Arial", 20, "bold"), 
                                   bg="#FF4444", fg="white", command=self.send_alert, 
                                   width=10, height=2)
        self.sos_button.pack()
    
    def create_contact_settings(self):
        """Create settings area for user to input phone and email"""
        settings_frame = tk.Frame(self, bg=self.colors['background'], padx=20, pady=10)
        settings_frame.grid(row=5, column=0, sticky="ew", padx=10)
        
        # Phone number input
        phone_label = tk.Label(settings_frame, text="Phone Number (e.g., +1234567890):", 
                              font=self.small_font, bg=self.colors['background'], fg=self.colors['text'])
        phone_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.phone_entry = ttk.Entry(settings_frame, width=20, font=self.body_font)
        self.phone_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Email input
        email_label = tk.Label(settings_frame, text="Email:", 
                              font=self.small_font, bg=self.colors['background'], fg=self.colors['text'])
        email_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.email_entry = ttk.Entry(settings_frame, width=20, font=self.body_font)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Set button
        set_button = ttk.Button(settings_frame, text="Set Contacts", command=self.update_contacts, 
                               style="Accent.TButton", width=15)
        set_button.grid(row=2, column=1, pady=10)
    
    def update_contacts(self):
        """Update CONTACTS dictionary with user input"""
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        
        CONTACTS["phone"] = [phone] if phone else []
        CONTACTS["email"] = [email] if email else []
        
        self.add_system_message(f"Contacts updated - Phone: {phone or 'None'}, Email: {email or 'None'}")
    
    def initialize_microphone(self):
        """Initialize microphone in background"""
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
            self.update_status("Microphone initialized and ready")
        except Exception as e:
            self.update_status(f"Microphone initialization failed: {str(e)}")
    
    def toggle_speech(self):
        """Toggle speech output on/off"""
        self.speech_enabled = not self.speech_enabled
        status = "enabled" if self.speech_enabled else "disabled"
        self.add_system_message(f"Speech output {status}")
        self.speech_button.config(text=f"Speech: {'ON' if self.speech_enabled else 'OFF'}")
        if self.speech_enabled and self.icon_images['speaker_on']:
            self.speech_button.config(image=self.icon_images['speaker_on'])
        elif not self.speech_enabled and self.icon_images['speaker_off']:
            self.speech_button.config(image=self.icon_images['speaker_off'])
    
    def toggle_listening_mode(self):
        """Toggle voice recognition on/off"""
        self.listening_mode = not self.listening_mode
        if self.listening_mode:
            self.voice_button.config(text="Voice: ON")
            if self.icon_images['mic_on']:
                self.voice_button.config(image=self.icon_images['mic_on'])
            self.update_status(f"Listening for wake word '{self.wake_word}'")
            self.update_indicator('secondary')
            threading.Thread(target=self.voice_recognition_loop, daemon=True).start()
        else:
            self.voice_button.config(text="Voice: OFF")
            if self.icon_images['mic_off']:
                self.voice_button.config(image=self.icon_images['mic_off'])
            self.update_status("Voice recognition inactive")
            self.update_indicator('secondary')
    
    def set_wake_word(self):
        """Update the wake word for voice activation"""
        new_word = self.wake_word_entry.get().strip().lower()
        if new_word:
            self.wake_word = new_word
            self.add_system_message(f"Wake word set to '{self.wake_word}'")
            if self.listening_mode:
                self.update_status(f"Listening for wake word '{self.wake_word}'")
    
    def update_status(self, message):
        """Update status label safely from any thread"""
        def update():
            self.status_label.config(text=f"Status: {message}")
        self.after(0, update)
    
    def update_indicator(self, color):
        """Update the indicator light color safely from any thread"""
        def update():
            self.indicator_canvas.itemconfig(self.indicator, fill=self.colors[color])
        self.after(0, update)
    
    def add_system_message(self, message):
        """Add system message to chat history"""
        def update():
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.insert(tk.END, f"System: {message}\n", "system")
            self.chat_history.config(state=tk.DISABLED)
            self.chat_history.see(tk.END)
        self.after(0, update)
    
    def display_welcome(self):
        """Display and speak welcome message"""
        welcome = "Welcome! I'm your Safety Assistant. Ask me about self-defense techniques or set your contacts below and press SOS to send your location."
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, "Assistant: " + welcome + "\n", "bot")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)
        if self.speech_enabled:
            tts_engine.say(welcome)
            tts_engine.runAndWait()
    
    def send_on_enter(self, event):
        """Handle Enter key press to send message"""
        self.send_message()
        return "break"
    
    def send_message(self):
        """Process and send user message"""
        user_input = self.entry.get("1.0", tk.END).strip()
        if not user_input:
            return
        self.entry.delete("1.0", tk.END)
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, "You: " + user_input + "\n", "user")
        if user_input.lower() in ["bye", "goodbye", "exit", "quit"]:
            response = "Stay safe! If you need more help in the future, just come back."
            self.chat_history.insert(tk.END, "Assistant: " + response + "\n", "bot")
        else:
            response = get_response(user_input)
            self.chat_history.insert(tk.END, "Assistant: " + response + "\n", "bot")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)
        if self.speech_enabled:
            tts_engine.say(response)
            tts_engine.runAndWait()
    
    def process_voice_input(self, text):
        """Process recognized voice input"""
        if not text:
            return
        def update_chat():
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.insert(tk.END, f"You: {text}\n", "user")
            self.chat_history.config(state=tk.DISABLED)
            self.chat_history.see(tk.END)
        self.after(0, update_chat)
        response = get_response(text)
        def update_response():
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.insert(tk.END, f"Assistant: {response}\n", "bot")
            self.chat_history.config(state=tk.DISABLED)
            self.chat_history.see(tk.END)
        self.after(0, update_response)
        if self.speech_enabled:
            tts_engine.say(response)
            tts_engine.runAndWait()
    
    def voice_recognition_loop(self):
        """Continuously listen for voice input"""
        self.is_listening = True
        try:
            with sr.Microphone() as source:
                while self.listening_mode and self.is_listening:
                    try:
                        self.update_status("Listening for wake word...")
                        self.update_indicator('secondary')
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        text = recognizer.recognize_google(audio).lower()
                        if self.wake_word.lower() in text:
                            self.update_status("Wake word detected! What's your question?")
                            self.update_indicator('accent')
                            self.add_system_message("Wake word detected, listening for your question...")
                            try:
                                question_audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
                                question_text = recognizer.recognize_google(question_audio)
                                self.update_status("Processing your question...")
                                self.process_voice_input(question_text)
                            except sr.WaitTimeoutError:
                                self.add_system_message("No question detected, listening again...")
                            except sr.UnknownValueError:
                                self.add_system_message("Sorry, I couldn't understand your question. Please try again.")
                            except Exception as e:
                                self.add_system_message(f"Error processing question: {str(e)}")
                            self.update_status(f"Listening for wake word '{self.wake_word}'")
                            self.update_indicator('secondary')
                    except sr.WaitTimeoutError:
                        pass
                    except sr.UnknownValueError:
                        pass
                    except Exception as e:
                        self.update_status(f"Error in voice recognition: {str(e)}")
                        time.sleep(2)
        except Exception as e:
            self.update_status(f"Voice recognition error: {str(e)}")
            self.add_system_message(f"Voice recognition stopped due to error: {str(e)}")
            self.listening_mode = False
            self.voice_button.config(text="Voice: OFF")
            if self.icon_images['mic_off']:
                self.voice_button.config(image=self.icon_images['mic_off'])
        self.is_listening = False
        self.update_status("Voice recognition inactive")
        self.update_indicator('secondary')
    
    def send_alert(self):
        """Send SOS alert with GPS coordinates"""
        if not CONTACTS["phone"] and not CONTACTS["email"]:
            self.add_system_message("No contacts set! Please enter a phone number or email below.")
            messagebox.showwarning("Warning", "No contacts set! Please enter a phone number or email.")
            return
        
        coords = get_gps_coordinates()
        try:
            threading.Thread(target=lambda: (send_sms(coords) if CONTACTS["phone"] else None, 
                                           send_email(coords) if CONTACTS["email"] else None), 
                            daemon=True).start()
            self.add_system_message("Emergency alerts sent to your contacts!")
            messagebox.showinfo("Success", "Emergency alerts sent!")
        except Exception as e:
            self.add_system_message(f"Failed to send alerts: {str(e)}")
            messagebox.showerror("Error", f"Failed to send: {str(e)}")

if __name__ == "__main__":
    app = SafetyApp()
    app.mainloop()