from transformers import MarianMTModel, MarianTokenizer
from langdetect import detect

# Load the multi-to-multi model once
MODEL_PATH = "./models/Helsinki-NLP/opus-mt-mul-mul"
tokenizer = MarianTokenizer.from_pretrained(MODEL_PATH)
model = MarianMTModel.from_pretrained(MODEL_PATH)

# Function to detect the language
def detect_language(text):
    """Detect the language of the input text."""
    return detect(text)

# Function to translate text to the selected target language
def translate_text(text, target_lang="eng"):
    """Translate text from detected language to the target language."""
    source_lang = detect_language(text)
    
    # Ensure target language is a valid model token
    target_lang = target_lang.lower()

    # Prepare text with language prefix
    src_tgt_prefix = f">>{target_lang}<<"  # MarianMT models require ">>fr<<" for French
    formatted_text = f"{src_tgt_prefix} {text}"

    # Tokenize and translate
    inputs = tokenizer(formatted_text, return_tensors="pt", padding=True, truncation=True)
    translated = model.generate(**inputs)

    return tokenizer.batch_decode(translated, skip_special_tokens=True)[0], source_lang
