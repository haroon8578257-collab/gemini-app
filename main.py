import threading
import time
import os
from flask import Flask, request, jsonify, render_template_string
import requests

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform

# ---------------- FLASK BACKEND ----------------

app = Flask(__name__)

# API key ab environment variable se aayegi (hardcode nahi hai)
API_KEY = os.environ.get("GEMINI_API_KEY", "")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chafre Agent</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; margin: 0; padding: 15px; }
        h2 { text-align: center; color: #0088cc; }
        #chatbox { height: 70vh; overflow-y: auto; border: 1px solid #333; padding: 10px; border-radius: 8px; background: #1e1e1e; margin-bottom: 10px; }
        .msg { margin-bottom: 10px; padding: 8px 12px; border-radius: 6px; }
        .user { background: #005c4b; text-align: right; }
        .agent { background: #262d31; text-align: left; }
        .input-area { display: flex; gap: 5px; }
        input { flex: 1; padding: 12px; border: none; border-radius: 5px; font-size: 16px; }
        button { padding: 12px 18px; background: #0088cc; color: white; border: none; border-radius: 5px; font-weight: bold; }
    </style>
</head>
<body>
    <h2>Chafre Agent</h2>
    <div id="chatbox"></div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Type a message...">
        <button onclick="sendMsg()">Send</button>
    </div>
    <script>
        async function sendMsg() {
            let input = document.getElementById("userInput");
            let chat = document.getElementById("chatbox");
            let text = input.value.trim();
            if (!text) return;
            chat.innerHTML += `<div class="msg user"><b>You:</b> ${text}</div>`;
            input.value = "";
            chat.scrollTop = chat.scrollHeight;
            try {
                let response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                let data = await response.json();
                chat.innerHTML += `<div class="msg agent"><b>Agent:</b> ${data.reply}</div>`;
            } catch (e) {
                chat.innerHTML += `<div class="msg agent" style="color:red;">Error connecting to server</div>`;
            }
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get("message", "")
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": user_msg}]}]}
    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=30)
        data = response.json()
        reply = data['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

def run_flask():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)


# ---------------- KIVY FRONTEND (WebView wrapper) ----------------

class ChafreApp(App):
    def build(self):
        # Flask ko background thread mein start karein
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        time.sleep(1.5)  # server ko boot hone ka thoda time dein

        root = BoxLayout()

        if platform == "android":
            self.load_android_webview(root)
        else:
            # Desktop/test ke liye fallback: browser mein khol dein
            import webbrowser
            webbrowser.open("http://127.0.0.1:5000")
            from kivy.uix.label import Label
            root.add_widget(Label(text="Chafre Agent running at http://127.0.0.1:5000"))

        return root

    def load_android_webview(self, root):
        from jnius import autoclass, cast
        from android.runnable import run_on_ui_thread

        WebView = autoclass('android.webkit.WebView')
        WebViewClient = autoclass('android.webkit.WebViewClient')
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        layout = autoclass('android.widget.FrameLayout')(activity)

        @run_on_ui_thread
        def setup_webview():
            webview = WebView(activity)
            webview.getSettings().setJavaScriptEnabled(True)
            webview.setWebViewClient(WebViewClient())
            webview.loadUrl("http://127.0.0.1:5000")
            activity.setContentView(webview)

        setup_webview()


if __name__ == '__main__':
    ChafreApp().run()
