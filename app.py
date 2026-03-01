import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

app = Flask(__name__)
CORS(app)

@app.route('/yt-api', methods=['POST', 'OPTIONS'])
@app.route('/yt-api/', methods=['POST', 'OPTIONS'])
@app.route('/', methods=['GET'])
def fetch_transcript():
    if request.method == 'GET':
        return '✅ HazelNote YT Transcript API (official library) — Running free!', 200
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json(silent=True) or {}
    video_id = data.get('videoId', '').strip()

    if len(video_id) != 11:
        return jsonify({'error': 'Invalid videoId'}), 400

    try:
        # Try manual English first
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US', 'en-GB'])
        full_text = ' '.join([entry['text'] for entry in transcript])
        method = 'manual_en'
    except (NoTranscriptFound, TranscriptsDisabled):
        try:
            # Fallback to auto-generated (YouTube's own AI captions)
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            full_text = ' '.join([entry['text'] for entry in transcript])
            method = 'auto_generated'
        except Exception as e:
            return jsonify({'error': str(e), 'debug': {'method': 'failed'}}), 500
    except Exception as e:
        return jsonify({'error': str(e), 'debug': {'method': 'failed'}}), 500

    return jsonify({
        'transcript': full_text,
        'length': len(full_text),
        'debug': {
            'method': method,
            'lang': 'en',
            'is_translated': False
        }
    })

application = app
