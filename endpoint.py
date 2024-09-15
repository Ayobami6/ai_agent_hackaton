from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import transformers
# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-Guard-2-8B")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-Guard-2-8B")
# Initialize Flask app
app = Flask(__name__)



# Load Llama model from Hugging Face (or another causal LM model)
# Here, we load it once and use it throughout the interaction.
model_name = "meta-llama/Meta-Llama-Guard-2-8B"  
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Ensure the model runs on a GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

# Helper function to generate chatbot response using the model
def generate_response(user_input):
    # Encode the input and generate a response using the Llama model
    inputs = tokenizer(user_input, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=150)
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Define the chatbot endpoint
@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.json  # Get the user input as JSON
    
    # Ensure the request contains the required input
    if 'user_input' not in data:
        return jsonify({"error": "user_input is required"}), 400
    
    user_input = data['user_input']
    
    # Generate the chatbot response
    chatbot_response = generate_response(user_input)
    
    # Return the response as JSON
    return jsonify({"response": chatbot_response})

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
