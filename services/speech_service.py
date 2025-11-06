"""
Speech Service Module
Handles text-to-speech conversion using OpenAI TTS (high quality) with fallback to gTTS.
"""

from gtts import gTTS
import os
from openai import OpenAI
from dotenv import load_dotenv
# Speed adjustment removed - not needed

# Load environment variables from .env file
# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)  # Load .env file if it exists

# Languages that gTTS doesn't support - these require OpenAI TTS
# gTTS doesn't support: Assamese (as), Odia (or), and Punjabi (pa)
GTTS_UNSUPPORTED_LANGUAGES = {'as', 'or', 'pa'}  # Assamese, Odia, Punjabi


class SpeechService:
    """
    Service class for handling text-to-speech conversion operations.
    """
    
    def __init__(self, output_dir='output', use_openai=True):
        """
        Initialize the SpeechService with output directory.
        
        Args:
            output_dir (str): Directory where audio files will be saved
            use_openai (bool): Whether to use OpenAI TTS (requires API key)
        """
        self.output_dir = output_dir
        self.use_openai = use_openai
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize OpenAI client if API key is available
        self.openai_client = None
        if self.use_openai:
            api_key = os.getenv('OPENAI_API_KEY')
            # Also check if it's set but empty
            if api_key and api_key.strip():
                api_key = api_key.strip()
                # Validate API key format (should start with sk-)
                if not api_key.startswith('sk-'):
                    print(f"⚠️ Warning: OpenAI API key doesn't start with 'sk-'. Got: {api_key[:10]}...")
                try:
                    self.openai_client = OpenAI(api_key=api_key)
                    print(f"✅ OpenAI TTS client initialized successfully (key: {api_key[:10]}...)")
                except Exception as e:
                    print(f"❌ Error: Could not initialize OpenAI client: {e}")
                    self.use_openai = False
                    self.openai_client = None
            else:
                print("⚠️ OpenAI API key not found in environment variables or .env file")
                print(f"   Checked .env file at: {env_path}")
                self.use_openai = False
                self.openai_client = None
    
    def text_to_speech(self, text, lang_code, filename='output.mp3', voice='nova', use_openai_preference=True):
        """
        Converts text to speech and saves it as an MP3 file.
        Uses OpenAI TTS if available, otherwise falls back to gTTS.
        
        Args:
            text (str): The text to convert to speech
            lang_code (str): Language code for the speech (e.g., 'te', 'en', 'hi')
            filename (str): Name of the output MP3 file (default: 'output.mp3')
            voice (str): Voice selection for OpenAI TTS ('alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer')
            use_openai_preference (bool): Whether to prefer OpenAI TTS if available
            
        Returns:
            dict: Dictionary containing:
                - 'file_path': Full path to the generated audio file
                - 'filename': Name of the file
                - 'success': Boolean indicating if conversion was successful
                - 'message': Status message
                - 'tts_engine': Which TTS engine was used ('openai' or 'gtts')
        
        Example:
            >>> service = SpeechService()
            >>> result = service.text_to_speech("Hello", "en", "hello.mp3", voice='nova')
            >>> print(result['file_path'])  # Output: output/hello.mp3
        """
        try:
            # Validate input
            if not text or not text.strip():
                return {
                    'file_path': None,
                    'filename': filename,
                    'success': False,
                    'message': 'Error: Empty text provided',
                    'tts_engine': None
                }
            
            # Construct full file path
            file_path = os.path.join(self.output_dir, filename)
            
            # Check if language is unsupported by gTTS
            is_unsupported = lang_code.lower() in GTTS_UNSUPPORTED_LANGUAGES
            
            # For unsupported languages, prioritize OpenAI TTS
            # OpenAI TTS supports more languages including these Indian languages
            if is_unsupported:
                print(f"⚠️ Language '{lang_code}' is not supported by gTTS. Using OpenAI TTS if available.")
                use_openai_preference = True  # Force OpenAI for unsupported languages
            
            # Try OpenAI TTS first if enabled and client is available
            if use_openai_preference and self.use_openai and self.openai_client:
                try:
                    # Validate voice is one of OpenAI's supported voices
                    valid_voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
                    if voice not in valid_voices:
                        print(f"Invalid voice '{voice}', defaulting to 'nova'")
                        voice = 'nova'
                    
                    # Debug: Print voice being used
                    print(f"Using OpenAI TTS with voice: {voice}")
                    
                    # OpenAI TTS API call
                    response = self.openai_client.audio.speech.create(
                        model="tts-1",  # or "tts-1-hd" for higher quality (more expensive)
                        voice=voice,  # Use the selected voice
                        input=text
                    )
                    
                    # Save the audio file
                    response.stream_to_file(file_path)
                    
                    # Verify file was created
                    if os.path.exists(file_path):
                        return {
                            'file_path': file_path,
                            'filename': filename,
                            'success': True,
                            'message': f'Audio file generated successfully using OpenAI TTS with voice "{voice}": {file_path}',
                            'tts_engine': 'openai',
                            'voice_used': voice
                        }
                except Exception as e:
                    # If OpenAI fails
                    error_msg = str(e)
                    
                    # For unsupported languages, don't try gTTS - return error immediately
                    if is_unsupported:
                        lang_names = {
                            'as': 'Assamese',
                            'or': 'Odia',
                            'pa': 'Punjabi'
                        }
                        lang_name = lang_names.get(lang_code.lower(), lang_code.upper())
                        return {
                            'file_path': None,
                            'filename': filename,
                            'success': False,
                            'message': f'Language "{lang_name}" ({lang_code}) requires OpenAI TTS, but OpenAI TTS failed: {error_msg}. Please check your OpenAI API key configuration.',
                            'tts_engine': None
                        }
                    
                    # For supported languages, fall back to gTTS
                    if 'quota' in error_msg.lower() or 'insufficient_quota' in error_msg.lower():
                        print(f"⚠️ OpenAI quota exceeded, falling back to gTTS")
                    else:
                        print(f"⚠️ OpenAI TTS failed, falling back to gTTS: {error_msg}")
                    # Don't print full traceback for quota errors
                    if 'quota' not in error_msg.lower():
                        import traceback
                        traceback.print_exc()
            
            # Fallback to gTTS
            # If language is unsupported by gTTS and OpenAI is not available, return error
            if is_unsupported:
                # Language is not supported by gTTS and OpenAI failed or is not available
                lang_names = {
                    'as': 'Assamese',
                    'or': 'Odia',
                    'pa': 'Punjabi'
                }
                lang_name = lang_names.get(lang_code.lower(), lang_code.upper())
                return {
                    'file_path': None,
                    'filename': filename,
                    'success': False,
                    'message': f'Language "{lang_name}" ({lang_code}) is not supported by gTTS. Please configure OpenAI TTS API key in your .env file to generate audio for this language. OpenAI TTS supports Assamese, Odia, and Punjabi.',
                    'tts_engine': None
                }
            
            try:
                # Create gTTS object with the text and language
                # slow=False means normal speed speech
                tts = gTTS(text=text, lang=lang_code, slow=False)
                
                # Save the audio file
                tts.save(file_path)
                
                # Verify file was created
                if os.path.exists(file_path):
                    return {
                        'file_path': file_path,
                        'filename': filename,
                        'success': True,
                        'message': f'Audio file generated successfully using gTTS: {file_path}',
                        'tts_engine': 'gtts'
                    }
                else:
                    return {
                        'file_path': None,
                        'filename': filename,
                        'success': False,
                        'message': 'Error: File was not created',
                        'tts_engine': None
                    }
            except Exception as e:
                error_message = str(e)
                # Check if it's a language not supported error
                if 'not supported' in error_message.lower() or 'language' in error_message.lower():
                    # Provide helpful error message
                    return {
                        'file_path': None,
                        'filename': filename,
                        'success': False,
                        'message': f'Language "{lang_code}" is not supported by gTTS. Please configure OpenAI TTS API key for better language support. Error: {error_message}',
                        'tts_engine': None
                    }
                
                error_message = f"Error generating speech with gTTS: {error_message}"
                print(error_message)
                return {
                    'file_path': None,
                    'filename': filename,
                    'success': False,
                    'message': error_message,
                    'tts_engine': None
                }
                
        except Exception as e:
            # Handle any errors during TTS conversion
            error_message = f"Error generating speech: {str(e)}"
            print(error_message)
            return {
                'file_path': None,
                'filename': filename,
                'success': False,
                'message': error_message,
                'tts_engine': None
            }
    
    @staticmethod
    def get_available_voices():
        """
        Returns available OpenAI TTS voices categorized by gender.
        
        Returns:
            dict: Dictionary with voice categories
        """
        return {
            'Female': {
                'nova': 'Nova - Clear and expressive female voice',
                'shimmer': 'Shimmer - Warm female voice'
            },
            'Male': {
                'onyx': 'Onyx - Deep male voice',
                'echo': 'Echo - Strong male voice'
            },
            'Neutral': {
                'alloy': 'Alloy - Balanced neutral voice',
                'fable': 'Fable - Versatile neutral voice'
            }
        }
    
    @staticmethod
    def get_voice_by_gender_and_age(gender='Female', age_tone='Adult'):
        """
        Returns voice selection based on gender and age tone preference.
        
        Args:
            gender (str): 'Male' or 'Female'
            age_tone (str): 'Child', 'Adult', or 'Senior'
            
        Returns:
            str: Voice code that best matches the criteria
        """
        # Voice mapping based on characteristics
        voice_map = {
            'Female': {
                'Child': 'nova',      # Higher, clearer voice
                'Adult': 'shimmer',   # Warm, mature voice
                'Senior': 'shimmer'    # Warm, gentle voice
            },
            'Male': {
                'Child': 'echo',      # Strong but not too deep
                'Adult': 'onyx',      # Deep, mature voice
                'Senior': 'onyx'       # Deep, mature voice
            }
        }
        
        # Default to first available voice if not found
        if gender in voice_map and age_tone in voice_map[gender]:
            return voice_map[gender][age_tone]
        
        # Fallback
        if gender == 'Female':
            return 'nova'
        elif gender == 'Male':
            return 'onyx'
        else:
            return 'alloy'
    
    def get_output_path(self, filename='output.mp3'):
        """
        Gets the full path for an output file.
        
        Args:
            filename (str): Name of the file
            
        Returns:
            str: Full path to the file
        """
        return os.path.join(self.output_dir, filename)

