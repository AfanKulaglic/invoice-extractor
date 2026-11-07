from fastapi import FastAPI
from pydantic import BaseModel
from invoice_processor import process_invoice

app = FastAPI(title="Invoice Extractor AI", version="1.0")


class InvoiceRequest(BaseModel):
    filename: str
    text: str


class InvoiceResponse(BaseModel):
    filename: str
    extracted: dict
    saved: bool


@app.post("/extract-invoice", response_model=InvoiceResponse)
def extract(req: InvoiceRequest):
    return process_invoice(req.filename, req.text)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
