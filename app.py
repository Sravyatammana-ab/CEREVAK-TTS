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
import base64
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Load environment variables
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

from services.translation_service import TranslationService
from services.speech_service import SpeechService
from services.pitch_service import apply_pitch
from services.azure_tts_service import (
    AZURE_VOICES,
    get_available_genders,
    get_voice_for_gender,
    synthesize_speech,
)

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

# Language configuration aligned with Azure Neural voices
LANGUAGE_CONFIG = {
    'as': {'name': 'Assamese', 'voices': AZURE_VOICES['Assamese']},
    'bn': {'name': 'Bengali', 'voices': AZURE_VOICES['Bengali']},
    'en': {'name': 'English (India)', 'voices': AZURE_VOICES['English (India)']},
    'gu': {'name': 'Gujarati', 'voices': AZURE_VOICES['Gujarati']},
    'hi': {'name': 'Hindi', 'voices': AZURE_VOICES['Hindi']},
    'kn': {'name': 'Kannada', 'voices': AZURE_VOICES['Kannada']},
    'ml': {'name': 'Malayalam', 'voices': AZURE_VOICES['Malayalam']},
    'mr': {'name': 'Marathi', 'voices': AZURE_VOICES['Marathi']},
    'or': {'name': 'Odia', 'voices': AZURE_VOICES['Odia']},
    'pa': {'name': 'Punjabi', 'voices': AZURE_VOICES['Punjabi']},
    'ta': {'name': 'Tamil', 'voices': AZURE_VOICES['Tamil']},
    'te': {'name': 'Telugu', 'voices': AZURE_VOICES['Telugu']},
    'ur': {'name': 'Urdu', 'voices': AZURE_VOICES['Urdu']},
}

LANGUAGE_CODE_TO_NAME = {code: config['name'] for code, config in LANGUAGE_CONFIG.items()}


def _slugify(value: str) -> str:
    normalized = []
    for ch in value.lower():
        if ch.isalnum():
            normalized.append(ch)
        elif ch in {' ', '-', '_'}:
            normalized.append('-')
    slug = ''.join(normalized).strip('-')
    while '--' in slug:
        slug = slug.replace('--', '-')
    return slug or 'default'


@app.route('/api/translate-and-speak', methods=['POST'])
def translate_and_speak():
    """
    API endpoint that handles text translation and TTS conversion.
    Expected JSON payload:
    {
        "text": "input text",
        "target_lang": "te",
        "voice_gender": "Male",
        "age_tone": "Adult",
        "tts_engine": "piper"
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
        requested_engine = data.get('tts_engine', 'azure')
        raw_rate = data.get('rate', 0)
        raw_pitch = data.get('pitch', 0)

        try:
            pitch_change = int(raw_pitch)
        except (TypeError, ValueError):
            pitch_change = 0

        try:
            rate_change = int(raw_rate)
        except (TypeError, ValueError):
            rate_change = 0

        if requested_engine:
            requested_engine = requested_engine.strip().lower()
        else:
            requested_engine = 'azure'
        
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
        target_lang_details = LANGUAGE_CONFIG.get(target_lang)
        if requested_engine == 'azure':
            if target_lang_details is None:
                return jsonify({'error': f"Unsupported target language '{target_lang}' for Azure TTS."}), 400

            voices = target_lang_details.get('voices') or {}
            available_genders = get_available_genders(target_lang_details['name'])

            pitch_change = max(-3, min(3, pitch_change))
            rate_change = max(-50, min(50, rate_change))

            pitch_ssml = "default" if pitch_change == 0 else f"{pitch_change:+d}st"
            rate_ssml = "default" if rate_change == 0 else f"{rate_change:+d}%"

            try:
                selected_voice = get_voice_for_gender(
                    target_lang_details['name'],
                    voice_gender,
                )
            except KeyError:
                # Fall back to first configured voice if mapping is missing.
                selected_voice = next(iter(voices.values())) if voices else None

            if not selected_voice:
                return jsonify({'error': f"No Azure voices configured for '{target_lang_details['name']}'."}), 400

            try:
                audio_bytes = synthesize_speech(
                    text=translated_text,
                    voice=selected_voice,
                    pitch=pitch_ssml,
                    rate=rate_ssml,
                )
            except Exception as exc:
                return jsonify({'error': f'Azure speech synthesis failed: {exc}'}), 500

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            content_hash = hashlib.md5(f"{translated_text}_{target_lang}_{pitch_ssml}_{rate_ssml}".encode()).hexdigest()[:8]
            filename = f"speech_{_slugify(target_lang_details['name'])}_{timestamp}_{content_hash}.mp3"
            file_path = os.path.join('output', filename)

            try:
                with open(file_path, 'wb') as file_handle:
                    file_handle.write(audio_bytes)
            except Exception as exc:
                return jsonify({'error': f'Failed to persist audio: {exc}'}), 500

            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

            return jsonify({
                'success': True,
                'source_lang': source_lang_code,
                'source_lang_name': source_lang_name,
                'target_lang': target_lang,
                'target_lang_name': target_lang_details['name'],
                'translated_text': translated_text,
                'audio_url': f'/api/audio/{filename}',
                'filename': filename,
                'tts_engine': 'azure',
                'audio_base64': audio_base64,
                'normalized_text': translated_text,
                'voice_name': selected_voice,
                'available_genders': list(available_genders.keys()),
                'pitch': pitch_ssml,
                'rate': rate_ssml,
                'message': 'Translation and speech generation successful!'
            })

        # Fallback to legacy providers for non-Azure engines
        tts_engine = requested_engine
        provider = speech_service.get_provider(tts_engine)
        if provider is None:
            return jsonify({
                'error': f"Unknown TTS engine '{tts_engine}'. Available options: {list(speech_service.providers.keys())}"
            }), 400

        target_lang_name = LANGUAGE_CODE_TO_NAME.get(target_lang, target_lang.upper())
        normalized_pitch = max(-3, min(3, pitch_change))
        provider_pitch = str(normalized_pitch) if normalized_pitch != 0 else None
        selected_voice = speech_service.get_voice_by_gender_and_age(voice_gender, age_tone)

        # Create hash for deduplication
        settings_hash = f"{voice_gender}_{age_tone}_{tts_engine}_{selected_voice}"
        content_hash = hashlib.md5(f"{translated_text}_{target_lang}_{settings_hash}".encode()).hexdigest()[:8]

        # Generate unique filename
        target_lang_name_lower = target_lang_name.lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        gender_slug = _slugify(voice_gender)
        age_slug = _slugify(age_tone)
        engine_slug = _slugify(tts_engine)
        voice_slug = _slugify(selected_voice)
        extension = getattr(provider, 'output_extension', 'mp3')
        filename = (
            f"speech_{target_lang_name_lower}_{engine_slug}_{gender_slug}_{age_slug}_{voice_slug}_{timestamp}_{content_hash}.{extension}"
        )

        # Generate audio file
        speech_result = speech_service.synthesize(
            text=translated_text,
            lang_code=target_lang,
            filename=filename,
            tts_engine=tts_engine,
            voice=selected_voice,
            gender=voice_gender,
            rate=raw_rate,
            pitch=provider_pitch
        )

        if speech_result['success']:
            final_file_path = speech_result.get('file_path')
            final_filename = speech_result.get('filename')
            final_audio_base64 = speech_result.get('audio_base64')

            if pitch_change != 0 and final_file_path:
                try:
                    processed_path = apply_pitch(final_file_path, pitch_change)
                    final_file_path = processed_path
                    final_filename = os.path.basename(processed_path)
                    with open(processed_path, 'rb') as processed_file:
                        processed_bytes = processed_file.read()
                    final_audio_base64 = base64.b64encode(processed_bytes).decode('utf-8')
                except Exception as exc:
                    return jsonify({'error': f'Pitch adjustment failed: {exc}'}), 500

            return jsonify({
                'success': True,
                'source_lang': source_lang_code,
                'source_lang_name': source_lang_name,
                'target_lang': target_lang,
                'target_lang_name': target_lang_name,
                'translated_text': translated_text,
                'audio_url': f'/api/audio/{final_filename}',
                'filename': final_filename,
                'tts_engine': tts_engine,
                'audio_base64': final_audio_base64,
                'normalized_text': speech_result.get('normalized_text', translated_text),
                'pitch_adjustment': pitch_change,
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
    return jsonify({
        code: {
            'code': code,
            'name': config['name'],
            'voices': config.get('voices', {}),
            'available_genders': list(
                gender for gender, voice_name in (config.get('voices') or {}).items() if voice_name
            ),
        }
        for code, config in LANGUAGE_CONFIG.items()
    })


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


