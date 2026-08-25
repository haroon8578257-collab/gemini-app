from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import requests
import json
import threading

API_KEY = "AIzaSyBHI79Y0OizTCYkOLYUmzVz0tLJX7InMH8"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

class AgentApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.output_text = TextInput(readonly=True, size_hint_y=0.8, multiline=True)
        self.input_text = TextInput(hint_text="Type message here...", size_hint_y=0.1, multiline=False)
        btn = Button(text="Send to Agent", size_hint_y=0.1)
        btn.bind(on_press=self.start_thread)

        layout.add_widget(self.output_text)
        layout.add_widget(self.input_text)
        layout.add_widget(btn)
        return layout

    def start_thread(self, instance):
        threading.Thread(target=self.send_msg).start()

    def send_msg(self):
        user_input = self.input_text.text
        if not user_input:
            return
        
        self.output_text.text += f"\nYou: {user_input}"
        self.input_text.text = ""

        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": user_input}]}]}

        try:
            response = requests.post(URL, headers=headers, data=json.dumps(payload))
            data = response.json()
            reply = data['candidates'][0]['content']['parts'][0]['text']
            self.output_text.text += f"\nAgent: {reply}\n"
        except Exception as e:
            self.output_text.text += f"\nError: {str(e)}\n"

if __name__ == '__main__':
    AgentApp().run()
    
