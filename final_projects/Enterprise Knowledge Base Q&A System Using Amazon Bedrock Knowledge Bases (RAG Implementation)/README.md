# 🧠 Enterprise Knowledge Base Q&A System

> **RAG-powered chatbot using Amazon Bedrock Knowledge Bases**  
> Ask questions about your organization's documents and get accurate, cited answers.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-Bedrock-orange?logo=amazon-aws&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red?logo=streamlit&logoColor=white)

---

## 📋 Table of Contents

- [Architecture](#-architecture)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Project Structure](#-project-structure)
- [Setup Instructions](#-setup-instructions)
- [Running the Application](#-running-the-application)
- [Configuration Reference](#-configuration-reference)
- [Troubleshooting](#-troubleshooting)

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│   Streamlit UI  │────▶│   Backend Engine  │────▶│  Amazon Bedrock         │
│   (app.py)      │     │   (backend.py)    │     │  Knowledge Base         │
│                 │◀────│                   │◀────│  (Retrieve & Generate)  │
│  • Chat UI      │     │  • boto3 client   │     │                         │
│  • Citations    │     │  • Error handling │     │  • Vector search        │
│  • History      │     │  • Response parse │     │  • Claude 3 generation  │
└─────────────────┘     └──────────────────┘     └─────────────────────────┘
                               │
                        ┌──────┴──────┐
                        │  config.py  │
                        │  (.env)     │
                        └─────────────┘
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **RAG Pipeline** | Retrieves relevant documents first, then generates answers |
| 📄 **Source Citations** | Every answer includes clickable source references |
| 🛡️ **Anti-Hallucination** | System prompt restricts answers to document content only |
| 💬 **Multi-Turn Chat** | Session-aware conversations with context retention |
| ⚡ **Error Handling** | Graceful handling of AWS errors with user-friendly messages |
| 📊 **Session Stats** | Tracks queries and messages in the sidebar |
| 🎨 **Premium UI** | Dark-themed, ChatGPT-style interface with animations |
| 🔐 **Secure Config** | Credentials via environment variables, never hardcoded |

---

## 📋 Prerequisites

1. **Python 3.9+** installed on your system
2. **AWS Account** with:
   - IAM user with Bedrock access permissions
   - Access Key ID and Secret Access Key
3. **Amazon Bedrock Knowledge Base** already created with:
   - Documents uploaded to S3
   - Data source synced
   - Knowledge Base ID noted
4. **Bedrock Model Access** enabled for Claude 3 Sonnet (or your preferred model) in `ap-south-1`

### Required IAM Permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:RetrieveAndGenerate",
                "bedrock:Retrieve"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## 📁 Project Structure

```
Enterprise Knowledge Base Q&A System/
│
├── app.py                  # Streamlit frontend (ChatGPT-style UI)
├── backend.py              # Bedrock RAG engine (retrieve & generate)
├── config.py               # Environment loading & validation
├── requirements.txt        # Python dependencies
├── .env.example            # Template for environment variables
├── .env                    # Your actual credentials (git-ignored)
├── .gitignore              # Git ignore rules
├── README.md               # This file
│
└── (sample documents)
    ├── company_policy.pdf
    ├── hr_guidelines.pdf
    └── it_security_policy.pdf
```

---

## 🚀 Setup Instructions

### Step 1: Clone / Navigate to the Project

```bash
cd "Enterprise Knowledge Base Q&A System Using Amazon Bedrock Knowledge Bases (RAG Implementation)"
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy the example file
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux
```

Edit `.env` with your actual values:

```env
AWS_ACCESS_KEY_ID=AKIA...your-key...
AWS_SECRET_ACCESS_KEY=wJal...your-secret...
AWS_REGION=ap-south-1
BEDROCK_KNOWLEDGE_BASE_ID=XXXXXXXXXX
```

### Step 5: Verify AWS Setup

Before running the app, verify your Bedrock access:

```python
python -c "from config import load_aws_config, load_bedrock_config; print('✅ Config OK:', load_aws_config().region)"
```

---

## ▶️ Running the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### What to Expect

1. **Sidebar** shows connection status, session stats, and example questions
2. **Chat input** at the bottom — type your question and press Enter
3. **Answers** appear with source citations showing which documents were used
4. **Clear Conversation** button resets the chat

---

## ⚙️ Configuration Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AWS_ACCESS_KEY_ID` | ✅ | — | Your AWS access key |
| `AWS_SECRET_ACCESS_KEY` | ✅ | — | Your AWS secret key |
| `AWS_REGION` | ❌ | `ap-south-1` | AWS region |
| `BEDROCK_KNOWLEDGE_BASE_ID` | ✅ | — | Your Knowledge Base ID |
| `BEDROCK_MODEL_ARN` | ❌ | Claude 3 Sonnet | Full model ARN |
| `BEDROCK_MAX_RESULTS` | ❌ | `5` | Number of documents to retrieve |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Access Denied** | Verify IAM permissions include `bedrock:RetrieveAndGenerate` |
| **Knowledge Base Not Found** | Double-check `BEDROCK_KNOWLEDGE_BASE_ID` in `.env` |
| **Model Not Available** | Ensure Claude 3 Sonnet is enabled in your region via the Bedrock console |
| **Throttling Errors** | Wait a moment and retry; consider requesting quota increase |
| **Connection Timeout** | Check network connectivity and VPN settings |
| **Import Errors** | Ensure virtual environment is activated and dependencies installed |

### Enable Debug Logging

```env
LOG_LEVEL=DEBUG
```

---

## 📜 License

This project is built for educational and enterprise internal use.

---

<p align="center">
  Built with ❤️ using Amazon Bedrock, Python, and Streamlit
</p>
