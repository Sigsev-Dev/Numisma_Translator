from flask import Flask, request, jsonify
import os
from pdf_processor import extract_text_from_pdf
from translator import translate_text
from confidence_scorer import calculate_confidence

app = Flask(__name__)

# Set upload folder for temporary PDF storage
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure folder exists

@app.route("/translate", methods=["POST"])
def translate_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    target_lang = request.form.get("target_lang", "eng")  # Default to English if not provided

    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDFs are supported"}), 400

    # Save the uploaded file
    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    try:
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        sentences = text.split(". ")  # Split into sentences for better translation handling

        translations = []
        for sentence in sentences:
            translated_text, source_lang = translate_text(sentence, target_lang)
            confidence = calculate_confidence(sentence, translated_text)
            translations.append({
                "source_lang": source_lang,
                "original": sentence,
                "translated": translated_text,
                "confidence": confidence
            })

        return jsonify(translations)

    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
