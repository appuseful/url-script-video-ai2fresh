from flask import Flask, request, jsonify, send_file
import requests
from bs4 import BeautifulSoup
from gtts import gTTS
from moviepy.editor import *
import os
import uuid

app = Flask(__name__)

@app.route("/api/extract-script", methods=["POST"])
def extract_script():
    data = request.get_json()
    url = data.get("url")
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = "\n".join(p.get_text() for p in paragraphs if len(p.get_text()) > 40)
        return jsonify({ "text": text[:3000] })
    except Exception as e:
        return jsonify({ "error": str(e) }), 500

@app.route("/api/script-to-video", methods=["POST"])
def script_to_video():
    data = request.get_json()
    text = data.get("text")
    try:
        filename = f"video_{uuid.uuid4().hex}.mp4"
        tts = gTTS(text)
        audio_path = f"{filename}.mp3"
        tts.save(audio_path)

        clip = TextClip(text[:200], fontsize=24, color='white', size=(720, 480), method='caption', bg_color='black', align='center', font='Arial')
        clip = clip.set_duration(AudioFileClip(audio_path).duration)
        clip = clip.set_audio(AudioFileClip(audio_path))
        clip.write_videofile(filename, fps=24)

        return jsonify({ "videoUrl": f"/video/{filename}" })
    except Exception as e:
        return jsonify({ "error": str(e) }), 500

@app.route("/video/<path:filename>")
def serve_video(filename):
    return send_file(filename, mimetype='video/mp4')

@app.route("/")
def home():
    return send_file("index.html")

if __name__ == "__main__":
    app.run(debug=True)
