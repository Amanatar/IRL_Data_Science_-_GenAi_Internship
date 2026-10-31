# Production GenAI & MLOps Suite (Innomatics Research Labs)

<div align="center">

[![CI Verified](https://github.com/Amanatar/IRL_Data_Science_-_GenAi_Internship/actions/workflows/ci-verify.yml/badge.svg)](https://github.com/Amanatar/IRL_Data_Science_-_GenAi_Internship/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![MLflow](https://img.shields.io/badge/MLflow-0194E2?logo=mlflow&logoColor=white)](https://mlflow.org)
[![AWS](https://img.shields.io/badge/AWS-EC2_%7C_Bedrock-232F3E?logo=amazon-aws&logoColor=white)](https://aws.amazon.com)

</div>

End-to-end production AI applications and MLOps pipelines developed during the Data Science & Generative AI engineering internship at Innomatics Research Labs. Deployed on AWS EC2 Ubuntu instances with Gunicorn daemons and real-time LLM failover.

---

## Shipped Systems & Architecture

### 1. FinWiser: Financial Intelligence Assistant (`finadvisor_ai/`)
- **Real-Time Dual-LLM Circuit Breaker:** Connects to Google Gemini API as primary engine and automatically falls back to NVIDIA NIM (Kimi 2 Thinker) with zero downtime when rate limits or API latency spikes occur.
- **Run Command:**
  ```bash
  cd finadvisor_ai
  pip install -r requirements.txt
  streamlit run app.py
  ```

### 2. Enterprise Bedrock RAG Knowledge Base (`final_projects/Enterprise Knowledge Base Q&A...`)
- **Knowledge Base Q&A:** Fully cited retrieval-augmented generation built on Amazon Bedrock Knowledge Bases using Titan text embeddings and Claude 3 / Llama foundation models.
- **Run Command:**
  ```bash
  cd "final_projects/Enterprise Knowledge Base Q&A System Using Amazon Bedrock Knowledge Bases (RAG Implementation)"
  streamlit run app.py
  ```

### 3. YouTube-to-Article & PDF Synthesis Engine (`final_projects/YouTube Video to Insightful Article...`)
- **Multi-Modal Synthesis:** Automated pipeline parsing YouTube transcripts, generating structured long-form technical write-ups, and compiling formatted PDF summaries using FPDF2.
- **Run Command:**
  ```bash
  cd "final_projects/YouTube Video to Insightful Article & PDF"
  streamlit run app.py
  ```

### 4. Flipkart Customer Sentiment Classifier & MLflow Registry (`Machine Learning/`)
- **Systematic Model Sweeps:** Evaluated 5 classification baselines (Logistic Regression, Naive Bayes, Linear SVM, Random Forest, Gradient Boosting) on e-commerce sentiment with centralized MLflow experiment tracking, shipped as a lightweight Flask service.

---

## Environment Setup

```bash
git clone https://github.com/Amanatar/IRL_Data_Science_-_GenAi_Internship.git
cd IRL_Data_Science_-_GenAi_Internship

python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

---

## License
MIT License. Copyright 2026 Aman Atar.
