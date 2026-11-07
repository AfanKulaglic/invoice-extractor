# Invoice & Document Extractor (Python + LLM)

## Poslovni problem
Administrativna ekipa ručno citai fakture i račune, upisuje broj, datum, iznos i dobavljača u sistem. Sporo, greške, gubitev podataka.

## Rješenje
Python + FastAPI servis koji:
- Prima tekst fakture (ili PDF pretvoren u tekst)
- Izvlači: broj fakture, datum, dobavljač, ukupan iznos, PDV, valuta
- Sprema u SQLite bazu
- Vraća JSON sa confidence skorom

## Tehnologije
- Python 3.11+
- FastAPI (REST API)
- SQLite (lokalna baza)
- Ollama (lokalni LLM — **besplatan**)
- python-dotenv, requests

## Kako pokrenuti

1. Instaliraj [Ollama](https://ollama.com)
   ```powershell
   ollama run llama3
   ```
2. U ovom folderu:
   ```powershell
   pip install -r requirements.txt
   copy .env.example .env
   python main.py
   ```
3. Testiraj na `http://localhost:8001/docs`

## Primjer zahteva
```json
POST /extract-invoice
{
  "filename": "faktura_001.pdf",
  "text": "Faktura br: INV-2026-042\nDatum: 15.10.2026.\nDobavljač: AutoServis d.o.o.\nIznos: 145,00 EUR\nPDV: 24,65 EUR"
}
```

## Primjer odgovora
```json
{
  "filename": "faktura_001.pdf",
  "extracted": {
    "invoice_number": "INV-2026-042",
    "invoice_date": "2026-10-15",
    "vendor": "AutoServis d.o.o.",
    "total_amount": 145.0,
    "tax_amount": 24.65,
    "currency": "EUR",
    "confidence": 0.88
  },
  "saved": true
}
```

## GitHub
github.com/AfanKulaglic/invoice-extractor
