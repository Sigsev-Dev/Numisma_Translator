import streamlit as st
import requests
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from streamlit_extras.stylable_container import stylable_container

supported_languages = {
    "Afar": "aar", "Abkhazian": "abk", "Afrikaans": "afr", "Albanian": "sqi", "Amharic": "amh", 
    "Arabic": "ara", "Armenian": "hye", "Azerbaijani": "aze_Latn", "Basque": "eus", "Belarusian": "bel",
    "Bengali": "ben", "Bosnian": "bos_Latn", "Bulgarian": "bul", "Burmese": "mya", "Catalan": "cat",
    "Chinese (Simplified)": "cmn_Hans", "Chinese (Traditional)": "cmn_Hant", "Croatian": "hrv",
    "Czech": "ces", "Danish": "dan", "Dutch": "nld", "English": "eng", "Estonian": "est", 
    "Filipino": "fil", "Finnish": "fin", "French": "fra", "Galician": "glg", "Georgian": "kat", 
    "German": "deu", "Greek": "ell", "Gujarati": "guj", "Haitian Creole": "hat", "Hebrew": "heb",
    "Hindi": "hin", "Hungarian": "hun", "Icelandic": "isl", "Indonesian": "ind", "Irish": "gle",
    "Italian": "ita", "Japanese": "jpn", "Javanese": "jav", "Kannada": "kan", "Kazakh": "kaz",
    "Khmer": "khm", "Korean": "kor", "Kurdish": "kur_Latn", "Lao": "lao", "Latvian": "lav", 
    "Lithuanian": "lit", "Macedonian": "mkd", "Malay": "msa_Latn", "Malayalam": "mal", "Maltese": "mlt",
    "Mongolian": "mon", "Nepali": "nep", "Norwegian": "nob", "Pashto": "pus", "Persian": "fas",
    "Polish": "pol", "Portuguese": "por", "Punjabi": "pan_Guru", "Romanian": "ron", "Russian": "rus",
    "Serbian": "srp_Cyrl", "Sinhala": "sin", "Slovak": "slk", "Slovenian": "slv", "Spanish": "spa",
    "Swahili": "swh", "Swedish": "swe", "Tamil": "tam", "Telugu": "tel", "Thai": "tha",
    "Turkish": "tur", "Ukrainian": "ukr", "Urdu": "urd", "Uzbek": "uzb_Latn", "Vietnamese": "vie",
    "Welsh": "cym", "Xhosa": "xho", "Yiddish": "yid", "Zulu": "zul"
}

# Set Streamlit page configuration
st.set_page_config(page_title="AI Document Translator", layout="wide")

st.title("📄 Numisma AI Document Translator")
st.markdown("### Upload a PDF to translate its content")

# File uploader for PDF
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

# Select target language
target_lang_name = st.selectbox("Select Target Language", list(supported_languages.keys()), index=21)  # Default: English
target_lang_code = supported_languages[target_lang_name]  # Get language code


translations = None  # Variable to store translation results

# Function to create translated PDF
def create_translated_pdf(translations):
    """Creates a properly formatted PDF with translated text."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Translated Document")

    y_position = 750  # Start position

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, y_position, "Translated Document")
    y_position -= 30

    pdf.setFont("Helvetica", 12)
    for translation in translations:
        translated_text = translation["translated"]

        # Wrap text if too long
        lines = simpleSplit(translated_text, pdf._fontname, pdf._fontsize, 400)
        for line in lines:
            pdf.drawString(100, y_position, line)
            y_position -= 20  # Move down

            if y_position < 50:  # Start a new page if space runs out
                pdf.showPage()
                y_position = 750

    pdf.save()
    buffer.seek(0)
    return buffer

# Function to create comparison PDF
def create_comparison_pdf(translations):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Comparison Document")

    y_position = 750  # Start position
    row_height = 40   # Height of each row (adjustable)
    padding = 10      # Extra padding between rows

    # Define column positions
    col_positions = [80, 280, 480, 580]  # X positions for column dividers

    # Draw title
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(100, y_position, "Original vs Translated Text with Confidence Scores")
    y_position -= 30

    # Draw table headers
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(100, y_position, "Original Text")
    pdf.drawString(300, y_position, "Translated Text")
    pdf.drawString(500, y_position, "Confidence Score")

    # Draw header divider
    pdf.line(col_positions[0], y_position - 5, col_positions[-1], y_position - 5)
    y_position -= row_height

    pdf.setFont("Helvetica", 10)

    for translation in translations:
        original_text = translation["original"]
        translated_text = translation["translated"]
        confidence = f"{translation['confidence']}%"

        # Wrap text properly
        orig_lines = simpleSplit(original_text, "Helvetica", 10, 180)
        trans_lines = simpleSplit(translated_text, "Helvetica", 10, 180)

        max_lines = max(len(orig_lines), len(trans_lines))

        # Adjust row height dynamically
        section_height = max_lines * 15  # Space for multiple lines

        # Check for page overflow
        if y_position - section_height - padding < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y_position = 750

            # Redraw headers on new page
            pdf.setFont("Helvetica", 10)
            pdf.drawString(100, y_position, "Original Text")
            pdf.drawString(300, y_position, "Translated Text")
            pdf.drawString(500, y_position, "Confidence Score")
            pdf.line(col_positions[0], y_position - 5, col_positions[-1], y_position - 5)
            y_position -= row_height
            pdf.setFont("Helvetica", 10)

        # **Add padding before starting new sentence**
        y_position -= padding

        # Draw table section for full sentence
        for i in range(max_lines):
            orig_text = orig_lines[i] if i < len(orig_lines) else ""
            trans_text = trans_lines[i] if i < len(trans_lines) else ""

            pdf.drawString(100, y_position, orig_text)
            pdf.drawString(300, y_position, trans_text)
            pdf.drawString(520, y_position, confidence if i == 0 else "")

            y_position -= 15  # Move down

        # **Draw Row Divider after full sentence**
        pdf.line(col_positions[0], y_position + 5, col_positions[-1], y_position + 5)

        # **Draw Column Dividers**
        for col in col_positions:
            pdf.line(col, y_position + section_height + padding, col, y_position + 5)

    pdf.save()
    buffer.seek(0)
    return buffer

# Button to trigger translation
if uploaded_file is not None:
    if st.button("Translate Document"):
        with st.spinner("Translating... Please wait"):
            # Send the file and target language to the backend API
            files = {"file": uploaded_file}
            data = {"target_lang": target_lang_code}  # Ensure lowercase formatting
            response = requests.post("http://127.0.0.1:5001/translate", files=files, data=data)

            if response.status_code == 200:
                translations = response.json()
                st.success("✅ Translation Complete!")

                # Display translations side-by-side
                st.markdown("### 🔍 Side-by-Side Translation with Confidence Scores")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### Original Text")
                with col2:
                    st.markdown(f"### Translated Text ({target_lang_name})")

                for translation in translations:
                    original_text = translation["original"]
                    translated_text = translation["translated"]
                    confidence = translation["confidence"]

                    # Display text in columns
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"{original_text}")
                    with col2:
                        with stylable_container(
                            key="tooltip-container",
                            css_styles="""
                                position: relative; display: inline-block; cursor: pointer;
                                border-bottom: 1px dotted black; padding: 3px;
                            """,
                        ):
                            st.markdown(f"{translated_text}")
                            st.caption(f"Confidence: {confidence}%")

                # Add download buttons after translation
                st.markdown("## 📥 Download Translated Document")

                if translations:
                    translated_pdf_bytes = create_translated_pdf(translations)  # Generate PDF first
                    comparison_pdf_bytes = create_comparison_pdf(translations)

                    col1, col2 = st.columns(2)

                    with col1:
                        st.download_button(
                            label="📄 Download Translated PDF",
                            data=translated_pdf_bytes,
                            file_name="translated_document.pdf",
                            mime="application/pdf"
                        )

                    with col2:
                        st.download_button(
                            label="📑 Download Comparison PDF",
                            data=comparison_pdf_bytes,
                            file_name="comparison_document.pdf",
                            mime="application/pdf"
                        )
            else:
                st.error("⚠️ Translation failed. Please check the backend logs.")
