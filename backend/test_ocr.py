from pdf_processor import extract_text_from_pdf

pdf_file = "./docs/sample_scanned.pdf"
extracted_text = extract_text_from_pdf(pdf_file)
print("Extracted OCR Text:\n", extracted_text)
