# 🧠 NLP Cloud Toolkit

A command-line application that lets registered users run **Named Entity Recognition (NER)**, **Language Detection** and **Sentiment / Emotion Analysis** on any text, powered by the [NLP Cloud](https://nlpcloud.com) API.

## ✨ Features

- 🔐 **User accounts** – register and log in; passwords are salted and hashed (PBKDF2-HMAC-SHA256), never stored in plain text
- 🏷️ **NER** – extracts people, organisations, places, dates and more, with a per-type summary
- 🌐 **Language detection** – returns the most likely language plus runner-up candidates with confidence scores
- 😊 **Emotion analysis** – joy, sadness, anger, fear, love, surprise, shown as a score bar chart
- 🛡️ **Safe by design** – API key in `.env`, friendly errors for bad keys / rate limits / network issues
- ✅ **Tested** – unit tests run offline with a mocked API (no credits used)

## 📁 Project structure

```
OopProject/
├── main.py                 # entry point
├── nlp_app/
│   ├── auth.py             # registration, login, password hashing
│   ├── cli.py              # menus and output formatting
│   ├── config.py           # settings loaded from .env
│   └── nlp_service.py      # NLP Cloud API wrapper (NER, language, sentiment)
├── tests/                  # offline unit tests
├── .env.example            # template for your API key and settings
├── .gitignore              # excludes local secrets and generated files
├── requirements.txt
└── README.md
```

## 🚀 Getting started

**1. Clone and install**

```bash
git clone https://github.com/abhishekvermacsds/OopProject.git
cd OopProject
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**2. Add your API key**

Create a free account at [nlpcloud.com](https://nlpcloud.com), copy your API token from the dashboard, then:

```bash
cp .env.example .env             # Windows: copy .env.example .env
# open .env and set NLPCLOUD_API_KEY=your_key
```

The app can start without an API key, but NLP analysis features require one.

**3. Run**

```bash
python main.py
```

## 💬 Example session

```
How would you like to proceed?
  1. Not a member? Register
  2. Already a member? Login
  3. Galti se aa gaye? Exit
> 2
...
> 1
Enter the paragraph: Sundar Pichai announced Google's new office in Hyderabad last Monday.

ENTITY                          TYPE          POSITION
----------------------------------------------------------
Sundar Pichai                   PERSON        0-13
Google                          ORG           25-31
Hyderabad                       GPE           50-59
last Monday                     DATE          60-71

Summary -> PERSON: 1, ORG: 1, GPE: 1, DATE: 1
```

## ⚙️ Configuration

All options are environment variables (set in `.env`):

| Variable | Default | Purpose |
|---|---|---|
| `NLPCLOUD_API_KEY` | – (required) | Your NLP Cloud API token |
| `NER_MODEL` | `en_core_web_lg` | Model used for entity recognition |
| `LANGDETECT_MODEL` | `python-langdetect` | Model used for language detection |
| `SENTIMENT_MODEL` | `distilbert-base-uncased-emotion` | Model used for emotion analysis |
| `NLPCLOUD_GPU` | `false` | Use GPU inference (paid plans) |
| `USERS_FILE` | `data/users.json` | Where user accounts are stored |

## 🧪 Running the tests

```bash
python -m unittest discover -s tests -v
```

## 🔒 Security notes

- `.env` and `data/` are in `.gitignore`: never commit your API key or the users file.
- If a key is ever pushed to GitHub, revoke it in the NLP Cloud dashboard and generate a new one.
- The JSON user store is meant for learning/demo use; a production app should use a real database.

## 🗺️ Roadmap

- [ ] Save analysis history per user (CSV / SQLite) for later review
- [ ] Add summarization and keyword extraction
- [ ] Streamlit web interface
- [ ] Batch analysis of text files

## 📄 License

MIT: see [LICENSE](LICENSE).
