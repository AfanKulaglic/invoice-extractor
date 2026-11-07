import sys
sys.path.insert(0, '.')
from invoice_processor import extract_invoice_fields


def test_extracts_invoice_number():
    result = extract_invoice_fields("Invoice number: INV-2026-042")
    assert result["invoice_number"] == "INV-2026-042"


def test_extracts_total_amount():
    result = extract_invoice_fields("Total: 145.00 EUR")
    assert result["total_amount"] == 145.0


def test_extracts_vendor():
    result = extract_invoice_fields("Vendor: AutoServis d.o.o.")
    assert result["vendor"] == "AutoServis d.o.o."