"""
Flask Web Application for Multilingual Text-to-Speech Translation
This provides a web interface for the TTS translation functionality.
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import sys
from datetime import datetime
import hashlib
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Load environment variables
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

from services.translation_service import TranslationService
from services.speech_service import SpeechService

# Check if React build exists
build_path = os.path.join('frontend', 'build')
if not os.path.exists(build_path):
    print("⚠️ WARNING: React build folder not found!")
    print("   Please run 'npm run build' in the frontend directory first.")
    print("   For now, Flask will serve API endpoints only.")

app = Flask(__name__, static_folder=build_path if os.path.exists(build_path) else None, static_url_path='')
CORS(app)  # Enable CORS for frontend-backend communication

# Ensure directories exist
os.makedirs('static', exist_ok=True)
os.makedirs('output', exist_ok=True)

# Initialize services
translation_service = TranslationService()
speech_service = SpeechService(output_dir='output')

# Language options mapping
LANGUAGE_OPTIONS = {
    'English': 'en',
    'Hindi': 'hi',
    'Urdu': 'ur',
    'Assamese': 'as',
    'Bengali': 'bn',
    'Gujarati': 'gu',
    'Kannada': 'kn',
    'Malayalam': 'ml',
    'Marathi': 'mr',
    'Odia': 'or',
    'Punjabi': 'pa',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Russian': 'ru',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Chinese': 'zh',
    'Arabic': 'ar',
    'Nepali': 'ne',
    'Sinhala': 'si'
}

# Reverse mapping for API
LANGUAGE_CODE_TO_NAME = {v: k for k, v in LANGUAGE_OPTIONS.items()}


@app.route('/api/translate-and-speak', methods=['POST'])
def translate_and_speak():
    """
    API endpoint that handles text translation and TTS conversion.
    Expected JSON payload:
    {
        "text": "input text",
        "target_lang": "te",
        "voice_gender": "Male",
        "age_tone": "Adult"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        input_text = data.get('text', '').strip()
        target_lang = data.get('target_lang', '').strip().lower()
        voice_gender = data.get('voice_gender', 'Male')
        age_tone = data.get('age_tone', 'Adult')
        
        if not input_text:
            return jsonify({'error': 'No text provided'}), 400
        
        if not target_lang:
            return jsonify({'error': 'No target language provided'}), 400
        
        # Detect source language
        detected_lang = translation_service.detect_language(input_text)
        source_lang_code = detected_lang['code']
        source_lang_name = detected_lang['name']
        
        # Translate text (only if source != target)
        if source_lang_code == target_lang:
            translation_result = {
                'translated_text': input_text,
                'source_lang': source_lang_code,
                'target_lang': target_lang,
                'original_text': input_text
            }
        else:
            translation_result = translation_service.translate_text(
                input_text,
                target_lang,
                source_lang_code=source_lang_code
            )
        
        translated_text = translation_result['translated_text']
        target_lang_name = LANGUAGE_CODE_TO_NAME.get(target_lang, target_lang.upper())
        
        # Get voice based on gender and age tone
        selected_voice = speech_service.get_voice_by_gender_and_age(voice_gender, age_tone)
        
        # Create hash for deduplication
        settings_hash = f"{voice_gender}_{age_tone}"
        content_hash = hashlib.md5(f"{translated_text}_{target_lang}_{settings_hash}".encode()).hexdigest()[:8]
        
        # Generate unique filename
        target_lang_name_lower = target_lang_name.lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"speech_{target_lang_name_lower}_{voice_gender.lower()}_{age_tone.lower()}_{selected_voice}_{timestamp}_{content_hash}.mp3"
        
        # Generate audio file
        speech_result = speech_service.text_to_speech(
            text=translated_text,
            lang_code=target_lang,
            filename=filename,
            voice=selected_voice,
            use_openai_preference=True
        )
        
        if speech_result['success']:
            return jsonify({
                'success': True,
                'source_lang': source_lang_code,
                'source_lang_name': source_lang_name,
                'target_lang': target_lang,
                'target_lang_name': target_lang_name,
                'translated_text': translated_text,
                'audio_url': f'/api/audio/{filename}',
                'filename': filename,
                'message': 'Translation and speech generation successful!'
            })
        else:
            return jsonify({'error': speech_result.get('message', 'Failed to generate audio file')}), 500
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/audio/<filename>', methods=['GET'])
def get_audio(filename):
    """Serve the generated audio file for playback."""
    audio_path = os.path.join('output', filename)
    if os.path.exists(audio_path):
        return send_file(
            audio_path, 
            mimetype='audio/mpeg',
            as_attachment=False,  # For audio player - stream inline
            download_name=filename
        )
    else:
        return jsonify({'error': 'Audio file not found', 'path': audio_path}), 404


@app.route('/api/download/<filename>', methods=['GET'])
def download_audio(filename):
    """Download the generated audio file."""
    audio_path = os.path.join('output', filename)
    if os.path.exists(audio_path):
        return send_file(
            audio_path, 
            mimetype='audio/mpeg',
            as_attachment=True,  # Force download dialog
            download_name=filename
        )
    else:
        return jsonify({'error': 'Audio file not found', 'path': audio_path}), 404


@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get list of supported languages."""
    return jsonify({v: k for k, v in LANGUAGE_OPTIONS.items()})


# Serve React static files - must be last route and exclude API routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Serve React static files."""
    # Don't serve React for API routes
    if path.startswith('api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    
    # Check if build folder exists
    if not app.static_folder or not os.path.exists(app.static_folder):
        return jsonify({
            'error': 'Frontend not built',
            'message': 'Please run "npm run build" in the frontend directory first.',
            'instructions': '1. cd frontend\n2. npm run build\n3. Restart Flask server'
        }), 503
    
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            return jsonify({
                'error': 'Frontend index.html not found',
                'message': 'Please run "npm run build" in the frontend directory.'
            }), 503


if __name__ == '__main__':
    print("Starting Flask server...")
    print("Open your browser and navigate to: http://localhost:5000")
    print("Note: Make sure to build the React frontend first with 'npm run build' in the frontend directory")
    app.run(debug=True, host='0.0.0.0', port=5000)


