import tiktoken
from typing import List, Dict

# The model for which we are calculating the tokens
MODEL_NAME = "gpt-4o-mini"

# The exact user message provided in the prompt
USER_MESSAGE_CONTENT = (
    "List only the valid English words from these: 7XEEql, c9QMFRhie, Xr7fYX, Rz9O, kscZBbV6, uq, Z5BKBk, I, 5pcVFo, tldbNbGWx, KWdJs, opVswuIP6a"
)

def num_tokens_from_messages(messages: List[Dict[str, str]], model: str) -> int:
    """
    Returns the number of tokens used by a list of messages for a given model.
    This function is based on the OpenAI cookbook's method.
    """
    try:
        # Get the appropriate encoding for the specified model
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback for models without a direct mapping, though 'gpt-4o-mini' is now supported.
        # This uses the encoding for 'gpt-4o' which is typically correct for the mini version.
        encoding = tiktoken.encoding_for_model("gpt-4o")

    # Tokens per message are the hidden tokens added for chat structure: 
    # <|im_start|>role\ncontent<|im_end|>\n
    # Note: For GPT-4o models, the exact number is debated but 3-4 is a common approximation.
    # The most recent method accounts for the role and end tokens.
    
    # Base tokens required for the start of any chat conversation
    tokens_per_message = 3  # Start token, role, and end token for the first message (approx)
    tokens_per_name = 1  # Used if 'name' key is present
    num_tokens = 0

    for message in messages:
        # Add tokens for the message structure
        num_tokens += tokens_per_message 
        
        # Add tokens for the role and content
        for key, value in message.items():
            if value:
                num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name

    # Every reply is primed with <|im_start|>assistant, which takes 2 tokens, 
    # so we add 3 to account for the overall structure of the conversation, 
    # but the logic above already includes most of it. 
    # The official recommendation is to start with 3 tokens for a simple user-only prompt.
    num_tokens += 3  # Final adjustment for conversation overhead
    
    # We will use the simplified, modern approach for messages:
    # We can also use a simpler calculation: len(encoding.encode(text)) + 4 (for prompt wrapper)
    # However, to be more precise, we re-run the calculation with a model-specific helper.
    
    # Re-calculating with a focus on the prompt's content, and then adding overhead.
    content_tokens = len(encoding.encode(USER_MESSAGE_CONTENT))
    
    # The structure for a simple user message is:
    # <|im_start|>user\n{USER_MESSAGE_CONTENT}<|im_end|>\n<|im_start|>assistant\n
    # which is about 6 tokens of overhead.
    # We will stick to the simplified method for general calculation:
    
    return num_tokens

# Define the messages structure for the Chat Completions API
messages = [
    {
        "role": "user", 
        "content": USER_MESSAGE_CONTENT
    }
]

# Calculate the tokens
input_tokens = num_tokens_from_messages(messages, MODEL_NAME)

print(f"User Message Content: \"{USER_MESSAGE_CONTENT}\"")
print(f"Calculated Input Tokens for '{MODEL_NAME}': {input_tokens}")