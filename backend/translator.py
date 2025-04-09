import torch
from transformers import MarianMTModel, MarianTokenizer
from langdetect import detect

# Load the model on GPU if available
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = "./models/Helsinki-NLP/opus-mt-mul-mul"

tokenizer = MarianTokenizer.from_pretrained(MODEL_PATH)
model = MarianMTModel.from_pretrained(MODEL_PATH).to(DEVICE)

# Function to detect the language
def detect_language(text):
    return detect(text)

# Function to translate text to the selected target language
def translate_text(text, target_lang="eng"):
    source_lang = detect_language(text)
    target_lang = target_lang.lower()

    # Prefixing with >>{target_lang}<< for MarianMT
    src_tgt_prefix = f">>{target_lang}<<"
    formatted_text = f"{src_tgt_prefix} {text}"

    # Tokenize and move tensors to the same device as model
    inputs = tokenizer(formatted_text, return_tensors="pt", padding=True, truncation=True).to(DEVICE)

    with torch.no_grad():
        outputs = model.generate(**inputs)

    translated = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    return translated, source_lang
