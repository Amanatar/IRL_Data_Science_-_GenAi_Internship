# 🎬 YouTube Video → Insightful Article & PDF

Transform any YouTube video into a polished, SEO-optimized article with key insights and a downloadable PDF — powered by Google Gemini AI.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red?logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-0.2+-green)
![Gemini](https://img.shields.io/badge/Google_Gemini-2.0-yellow?logo=google)

---

## ✨ Features

| Feature | Description |
|---|---|
| 📝 **Smart Transcription** | Auto-extracts and cleans YouTube captions |
| 🤖 **AI Article Writer** | Generates polished, structured, SEO-optimized articles |
| 💡 **Key Insights** | Extracts actionable takeaways as bullet points |
| 📄 **PDF Export** | Professional, beautifully formatted downloadable PDF |
| 📏 **Summary Styles** | Choose between short (3-5 sentences) or detailed (8-12 sentences) |
| 💾 **Local Saving** | Auto-saves outputs as Markdown and PDF files |

---

## 📁 Project Structure

```
YouTube Video to Insightful Article & PDF/
│
├── app.py                  # Main Streamlit application (UI + orchestration)
├── config.py               # Configuration, env vars, and prompt templates
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables file
├── README.md               # This file
│
├── modules/
│   ├── __init__.py         # Package initializer
│   ├── transcript.py       # YouTube transcript extraction
│   ├── processing.py       # Text cleaning and preprocessing
│   ├── llm_engine.py       # LLM-powered content generation (Gemini)
│   └── pdf_generator.py    # Professional PDF creation
│
└── outputs/                # Generated PDFs and Markdown files (auto-created)
```

---

## 🚀 Quick Start

### 1. Clone / Navigate to Project

```bash
cd "YouTube Video to Insightful Article & PDF"
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up API Key

**Option A**: Copy the example env file and add your key:

```bash
copy .env.example .env
# Edit .env and paste your Google Gemini API key
```

**Option B**: Enter the key directly in the Streamlit sidebar when the app runs.

> **Get a free Google Gemini API key at:** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### 5. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 🎯 How It Works

```
YouTube URL → Extract Transcript → Clean Text → LLM Processing → Display & PDF
```

1. **Transcript Extraction** — Uses `youtube-transcript-api` to fetch captions
2. **Text Preprocessing** — Removes filler words, timestamps, auto-caption artifacts
3. **LLM Processing** — Google Gemini generates title, summary, article, and insights
4. **Output** — Displays results in a premium UI with downloadable PDF

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.9+** | Core language |
| **Streamlit** | Web UI framework |
| **LangChain** | LLM orchestration |
| **Google Gemini** | AI content generation |
| **youtube-transcript-api** | Transcript extraction |
| **fpdf2** | PDF generation |
| **python-dotenv** | Environment variable management |

---

## 📝 Configuration

All settings are in `config.py`:

- **`GEMINI_MODEL`** — Change the Gemini model (default: `gemini-2.0-flash`)
- **Prompt Templates** — Customize the prompts for title, summary, article, and insights generation
- **`OUTPUT_DIR`** — Change where generated files are saved

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request

---

## 📄 License

This project is open-source and available under the MIT License.
