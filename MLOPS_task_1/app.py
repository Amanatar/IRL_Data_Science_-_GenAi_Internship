from flask import Flask, request, render_template
import joblib
import re

app = Flask(__name__)

# Load trained artifacts
model = joblib.load("deployment_files/sentiment_model.pkl")
vectorizer = joblib.load("deployment_files/tfidf_vectorizer.pkl")

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

@app.route("/", methods=["GET", "POST"])
def home():
    sentiment = None
    confidence = None
    review_text = None

    if request.method == "POST":
        review_text = request.form.get("review")

        if review_text:
            cleaned = clean_text(review_text)
            X = vectorizer.transform([cleaned])

            prediction = model.predict(X)[0]
            probabilities = model.predict_proba(X)[0]

            confidence = round(max(probabilities) * 100, 2)
            sentiment = "Positive" if prediction == 1 else "Negative"

    return render_template(
        "index.html",
        sentiment=sentiment,
        confidence=confidence,
        review_text=review_text
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
