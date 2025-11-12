"""
Azure Text-to-Speech service integration.

Provides utilities for synthesising speech using Azure Neural voices
with SSML controls for pitch and speaking rate.
"""

from __future__ import annotations

import os
from typing import Dict, Tuple
from xml.sax.saxutils import escape
import io

from pydub import AudioSegment


try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise ImportError(
        "azure-cognitiveservices-speech is required for Azure TTS. "
        "Install it via 'pip install azure-cognitiveservices-speech'."
    ) from exc


# Mapping between UI language labels and Azure neural voice names.
AZURE_VOICES: Dict[str, Dict[str, str]] = {
    "Assamese": {
        "female": "as-IN-GitanjaliNeural",
        "male": "as-IN-ManishNeural",
    },
    "Bengali": {
        "female": "bn-IN-TanishaaNeural",
        "male": "bn-IN-BashkarNeural",
    },
    "English (India)": {
        "female": "en-IN-NeerjaNeural",
        "male": "en-IN-PrabhatNeural",
    },
    "Gujarati": {
        "female": "gu-IN-DhwaniNeural",
        "male": "gu-IN-NiranjanNeural",
    },
    "Hindi": {
        "female": "hi-IN-SwaraNeural",
        "male": "hi-IN-MadhurNeural",
    },
    "Kannada": {
        "female": "kn-IN-SapnaNeural",
        "male": "kn-IN-GaganNeural",
    },
    "Malayalam": {
        "female": "ml-IN-SobhanaNeural",
        "male": "ml-IN-MidhunNeural",
    },
    "Marathi": {
        "female": "mr-IN-AarohiNeural",
        "male": "mr-IN-ManoharNeural",
    },
    "Odia": {
        "female": "or-IN-KalpanaNeural",
        "male": "or-IN-SubhenduNeural",
    },
    "Punjabi": {
        "female": "pa-IN-GurpreetNeural",
        "male": "pa-IN-ManinderNeural",
    },
    "Tamil": {
        "female": "ta-IN-PallaviNeural",
        "male": "ta-IN-ValluvarNeural",
    },
    "Telugu": {
        "female": "te-IN-ShrutiNeural",
        "male": "te-IN-MohanNeural",
    },
    "Urdu": {
        "female": "ur-IN-UditaNeural",
        "male": "ur-IN-AsadNeural",
    },
}


def _extract_locale(voice: str) -> str:
    """Derive locale from the Azure voice name (e.g. 'hi-IN')."""
    parts = voice.split("-")
    if len(parts) >= 2:
        return f"{parts[0]}-{parts[1]}"
    return "en-US"


def _build_ssml(text: str, voice: str, pitch: str, rate: str) -> str:
    """Create the SSML payload required by Azure Speech."""
    safe_text = escape(text, entities={"'": "&apos;", '"': "&quot;"})
    locale = _extract_locale(voice)
    ssml = (
        f'<speak version="1.0" xml:lang="{locale}" '
        f'xmlns="http://www.w3.org/2001/10/synthesis" '
        f'xmlns:mstts="http://www.w3.org/2001/mstts">'
        f'<voice name="{voice}" xml:lang="{locale}">'
        f'<prosody pitch="{pitch}" rate="{rate}">{safe_text}</prosody>'
        f'</voice>'
        f'</speak>'
    )
    return ssml
def _resolve_output_format() -> Tuple[int, str]:
    """
    Locate a supported Azure output format.

    Returns:
        Tuple of (enum value, label) where label is either 'mp3' or 'pcm'.
    """
    preferred_mp3_formats = [
        "Audio16Khz32KBitrateMonoMp3",
        "Audio24Khz48KBitrateMonoMp3",
        "Audio16Khz16KBitrateMonoMp3",
        "Audio16Khz128KBitrateMonoMp3",
        "Audio48Khz96KBitrateMonoMp3",
        "Audio48Khz192KBitrateMonoMp3",
    ]
    for attr_name in preferred_mp3_formats:
        if hasattr(speechsdk.SpeechSynthesisOutputFormat, attr_name):
            return getattr(speechsdk.SpeechSynthesisOutputFormat, attr_name), "mp3"

    pcm_fallbacks = [
        "Riff24Khz16BitMonoPcm",
        "Riff16Khz16BitMonoPcm",
        "Riff8Khz16BitMonoPcm",
    ]
    for attr_name in pcm_fallbacks:
        if hasattr(speechsdk.SpeechSynthesisOutputFormat, attr_name):
            return getattr(speechsdk.SpeechSynthesisOutputFormat, attr_name), "pcm"

    raise AttributeError(
        "Azure Speech SDK does not expose MP3 or PCM output formats. "
        "Please upgrade azure-cognitiveservices-speech."
    )


def synthesize_speech(text: str, voice: str, pitch: str, rate: str) -> bytes:
    """
    Convert text to speech using Azure Cognitive Services.

    Args:
        text: Input text for synthesis.
        voice: Azure neural voice name (e.g. "hi-IN-SwaraNeural").
        pitch: SSML pitch adjustment (e.g. "+2st").
        rate: SSML rate adjustment (e.g. "-10%").

    Returns:
        bytes: Audio data in MP3 format.

    Raises:
        RuntimeError: If credentials are missing or synthesis fails.
    """
    if not text.strip():
        raise ValueError("Cannot synthesise empty text.")

    speech_key = os.getenv("AZURE_SPEECH_KEY", "").strip()
    speech_region = os.getenv("AZURE_SPEECH_REGION", "").strip()

    if not speech_key or not speech_region:
        raise RuntimeError(
            "Azure Speech credentials are missing. Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION."
        )

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_synthesis_voice_name = voice

    try:
        output_format, format_label = _resolve_output_format()
        speech_config.set_speech_synthesis_output_format(output_format)
    except AttributeError as exc:
        raise RuntimeError(str(exc)) from exc

    ssml = _build_ssml(text=text, voice=voice, pitch=pitch, rate=rate)

    # audio_config=None ensures the audio is returned in-memory.
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
    result = synthesizer.speak_ssml_async(ssml).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        audio_bytes = result.audio_data
        if format_label == "pcm":
            try:
                wav_stream = io.BytesIO(audio_bytes)
                audio_segment = AudioSegment.from_file(wav_stream, format="wav")
                mp3_buffer = io.BytesIO()
                audio_segment.export(mp3_buffer, format="mp3")
                audio_bytes = mp3_buffer.getvalue()
            except FileNotFoundError as exc:
                raise RuntimeError(
                    "MP3 conversion requires ffmpeg or avlib to be installed. "
                    "Install it and ensure it's on PATH."
                ) from exc
            except Exception as exc:  # pragma: no cover - conversion edge cases
                raise RuntimeError(f"Failed to convert PCM audio to MP3: {exc}") from exc
        return audio_bytes

    if result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        error_details = getattr(cancellation_details, "error_details", "No error details provided.")
        raise RuntimeError(f"Azure speech synthesis cancelled: {error_details}")

    raise RuntimeError(f"Azure speech synthesis failed with reason: {result.reason}")


def get_voice_for_gender(language: str, gender: str) -> str:
    """
    Resolve the Azure voice for the requested language and gender.

    Falls back to the first available gender if the requested one is missing.
    """
    voices = AZURE_VOICES.get(language, {})
    if not voices:
        raise KeyError(f"No Azure voices configured for '{language}'.")

    gender_key = (gender or "").lower()
    if gender_key in voices and voices[gender_key]:
        return voices[gender_key]

    # Prefer female fallback, then male, otherwise first voice.
    if "female" in voices and voices["female"]:
        return voices["female"]
    if "male" in voices and voices["male"]:
        return voices["male"]

    # Return arbitrary voice to avoid total failure.
    for voice_name in voices.values():
        if voice_name:
            return voice_name

    raise KeyError(f"No valid Azure voices configured for '{language}'.")


def get_available_genders(language: str) -> Dict[str, str]:
    """Return the gender->voice mapping for the provided language."""
    return {
        gender: voice
        for gender, voice in AZURE_VOICES.get(language, {}).items()
        if voice
    }


__all__ = ["AZURE_VOICES", "synthesize_speech", "get_voice_for_gender", "get_available_genders"]

