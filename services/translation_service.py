"""
Translation Service Module
Handles language detection and text translation using deep-translator library.
This library is Python 3.13 compatible and doesn't have the cgi module dependency issue.
"""

from deep_translator import GoogleTranslator
from langdetect import detect, detect_langs, DetectorFactory


class TranslationService:
    """
    Service class for handling language detection and translation operations.
    Uses deep-translator for translation (Python 3.13 compatible).
    """
    
    def __init__(self):
        """
        Initialize the TranslationService.
        """
        # Set seed for consistent language detection
        DetectorFactory.seed = 0
    
    def detect_language(self, text):
        """
        Automatically detects the language of the input text.
        Uses multiple detection methods for better accuracy.
        
        Args:
            text (str): The input text to detect language for
            
        Returns:
            dict: Dictionary containing:
                - 'code': Language code (e.g., 'en', 'te', 'hi')
                - 'name': Language name (e.g., 'English', 'Telugu', 'Hindi')
                - 'confidence': Confidence score (0-1)
        
        Example:
            >>> service = TranslationService()
            >>> result = service.detect_language("Hello, how are you?")
            >>> print(result['code'])  # Output: 'en'
        """
        if not text or not text.strip():
            return {
                'code': 'en',
                'name': 'English',
                'confidence': 0.0
            }
        
        # Clean and prepare text for detection
        text_clean = text.strip()
        
        # For very short texts, langdetect can be unreliable
        # Use detect_langs to get confidence scores for better accuracy
        try:
            # Use langdetect with confidence scores
            detected_languages = detect_langs(text_clean)
            
            if detected_languages:
                # Get the most likely language
                best_match = detected_languages[0]
                detected_lang_code = best_match.lang
                confidence = best_match.prob
                
                return {
                    'code': detected_lang_code,
                    'name': self._get_language_name(detected_lang_code),
                    'confidence': confidence
                }
            else:
                # Fallback to simple detect if detect_langs returns empty
                detected_lang_code = detect(text_clean)
                return {
                    'code': detected_lang_code,
                    'name': self._get_language_name(detected_lang_code),
                    'confidence': 0.5
                }
        except Exception as e:
            # If detect_langs fails, try simple detect as fallback
            try:
                detected_lang_code = detect(text_clean)
                print(f"Warning: Using fallback detection method. Error: {e}")
                return {
                    'code': detected_lang_code,
                    'name': self._get_language_name(detected_lang_code),
                    'confidence': 0.3
                }
            except Exception as e2:
                # If all detection fails, default to English
                print(f"Error detecting language: {e2}")
                return {
                    'code': 'en',
                    'name': 'English',
                    'confidence': 0.0
                }
    
    def translate_text(self, text, target_lang_code, source_lang_code=None):
        """
        Translates the input text to the target language.
        
        Args:
            text (str): The text to translate
            target_lang_code (str): Target language code (e.g., 'te' for Telugu, 'hi' for Hindi)
            source_lang_code (str, optional): Source language code. If not provided, will auto-detect.
            
        Returns:
            dict: Dictionary containing:
                - 'translated_text': The translated text
                - 'source_lang': Source language code
                - 'target_lang': Target language code
                - 'original_text': Original input text
        
        Example:
            >>> service = TranslationService()
            >>> result = service.translate_text("Hello", "te")
            >>> print(result['translated_text'])  # Output: Telugu translation
        """
        try:
            # Use provided source language or detect it
            if source_lang_code is None:
                source_lang_code = self.detect_language(text)['code']
            
            # If source and target are the same, return original text
            if source_lang_code == target_lang_code:
                return {
                    'translated_text': text,
                    'source_lang': source_lang_code,
                    'target_lang': target_lang_code,
                    'original_text': text
                }
            
            # Translate the text to target language using deep-translator
            translator = GoogleTranslator(source=source_lang_code, target=target_lang_code)
            translated_text = translator.translate(text)
            
            return {
                'translated_text': translated_text,
                'source_lang': source_lang_code,
                'target_lang': target_lang_code,
                'original_text': text
            }
        except Exception as e:
            # If translation fails, return original text
            print(f"Error translating text: {e}")
            return {
                'translated_text': text,
                'source_lang': source_lang_code if source_lang_code else 'unknown',
                'target_lang': target_lang_code,
                'original_text': text
            }
    
    def _get_language_name(self, lang_code):
        """
        Converts language code to readable language name.
        
        Args:
            lang_code (str): Language code (e.g., 'en', 'te', 'hi')
            
        Returns:
            str: Language name (e.g., 'English', 'Telugu', 'Hindi')
        """
        # Mapping of language codes to language names
        language_map = {
            'en': 'English',
            'hi': 'Hindi',
            'ur': 'Urdu',
            'as': 'Assamese',
            'bn': 'Bengali',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'mr': 'Marathi',
            'or': 'Odia',
            'pa': 'Punjabi',
            'ta': 'Tamil',
            'te': 'Telugu',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'ne': 'Nepali',
            'si': 'Sinhala'
        }
        return language_map.get(lang_code, lang_code.upper())

