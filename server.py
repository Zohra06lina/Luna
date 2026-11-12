import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
CORS(app)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL = os.environ.get("MODEL", "gemini-2.5-flash")

SYSTEM = (
    "أنت لونا، مساعدة شخصية ودودة. تجاوبي بالدارجة الجزائرية البسيطة "
    "إلا إذا كتب المستخدم بلغة أخرى. الجواب قصير وواضح."
)


@app.post("/chat")
def chat():
    msg = (request.get_json(silent=True) or {}).get("message", "").strip()
    if not msg:
        return jsonify(error="الرسالة فارغة"), 400
    try:
        res = client.models.generate_content(
            model=MODEL,
            contents=msg,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM,
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )
        return jsonify(reply=res.text)
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.get("/")
def home():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
