from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return '✅ HazelNote YouTube Transcript API (v4 - Auto-Translate) Running!', 200

@app.route('/yt-api', methods=['POST', 'OPTIONS'])  # Keep your old route for compatibility
@app.route('/', methods=['POST', 'OPTIONS'])
def fetch_transcript():
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json(silent=True) or {}
    video_id = data.get('videoId', '').strip()

    if len(video_id) != 11:
        return jsonify({'error': 'videoId must be exactly 11 characters'}), 400

    try:
        # === GEMINI SUGGESTION IMPLEMENTED + IMPROVED ===
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        try:
            # Prefer native English (manual or auto-generated)
            transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
            method = 'english_native'
        except:
            # No English → take the first available transcript and translate to English
            transcript = list(transcript_list)[0].translate('en')
            method = 'auto_translated_to_english'

        # Fetch the actual text
        full_text = ' '.join([entry['text'] for entry in transcript.fetch()])
        full_text = ' '.join(full_text.split())  # clean extra spaces

        return jsonify({
            'transcript': full_text,
            'length': len(full_text),
            'debug': {
                'method': method,
                'lang': transcript.language_code,
                'is_translated': method == 'auto_translated_to_english'
            }
        })

    except (NoTranscriptFound, TranscriptsDisabled):
        return jsonify({'error': 'No transcript available for this video'}), 404
    except Exception as e:
        return jsonify({
            'error': str(e),
            'debug': {'method': 'failed'}
        }), 500

# REMOVE THIS BLOCK — Render uses Gunicorn, not app.run()
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)
