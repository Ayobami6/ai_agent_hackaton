from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
# Use a pipeline as a high-level helper
from transformers import pipeline
# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-Guard-2-8B")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-Guard-2-8B")

messages = [
    {"role": "user", "content": "Who are you?"},
]
pipe = pipeline("text-generation", model="meta-llama/Meta-Llama-Guard-2-8B")
pipe(messages)
# Initialize Flask app
app = Flask(__name__)

# Load Meta-Llama-Guard-2-8B model from Hugging Face (replace with the correct model if needed)
model_name = "meta-llama/Meta-Llama-Guard-2-8B"  # Assuming this is the model you're using
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Ensure the model runs on a GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Helper function to calculate BMI
def calculate_bmi(height, weight):
    return round(weight / ((height / 100) ** 2), 2)

# Health and diet analysis based on user input
def get_user_info(data):
    user_data = {}

    # Get height and weight
    user_data['height'] = float(data.get("height"))
    user_data['weight'] = float(data.get("weight"))

    # Calculate BMI
    user_data['BMI'] = calculate_bmi(user_data['height'], user_data['weight'])

    # Get diet routine
    user_data['diet_routine'] = data.get("diet_routine")

    # Get fast food consumption
    user_data['fast_food_frequency'] = int(data.get("fast_food_frequency"))

    # Get workout routine
    user_data['workout_frequency'] = int(data.get("workout_frequency"))

    # Get food preferences
    user_data['food_preferences'] = data.get("food_preferences")

    # Get cuisine preferences
    user_data['preferred_cuisine'] = data.get("preferred_cuisine")

    return user_data

# Basic analysis
def analyze_data(user_data):
    analysis = {
        "Height": f"{user_data['height']} cm",
        "Weight": f"{user_data['weight']} kg",
        "BMI": user_data['BMI']
    }

    # Basic fast food habits
    if user_data['fast_food_frequency'] > 2:
        analysis['Fast food advice'] = "Consider reducing your fast food intake for better health."
    else:
        analysis['Fast food advice'] = "Your fast food intake is moderate."

    # Basic workout habits
    if user_data['workout_frequency'] < 3:
        analysis['Workout advice'] = "Try to work out at least 3 times a week for improved fitness."
    else:
        analysis['Workout advice'] = "Great job on your regular workout routine!"

    analysis['Preferred cuisine'] = f"You prefer {user_data['preferred_cuisine']} cuisine."
    analysis['Food preferences'] = f"You follow a {user_data['food_preferences']} diet."

    return analysis

# Function to generate response using Meta-Llama
def generate_response(user_input):
    inputs = tokenizer(user_input, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=150)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Define the chatbot endpoint
@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.json  # Get the user input as JSON

    # Validate the input data
    required_fields = ['height', 'weight', 'diet_routine', 'fast_food_frequency', 'workout_frequency', 'food_preferences', 'preferred_cuisine']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    # Get user info and generate health summary
    user_data = get_user_info(data)
    health_summary = analyze_data(user_data)

    # Optionally, generate a chatbot-style response (using Meta-Llama) for the health summary
    chatbot_response = generate_response(f"Health summary for a user with the following data: {health_summary}")

    return jsonify({
        "health_summary": health_summary,
        "chatbot_response": chatbot_response
    })

# Run the app
if __name__ == "__main__":
    app.run(host="10.0.0.1", port=8080)
