import requests
import base64
import numpy as np
from io import BytesIO
from PIL import Image

# Jina AI API configuration
JINA_API_URL = "https://api.jina.ai/v1/embeddings"
JINA_API_KEY = "jina_c80d1ad754e04fb89f6a9cc6c7ddbb4bh5_xo0EX_1F90LmkgUxgpRNSjRHJ"  # Replace with your actual API key

# Text description in Swahili
text_description = "Mbinu za upimaji wa ubora wa maji"

# Path to your image file
image_path = "week 4/multimodal_embedding.py"  # Replace with your actual image path

def encode_image_to_base64(image_path):
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_jina_embeddings(text_input=None, image_base64=None):
    """
    Get embeddings from Jina AI CLIP V2 model
    
    Args:
        text_input: Text string (optional)
        image_base64: Base64 encoded image (optional)
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {JINA_API_KEY}"
    }
    
    # Build input array with text and/or image objects
    input_array = []
    if text_input:
        input_array.append({"text": text_input})
    if image_base64:
        input_array.append({"image": image_base64})
    
    payload = {
        "model": "jina-clip-v2",
        "input": input_array
    }
    
    response = requests.post(JINA_API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

def calculate_cosine_similarity(embedding1, embedding2):
    """
    Calculate dot product (cosine similarity) between two normalized vectors
    Since vectors are already normalized, dot product = cosine similarity
    """
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    # Dot product for normalized vectors
    similarity = np.dot(vec1, vec2)
    
    return similarity

def main():
    print("AIrtGallery Similarity Calculator")
    print("=" * 50)
    
    # Step 1: Encode image to base64
    print("\n1. Encoding image to base64...")
    image_base64 = encode_image_to_base64(image_path)
    print("   ✓ Image encoded")
    
    # Step 2: Get embeddings for both text and image in single request
    print("\n2. Getting embeddings from Jina AI CLIP V2...")
    print(f"   Text: '{text_description}'")
    
    response = get_jina_embeddings(text_input=text_description, image_base64=image_base64)
    
    # Extract embeddings (first is text, second is image based on order)
    text_embedding = response['data'][0]['embedding']
    image_embedding = response['data'][1]['embedding']
    
    print(f"   ✓ Text embedding received (dimension: {len(text_embedding)})")
    print(f"   ✓ Image embedding received (dimension: {len(image_embedding)})")
    
    # Step 3: Calculate similarity
    print("\n3. Calculating cosine similarity...")
    similarity_score = calculate_cosine_similarity(text_embedding, image_embedding)
    
    # Results
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"Text: {text_description}")
    print(f"Model: jina-clip-v2")
    print(f"Embedding dimensions: {len(text_embedding)}")
    print(f"\nSimilarity Score (Dot Product): {similarity_score:.6f}")
    print("=" * 50)
    
    # Interpretation
    print("\nInterpretation:")
    if similarity_score > 0.5:
        print("✓ High similarity - Text describes the image well")
    elif similarity_score > 0.3:
        print("~ Moderate similarity - Some relevance")
    else:
        print("✗ Low similarity - Text doesn't match the image well")
    
    return similarity_score

if __name__ == "__main__":
    try:
        score = main()
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print("\nMake sure to:")
        print("1. Replace 'your-jina-api-key-here' with your actual Jina AI API key")
        print("2. Update 'image_path' to point to your fractal image")
        print("3. Install required packages: pip install requests numpy pillow")