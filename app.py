import string
from flask import Flask, request
from googletrans import Translator

app = Flask(__name__)
translator = Translator()

# English-style phonetics
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

def get_phonetic(word, style="english"):
    word = word.lower()
    phonetic = ""
    mapping = EN_PHONETIC_MAP if style == "english" else DE_PHONETIC_MAP
    for char in word:
        if char in mapping:
            phonetic += mapping[char] + "-"
        else:
            phonetic += char
    return phonetic.strip("-")

@app.route("/", methods=["GET", "POST"])
def home():
    html = """
    <h2>English → German Learning App</h2>

    <form method="post">
        <textarea name="text" rows="4" cols="50"
        placeholder="Write English here">{}</textarea><br><br>

        <label for="phonetic">Phonetics style:</label>
        <select name="phonetic" id="phonetic">
            <option value="english" {}>English</option>
            <option value="german" {}>German</option>
        </select><br><br>

        <!-- Hidden input to store last German translation -->
        <input type="hidden" name="last_german" value="{}">

        <button type="submit">Translate / Update Phonetics</button>
    </form>
    """

    english_input = ""
    last_german = ""
    selected_style = "english"
    if request.method == "POST":
        english_input = request.form.get("text", "")
        last_german = request.form.get("last_german", "")
        selected_style = request.form.get("phonetic", "english")

        # If new English text is entered, translate; else reuse last German
        if english_input.strip() != "" or last_german.strip() == "":
            result = translator.translate(english_input, src="en", dest="de")
            german = result.text
        else:
            german = last_german

        # Process words
        words = german.lower().translate(
            str.maketrans("", "", string.punctuation)
        ).split()

        explanations = {}
        phonetics = {}

        for word in words:
            translated_word = translator.translate(word, src="de", dest="en").text
            explanations[word] = translated_word
            phonetics[word] = get_phonetic(word, style=selected_style)

        # Render output
        html += f"<h3>German:</h3><p><b>{german}</b></p>"
        html += "<h3>Word meanings + Phonetics:</h3><ul>"
        for word in words:
            html += f"<li><b>{word}</b> → {explanations[word]} | Pronunciation: {phonetics[word]}</li>"
        html += "</ul>"

        # Fill hidden input for next submission
        last_german = german

    # Fill dropdown selection and hidden input
    english_selected = "selected" if selected_style == "english" else ""
    german_selected = "selected" if selected_style == "german" else ""
    return html.format(
        english_input, english_selected, german_selected, last_german
    )

app.run(debug=True)
