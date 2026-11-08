# IT2025C Week 11 - Week 10's app, ready to go online: a landing page you make yours, and the key in .env.
# Run:    python3 app.py      then open http://127.0.0.1:5001
# Needs:  python3 -m pip install -r requirements.txt
# The whole app is in this one file. Your pictures go in the public/ folder.

import io
import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template_string, request, jsonify

# ---------- 1. Settings ----------
load_dotenv()                                              # reads .env from this folder, if it exists
key = os.environ.get("BEARCAT_KEY", "")                    # new: the key lives in .env, not in this file

url = "https://apim-azr-ue2-bgpt-prd-ucin.azure-api.net/openai/deployments/gpt-5.4-ptu/chat/completions?api-version=2024-10-21"
NO_ANSWER = "The file does not answer this question."
instructions = (
    "Answer the question in plain sentences, using the files below. You may summarize, explain, and combine parts of them.\n"
    "Only if nothing in the files is related to the question, reply with exactly this sentence: " + NO_ANSWER
)


# ---------- 2. Read: any file -> text (Week 9) ----------
def read_any(filename, data):
    """data is the raw bytes of the file. Return the text inside it."""
    name = filename.lower()
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))       # treat the bytes as a file
        text = ""
        for page in reader.pages:
            text = text + page.extract_text() + "\n"
        return text
    if name.endswith(".docx"):
        import docx
        document = docx.Document(io.BytesIO(data))
        text = ""
        for paragraph in document.paragraphs:
            text = text + paragraph.text + "\n"
        return text
    return data.decode("utf-8", errors="replace")  # .txt .csv .md: the bytes already are text


# ---------- 3. Ask: send the whole text of every file and the question to GPT-5.4 (Week 10) ----------
def ask_files(file_texts, prompt):
    """file_texts is a list of (file name, text). The model reads all of it."""
    if key in ("", "PASTE-YOUR-KEY-HERE"):                # new: no key in .env, so say so instead of calling the model
        return "No key found. Copy .env.example to .env and put your key after BEARCAT_KEY="
    context = ""
    for name, text in file_texts:
        context = context + "File: " + name + "\n" + text + "\n\n"
    payload = {
        "model": "gpt-5.4-ptu",
        "messages": [{"role": "system", "content": instructions}, {"role": "user", "content": "Files:\n" + context + "Question: " + prompt}],
        "max_completion_tokens": 2000
    }
    response = requests.post(url, headers={"api-key": key}, json=payload)
    data = response.json() if "json" in response.headers.get("Content-Type", "") else {}   # some errors are not JSON
    if "choices" not in data:
        return "The API said no (status " + str(response.status_code) + "): " + (str(data) if data else response.text[:300])
    return data["choices"][0]["message"]["content"]


# ---------- 4. The web app: three pages and a health check ----------
app = Flask(__name__, static_folder="public", static_url_path="")   # new: public/hero.png is at /hero.png


@app.route("/")
def home():
    return render_template_string(LANDING_PAGE)            # new: the first page people see


@app.route("/start")
def start():
    return render_template_string(INDEX_PAGE)              # the form (it was at / in Week 10)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "Week 11 app is running."})


@app.route("/ask", methods=["POST"])
def ask():
    prompt = request.form.get("prompt", "").strip()
    uploads = [u for u in request.files.getlist("file") if u.filename != ""]   # one or more files
    if prompt == "" or uploads == []:
        return render_template_string(RESULT_PAGE, files=[], prompt=prompt,
                                      answer="Choose at least one file and type a question first.")
    file_texts = []
    for upload in uploads:
        file_texts.append((upload.filename, read_any(upload.filename, upload.read())))   # bytes -> text
    answer = ask_files(file_texts, prompt)                  # the model reads every file
    return render_template_string(RESULT_PAGE, files=[u.filename for u in uploads], prompt=prompt, answer=answer)


# ---------- 5. The pages: how they look (STYLE) and what they say ----------
# Change STYLE or a page, save, and refresh the browser.
# Asking BearcatGPT for help? Paste this part. Your key is in .env, not here.

STYLE = """
/* Make it yours: change these values first. */
:root {
  --brand: #e00122;      /* your project's color: header, buttons, links */
  --page: #f4f5f7;       /* the page background */
  --text: #1f2933;       /* normal text */
  --muted: #6b7280;      /* small, less important text */
}

/* One readable column in the middle of the page */
body {
  font-family: Arial, sans-serif;
  color: var(--text);
  background: var(--page);
  max-width: 760px;
  margin: 0 auto;
  padding: 0 16px 40px;
  line-height: 1.5;
}

/* A bar at the top of every page */
.nav { display: flex; gap: 16px; padding: 12px 0; font-weight: bold; }
.nav a { color: var(--brand); text-decoration: none; }

/* The header: the biggest thing on the page says what the app is */
.header {
  background: var(--brand);
  color: white;
  padding: 20px 24px;
  border-radius: 12px;
  margin-bottom: 24px;
}
.header h1 { margin: 0 0 4px; }
.header p { margin: 0; }

/* The picture on the landing page */
.hero { width: 100%; border-radius: 12px; margin-bottom: 24px; display: block; }

/* Cards: a white box groups things that belong together */
.card {
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}
.steps { display: flex; gap: 12px; flex-wrap: wrap; margin: 16px 0; }
.step { flex: 1; min-width: 160px; background: var(--page); border-radius: 10px; padding: 12px 14px; }
label { display: block; font-weight: bold; margin: 12px 0 6px; }
input, textarea { width: 100%; box-sizing: border-box; font: inherit; padding: 8px; }
button, .button {
  display: inline-block;
  margin-top: 16px;
  background: var(--brand);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font: inherit;
  font-weight: bold;
  text-decoration: none;
}
.answer { font-size: 18px; white-space: pre-wrap; border-left: 6px solid var(--brand); }
.note { color: var(--muted); font-size: 14px; }
"""

# The landing page: what the app is, who it is for, and one button to start. Make every line yours.
LANDING_PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Chat With Your File</title>
    <style>""" + STYLE + """</style>
  </head>
  <body>
    <nav class="nav"><a href="/">Home</a><a href="/start">Ask a question</a></nav>
    <header class="header">
      <h1>Malfind</h1>
      <p>Submit your suspected malware samples here.</p>
    </header>
    <img class="hero" src="/matrix-code.webp" alt="Matrix Code">
    <div class="card">
      <h2>Who it is for</h2>
      <p>Anyone with any potentially malicious files.</p>
      <h2>How it works</h2>
      <div class="steps">
        <div class="step"><strong>1. Upload</strong><br>One or more files: PDF, Word, or text.</div>
        <div class="step"><strong>2. Ask</strong><br>One question, in plain words.</div>
        <div class="step"><strong>3. Read</strong><br>An answer that uses only your files.</div>
      </div>
      <a class="button" href="/start">Start</a>
    </div>
    <p class="note">Use fictional or public files only.</p>
  </body>
</html>"""

# The form. The button changes while the model reads your files.
INDEX_PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Ask a Question</title>
    <style>""" + STYLE + """</style>
  </head>
  <body>
    <nav class="nav"><a href="/">Home</a><a href="/start">Ask a question</a></nav>
    <header class="header">
      <h1>Ask a Question</h1>
      <p>Upload one or more files and ask one question about them.</p>
    </header>
    <form class="card" action="/ask" method="post" enctype="multipart/form-data"
          onsubmit="this.querySelector('button').textContent = 'Reading your files...';">
      <label for="file">Your files: one or more (.txt, .csv, .md, .pdf, .docx)</label>
      <input type="file" id="file" name="file" accept=".txt,.csv,.md,.pdf,.docx" multiple>
      <label for="prompt">Your question</label>
      <textarea id="prompt" name="prompt" rows="3"></textarea>
      <button type="submit">Ask</button>
    </form>
    <p class="note">Use fictional or public files only.</p>
  </body>
</html>"""

# The answer page. {{ name }} prints a value from Python.
RESULT_PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Answer</title>
    <style>""" + STYLE + """</style>
  </head>
  <body>
    <nav class="nav"><a href="/">Home</a><a href="/start">Ask a question</a></nav>
    <header class="header">
      <h1>Answer</h1>
      <p><strong>Files:</strong> {{ files|join(", ") }} &middot; <strong>Question:</strong> {{ prompt }}</p>
    </header>
    <div class="card answer">{{ answer }}</div>
    <a class="button" href="/start">Ask another question</a>
  </body>
</html>"""


if __name__ == "__main__":
    app.run(debug=True, port=5001)   # 5001, not 5000: on a Mac, AirPlay already uses 5000


# ---------- 6. Notes ----------
# The key: copy .env.example to .env (Windows: copy .env.example .env), then put your key after BEARCAT_KEY=
#   .gitignore keeps .env out of Git and GitHub. Check with: git status
#
# Make it yours, on the landing page:
#   --brand in STYLE (your color), the <title> and <h1> (your app's name), the sentence under it,
#   the picture (put yours in public/ and change src="/hero.png"), "Who it is for", and the three steps.
#
# Stuck?
#   No module named ...          -> python3 -m pip install -r requirements.txt
#   No key found                 -> .env missing, still the placeholder, or not named BEARCAT_KEY; fix it, then Control+C and run python3 app.py again
#   The API said no (413, 500, or 504) -> your files are too long for one question: try one shorter file
#   The picture does not show    -> is it in public/? Does src="/your-file.png" match the name exactly, capitals too?
#   Address already in use       -> another app (Week 10?) is still running: press Control+C in its terminal
#   Page looks the same after a change -> save app.py; Flask restarts by itself; then Cmd+Shift+R (Windows: Ctrl+F5)
#   Windows: use py instead of python3.
