# Self-defense-chat-bot
A prototype chatbot that provides simple, safety-oriented responses. Built with a basic Tkinter GUI and an SOS button. This prototype showcases skills in Python, GUI development NLP, and API integration, with a focus on user safety.

## Status 
- **prototype**: Works for predfined prompts.
- Knowns issues: Not yet robust to free-form input; some environments may need dependencies installed.

## Features 
- Self-Defense Chatbot: Responds to queries about techniques (e.g., escaping chokehold, pressure points) using NLTK and TF-IDF vectorization.
- Basic GUI (Tkinter): Features a Tkinter-based interface with a chat area, status indicators, and contact settings, styled with custom colors and fonts.
- SOS button hook: Sends location-based alerts via SMS (Twilio) and email (Gmail) to user-defined contacts.
- Voice Interaction: Supports voice input (SpeechRecognition) and output (pyttsx3) with a customizable wake word for hands-free use.
- Contact management: Allows users to set emergency phone and email contacts with the app.

## Tech Stack 
- Python (3.10+ recommended)
- Libraries:
  - GUI: Tkinter
  - NLP: NLTK (tokenization, stemming), scikit-learn (TF-IDF, cosine similarity)
  - Voice: pyttsx (text-to-speech), SpeechRecognition (voice input)

## Setup
'''bash 
python -m venv .venv

# Windows 
.venv/Scripts/activate
pip install -r requirements.txt 
