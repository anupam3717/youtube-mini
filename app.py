from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai
from dotenv import load_dotenv
import os
import re

load_dotenv()
app = Flask(__name__)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def home():
    summary = ""

    if request.method == "POST":
        url = request.form["video_url"]
        video_id = re.search(r"(?:v=|youtu\.be/)([\w-]{11})", url).group(1)

        transcript = YouTubeTranscriptApi().fetch(video_id)
        text = " ".join(s.text for s in transcript)

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Summarize this video:\n" + text
        )

        summary = response.text

    return render_template("index.html", summary=summary)

if __name__ == "__main__":
    app.run(debug=True)