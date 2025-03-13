from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Ellipse, Color, Line
from kivy.animation import Animation
import speech_recognition as sr
import pyttsx3
import wikipedia
import pyjokes
import pywhatkit
import datetime
import requests
import os
import openai

# Initialize recognizer and speech engine
listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# OpenAI API Key
openai.api_key = "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"

# Function to speak
def talk(text):
    engine.say(text)
    engine.runAndWait()

# Function to take voice command
def take_command():
    try:
        with sr.Microphone() as source:
            print("Listening...")
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'alpha' in command:
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
    else:
        talk("Let me check that for you.")
        response = ask_openai(command)
        talk(response)

# Kivy UI Class with Animation
class AnimatedMic(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0, 1, 0, 1)
            self.outer_ring = Line(circle=(self.center_x, self.center_y, 60), width=2)
            self.circle = Ellipse(pos=(self.center_x-50, self.center_y-50), size=(100, 100))
        self.animate()

    def animate(self):
        anim = Animation(width=4, duration=0.5) + Animation(width=2, duration=0.5)
        anim.repeat = True
        anim.start(self.outer_ring)

    def react_to_voice(self):
        anim = Animation(width=6, duration=0.3) + Animation(width=2, duration=0.3)
        anim.start(self.outer_ring)

class VoiceAssistantApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.label = Label(text='ALPHA', font_size='30sp')
        self.mic_visual = AnimatedMic()
        layout.add_widget(self.mic_visual)
        layout.add_widget(self.label)
        return layout
    
    def on_start(self):
        self.listen_for_wake_word()
    
    def listen_for_wake_word(self):
        while True:
            command = take_command()
            if command:
                self.label.text = "You said: " + command
                self.mic_visual.react_to_voice()
                run_alpha(command)

# Run the app
if __name__ == '__main__':
    VoiceAssistantApp().run()
