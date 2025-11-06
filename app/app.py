"""
Multilingual Text-to-Speech Translator - Streamlit Application
Main Streamlit UI for the text-to-speech translation system.
"""

import streamlit as st
import sys
import os
import hashlib
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
# Get the project root directory (parent of app directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)  # Load .env file if it exists

# Add parent directory to path to import services
sys.path.append(project_root)

from services.translation_service import TranslationService
from services.speech_service import SpeechService


# Page configuration
st.set_page_config(
    page_title="Multilingual TTS Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar
)

# Initialize services
@st.cache_resource
def get_translation_service():
    """Initialize and cache the translation service."""
    return TranslationService()

@st.cache_resource
def get_speech_service():
    """Initialize and cache the speech service."""
    return SpeechService(output_dir='output')

translation_service = get_translation_service()
speech_service = get_speech_service()


# Language options for dropdown
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


def main():
    """
    Main function that renders the Streamlit UI and handles user interactions.
    """
    # Custom CSS for better UI
    st.markdown("""
    <style>
    /* Main title styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* Subheader styling - cleaner look */
    h3 {
        color: #2c3e50;
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 15px;
        padding-bottom: 8px;
        border-bottom: 2px solid #e8e8e8;
    }
    
    /* Section containers */
    .section-container {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid #e0e0e0;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        border-radius: 4px;
        padding: 12px;
    }
    
    /* Success boxes */
    .stSuccess {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        border-radius: 4px;
        padding: 12px;
    }
    
    /* Warning boxes */
    .stWarning {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        border-radius: 4px;
        padding: 12px;
    }
    
    /* Error boxes */
    .stError {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        border-radius: 4px;
        padding: 12px;
    }
    
    /* Button styling - red/prominent */
    .stButton > button {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 12px 24px;
        transition: all 0.3s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(231, 76, 60, 0.3);
        background: linear-gradient(135deg, #c0392b 0%, #a93226 100%);
    }
    
    /* Card-like containers */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Radio button styling - cleaner */
    .stRadio > div {
        background-color: #ffffff;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-top: 5px;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 6px;
    }
    
    /* Slider styling */
    .stSlider > div > div {
        background-color: #f0f0f0;
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        border-radius: 6px;
        border: 1px solid #ddd;
    }
    
    /* Caption styling */
    .stCaption {
        color: #666;
        font-size: 0.85rem;
    }
    
    /* Horizontal rule styling */
    hr {
        margin: 25px 0;
        border: none;
        border-top: 2px solid #e8e8e8;
    }
    
    /* Clean spacing */
    .element-container {
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.title("🌐 Multilingual Text-to-Speech Translator")
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Input method selection
        st.subheader("📝 Input Text")
        input_method = st.radio(
            "Choose input method:",
            ["Type Text", "Upload Text File"],
            horizontal=True,
            help="Select whether to type text or upload a text file"
        )
        
        input_text = ""
        
        if input_method == "Type Text":
            # Text input area
            input_text = st.text_area(
                "Text Input",
                height=150,
                placeholder="Type or paste your text here in any language...\n\nExample: Hello, how are you?",
                help="Enter text in any language. The system will automatically detect it.",
                label_visibility="collapsed"
            )
        else:
            # File upload option
            uploaded_file = st.file_uploader(
                "Upload a file (.txt, .pdf, .doc, .docx)",
                type=['txt', 'pdf', 'doc', 'docx'],
                help="Upload a text file (.txt), PDF (.pdf), or Word document (.doc/.docx)"
            )
            
            if uploaded_file is not None:
                # Get file extension
                file_extension = uploaded_file.name.split('.')[-1].lower() if '.' in uploaded_file.name else ''
                
                # Read the file content based on file type
                try:
                    file_content = ""
                    
                    if file_extension == 'txt':
                        # Read text file
                        file_bytes = uploaded_file.read()
                        try:
                            file_content = file_bytes.decode('utf-8')
                        except UnicodeDecodeError:
                            file_content = file_bytes.decode('utf-8', errors='ignore')
                            st.warning("⚠️ File encoding may have issues. Some characters might not display correctly.")
                    
                    elif file_extension == 'pdf':
                        # Read PDF file
                        try:
                            from PyPDF2 import PdfReader
                            import io
                            # Reset file pointer and read as bytes
                            uploaded_file.seek(0)
                            pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
                            file_content = ""
                            for page in pdf_reader.pages:
                                page_text = page.extract_text()
                                if page_text:
                                    file_content += page_text + "\n"
                            if not file_content.strip():
                                st.warning("⚠️ PDF appears to be empty or text could not be extracted.")
                        except Exception as e:
                            st.error(f"❌ Error reading PDF: {str(e)}")
                            file_content = ""
                    
                    elif file_extension in ['doc', 'docx']:
                        # Read Word document
                        try:
                            from docx import Document
                            import io
                            # Reset file pointer and read as bytes
                            uploaded_file.seek(0)
                            doc = Document(io.BytesIO(uploaded_file.read()))
                            file_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                            if not file_content.strip():
                                st.warning("⚠️ Document appears to be empty.")
                        except Exception as e:
                            st.error(f"❌ Error reading Word document: {str(e)}")
                            file_content = ""
                    
                    else:
                        st.error(f"❌ Unsupported file type: {file_extension}")
                        file_content = ""
                    
                    input_text = file_content
                    
                    # Show file content preview
                    if file_content.strip():  # Only show preview if content exists
                        st.text_area(
                            "File Content Preview:",
                            value=file_content[:1000] + ("..." if len(file_content) > 1000 else ""),  # Limit preview to 1000 chars
                            height=150,
                            disabled=True,
                            help="Preview of the uploaded file content (first 1000 characters)"
                        )
                        if len(file_content) > 1000:
                            st.caption(f"📄 Total characters: {len(file_content)} (showing first 1000)")
                    else:
                        st.warning("⚠️ The uploaded file appears to be empty or could not be read.")
                        
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
                    input_text = ""
            else:
                st.info("👆 Please upload a file (.txt, .pdf, .doc, or .docx)")
    
    with col2:
        # Target language selection
        st.subheader("🎯 Target Language")
        target_language = st.selectbox(
            "Select Target Language",
            options=list(LANGUAGE_OPTIONS.keys()),
            index=0,  # Default to English
            help="Choose the language you want to translate and speak"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        
        # Voice Settings Section
        st.subheader("🎤 Voice Settings")
        
        # Gender selection
        voice_gender = st.radio(
            "Voice Gender",
            options=["Female", "Male"],
            index=0,  # Default to Female
            help="Select the gender of the voice",
            horizontal=True
        )
        
        # Age tone selection
        age_tone = st.selectbox(
            "Age Tone",
            options=["Child", "Adult", "Senior"],
            index=1,  # Default to Adult
            help="Select the age tone of the voice"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        
        # Speed Control Section
        st.subheader("⚡ Speed Control")
        speaking_speed = st.slider(
            "Adjust Speaking Speed",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="Control the playback speed (0.5x = slow, 1.0x = normal, 2.0x = fast)",
            format="%.1fx"
        )
        st.caption(f"Current speed: {speaking_speed:.1f}x")
    
    # Generate Speech button
    st.markdown("---")
    generate_button = st.button(
        "🎵 Generate Speech",
        type="primary",
        use_container_width=True,
        help="Click to translate and generate speech audio"
    )
    
    # Process when button is clicked
    if generate_button:
        # Validate input
        if not input_text or not input_text.strip():
            if input_method == "Type Text":
                st.error("❌ Please enter some text before generating speech!")
            else:
                st.error("❌ Please upload a text file with content before generating speech!")
            st.stop()
        
        # Show processing status
        with st.spinner("🔄 Processing your request..."):
            # Step 1: Auto-detect source language
            target_lang_code = LANGUAGE_OPTIONS[target_language]
            
            st.info("🔍 Detecting source language...")
            detected_lang = translation_service.detect_language(input_text)
            source_lang_code = detected_lang['code']
            source_lang_name = detected_lang['name']
            
            # Show detection result (without confidence score)
            st.success(f"✅ Detected Language: **{source_lang_name}** ({source_lang_code})")
            
            # Step 2: Translate text (only if source != target)
            if source_lang_code == target_lang_code:
                st.info("ℹ️ Source and target languages are the same. Skipping translation.")
                translation_result = {
                    'translated_text': input_text,
                    'source_lang': source_lang_code,
                    'target_lang': target_lang_code,
                    'original_text': input_text
                }
            else:
                st.info(f"🔄 Translating from {source_lang_name} to {target_language}...")
                translation_result = translation_service.translate_text(
                    input_text, 
                    target_lang_code,
                    source_lang_code=source_lang_code
                )
            
            # Step 3: Generate speech with unique filename
            st.info("🎵 Converting to speech...")
            
            # Create hash of translated text + target language + voice settings for deduplication
            translated_text = translation_result['translated_text']
            # Include voice settings in hash for proper deduplication
            settings_hash = f"{voice_gender}_{age_tone}_{speaking_speed:.1f}"
            content_hash = hashlib.md5(f"{translated_text}_{target_lang_code}_{settings_hash}".encode()).hexdigest()[:8]
            
            # Use language name (lowercase) instead of code
            target_lang_name = target_language.lower()
            
            # Get voice based on gender and age tone
            selected_voice = speech_service.get_voice_by_gender_and_age(voice_gender, age_tone)
            
            # Check if a file with the same hash already exists (same text + language + settings)
            # Search for existing files with the same hash in the filename
            output_dir = speech_service.output_dir
            existing_file = None
            if os.path.exists(output_dir):
                for file in os.listdir(output_dir):
                    if file.endswith('.mp3') and content_hash in file and target_lang_name in file:
                        existing_file = os.path.join(output_dir, file)
                        break
            
            if existing_file and os.path.exists(existing_file):
                # File already exists, reuse it
                st.info("♻️ Using existing audio file (same text, language, and settings)")
                speech_result = {
                    'file_path': existing_file,
                    'filename': os.path.basename(existing_file),
                    'success': True,
                    'message': f'Reusing existing audio file: {os.path.basename(existing_file)}',
                    'tts_engine': 'existing',
                    'voice_used': selected_voice,
                    'speed': speaking_speed
                }
            else:
                # Generate new filename with timestamp, settings, and hash
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                speed_str = f"speed{speaking_speed:.1f}".replace('.', 'p')
                filename = f"speech_{target_lang_name}_{voice_gender.lower()}_{age_tone.lower()}_{selected_voice}_{speed_str}_{timestamp}_{content_hash}.mp3"
                
                # Generate new audio file
                speech_result = speech_service.text_to_speech(
                    text=translated_text,
                    lang_code=target_lang_code,
                    filename=filename,
                    voice=selected_voice,
                    use_openai_preference=True,
                    speed=speaking_speed
                )
        
        # Display results
        st.markdown("---")
        st.subheader("📊 Results")
        
        # Create columns for results display
        result_col1, result_col2 = st.columns(2)
        
        with result_col1:
            st.markdown("### 📝 Translation Details")
            st.markdown(f"**Source Language:** {source_lang_name} ({source_lang_code})")
            st.markdown(f"**Target Language:** {target_language} ({target_lang_code})")
            st.markdown(f"**Original Text:**")
            st.info(input_text)
            st.markdown(f"**Translated Text:**")
            st.success(translation_result['translated_text'])
        
        with result_col2:
            st.markdown("### 🎵 Audio Output")
            if speech_result['success']:
                st.success("✅ Audio generated successfully!")
                
                # Display voice settings used
                voice_info = speech_result.get('voice_used', 'unknown')
                speed_info = speech_result.get('speed', 1.0)
                engine_info = speech_result.get('tts_engine', 'unknown')
                
                # Get gender and age from voice
                gender_display = voice_gender
                age_display = age_tone
                
                # Quality indicator
                quality = "HD Quality" if engine_info == 'openai' else "Standard Quality"
                
                st.info(f"**{gender_display}** • **{age_display} tone** • Speed: **{speed_info:.1f}x** • {quality} • TTS Engine: **{engine_info.upper()}**")
                
                # Display audio player
                audio_file = open(speech_result['file_path'], 'rb')
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3', start_time=0)
                
                # Download button
                st.download_button(
                    label="📥 Download Audio (MP3)",
                    data=audio_bytes,
                    file_name=speech_result['filename'],
                    mime="audio/mpeg",
                    use_container_width=True
                )
                
                # File path info
                st.caption(f"File: `{speech_result['filename']}`")
            else:
                st.error(f"❌ {speech_result['message']}")


if __name__ == "__main__":
    main()

