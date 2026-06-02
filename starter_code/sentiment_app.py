"""
sentiment_app.py
================
Project:    Sentiment Analysis Web App
Difficulty: Intermediate
Skills:     Python, Flask, scikit-learn, HTML, CSS
Time:       High (a week or more)

What you will build:
    Build a web application that predicts whether the text
    entered by a user has positive, negative, or neutral
    sentiment. The project teaches NLP preprocessing, tokenization
    and machine learning basics with Flask integration.

How to run:
    pip install flask scikit-learn pandas
    python sentiment_app.py

Open the local Flask server in your browser and enter sample text to test sentiment predictions.

A sample dataset such as Sentiment140 or IMDb reviews can be used for training and testing the model.

Learning goals:
    - Preprocessing text data for NLP tasks
    - Converting text into numerical features
    - Building a simple sentiment prediction model
    - Building a Flask web app and displaying sentiment predictions

Roadmap:
    Step 1:  Load and inspect the sentiment dataset
    Step 2:  Clean and preprocess text input data
    Step 3:  Convert text into numerical feature vectors
    Step 4:  Build a simple sentiment prediction model
    Step 5:  Evaluate model accuracy on test data
    Step 6:  Create Flask routes and an HTML template for structure and CSS for design
    Step 7:  Connect the trained model to the web app
    Step 8:  Test predictions with varied user entered text
"""

from flask import Flask, request
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression


# -------------------------------------------------------------------
# Flask App Setup
# -------------------------------------------------------------------

app = Flask(__name__)


# -------------------------------------------------------------------
# Sample Dataset
# -------------------------------------------------------------------

texts = [
    "I love this movie",
    "This is amazing",
    "Fantastic experience",
    "I hate this product",
    "This is terrible",
    "Very disappointing"
]

labels = [
    "Positive",
    "Positive",
    "Positive",
    "Negative",
    "Negative",
    "Negative"
]

# TODO:
# Add more training examples for better predictions
# Include neutral sentiment examples
# Load dataset from a CSV file instead of hardcoding values


# -------------------------------------------------------------------
# Model Training
# -------------------------------------------------------------------

vectorizer = CountVectorizer()

X = vectorizer.fit_transform(texts)

model = LogisticRegression()

model.fit(X, labels)


# -------------------------------------------------------------------
# Core Functions
# -------------------------------------------------------------------

def predict_sentiment(text):
    """
    Predict sentiment for user-entered text.
    """
    # TODO:
    # Add text preprocessing such as:
    # - lowercasing
    # - punctuation removal
    # - stopword filtering

    transformed_text = vectorizer.transform([text])

    prediction = model.predict(transformed_text)

    return prediction[0]


# -------------------------------------------------------------------
# Flask Routes
# -------------------------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def home():
    """
    Main route for sentiment prediction.
    """

    prediction = ""

    if request.method == "POST":
        user_text = request.form.get("text")

        if user_text:
            prediction = predict_sentiment(user_text)
            
    # TODO:
    # Move HTML into separate template files
    # Add CSS styling

    return f"""
    <html>
        <head>
            <title>Sentiment Analysis App</title>
        </head>

        <body style="font-family: Arial; padding: 40px;">
            <h1>Sentiment Analysis Web App</h1>

            <form method="POST">
                <textarea
                    name="text"
                    rows="5"
                    cols="50"
                    placeholder="Enter text here..."
                ></textarea>

                <br><br>

                <button type="submit">
                    Predict Sentiment
                </button>
            </form>

            <h2>{prediction}</h2>
        </body>
    </html>
    """


# -------------------------------------------------------------------
# Main Program
# -------------------------------------------------------------------

if __name__ == "__main__":
    print("Starting Flask server")
    app.run(debug=True)