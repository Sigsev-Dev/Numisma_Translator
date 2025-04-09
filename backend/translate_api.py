from flask import Flask, request, jsonify
import os
from pdf_processor import extract_text_from_pdf
from translator import translate_text
from confidence_scorer import calculate_confidence
from langdetect import detect
import spacy
from sentence_transformers import SentenceTransformer, util

# Initialize app and models
app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load SpaCy Spanish tokenizer
try:
    nlp = spacy.load("es_core_news_sm")
except:
    import spacy.cli
    spacy.cli.download("es_core_news_sm")
    nlp = spacy.load("es_core_news_sm")

similarity_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def robust_detect_language(text_lines):
    detected = []
    for line in text_lines:
        try:
            if len(line.strip()) > 20:
                lang = detect(line)
                detected.append(lang)
        except:
            continue
    return max(set(detected), key=detected.count) if detected else "unknown"

def split_sentences(text):
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

def match_sentence_to_line(line, translated_pairs):
    if not line.strip():
        return "", 0.0
    best_match = ""
    best_score = -1
    line_vector = similarity_model.encode(line, convert_to_tensor=True)
    for original, translated in translated_pairs:
        try:
            score = util.pytorch_cos_sim(
                line_vector,
                similarity_model.encode(original, convert_to_tensor=True)
            ).item()
            if score > best_score:
                best_score = score
                best_match = translated
        except Exception as e:
            continue
    return best_match, round(best_score * 100, 2)

@app.route("/translate", methods=["POST"])
def translate_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    target_lang = request.form.get("target_lang", "eng")

    if not (file.filename.endswith(".pdf") or file.filename.endswith(".docx")):
        return jsonify({"error": "Only PDF or DOCX files are supported"}), 400

    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    try:
        # Step 1: Extract lines and full paragraph text
        raw_text = extract_text_from_pdf(pdf_path)
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        paragraph = " ".join(lines)

        # Step 2: Detect main language
        doc_lang = robust_detect_language(lines)
        print("Detected Language:", doc_lang)

        # Step 3: Translate every individual sentence
        sentences = split_sentences(paragraph)
        translated_pairs = []
        for sentence in sentences:
            try:
                translated_text, _ = translate_text(sentence, target_lang)
                translated_pairs.append((sentence, translated_text))
            except Exception as e:
                print(f"[⚠️] Failed to translate: '{sentence[:40]}...' — {e}")
                translated_pairs.append((sentence, "[⚠️ Translation Failed]"))

        # Step 4: Match each original line to the best sentence translation
        translations = []
        for line in lines:
            if len(line.strip()) < 4:
                translations.append({
                    "source_lang": doc_lang,
                    "original": line,
                    "translated": "[⚠️ Too short to match]",
                    "confidence": 0.0
                })
                continue

            translated_line, confidence = match_sentence_to_line(line, translated_pairs)
            if not translated_line:
                translated_line = "[⚠️ No Match Found]"
                confidence = 0.0

            translations.append({
                "source_lang": doc_lang,
                "original": line,
                "translated": translated_line,
                "confidence": confidence
            })

        return jsonify(translations)

    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
