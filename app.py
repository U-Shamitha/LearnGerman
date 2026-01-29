import string
from flask import Flask, request
from googletrans import Translator

app = Flask(__name__)
translator = Translator()

# VERY small starter dictionary
dictionary = {
    "ich": "I",
    "bin": "am",
    "lerne": "learn",
    "deutsch": "German",
    "sprache": "language",
    "die": "the"
}

@app.route("/", methods=["GET", "POST"])
def home():
    html = """
    <h2>English → German Learning App</h2>

    <form method="post">
        <textarea name="text" rows="4" cols="50"
        placeholder="Write English here"></textarea><br><br>
        <button type="submit">Translate</button>
    </form>
    """

    if request.method == "POST":
        english = request.form["text"]

        result = translator.translate(english, src="en", dest="de")
        german = result.text

        words = german.lower().translate(
            str.maketrans("", "", string.punctuation)
        ).split()

        explanations = {}

        for word in words:
            translated_word = translator.translate(word, src="de", dest="en").text
            explanations[word] = translated_word

        html += f"<h3>German:</h3><p><b>{german}</b></p>"
        html += "<h3>Word meanings:</h3><ul>"
        
        for word, meaning in explanations.items():
            html += f"<li><b>{word}</b> → {meaning}</li>"



        html += "</ul>"

    return html

app.run(debug=True)
