import pygame
import pygame.camera
import requests
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading
import os
from gtts import gTTS
import pygame.mixer
from tempfile import NamedTemporaryFile
from translate import Translator as AltTranslator

# Define constants
API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
API_KEY = "USE YOUR OWN API"
IMAGE_FILE = "file.jpg"
CAPTION = "No caption yet"
time_counter = 0

# Initialize the alternate translator
alt_translator = AltTranslator(to_lang='en')

# Initialize pygame mixer for audio
pygame.mixer.init()

# Language configuration
LANGUAGES = {
    # Indian Languages
    'en': {'name': 'English', 'code': 'en'},
    'ta': {'name': 'Tamil', 'code': 'ta'},
    'kn': {'name': 'Kannada', 'code': 'kn'},
    'hi': {'name': 'Hindi', 'code': 'hi'},
    'ml': {'name': 'Malayalam', 'code': 'ml'},
    'te': {'name': 'Telugu', 'code': 'te'},
    'bn': {'name': 'Bengali', 'code': 'bn'},
    'gu': {'name': 'Gujarati', 'code': 'gu'},
    'mr': {'name': 'Marathi', 'code': 'mr'},
    'pa': {'name': 'Punjabi', 'code': 'pa'},
    'ur': {'name': 'Urdu', 'code': 'ur'},
    'or': {'name': 'Odia', 'code': 'or'},
    'as': {'name': 'Assamese', 'code': 'as'},
    'sa': {'name': 'Sanskrit', 'code': 'sa'},
    'sd': {'name': 'Sindhi', 'code': 'sd'},
    'mai': {'name': 'Maithili', 'code': 'mai'},
    'bho': {'name': 'Bhojpuri', 'code': 'bho'},
    'mni': {'name': 'Manipuri', 'code': 'mni'},
    'kok': {'name': 'Konkani', 'code': 'kok'},
    'ks': {'name': 'Kashmiri', 'code': 'ks'},
    # Asian Languages
    'zh': {'name': 'Chinese', 'code': 'zh-cn'},
    'ja': {'name': 'Japanese', 'code': 'ja'},
    'ko': {'name': 'Korean', 'code': 'ko'},
    'vi': {'name': 'Vietnamese', 'code': 'vi'},
    'th': {'name': 'Thai', 'code': 'th'},
    'ms': {'name': 'Malay', 'code': 'ms'},
    'id': {'name': 'Indonesian', 'code': 'id'},
    # European Languages
    'fr': {'name': 'French', 'code': 'fr'},
    'es': {'name': 'Spanish', 'code': 'es'},
    'de': {'name': 'German', 'code': 'de'},
    'it': {'name': 'Italian', 'code': 'it'},
    'ru': {'name': 'Russian', 'code': 'ru'},
    'pt': {'name': 'Portuguese', 'code': 'pt'},
    'pl': {'name': 'Polish', 'code': 'pl'},
    'nl': {'name': 'Dutch', 'code': 'nl'},
    'el': {'name': 'Greek', 'code': 'el'},
    'ro': {'name': 'Romanian', 'code': 'ro'},
    'tr': {'name': 'Turkish', 'code': 'tr'},
    'uk': {'name': 'Ukrainian', 'code': 'uk'},
    'sv': {'name': 'Swedish', 'code': 'sv'},
    # Middle Eastern and African Languages
    'ar': {'name': 'Arabic', 'code': 'ar'},
    'fa': {'name': 'Persian', 'code': 'fa'},
    'he': {'name': 'Hebrew', 'code': 'he'},
    'am': {'name': 'Amharic', 'code': 'am'},
    'sw': {'name': 'Swahili', 'code': 'sw'},
    'zu': {'name': 'Zulu', 'code': 'zu'},
    'xh': {'name': 'Xhosa', 'code': 'xh'},
    # Others
    'tl': {'name': 'Tagalog', 'code': 'tl'},
    'haw': {'name': 'Hawaiian', 'code': 'haw'}
}


current_language = 'en'

def translate_text(text, target_lang):
    try:
        global alt_translator
        if target_lang == 'en':
            return text
        alt_translator = AltTranslator(to_lang=target_lang)
        translation = alt_translator.translate(text)
        return translation
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def speak_caption(caption, language):
    try:
        # Create a temporary file for the audio
        temp_file = NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_filename = temp_file.name
        temp_file.close()

        # Generate speech
        tts = gTTS(text=caption, lang=language)
        tts.save(temp_filename)

        # Play the audio
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # Clean up
        pygame.mixer.music.unload()
        os.unlink(temp_filename)

    except Exception as e:
        print(f"Text-to-speech error: {e}")

# Initialize camera
pygame.camera.init()
camlist = pygame.camera.list_cameras()

def capture():
    if camlist:
        cam = pygame.camera.Camera(camlist[0], (640, 480))
        cam.start()
        image = cam.get_image()
        pygame.image.save(image, IMAGE_FILE)
        cam.stop()
        print(f"Image captured and saved as {IMAGE_FILE}")
    else:
        print("Your device cannot run this script.")

def query(filename):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)
    return response.json()

def define():
    global CAPTION
    try:
        response = query(IMAGE_FILE)
        if isinstance(response, list) and len(response) > 0:
            english_caption = response[0].get("generated_text", "No caption generated")
            translated_caption = translate_text(english_caption, current_language)
            CAPTION = translated_caption
            speak_caption(CAPTION, current_language)
        else:
            CAPTION = "Unexpected response format"
        print(f"Caption generated: {CAPTION}")
    except Exception as e:
        CAPTION = f"Error: {e}"
        print(f"Error generating caption: {e}")

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project ZETA</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #007bff;
            --secondary-color: #6c757d;
            --background-color: #f4f4f4;
            --text-color: #333;
            --border-color: #ddd;
            --menu-bg: white;
            --shadow-color: rgba(0, 0, 0, 0.1);
        }

        [data-theme="dark"] {
            --primary-color: #0d6efd;
            --secondary-color: #adb5bd;
            --background-color: #212529;
            --text-color: #f8f9fa;
            --border-color: #495057;
            --menu-bg: #343a40;
            --shadow-color: rgba(255, 255, 255, 0.1);
        }

        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background-color: var(--background-color);
            color: var(--text-color);
            transition: all 0.3s ease;
        }

        h1 {
            color: var(--primary-color);
            text-align: center;
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 10px;
            margin-top: 60px;
        }

        #capturedImage {
            display: block;
            max-width: 100%;
            height: auto;
            margin: 20px auto;
            border: 2px solid var(--primary-color);
            border-radius: 8px;
            box-shadow: 0 4px 6px var(--shadow-color);
        }

        #caption {
            display: block;
            background-color: var(--menu-bg);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-style: italic;
            margin: 20px 0;
            box-shadow: 0 2px 4px var(--shadow-color);
        }

        .refresh-note {
            text-align: center;
            color: var(--secondary-color);
            font-size: 0.9em;
        }

        /* Hamburger Menu */
        .menu-container {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 1000;
        }

        .hamburger-icon {
            font-size: 24px;
            width: 45px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary-color);
            background: var(--menu-bg);
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 2px 5px var(--shadow-color);
            transition: transform 0.3s ease;
            border: none;
        }

        .hamburger-icon:hover {
            transform: scale(1.1);
        }

        .menu-content {
            display: none;
            position: fixed;
            left: -300px;
            top: 0;
            width: 300px;
            height: 100vh;
            background-color: var(--menu-bg);
            border-right: 1px solid var(--border-color);
            box-shadow: 2px 0 5px var(--shadow-color);
            overflow-y: auto;
            transition: left 0.3s ease;
            z-index: 1001;
        }

        .menu-content.active {
            left: 0;
        }

        .menu-section {
            border-bottom: 1px solid var(--border-color);
            padding: 10px 0;
        }

        .menu-section-title {
            padding: 10px 15px;
            font-weight: bold;
            color: var(--primary-color);
            background-color: var(--background-color);
        }

        .menu-item {
            padding: 12px 20px;
            cursor: pointer;
            transition: background-color 0.2s;
            color: var(--text-color);
            text-decoration: none;
            display: block;
            border: none;
            background: none;
            width: 100%;
            text-align: left;
            font-size: 1rem;
        }

        .menu-item:hover {
            background-color: var(--primary-color);
            color: white;
        }

        .search-container {
            padding: 15px;
            position: sticky;
            top: 0;
            background-color: var(--menu-bg);
            z-index: 2;
            border-bottom: 1px solid var(--border-color);
        }

        .search-box {
            width: 100%;
            padding: 10px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            background-color: var(--background-color);
            color: var(--text-color);
        }

        .theme-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 45px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            background: var(--menu-bg);
            cursor: pointer;
            box-shadow: 0 2px 5px var(--shadow-color);
            border: none;
            color: var(--text-color);
            z-index: 1000;
        }

        .overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 1000;
        }

        /* Close button */
        .close-menu {
            position: absolute;
            top: 10px;
            right: 10px;
            background: none;
            border: none;
            font-size: 24px;
            color: var(--text-color);
            cursor: pointer;
            padding: 5px;
            z-index: 1002;
        }

        .menu-header {
            position: sticky;
            top: 0;
            background-color: var(--menu-bg);
            padding: 15px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 1002;
        }

        .menu-title {
            font-size: 1.2rem;
            font-weight: bold;
            color: var(--primary-color);
        }
    </style>
    <script>
        let isDarkTheme = false;

        function toggleMenu(event) {
            event.stopPropagation();
            const menu = document.getElementById('menuContent');
            const overlay = document.getElementById('overlay');
            menu.style.display = 'block';
            overlay.style.display = 'block';
            setTimeout(() => {
                menu.classList.add('active');
            }, 10);
        }

        function closeMenu(event) {
            if (event) {
                event.stopPropagation();
            }
            const menu = document.getElementById('menuContent');
            const overlay = document.getElementById('overlay');
            menu.classList.remove('active');
            setTimeout(() => {
                menu.style.display = 'none';
                overlay.style.display = 'none';
            }, 300);
        }

        function toggleTheme(event) {
            event.stopPropagation();
            isDarkTheme = !isDarkTheme;
            document.documentElement.setAttribute('data-theme', isDarkTheme ? 'dark' : 'light');
            const themeIcon = document.getElementById('themeIcon');
            themeIcon.className = isDarkTheme ? 'fas fa-sun' : 'fas fa-moon';
        }

        function changeLanguage(langCode, event) {
            event.stopPropagation();
            fetch(`/change_language?lang=${langCode}`)
                .then(response => response.text())
                .then(data => {
                    console.log('Language changed:', data);
                    refreshContent();
                    closeMenu();
                })
                .catch(error => console.error('Error changing language:', error));
        }

        function refreshContent(event) {
            if (event) {
                event.stopPropagation();
            }
            document.getElementById('capturedImage').src = '/image?rand=' + Math.random();
            fetch('/caption')
                .then(response => response.text())
                .then(data => {
                    document.getElementById('caption').innerText = data;
                })
                .catch(error => {
                    console.error('Error refreshing caption:', error);
                    document.getElementById('caption').innerText = 'Error loading caption';
                });
        }

        function filterLanguages(event) {
            event.stopPropagation();
            const searchInput = document.getElementById('searchBox').value.toLowerCase();
            const sections = document.querySelectorAll('.menu-section');
            
            sections.forEach(section => {
                const items = section.querySelectorAll('.menu-item');
                let hasVisibleItems = false;
                
                items.forEach(item => {
                    if (item.innerText.toLowerCase().includes(searchInput)) {
                        item.style.display = 'block';
                        hasVisibleItems = true;
                    } else {
                        item.style.display = 'none';
                    }
                });
                
                section.style.display = hasVisibleItems ? 'block' : 'none';
            });
        }

        window.onload = refreshContent;
    </script>
</head>
<body>
    <button class="hamburger-icon" onclick="toggleMenu(event)">
        <i class="fas fa-bars"></i>
    </button>

    <button class="theme-toggle" onclick="toggleTheme(event)">
        <i id="themeIcon" class="fas fa-moon"></i>
    </button>

    <div id="overlay" class="overlay" onclick="closeMenu(event)"></div>

    <div id="menuContent" class="menu-content">
        <div class="menu-header">
            <span class="menu-title">Menu</span>
            <button class="close-menu" onclick="closeMenu(event)">
                <i class="fas fa-times"></i>
            </button>
        </div>

        <div class="search-container">
            <input type="text" id="searchBox" class="search-box" placeholder="Search languages..." oninput="filterLanguages(event)">
        </div>

        <div class="menu-section">
            <div class="menu-section-title">Actions</div>
            <button class="menu-item" onclick="refreshContent(event)">
                <i class="fas fa-sync-alt"></i> Refresh Content
            </button>
        </div>

        <div class="menu-section">
            <div class="menu-section-title">Indian Languages</div>
            <button class="menu-item" onclick="changeLanguage('hi', event)">Hindi</button>
            <button class="menu-item" onclick="changeLanguage('ta', event)">Tamil</button>
            <button class="menu-item" onclick="changeLanguage('te', event)">Telugu</button>
            <button class="menu-item" onclick="changeLanguage('kn', event)">Kannada</button>
            <button class="menu-item" onclick="changeLanguage('ml', event)">Malayalam</button>
            <button class="menu-item" onclick="changeLanguage('bn', event)">Bengali</button>
            <button class="menu-item" onclick="changeLanguage('gu', event)">Gujarati</button>
            <button class="menu-item" onclick="changeLanguage('pa', event)">Punjabi</button>
            <button class="menu-item" onclick="changeLanguage('mr', event)">Marathi</button>
        </div>

        <div class="menu-section">
            <div class="menu-section-title">East Asian Languages</div>
            <button class="menu-item" onclick="changeLanguage('zh', event)">Chinese</button>
            <button class="menu-item" onclick="changeLanguage('ja', event)">Japanese</button>
            <button class="menu-item" onclick="changeLanguage('ko', event)">Korean</button>
            <button class="menu-item" onclick="changeLanguage('vi', event)">Vietnamese</button>
            <button class="menu-item" onclick="changeLanguage('th', event)">Thai</button>
        </div>

        <div class="menu-section">
            <div class="menu-section-title">European Languages</div>
            <button class="menu-item" onclick="changeLanguage('en', event)">English</button>
            <button class="menu-item" onclick="changeLanguage('es', event)">Spanish</button>
            <button class="menu-item" onclick="changeLanguage('fr', event)">French</button>
            <button class="menu-item" onclick="changeLanguage('de', event)">German</button>
            <button class="menu-item" onclick="changeLanguage('it', event)">Italian</button>
            <button class="menu-item" onclick="changeLanguage('ru', event)">Russian</button>
            <button class="menu-item" onclick="changeLanguage('pt', event)">Portuguese</button>
        </div>

        <div class="menu-section">
            <div class="menu-section-title">Middle Eastern Languages</div>
            <button class="menu-item" onclick="changeLanguage('ar', event)">Arabic</button>
            <button class="menu-item" onclick="changeLanguage('he', event)">Hebrew</button>
            <button class="menu-item" onclick="changeLanguage('fa', event)">Persian</button>
            <button class="menu-item" onclick="changeLanguage('tr', event)">Turkish</button>
        </div>
    </div>

    <h1>Project ZETA</h1>

    <div id="caption-container">
        <strong>Caption:</strong> 
        <span id="caption">Loading...</span>
    </div>

    <img id="capturedImage" src="/image" alt="Captured Image">

    <p class="refresh-note">Image and caption auto-refresh every 5 seconds</p>
</body>
</html>
"""

class ImageRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/image"):
            if os.path.exists(IMAGE_FILE):
                self.send_response(200)
                self.send_header("Content-type", "image/jpeg")
                self.end_headers()
                with open(IMAGE_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Image not found")
        elif self.path == "/caption":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(CAPTION.encode("utf-8"))
        elif self.path.startswith("/change_language"):
            global current_language
            query_components = dict(q.split("=") for q in self.path.split("?")[1].split("&"))
            new_lang = query_components.get("lang", "en")
            if new_lang in LANGUAGES:
                current_language = new_lang
                print(f"Language changed to: {LANGUAGES[current_language]['name']}")
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Language changed to {LANGUAGES[current_language]['name']}".encode("utf-8"))
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html_with_caption = HTML_CONTENT.replace("{CAPTION}", CAPTION)
            self.wfile.write(html_with_caption.encode("utf-8"))
        else:
            self.send_error(404, "Page not found")

def run_http_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, ImageRequestHandler)
    print("HTTP server is running on http://localhost:8000")
    httpd.serve_forever()

# Start the server in a separate thread
http_thread = threading.Thread(target=run_http_server, daemon=True)
http_thread.start()

# Main loop
while True:
    capture()
    define()
    print(f"Time: {time_counter}, Caption: {CAPTION} (Language: {LANGUAGES[current_language]['name']})")
    time_counter += 1
    time.sleep(3)
