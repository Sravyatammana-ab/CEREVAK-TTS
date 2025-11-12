"""
Multilingual Text-to-Speech Translator - Streamlit Application
Main Streamlit UI for the text-to-speech translation system.
"""

import streamlit as st
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# Get the project root directory (parent of app directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)  # Load .env file if it exists

# Add parent directory to path to import services
sys.path.append(project_root)

from services.translation_service import TranslationService
from services.azure_tts_service import AZURE_VOICES, synthesize_speech


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

translation_service = get_translation_service()


# Language options for dropdown
LANGUAGE_OPTIONS = {
    "Assamese": "as",
    "Bengali": "bn",
    "English (India)": "en",
    "Gujarati": "gu",
    "Hindi": "hi",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Odia": "or",
    "Punjabi": "pa",
    "Tamil": "ta",
    "Telugu": "te",
    "Urdu": "ur",
}


def _format_pitch(value: int) -> str:
    """Convert slider semitone value to SSML string."""
    if value == 0:
        return "default"
    return f"{value:+d}st"


def _format_rate(value: int) -> str:
    """Convert slider percentage to SSML rate string."""
    if value == 0:
        return "default"
    return f"{value:+d}%"


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
            index=list(LANGUAGE_OPTIONS.keys()).index("English (India)"),
            help="Choose the language you want to translate and speak"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        
        # Voice Settings Section
        st.subheader("🎤 Voice Settings")
        voice_options = AZURE_VOICES.get(target_language, {})
        available_genders = [gender.title() for gender in voice_options.keys() if voice_options[gender]]
        default_gender_index = 0
        if available_genders and "Female" in available_genders:
            default_gender_index = available_genders.index("Female")
        selected_gender = st.radio(
            "Voice Gender",
            options=available_genders or ["Female"],
            index=default_gender_index if available_genders else 0,
            horizontal=True,
        )
        selected_voice = voice_options.get(selected_gender.lower()) or next(iter(voice_options.values()), None)
        if selected_voice:
            st.caption(f"Azure neural voice: `{selected_voice}`")
        else:
            st.warning("⚠️ No Azure voice configured for this language; please update the configuration.")

        pitch_value = st.slider(
            "Pitch",
            min_value=-3,
            max_value=3,
            value=0,
            help="Adjust pitch (in semitones). Negative values lower the pitch, positive values raise it.",
        )
        st.caption(f"Current pitch: {_format_pitch(pitch_value)}")

        speed_value = st.slider(
            "Speed",
            min_value=-50,
            max_value=50,
            value=0,
            help="Adjust speaking speed (percentage). Negative values slow down the speech, positive values speed it up.",
        )
        st.caption(f"Current speed: {_format_rate(speed_value)}")
    
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
            
            translated_text = translation_result['translated_text']
            pitch_ssml = _format_pitch(pitch_value)
            rate_ssml = _format_rate(speed_value)

            try:
                audio_bytes = synthesize_speech(
                    text=translated_text,
                    voice=selected_voice,
                    pitch=pitch_ssml,
                    rate=rate_ssml,
                )
            except Exception as exc:
                st.error(f"❌ Azure speech synthesis failed: {exc}")
                st.stop()
            
            filename = f"speech_{target_language.replace(' ', '_').lower()}.mp3"
            speech_result = {
                'success': True,
                'audio_bytes': audio_bytes,
                'filename': filename,
                'voice_used': selected_voice,
                'pitch': pitch_ssml,
                'rate': rate_ssml,
            }
        
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
                
                audio_bytes = speech_result['audio_bytes']

                # Display audio player
                st.audio(audio_bytes, format='audio/mp3', start_time=0)
                
                # Download button
                st.download_button(
                    label="📥 Download Audio (MP3)",
                    data=audio_bytes,
                    file_name=speech_result['filename'],
                    mime="audio/mpeg",
                    use_container_width=True
                )
            else:
                st.error(f"❌ {speech_result['message']}")


if __name__ == "__main__":
    main()

