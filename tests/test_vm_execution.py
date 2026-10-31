import os
import sys
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "finadvisor_ai"))
sys.path.insert(0, str(REPO_ROOT / "MLOPS_task_1"))

from chatbot_engine import call_with_failover
from app import clean_text, model, vectorizer

def test_circuit_breaker_failover():
    # Test primary throttle (mock 429) failover to secondary provider
    res = call_with_failover("What is a debt service coverage ratio (DSCR)?", force_failover=True)
    
    assert res["status"] == "FAILOVER_ACTIVE"
    assert res["provider"] == "NVIDIA-NIM"
    assert "DSCR" in res["text"] or "Debt Service" in res["text"]
    
    print(f"\n[VM EXECUTION] Dual-LLM Circuit Breaker: Primary Gemini throttled ({res['reason']}).")
    print(f"[VM EXECUTION] -> Successfully failed over to Provider: {res['provider']} (Model: {res['model']})")
    print(f"[VM EXECUTION] -> Failover Response: '{res['text'][:85]}...'")

def test_sentiment_classification_inference():
    sample_review = "The product arrived in perfect condition and battery life exceeded expectations!"
    cleaned = clean_text(sample_review)
    X = vectorizer.transform([cleaned])
    pred = model.predict(X)[0]
    prob = model.predict_proba(X)[0]
    
    sentiment = "Positive" if pred == 1 else "Negative"
    confidence = round(max(prob) * 100, 2)
    
    print(f"\n[VM EXECUTION] Consumer Review Sentiment Pipeline:")
    print(f"[VM EXECUTION] -> Input: '{sample_review}'")
    print(f"[VM EXECUTION] -> Classification: '{sentiment}' (Confidence: {confidence}%)")
    
    assert sentiment == "Positive"
    assert confidence > 50.0

def test_modules_syntax_compilation():
    # Verify Bedrock and YouTube modules syntax on Linux
    py_files = []
    for root, dirs, files in os.walk(str(REPO_ROOT / "final_projects")):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
                
    compiled_count = 0
    for pf in py_files:
        with open(pf, "r", encoding="utf-8") as f_obj:
            compile(f_obj.read(), pf, "exec")
            compiled_count += 1
            
    print(f"\n[VM EXECUTION] Verified {compiled_count} Python modules in final_projects compile cleanly without syntax errors.")
    assert compiled_count >= 4
