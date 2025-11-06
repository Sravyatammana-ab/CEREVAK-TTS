"""
Multilingual Text-to-Speech Translation Module
This module provides functions for language detection, translation, and text-to-speech conversion.
"""

from googletrans import Translator
from gtts import gTTS
import os


def detect_language(text):
    """
    Detects the language of the input text.
    
    Args:
        text (str): The input text to detect language for
        
    Returns:
        str: Language code (e.g., 'en', 'es', 'hi', 'te')
    """
    translator = Translator()
    try:
        detected = translator.detect(text)
        return detected.lang
    except Exception as e:
        print(f"Error detecting language: {e}")
        return 'en'  # Default to English if detection fails


def translate_text(text, target_lang):
    """
    Translates the input text to the target language.
    
    Args:
        text (str): The text to translate
        target_lang (str): Target language code (e.g., 'te' for Telugu, 'hi' for Hindi)
        
    Returns:
        str: Translated text
    """
    translator = Translator()
    try:
        translated = translator.translate(text, dest=target_lang)
        return translated.text
    except Exception as e:
        print(f"Error translating text: {e}")
        return text  # Return original text if translation fails


def text_to_speech(text, lang, output_filename='output_speech.mp3'):
    """
    Converts text to speech and saves it as an MP3 file.
    
    Args:
        text (str): The text to convert to speech
        lang (str): Language code for the speech (e.g., 'te', 'en', 'hi')
        output_filename (str): Name of the output MP3 file (default: 'output_speech.mp3')
        
    Returns:
        str: Path to the generated MP3 file
    """
    try:
        # Create gTTS object
        tts = gTTS(text=text, lang=lang, slow=False)
        
        # Save to file (overwrites if exists)
        tts.save(output_filename)
        print(f"Audio saved as {output_filename}")
        
        return output_filename
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None


def get_language_name(lang_code):
    """
    Converts language code to readable language name.
    
    Args:
        lang_code (str): Language code (e.g., 'en', 'te', 'hi')
        
    Returns:
        str: Language name (e.g., 'English', 'Telugu', 'Hindi')
    """
    lang_names = {
        'en': 'English',
        'te': 'Telugu',
        'hi': 'Hindi',
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
        'ta': 'Tamil',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'bn': 'Bengali',
        'gu': 'Gujarati',
        'mr': 'Marathi',
        'pa': 'Punjabi'
    }
    return lang_names.get(lang_code, lang_code.upper())


def main():
    """
    Main function that orchestrates the text-to-speech translation process.
    """
    print("=" * 60)
    print("Multilingual Text-to-Speech Translation System")
    print("=" * 60)
    
    # Get input text from user
    input_text = input("\nEnter the text you want to translate and convert to speech: ").strip()
    
    if not input_text:
        print("Error: No text provided!")
        return
    
    # Get target language from user
    print("\nCommon language codes:")
    print("  te - Telugu | hi - Hindi | es - Spanish | fr - French")
    print("  de - German | ja - Japanese | ko - Korean | zh - Chinese")
    print("  ar - Arabic | ta - Tamil | kn - Kannada | ml - Malayalam")
    print("  en - English | pt - Portuguese | ru - Russian")
    
    target_lang = input("\nEnter target language code (e.g., 'te' for Telugu): ").strip().lower()
    
    if not target_lang:
        print("Error: No target language provided!")
        return
    
    # Detect source language
    print("\n" + "-" * 60)
    print("Processing...")
    print("-" * 60)
    
    source_lang = detect_language(input_text)
    source_lang_name = get_language_name(source_lang)
    print(f"Detected source language: {source_lang_name} ({source_lang})")
    
    # Translate text
    translated_text = translate_text(input_text, target_lang)
    target_lang_name = get_language_name(target_lang)
    print(f"Translated text ({target_lang_name}): {translated_text}")
    
    # Convert to speech
    output_file = text_to_speech(translated_text, target_lang)
    
    if output_file:
        print(f"\n✓ Audio file generated successfully: {output_file}")
        print(f"✓ Language: {target_lang_name}")
        print(f"✓ Translated text: {translated_text}")
        
        # Play the audio
        try:
            from playsound import playsound
            print("\nPlaying audio...")
            playsound(output_file)
            print("✓ Audio playback completed!")
        except Exception as e:
            print(f"Note: Could not play audio automatically: {e}")
            print(f"Please manually play the file: {output_file}")
    else:
        print("Error: Failed to generate audio file!")


if __name__ == "__main__":
    main()


