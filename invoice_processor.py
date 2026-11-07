import sqlite3
import json
import re
import os
from datetime import datetime
from typing import Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
DB_PATH = os.getenv("DB_PATH", "./data/invoice_extractor.db")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        raw_text TEXT,
        invoice_number TEXT,
        invoice_date TEXT,
        vendor TEXT,
        total_amount REAL,
        tax_amount REAL,
        currency TEXT,
        created_at TEXT
    )"""
    )
    conn.commit()
    conn.close()


def extract_invoice_fields(text: str) -> Dict[str, Any]:
    prompt = f"""
    Extract invoice information from the following text. Return ONLY valid JSON:
    {{
      "invoice_number": "...",
      "invoice_date": "...",
      "vendor": "...",
      "total_amount": 0.0,
      "tax_amount": 0.0,
      "currency": "EUR",
      "confidence": 0.0-1.0
    }}

    If a field is not found, use null or empty string.

    Text:
    {text[:3000]}
    """

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=60,
        )
        if resp.status_code == 200:
            raw = resp.json().get("response", "{}")
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(raw[start:end])
    except Exception as e:
        print(f"Ollama unavailable: {e}")

    # Fallback regex extraction
    inv_num = re.search(r"(?:invoice|broj|#)[:\s]*([A-Z0-9\-]+)", text, re.I)
    date = re.search(r"(\d{1,2}[\.\-/]\d{1,2}[\.\-/]\d{2,4})", text)
    amount = re.search(r"([\d]+[\.,]\d{2})\s*(EUR|KM|€)?", text)

    return {
        "invoice_number": inv_num.group(1) if inv_num else None,
        "invoice_date": date.group(1) if date else None,
        "vendor": None,
        "total_amount": float(amount.group(1).replace(",", ".")) if amount else None,
        "tax_amount": None,
        "currency": "EUR",
        "confidence": 0.5,
    }


def process_invoice(filename: str, text: str) -> Dict[str, Any]:
    init_db()
    result = extract_invoice_fields(text)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """INSERT INTO invoices (filename, raw_text, invoice_number, invoice_date, vendor,
           total_amount, tax_amount, currency, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            filename,
            text[:5000],
            result.get("invoice_number"),
            result.get("invoice_date"),
            result.get("vendor"),
            result.get("total_amount"),
            result.get("tax_amount"),
            result.get("currency"),
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()

    return {
        "filename": filename,
        "extracted": result,
        "saved": True,
    }
