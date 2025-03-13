from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.clock import Clock
import threading
import speech_recognition as sr
from gtts import gTTS
import wikipedia
import pyjokes
import pywhatkit
import datetime
import requests
import os
import openai
from playsound import playsound
import time
import subprocess

# Initialize recognizer
listener = sr.Recognizer()

# OpenAI API Key
openai.api_key = "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"

# Function to speak with gTTS
def talk(text):
    tts = gTTS(text=text, lang="en", slow=True)
    filename = "response.mp3"
    tts.save(filename)
    threading.Thread(target=playsound, args=(filename,), daemon=True).start()
    time.sleep(2)  # Give time for speech to play
    os.remove(filename)  # Clean up the file

# Function to take voice command
def take_command():
    try:
        with sr.Microphone() as source:
            print("Listening...")
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'alpha' in command:
                talk("Yes, I am listening")
                return command.replace('alpha', '').strip()
    except:
        return ""
    return ""

# Get Weather Information
def get_weather():
    api_key = "7fb09907406407fd4ab4790efbade607"
    city = "Ruiru,Kenya"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url).json()
    if response["cod"] != "404":
        weather = response["weather"][0]["description"]
        temp = response["main"]["temp"]
        talk(f"The weather in {city} is {weather} with a temperature of {temp} degrees Celsius.")
    else:
        talk("Sorry, I couldn't fetch the weather details.")

# Fetch News
def get_news():
    talk("Fetching the latest news headlines.")
    url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=00ddfde1d6e64e748870a5ac781deb18"
    response = requests.get(url).json()
    articles = response["articles"][:5]
    for article in articles:
        talk(article["title"])

# Get AI-generated response from OpenAI
def ask_openai(question):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}]
    )
    return response["choices"][0]["message"]["content"]

# Open Applications
def open_application(command):
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "chrome.exe",
        "whatsapp": "C:\\Program Files\\WindowsApps\\WhatsApp.WhatsAppDesktop_2.2142.12.0_x64__8x8jfqn7c6gh2\\app\\WhatsApp.exe",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "twitter": "https://www.twitter.com",
        "snapchat": "https://www.snapchat.com",
        "tiktok": "https://www.tiktok.com"
    }
    
    for app in apps:
        if app in command:
            if apps[app].startswith("http"):
                talk(f"Opening {app}")
                subprocess.run(["cmd", "/c", "start", apps[app]])
            elif os.path.exists(apps[app]):
                talk(f"Opening {app}")
                subprocess.run(apps[app])
            else:
                talk(f"I couldn't find {app} on your system.")
            return
    talk("I couldn't find that application.")

# AI Assistant Functionalities
def run_alpha(command):
    if 'play' in command:
        song = command.replace('play', '').strip()
        talk('Playing ' + song)
        pywhatkit.playonyt(song)
    elif 'search' in command:
        query = command.replace('search', '').strip()
        talk('Searching for ' + query)
        pywhatkit.search(query)
    elif 'time' in command:
        time_now = datetime.datetime.now().strftime('%I:%M %p')
        talk('Current time is ' + time_now)
    elif 'who is' in command:
        person = command.replace('who is', '').strip()
        try:
            info = wikipedia.summary(person, 1)
            talk(info)
        except:
            talk("I couldn't find any information.")
    elif 'joke' in command:
        talk(pyjokes.get_joke())
    elif 'weather' in command:
        get_weather()
    elif 'news' in command:
        get_news()
    elif 'open' in command:
        open_application(command)
    else:
        talk("Let me check that for you.")
        response = ask_openai(command)
        talk(response)

# Kivy UI Class with Online Background Animation
class VoiceAssistantApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Background Image
        self.background = AsyncImage(source="https://i.imgur.com/0sdbcm8.jpeg", allow_stretch=True, keep_ratio=False)
        layout.add_widget(self.background)
        
        Clock.schedule_once(self.startup_message, 1)  # Display startup message
        Clock.schedule_interval(self.listen_for_wake_word, 2)  # Check for wake word every 2 seconds
        return layout

    def startup_message(self, dt):
        talk("Hey there buddy")

    def listen_for_wake_word(self, dt):
        def recognize():
            command = take_command()
            if command:
                run_alpha(command)
        
        threading.Thread(target=recognize, daemon=True).start()

# Run the app
if __name__ == '__main__':
    VoiceAssistantApp().run()
