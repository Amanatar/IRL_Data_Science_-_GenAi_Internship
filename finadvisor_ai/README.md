# 🏦 FinAdvisor AI

> **Your Personal AI-Powered Financial Advisor** — built with Google Gemini 1.5 Flash & Streamlit.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red.svg)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Google-Gemini-orange.svg)](https://ai.google.dev)
[![AWS EC2](https://img.shields.io/badge/Deployed-AWS%20EC2-yellow.svg)](https://aws.amazon.com/ec2)

---

## 🌐 Live Demo

**[http://43.204.23.183:8501](http://43.204.23.183:8501)**

---

## 📖 About

FinAdvisor AI is a conversational chatbot that provides personalized financial guidance. It covers:

- 📊 **Budgeting & Expense Tracking** — 50/30/20 rules, saving strategies
- 📈 **Investment Basics** — Stocks, ETFs, Bonds, Mutual Funds
- 🏦 **Retirement Planning** — 401k, IRA, Pension basics
- 💸 **Debt Management** — Student loans, credit cards, mortgages
- 🏠 **Financial Goal Setting** — Buying a home, education fund

> ⚠️ **Disclaimer:** FinAdvisor AI is for educational purposes only. It is not a licensed financial advisor. Always consult a certified professional before making major financial decisions.

---

## 🗂️ Project Structure

```
ai_chatbots/
├── app.py              # Streamlit UI — chat interface & layout
├── chatbot_engine.py   # Gemini API interaction logic
├── prompts.py          # Financial Advisor persona & system prompt
├── requirements.txt    # Python dependencies
├── .env.example        # Template for environment variables
└── PRD.md              # Product Requirements Document
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/finadvisor-ai.git
cd finadvisor-ai
```

### 2. Set Up Environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API Key
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

Get your free API key at [Google AI Studio](https://aistudio.google.com).

### 4. Run the App
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| [Streamlit](https://streamlit.io) | Web UI framework |
| [Google Gemini](https://ai.google.dev) | LLM / AI backbone |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Secure API key management |
| [AWS EC2](https://aws.amazon.com/ec2) | Cloud deployment |

---

## ☁️ Deploy to AWS EC2

```bash
# Transfer files
scp -i your-key.pem app.py chatbot_engine.py prompts.py requirements.txt .env ubuntu@YOUR_IP:~/finadvisor/

# On the server
cd ~/finadvisor
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
nohup ./venv/bin/streamlit run app.py --server.port 8501 --server.headless true &
```

> Remember to allow port **8501** in your EC2 Security Group (Custom TCP, 0.0.0.0/0).

---

## 📄 License

MIT License — feel free to use, modify, and share.
