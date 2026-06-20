"""
spam_classifier.py
==================
Project:    Spam Email Classifier
Difficulty: Beginner
Skills:     Python, pandas, scikit-learn
Time:       Medium (3-5 days)

What you will build:
    A Python script that learns to distinguish between legitimate emails and
    spam using text preprocessing and TF-IDF vectorization. You will train a
    Naive Bayes classifier on a dataset of labeled emails, evaluate its
    performance using accuracy/precision/recall metrics, and use it to
    classify new emails.

    The project teaches core machine learning workflow: load data → clean →
    vectorize → train → evaluate → predict. No external APIs needed — just
    pandas for data handling and scikit-learn for ML.

How to run:
    pip install pandas scikit-learn
    python spam_classifier.py
    Follow the interactive prompts to classify emails or train a new model.

Learning goals:
    - Understanding TF-IDF vectorization — how text becomes numbers
    - Implementing a complete ML pipeline from data to prediction
    - Reading and cleaning real (messy) text data
    - Training a Naive Bayes classifier and interpreting results
    - Evaluating classifier performance: accuracy, precision, recall, F1-score
    - Using sklearn's train_test_split for proper model validation
    - Building confidence in debugging ML models step-by-step

Key concept — Naive Bayes in plain English:
    Naive Bayes is a probabilistic classifier based on Bayes' theorem:
    P(Spam | words) = P(words | Spam) × P(Spam) / P(words)

    It answers: "Given these words, what is the probability this email is spam?"

    "Naive" means the algorithm assumes each word is independent of others
    (which is technically false, but works well in practice). This simplification
    makes the math fast and the model interpretable — you can see which words
    the classifier thinks are "spam-y" and which are "legitimate-y".

Data flow:
    Raw email dataset (CSV or similar)
        |
        v
    load_dataset()           <- read CSV, split into train/test    [TODO]
        |
        v
    preprocess_text()        <- lowercase, remove punctuation      [TODO]
        |
        v
    vectorize_text()         <- TF-IDF vectors (already done)
        |
        v
    train_model()            <- fit Naive Bayes classifier         [TODO]
        |
        v
    evaluate_model()         <- accuracy, precision, recall, F1    [TODO]
        |
        v
    predict_email()          <- classify new emails                [TODO]
        |
        v
    Print results to user

Roadmap:
    Step 1:  Install dependencies and understand the starter file structure
    Step 2:  Read and understand vectorize_text() — TF-IDF is already done
    Step 3:  Complete load_dataset() to read a CSV and split into train/test
    Step 4:  Complete preprocess_text() to clean individual email texts
    Step 5:  Complete train_model() to fit a Naive Bayes classifier
    Step 6:  Complete evaluate_model() to compute and display metrics
    Step 7:  Complete predict_email() for classifying new emails
    Step 8:  Wire everything together in main() and test end-to-end
"""

import csv
import io
import re
import string
from collections import defaultdict

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Default random state ensures reproducible train/test splits across runs.
RANDOM_STATE = 42

# Minimum word frequency to include in the vocabulary (1 = keep all words).
MIN_WORD_LENGTH = 2

# Maximum vocabulary size for TF-IDF (limits memory usage on large datasets).
MAX_FEATURES = 5000

# Email classification labels.
SPAM_LABEL = 1      # 1 = spam
HAM_LABEL = 0       # 0 = legitimate (ham)

# Common English stopwords — words that appear in both spam and ham.
# Removing them focuses the classifier on more meaningful words.
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "he", "in", "is", "it", "its", "of", "on", "or", "she", "that", "the",
    "to", "was", "will", "with", "you", "your", "this", "these", "those",
    "have", "had", "do", "does", "did", "should", "would", "could", "will",
    "can", "may", "might", "must", "shall", "should", "am", "been", "being",
}


# ---------------------------------------------------------------------------
# Data loading and preprocessing
# ---------------------------------------------------------------------------

def load_dataset(filepath, test_size=0.2):
    """
    Load email dataset from a CSV file and split into training and test sets.

    Args:
        filepath (str):   Path to CSV file. Expected columns: "text" and "label"
                          where label is 0 (ham) or 1 (spam).
        test_size (float): Fraction of data to use for testing (default 0.2 = 20%).

    Returns:
        tuple: (X_train, X_test, y_train, y_test)
            X_train (list[str]): Training email texts
            X_test (list[str]):  Test email texts
            y_train (list[int]): Training labels (0 or 1)
            y_test (list[int]):  Test labels (0 or 1)

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError:       If required columns ("text", "label") are missing.

    Example CSV format:
        text,label
        "Great offer for you!",1
        "Meeting at 3pm tomorrow",0
        "Click here for free money!",1

    TODO:
        1. Read the CSV file using pd.read_csv(filepath).
        2. Check that the DataFrame has columns "text" and "label".
           Raise ValueError with a helpful message if not.
        3. Verify that all labels are 0 or 1. Raise ValueError if not.
        4. Extract X = list(df["text"]) and y = list(df["label"]).
        5. Use train_test_split() with test_size, random_state=RANDOM_STATE
           to split the data.
        6. Return (X_train, X_test, y_train, y_test).

    Note: train_test_split() is already imported from sklearn.model_selection.
    """
    # --- Write your dataset loading code here ---

    return [], [], [], []


def preprocess_text(text):
    """
    Clean a single email text by normalising case, punctuation, and tokens.

    Args:
        text (str): Raw email text (may contain URLs, special chars, etc.).

    Returns:
        str: Cleaned text suitable for vectorization.

    Preprocessing steps (in order):
        1. Lowercase — "Python" and "PYTHON" should be treated the same.
        2. Remove URLs — they add noise (e.g. "http://spam-site.com").
        3. Remove punctuation — "hello!" and "hello" are the same word.
        4. Remove extra whitespace — collapse multiple spaces/newlines.
        5. Remove stopwords — common words like "the", "a", "is" carry no signal.
        6. Strip leading/trailing whitespace.

    TODO:
        Implement each step using string methods and regex:
        1. text = text.lower()
        2. text = re.sub(r"https?://\S+|www\.\S+", " ", text)
           (removes URLs starting with http://, https://, or www.)
        3. text = text.translate(str.maketrans("", "", string.punctuation))
           (removes all punctuation in one pass).
        4. text = re.sub(r"\s+", " ", text)
           (collapses whitespace).
        5. Remove stopwords:
           a. Split text into words: words = text.split()
           b. Keep only words NOT in STOPWORDS: words = [w for w in words
                                                         if w not in STOPWORDS]
           c. Rejoin: text = " ".join(words)
        6. Return text.strip()

    Example:
        preprocess_text("Check out http://spam-site.com NOW!!!")
        # -> "check spam site"
    """
    # --- Write your preprocessing code here ---

    return ""


def vectorize_text(texts, is_training=True, vectorizer=None):
    """
    Convert email texts to TF-IDF numerical vectors.

    Args:
        texts (list[str]):              List of email texts.
        is_training (bool):             If True, fit a new vectorizer on texts.
                                        If False, use the provided vectorizer.
        vectorizer (TfidfVectorizer):   Pre-trained vectorizer (required if
                                        is_training=False).

    Returns:
        tuple: (vectors, vectorizer)
            vectors (sparse matrix):    TF-IDF vectors (one row per email).
            vectorizer (TfidfVectorizer): Fitted vectorizer object (useful for
                                          transforming new emails at prediction time).

    How TF-IDF vectorization works:
        Each email becomes a vector where each dimension represents a word in
        the vocabulary. The value at each dimension is the TF-IDF weight —
        how "important" that word is to this email relative to the dataset.

    This function is already complete — read it carefully before tackling
    the TODOs above.
    """
    if is_training:
        # Create a new vectorizer during training.
        vectorizer = TfidfVectorizer(
            max_features=MAX_FEATURES,
            stop_words='english',
            lowercase=True,
            min_df=2,  # Ignore words that appear in fewer than 2 documents.
        )
        vectors = vectorizer.fit_transform(texts)
    else:
        # Use an existing vectorizer during inference (prediction).
        if vectorizer is None:
            raise ValueError(
                "vectorizer must be provided when is_training=False"
            )
        vectors = vectorizer.transform(texts)

    return vectors, vectorizer


# ---------------------------------------------------------------------------
# Model training and evaluation
# ---------------------------------------------------------------------------

def train_model(X_train, y_train):
    """
    Train a Naive Bayes classifier on training data.

    Args:
        X_train (sparse matrix): TF-IDF vectors from vectorize_text().
        y_train (list[int]):     Training labels (0 or 1).

    Returns:
        MultinomialNB: A fitted classifier ready to make predictions.

    How Naive Bayes training works:
        The classifier learns two things:
        1. P(word | spam) and P(word | ham) — the probability of each word
           given the class.
        2. P(spam) and P(ham) — the prior probability of each class in the
           training data.

        Training is very fast — it scans the training vectors once and stores
        statistics. No iterative optimization like neural networks.

    TODO:
        1. Create a MultinomialNB() instance (already imported).
        2. Call .fit(X_train, y_train) on it.
        3. Return the fitted model.

    Example:
        model = train_model(X_train_vectors, y_train)
        # model is now ready to call .predict() on new vectors
    """
    # --- Write your training code here ---

    return None


def evaluate_model(model, X_test, y_test):
    """
    Assess classifier performance on held-out test data.

    Args:
        model (MultinomialNB):  Fitted classifier from train_model().
        X_test (sparse matrix): TF-IDF vectors of test emails.
        y_test (list[int]):     True labels for test emails.

    Returns:
        dict: A dictionary with the following keys:
            "accuracy":  Fraction of correct predictions.
            "precision": Of emails predicted as spam, how many were actually spam?
            "recall":    Of actual spam emails, how many did we catch?
            "f1":        Harmonic mean of precision and recall.

    Why these metrics matter:
        - Accuracy: (TP + TN) / total. Simple but can be misleading if classes
          are imbalanced (e.g., 95% ham, 5% spam).
        - Precision: TP / (TP + FP). High precision = few false positives.
          In email, a false positive (marking ham as spam) is very bad.
        - Recall: TP / (TP + FN). High recall = few false negatives.
          In email, a false negative (missing spam) is less bad than FP.
        - F1: Harmonic mean. A balanced metric when precision and recall matter.

    TODO:
        1. Call model.predict(X_test) to get predicted labels.
        2. Compute metrics using the sklearn functions already imported:
           - accuracy_score(y_test, y_pred)
           - precision_score(y_test, y_pred, zero_division=0)
           - recall_score(y_test, y_pred, zero_division=0)
           - f1_score(y_test, y_pred, zero_division=0)
        3. Return a dict with keys "accuracy", "precision", "recall", "f1"
           and their respective values (rounded to 4 decimals).

    Example:
        metrics = evaluate_model(model, X_test, y_test)
        print(f"Accuracy: {metrics['accuracy']:.4f}")
        # -> "Accuracy: 0.9534"
    """
    # --- Write your evaluation code here ---

    return {}


def predict_email(model, vectorizer, email_text):
    """
    Classify a single email as spam (1) or ham (0).

    Args:
        model (MultinomialNB):   Fitted classifier.
        vectorizer (TfidfVectorizer): Fitted vectorizer (must be the same one
                                      used during training).
        email_text (str):        Raw email text to classify.

    Returns:
        dict: Prediction result with keys:
            "label":      0 (ham) or 1 (spam).
            "probability": Confidence as a float between 0.0 and 1.0.
            "prediction": Human-readable string ("Spam" or "Ham").

    How prediction works:
        1. Preprocess the email using the same steps as training.
        2. Vectorize it using the fitted vectorizer.
        3. Call model.predict() to get the label (0 or 1).
        4. Call model.predict_proba() to get confidence.
        5. Return results.

    TODO:
        1. Preprocess the email_text using preprocess_text().
        2. Vectorize the cleaned text using vectorize_text(..., is_training=False,
           vectorizer=vectorizer).
        3. Get the prediction: label = model.predict(vectors)[0]
        4. Get the confidence:
           proba = model.predict_proba(vectors)[0]
           probability = max(proba)
           (max(proba) is the higher of the two class probabilities)
        5. Map label to a readable string:
           prediction = "Spam" if label == SPAM_LABEL else "Ham"
        6. Return dict with "label", "probability", and "prediction".

    Example:
        result = predict_email(model, vec, "You won a free prize!!!")
        print(result)
        # -> {"label": 1, "probability": 0.87, "prediction": "Spam"}
    """
    # --- Write your prediction code here ---

    return {}


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def main():
    """
    Orchestrate the full ML pipeline: load data, train, evaluate, predict.

    This function is already complete — read it carefully.  It shows how to
    wire the individual functions together into a working end-to-end system.

    You do not need to modify this function — just complete the TODOs in
    the functions above, then run:
        python spam_classifier.py
    """
    print("=" * 70)
    print("SPAM EMAIL CLASSIFIER")
    print("=" * 70)
    print()

    # --- Step 1: Load dataset ---
    print("[Step 1] Loading dataset...")
    try:
        X_train, X_test, y_train, y_test = load_dataset("spam_emails.csv")
        print(f"  ✓ Loaded {len(X_train)} training emails, {len(X_test)} test emails")
    except FileNotFoundError:
        print("  ✗ Error: spam_emails.csv not found.")
        print("    Create a CSV file with columns: 'text' and 'label' (0=ham, 1=spam)")
        return
    except Exception as e:
        print(f"  ✗ Error loading dataset: {e}")
        return

    # --- Step 2: Preprocess training data ---
    print("\n[Step 2] Preprocessing training data...")
    try:
        X_train_clean = [preprocess_text(text) for text in X_train]
        X_test_clean = [preprocess_text(text) for text in X_test]
        print(f"  ✓ Preprocessing complete")
        print(f"    Sample cleaned text: '{X_train_clean[0][:60]}...'")
    except Exception as e:
        print(f"  ✗ Error preprocessing: {e}")
        return

    # --- Step 3: Vectorize text ---
    print("\n[Step 3] Vectorizing text with TF-IDF...")
    try:
        X_train_vectors, vectorizer = vectorize_text(X_train_clean, is_training=True)
        X_test_vectors, _ = vectorize_text(X_test_clean, is_training=False, vectorizer=vectorizer)
        print(f"  ✓ Vectorization complete")
        print(f"    Vocabulary size: {len(vectorizer.get_feature_names_out())}")
        print(f"    Train vectors shape: {X_train_vectors.shape}")
        print(f"    Test vectors shape: {X_test_vectors.shape}")
    except Exception as e:
        print(f"  ✗ Error vectorizing: {e}")
        return

    # --- Step 4: Train model ---
    print("\n[Step 4] Training Naive Bayes classifier...")
    try:
        model = train_model(X_train_vectors, y_train)
        if model is None:
            print("  ✗ train_model() returned None. Have you completed the TODO?")
            return
        print(f"  ✓ Training complete")
    except Exception as e:
        print(f"  ✗ Error training: {e}")
        return

    # --- Step 5: Evaluate model ---
    print("\n[Step 5] Evaluating on test set...")
    try:
        metrics = evaluate_model(model, X_test_vectors, y_test)
        if not metrics:
            print("  ✗ evaluate_model() returned empty dict. Have you completed the TODO?")
            return
        print(f"  ✓ Evaluation complete")
        print(f"    Accuracy:  {metrics['accuracy']:.4f}")
        print(f"    Precision: {metrics['precision']:.4f}")
        print(f"    Recall:    {metrics['recall']:.4f}")
        print(f"    F1-score:  {metrics['f1']:.4f}")
    except Exception as e:
        print(f"  ✗ Error evaluating: {e}")
        return

    # --- Step 6: Test on sample emails ---
    print("\n[Step 6] Testing predictions on sample emails...")
    sample_emails = [
        "CONGRATULATIONS! You have won a free iPhone! Click here now!!!",
        "Hi, can we schedule a meeting for next Tuesday at 2pm?",
        "Limited time offer! Get 50% off all products! BUY NOW!",
        "The project deadline has been moved to Friday. Let me know if you have questions.",
    ]
    try:
        for email in sample_emails:
            result = predict_email(model, vectorizer, email)
            if not result:
                print("  ✗ predict_email() returned empty dict. Have you completed the TODO?")
                return
            label = result['prediction']
            prob = result['probability']
            print(f"  [{label:4s}] (confidence: {prob:.2%}) {email[:50]}...")
    except Exception as e:
        print(f"  ✗ Error predicting: {e}")
        return

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE ✓")
    print("=" * 70)


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Sample dataset for testing (CSV format)
# ---------------------------------------------------------------------------
#
# Save this as "spam_emails.csv" and run:  python spam_classifier.py
#
# text,label
# "URGENT: Claim your FREE money NOW!!!",1
# "Can you send me the quarterly report?",0
# "You have won a lottery! Click here to claim.",1
# "Meeting rescheduled to Thursday 3pm.",0
# "BUY NOW and save 99%! LIMITED TIME!",1
# "Hi, just checking in on the project status.",0
# "Your account has been COMPROMISED. Verify identity now!",1
# "The code review comments are in the pull request.",0
# "Get rich quick with this one weird trick!",1
# "Reminder: standups start at 10am tomorrow.",0
# "CLICK HERE for the hottest deals!!!",1
# "Your order #12345 has been shipped.",0
# ... (add more examples as needed)
