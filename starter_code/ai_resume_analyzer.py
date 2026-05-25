"""
ai_resume_analyzer.py
=====================
Project:    AI Resume Analyzer
Difficulty: Intermediate
Skills:     Python, Flask, NLP concepts, TF-IDF, PDF parsing
Time:       High (a week or more)

What you will build:
    A Flask web app where a user uploads a resume (PDF or plain text) and
    pastes a job description. The app extracts keywords from both, scores
    how well the resume matches the job, lists skills the resume is missing,
    and gives short, actionable feedback — all without calling any external
    AI API.

    You will implement the NLP ideas yourself using only the Python standard
    library plus two small, widely-used packages: PyPDF2 (PDF reading)
    and scikit-learn (TF-IDF vectoriser). This keeps the project honest —
    you will understand exactly what "AI" is doing under the hood.

How to run:
    pip install flask PyPDF2 scikit-learn
    python ai_resume_analyzer.py
    Open http://127.0.0.1:5000 in your browser.

Learning goals:
    - Understanding TF-IDF similarity — what it measures and why it works
    - Parsing real PDF files and cleaning messy extracted text
    - Using a bag-of-words approach to find keyword gaps
    - Building a single-file Flask app with an embedded HTML template
    - Designing a simple scoring algorithm from scratch
    - Practising function decomposition: one function, one job

Key concept — TF-IDF in plain English:
    TF-IDF stands for Term Frequency – Inverse Document Frequency.
    It answers the question: "How important is this word to THIS document
    compared with documents in general?"

    - TF (term frequency): how often the word appears in the document.
    - IDF (inverse document frequency): how rare the word is across all
      documents. Common words like "the" or "and" get a low IDF score
      because they appear everywhere and carry little meaning.

    When you compare a resume and a job description using TF-IDF vectors,
    words that appear in both AND are relatively rare (like "kubernetes" or
    "regression") pull the similarity score up more than filler words do.
    The result is a score between 0 (no overlap) and 1 (identical content).

Data flow:
    User uploads resume + pastes job description
        |
        v
    extract_text_from_pdf()  <- handles PDF bytes -> plain string
        |
        v
    clean_text()             <- lowercase, remove punctuation, strip numbers
        |   (already implemented — study this one first)
        v
    extract_keywords()       <- keep meaningful words, drop stopwords
        |   (already implemented — study this one too)
        v
    calculate_similarity()   <- TF-IDF cosine similarity score  [TODO]
        |
        v
    find_missing_skills()    <- keywords in job but not resume   [TODO]
        |
        v
    generate_feedback()      <- human-readable advice            [TODO]
        |
        v
    Return JSON to the browser

Roadmap:
    Step 1:  Run the server — the upload form renders already
    Step 2:  Read and understand clean_text() — it is already complete
    Step 3:  Read and understand extract_keywords() — it is already complete
    Step 4:  Complete extract_text_from_pdf() using PyPDF2
    Step 5:  Complete calculate_similarity() with TF-IDF and cosine distance
    Step 6:  Complete find_missing_skills() by comparing two keyword sets
    Step 7:  Complete generate_feedback() to produce the written report
    Step 8:  Wire everything together inside the /analyze route
"""

import base64
import io
import re
import string

from flask import Flask, jsonify, render_template_string, request

# PyPDF2 is a beginner-friendly library for reading text from PDF files.
# Install it with:  pip install PyPDF2
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("Warning: PyPDF2 not installed. PDF upload will be disabled.")
    print("Run:  pip install PyPDF2")

# scikit-learn provides the TF-IDF vectoriser and cosine similarity.
# Install it with:  pip install scikit-learn
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_SUPPORT = True
except ImportError:
    SKLEARN_SUPPORT = False
    print("Warning: scikit-learn not installed. Similarity scoring will be disabled.")
    print("Run:  pip install scikit-learn")

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Maximum file size for PDF uploads (in bytes).  5 MB is generous for a CV.
MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB

# The similarity score is a float between 0 and 1.
# These thresholds map the number to a human-readable label.
SCORE_LABELS = {
    0.75: "Excellent match",
    0.50: "Good match",
    0.30: "Fair match",
    0.00: "Weak match",
}

# Words that carry almost no meaning on their own and should be ignored
# when extracting keywords.  This list covers the most common English
# stopwords without needing an external library.
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "up", "about", "into", "through", "during",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "shall", "can", "need", "dare", "ought", "used", "that", "which", "who",
    "this", "these", "those", "it", "its", "we", "our", "you", "your", "he",
    "she", "they", "their", "i", "my", "me", "us", "him", "her", "as", "if",
    "not", "no", "so", "yet", "both", "either", "each", "all", "any", "more",
    "most", "other", "some", "such", "than", "then", "too", "very", "just",
    "also", "well", "get", "got", "work", "worked", "working", "new", "use",
    "using", "good", "high", "able", "including", "within", "across", "per",
    "etc", "e", "g", "ie", "vs", "re", "s", "t",
}

# Minimum number of characters for a word to be considered meaningful.
MIN_WORD_LENGTH = 3


# ---------------------------------------------------------------------------
# HTML template — already complete, no changes needed
# The template is embedded here to keep the project single-file.
# Jinja2 template syntax: {{ variable }}, {% if %}, {% for %} etc.
# ---------------------------------------------------------------------------

PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI Resume Analyzer</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #f0f2ff;
            color: #1a1a2e;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 50px 20px;
        }
        h1 { font-size: 2rem; color: #2335c2; margin-bottom: 6px; }
        p.sub { color: #6b7280; margin-bottom: 32px; }
        .row {
            display: flex;
            gap: 20px;
            width: 100%;
            max-width: 860px;
            margin-bottom: 16px;
        }
        .card {
            flex: 1;
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 12px rgba(35,53,194,0.09);
        }
        .card h3 { margin-bottom: 10px; font-size: 1rem; color: #374151; }
        textarea, input[type=file] {
            width: 100%;
            padding: 10px;
            border: 1.5px solid #e5e7eb;
            border-radius: 8px;
            font-size: 0.9rem;
            font-family: inherit;
            resize: vertical;
        }
        textarea { min-height: 160px; }
        textarea:focus { outline: none; border-color: #4f6ef7; }
        .divider { text-align: center; color: #9ca3af; margin: 8px 0; font-size: 0.85rem; }
        button {
            width: 100%;
            max-width: 860px;
            padding: 13px;
            background: linear-gradient(90deg, #2335c2, #7c3aed);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            margin-bottom: 8px;
        }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        .error { color: #dc2626; font-size: 0.88rem; margin: 6px 0; }

        /* --- Results --- */
        #results { width: 100%; max-width: 860px; display: none; margin-top: 20px; }
        .score-box {
            background: white;
            border-radius: 12px;
            padding: 20px 24px;
            box-shadow: 0 2px 12px rgba(35,53,194,0.09);
            margin-bottom: 16px;
        }
        .score-box .score-num {
            font-size: 2.4rem;
            font-weight: 700;
            color: #2335c2;
        }
        .score-box .score-label { font-size: 1rem; color: #374151; margin-top: 2px; }
        .score-box .score-desc  { font-size: 0.88rem; color: #6b7280; margin-top: 4px; }
        .kw-section {
            display: flex;
            gap: 16px;
            margin-bottom: 16px;
        }
        .kw-card {
            flex: 1;
            background: white;
            border-radius: 12px;
            padding: 18px 20px;
            box-shadow: 0 2px 12px rgba(35,53,194,0.09);
        }
        .kw-card h3 { font-size: 0.95rem; margin-bottom: 10px; color: #374151; }
        .tags { display: flex; flex-wrap: wrap; gap: 6px; }
        .tag {
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.78rem;
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
        }
        .tag.missing { background: #fff7ed; color: #b45309; border-color: #fed7aa; }
        .feedback-card {
            background: white;
            border-radius: 12px;
            padding: 18px 20px;
            box-shadow: 0 2px 12px rgba(35,53,194,0.09);
        }
        .feedback-card h3 { font-size: 0.95rem; margin-bottom: 10px; color: #374151; }
        .feedback-card ul { list-style: none; padding: 0; }
        .feedback-card li {
            padding: 7px 0;
            border-bottom: 1px solid #f3f4f6;
            font-size: 0.88rem;
            color: #374151;
            line-height: 1.5;
        }
        .feedback-card li:last-child { border-bottom: none; }
        .feedback-card li::before { content: "→ "; color: #2335c2; font-weight: 700; }
        #spinner { color: #6b7280; font-size: 0.9rem; margin: 8px 0; display: none; }
    </style>
</head>
<body>

<h1>AI Resume Analyzer</h1>
<p class="sub">Paste your resume and a job description to see how well they match.</p>

<div class="row">
    <!-- Left panel: resume -->
    <div class="card">
        <h3>Your Resume</h3>
        <input type="file" id="resume-file" accept=".pdf" />
        <div class="divider">— or paste text below —</div>
        <textarea id="resume-text" placeholder="Paste resume text here..."></textarea>
    </div>

    <!-- Right panel: job description -->
    <div class="card">
        <h3>Job Description</h3>
        <textarea id="job-text" placeholder="Paste the full job posting here..."
                  style="min-height: 240px;"></textarea>
    </div>
</div>

<p class="error" id="error-msg"></p>
<button id="analyze-btn" onclick="runAnalysis()">Analyze Match</button>
<p id="spinner">Analyzing…</p>

<!-- Results — hidden until /analyze returns data -->
<div id="results">
    <div class="score-box">
        <div class="score-num" id="score-pct">–</div>
        <div class="score-label" id="score-label">–</div>
        <div class="score-desc"  id="score-desc">–</div>
    </div>

    <div class="kw-section">
        <div class="kw-card">
            <h3>Keywords Found in Resume</h3>
            <div class="tags" id="present-keywords"></div>
        </div>
        <div class="kw-card">
            <h3>Missing Skills &amp; Keywords</h3>
            <div class="tags" id="missing-keywords"></div>
        </div>
    </div>

    <div class="feedback-card">
        <h3>Feedback &amp; Suggestions</h3>
        <ul id="feedback-list"></ul>
    </div>
</div>

<script>
    // -----------------------------------------------------------------------
    // Front-end logic — already complete, no changes needed here.
    // Sends resume + job description to Flask, renders the JSON response.
    // -----------------------------------------------------------------------

    function readPdfAsBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload  = () => resolve(reader.result.split(',')[1]);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    async function runAnalysis() {
        const btn       = document.getElementById('analyze-btn');
        const spinner   = document.getElementById('spinner');
        const errEl     = document.getElementById('error-msg');
        const resultsEl = document.getElementById('results');

        errEl.textContent = '';
        resultsEl.style.display = 'none';

        const jobText    = document.getElementById('job-text').value.trim();
        const resumeTxt  = document.getElementById('resume-text').value.trim();
        const resumeFile = document.getElementById('resume-file').files[0];

        if (!jobText)                   { errEl.textContent = 'Please paste a job description.'; return; }
        if (!resumeTxt && !resumeFile)  { errEl.textContent = 'Please upload a PDF or paste resume text.'; return; }

        btn.disabled = true;
        spinner.style.display = 'block';

        try {
            const payload = { job_description: jobText };
            if (resumeFile) {
                payload.resume_pdf_b64  = await readPdfAsBase64(resumeFile);
                payload.resume_filename = resumeFile.name;
            } else {
                payload.resume_text = resumeTxt;
            }

            const resp = await fetch('/analyze', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify(payload),
            });
            const data = await resp.json();

            if (data.error) { errEl.textContent = data.error; return; }
            renderResults(data);

        } catch (err) {
            errEl.textContent = 'Something went wrong. Check the terminal for details.';
            console.error(err);
        } finally {
            btn.disabled = false;
            spinner.style.display = 'none';
        }
    }

    function renderResults(data) {
        const pct = Math.round(data.score * 100);
        document.getElementById('score-pct').textContent   = pct + '%';
        document.getElementById('score-label').textContent = data.label;
        document.getElementById('score-desc').textContent  = data.description;

        // Present keywords
        const presentEl = document.getElementById('present-keywords');
        presentEl.innerHTML = (data.present_keywords || []).length
            ? data.present_keywords.map(k => `<span class="tag">${k}</span>`).join('')
            : 'No strong keywords detected.';

        // Missing keywords
        const missingEl = document.getElementById('missing-keywords');
        missingEl.innerHTML = (data.missing_keywords || []).length
            ? data.missing_keywords.map(k => `<span class="tag missing">${k}</span>`).join('')
            : 'No obvious gaps — great job!';

        // Feedback tips
        const feedbackEl = document.getElementById('feedback-list');
        feedbackEl.innerHTML = (data.feedback || [])
            .map(tip => `<li>${tip}</li>`).join('');

        document.getElementById('results').style.display = 'block';
        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    }
</script>

</body>
</html>
"""


# ---------------------------------------------------------------------------
# Text extraction helpers
# ---------------------------------------------------------------------------

def extract_text_from_pdf(pdf_bytes):
    """
    Extract all text from a PDF given its raw bytes.

    Args:
        pdf_bytes (bytes): The binary content of a PDF file.

    Returns:
        str: The concatenated text from every page, or an empty string
             if extraction fails (encrypted PDF, scanned image, etc.).

    How PyPDF2 works:
        PyPDF2 opens a PDF from a file-like object and lets you iterate
        over pages.  Each page has an extract_text() method that returns a
        string.  We read from memory using io.BytesIO so no file needs to
        be written to disk first.

        Note: PyPDF2 works well on text-based PDFs but cannot read scanned
        documents (those are images, not text).  If extract_text() returns
        an empty string for every page, the file is likely a scan.

    TODO:
        1. Wrap the whole function in try/except and return "" on any error.
        2. Create a file-like object from the bytes:
               reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        3. Loop over reader.pages and call page.extract_text() on each.
        4. Skip pages where extract_text() returns None or "".
        5. Join all non-empty page strings with "\\n" and return the result.

    Example (once complete):
        text = extract_text_from_pdf(open("resume.pdf", "rb").read())
        print(text[:100])
        # -> "Jane Doe\\nSoftware Engineer\\nPython  Flask  PostgreSQL..."
    """
    if not PDF_SUPPORT:
        return ""

    # --- Write your code here ---

    return ""


def clean_text(raw_text):
    """
    Normalise raw text so it is easier to tokenise and compare.

    Args:
        raw_text (str): Text as extracted from a PDF or typed by the user.

    Returns:
        str: Cleaned text: lowercase, no punctuation, collapsed whitespace.

    This function is already complete — read it carefully before moving on.
    Notice how each cleaning step is a single expression; that keeps the
    logic easy to test one step at a time.
    """
    # Step 1: Lowercase everything so "Python" and "python" are treated the same.
    text = raw_text.lower()

    # Step 2: Remove URLs — they add noise without useful keywords.
    # re.sub() replaces every match of the pattern with a space.
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # Step 3: Remove all punctuation characters (.,!?:;'"()[]{} etc.).
    # str.maketrans builds a translation table that maps every punctuation
    # character to None, then str.translate applies it.
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Step 4: Remove standalone digits (phone numbers, years, zip codes).
    # \b is a word-boundary anchor — it only matches whole tokens like "2024"
    # and leaves mixed tokens like "python3" or "iso9001" untouched.
    text = re.sub(r"\b\d+\b", " ", text)

    # Step 5: Collapse multiple spaces/newlines/tabs into a single space
    # and strip any leading or trailing whitespace.
    text = re.sub(r"\s+", " ", text).strip()

    return text


# Quick sanity check — remove this print() once you understand the output:
# print(clean_text("  Experienced in Python 3.11 & REST APIs! (2020-2024) "))
# Expected: "experienced in python rest apis"


def extract_keywords(text, top_n=30):
    """
    Return the most meaningful words from a piece of text.

    Args:
        text  (str): Cleaned text (run clean_text() first).
        top_n (int): How many top keywords to return (default 30).

    Returns:
        list[str]: Unique keywords sorted by frequency (most frequent first),
                   limited to top_n items.

    This function is already complete — study it before tackling the TODOs
    below.  The bag-of-words approach here is intentionally simple; the
    TF-IDF step in calculate_similarity() handles more sophisticated weighting.
    """
    # Step 1: Split the cleaned text into individual word tokens.
    words = text.split()

    # Step 2 & 3: Keep only words that are long enough AND not in STOPWORDS.
    # A set lookup (word in STOPWORDS) is O(1), so this loop is fast even
    # on long documents.
    filtered = [
        word for word in words
        if len(word) >= MIN_WORD_LENGTH and word not in STOPWORDS
    ]

    # Step 4: Count how often each word appears.
    # We use a plain dict instead of collections.Counter to keep the
    # standard-library imports minimal and the logic visible.
    counts = {}
    for word in filtered:
        counts[word] = counts.get(word, 0) + 1

    # Step 5: Sort by count descending, then extract just the words.
    # sorted() with key=lambda returns a new list without modifying counts.
    sorted_words = sorted(counts, key=lambda w: counts[w], reverse=True)

    # Step 6: Return the top_n unique keywords.
    return sorted_words[:top_n]


# Quick sanity check — remove once you understand the output:
# print(extract_keywords("python flask python sql python api flask sql"))
# Expected: ["python", "flask", "sql", "api"]


# ---------------------------------------------------------------------------
# Core analysis functions
# ---------------------------------------------------------------------------

def calculate_similarity(text_a, text_b):
    """
    Compute the TF-IDF cosine similarity between two pieces of text.

    Args:
        text_a (str): First document (e.g. resume text).
        text_b (str): Second document (e.g. job description).

    Returns:
        float: Similarity score between 0.0 (no overlap) and 1.0 (identical).
               Returns 0.0 if scikit-learn is not installed or if either
               document is empty.

    How cosine similarity works:
        Imagine each document as a point in a high-dimensional space where
        every unique word is one dimension and the TF-IDF weight is the
        coordinate on that axis.  The cosine similarity measures the angle
        between the two vectors — if they point in the same direction (same
        words, similar weights) the angle is 0° and cosine is 1.0.
        If they share nothing, the angle is 90° and cosine is 0.0.

    scikit-learn API used here:
        TfidfVectorizer().fit_transform([text_a, text_b])
            Returns a 2×N sparse matrix where N is the vocabulary size.
        cosine_similarity(matrix[0], matrix[1])
            Returns a 1×1 array with the similarity score.

    TODO:
        1. Return 0.0 early if SKLEARN_SUPPORT is False or if either
           text_a or text_b is empty after stripping whitespace.
        2. Create a TfidfVectorizer instance.
           Pass stop_words='english' so sklearn also removes common words.
        3. Call vectorizer.fit_transform([text_a, text_b]) — this tokenises
           both texts and computes TF-IDF weights in one step.
        4. Extract the two row vectors:
               vec_a = tfidf_matrix[0]
               vec_b = tfidf_matrix[1]
        5. Call cosine_similarity(vec_a, vec_b) and extract the scalar:
               score = cosine_similarity(vec_a, vec_b)[0][0]
        6. Return round(float(score), 4).

    Example (once complete):
        calculate_similarity("python flask sql", "sql flask django python")
        # -> something around 0.7 – 0.9 depending on TF-IDF weights
    """
    if not SKLEARN_SUPPORT:
        return 0.0

    # --- Write your similarity code here ---

    return 0.0


def find_missing_skills(resume_keywords, job_keywords, max_results=15):
    """
    Find keywords that appear in the job description but not in the resume.

    Args:
        resume_keywords (list[str]): Keywords extracted from the resume.
        job_keywords    (list[str]): Keywords extracted from the job description.
        max_results     (int):       Cap on how many missing skills to return.

    Returns:
        list[str]: Words from job_keywords that are absent in resume_keywords,
                   limited to max_results items.

    Why this matters:
        A similarity score tells you HOW WELL the resume matches, but not
        WHAT IS MISSING.  This function gives the actionable list — the
        exact words the recruiter will search for that your resume doesn't
        contain yet.

    TODO:
        1. Convert resume_keywords to a set for O(1) lookups.
        2. Iterate over job_keywords (order is preserved — most important first
           because extract_keywords() sorts by frequency).
        3. Collect words from job_keywords that are NOT in the resume set.
        4. Stop once you have max_results items.
        5. Return the list.

    Example:
        find_missing_skills(
            ["python", "flask", "sql"],
            ["python", "kubernetes", "docker", "sql", "terraform"]
        )
        # -> ["kubernetes", "docker", "terraform"]
    """
    # --- Write your gap analysis code here ---

    return []


def generate_feedback(score, missing_keywords, resume_keyword_count, job_keyword_count):
    """
    Produce a list of short, actionable feedback strings based on the analysis.

    Args:
        score                 (float):     TF-IDF similarity score (0.0 – 1.0).
        missing_keywords      (list[str]): Keywords in the job but not the resume.
        resume_keyword_count  (int):       Number of unique keywords found in resume.
        job_keyword_count     (int):       Number of unique keywords in job description.

    Returns:
        list[str]: 3 – 6 plain-English tips personalised to the analysis results.

    This is the "human layer" on top of the raw numbers.  A score of 0.32 is
    meaningless to most people; "Your resume covers about a third of the key
    topics in this role — focus on adding the missing technical keywords"
    is actionable.

    TODO:
        Build the feedback list using if/elif chains.  Some ideas:

        1. Score-based opening tip:
           - score >= 0.75: "Strong match! Your resume aligns well …"
           - score >= 0.50: "Good overlap. A few targeted additions …"
           - score >= 0.30: "Moderate match. Focus on the missing keywords …"
           - else:          "Low match. Consider rewriting key sections …"

        2. Missing keyword tip:
           - If len(missing_keywords) > 10:
               "Your resume is missing many key terms. Prioritise adding: …"
           - Elif len(missing_keywords) > 0:
               "Consider adding these terms where truthful: …"
           - Else:
               "You have covered the main keywords — great job!"

        3. Keyword density tip:
           - If resume_keyword_count < 20:
               "Your resume looks short or sparse. …"
           - Elif resume_keyword_count > 80:
               "Your resume is detailed. Make sure …"

        4. Quantification reminder (always include):
           "Add measurable achievements (numbers, percentages, scale) …"

        5. ATS tip (always include):
           "Many employers use ATS software. …"

        You decide the exact wording — make it helpful and encouraging.
    """
    feedback = []

    # --- Write your feedback generation code here ---

    # Always include these two universal tips
    feedback.append(
        "Add measurable achievements where possible — numbers, percentages, "
        "and scale (e.g. 'reduced latency by 40%') make a resume stand out."
    )
    feedback.append(
        "Many employers use Applicant Tracking Systems (ATS) that scan for "
        "exact keyword matches. Use the same terminology as the job posting."
    )

    return feedback


# ---------------------------------------------------------------------------
# Helper: map a score to a human-readable label and description
# ---------------------------------------------------------------------------

def score_to_label(score):
    """
    Return a (label, description) tuple for a similarity score.

    Args:
        score (float): Similarity score between 0.0 and 1.0.

    Returns:
        tuple[str, str]: (short_label, one_sentence_description)

    This function is already complete — no TODO here.
    Study how it works: it iterates over SCORE_LABELS in descending threshold
    order so the first threshold the score meets wins.
    """
    thresholds = sorted(SCORE_LABELS.keys(), reverse=True)
    for threshold in thresholds:
        if score >= threshold:
            label = SCORE_LABELS[threshold]
            descriptions = {
                "Excellent match": (
                    "Your resume closely mirrors the language and skills in this job posting."
                ),
                "Good match": (
                    "You cover most of the key areas — a few targeted additions could push "
                    "you higher."
                ),
                "Fair match": (
                    "There is noticeable overlap, but several important topics are missing "
                    "from your resume."
                ),
                "Weak match": (
                    "Your resume and this job description share little common vocabulary. "
                    "Consider tailoring your resume significantly."
                ),
            }
            return label, descriptions.get(label, "")
    return "Weak match", "Unable to score."


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    """
    GET /
    Render the upload form.

    This route is already complete — it just renders the embedded template.
    You do not need to change anything here.
    """
    return render_template_string(PAGE_TEMPLATE)


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    POST /analyze
    Accept a resume (PDF or text) and a job description, run the analysis
    pipeline, and return a JSON result.

    Expected request body (JSON):
        One of two shapes —

        Shape A — plain text resume:
            {
                "resume_text":    "Jane Doe, Software Engineer ...",
                "job_description": "We are looking for a Python developer ..."
            }

        Shape B — PDF upload (base64-encoded):
            {
                "resume_pdf_b64":  "<base64 string>",
                "resume_filename": "jane_doe_cv.pdf",
                "job_description": "We are looking for a Python developer ..."
            }

    Response (200 OK):
        {
            "score":            0.62,
            "label":            "Good match",
            "description":      "You cover most of the key areas ...",
            "present_keywords": ["python", "flask", "sql", ...],
            "missing_keywords": ["kubernetes", "docker", ...],
            "feedback":         ["Add measurable achievements ...", ...]
        }

    Error response (400 Bad Request):
        { "error": "Human-readable error message." }

    TODO:
        1. Parse the JSON body: data = request.get_json()
           Return 400 if body is missing or not valid JSON.

        2. Extract the job_description field.
           Return 400 if it is missing or blank.

        3. Determine resume text:
           - If "resume_pdf_b64" is in data:
               a. Decode it from base64 to bytes:
                      import base64
                      pdf_bytes = base64.b64decode(data["resume_pdf_b64"])
               b. Check it is within MAX_FILE_BYTES; return 400 if too large.
               c. Call extract_text_from_pdf(pdf_bytes).
               d. If the result is empty, return 400 with a helpful message
                  (the PDF may be scanned/image-only).
           - Else if "resume_text" is in data:
               Use data["resume_text"] directly.
           - Else return 400: "Provide either resume_text or resume_pdf_b64."

        4. Clean both texts using clean_text().

        5. Run the pipeline:
               resume_kw  = extract_keywords(clean_resume)
               job_kw     = extract_keywords(clean_job)
               score      = calculate_similarity(clean_resume, clean_job)
               missing    = find_missing_skills(resume_kw, job_kw)
               label, desc = score_to_label(score)
               feedback   = generate_feedback(score, missing,
                                              len(resume_kw), len(job_kw))

        6. Return jsonify({
               "score":            score,
               "label":            label,
               "description":      desc,
               "present_keywords": resume_kw[:20],
               "missing_keywords": missing,
               "feedback":         feedback,
           })

    Important Flask notes:
        - request.get_json() returns None if the Content-Type header is not
          'application/json'. Return a 400 error in that case.
        - Use jsonify() for all responses — it sets the correct Content-Type.
        - Return error responses as:
              return jsonify({"error": "message"}), 400
    """
    # base64 is imported at the top of the file — use it directly here.
    # --- Write your route handler here ---

    return jsonify({"error": "Route not yet implemented. Complete the TODO above."}), 501


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("AI Resume Analyzer starting...")
    print("Open http://127.0.0.1:5000 in your browser.\n")
    if not PDF_SUPPORT:
        print("  [!] PyPDF2 not installed — PDF upload disabled.")
        print("      pip install PyPDF2\n")
    if not SKLEARN_SUPPORT:
        print("  [!] scikit-learn not installed — similarity scoring disabled.")
        print("      pip install scikit-learn\n")
    app.run(debug=True)


# ---------------------------------------------------------------------------
# Sample inputs — useful for manual testing while you build
# ---------------------------------------------------------------------------
#
# Once the server is running, you can test the /analyze endpoint directly
# from the command line using curl (no browser needed):
#
#   curl -s -X POST http://127.0.0.1:5000/analyze \
#        -H "Content-Type: application/json" \
#        -d '{
#              "resume_text": "Python developer with 3 years experience. Skills include
#                              Flask, REST APIs, SQL, PostgreSQL, Git, and Docker.
#                              Built data pipelines using pandas and deployed services
#                              on AWS EC2.",
#              "job_description": "We are looking for a backend engineer proficient in
#                                  Python, Django or Flask, PostgreSQL, Docker,
#                                  Kubernetes, and CI/CD pipelines."
#            }'
#
# Expected response shape:
#   {
#     "score": 0.61,
#     "label": "Good match",
#     "present_keywords": ["python", "flask", "postgresql", "docker", ...],
#     "missing_keywords": ["kubernetes", "django", "cicd", ...],
#     "feedback": [...]
#   }
#
# You can also test the NLP helpers in isolation before wiring the route:
#
#   python -c "
#   from ai_resume_analyzer import clean_text, extract_keywords
#   sample = 'Experienced Python developer. Built REST APIs with Flask and SQL.'
#   cleaned = clean_text(sample)
#   print('Cleaned:', cleaned)
#   print('Keywords:', extract_keywords(cleaned))
#   "
