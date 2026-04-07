<p align="center">
  <h1 align="center">💰 FinWise — AI Financial Advisor Chatbot</h1>
  <p align="center">
    A production-ready, multi-turn financial advisor chatbot powered by <strong>Google Gemini</strong> and <strong>Streamlit</strong>.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" />
  <img src="https://img.shields.io/badge/LLM-Google%20Gemini-orange?logo=google" />
  <img src="https://img.shields.io/badge/Frontend-Streamlit-red?logo=streamlit" />
  <img src="https://img.shields.io/badge/Deploy-AWS%20EC2-yellow?logo=amazon-aws" />
</p>

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Built-in Tools](#-built-in-tools)
- [Deployment — AWS EC2](#-deployment--aws-ec2)
- [Prompt Engineering](#-prompt-engineering)
- [Disclaimer](#-disclaimer)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI-Powered Advice** | Personal finance guidance via Google Gemini (multi-turn) |
| 📊 **SIP Calculator** | Compound-interest SIP estimator (`/sip 5000 10 12`) |
| ⚖️ **Risk Profiling** | Automatic classification into low / medium / high risk |
| 🧠 **Smart Memory** | Extracts income, goals, age, risk level from conversation |
| 🔄 **Retry & Fallback** | Exponential back-off + graceful fallback response |
| 📝 **Structured Logging** | Console + file logging for every API call |
| 🎨 **Premium UI** | Dark navy glassmorphism theme with micro-interactions |
| 🔒 **No Hardcoded Secrets** | All config via `.env` / environment variables |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                   STREAMLIT UI                       │
│  (Chat interface, sidebar tools, quick actions)      │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│                  CHAT SERVICE                        │
│  (Orchestrator: routes tools, builds prompts,        │
│   manages flow, SIP calc, risk profiler)             │
└─────────┬─────────────────┬──────────────────────────┘
          │                 │
          ▼                 ▼
┌─────────────────┐  ┌─────────────────────────────────┐
│  GEMINI CLIENT   │  │       MEMORY MANAGER            │
│  (API calls,     │  │  (Chat history, user profile,   │
│   retry logic,   │  │   context extraction, trim)     │
│   error handling)│  └─────────────────────────────────┘
└─────────────────┘
          │
          ▼
┌─────────────────┐
│  GOOGLE GEMINI   │
│  (GenAI API)     │
└─────────────────┘
```

**Design Principles:**
- **Single Responsibility** — each module does one thing well
- **Dependency Injection** — services are composed, not tightly coupled
- **Fail-Safe** — fallback responses when the API is unavailable
- **Observable** — structured logging at every layer

---

## 📁 Project Structure

```
Production-Ready GenAI Chatbot Project/
│
├── frontend/
│   ├── __init__.py
│   └── streamlit_app.py        # Streamlit chat UI
│
├── backend/
│   ├── __init__.py
│   ├── gemini_client.py        # Google Gemini API wrapper
│   ├── chat_service.py         # Business logic orchestrator
│   └── memory_manager.py       # Session memory & profile extraction
│
├── prompts/
│   ├── __init__.py
│   └── system_prompt.py        # System prompt with dynamic profile
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Env-based configuration
│
├── utils/
│   ├── __init__.py
│   └── logger.py               # Centralised logging
│
├── .streamlit/
│   └── config.toml             # Streamlit theme & server config
│
├── .env.example                # Template for environment variables
├── .gitignore
├── requirements.txt
└── README.md                   # ← You are here
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- A Google Gemini API key ([get one here](https://aistudio.google.com/apikey))

### 1. Clone & enter the project
```bash
git clone <your-repo-url>
cd "Production-Ready GenAI Chatbot Project"
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and paste your GEMINI_API_KEY
```

### 5. Run the app
```bash
streamlit run frontend/streamlit_app.py
```

The app opens at **http://localhost:8501** 🎉

---

## ⚙️ Configuration

All settings are loaded from environment variables (via `.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | *(required)* | Your Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Model name |
| `TEMPERATURE` | `0.7` | Creativity (0.0 – 1.0) |
| `MAX_OUTPUT_TOKENS` | `2048` | Max response length |
| `TOP_P` | `0.9` | Nucleus sampling |
| `TOP_K` | `40` | Top-K sampling |
| `MAX_HISTORY_TURNS` | `20` | Conversation window size |
| `MAX_RETRIES` | `3` | API retry attempts |
| `RETRY_DELAY` | `1.0` | Base retry delay (seconds) |

---

## 🛠️ Built-in Tools

Type these commands directly in chat:

| Command | Example | Description |
|---------|---------|-------------|
| `/sip` | `/sip 5000 10 12` | Calculate SIP maturity (₹5k/mo, 10 yrs, 12% p.a.) |
| `/risk` | `/risk` | View your risk profile assessment |
| `/profile` | `/profile` | See all collected financial profile data |

---

## 🚢 Deployment — AWS EC2

### Step 1: Launch an EC2 Instance
- **AMI:** Ubuntu 22.04 LTS
- **Instance type:** `t2.micro` (free tier) or `t3.small`
- **Security group:** Allow inbound TCP on port **8501**
- **Storage:** 20 GB gp3

### Step 2: Connect & set up
```bash
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install -y python3 python3-pip python3-venv git
```

### Step 3: Deploy the project
```bash
# Clone
git clone <your-repo-url> finwise
cd finwise

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Dependencies
pip install -r requirements.txt

# Environment
cp .env.example .env
nano .env   # paste your GEMINI_API_KEY
```

### Step 4: Run in background (tmux)
```bash
# Install tmux
sudo apt install -y tmux

# Create a named session
tmux new -s finwise

# Inside tmux
source venv/bin/activate
streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0

# Detach: Ctrl+B then D
# Re-attach: tmux attach -t finwise
```

### Step 5: Access the app
Open in your browser:
```
http://<EC2_PUBLIC_IP>:8501
```

### Alternative: Run with nohup
```bash
nohup streamlit run frontend/streamlit_app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  > logs/streamlit.log 2>&1 &
```

### Optional: Systemd Service (production)
```bash
sudo tee /etc/systemd/system/finwise.service << 'EOF'
[Unit]
Description=FinWise AI Financial Advisor
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/finwise
ExecStart=/home/ubuntu/finwise/venv/bin/streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=5
EnvironmentFile=/home/ubuntu/finwise/.env

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable finwise
sudo systemctl start finwise
```

---

## 📝 Prompt Engineering

The system prompt in `prompts/system_prompt.py` is designed with:

1. **Persona** — Expert financial advisor named FinWise
2. **Capabilities** — Budgeting, investing, savings, tax, debt, retirement
3. **Communication style** — Warm, jargon-free, structured (bullets, tables, steps)
4. **Follow-up behaviour** — Asks clarifying questions before advising
5. **Guardrails** — No guaranteed returns, no illegal advice, always disclaims
6. **Dynamic profile** — User's financial context is injected into every prompt

---

## ⚠️ Disclaimer

> **This chatbot provides educational financial guidance only and not professional financial advice.**
> Always consult a certified financial planner before making investment decisions.
> Past performance does not guarantee future results. The creators of this tool assume no liability for financial decisions made based on its output.

---

## 📄 License

This project is for educational and demonstration purposes.

---

<p align="center">
  Built with ❤️ using Google Gemini & Streamlit
</p>
