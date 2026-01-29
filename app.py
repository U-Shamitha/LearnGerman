import string
import os
from flask import Flask, request
from googletrans import Translator
from gtts import gTTS

# -------------------------------
# Flask app setup
# -------------------------------
app = Flask(__name__)
translator = Translator()

# Ensure folder for audio exists
AUDIO_FOLDER = "static/audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# -------------------------------
# Phonetic mappings
# -------------------------------

# English-style phonetics (for learners)
EN_PHONETIC_MAP = {
    'a': 'ah', 'ä': 'eh', 'b': 'b', 'c': 'ts', 'd': 'd', 'e': 'eh',
    'f': 'f', 'g': 'g', 'h': 'h', 'i': 'ee', 'j': 'y', 'k': 'k', 'l': 'l',
    'm': 'm', 'n': 'n', 'o': 'oh', 'ö': 'ur', 'p': 'p', 'q': 'kw', 'r': 'r',
    's': 'z', 'ß': 'ss', 't': 't', 'u': 'oo', 'ü': 'ue', 'v': 'f', 'w': 'v',
    'x': 'ks', 'y': 'ee', 'z': 'ts'
}

# German-style phonetics (IPA-like simplified)
DE_PHONETIC_MAP = {
    'a': 'a', 'ä': 'ɛ', 'b': 'b', 'c': 'ts', 'd': 'd', 'e': 'e',
    'f': 'f', 'g': 'g', 'h': 'h', 'i': 'i', 'j': 'j', 'k': 'k', 'l': 'l',
    'm': 'm', 'n': 'n', 'o': 'o', 'ö': 'ø', 'p': 'p', 'q': 'kv', 'r': 'r',
    's': 's', 'ß': 's', 't': 't', 'u': 'u', 'ü': 'y', 'v': 'f', 'w': 'v',
    'x': 'ks', 'y': 'y', 'z': 'ts'
}

# -------------------------------
# Function to generate phonetic spelling
# -------------------------------
def get_phonetic(word, style="english"):
    """
    Convert a German word into a phonetic spelling
    style: "english" or "german"
    """
    word = word.lower()
    phonetic = ""
    mapping = EN_PHONETIC_MAP if style == "english" else DE_PHONETIC_MAP
    for char in word:
        if char in mapping:
            phonetic += mapping[char] + "-"
        else:
            phonetic += char
    return phonetic.strip("-")

# -------------------------------
# Main route
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    # Base HTML form with placeholders for dynamic values
    html = """
    <h2>English → German Learning App</h2>

    <form method="post">
        <textarea name="text" rows="4" cols="50"
        placeholder="Write English here">{}</textarea><br><br>

        <!-- Phonetic style dropdown -->
        <label for="phonetic">Phonetics style:</label>
        <select name="phonetic" id="phonetic">
            <option value="english" {}>English</option>
            <option value="german" {}>German</option>
        </select><br><br>

        <!-- Audio speed dropdown -->
        <label for="speed">Audio speed:</label>
        <select name="speed" id="speed">
            <option value="slow" {}>Slow</option>
            <option value="normal" {}>Normal</option>
        </select><br><br>

        <!-- Hidden input stores last German sentence for reswitching phonetics -->
        <input type="hidden" name="last_german" value="{}">

        <button type="submit">Translate / Update Phonetics</button>
    </form>
    """

    # Default values
    english_input = ""
    last_german = ""
    selected_style = "english"
    speed = "normal"

    if request.method == "POST":
        # -------------------------------
        # Get user inputs
        # -------------------------------
        english_input = request.form.get("text", "")
        last_german = request.form.get("last_german", "")
        selected_style = request.form.get("phonetic", "english")
        speed = request.form.get("speed", "normal")

        # -------------------------------
        # Determine if translation is needed
        # If English input changed or no last German sentence, translate
        # Otherwise reuse last German sentence
        # -------------------------------
        if english_input.strip() != "" or last_german.strip() == "":
            result = translator.translate(english_input, src="en", dest="de")
            german = result.text
        else:
            german = last_german

        # -------------------------------
        # Process each word
        # -------------------------------
        # Remove punctuation and split words
        words = german.lower().translate(
            str.maketrans("", "", string.punctuation)
        ).split()

        explanations = {}  # English meanings
        phonetics = {}     # Phonetic spellings

        for word in words:
            # Translate word back to English for meaning
            translated_word = translator.translate(word, src="de", dest="en").text
            explanations[word] = translated_word

            # Generate phonetic spelling
            phonetics[word] = get_phonetic(word, style=selected_style)

            # Generate audio file for each word
            audio_file_path = f"{AUDIO_FOLDER}/{word}.mp3"
            tts_speed = True if speed == "slow" else False
            tts = gTTS(text=word, lang="de", slow=tts_speed)
            tts.save(audio_file_path)

        # -------------------------------
        # Render output in HTML
        # -------------------------------
        html += f"<h3>German:</h3><p><b>{german}</b></p>"
        html += "<h3>Word meanings + Phonetics + Audio:</h3><ul>"

        for word in words:
            html += f"<li><b>{word}</b> → {explanations[word]} | Pronunciation: {phonetics[word]} " \
                    f"| <audio controls><source src='{AUDIO_FOLDER}/{word}.mp3' type='audio/mpeg'></audio></li>"
        html += "</ul>"

        # Update hidden input for next submission
        last_german = german

    # -------------------------------
    # Set dropdown selections
    # -------------------------------
    english_selected = "selected" if selected_style == "english" else ""
    german_selected = "selected" if selected_style == "german" else ""
    slow_selected = "selected" if speed == "slow" else ""
    normal_selected = "selected" if speed == "normal" else ""

    # Render final HTML
    return html.format(
        english_input, english_selected, german_selected,
        slow_selected, normal_selected, last_german
    )

# -------------------------------
# Run the app
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
