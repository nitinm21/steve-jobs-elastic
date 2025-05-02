import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
import openai
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from elevenlabs import stream

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

es_client = Elasticsearch(
    "https://4a8d0a9b7eac47aa9f1e8e412002877b.us-central1.gcp.cloud.es.io:443",
    api_key=os.environ["ES_API_KEY"]
)

openai.api_key = os.environ["OPENAI_API_KEY"]
# ElevenLabs client with the API key
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# voice settings for stability and similarity
voice_settings = VoiceSettings(
    stability=0.05,  # Adjust stability (0.0 to 1.0)
    similarity_boost=0.95  # Adjust similarity boost (0.0 to 1.0)
)

index_source_fields = {
    "search-allaboutstevejobs.com": [
        "body_content"
    ]
}

def get_elasticsearch_results(query):
    es_query = {
        "retriever": {
            "standard": {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "body_content",
                            "title"
                        ]
                    }
                }
            }
        },
        "size": 3
    }
    result = es_client.search(index="search-allaboutstevejobs.com", body=es_query)
    return result["hits"]["hits"]

def create_openai_prompt(results):
    context = ""
    for hit in results:
        inner_hit_path = f"{hit['_index']}.{index_source_fields.get(hit['_index'])[0]}"
        if 'inner_hits' in hit and inner_hit_path in hit['inner_hits']:
            context += '\n --- \n'.join(inner_hit['_source']['text'] for inner_hit in hit['inner_hits'][inner_hit_path]['hits']['hits'])
        else:
            source_field = index_source_fields.get(hit["_index"])[0]
            hit_context = hit["_source"][source_field]
            context += f"{hit_context}\n"
    prompt = f"""
  Instructions:
  
You are Steve Jobs, speaking to someone who admires your work and wants to have a meaningful conversation with you. This is a two-way voice interaction—no typing involved—so your responses should feel natural, thoughtful, and conversational. Listen to the person’s question carefully, and respond as if you’re having an engaging, real-time chat over coffee. Your tone should reflect your well-known charisma, vision, and directness. Feel free to draw on your life experiences, philosophies, and innovations as if they were part of your lived memories. Ensure your responses are succinct yet impactful, sparking curiosity and making the person feel inspired. Remember, this is a back-and-forth dialogue, so leave room for them to continue the conversation.

Answer it just like how Steve Jobs would. Keep your responses short and concise.
  
  
  
  """
    return prompt

def generate_openai_completion(user_prompt, question):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": user_prompt},
            {"role": "user", "content": question},
        ],
        max_tokens=3000
    )
    return response.choices[0].message.content

@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        # Parse JSON data from the request
        data = request.get_json()
        question = data.get("question")
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        # Get results from Elasticsearch
        elasticsearch_results = get_elasticsearch_results(question)
        
        # Create prompt and generate answer using OpenAI
        context_prompt = create_openai_prompt(elasticsearch_results)
        answer = generate_openai_completion(context_prompt, question)
        # Convert the answer to speech using ElevenLabs
        audio_stream = client.text_to_speech.convert_as_stream(
            text=answer,
            voice_id="CwhRBWXzGAHq8TQ4Fs17",
            model_id="eleven_flash_v2",
            voice_settings=voice_settings
        )
        stream(audio_stream)
        
        return jsonify({"answer": answer})
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
