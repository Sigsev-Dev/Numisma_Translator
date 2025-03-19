from sentence_transformers import SentenceTransformer, util

# Load a similarity model
similarity_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def calculate_confidence(original, translated):
    """Calculate confidence score based on semantic similarity."""
    score = util.pytorch_cos_sim(
        similarity_model.encode(original, convert_to_tensor=True),
        similarity_model.encode(translated, convert_to_tensor=True)
    )
    return round(score.item() * 100, 2)  # Convert to percentage
