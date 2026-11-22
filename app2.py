
# Import Flask modules
from flask import Flask, render_template, request, Response

# Import YouTube Transcript API
from youtube_transcript_api import YouTubeTranscriptApi

# Import Gemini AI
from google import genai

# Import dotenv to read environment variables
from dotenv import load_dotenv

# Import required Python modules
import os
import re


# Load environment variables from .env file
load_dotenv()


# Create Flask application
app = Flask(__name__)


# Connect Gemini API using API key
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# Function to extract YouTube video ID
def extract_video_id(url):

    # Regex pattern for different YouTube URL formats
    pattern = (
        r"(?:youtube\.com/watch\?v=|youtu\.be/|"
        r"youtube\.com/embed/|youtube\.com/shorts/)"
        r"([\w-]{11})"
    )

    # Search for video ID
    match = re.search(pattern, url)

    # Return video ID if found
    if match:
        return match.group(1)

    return None


# Main route
@app.route("/", methods=["GET", "POST"])
def home():

    # Initialize variables
    summary = ""
    error = ""
    video_url = ""
    word_count = 0

    # Check whether form is submitted
    if request.method == "POST":

        # Get YouTube URL from HTML form
        video_url = request.form.get("video_url", "").strip()

        # Extract video ID
        video_id = extract_video_id(video_url)

        # Validate YouTube URL
        if not video_id:

            error = "Invalid YouTube URL! Please try again."

        else:

            try:

                # Fetch video transcript
                transcript = YouTubeTranscriptApi().fetch(video_id)

                # Convert transcript into plain text
                text = " ".join(
                    segment.text for segment in transcript
                )

                # Check transcript availability
                if not text.strip():
                    raise ValueError("Transcript is empty.")

                # Create prompt for Gemini AI
                prompt = f"""
                You are an expert YouTube video summarizer.

                Summarize the following video in simple English.

                Follow this format:

                1. Video Overview
                2. Detailed Summary
                3. Important Points
                4. Key Takeaways
                5. Conclusion

                Use bullet points wherever necessary.

                Transcript:
                {text}
                """

                # Generate summary using Gemini AI
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

                # Store generated summary
                summary = response.text or "No summary generated."

                # Calculate summary word count
                word_count = len(summary.split())

            except Exception as e:

                # Display error if something goes wrong
                error = f"Error: {str(e)}"

    # Render HTML template and send data
    return render_template(
        "index.html",
        summary=summary,
        error=error,
        video_url=video_url,
        word_count=word_count
    )


# Route for downloading summary
@app.route("/download", methods=["POST"])
def download():

    # Get summary from HTML form
    summary = request.form.get("summary", "")

    # Check if summary is available
    if not summary.strip():
        return "No summary available!", 400

    # Create downloadable text file
    return Response(
        summary,
        mimetype="text/plain",
        headers={
            "Content-Disposition":
            "attachment; filename=video_summary.txt"
        }
    )


# Run Flask application
if __name__ == "__main__":

    # Debug mode helps during development
    app.run(debug=True)
# Testing Git Stash