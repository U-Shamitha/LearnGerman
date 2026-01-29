import re
import string, os, uuid
from flask import Flask, render_template, request
from googletrans import Translator
from gtts import gTTS

# -------------------------------
# Flask app setup
# -------------------------------
app = Flask(__name__)
translator = Translator()

# Ensure audio folder exists
AUDIO_FOLDER = "static/audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# -------------------------------
# Phonetic mappings
# -------------------------------
EN_PHONETIC_MAP = {
    'a': 'ah', 'ä': 'eh', 'b': 'b', 'c': 'ts', 'd': 'd', 'e': 'eh',
    'f': 'f', 'g': 'g', 'h': 'h', 'i': 'ee', 'j': 'y', 'k': 'k', 'l': 'l',
    'm': 'm', 'n': 'n', 'o': 'oh', 'ö': 'ur', 'p': 'p', 'q': 'kw', 'r': 'r',
    's': 'z', 'ß': 'ss', 't': 't', 'u': 'oo', 'ü': 'ue', 'v': 'f', 'w': 'v',
    'x': 'ks', 'y': 'ee', 'z': 'ts'
}

DE_PHONETIC_MAP = {
    'a': 'a', 'ä': 'ɛ', 'b': 'b', 'c': 'ts', 'd': 'd', 'e': 'e',
    'f': 'f', 'g': 'g', 'h': 'h', 'i': 'i', 'j': 'j', 'k': 'k', 'l': 'l',
    'm': 'm', 'n': 'n', 'o': 'o', 'ö': 'ø', 'p': 'p', 'q': 'kv', 'r': 'r',
    's': 's', 'ß': 's', 't': 't', 'u': 'u', 'ü': 'y', 'v': 'f', 'w': 'v',
    'x': 'ks', 'y': 'y', 'z': 'ts'
}

# -------------------------------
# Generate phonetic spelling
# -------------------------------
def get_phonetic(word, style="english"):
    word = word.lower()
    phonetic = ""
    mapping = EN_PHONETIC_MAP if style == "english" else DE_PHONETIC_MAP
    for char in word:
        phonetic += mapping.get(char, char) + " "  # Use spaces for readability
    return phonetic.strip()

# -------------------------------
# Main route
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    english_input = ""
    last_german = ""
    selected_style = "english"
    speed = "normal"
    german_sentence = ""
    word_blocks = []

    if request.method == "POST":
        english_input = request.form.get("text", "")
        last_german = request.form.get("last_german", "")
        selected_style = request.form.get("phonetic", "english")
        speed = request.form.get("speed", "normal")

        # Translate if needed
        if english_input.strip() != "" or last_german.strip() == "":
            result = translator.translate(english_input, src="en", dest="de")
            german_sentence = result.text
        else:
            german_sentence = last_german

        # Process words
        # Replace punctuation with spaces, then split
        words = re.sub(r'[^\wäöüßÄÖÜ]', ' ', german_sentence.lower()).split()   

        for word in words:
            # English meaning
            english_meaning = translator.translate(word, src="de", dest="en").text

            # Generate unique audio filename
            audio_file = f"{AUDIO_FOLDER}/{word}_{uuid.uuid4().hex}.mp3"
            tts_speed = True if speed == "slow" else False
            tts = gTTS(text=word, lang="de", slow=tts_speed)
            tts.save(audio_file)

            # Build word block
            word_blocks.append({
                "word": word,
                "meaning": english_meaning,
                "phonetic": {
                    "de": get_phonetic(word, "german"),
                    "en": get_phonetic(word, "english")  # English-style phonetic for German word
                },
                "audio": audio_file
            })

        last_german = german_sentence

    return render_template("index.html",
                           english_input=english_input,
                           german_sentence=german_sentence,
                           word_blocks=word_blocks,
                           selected_style=selected_style,
                           speed=speed,
                           last_german=last_german)

# -------------------------------
# Run the app
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
