from transformers import MarianTokenizer

# Define the model path
local_path = "models/Helsinki-NLP/opus-mt-mul-en"

# Load tokenizer from available files
tokenizer = MarianTokenizer.from_pretrained(local_path)

# Save tokenizer.json inside the model directory
tokenizer.save_pretrained(local_path)

print(f"✅ Tokenizer.json successfully generated at: {local_path}")
