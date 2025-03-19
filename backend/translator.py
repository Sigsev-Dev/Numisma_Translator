from transformers import MarianMTModel, MarianTokenizer
from langdetect import detect

# Load the multi-to-multi model once
MODEL_PATH = "./models/Helsinki-NLP/opus-mt-tc-bible-big-mul-mul"
tokenizer = MarianTokenizer.from_pretrained(MODEL_PATH)
model = MarianMTModel.from_pretrained(MODEL_PATH)

# Function to detect the language
def detect_language(text):
    """Detect the language of the input text."""
    return detect(text)

# Function to translate text from detected language to target language
def translate_text(text, target_lang="en"):
    """Translate text from detected language to the target language."""
    source_lang = detect_language(text)
    
    # Ensure target language is lowercase
    target_lang = target_lang.lower()

    # Prepare text with language prefix
    src_tgt_prefix = f">>{target_lang}<<"  # MarianMT models use special tokens like ">>fr<<"
    formatted_text = f"{src_tgt_prefix} {text}"

    # Tokenize and translate
    inputs = tokenizer(formatted_text, return_tensors="pt", padding=True, truncation=True)
    translated = model.generate(**inputs)

    return tokenizer.batch_decode(translated, skip_special_tokens=True)[0], source_lang
