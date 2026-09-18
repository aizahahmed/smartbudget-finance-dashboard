from pathlib import Path
import re

import pandas as pd
import pytesseract
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader


PROJECT = Path(__file__).parent
INVOICE_FOLDER = PROJECT / "invoices"
OUTPUT_FOLDER = PROJECT / "outputs"

INVOICE_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)


def create_sample_invoice():
    """Create a clear fictional invoice for OCR testing."""
    sample_path = INVOICE_FOLDER / "sample_invoice.png"

    image = Image.new(
        "RGB",
        (1400, 1000),
        color="white",
    )

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        34,
    )

    invoice_text = """SMARTBUDGET SAMPLE INVOICE

Vendor: MarketWorks
Invoice Number: INV-2045
Invoice Date: 09/18/2026
Department: Technology

Description: Marketing analytics services
Subtotal: $12,000.00
Tax: $490.00
Total: $12,490.00

Payment Method: Wire"""

    draw.multiline_text(
        (80, 70),
        invoice_text,
        fill="black",
        font=font,
        spacing=22,
    )

    image.save(sample_path)

    print(
        f"Created fictional invoice: {sample_path.name}"
    )


def read_document(file_path):
    """Extract text from a PDF or image."""
    extension = file_path.suffix.lower()

    if extension == ".pdf":
        reader = PdfReader(file_path)

        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    if extension in {
        ".png",
        ".jpg",
        ".jpeg",
        ".tiff",
    }:
        image = Image.open(file_path)

        return pytesseract.image_to_string(
            image,
            config="--psm 6",
        )

    return ""


def find_value(pattern, text):
    """Find one value using a regular expression."""
    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    if match:
        return match.group(1).strip()

    return None


def parse_invoice(file_path, text):
    """Convert extracted invoice text into fields."""
    vendor = find_value(
        r"^Vendor\s*:\s*([^\n]+)",
        text,
    )

    invoice_number = find_value(
        r"^Invoice\s*(?:Number|No\.?)\s*:\s*([^\n]+)",
        text,
    )

    invoice_date = find_value(
        r"^Invoice\s*Date\s*:\s*([^\n]+)",
        text,
    )

    department = find_value(
        r"^Department\s*:\s*([^\n]+)",
        text,
    )

    total_text = find_value(
        r"^Total\s*:\s*\$?\s*([\d,]+\.\d{2})",
        text,
    )

    payment_method = find_value(
        r"^Payment\s*Method\s*:\s*([^\n]+)",
        text,
    )

    if total_text:
        total_amount = float(
            total_text.replace(",", "")
        )
    else:
        total_amount = None

    required_fields = [
        vendor,
        invoice_number,
        invoice_date,
        total_amount,
    ]

    return {
        "source_file": file_path.name,
        "vendor": vendor,
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "department": department,
        "total_amount": total_amount,
        "payment_method": payment_method,
        "review_required": (
            "Yes"
            if None in required_fields
            else "No"
        ),
    }


def main():
    create_sample_invoice()

    supported_extensions = {
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".tiff",
    }

    supported_files = [
        file_path
        for file_path in INVOICE_FOLDER.iterdir()
        if file_path.suffix.lower()
        in supported_extensions
    ]

    extracted_records = []

    for file_path in supported_files:
        print(f"Reading {file_path.name}...")

        extracted_text = read_document(
            file_path
        )

        text_output = (
            OUTPUT_FOLDER
            / f"{file_path.stem}_ocr_text.txt"
        )

        text_output.write_text(
            extracted_text,
            encoding="utf-8",
        )

        record = parse_invoice(
            file_path,
            extracted_text,
        )

        extracted_records.append(record)

    results = pd.DataFrame(
        extracted_records
    )

    output_file = (
        OUTPUT_FOLDER
        / "extracted_invoices.csv"
    )

    results.to_csv(
        output_file,
        index=False,
    )

    print("\nOCR completed")
    print(
        f"Documents processed: "
        f"{len(results)}"
    )

    print(
        results.to_string(index=False)
    )

    print(
        f"\nResults saved to: "
        f"{output_file}"
    )


if __name__ == "__main__":
    main()