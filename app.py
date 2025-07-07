

from flask import Flask, request, render_template, jsonify
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import re
# from azure.search.documents import SearchClient
# from azure.identity import DefaultAzureCredential

load_dotenv()

app = Flask(__name__)

# Azure OpenAI credentials
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = "2024-02-15-preview"
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# search_endpoint  = os.getenv("AZURE_SEARCH_ENDPOINT")
# search_index = os.getenv("AZURE_INDEX_NAME")

# Init client
client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=api_base,
)

# System prompt (replace with full Sophia prompt later if needed)
with open("sophia_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()
    
with open("sophia_grounding.txt", "r", encoding="utf-8") as f:
    GROUNDING_TEXT = f.read()
    
conversation_history = []
cumulative_trust_score = 0

def assess_trust_score(user_input):
    strategic_keywords = [
        "business case", "risk", "succession", "board", "KPI", 
        "commercial", "leadership", "capability", "ROI", "evidence"
    ]
    generic_keywords = ["solution", "synergy", "innovative", "cutting-edge", "leverage"]

    score = 0

    # Strategic keywords
    for word in strategic_keywords:
        if word.lower() in user_input.lower():
            score += 1

    # Salesy / generic buzzwords
    for word in generic_keywords:
        if word.lower() in user_input.lower():
            score -= 1

    # Bonus if it's a follow-up (you can improve with NLP later)
    if user_input.strip().endswith("?"):
        score += 1

    return score


# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    global cumulative_trust_score

    user_message = request.json.get("message")
    trust_boost = assess_trust_score(user_message)
    cumulative_trust_score += trust_boost

    print(f"[Debug] Message: {user_message}")
    print(f"[Debug] Trust boost: {trust_boost}, Cumulative score: {cumulative_trust_score}")

    conversation_history.append({"role": "user", "content": user_message})

    # Decide whether to include grounding text
    if cumulative_trust_score >= 3:
        system_prompt = SYSTEM_PROMPT + f"\n\nRelevant context (use only if relevant and earned):\n\"\"\"\n{GROUNDING_TEXT}\n\"\"\""
    else:
        system_prompt = SYSTEM_PROMPT

    # Build message history
    messages = [{"role": "system", "content": system_prompt}]
    messages += conversation_history[:-1]  # previous messages (optional)
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=messages
        )
        reply = response.choices[0].message.content
        cleaned_reply = re.sub(r'\[\^.*?\^]', '', reply)
        conversation_history.append({"role": "assistant", "content": cleaned_reply})
        return jsonify({"response": cleaned_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
