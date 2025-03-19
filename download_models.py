from transformers import MarianMTModel, MarianTokenizer

# Define the multi-to-multi model name
model_name = "Helsinki-NLP/opus-mt-tc-bible-big-mul-mul"
local_path = "./models/Helsinki-NLP/opus-mt-mul-mul"

# Download and save tokenizer and model locally
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

tokenizer.save_pretrained(local_path)
model.save_pretrained(local_path)

print(f"✅ Multi-to-Multi model downloaded and saved at: {local_path}")
