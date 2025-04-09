from pdfminer.high_level import extract_text

pdf_path = "./docs/Ueno Bank - AML _shorter verwsion.pdf"

import re

# Extract text
extracted_text = extract_text(pdf_path)

# Print first 500 characters
print(f"Extracted Text Preview:\n{extracted_text[:2000]}")

# Check for special or invisible characters
hidden_chars = re.findall(r"[\u200B-\u200D\uFEFF]", extracted_text)
if hidden_chars:
    print(f"⚠️ Hidden characters found in the extracted text: {hidden_chars}")
else:
    print("✅ No hidden characters detected.")

# Check if text contains non-printable characters
non_printable_chars = re.findall(r"[^\x20-\x7E]", extracted_text)
if non_printable_chars:
    print(f"⚠️ Non-printable characters detected: {non_printable_chars}")
else:
    print("✅ No non-printable characters detected.")
