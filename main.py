import google.generativeai as genai
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

genai.configure(api_key="AIzaSyBHI79Y0OizTCYkOLYUmzVz0tLJX7InMH8")
model = genai.GenerativeModel("gemini-1.5-flash")


class AgentApp(App):

    def build(self):
        layout = BoxLayout(orientation="vertical")
        self.input_text = TextInput(
            hint_text="Type your message...", size_hint_y=0.2
        )
        self.output_text = TextInput(readonly=True, size_hint_y=0.6)
        btn = Button(text="Send to Agent", size_hint_y=0.2)
        btn.bind(on_press=self.send_msg)

        layout.add_widget(self.output_text)
        layout.add_widget(self.input_text)
        layout.add_widget(btn)
        return layout

    def send_msg(self, instance):
        user_input = self.input_text.text
        if user_input:
            try:
                res = model.generate_content(user_input)
                self.output_text.text += (
                    f"\nUser: {user_input}\nAgent: {res.text}\n"
                )
            except Exception as e:
                self.output_text.text += f"\nError: {e}\n"
            self.input_text.text = ""


if __name__ == "__main__":
    AgentApp().run()
